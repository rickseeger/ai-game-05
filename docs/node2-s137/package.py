#!/usr/bin/env python3
"""Losslessly archive fresh evidence, verify every byte, then remove loose duplicates."""
import hashlib, json, shutil, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
import os
os.chdir(ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=Path("docs/node2-s137")
roots=sorted(Path("evidence/arena").glob("n2-s137-*"))+[report/"logs"]
files=sorted(p for d in roots for p in d.rglob("*") if p.is_file())
assert files and all(d.is_dir() for d in roots)
output=Path("evidence/node2-s137");output.mkdir(exist_ok=False)
archive=output/"runtime-evidence.tar.xz"
members=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
with tarfile.open(archive,"w:xz",preset=3) as t:
    for p in files:t.add(p,arcname=str(p),recursive=False)
with tarfile.open(archive,"r:xz") as t:
    actual=t.getmembers()
    assert len(actual)==len(members)
    for m,e in zip(actual,members):
        assert m.name==e["path"] and m.size==e["bytes"]
        assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==e["sha256"]
manifest=dict(archive=str(archive),bytes=archive.stat().st_size,sha256=sha(archive),
    members_verified=True,member_count=len(members),png_count=sum(p.suffix==".png" for p in files),members=members)
(report/"artifact-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
(output/"SHA256SUMS").write_text(sha(archive)+"  "+str(archive)+"\n")
for d in roots:shutil.rmtree(d)
print(json.dumps({k:v for k,v in manifest.items() if k!="members"},indent=2))
