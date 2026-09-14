#!/usr/bin/env python3
"""Verify and package this focused execution, never mutate mission state."""
import hashlib, json, shutil, subprocess, tarfile
from pathlib import Path
root = Path(__file__).resolve().parents[1]
out = root / "evidence/audio-node5-s147"
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def read(f): return json.loads((root/f).read_text())
revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
assert revision == "7ee3d568eaa81d4095c7b1d4a75f331318054c38"
for name in ["evidence/audio/n5s147/launch.json", "evidence/audio/n5s147-spatial/launch.json", "evidence/audio/n5s147-transport/playback.json"]:
    for path, digest in read(name)["source_sha256"].items():
        assert sha(root/path) == digest
        assert hashlib.sha256(subprocess.check_output(["git", "show", revision+":"+path], cwd=root)).hexdigest() == digest
assert not subprocess.check_output(["git", "diff", "--", "game"], cwd=root)
commands = read("evidence/audio-node5-s147/commands.json")
assert all(c["returncode"] == 0 for c in commands)
summary = dict(source_revision=revision, production_sources_unchanged=True,
    commands=commands, audio=read("evidence/audio/n5s147/analysis.json"),
    spatial=read("evidence/audio/n5s147-spatial/spatial-analysis.json"),
    combat=read("evidence/audio-node5-s147/combat-check.log"),
    provenance=read("evidence/audio-node5-s147/provenance-check.json"),
    daemon=read("evidence/n5s147-transport-daemon/lifecycle.json"),
    listening="NONE. No physical soundcard or auditory perception. Null-sink transport is not listening. Virtual loopback fidelity fails; sparse live video is not synchronization proof. Primary MovieWriter is real engine/mixer execution, offline common clock, not real-time speaker latency.",
    worker_execution_finished=True, durable_node_acceptance=False)
assert summary["daemon"]["daemon_stopped"]
(out/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
for name in ["runtime.wav", "runtime.mp4"]:
    shutil.copy2(root/"evidence/audio/n5s147"/name, out/name)
dirs = [root/p for p in ["evidence/audio/n5s147", "evidence/audio/n5s147-spatial", "evidence/audio/n5s147-transport", "evidence/opposition/n5s147", "evidence/n5s147-transport-daemon"]]
logs = [f for f in out.iterdir() if f.suffix == ".log" or f.name in ["commands.json", "provenance-check.json"]]
files = sorted(logs + [f for d in dirs for f in d.rglob("*") if f.is_file() and f.name != "movie.avi"])
members = [dict(path=str(f.relative_to(root)), bytes=f.stat().st_size, sha256=sha(f)) for f in files]
archive = out/"runtime-evidence.tar.gz"
assert not archive.exists()
with tarfile.open(archive, "w:gz") as t:
    for f in files: t.add(f, arcname=str(f.relative_to(root)), recursive=False)
with tarfile.open(archive) as t:
    assert len(t.getmembers()) == len(members)
    for m in members:
        data = t.extractfile(m["path"]).read()
        assert len(data) == m["bytes"] and hashlib.sha256(data).hexdigest() == m["sha256"]
manifest = dict(source_revision=revision, archive_sha256=sha(archive),
    archive=str(archive.relative_to(root)), member_count=len(members), members=members,
    every_member_verified=True, source_hashes_verified_against_git=True,
    primary_capture=["evidence/audio-node5-s147/runtime.mp4", "evidence/audio-node5-s147/runtime.wav"],
    excluded_incidental="Engine/venv/import/git caches; intermediate AVIs hashed in launch.json")
(out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
for d in dirs: shutil.rmtree(d)
for f in logs: f.unlink()
retained = sorted(list(out.iterdir()) + [root/"docs/audio-node5-s147.md", root/"scripts/verify_audio_s147.py", Path(__file__).resolve()])
(out/"SHA256SUMS").write_text("".join(sha(f)+"  "+str(f.relative_to(root))+"\n" for f in retained))
print(json.dumps(dict(archive_bytes=archive.stat().st_size, members=len(members), verified=True)))
