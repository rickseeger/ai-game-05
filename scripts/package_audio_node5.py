#!/usr/bin/env python3
"""Package step-143 actual runs; verify archive before removing loose duplicates."""
import hashlib, json, platform, shutil, subprocess, tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"evidence/audio-node5-s143"
out.mkdir(exist_ok=False)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads((ROOT/p).read_text())
report="evidence/n5s143-final-report"
base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
production={}
for f in sorted((ROOT/"game").rglob("*")):
    if not f.is_file() or ".godot" in f.parts or "tests" in f.parts: continue
    path=str(f.relative_to(ROOT))
    original=subprocess.check_output(["git","show",base+":"+path],cwd=ROOT)
    assert hashlib.sha256(original).hexdigest()==digest(f), path
    production[path]=digest(f)
summary={"base_main":base,"production_unchanged":True,"contract":"docs/audio-contract.json",
    "audio":read("evidence/audio/n5s143-final/analysis.json"),
    "combat":read(report+"/combat-audio-check.log"),
    "active_input_combat":read(report+"/active-audio.json"),
    "physics":read(report+"/physics-comparison.json"),
    "performance":read(report+"/performance.json"),
    "controls":{k:v for k,v in read(report+"/controls-check.log").items() if k!="runs"},
    "controls_assertions":99,
    "asset_regeneration":read(report+"/asset-regeneration.json"),
    "diagnostic_failures":read(report+"/diagnostic-failures.json"),
    "listening":"NOT PERFORMED: no physical card or auditory perception. Forceful/clear/satisfying sound remains unverified; human exact-release playtest required.",
    "production_sha256":production,
    "source_asset_provenance":"game/audio/provenance.json",
    "engine_sha256":digest(ROOT/".tools/Godot_v4.5.1-stable_linux.x86_64"),
    "python3":platform.python_version(),
    "signal_python":subprocess.check_output([str(ROOT/".tools/audio-venv/bin/python"),"--version"],text=True).strip(),
    "signal_packages":subprocess.check_output([str(ROOT/".tools/audio-venv/bin/python"),"-c","import numpy,scipy;print(numpy.__version__,scipy.__version__)"],text=True).strip()}
summary["controls_assertions"]=read("evidence/controls/n5s143-final/results.json")["checks"].__len__()
(out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
directories=sorted({p for p in (ROOT/"evidence").glob("n5s143*") if p.is_dir()} | {p for parent in ["audio","destruction","controls","opposition"] for p in (ROOT/"evidence"/parent).glob("n5s143*") if p.is_dir()})
files=sorted(f for d in directories for f in d.rglob("*") if f.is_file() and f.name!="movie.avi")
members=[dict(path=str(f.relative_to(ROOT)),bytes=f.stat().st_size,sha256=digest(f)) for f in files]
archive=out/"runtime-evidence.tar.gz"
with tarfile.open(archive,"w:gz",compresslevel=6) as t:
    for f in files: t.add(f,arcname=str(f.relative_to(ROOT)),recursive=False)
with tarfile.open(archive) as t:
    assert len(t.getmembers())==len(members)
    for m in members:
        b=t.extractfile(m["path"]).read()
        assert len(b)==m["bytes"] and hashlib.sha256(b).hexdigest()==m["sha256"]
authored=["game/tests/opposition_tests.gd","scripts/check_combat_audio.py","scripts/rerun_audio_node5.py","scripts/run_audio_transport.py","scripts/verify_audio_playback.py","scripts/package_audio_node5.py","docs/audio-node5-s143.md"]
manifest={"base_main":base,"report":"docs/audio-node5-s143.md","archive":str(archive.relative_to(ROOT)),"archive_bytes":archive.stat().st_size,"archive_sha256":digest(archive),"members_verified":True,"member_count":len(members),"members":members,"authored_or_modified":{f:digest(ROOT/f) for f in authored},"summary_sha256":digest(out/"summary.json"),"extract":"tar -xzf evidence/audio-node5-s143/runtime-evidence.tar.gz","no_durable_node_completion_claim":True}
(out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
checksums=[*[(ROOT/f) for f in authored],out/"summary.json",out/"manifest.json",archive]
(out/"SHA256SUMS").write_text("".join(digest(f)+"  "+str(f.relative_to(ROOT))+"\n" for f in checksums))
# Verified bytes are retained in the committed archive; remove only this run’s
# generated directories, never existing evidence or production files.
for d in directories: shutil.rmtree(d)
print(json.dumps({"archive":str(archive),"members":len(members),"bytes":archive.stat().st_size,"verified":True},indent=2))
