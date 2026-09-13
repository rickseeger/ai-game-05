#!/usr/bin/env python3
"""Analyze actual rendered frames/physics; no image-perception or realism verdict."""
import csv, gzip, hashlib, json, math, pathlib, re, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from check_arena import image_data
prefix = sys.argv[1] if len(sys.argv)>1 else "n4s136"
D = ROOT / "evidence/destruction" / (prefix + "-capture")
d = json.loads((D / "results.json").read_text())
ticks = {f["observed_tick"] for f in d["frames"]}
by_tick = {t: [] for t in ticks}
with gzip.open(D / "physics.csv.gz", "rt") as f:
    for row in csv.DictReader(f):
        tick = int(row["tick"])
        if tick in ticks: by_tick[tick].append(row)
frames = []
previous = None
for f in d["frames"]:
    raw, image = image_data(D / f["file"], [1280,720])
    rows = by_tick[f["observed_tick"]]
    changed = None if previous is None else sum(any(a != b for a,b in zip(raw[i:i+3], previous[i:i+3])) for i in range(0,len(raw),3))
    frames.append({**f, **image, "changed_pixels_from_previous": changed, "bodies_at_observed_tick": len(rows), "solver_contact_bodies": sum(int(r["contacts"])>0 for r in rows), "sleeping_bodies": sum(int(r["sleeping"]) for r in rows), "height_range_m": [min(float(r["y"]) for r in rows), max(float(r["y"]) for r in rows)] if rows else None})
    previous = raw
assert len(frames)==32
(OUT / (prefix + "-frames.json")).write_text(json.dumps({"frames": frames, "limitation": "Pixel differences establish changed renderer output, not subjective weight, independent visibility of every block, or crowded-scene readability. Contact counts come from physics, not image interpretation."}, indent=2)+"\n")
base = "f6631e436e3caedc33f705bec65a5a646db609da"
def old(name): return subprocess.check_output(["git", "show", base + ":" + name], cwd=ROOT)
def digest(data): return hashlib.sha256(data).hexdigest()
unchanged = {}
for name in ["game/debris_block.gd", "game/tests/destruction_tests.gd", "game/destructible_target.gd", "game/destruction_demo.gd", "game/destruction_demo.tscn", "scripts/run_destruction.py", "scripts/check_destruction.py", "scripts/check_frame_target.py"]:
    unchanged[name] = {"sha256": digest((ROOT/name).read_bytes()), "identical_to_node10": old(name)==(ROOT/name).read_bytes()}
    assert unchanged[name]["identical_to_node10"], name
name = "game/destruction.gd"
a = old(name).decode(); b = (ROOT/name).read_text()
# The existing post-node10 change is the rendering material, not physical settings.
a = a.replace("var material := StandardMaterial3D.new()\n    material.vertex_color_use_as_albedo = true\n    material.roughness = 0.86", "var material := ShaderMaterial.new()\n    material.shader = preload(\"res://debris_surface.gdshader\")\n    material.set_shader_parameter(\"instance_colors\", true)")
assert a==b
name = "game/arena.gd"
def ring(text): return re.search(r"static func ring\(.*?(?=\n(?:static )?func |\Z)",text,re.S).group()
assert ring(old(name).decode())==ring((ROOT/name).read_text())
launch=json.loads((D / "launch.json").read_text())
for name, sha in launch["source_sha256"].items(): assert digest((ROOT/name).read_bytes())==sha
comparison=json.loads((OUT / (prefix+"-physics-comparison.json")).read_text())
historical=json.loads((ROOT / "evidence/destruction-remediation/physics-comparison.json").read_text())
assert comparison["baseline"]["physics_sha256_without_wall_time"]==historical["corrected"]["physics_sha256_without_wall_time"]
(OUT / (prefix+"-provenance.json")).write_text(json.dumps({"source_commit":launch["source_commit"], "node10_source_commit":base, "unchanged_files":unchanged, "ring_function_identical_to_node10":True, "destruction_diff_only_existing_render_material":True, "game_source_matches_launch_hashes":True, "historical_node10_fixed_step_hash_matches":True, "fixed_step_hash": comparison["baseline"]["physics_sha256_without_wall_time"], "frame_count":len(frames), "distinct_capture_hashes":len({f["sha256"] for f in frames}), "renderer":d["renderer"], "engine":d["engine"], "logical_cpus":launch["logical_cpus"], "cpuinfo":launch["cpuinfo"], "uname":launch["uname"]},indent=2)+"\n")
(OUT / (prefix+"-arena-checks.json")).write_text((OUT / (prefix+"-logs/arena-check.log")).read_text())
print("PASS: frame analysis, current source hashes, original workload, ring optimization and historical fixed-step hash")
