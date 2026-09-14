#!/usr/bin/env python3
"""Package actual worker runs; verify every archive member before cleanup."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tarfile,tempfile
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT.parent
OUT=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def archive(name,items):
    rows=[]
    with tarfile.open(OUT/name,"w:gz") as tar:
        for p,arc in sorted(items,key=lambda item:item[1]):
            if p.name == "movie.avi" or p.suffix == ".cache":continue
            tar.add(p,arcname=arc,recursive=False)
            rows.append({"path":arc,"bytes":p.stat().st_size,"sha256":digest(p)})
    with tarfile.open(OUT/name,"r:gz") as tar:
        members=tar.getmembers();assert len(members)==len(rows)
        for member,row in zip(members,rows):
            assert member.name==row["path"] and hashlib.sha256(tar.extractfile(member).read()).hexdigest()==row["sha256"]
    return rows

dirs=sorted(p for p in (ROOT/"evidence").rglob("n12-s153*") if p.is_dir())
raw=[];dev=[]
for d in dirs:
    target=raw if d.name.startswith("n12-s153-final") else dev
    target.extend((p,str(p.relative_to(ROOT))) for p in d.rglob("*") if p.is_file())
local_files=[p for p in WORK.iterdir() if p.is_file() and p.name not in ("delivery-verification.json",)]
for p in local_files:
    dev.append((p,"worker-context/"+p.name))
for d in WORK.glob("development-integration-*"):
    if d.is_dir(): dev.extend((p,"worker-context/"+str(p.relative_to(WORK))) for p in d.rglob("*") if p.is_file())
clean=[(p,"clean-integration/"+str(p.relative_to(WORK/"clean-integration"))) for p in (WORK/"clean-integration").rglob("*") if p.is_file()]
clean.extend((p,p.name) for p in WORK.glob("clean-*") if p.is_file())
manifest={"source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"archives":{},"excluded_patterns":["movie.avi (redundant, PCM and MP4 retained)","*.cache (disposable shader cache)"]}
for name,items in [("raw-runs.tar.gz",raw),("development-history.tar.gz",dev),("clean-remote-verification.tar.gz",clean)]:
    manifest["archives"][name]=archive(name,items)
archive_rechecks=[]
with tempfile.TemporaryDirectory(prefix="archive-check-",dir=WORK) as temp:
    with tarfile.open(OUT/"raw-runs.tar.gz","r:gz") as tar:tar.extractall(temp,filter="data")
    base=Path(temp)/"evidence"
    for script,args in [("check_integration.py",[str(base/"n12-s153-final-integration-1"),str(base/"n12-s153-final-integration-2")]),("check_audio.py",[str(base/"audio/n12-s153-final-regression-audio"),"--self-test"])]:
        command=[str(ROOT/".tools/validation-venv/bin/python"),str(ROOT/"scripts"/script)]+args
        result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
        assert result.returncode==0,result.stdout
        archive_rechecks.append({"command":command,"returncode":result.returncode,"result":json.loads(result.stdout)})
verify=ROOT/"evidence/n12-s153-final-integration-verification"
reg=ROOT/"evidence/n12-s153-final-regression-verification"
summary=json.loads((verify/"summary.json").read_text())
summary["archive_rechecks"]=archive_rechecks
summary["integration_checks"]=json.loads((verify/"integration-checks.json").read_text())
summary["accepted_regressions"]=json.loads((reg/"summary.json").read_text())
summary["clean_remote_execution"]=json.loads((WORK/"clean-verification.json").read_text())
summary["clean_remote_checks"]=json.loads((WORK/"clean-checks.json").read_text())
(OUT/"verification.json").write_text(json.dumps(summary,indent=2)+"\n")
shutil.copy2(WORK/"prerequisites.json",OUT/"prerequisites.json")
shutil.copy2(verify/"plain-default-engine.log",OUT/"plain-default-engine.log")
(OUT/"source.diff").write_text(subprocess.check_output(["git","diff","ea9bab25d6de2caac5939d91c123f2a818c1e78f","HEAD","--","game","scripts","docs/session-integration.md","README.md"],cwd=ROOT,text=True))
cap=OUT/"captures";cap.mkdir(exist_ok=True)
for name in ["default-playing","paused-visible","paused-4x3","victory-fixture","death-fixture","timeout-fixture","extraction-open-fixture","final-retry-paused"]:
    shutil.copy2(ROOT/"evidence/n12-s153-final-integration-1"/(name+".png"),cap/(name+".png"))
manifest["files"]=[{"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":digest(p)} for p in sorted(OUT.rglob("*")) if p.is_file() and p.name not in ("artifact-manifest.json","SHA256SUMS")]
(OUT/"artifact-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
(OUT/"SHA256SUMS").write_text("".join(digest(p)+"  "+str(p.relative_to(ROOT))+"\n" for p in sorted(OUT.rglob("*")) if p.is_file() and p.name!="SHA256SUMS"))
print(json.dumps({"archive_members":{name:len(rows) for name,rows in manifest["archives"].items()},"all_archive_hashes_verified":True,"files":len(manifest["files"])},indent=2))
