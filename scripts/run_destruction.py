#!/usr/bin/env python3
"""Fresh evidence only. Real rendering through Xvfb; never --headless."""
import argparse
import json
import os
import signal
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("output", help="new directory relative to repo/evidence/destruction")
p.add_argument("--size", default="1280x720")
p.add_argument("--negative-gravity", action="store_true")
p.add_argument("--negative-ground", action="store_true")
p.add_argument("--no-captures", action="store_true")
p.add_argument("--performance", action="store_true")
p.add_argument("--seed", type=int, default=1201)
a = p.parse_args()
if not a.output or Path(a.output).name != a.output or a.output in (".", ".."):
    p.error("output must be a single new directory name")
width, height = map(int, a.size.split("x"))
if min(width, height) < 360:
    p.error("use at least 360 pixels on each axis")
out = ROOT / "evidence" / "destruction" / a.output
out.mkdir(parents=True, exist_ok=False)
godot = Path(os.environ.get("GODOT_BIN", str(ROOT / ".tools/Godot_v4.5.1-stable_linux.x86_64"))).resolve()
cmd = ["xvfb-run", "-a", "-s", f"-screen 0 {max(width,1280)}x{max(height,1024)}x24", str(godot),
       "--path", str(ROOT / "game"), "res://destruction_demo.tscn", "--rendering-method", "gl_compatibility",
       "--audio-driver", "Dummy", "--resolution", a.size, "--disable-vsync", "--max-fps", "60"]
cmd += ["--", "--destruction-test"]
if a.negative_gravity:
    cmd += ["--negative-gravity"]
if a.negative_ground: cmd += ["--negative-ground"]
if a.performance: cmd += ["--performance", "--no-captures"]
if a.no_captures: cmd += ["--no-captures"]
env = dict(os.environ, DESTRUCTION_SEED=str(a.seed), DESTRUCTION_OUT=str(out), GODOT_SILENCE_ROOT_WARNING="1", LIBGL_ALWAYS_SOFTWARE="1")
start = time.monotonic()
with (out / "engine.log").open("w") as log:
    process = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        returncode = process.wait(timeout=150)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait()
        returncode = 124
        log.write("\nRUNNER_TIMEOUT after 150 seconds; process group terminated\n")
metadata = {"command": cmd, "environment": {k: env[k] for k in
    ("DESTRUCTION_SEED", "DESTRUCTION_OUT", "GODOT_SILENCE_ROOT_WARNING", "LIBGL_ALWAYS_SOFTWARE")},
    "returncode": returncode, "wall_seconds": time.monotonic()-start,
    "uname": list(os.uname()), "python": sys.version,
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "source_sha256": {str(path.relative_to(ROOT)): __import__("hashlib").sha256(path.read_bytes()).hexdigest() for path in sorted((ROOT / "game").rglob("*")) if path.is_file() and ".godot" not in path.parts},
    "source_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
    "utc_started": __import__("datetime").datetime.fromtimestamp(time.time()-(time.monotonic()-start), __import__("datetime").timezone.utc).isoformat(),
    "cpu": __import__("platform").processor(), "logical_cpus": os.cpu_count(),
    "cpuinfo": Path("/proc/cpuinfo").read_text().split("\n\n")[0],
    "observation": "Offscreen Xvfb software OpenGL, explicit Dummy audio; no human desktop or audio observation."}
(out / "launch.json").write_text(json.dumps(metadata, indent=2) + "\n")
for path in [out / "physics.csv"]:
    if path.exists():
        import gzip
        with gzip.open(str(path)+".gz", "wb") as f: f.write(path.read_bytes())
        path.unlink()
print((out / "engine.log").read_text())
print(json.dumps(metadata, indent=2))
sys.exit(returncode)
