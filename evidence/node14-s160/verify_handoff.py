#!/usr/bin/env python3
import datetime, hashlib, json, os, platform, shutil, subprocess, tarfile, time, urllib.request
from pathlib import Path
W = Path(__file__).resolve().parent
EXPECTED = "1fc3c4121aed811406a1e34475f5d8abf99850c0b7cc9cde41c91f1f1373e6cf"
SOURCE = "42e3bd348b22590ba504ef5ebcb55dbd8443e652"
COMMIT = "c3147c7c37fd14aa6c2f03354483b54a7473aa30"
URL = "https://raw.githubusercontent.com/rickseeger/ai-game-05/"+COMMIT+"/downloads/breakwater-42e3bd348b22/breakwater-linux-x86_64.tar.gz"
def sha(p):
    with p.open("rb") as f: return hashlib.file_digest(f,"sha256").hexdigest()
report = {"utc_started": datetime.datetime.now(datetime.timezone.utc).isoformat(), "download_url":URL, "delivery_commit":COMMIT, "source_revision":SOURCE, "commands":[], "environment":{"uname":list(os.uname()),"glibc":platform.libc_ver()}, "scope":"Fresh HTTPS retrieval, archive identity/manifest, documented tar extraction and launcher, additional forced integration/pixel assertions. Full natural gameplay/physics/mixer acceptance remains referenced node8-s158 evidence; not rerun here."}
def save(): (W/"delivery-verification.json").write_text(json.dumps(report,indent=2)+"\n")
save()
D=W/"downloaded"; D.mkdir(exist_ok=False)
for suffix in ["", ".sha256"]:
    target=D/("breakwater-linux-x86_64.tar.gz"+suffix)
    with urllib.request.urlopen(URL+suffix,timeout=120) as response, target.open("wb") as f:
        entry={"url":URL+suffix,"final_url":response.url,"status":response.status,"headers":dict(response.headers),"authentication":"none"}
        shutil.copyfileobj(response,f)
    entry.update(bytes=target.stat().st_size,sha256=sha(target))
    report.setdefault("retrievals",[]).append(entry);save()
A=D/"breakwater-linux-x86_64.tar.gz"
assert sha(A)==EXPECTED
assert (D/(A.name+".sha256")).read_text()==EXPECTED+"  "+A.name+"\n"
original=Path("/opt/g-harness/workspace/G12/node_8_step_158/dist")/A.name
assert sha(original)==EXPECTED and A.read_bytes()==original.read_bytes()
V=W/"fresh verification with spaces";V.mkdir(exist_ok=False)
R=V/"breakwater-linux-x86_64"
L=W/"verification-logs";L.mkdir(exist_ok=False)
env=dict(os.environ,LIBGL_ALWAYS_SOFTWARE="1",GODOT_SILENCE_ROOT_WARNING="1",XDG_DATA_HOME=str(V/"smoke-userdata"),PYTHONDONTWRITEBYTECODE="1")
def run(cmd,name,cwd,timeout=240):
    start=time.monotonic()
    with (L/name).open("w") as log: p=subprocess.run(list(map(str,cmd)),cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
    report["commands"].append({"command":list(map(str,cmd)),"cwd":str(cwd),"returncode":p.returncode,"seconds":time.monotonic()-start,"log":"verification-logs/"+name});save()
    print(name,p.returncode,flush=True)
    assert p.returncode==0, (L/name).read_text()
run(["sha256sum","-c",A.name+".sha256"],"checksum.log",D)
with tarfile.open(A) as t:
    members=t.getmembers()
    assert all(m.isfile() and m.name.startswith("breakwater-linux-x86_64/") and ".." not in Path(m.name).parts for m in members)
run(["tar","-xzf",A],"extraction.log",V)
m=json.loads((R/"RELEASE.json").read_text());assert m["source_revision"]==SOURCE
assert not (R/"game/.godot").exists()
def manifest():
    for n,s in m["files"].items():
        f=R/n
        assert sha(f)==s["sha256"] and f.stat().st_size==s["bytes"] and f.stat().st_mode & 0o777 == s["mode"],n
manifest();assert len(members)==len(m["files"])+1
report.update(verified_archive_members=len(members),fresh_cache_absent_before_launch=True,original_and_download_byte_identical=True)
engine=R/"runtime/Godot_v4.5.1-stable_linux.x86_64"
env["GODOT_BIN"]=str(engine)
run(["ldd",engine],"ldd.log",R)
run(["xvfb-run","-a","./launch.sh","--audio-driver","Dummy","--quit-after","120","--max-fps","60","--verbose"],"launch.log",R)
text=(L/"launch.log").read_text();assert "ERROR" not in text and "OpenGL" in text and (R/"game/.godot").exists()
run(["xvfb-run","-a",R/"launch.sh","--audio-driver","Dummy","--quit-after","30","--max-fps","60"],"unrelated-cwd-launch.log",W)
assert "ERROR" not in (L/"unrelated-cwd-launch.log").read_text()
py="/opt/g-harness/workspace/G12/node_8_step_157/.validation-venv/bin/python"
run([py,R/"scripts/run_integration.py",L/"integration"],"integration-run.log",R)
run([py,R/"scripts/check_integration.py",L/"integration"],"integration-checks.json",R)
report["integration"]=json.loads((L/"integration-checks.json").read_text())
manifest();assert sha(A)==EXPECTED and sha(original)==EXPECTED
report.update(passed=True,sha256=sha(A),bytes=A.stat().st_size,release_files_unchanged=True,limitations="Only Linux x86_64/glibc X11/OpenGL on Xvfb/Mesa llvmpipe server tested. Dummy audio here; accepted node8 mixer PCM is not subjective listening or desktop speakers. Rick hardware, physical controls, readability and fun unverified. No nodes completed or human verdict solicited.")
save()
index={str(p.relative_to(L)):{"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted(L.rglob("*")) if p.is_file()}
(W/"verification-log-index.json").write_text(json.dumps(index,indent=2)+"\n")
archive=W/"verification-logs.tar.gz"
with tarfile.open(archive,"w:gz") as t:
    for name in index: t.add(L/name,arcname=name)
with tarfile.open(archive) as t:
    for name,info in index.items(): assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==info["sha256"]
print(json.dumps({"passed":True,"download_url":URL,"sha256":sha(A),"integration":report["integration"]},indent=2))
