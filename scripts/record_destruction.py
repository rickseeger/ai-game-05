#!/usr/bin/env python3
"""Supplemental real-time X11 recording; NOT an acceptance timing run.
Invokes the original benchmark engine argv on a private Xvfb, adding only external
screen capture. Records full 1280x1024 display (1280x720 game window unchanged).
"""
import argparse
import datetime
import gzip
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import time

p = argparse.ArgumentParser()
p.add_argument("launch", type=Path, help="existing baseline/corrected launch.json")
p.add_argument("output", type=Path, help="new evidence directory")
a = p.parse_args()
a.output = a.output.resolve()
a.output.mkdir(parents=True, exist_ok=False)
launch = json.loads(a.launch.read_text())
cmd = launch["command"][4:]
assert cmd[0].endswith("Godot_v4.5.1-stable_linux.x86_64")
assert "--performance" in cmd and "--no-captures" in cmd
read_fd, write_fd = os.pipe()
xcmd = ["Xvfb", "-displayfd", str(write_fd), "-screen", "0", "1280x1024x24", "-nolisten", "tcp"]
xlog = (a.output / "xvfb.log").open("w")
xvfb = subprocess.Popen(xcmd, pass_fds=[write_fd], stdout=xlog, stderr=subprocess.STDOUT)
os.close(write_fd)
recorder = None
engine = None
try:
    assert select.select([read_fd], [], [], 10)[0], "Xvfb readiness timeout"
    display = ":" + os.read(read_fd, 64).decode().strip()
    os.close(read_fd)
    env = dict(os.environ, **launch["environment"])
    env.update(DISPLAY=display, DESTRUCTION_OUT=str(a.output))
    fcmd = ["ffmpeg", "-y", "-f", "x11grab", "-video_size", "1280x1024", "-framerate", "30",
            "-i", display, "-an", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-threads", "1", str(a.output / "runtime.mp4")]
    utc_start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    with (a.output / "ffmpeg.log").open("w") as flog, (a.output / "engine.log").open("w") as elog:
        recorder = subprocess.Popen(fcmd, stdout=flog, stderr=subprocess.STDOUT)
        engine = subprocess.Popen(cmd, env=env, stdout=elog, stderr=subprocess.STDOUT)
        code = engine.wait(timeout=150)
        recorder.send_signal(signal.SIGINT)
        recorder_code = recorder.wait(timeout=20)
    metadata = {"command": cmd, "xvfb_command": xcmd, "ffmpeg_command": fcmd,
                "engine_returncode": code, "ffmpeg_returncode": recorder_code,
                "utc_started": utc_start, "wall_seconds": time.monotonic()-start,
                "source_launch": str(a.launch.resolve()), "source_commit": launch["source_commit"],
                "source_sha256": launch["source_sha256"],
                "environment": {k: env[k] for k in ["DISPLAY", "DESTRUCTION_OUT", "DESTRUCTION_SEED", "LIBGL_ALWAYS_SOFTWARE"]},
                "not_acceptance_timing": True, "visual_assessment": "UNASSESSED"}
    (a.output / "recording.json").write_text(json.dumps(metadata, indent=2))
    probe = subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(a.output / "runtime.mp4")], text=True)
    (a.output / "video.json").write_text(probe)
    physics = a.output / "physics.csv"
    with gzip.open(str(physics)+".gz", "wb") as f:
        f.write(physics.read_bytes())
    physics.unlink()
    assert code == 0 and int(json.loads(probe)["streams"][0]["nb_frames"]) > 500
    print(json.dumps(metadata, indent=2))
finally:
    for process in [engine, recorder, xvfb]:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=20)
    xlog.close()
