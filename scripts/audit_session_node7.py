#!/usr/bin/env python3
"""Bounded node-7 readiness audit, NOT full-game acceptance. No gameplay writes."""
import argparse, datetime, hashlib, json, os, re, subprocess, sys, tarfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument("prefix")
a = p.parse_args()
assert Path(a.prefix).name == a.prefix and a.prefix not in (".", "..")
out = ROOT / "evidence" / a.prefix
out.mkdir(exist_ok=False)
commands = []
def dump(name, value):
    (out/name).write_text(json.dumps(value, indent=2)+"\n")
def run(cmd, filename):
    r = subprocess.run(cmd, cwd=ROOT, env=os.environ, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=600)
    (out/filename).write_text(r.stdout)
    commands.append({"command":cmd, "returncode":r.returncode, "output":filename})
    dump("commands.json", commands)
    assert r.returncode == 0, r.stdout
    print(filename, r.returncode, flush=True)
    return r.stdout
base = subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
tracked = subprocess.check_output(["git","ls-files","game"],cwd=ROOT,text=True).splitlines()
hashes = {}
for f in tracked:
    data = (ROOT/f).read_bytes()
    assert data == subprocess.check_output(["git","show",base+":"+f],cwd=ROOT)
    hashes[f] = hashlib.sha256(data).hexdigest()
godot = os.environ.get("GODOT_BIN", str(ROOT/".tools/Godot_v4.5.1-stable_linux.x86_64"))
version = run([godot,"--version"],"engine-version.txt").strip()
# Required on fresh clones: WAV descriptors alone are not the imported streams.
run([godot,"--headless","--path","game","--editor","--import","--quit"],"import.log")
scenario = a.prefix + "-inactive"
run([sys.executable,"scripts/run_opposition.py",scenario,"--scenario","inactive","--capture"],"inactive.log")
directory = ROOT / "evidence/opposition" / scenario
run([sys.executable,"scripts/check_opposition.py",str(directory)],"independent-checks.json")
r = json.loads((directory/"results.json").read_text())
pixels = []
raws = []
for f in sorted(directory.glob("frame_*.png")):
    raw = subprocess.check_output(["ffmpeg","-v","error","-i",str(f),"-f","rawvideo","-pix_fmt","rgb24","-threads","1","-"])
    assert len(raw) == 1280*720*3
    unique = len(set(zip(raw[::3],raw[1::3],raw[2::3])))
    assert unique > 100
    pixels.append({"file":str(f.relative_to(ROOT)),"unique_rgb_colors":unique,"rgb_sha256":hashlib.sha256(raw).hexdigest()})
    raws.append(raw)
assert len(raws) >= 2
changed = sum(raws[0][i:i+3] != raws[-1][i:i+3] for i in range(0,len(raws[0]),3))
assert changed > 100
dump("pixel-checks.json", {"frames":pixels,"first_last_changed_pixels":changed,
    "scope":"Nonuniform rendered frames and temporal change only; not text recognition or visual judgment."})
pattern = re.compile(r"State\.WON|finish\(|exit_transform|objectives_changed|destroyed\.connect|elapsed|func clear|func start")
references = [{"file":str(f.relative_to(ROOT)),"line":i,"text":s}
    for f in sorted((ROOT/"game").glob("*.gd")) for i,s in enumerate(f.read_text().splitlines(),1) if pattern.search(s)]
dump("source-survey.json", {"source_commit":base,"references":references,
    "main_scene":(ROOT/"game/project.godot").read_text(),
    "method":"Read all production session scripts and inspect references across top-level game scripts. Symbol search supports manual source review; not a universal proof over arbitrary programs."})
for f,digest in hashes.items():
    assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest() == digest
dump("provenance.json", {"source_commit":base,"engine_version":version,
    "engine_sha256":hashlib.sha256(Path(godot).read_bytes()).hexdigest(),
    "tracked_game_files_unchanged":True,"game_sha256":hashes,
    "utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope":"Readiness audit + natural inactivity loss in opposition slice; NOT complete session validation.",
    "runtime":{"ticks":r["ticks"],"health":r["health"],"state":r["state"],"engine_checks":len(r["checks"]),"frames":len(r["frames"])},
    "limitations":["No natural victory rule exists in current production sessions.",
        "No full-session progression/restart tests or captures were produced.",
        "This diagnostic MP4 has no audio track; no synchronized mixer-audio claim.",
        "No subjective visual, listening, tension or fun judgment.",
        "Existing inactive driver starts the ordinary seed 1201 once; it then sends no input and makes no health, position, target or terminal mutations."]})
# Keep raw engine evidence reproducibly in a single tracked archive.
archive = out/"raw-inactive.tar.gz"
files = sorted(f for f in directory.rglob("*") if f.is_file())
manifest = {str(f.relative_to(ROOT)):{"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()} for f in files}
with tarfile.open(archive,"w:gz") as tar:
    for f in files: tar.add(f,arcname=str(f.relative_to(ROOT)))
with tarfile.open(archive,"r:gz") as tar:
    assert len(tar.getmembers()) == len(manifest)
    for m in tar.getmembers():
        b=tar.extractfile(m).read()
        assert len(b)==manifest[m.name]["bytes"] and hashlib.sha256(b).hexdigest()==manifest[m.name]["sha256"]
dump("artifact-manifest.json", {"archive":str(archive.relative_to(ROOT)),"sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"members":manifest,"readback_verified":True})
print(json.dumps({"output":str(out),"runtime_checks_passed":True,"complete_game":False}))
