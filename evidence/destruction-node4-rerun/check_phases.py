#!/usr/bin/env python3
"""Assert frame/physics phase correlation from existing actual-engine outputs.
Run analyze.py first. Pixel checks establish motion/stability, not visual quality.
"""
import csv, datetime, gzip, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
prefix = sys.argv[1]
frames = json.loads((OUT / (prefix + "-frames.json")).read_text())["frames"]
directory = ROOT / "evidence/destruction" / (prefix + "-capture")
selected = {f["observed_tick"] for f in frames}
times = {}
with gzip.open(directory / "physics.csv.gz", "rt") as file:
    for r in csv.DictReader(file):
        tick = int(r["tick"])
        if tick in selected:
            times.setdefault(tick, []).append(float(r["unix_seconds"]))
assert all(b["unix_seconds"] > a["unix_seconds"] for a,b in zip(frames, frames[1:]))
correlation = []
for f in frames:
    t = f["observed_tick"]
    lag = f["unix_seconds"] - max(times[t]) if t in times else None
    if lag is not None:
        assert -.001 <= lag < 1, (f["file"], lag)
    correlation.append({"file": f["file"], "observed_tick": t,
        "utc_captured": datetime.datetime.fromtimestamp(f["unix_seconds"], datetime.timezone.utc).isoformat(),
        "capture_minus_last_body_sample_seconds": lag,
        "note": "No body rows after cleanup" if lag is None else "Same observed physics tick; asynchronous rendered frame, not exact simultaneous pose"})
by_name = {f["file"]: f for f in frames}
def frame(tick): return by_name["frame_%04d.png" % tick]
for tick in [10,30,60,90,96,102,108,114,120,126,132,138,144,150,210,300,450,511,540,600,631,660,720,900,930,1020,1190,1385]:
    assert frame(tick)["changed_pixels_from_previous"] > 100, tick
for tick in [10,30]:
    assert frame(tick)["bodies_at_observed_tick"] == 32
    assert frame(tick)["solver_contact_bodies"] == 0
assert frame(60)["solver_contact_bodies"] > 0
assert 0 < frame(210)["sleeping_bodies"] < 32
for tick in [300,390]:
    assert frame(tick)["sleeping_bodies"] == 32
assert frame(300)["sha256"] == frame(390)["sha256"]
assert frame(390)["changed_pixels_from_previous"] == 0
for tick in [490,1385]: assert frame(tick)["bodies_at_observed_tick"] == 0
for tick in [511,540,600,631,660,720,900,930,1020]:
    assert frame(tick)["bodies_at_observed_tick"] == 192
result = {"passed": True, "prefix": prefix, "correlation": correlation,
    "asserted": ["strictly increasing capture UTC", "same-observed-tick body sample/capture lag under one second", "launch, flight, ground interaction and overload change actual pixels", "natural settling transitions to pixel-identical resting frames", "shrink and complete cleanup", "repeated simultaneous breaks at cap"],
    "limitations": ["Whole-image pixel differences include shadows/UI; do not establish individual fragment visibility or subjective weight", "Physics telemetry establishes collision/spin/rebound, not inference from pixels", "Subjective quality belongs to node 9 human exact-release playtest"]}
(OUT / (prefix + "-phase-checks.json")).write_text(json.dumps(result, indent=2) + "\n")
print("PASS: timestamp correlation and actual rendered launch/impact/settling/cleanup phase checks")
