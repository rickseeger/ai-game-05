#!/usr/bin/env python3
"""Fresh rendered Godot process. Movie-time captures are NOT a performance test."""
import argparse, datetime, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("output")
p.add_argument("--scenario", choices=["focused", "inactive", "active"], required=True)
p.add_argument("--capture", action="store_true")
a = p.parse_args()
if Path(a.output).name != a.output or a.output in (".", ".."):
    p.error("output must be a fresh single directory name")
out = ROOT / "evidence/opposition" / a.output
out.mkdir(parents=True, exist_ok=False)
godot = os.environ.get("GODOT_BIN", str(ROOT / ".tools/Godot_v4.5.1-stable_linux.x86_64"))
cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x1024x24", godot,
       "--path", str(ROOT / "game"), "res://opposition.tscn", "--rendering-method", "gl_compatibility",
       "--audio-driver", "Dummy", "--resolution", "1280x720", "--disable-vsync"]
cmd += ["--fixed-fps", "30"] if a.capture else ["--max-fps", "60"]
cmd += ["--", "--opposition-test"]
env = dict(os.environ, OPPOSITION_OUT=str(out), OPPOSITION_SCENARIO=a.scenario,
           OPPOSITION_CAPTURE=str(int(a.capture)), GODOT_SILENCE_ROOT_WARNING="1", LIBGL_ALWAYS_SOFTWARE="1")
metadata = {"command": cmd, "environment": {k: v for k,v in env.items() if k.startswith("OPPOSITION_") or k in ("GODOT_SILENCE_ROOT_WARNING", "LIBGL_ALWAYS_SOFTWARE")},
            "utc_started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "source_sha256": {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/"game").rglob("*")) if f.is_file() and ".godot" not in f.parts},
            "source_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
            "uname": list(os.uname()), "capture_clock": "fixed 30 rendered FPS / 60Hz physics" if a.capture else "real time",
            "observation": "Xvfb software OpenGL, Dummy audio. No subjective visual/audio assessment. Not a frame-time benchmark."}
start = time.monotonic()
with (out/"engine.log").open("w") as log:
    proc = subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    try:
        rc = proc.wait(timeout=210)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait()
        rc = 124
        log.write("\nRUNNER TIMEOUT\n")
metadata.update(returncode=rc, wall_seconds=time.monotonic()-start)
text = (out/"engine.log").read_text()
valid = rc == 0 and "SCRIPT ERROR" not in text and "ERROR:" not in text and (out/"results.json").exists()
if valid:
    result = json.loads((out/"results.json").read_text())
    valid = result["passed"] and all(c["pass"] for c in result["checks"])
if valid and a.capture:
    encode = ["ffmpeg", "-hide_banner", "-y", "-framerate", "30", "-i", str(out/"frame_%05d.png"), "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", str(out/"runtime.mp4")]
    with (out/"encode.log").open("w") as log:
        erc = subprocess.run(encode, stdout=log, stderr=subprocess.STDOUT).returncode
    metadata["encode_command"] = encode
    metadata["encode_returncode"] = erc
    valid = valid and erc == 0
    if erc == 0:
        # Preserve selected original stills; every other original frame is encoded
        # in runtime.mp4 in index order with its engine tick retained in results.
        wanted = [0, len(result["frames"])-1]
        for kind in ("spawn_warning", "aim", "player_damage", "destroyed", "player_died"):
            matches = [e for e in result["events"] if e["kind"] == kind]
            if matches:
                at = matches[0]["tick"]
                wanted.append(min(range(len(result["frames"])), key=lambda i: abs(result["frames"][i]["observed_tick"]-at-2)))
        keep = {result["frames"][i]["file"] for i in wanted}
        metadata["retained_stills"] = sorted(keep)
        for f in out.glob("frame_*.png"):
            if f.name not in keep:
                f.unlink()
        probe = subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-of", "json", str(out/"runtime.mp4")], text=True)
        (out/"video.json").write_text(probe)
        valid = valid and int(json.loads(probe)["streams"][0]["nb_read_frames"]) == len(result["frames"])
metadata["validated_runner_success"] = valid
(out/"launch.json").write_text(json.dumps(metadata, indent=2)+"\n")
print(text)
print(json.dumps({"output": str(out), "returncode": rc, "valid": valid, "wall_seconds": metadata["wall_seconds"]}))
sys.exit(0 if valid else 1)
