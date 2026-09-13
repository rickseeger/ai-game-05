#!/usr/bin/env python3
"""Independent trace/input/physics checker. Never infer playability from a pass."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from check_arena import image_data

ROOT = Path(__file__).resolve().parents[1]


def distance(a, b):
    return math.hypot(a[0]-b[0], a[2]-b[2])


def trace_checks(trace):
    samples, events, shots = (trace[k] for k in ("samples", "events", "shots"))
    assert len(samples) >= 2000 and len(events) >= 400, "truncated trace"
    assert [s["tick"] for s in samples] == list(range(1, len(samples)+1)), "noncontiguous ticks"
    by_tick = {s["tick"]: s for s in samples}
    assert all(abs(s["dt"]-1/60) < 1e-9 for s in samples), "physics rate"
    assert {e["type"] for e in events} >= {"key", "motion", "button", "fixture_position", "fixture_terminal"}
    for code, axis, sign in [(87, 2, -1), (65, 0, -1), (83, 2, 1), (68, 0, 1)]:
        phase = "movement_" + str(code)
        press = next(e for e in events if e["phase"] == phase and e["type"] == "key" and e["physical_keycode"] == code and e["pressed"])
        before = by_tick[press["tick"]]["position"]
        first = by_tick[press["tick"]+1]["position"]
        end = by_tick[press["tick"]+12]["position"]
        assert abs((first[axis]-before[axis])*sign-5/60) < .003, "press next tick"
        assert abs((end[axis]-before[axis])*sign-1) < .003, "movement speed"
        release = next(e for e in events if e["phase"] == phase and e["type"] == "key" and e["physical_keycode"] == code and not e["pressed"] and e["tick"] > press["tick"])
        rest = by_tick[release["tick"]]["position"]
        assert all(distance(by_tick[release["tick"]+i]["position"], rest) < .001 for i in range(1, 13)), "release stuck"
    ds = [s for s in samples if s["phase"] == "diagonal" and "move_up" in s["held"]]
    assert len(ds) == 60
    origin = by_tick[ds[0]["tick"]-1]["position"]
    assert abs(distance(origin, ds[-1]["position"])-5) < .005, "diagonal normalization"
    # Global continuous actor bound, not just the single final assertion per wall.
    assert all(abs(s["position"][axis]) <= 11.602 for s in samples for axis in (0, 2)), "actor left arena"
    walls = {"wall_87": (2, -1), "wall_65": (0, -1), "wall_83": (2, 1), "wall_68": (0, 1)}
    for phase, (axis, sign) in walls.items():
        ss = [s for s in samples if s["phase"] == phase]
        assert max(s["position"][axis]*sign for s in ss) > 11.59, "wall was not reached"
    for phase, axis, sign, limit in [("cover_west", 2, -1, -2.9), ("cover_east", 0, -1, -4.9), ("cover_north", 2, -1, 3.1)]:
        ss = [s for s in samples if s["phase"] == phase]
        peak = max(s["position"][axis]*sign for s in ss)
        assert limit-.004 < peak <= limit+.001, "cover collision"
    dash_samples = [s for s in samples if s["phase"] == "dash_open"]
    changes = [(by_tick[s["tick"]-1], s) for s in dash_samples if s["tick"] > 1 and s["dash_count"] > by_tick[s["tick"]-1]["dash_count"]]
    assert len(changes) == 2, "held dash repeat/cooldown"
    assert changes[1][1]["tick"]-changes[0][1]["tick"] >= 120
    assert all(abs(distance(a["position"], b["position"])-3) < .003 for a, b in changes), "dash distance"
    aim_shots = [s for s in shots if s["phase"] == "aim_and_fire"]
    assert len(aim_shots) == 4, "hold/release fire count"
    assert [b["tick"]-a["tick"] for a,b in zip(aim_shots, aim_shots[1:])] == [21,21,21], "fire cadence"
    for shot in shots:
        state = by_tick[shot["tick"]]
        assert state["state"] == 0 and state["aim_valid"] and "fire" in state["held"], "unrequested shot"
        target, pos, direction, origin = (shot[k] for k in ("aim_point", "position", "direction", "origin"))
        length = distance(target, pos)
        expected = [(target[0]-pos[0])/length, 0, (target[2]-pos[2])/length]
        assert sum(a*b for a,b in zip(expected, direction)) > .99999, "wrong shot targeting"
        assert abs(direction[1]) < 1e-9 and abs(distance(origin, pos)-.25) < .001, "unsafe muzzle origin"
    paused = [s for s in samples if s["phase"] == "pause_held" and s["state"] == 1]
    assert len(paused) >= 30 and paused[0]["dash_remaining"] > 1.9
    for field in ("position", "elapsed", "dash_remaining", "fire_remaining", "shot_count"):
        assert all(s[field] == paused[0][field] for s in paused), "pause drift: "+field
    resumed = [s for s in samples if s["phase"] == "resume_held"][:14]
    assert len(resumed) == 14 and all(distance(s["position"], paused[0]["position"]) < .001 and s["shot_count"] == paused[0]["shot_count"] for s in resumed), "resume stuck controls"
    generations = sorted({s["generation"] for s in samples})
    assert generations == [1,2,3,4], "restart count"
    for generation in generations[1:]:
        first = next(s for s in samples if s["generation"] == generation)
        assert first["state"] == 0 and distance(first["position"], [0,0,10]) < .001
        assert first["shot_count"] == first["dash_count"] == first["dash_remaining"] == first["fire_remaining"] == 0, "restart stale state"
        assert any(e["type"] == "key" and e["physical_keycode"] == 82 and e["pressed"] and e["tick"] == first["tick"]-1 for e in events), "restart not R driven"
    return {"ticks": len(samples), "injected_events": len(events), "emitted_shots": len(shots),
        "fire_tick_intervals": [21,21,21], "generations": generations,
        "maximum_actor_extent_m": max(abs(s["position"][a]) for s in samples for a in (0,2))}


def validate(directory):
    directory = Path(directory)
    report = json.loads((directory/"results.json").read_text())
    launch = json.loads((directory/"launch.json").read_text())
    assert launch["returncode"] == 0
    assert report["passed"] and not report["failures"]
    checks = report["checks"]
    assert len(checks) == 99 and all(c["pass"] for c in checks)
    assert len({c["name"] for c in checks}) == len(checks)
    assert report["display"] == "X11" and report["renderer"] == "gl_compatibility"
    log = (directory/"engine.log").read_text()
    assert "CONTROLS_TEST_DONE checks=99 failures=0" in log and "OpenGL API" in log
    assert "ERROR:" not in log and "SCRIPT ERROR" not in log
    for path, digest in launch["source_sha256"].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, "runtime source differs: "+path
    result = trace_checks(json.loads((directory/"trace.json").read_text()))
    width, height = map(int, launch["command"][launch["command"].index("--resolution")+1].split("x"))
    resized = [960,720] if width > 1000 else [1280,720]
    assert report["captures"] == ["initial.png", "aim_cover.png", "resized_target.png", "paused_controls.png", "final_restart.png"]
    frames = [image_data(directory/name, [width,height] if index < 2 else resized)[1]
              for index, name in enumerate(report["captures"])]
    assert len({f["sha256"] for f in frames}) == 5
    result.update(directory=str(directory), assertions=len(checks), frames=frames)
    return result


def self_test(directory):
    baseline = json.loads((Path(directory)/"trace.json").read_text())
    rejected = []
    for name in ["missing_input_events", "static_movement", "outside_wall", "wrong_targeting", "pause_clock_drift", "restart_stale_shots"]:
        bad = copy.deepcopy(baseline)
        if name == "missing_input_events": bad["events"] = []
        elif name == "static_movement":
            for s in bad["samples"]:
                if s["phase"] == "movement_87": s["position"] = [-7,0,5]
        elif name == "outside_wall": bad["samples"][100]["position"][0] = 15
        elif name == "wrong_targeting": bad["shots"][0]["direction"] = [1,0,0]
        elif name == "pause_clock_drift":
            next(s for s in bad["samples"] if s["phase"] == "pause_held" and s["state"] == 1)["elapsed"] += 1
        elif name == "restart_stale_shots":
            next(s for s in bad["samples"] if s["generation"] == 2)["shot_count"] = 99
        try:
            trace_checks(bad)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError("negative accepted: "+name)
    return rejected


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directories", nargs="+")
    p.add_argument("--negative-dir")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    result = {"runs": [validate(d) for d in a.directories]}
    if a.self_test:
        result["rejected_trace_mutations"] = self_test(a.directories[0])
    if a.negative_dir:
        directory = Path(a.negative_dir)
        report = json.loads((directory/"results.json").read_text())
        assert not report["passed"] and report["failures"] == ["negative_control_wall_must_stop"]
        assert json.loads((directory/"launch.json").read_text())["returncode"] == 1
        try:
            trace_checks(json.loads((directory/"trace.json").read_text()))
        except AssertionError as error:
            assert str(error) == "actor left arena"
            result["runtime_negative_rejected"] = str(error)
        else:
            raise AssertionError("disabled collision accepted")
    result["passed"] = True
    print(json.dumps(result, indent=2))
