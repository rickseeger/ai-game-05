#!/usr/bin/env python3
"""Fresh Linux renderer verification; no mission-state writes. Run from repo root."""
import argparse, hashlib, json, os, platform, subprocess, sys, time
from pathlib import Path
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
p = argparse.ArgumentParser()
p.add_argument("--prefix", default="n2-s137")
p.add_argument("--report-dir", default="docs/node2-s137")
a = p.parse_args()
report = Path(a.report_dir)
report.mkdir(parents=True, exist_ok=True)
logs = report / "logs"
logs.mkdir(exist_ok=False)
assert Path(a.prefix).name == a.prefix
assert "GODOT_BIN" in os.environ

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(["git", *args], text=True).strip()
def save(name, data): (report / name).write_text(json.dumps(data, indent=2) + "\n")
source = git("rev-parse", "HEAD")
tracked = git("ls-files", "game", "scripts").splitlines()
assert not git("diff", "HEAD", "--", "game", "scripts")
save("provenance.json", dict(tested_commit=source, repository=git("remote", "get-url", "origin"),
    previous_independently_validated_commit="8f311f7643d493e7fa5be11d88feb97c93261ff4",
    game_and_test_diff_from_previous=git("diff", "8f311f7643d493e7fa5be11d88feb97c93261ff4", "HEAD", "--", "game", "scripts"),
    source_sha256={f:sha(f) for f in tracked}, binary=os.environ["GODOT_BIN"],
    binary_sha256=sha(os.environ["GODOT_BIN"]),
    engine=subprocess.check_output([os.environ["GODOT_BIN"], "--version"], text=True).strip(),
    uname=list(os.uname()), python=sys.version,
    prerequisite=json.loads(Path("evidence/arena/prerequisite.json").read_text()),
    scope="Node 2 renderer/camera only; no node state changes or other-node acceptance."))
commands=[]
def run(name, args, expected=0):
    cmd=[sys.executable, *args]
    start=time.monotonic()
    with (logs/(name+".log")).open("w") as f:
        result=subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=300)
    commands.append(dict(name=name, command=cmd, cwd=str(ROOT), returncode=result.returncode,
        expected_returncode=expected, elapsed_seconds=time.monotonic()-start, log=str(logs/(name+".log"))))
    save("commands.json", commands)
    print(name, result.returncode, flush=True)
    assert result.returncode==expected, name

def directory(s): return str(Path("evidence/arena")/(a.prefix+"-"+s))
for suffix,size in [("720p","1280x720"),("4x3","960x720"),("wide","1680x720")]:
    run(suffix,["scripts/run_arena.py",a.prefix+"-"+suffix,"--size",size])
run("negative",["scripts/run_arena.py",a.prefix+"-negative","--negative-camera"],1)
run("tour",["scripts/run_arena.py",a.prefix+"-tour","--tour-frames","720"])
for suffix,size in [("720p","1280x720"),("4x3","960x720")]:
    run("analytic-"+suffix,["scripts/run_visibility.py",a.prefix+"-analytic-"+suffix,"--size",size])
    run("dense-"+suffix,["scripts/run_dense_visibility.py",a.prefix+"-dense-"+suffix,"--size",size])
run("arena-checks",["scripts/check_arena.py",directory("720p"),directory("4x3"),directory("wide"),
    "--negative-dir",directory("negative"),"--tour-dir",directory("tour"),"--self-test"])
save("arena-checks.json",json.loads((logs/"arena-checks.log").read_text()))
sys.path.insert(0,str(ROOT/"scripts"))
from test_visibility import run as check_pixels
pixels=check_pixels(SimpleNamespace(analytic=[directory("analytic-720p"),directory("analytic-4x3")],
    dense=[directory("dense-720p"),directory("dense-4x3")],before=[]))
save("pixel-checks.json",pixels)
summary=dict(passed=True,analytic=[r["summary"] for r in pixels["analytic"]],dense=[])
for r in pixels["dense"]:
    summary["dense"].append(dict(directory=r["directory"], perspective=r["perspective"],
        minimum_cubes_with_3_pixels=min(x["cubes_with_3_pixels"] for x in r["records"]),
        minimum_shadow_pixels=min(x["shadow_darkened_non_debris_pixels"] for x in r["records"]),
        minimum_retained_fraction={n:min(x["landmarks"][n]["retained_fraction"] for x in r["records"]) for n in ["actor","contact","exit","label"]}))
summary["rejected_pixel_mutations"]=pixels["rejected_mutations"]
save("summary.json",summary)
assert not git("diff", "HEAD", "--", "game", "scripts")
print(json.dumps(summary,indent=2),flush=True)
