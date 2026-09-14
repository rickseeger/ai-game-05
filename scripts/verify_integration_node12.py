#!/usr/bin/env python3
"""Serial fresh default-entry integration + accepted-system regressions."""
import argparse, datetime, hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument("prefix");a=p.parse_args()
assert Path(a.prefix).name == a.prefix and a.prefix not in (".","..")
out=ROOT/"evidence"/(a.prefix+"-integration-verification");out.mkdir(exist_ok=False)
commands=[]
env=dict(os.environ,GODOT_BIN=str(Path(os.environ.get("GODOT_BIN",ROOT/".tools/Godot_v4.5.1-stable_linux.x86_64")).resolve()),LIBGL_ALWAYS_SOFTWARE="1",GODOT_SILENCE_ROOT_WARNING="1")
def run(cmd,filename):
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=1500)
        code,text=r.returncode,r.stdout
    except subprocess.TimeoutExpired as e:
        code,text=124,str(e.stdout)
    (out/filename).write_text(text)
    commands.append({"command":cmd,"utc_started":started,"returncode":code,"output":filename})
    (out/"commands.json").write_text(json.dumps(commands,indent=2)+"\n")
    print(filename,code,flush=True)
    if code: print(text,flush=True)
    return code
runs=["evidence/"+a.prefix+"-integration-"+str(i) for i in (1,2)]
for i,d in enumerate(runs):run([sys.executable,"scripts/run_integration.py",d],f"integration-{i+1}.log")
run([sys.executable,"scripts/check_integration.py"]+runs,"integration-checks.json")
run(["xvfb-run","-a",env["GODOT_BIN"],"--path",str(ROOT/"game"),"--audio-driver","Dummy","--quit-after","120","--max-fps","60"],"plain-default-engine.log")
# Imported, accepted fixtures stay independent of the new default-entry driver.
run([sys.executable,"scripts/verify_session_node11.py",a.prefix+"-regression"],"accepted-regressions.log")
run([sys.executable,"scripts/run_arena.py",a.prefix+"-arena"],"arena.log")
run([sys.executable,"scripts/check_arena.py","evidence/arena/"+a.prefix+"-arena"],"arena-checks.json")
run([sys.executable,"scripts/run_ring_batch.py",a.prefix+"-ring"],"ring.log")
passed=all(c["returncode"] == 0 for c in commands) and "ERROR" not in (out/"plain-default-engine.log").read_text()
summary={"passed":passed,"commands":commands,"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"engine_sha256":hashlib.sha256(Path(env["GODOT_BIN"]).read_bytes()).hexdigest(),"limits":"Forced terminal fixtures are not natural victories. Pixel checks are not readability; Dummy/mixer audio is not listening. No performance claim."}
(out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({"passed":passed,"commands":len(commands)}),flush=True)
sys.exit(0 if passed else 1)
