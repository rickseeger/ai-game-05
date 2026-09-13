#!/usr/bin/env python3
"""Read-back preservation checks and lossless packaging of this worker evidence."""
import hashlib,json,os,platform,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
os.chdir(ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(["git",*args],text=True).strip()
def load(p):return json.loads(Path(p).read_text())
base="aef37d7"
source=git("rev-parse","HEAD")
old_files=git("ls-tree","-r","--name-only",base,"game").splitlines()
unchanged={p:subprocess.check_output(["git","show",base+":"+p])==Path(p).read_bytes() for p in old_files if p!="game/arena_camera.gd"}
assert all(unchanged.values())
ring=lambda s:s.split("static func ring",1)[1].split("static func label",1)[0]
ring_preserved=ring(git("show","f6631e436e3caedc33f705bec65a5a646db609da:game/arena.gd"))==ring(Path("game/arena.gd").read_text())
assert ring_preserved
comparisons=[]
for size in ["720p","4x3"]:
 b=load(f"evidence/arena/n2-s135-before-v2-dense-{size}/dense.json")
 a=load(f"evidence/arena/n2-s135-verified-v2-dense-{size}/dense.json")
 same=[x["poses"]==y["poses"] for x,y in zip(a["records"],b["records"])]
 assert all(same) and len(same)==6
 comparisons.append(dict(size=size,identical_physics_pose_snapshots=same,
     same_threat_count=all(x["sentries"]==y["sentries"]==2 for x,y in zip(a["records"],b["records"]))))
# Two distinct post-flush launches at the final camera must produce identical color bytes.
d1=Path("evidence/arena/n2-s135-settled-dense-720p");d2=Path("evidence/arena/n2-s135-settled-dense-rerun")
repeat={r["prefix"]:sha(d1/(r["prefix"]+"_color.png"))==sha(d2/(r["prefix"]+"_color.png")) for r in load(d1/"dense.json")["records"]}
assert all(repeat.values())
binary=Path(os.environ["GODOT_BIN"])
provenance=dict(baseline=git("rev-parse",base),tested_source=source,author=git("show","-s","--format=%an <%ae>"),
    production_change="Only camera direction Z/Y 0.9 -> 1.2 plus comment; every other pre-existing game file byte-identical.",
    unchanged_game_files=unchanged,node10_ring_function_identical=ring_preserved,
    source_sha256={str(p):sha(p) for p in sorted(Path("game").rglob("*")) if p.is_file() and ".godot" not in p.parts},
    binary=str(binary),binary_sha256=sha(binary),godot_version=subprocess.check_output([str(binary),"--version"],text=True).strip(),
    host=list(os.uname()),python=platform.python_version(),dense_physics_comparisons=comparisons,
    dense_repeat_identical_pngs=repeat,prerequisite="Accepted design/engine feasibility record in evidence/arena/prerequisite.json; read design and node2-s132/s133 reviews. No mission state changes.",
    authoritative_pixel_report="docs/node2-s135/pixel-checks-v2.json",
    capability_limit="No visual-perception provider used or repaired. Automated actual-renderer evidence, not subjective approval.")
Path("docs/node2-s135/provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
logs=Path("docs/node2-s135/session-logs");logs.mkdir(exist_ok=True)
for p in ROOT.parent.iterdir():
 if p.is_file() and p.suffix in [".log",".json"]:p.rename(logs/p.name)
files=sorted([p for family in ["arena","destruction","controls"] for d in Path("evidence",family).glob("n2-s135-*") for p in d.rglob("*") if p.is_file()]+list(logs.iterdir()))
out=Path("evidence/node2-s135");out.mkdir(exist_ok=True)
archive=out/"runtime-evidence.tar.xz"
manifest=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in files]
with tarfile.open(archive,"w:xz",preset=6) as t:
 for p in files:t.add(p,arcname=str(p),recursive=False)
with tarfile.open(archive,"r:xz") as t:
 members=t.getmembers();assert len(members)==len(manifest)
 for expected,member in zip(manifest,members):
  assert member.name==expected["path"] and hashlib.sha256(t.extractfile(member).read()).hexdigest()==expected["sha256"]
Path("docs/node2-s135/artifact-manifest.json").write_text(json.dumps(dict(archive=str(archive),sha256=sha(archive),bytes=archive.stat().st_size,members=manifest),indent=2)+"\n")
print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,members=len(files),pngs=sum(p.suffix==".png" for p in files),source=source,preservation=True,repeat=repeat),indent=2))
