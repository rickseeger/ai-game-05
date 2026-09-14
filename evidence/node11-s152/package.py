#!/usr/bin/env python3
"""Package only this worker's fresh outputs, retaining member hashes."""
import hashlib, json, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence/node11-s152"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
roots = [ROOT / "evidence" / ("n11-s152-"+s) for s in ["verification","session-1","session-2"]]
roots += [ROOT / "evidence/opposition" / ("n11-s152-"+s) for s in ["focused","inactive","active"]]
roots += [ROOT/"evidence/controls/n11-s152-controls", ROOT/"evidence/destruction/n11-s152-physics", ROOT/"evidence/audio/n11-s152-audio"]
files = sorted(p for directory in roots for p in directory.rglob("*") if p.is_file() and p.name != "movie.avi")
manifest = []
with tarfile.open(OUT/"raw-runs.tar.gz","w:gz") as archive:
    for f in files:
        name = str(f.relative_to(ROOT))
        archive.add(f,arcname=name)
        manifest.append({"path":name,"bytes":f.stat().st_size,"sha256":sha(f)})
with tarfile.open(OUT/"raw-runs.tar.gz") as archive:
    assert len(archive.getmembers()) == len(manifest)
    for f in manifest:
        assert hashlib.sha256(archive.extractfile(f["path"]).read()).hexdigest() == f["sha256"]
context = [ROOT.parent/p for p in ["persisted-contract.json","initial-import.log","source-import.log"]]
context += sorted(p for p in (ROOT.parent/"development-session-1").rglob("*") if p.is_file())
development = []
with tarfile.open(OUT/"development-context.tar.gz","w:gz") as archive:
    for f in context:
        name = str(f.relative_to(ROOT.parent))
        archive.add(f,arcname=name)
        development.append({"path":name,"bytes":f.stat().st_size,"sha256":sha(f)})
with tarfile.open(OUT/"development-context.tar.gz") as archive:
    for f in development:
        assert hashlib.sha256(archive.extractfile(f["path"]).read()).hexdigest() == f["sha256"]
result = {"raw_runs":manifest,"development_context":development,"archives":{p.name:{"sha256":sha(p),"bytes":p.stat().st_size} for p in OUT.glob("*.tar.gz")},"omission":"Redundant original MovieWriter AVI excluded; original hash in audio launch.json, lossless PCM and encoded MP4 retained. Dependencies/.godot caches are not deliverables."}
(OUT/"artifact-manifest.json").write_text(json.dumps(result,indent=2)+"\n")
(OUT/"SHA256SUMS").write_text("".join(sha(p)+"  "+p.name+"\n" for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "SHA256SUMS"))
print(json.dumps({"raw_files":len(manifest),"development_files":len(development),"archives":result["archives"]},indent=2))
