#!/usr/bin/env python3
"""Fresh extraction, manifest validation and real default-game Linux processes.
Use Python 3.12 with release/requirements-test.txt; no development checkout runtime.
"""
import argparse, datetime, hashlib, json, os, platform, subprocess, sys, tarfile, time
from pathlib import Path

def sha(p):return hashlib.file_digest(p.open("rb"),"sha256").hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument("artifact",type=Path);p.add_argument("output",type=Path);a=p.parse_args()
 artifact=a.artifact.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 digest=sha(artifact);unpacked=out/"fresh directory with spaces";unpacked.mkdir()
 with tarfile.open(artifact) as tar:
  members=tar.getmembers();assert all(t.isfile() and t.name.startswith("breakwater-linux-x86_64/") and ".." not in Path(t.name).parts for t in members)
  tar.extractall(unpacked,filter="data")
 root=unpacked/"breakwater-linux-x86_64";manifest=json.loads((root/"RELEASE.json").read_text())
 assert not (root/"game/.godot").exists() and not (root/".git").exists()
 assert len(members)==len(manifest["files"])+1
 for n,s in manifest["files"].items():
  f=root/n;assert sha(f)==s["sha256"] and f.stat().st_size==s["bytes"] and f.stat().st_mode&0o777==s["mode"],n
 engine=root/"runtime/Godot_v4.5.1-stable_linux.x86_64"
 env=dict(os.environ,GODOT_BIN=str(engine),LIBGL_ALWAYS_SOFTWARE="1",GODOT_SILENCE_ROOT_WARNING="1",XDG_DATA_HOME=str(out/"smoke-userdata"),PYTHONDONTWRITEBYTECODE="1")
 import numpy, scipy, PIL
 report={"artifact":str(artifact),"artifact_sha256":digest,"source_revision":manifest["source_revision"],"accepted_game_revision":manifest["accepted_game_revision"],"engine_sha256":sha(engine),"fresh_root":str(root),"fresh_cache_absent":True,"verified_members":len(members),"utc_started":datetime.datetime.now(datetime.timezone.utc).isoformat(),"environment":{"uname":list(os.uname()),"python":sys.version,"glibc":platform.libc_ver(),"numpy":numpy.__version__,"scipy":scipy.__version__,"pillow":PIL.__version__},"commands":[]}
 def save(): (out/"verification.json").write_text(json.dumps(report,indent=2)+"\n")
 def run(cmd,name,strict=True,timeout=1500):
  t=time.monotonic()
  with (out/name).open("w") as log:
   proc=subprocess.run(list(map(str,cmd)),cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
  report["commands"].append({"command":list(map(str,cmd)),"cwd":str(root),"log":name,"returncode":proc.returncode,"wall_seconds":time.monotonic()-t,"required":strict});save()
  print(name,proc.returncode,flush=True)
  if strict: assert proc.returncode==0,(name,(out/name).read_text()[-3000:])
 def script(name,*args):return [sys.executable,root/"scripts"/name,*args]
 save()
 run(["ldd",engine],"runtime-ldd.log")
 run(["xvfb-run","-a",root/"launch.sh","--audio-driver","Dummy","--quit-after","120","--max-fps","60","--verbose"],"clean-launch.log")
 assert "ERROR" not in (out/"clean-launch.log").read_text()
 assert "OpenGL" in (out/"clean-launch.log").read_text() and (root/"game/.godot").exists()
 # Non-gating native-audio diagnostic: server has no speaker device/session.
 run(["xvfb-run","-a",root/"launch.sh","--quit-after","30","--max-fps","60","--verbose"],"native-audio-diagnostic.log",strict=False)
 run(script("run_natural.py",out/"natural-movie","--movie"),"natural-movie.log")
 run(script("check_natural.py",out/"natural-movie","--self-test"),"natural-checks.log")
 run(script("check_natural_resume.py",out/"natural-movie","--output",out/"natural-supplement.json"),"natural-supplement.log")
 run(script("run_natural.py",out/"natural-realtime"),"natural-realtime.log")
 run(script("check_natural.py",out/"natural-realtime","--self-test"),"realtime-checks.log")
 for i in (1,2):run(script("run_session.py",out/("rules-"+str(i))),"rules-"+str(i)+".log")
 run(script("check_session.py",out/"rules-1",out/"rules-2"),"rules-checks.log")
 run(script("run_integration.py",out/"integration"),"integration.log")
 run(script("check_integration.py",out/"integration"),"integration-checks.log")
 for n,s in manifest["files"].items():assert sha(root/n)==s["sha256"],"Release source/runtime modified: "+n
 report.update(passed=True,unchanged_release_members_after_tests=True,limits="Xvfb + software llvmpipe; offline MovieWriter is actual mixer PCM, not speakers or realtime FPS. Unfixed realtime separately measured with observer overhead. Native audio diagnostic is not a speaker pass. No subjective visual, sound or fun verdict. Other distributions, GPUs, older glibc, Wayland and ARM unverified; Windows not built.");save()
 print(json.dumps({"passed":True,"artifact_sha256":digest,"output":str(out)},indent=2))
if __name__=="__main__":main()
