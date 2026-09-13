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
p.add_argument("output", help="new directory relative to repo/evidence/arena")
p.add_argument("--size", default="1280x720")
p.add_argument("--negative-camera", action="store_true")
p.add_argument("--tour-frames", type=int, default=0, help="normal real-time animated preview, bounded frame count")
a = p.parse_args()
if not a.output or Path(a.output).name != a.output or a.output in (".", ".."):
    p.error("output must be a single new directory name")
width, height = map(int, a.size.split("x"))
if min(width, height) < 360:
    p.error("use at least 360 pixels on each axis")
out = ROOT / "evidence" / "arena" / a.output
out.mkdir(parents=True, exist_ok=False)
godot = Path(os.environ.get("GODOT_BIN", str(ROOT / ".tools/Godot_v4.5.1-stable_linux.x86_64"))).resolve()
cmd = ["xvfb-run", "-a", "-s", f"-screen 0 {max(width,1280)}x{max(height,1024)}x24", str(godot),
       "--path", str(ROOT / "game"), "--rendering-method", "gl_compatibility",
       "--audio-driver", "Dummy", "--resolution", a.size, "--disable-vsync", "--max-fps", "60"]
if a.tour_frames:
    cmd += ["--quit-after", str(a.tour_frames)]
else:
    cmd += ["--", "--arena-test"]
    if a.negative_camera:
        cmd += ["--camera-negative"]
env = dict(os.environ, ARENA_OUT=str(out), GODOT_SILENCE_ROOT_WARNING="1", LIBGL_ALWAYS_SOFTWARE="1")
start = time.monotonic()
with (out / "engine.log").open("w") as log:
    process = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        returncode = process.wait(timeout=90)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait()
        returncode = 124
        log.write("\nRUNNER_TIMEOUT after 90 seconds; process group terminated\n")
metadata = {"command": cmd, "environment": {k: env[k] for k in
    ("ARENA_OUT", "GODOT_SILENCE_ROOT_WARNING", "LIBGL_ALWAYS_SOFTWARE")},
    "returncode": returncode, "wall_seconds": time.monotonic()-start,
    "uname": list(os.uname()), "python": sys.version,
    "observation": "Offscreen Xvfb software OpenGL, explicit Dummy audio; no human desktop or audio observation."}
(out / "launch.json").write_text(json.dumps(metadata, indent=2) + "\n")
print((out / "engine.log").read_text())
print(json.dumps(metadata, indent=2))
sys.exit(returncode)
