#!/usr/bin/env python3
"""Package only step-144 actual runs; verify hashes before deleting loose copies."""
import hashlib, json, platform, shutil, subprocess, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/audio-node5-s144"
OUT.mkdir(exist_ok=False)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads((ROOT/p).read_text())
revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
base = subprocess.check_output(["git", "rev-parse", "HEAD^"], cwd=ROOT, text=True).strip()
report = "evidence/n5s144-final-report"
# Final game source must match BOTH actual offline and actual live launches.
for path in ["evidence/audio/n5s144-final/launch.json", "evidence/audio/n5s144-spatial-final/launch.json", "evidence/audio/n5s144-transport/playback.json"]:
    for f, h in read(path)["source_sha256"].items():
        assert sha(ROOT/f) == h, f
        committed = subprocess.check_output(["git", "show", revision+":"+f], cwd=ROOT)
        assert hashlib.sha256(committed).hexdigest() == h, f
production = {}
changed = []
for f in sorted((ROOT/"game").rglob("*")):
    if not f.is_file() or ".godot" in f.parts or "tests" in f.parts: continue
    path = str(f.relative_to(ROOT))
    production[path] = sha(f)
    original = subprocess.check_output(["git", "show", base+":"+path], cwd=ROOT)
    if hashlib.sha256(original).hexdigest() != sha(f): changed.append(path)
assert changed == ["game/sound.gd"], changed
summary = dict(source_revision=revision, baseline_main=base,
    source_matches_final_live_and_offline_capture=True, production_changes=changed,
    production_sha256=production, contract="docs/audio-contract.json",
    audio=read("evidence/audio/n5s144-final/analysis.json"),
    spatial=read("evidence/audio/n5s144-spatial-final/spatial-analysis.json"),
    combat=read(report+"/combat-audio-check.log"),
    active_combat=read(report+"/active-check.log"),
    physics=read(report+"/physics-comparison.json"),
    baseline_physics_archive="evidence/destruction-node4-rerun/n4s140-raw-runs.tar.gz",
    baseline_physics_member="evidence/destruction/n4s140-capture/physics.csv.gz",
    performance=read(report+"/performance.json"),
    instrumented_regression_performance=read(report+"/destruction-check.log")["runs"][0]["performance"],
    controls_assertions=len(read("evidence/controls/n5s144-final/results.json")["checks"]),
    asset_regeneration=read(report+"/asset-regeneration.json"),
    source_asset_provenance="game/audio/provenance.json", python3=platform.python_version(),
    daemon=read("evidence/n5s144-transport-daemon/lifecycle.json"),
    listening="NOT PERFORMED. No physical soundcard or auditory perception. Human exact-release playtest must judge force, weight, clarity and audiovisual satisfaction.",
    no_durable_node_completion_claim=True)
(OUT/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
directories = sorted({p for p in (ROOT/"evidence").glob("n5s144*") if p.is_dir()} |
    {p for parent in ["audio", "destruction", "controls", "opposition"] for p in (ROOT/"evidence"/parent).glob("n5s144*") if p.is_dir()})
files = sorted(f for d in directories for f in d.rglob("*") if f.is_file() and f.name != "movie.avi")
members = [dict(path=str(f.relative_to(ROOT)), bytes=f.stat().st_size, sha256=sha(f)) for f in files]
archive = OUT/"runtime-evidence.tar.gz"
with tarfile.open(archive, "w:gz", compresslevel=6) as t:
    for f in files: t.add(f, arcname=str(f.relative_to(ROOT)), recursive=False)
with tarfile.open(archive) as t:
    assert len(t.getmembers()) == len(members)
    for m in members:
        content = t.extractfile(m["path"]).read()
        assert len(content) == m["bytes"] and hashlib.sha256(content).hexdigest() == m["sha256"]
authored = ["game/sound.gd", "game/tests/audio_spatial_tests.gd", "game/tests/audio_spatial_tests.gd.uid", "scripts/run_audio.py", "scripts/check_audio_spatial.py", "scripts/package_audio_s144.py", "docs/audio-node5-s144.md"]
manifest = dict(source_revision=revision, archive=str(archive.relative_to(ROOT)),
    archive_bytes=archive.stat().st_size, archive_sha256=sha(archive), members_verified=True,
    member_count=len(members), members=members,
    authored_or_modified={p:sha(ROOT/p) for p in authored}, summary_sha256=sha(OUT/"summary.json"),
    extract="tar -xzf evidence/audio-node5-s144/runtime-evidence.tar.gz",
    incidental_not_deliverables="Downloaded engine, venv, import caches, temporary sockets, git metadata and original intermediate AVI; AVI hashes retained in launch metadata.")
(OUT/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
checksums = [ROOT/p for p in authored] + [OUT/"summary.json", OUT/"manifest.json", archive]
(OUT/"SHA256SUMS").write_text("".join(sha(f)+"  "+str(f.relative_to(ROOT))+"\n" for f in checksums))
# Archive bytes were read back above. Retain all raw evidence there, remove ONLY
# this execution’s now-redundant loose directories and intermediate AVI files.
for d in directories: shutil.rmtree(d)
print(json.dumps(dict(archive=str(archive), members=len(members), bytes=archive.stat().st_size, verified=True), indent=2))
