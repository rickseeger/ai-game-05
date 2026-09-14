#!/usr/bin/env python3
"""Serial, fresh-prefix engine launches and independent checks; no mission writes."""
import argparse, datetime, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("prefix")
a = p.parse_args()
assert Path(a.prefix).name == a.prefix and a.prefix not in (".", "..")
out = ROOT / "evidence" / (a.prefix + "-verification")
out.mkdir(exist_ok=False)
commands = []
def run(arguments, filename):
    cmd = [sys.executable] + arguments
    utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (out/filename).write_text(r.stdout)
    commands.append({"command":cmd, "utc_started":utc, "returncode":r.returncode, "output":filename})
    (out/"commands.json").write_text(json.dumps(commands, indent=2)+"\n")
    print(filename, r.returncode, flush=True)
    assert r.returncode == 0, r.stdout
for mode in ("focused", "inactive", "active"):
    run(["scripts/run_opposition.py", a.prefix+"-"+mode, "--scenario", mode] +
        (["--capture"] if mode != "focused" else []), mode+".log")
dirs = ["evidence/opposition/"+a.prefix+"-"+s for s in ("focused","inactive","active")]
run(["scripts/check_opposition.py"]+dirs+["--self-test",dirs[2],dirs[1]], "opposition-checks.json")
run(["scripts/check_opposition_cue.py",dirs[0]], "cue-checks.json")
run(["scripts/run_controls.py",a.prefix+"-controls"], "controls.log")
run(["scripts/check_controls.py","evidence/controls/"+a.prefix+"-controls","--self-test"], "controls-checks.json")
# Must remain serial: the negative runner briefly mutates and restores sentry.gd.
run(["scripts/test_opposition_negative.py",a.prefix+"-negative"], "negative.log")
run(["scripts/check_opposition.py"]+dirs, "post-restore-checks.json")
print(str(out))
