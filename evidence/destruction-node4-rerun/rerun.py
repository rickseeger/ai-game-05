#!/usr/bin/env python3
"""Run existing assertions unchanged, serially, with fresh output names."""
import datetime, hashlib, json, os, pathlib, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
prefix = sys.argv[1] if len(sys.argv) > 1 else "n4s136"
logs = OUT / (prefix + "-logs")
logs.mkdir(exist_ok=False)
env = dict(os.environ)
assert pathlib.Path(env["GODOT_BIN"]).is_file()
manifest = {"source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(), "godot_sha256": hashlib.sha256(pathlib.Path(env["GODOT_BIN"]).read_bytes()).hexdigest(), "commands": []}
def run(label, args, expected=0):
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    t = time.monotonic()
    with (logs / (label + ".log")).open("w") as f:
        rc = subprocess.run(["python3", *args], cwd=ROOT, env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    manifest["commands"].append({"label": label, "argv": ["python3", *args], "cwd": str(ROOT), "GODOT_BIN": env["GODOT_BIN"], "utc_started": start, "wall_seconds": time.monotonic()-t, "returncode": rc, "expected_returncode": expected})
    (OUT / (prefix + "-commands.json")).write_text(json.dumps(manifest, indent=2)+"\n")
    print(label, "exit", rc, "expected", expected, flush=True)
    if rc != expected:
        print((logs / (label + ".log")).read_text(), flush=True)
        raise SystemExit(1)
def d(name): return "evidence/destruction/" + prefix + "-" + name
run("arena", ["scripts/run_arena.py", prefix + "-arena"])
run("arena-check", ["scripts/check_arena.py", "evidence/arena/" + prefix + "-arena", "--self-test"])
for name, flags in [("capture", []), ("rerun", ["--no-captures"]), ("seed2207", ["--seed", "2207", "--no-captures"]), ("perf1", ["--performance"]), ("perf2", ["--performance"]), ("perf3", ["--performance"]), ("no-gravity", ["--negative-gravity", "--no-captures"]), ("no-ground", ["--negative-ground", "--no-captures"])]:
    run(name, ["scripts/run_destruction.py", prefix + "-" + name, *flags], 1 if name.startswith("no-") else 0)
run("destruction-check", ["scripts/check_destruction.py", *[d(n) for n in ["capture", "rerun", "seed2207", "perf1", "perf2", "perf3"]], "--self-test", "--negative", d("no-gravity"), "--negative", d("no-ground"), "--output", str(OUT / (prefix + "-checks.json"))])
run("performance-gate", ["scripts/check_frame_target.py", *[d(n) for n in ["perf1", "perf2", "perf3"]], "--output", str(OUT / (prefix + "-performance.json"))])
run("physics-comparison", ["scripts/compare_destruction_physics.py", d("capture"), d("rerun"), "--output", str(OUT / (prefix + "-physics-comparison.json"))])
print("All fresh runs and independent checks passed", flush=True)
