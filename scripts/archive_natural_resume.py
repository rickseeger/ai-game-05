#!/usr/bin/env python3
"""Archive node-13 validation evidence, not a game release. Run at repo root.
Reads each newly made archive back and hashes every member; leaves originals intact.
"""
import hashlib, json, shutil, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"evidence/node13-s155"
NAMES = ["controller-n13-movie","controller-n13-replay","controller-realtime-retry","controller-timeout-retry","controller-n13-timeout","controller-n13-verification","s155-fresh-replay"]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest = {}; archives = {}
    for name in NAMES:
        directory = ROOT/".tools"/name
        archive = OUT/(name+".tar.gz")
        files = sorted(p for p in directory.rglob("*") if p.is_file() and "shader_cache" not in p.parts)
        with tarfile.open(archive,"w:gz",compresslevel=6) as t:
            for p in files:
                key = str(p.relative_to(ROOT))
                manifest[key] = {"sha256":digest(p),"size":p.stat().st_size,"archive":archive.name}
                t.add(p,arcname=key,recursive=False)
        seen = []
        with tarfile.open(archive) as t:
            for m in t:
                assert m.isfile()
                expected = manifest[m.name]
                assert m.size == expected["size"]
                assert hashlib.sha256(t.extractfile(m).read()).hexdigest() == expected["sha256"]
                seen.append(m.name)
        assert set(seen) == {str(p.relative_to(ROOT)) for p in files}
        archives[archive.name] = {"sha256":digest(archive),"size":archive.stat().st_size,"members":len(seen)}
    # Independently check the already committed previous-worker archives too.
    old = ROOT/"evidence/node13-s154"
    previous = json.loads((old/"artifact-manifest.json").read_text())
    checked = 0
    for archive in sorted({v["archive"] for v in previous.values()}):
        with tarfile.open(old/archive) as t:
            seen = []
            for m in t:
                assert m.isfile()
                expected = previous[m.name]
                assert m.size == expected["size"] and hashlib.sha256(t.extractfile(m).read()).hexdigest() == expected["sha256"]
                seen.append(m.name); checked += 1
        assert set(seen) == {k for k,v in previous.items() if v["archive"] == archive}
    for line in (old/"SHA256SUMS").read_text().splitlines():
        h,n = line.split(None,1); assert digest(old/n.strip()) == h
    for src,dst in [("game.mp4","fresh-natural-session.mp4"),("audio.wav","fresh-actual-game-mixer.wav"),("analysis.json","fresh-analysis.json"),("launch.json","fresh-launch.json")]:
        shutil.copy2(ROOT/".tools/s155-fresh-replay"/src,OUT/dst)
    (OUT/"archive-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    summary = {"passed":True,"archives":archives,"members":len(manifest),"previous_worker_members_verified":checked,"excluded":"Disposable shader caches only; MovieWriter already removed redundant AVI after decoding and recording its SHA256. Incomplete controller timeout retained as failure evidence, never counted as a passing run."}
    (OUT/"archive-verification.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__ == "__main__": main()
