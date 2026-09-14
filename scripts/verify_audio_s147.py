#!/usr/bin/env python3
"""Focused node5 rerun, unchanged game sources; fresh names required."""
import datetime, hashlib, json, os, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
os.chdir(root)
out = root / "evidence/audio-node5-s147"
out.mkdir(exist_ok=False)
py = sys.executable
engine = str(root / ".tools/Godot_v4.5.1-stable_linux.x86_64")
analysis_py = str(root / ".tools/audio-venv/bin/python")
commands = []
def run(name, args):
    record = dict(name=name, command=args, utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    with (out / (name + ".log")).open("w") as log:
        record["returncode"] = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, timeout=600).returncode
    commands.append(record)
    (out / "commands.json").write_text(json.dumps(commands, indent=2)+"\n")
    print(name, record["returncode"], flush=True)
    assert record["returncode"] == 0, name
provenance = json.loads((root / "game/audio/provenance.json").read_text())
run("regenerate", [py, "scripts/generate_sound_assets.py"])
for name, expected in provenance["assets"].items():
    assert hashlib.sha256((root / "game/audio" / name).read_bytes()).hexdigest() == expected["sha256"]
(out / "provenance-check.json").write_text(json.dumps(dict(byte_identical=True, asset_count=len(provenance["assets"]), provenance=provenance), indent=2)+"\n")
run("import", [engine, "--headless", "--path", "game", "--editor", "--import", "--quit"])
run("audio", [py, "scripts/run_audio.py", "n5s147"])
run("audio-check", [analysis_py, "scripts/check_audio.py", "evidence/audio/n5s147", "--self-test"])
run("spatial", [py, "scripts/run_audio.py", "n5s147-spatial", "--spatial"])
run("spatial-check", [analysis_py, "scripts/check_audio_spatial.py", "evidence/audio/n5s147-spatial", "--self-test"])
run("combat", [py, "scripts/run_opposition.py", "n5s147", "--scenario", "focused"])
run("combat-check", [py, "scripts/check_combat_audio.py", "evidence/opposition/n5s147", "--self-test"])
run("transport", [py, "scripts/run_audio_transport.py", "n5s147-transport", "--wav", "evidence/audio/n5s147/runtime.wav"])
run("transport-check", [analysis_py, "scripts/check_audio.py", "evidence/audio/n5s147", "--transport", "evidence/audio/n5s147-transport", "--self-test"])
