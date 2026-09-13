#!/usr/bin/env python3
"""Render original and batched rings; never headless or fabricated screenshots."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "evidence/destruction" / sys.argv[1]
out.mkdir(parents=True, exist_ok=False)
cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", os.environ["GODOT_BIN"],
       "--path", str(ROOT / "game"), "--script", "res://tests/ring_batch_tests.gd",
       "--rendering-method", "gl_compatibility", "--audio-driver", "Dummy",
       "--resolution", "1280x720", "--disable-vsync", "--max-fps", "60"]
env = dict(os.environ, RING_TEST_OUT=str(out), LIBGL_ALWAYS_SOFTWARE="1", GODOT_SILENCE_ROOT_WARNING="1")
with (out / "engine.log").open("w") as log:
    p = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        code = p.wait(timeout=120)
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGTERM)
        p.wait()
        code = 124
(out / "launch.json").write_text(json.dumps({"command": cmd, "returncode": code,
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "environment": {k: env[k] for k in ["RING_TEST_OUT", "LIBGL_ALWAYS_SOFTWARE", "GODOT_SILENCE_ROOT_WARNING"]}}, indent=2))
print((out / "engine.log").read_text())
sys.exit(code)
