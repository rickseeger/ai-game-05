#!/usr/bin/env python3
"""Serial fresh launches + independent checks. Requires numpy/scipy/Pillow.
No harness mutations. No capture FPS or subjective quality claims.
"""
import argparse, datetime, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument("prefix"); a = p.parse_args()
assert Path(a.prefix).name == a.prefix and a.prefix not in (".", "..")
out = ROOT / "evidence" / (a.prefix + "-verification")
out.mkdir(exist_ok=False)
commands = []
def run(args, filename):
    cmd = [sys.executable] + args
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
    (out/filename).write_text(r.stdout)
    commands.append({"command":cmd, "utc_started":started, "returncode":r.returncode, "output":filename})
    (out/"commands.json").write_text(json.dumps(commands,indent=2)+"\n")
    print(filename, r.returncode, flush=True)
    if r.returncode: print(r.stdout, flush=True)

sessions = ["evidence/" + a.prefix + "-session-" + str(i) for i in [1,2]]
for i,d in enumerate(sessions): run(["scripts/run_session.py", d], "session-"+str(i+1)+".log")
run(["scripts/check_session.py"]+sessions, "session-checks.json")
for mode in ["focused", "inactive", "active"]:
    run(["scripts/run_opposition.py", a.prefix+"-"+mode, "--scenario", mode], mode+".log")
opposition = ["evidence/opposition/"+a.prefix+"-"+mode for mode in ["focused","inactive","active"]]
run(["scripts/check_opposition.py"]+opposition+["--self-test",opposition[2],opposition[1]], "opposition-checks.json")
run(["scripts/check_opposition_cue.py",opposition[0]], "cue-checks.json")
run(["scripts/check_combat_audio.py",opposition[0],"--self-test"], "combat-audio-checks.json")
run(["scripts/run_controls.py",a.prefix+"-controls"], "controls.log")
run(["scripts/check_controls.py","evidence/controls/"+a.prefix+"-controls","--self-test"], "controls-checks.json")
run(["scripts/run_destruction.py",a.prefix+"-physics","--no-captures"], "physics.log")
run(["scripts/check_destruction.py","evidence/destruction/"+a.prefix+"-physics","--self-test"], "physics-checks.json")
run(["scripts/run_audio.py",a.prefix+"-audio"], "audio.log")
run(["scripts/check_audio.py","evidence/audio/"+a.prefix+"-audio","--self-test"], "audio-checks.json")
passed = all(c["returncode"] == 0 for c in commands)
summary = {"passed":passed, "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(), "commands":len(commands), "limits":"Session runs are isolated rules fixtures; opposition inactive/active runs use existing natural threat/counterplay drivers, not full-session victories. Audio is offline engine mixer, not speakers. No perception or performance claims."}
(out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary),flush=True)
sys.exit(0 if passed else 1)
