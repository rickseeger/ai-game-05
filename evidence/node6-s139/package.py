#!/usr/bin/env python3
"""Package actual step-139 results; no simulated game data. Run at repository root."""
import datetime, hashlib, json, subprocess, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/node6-s139"
def read(path): return json.loads((ROOT/path).read_text())
def write(name, value): (OUT/name).write_text(json.dumps(value, indent=2)+"\n")
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
verification = ROOT / "evidence/n6s139-final-verification"
summary = {name: json.loads((verification/name).read_text()) for name in
           ["commands.json", "opposition-checks.json", "cue-checks.json", "controls-checks.json", "post-restore-checks.json"]}
summary["negative"] = read("evidence/opposition/n6s139-final-negative/negative-control.json")
summary["scope"] = "Worker execution only; no durable mission-state change; subjective readability and fun unassessed"
write("verification.json", summary)
handoff = {}
for scenario in ["inactive", "active"]:
    directory = "evidence/opposition/n6s139-final-" + scenario
    result = read(directory+"/results.json")
    trace = read(directory+"/trace.json")
    for samples in [trace, result["events"], result["frames"]]:
        assert all("unix_seconds" in s for s in samples)
        assert all(a["unix_seconds"] <= b["unix_seconds"] for a,b in zip(samples,samples[1:]))
    moments = []
    for event in result["events"]:
        if event["kind"] not in ["spawn_warning", "aim", "attack", "player_damage", "destroyed", "player_died"]:
            continue
        i = min(range(len(result["frames"])), key=lambda i: abs(result["frames"][i]["observed_tick"] - event["tick"]))
        moments.append({"event":event, "video_frame_one_based":i+1, "video_seconds":i/30,
                        "note":"Telemetry index, not a subjective visual observation"})
    handoff[scenario] = {"movie": directory+"/runtime.mp4", "results":directory+"/results.json",
                        "trace":directory+"/trace.json", "moments":moments}
write("human-handoff.json", {"status":"UNASSESSED; carry to node 9 human playtest, not a worker vision blocker",
     "concerns":["Red warning/aim/bolt discrimination at normal speed", "Directional damage clarity",
                 "Threat/counterplay readability during debris", "Difficulty, responsiveness and fun"],
     "archive_extraction":"tar -xzf evidence/node6-s139/raw-runs.tar.gz", "runs":handoff})
base = "ed443098523eb09094b9024f42d45a3e4117897e"
production = [p for p in (ROOT/"game").rglob("*") if p.is_file() and ".godot" not in p.parts and "tests" not in p.parts]
for p in production:
    assert p.read_bytes() == subprocess.check_output(["git", "show", base+":"+str(p.relative_to(ROOT))], cwd=ROOT)
write("provenance.json", {"base_commit":base, "packaged_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "production_unchanged":True, "production_sha256":{str(p.relative_to(ROOT)):digest(p) for p in sorted(production)},
     "engine_zip_sha256":digest(ROOT/".tools/godot.zip"), "engine_sha256":digest(ROOT/".tools/Godot_v4.5.1-stable_linux.x86_64"),
     "development_failure":"n6s139-focused initial diagnostic test parse error: filename inferred Variant. Explicit String fixed; failed launch/log retained, not success evidence.",
     "timestamps_verified":True, "prerequisites":"Read accepted design, controls, current opposition/destruction and prior node-6 report; fresh focused engine tests exercised both pylon and sentry burst interfaces."})
raw_dirs = sorted((ROOT/"evidence/opposition").glob("n6s139-*")) + sorted((ROOT/"evidence/controls").glob("n6s139-*")) + [verification]
files = sorted(p for d in raw_dirs for p in d.rglob("*") if p.is_file())
manifest = {str(p.relative_to(ROOT)):{"size":p.stat().st_size,"sha256":digest(p)} for p in files}
archive = OUT/"raw-runs.tar.gz"
with tarfile.open(archive, "w:gz") as tar:
    for p in files: tar.add(p, arcname=str(p.relative_to(ROOT)))
with tarfile.open(archive, "r:gz") as tar:
    assert len(tar.getmembers()) == len(manifest)
    for member in tar.getmembers():
        data = tar.extractfile(member).read()
        assert len(data) == manifest[member.name]["size"]
        assert hashlib.sha256(data).hexdigest() == manifest[member.name]["sha256"]
write("artifact-manifest.json", {"archive":"evidence/node6-s139/raw-runs.tar.gz", "archive_sha256":digest(archive),
                               "file_count":len(manifest), "members":manifest, "verified_by_readback":True})
print(json.dumps({"archive_bytes":archive.stat().st_size,"archived_files":len(manifest),"production_unchanged":True}))
