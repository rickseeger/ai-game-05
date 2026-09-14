#!/usr/bin/env python3
import datetime, hashlib, json, shutil, tarfile
from pathlib import Path
root=Path.cwd(); docs=Path("docs/node2-s138"); out=Path("evidence/node2-s138")
out.mkdir(exist_ok=False)
files=sorted(p for d in Path("evidence/arena").glob("n2-s138-*") for p in d.rglob("*") if p.is_file())
files+=sorted((docs/"logs").glob("*.log"))+[docs/"concerns.log"]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=[dict(path=str(p),size=p.stat().st_size,sha256=sha(p),saved_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()) for p in files]
(docs/"artifact-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
archive=out/"runtime-evidence.tar.xz"
with tarfile.open(archive,"w:xz",preset=6) as t:
    for p in files:t.add(p,arcname=str(p),recursive=False)
with tarfile.open(archive,"r:xz") as t:
    assert len(t.getmembers())==len(manifest)
    for row in manifest:
        b=t.extractfile(row["path"]).read()
        assert len(b)==row["size"] and hashlib.sha256(b).hexdigest()==row["sha256"]
(out/"SHA256SUMS").write_text(sha(archive)+"  "+str(archive)+"\n")
for d in Path("evidence/arena").glob("n2-s138-*"):shutil.rmtree(d)
shutil.rmtree(docs/"logs");(docs/"concerns.log").unlink()
print(json.dumps(dict(verified_members=len(manifest),pngs=sum(x["path"].endswith(".png") for x in manifest),archive_bytes=archive.stat().st_size,archive_sha256=sha(archive))))
