#!/usr/bin/env python3
"""Fresh Linux rendered process running integration fixtures via the ACTUAL DEFAULT ENTRY."""
import argparse, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
from release_context import source_commit, source_status
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("output", type=Path)
a = p.parse_args()
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
godot = Path(os.environ.get("GODOT_BIN", ROOT / ".tools/Godot_v4.5.1-stable_linux.x86_64")).resolve()
cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", str(godot), "--path", str(ROOT / "game"), "--rendering-method", "gl_compatibility", "--audio-driver", "Dummy", "--resolution", "1280x720", "--disable-vsync", "--fixed-fps", "60", "--", "--integration-test"]
env = dict(os.environ, INTEGRATION_OUT=str(out), XDG_DATA_HOME=str(out / "userdata"), LIBGL_ALWAYS_SOFTWARE="1", GODOT_SILENCE_ROOT_WARNING="1")
meta = {"command": cmd, "source_commit": source_commit(), "source_status": source_status(), "source_sha256": {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT / "game").rglob("*")) if f.is_file() and ".godot" not in f.parts}, "engine_sha256": hashlib.sha256(godot.read_bytes()).hexdigest(), "uname": list(os.uname()), "environment": {k: env[k] for k in ["INTEGRATION_OUT", "XDG_DATA_HOME", "LIBGL_ALWAYS_SOFTWARE", "GODOT_SILENCE_ROOT_WARNING"]}, "scope": "Forced terminal/reset fixtures plus ordinary controls; rendered X11/software OpenGL, Dummy audio; no natural playability, speaker, perception or performance claim."}
t = time.monotonic()
with (out / "engine.log").open("w") as log:
    process = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        rc = process.wait(timeout=180)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait()
        rc = 124
meta.update(returncode=rc, wall_seconds=time.monotonic()-t)
(out / "launch.json").write_text(json.dumps(meta, indent=2)+"\n")
text = (out / "engine.log").read_text()
print(text)
valid = rc == 0 and "ERROR" not in text and (out / "results.json").exists()
if valid:
    r = json.loads((out / "results.json").read_text())
    valid = r["passed"] and bool(r["checks"]) and all(c["pass"] for c in r["checks"])
print(json.dumps({"valid":valid, "output":str(out), "returncode":rc}))
sys.exit(0 if valid else 1)
