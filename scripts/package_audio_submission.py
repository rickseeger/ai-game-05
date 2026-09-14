#!/usr/bin/env python3
"""Package a completed rerun_audio_node5 + spatial + transport submission.
Verifies recorded game bytes against HEAD and every archive member before pruning
only the named run directories. Never changes game code or mission state.
"""
import argparse, hashlib, json, platform, shutil, subprocess, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("prefix")
p.add_argument("output_name")
p.add_argument("--review", required=True)
a = p.parse_args()
for name in (a.prefix, a.output_name):
    assert Path(name).name == name and name not in (".", "..")
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def read(name): return json.loads((ROOT / name).read_text())
revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
report = "evidence/" + a.prefix + "-report"
audio = "evidence/audio/" + a.prefix
commands = read(report + "/commands.json") + read(report + "/supplemental-commands.json")
assert commands and all(c["returncode"] == 0 for c in commands)
for file in (audio + "/launch.json", audio + "-spatial/launch.json", audio + "-transport/playback.json"):
    for f, h in read(file)["source_sha256"].items():
        assert sha(ROOT/f) == h, f
        assert hashlib.sha256(subprocess.check_output(["git", "show", revision + ":" + f], cwd=ROOT)).hexdigest() == h, f
summary = dict(source_revision=revision, production_sources_unchanged_and_committed=True,
    contract="docs/audio-contract.json", audio=read(audio + "/analysis.json"),
    spatial=read(audio + "-spatial/spatial-analysis.json"),
    combat=read(report + "/combat-audio-check.log"), active_combat=read(report + "/active-check.log"),
    physics=read(report + "/physics-comparison.json"), performance=read(report + "/performance.json"),
    instrumented_regression_performance=read(report + "/destruction-check.log")["runs"][0]["performance"],
    controls_assertions=len(read("evidence/controls/" + a.prefix + "/results.json")["checks"]),
    asset_regeneration=read(report + "/asset-regeneration.json"),
    asset_provenance="game/audio/provenance.json", commands=commands,
    daemon=read("evidence/" + a.prefix + "-transport-daemon/lifecycle.json"),
    python=platform.python_version(),
    listening="NOT PERFORMED: no auditory perception or physical soundcard. Virtual playback is not listening. Force, weight, clarity and subjective synchronization need final human listening.",
    worker_execution_only=True, durable_node_completion_claim=False)
assert summary["physics"]["identical_fixed_step_physics"]
assert summary["daemon"]["daemon_stopped"]
assert summary["asset_regeneration"]["byte_identical"]
out = ROOT / "evidence" / a.output_name
out.mkdir(exist_ok=False)
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
directories = [ROOT / report, ROOT / ("evidence/" + a.prefix + "-transport-daemon")]
for parent, suffixes in {"audio": ["", "-spatial", "-transport"], "destruction": ["", "-perf1", "-perf2", "-perf3"], "controls": [""], "opposition": ["", "-active"]}.items():
    directories += [ROOT / "evidence" / parent / (a.prefix + suffix) for suffix in suffixes]
assert all(d.is_dir() for d in directories)
files = sorted(f for d in directories for f in d.rglob("*") if f.is_file() and f.name != "movie.avi")
members = [dict(path=str(f.relative_to(ROOT)), bytes=f.stat().st_size, sha256=sha(f)) for f in files]
archive = out / "runtime-evidence.tar.gz"
with tarfile.open(archive, "w:gz", compresslevel=6) as t:
    for f in files: t.add(f, arcname=str(f.relative_to(ROOT)), recursive=False)
with tarfile.open(archive) as t:
    assert len(t.getmembers()) == len(members)
    for m in members:
        data = t.extractfile(m["path"]).read()
        assert len(data) == m["bytes"] and hashlib.sha256(data).hexdigest() == m["sha256"]
manifest = dict(source_revision=revision, archive=str(archive.relative_to(ROOT)), archive_bytes=archive.stat().st_size,
    archive_sha256=sha(archive), member_count=len(members), members=members, every_member_verified=True,
    extract="tar -xzf " + str(archive.relative_to(ROOT)),
    incidental_exclusions="Engine, virtualenv, import caches, git metadata, extracted baseline copy and intermediate AVI. Original AVI hashes retained in launch.json.")
(out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
retained = [ROOT / a.review, Path(__file__).resolve(), out / "summary.json", out / "manifest.json", archive]
(out / "SHA256SUMS").write_text("".join(sha(f) + "  " + str(f.relative_to(ROOT)) + "\n" for f in retained))
for d in directories: shutil.rmtree(d)
print(json.dumps(dict(archive=str(archive), member_count=len(members), bytes=archive.stat().st_size, verified=True), indent=2))
