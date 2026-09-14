#!/usr/bin/env python3
"""Private virtual playback diagnostic. Never substitutes null transport for ears.
No changes to default/system PulseAudio. Poll readiness; stop only our child.
"""
import argparse, json, os, subprocess, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("output")
p.add_argument("--wav", type=Path, required=True)
a = p.parse_args()
assert Path(a.output).name == a.output and a.output not in (".", "..")
logdir = ROOT / "evidence" / (a.output + "-daemon")
logdir.mkdir(exist_ok=False)
with tempfile.TemporaryDirectory(prefix="g12-audio-") as tmp:
    socket = str(Path(tmp)/"pulse.sock")
    env = dict(os.environ, PULSE_SERVER="unix:"+socket, PULSE_SINK="g12_audio_validation")
    cmd = ["pulseaudio", "-n", "--daemonize=no", "--use-pid-file=no", "--exit-idle-time=-1", "--disable-shm=yes", "--log-target=stderr",
           "--load=module-native-protocol-unix socket="+socket+" auth-anonymous=1",
           "--load=module-null-sink sink_name=g12_audio_validation rate=48000 channels=2"]
    meta = {"command": cmd, "private_socket_directory_mode": oct(Path(tmp).stat().st_mode & 0o777), "listening": "NONE: virtual null sink only; no auditory perception"}
    with (logdir/"pulse.log").open("w") as log:
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic()+10
            while True:
                r = subprocess.run(["pactl", "list", "sinks", "short"], env=env, capture_output=True, text=True, timeout=3)
                if r.returncode == 0 and "g12_audio_validation" in r.stdout:
                    (logdir/"ready.txt").write_text(r.stdout)
                    break
                assert proc.poll() is None and time.monotonic() < deadline, r.stderr
                time.sleep(.05)  # readiness polling, never blind startup sleep
            verify = ["python3", "scripts/verify_audio_playback.py", a.output, "--wav", str(a.wav.resolve())]
            meta["verification_command"] = verify
            with (logdir/"verify.log").open("w") as vlog:
                result = subprocess.run(verify, cwd=ROOT, env=env, stdout=vlog, stderr=subprocess.STDOUT, timeout=240)
            meta["verification_returncode"] = result.returncode
        finally:
            if proc.poll() is None:
                proc.terminate()
            meta["daemon_exitcode"] = proc.wait(timeout=15)
            meta["daemon_stopped"] = proc.poll() is not None
            (logdir/"lifecycle.json").write_text(json.dumps(meta, indent=2)+"\n")
    assert meta["verification_returncode"] == 0, str(logdir/"verify.log")
print(json.dumps(meta, indent=2))
