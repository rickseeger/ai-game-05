#!/usr/bin/env python3
"""Deterministic, allowlisted source+runtime assembly from an exact Git revision."""
import argparse, gzip, hashlib, io, json, subprocess, tarfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE="Godot_v4.5.1-stable_linux.x86_64"
ZIP_SHA="02ec53d1cc7dbb9cc6355393c61b9ab43d1244751a124f10248a4802830788cd"
ACCEPTED="7ec9261cae21cd63d68e93c1fceb1c1090e3f091"
SCRIPTS={"setup.sh","build_linux_release.py","verify_linux_release.py","release_context.py","run_natural.py","check_natural.py","check_natural_resume.py","run_integration.py","check_integration.py","run_session.py","check_session.py","generate_sound_assets.py"}
def git(*args):return subprocess.check_output(["git",*args],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",default="HEAD");p.add_argument("--engine-zip",type=Path,default=ROOT/".tools/godot.zip");p.add_argument("--output",type=Path,required=True);a=p.parse_args()
 revision=git("rev-parse",a.source+"^{commit}").decode().strip()
 assert not git("diff",ACCEPTED,revision,"--","game"), "Accepted game/driver must remain byte-identical"
 z=a.engine_zip.read_bytes();assert hashlib.sha256(z).hexdigest()==ZIP_SHA,"Engine download checksum"
 files={};modes={}
 for line in git("ls-tree","-r",revision).decode().splitlines():
  desc,name=line.split("\t");mode,kind,oid=desc.split()
  parts=Path(name).parts
  selected=parts[0] in ("game","docs","release") or name in ("LICENSE","launch.sh") or parts[0]=="scripts" and Path(name).name in SCRIPTS
  if not selected:continue
  assert mode in ("100644","100755") and not any(x in parts for x in (".godot",".tools","__pycache__","evidence",".git"))
  files[name]=git("cat-file","blob",oid);modes[name]=0o755 if mode=="100755" else 0o644
 files["README.txt"]=files["docs/linux-release.txt"];modes["README.txt"]=0o644
 with zipfile.ZipFile(io.BytesIO(z)) as archive:files["runtime/"+ENGINE]=archive.read(ENGINE)
 modes["runtime/"+ENGINE]=0o755
 manifest={"format":1,"name":"Breakwater","platform":"Linux x86_64, glibc; Godot 4.5.1; X11/OpenGL 3.3 compatibility renderer","source_repository":"git@github.com:rickseeger/ai-game-05.git","source_revision":revision,"accepted_game_revision":ACCEPTED,"engine_zip_sha256":ZIP_SHA,"engine_sha256":hashlib.sha256(files["runtime/"+ENGINE]).hexdigest(),"files":{n:{"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b),"mode":modes[n]} for n,b in sorted(files.items())}}
 files["RELEASE.json"]=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode();modes["RELEASE.json"]=0o644
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open("xb") as raw:
  with gzip.GzipFile(filename="",fileobj=raw,mode="wb",mtime=0,compresslevel=9) as gz:
   with tarfile.open(fileobj=gz,mode="w",format=tarfile.USTAR_FORMAT) as tar:
    for name,data in sorted(files.items()):
     t=tarfile.TarInfo("breakwater-linux-x86_64/"+name);t.size=len(data);t.mode=modes[name];t.uid=t.gid=t.mtime=0;t.uname=t.gname="";tar.addfile(t,io.BytesIO(data))
 digest=hashlib.sha256(a.output.read_bytes()).hexdigest()
 a.output.with_suffix(a.output.suffix+".sha256").write_text(digest+"  "+a.output.name+"\n")
 print(json.dumps({"artifact":str(a.output.resolve()),"sha256":digest,"bytes":a.output.stat().st_size,"source_revision":revision,"members":len(files)},indent=2))
if __name__=="__main__":main()
