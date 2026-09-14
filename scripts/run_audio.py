#!/usr/bin/env python3
"""Capture actual rendered Godot damage/physics + the engine mixer in one AVI clock.
No fabricated audio, no alternate solver; MovieWriter is not speaker evidence.
"""
import argparse, datetime, hashlib, json, os, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument("output"); a = p.parse_args()
assert Path(a.output).name == a.output and a.output not in (".", "..")
out = ROOT / "evidence/audio" / a.output
out.mkdir(parents=True, exist_ok=False)
godot = os.environ.get("GODOT_BIN", str(ROOT / ".tools/Godot_v4.5.1-stable_linux.x86_64"))
env = dict(os.environ, AUDIO_OUT=str(out), XDG_DATA_HOME=str(out / "userdata"), LIBGL_ALWAYS_SOFTWARE="1", GODOT_SILENCE_ROOT_WARNING="1")
cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", godot, "--path", str(ROOT / "game"), "res://destruction_demo.tscn", "--rendering-method", "gl_compatibility", "--resolution", "1280x720", "--audio-driver", "Dummy", "--fixed-fps", "60", "--disable-vsync", "--write-movie", str(out / "movie.avi"), "--", "--audio-test"]
meta = {"command": cmd, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "clock": "MovieWriter 60fps, 60Hz actual GodotPhysics, 48000Hz mixer; offline not real-time or speakers", "engine_sha256": hashlib.sha256(Path(godot).read_bytes()).hexdigest(), "uname": list(os.uname()), "base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "source_sha256": {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT / "game").rglob("*")) if f.is_file() and ".godot" not in f.parts and f.suffix != ".uid"}, "environment": {k:env[k] for k in ["AUDIO_OUT", "XDG_DATA_HOME", "LIBGL_ALWAYS_SOFTWARE", "GODOT_SILENCE_ROOT_WARNING"]}}
start = time.monotonic()
with (out / "engine.log").open("w") as log:
    rc = subprocess.run(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=240).returncode
meta.update(returncode=rc, wall_seconds=time.monotonic()-start)
(out / "launch.json").write_text(json.dumps(meta, indent=2)+"\n")
print((out / "engine.log").read_text())
assert rc == 0 and "SCRIPT ERROR" not in (out / "engine.log").read_text()
r = json.loads((out / "results.json").read_text()); assert r["passed"]
commands = [["ffmpeg", "-y", "-i", str(out/"movie.avi"), "-vn", "-c:a", "pcm_s32le", str(out/"runtime.wav")], ["ffmpeg", "-y", "-i", str(out/"movie.avi"), "-c:v", "libx264", "-crf", "20", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out/"runtime.mp4")]]
with (out / "encode.log").open("w") as log:
    for command in commands:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)
meta["encode_commands"] = commands
meta["original_avi_sha256"] = hashlib.sha256((out/"movie.avi").read_bytes()).hexdigest()
(out / "launch.json").write_text(json.dumps(meta, indent=2)+"\n")
(out / "video.json").write_text(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(out / "runtime.mp4")], text=True))
print(json.dumps({"checks": len(r["checks"]), "passed": r["passed"], "output": str(out)}))
