#!/usr/bin/env python3
"""Focused node-2 renderer rerun; fresh directories only, no dense experiments."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument("--prefix", required=True)
p.add_argument("--report-dir", required=True)
a = p.parse_args()
os.chdir(ROOT)
report = Path(a.report_dir).resolve()
report.mkdir(parents=True, exist_ok=True)
logs = report / "logs"
logs.mkdir(exist_ok=False)
assert Path(a.prefix).name == a.prefix and a.prefix not in (".", "..")
engine = Path(os.environ["GODOT_BIN"]).resolve()
def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name, value):
    (report / name).write_text(json.dumps(value, indent=2) + chr(10))
assert not git("diff", "HEAD", "--", "game", "scripts")
source = git("rev-parse", "HEAD")
save("provenance.json", {
    "source_revision": source,
    "prior_independently_validated_revision": "ed443098523eb09094b9024f42d45a3e4117897e",
    "repository": git("remote", "get-url", "origin"),
    "started_utc": datetime.now(timezone.utc).isoformat(),
    "engine": str(engine), "engine_sha256": sha(engine),
    "engine_version": subprocess.check_output([str(engine), "--version"], text=True).strip(),
    "uname": list(os.uname()), "python": sys.version,
    "source_sha256": {f: sha(f) for f in git("ls-files", "game", "scripts").splitlines()},
    "production_changes_since_prior_validation": git("diff", "--stat", "ed443098523eb09094b9024f42d45a3e4117897e", "HEAD", "--", "game"),
    "arena_camera_changes_since_prior_validation": git("diff", "ed443098523eb09094b9024f42d45a3e4117897e", "HEAD", "--", "game/arena.gd", "game/arena_camera.gd", "game/arena_preview.gd", "game/tests/arena_tests.gd", "scripts/run_arena.py", "scripts/check_arena.py"),
    "prerequisite": json.loads(Path("evidence/arena/prerequisite.json").read_text()),
    "scope": "Node 2 technical execution only; no tree writes or subjective acceptance."})
commands = []
def run(name, argv, expected=0):
    start = time.monotonic()
    command = [sys.executable, *argv]
    logfile = logs / (name + ".log")
    with logfile.open("w") as stream:
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=180)
    commands.append({"name": name, "command": command, "cwd": str(ROOT),
        "returncode": result.returncode, "expected_returncode": expected,
        "elapsed_seconds": time.monotonic() - start, "log": str(logfile)})
    save("commands.json", commands)
    print(name, result.returncode, flush=True)
    assert result.returncode == expected, name
for suffix, size in [("720p", "1280x720"), ("4x3", "960x720")]:
    run(suffix, ["scripts/run_arena.py", a.prefix + "-" + suffix, "--size", size])
run("negative", ["scripts/run_arena.py", a.prefix + "-negative", "--negative-camera"], 1)
run("tour", ["scripts/run_arena.py", a.prefix + "-tour", "--tour-frames", "720"])
def directory(suffix):
    return "evidence/arena/" + a.prefix + "-" + suffix
run("arena-checks", ["scripts/check_arena.py", directory("720p"), directory("4x3"),
    "--negative-dir", directory("negative"), "--tour-dir", directory("tour"), "--self-test"])
save("arena-checks.json", json.loads((logs / "arena-checks.log").read_text()))
assert not git("diff", "HEAD", "--", "game", "scripts")
assert git("rev-parse", "HEAD") == source
print("FOCUSED_RENDERER_VERIFIED", flush=True)
