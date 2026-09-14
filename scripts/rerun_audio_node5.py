#!/usr/bin/env python3
"""Fresh serial audio and unchanged physics/performance regression execution.
Run with python3 (3.14+ for the existing frame checker), GODOT_BIN pinned and
AUDIO_PYTHON pointing to a numpy/scipy virtualenv. Does not start audio daemons.
"""
import argparse, datetime, hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("prefix")
a = p.parse_args()
assert Path(a.prefix).name == a.prefix and a.prefix not in (".", "..")
out = ROOT / "evidence" / (a.prefix + "-report")
out.mkdir(exist_ok=False)
commands = []
def run(name, cmd):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (out / (name + ".log")).open("w") as log:
        r = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=600)
    commands.append(dict(name=name, command=cmd, utc=started, returncode=r.returncode))
    (out / "commands.json").write_text(json.dumps(commands, indent=2)+"\n")
    print(name, r.returncode, flush=True)
    assert r.returncode == 0, str(out / (name+".log"))
os.environ.setdefault("GODOT_BIN", str(ROOT / ".tools/Godot_v4.5.1-stable_linux.x86_64"))
py = sys.executable
audio_py = os.environ.get("AUDIO_PYTHON", str(ROOT / ".tools/audio-venv/bin/python"))
assets = {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/"game/audio").glob("*.wav")}
run("regenerate", [py, "scripts/generate_sound_assets.py"])
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest() == h for f,h in assets.items())
(out / "asset-regeneration.json").write_text(json.dumps(dict(byte_identical=True, assets=assets), indent=2)+"\n")
run("import", [os.environ["GODOT_BIN"], "--headless", "--path", "game", "--editor", "--import", "--quit"])
run("audio", [py, "scripts/run_audio.py", a.prefix])
run("audio-check", [audio_py, "scripts/check_audio.py", "evidence/audio/"+a.prefix, "--self-test"])
run("destruction", [py, "scripts/run_destruction.py", a.prefix, "--no-captures"])
run("destruction-check", [py, "scripts/check_destruction.py", "evidence/destruction/"+a.prefix, "--self-test"])
for i in range(1,4):
    run("perf"+str(i), [py, "scripts/run_destruction.py", a.prefix+"-perf"+str(i), "--performance"])
run("performance-check", [py, "scripts/check_frame_target.py", *["evidence/destruction/"+a.prefix+"-perf"+str(i) for i in range(1,4)], "--output", str(out/"performance.json")])
run("controls", [py, "scripts/run_controls.py", a.prefix])
run("controls-check", [py, "scripts/check_controls.py", "evidence/controls/"+a.prefix, "--self-test"])
run("opposition", [py, "scripts/run_opposition.py", a.prefix, "--scenario", "focused"])

run("combat-audio-check", [py, "scripts/check_combat_audio.py", "evidence/opposition/"+a.prefix, "--self-test"])
run("opposition-check", [py, "scripts/check_opposition.py", "evidence/opposition/"+a.prefix])

run("active", [py, "scripts/run_opposition.py", a.prefix+"-active", "--scenario", "active"])
run("active-check", [py, "scripts/check_opposition.py", "evidence/opposition/"+a.prefix+"-active"])
