#!/usr/bin/env python3
"""Independent trace/image checks. Physics PASS is not a visual-quality verdict."""
import argparse
import collections
import copy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics
from check_arena import image_data

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = set("""rendered_x11 engine_451 physics_60hz gravity_9_8 three_hits_intact
collider_removed_before_burst once_only_destruction pylon_32 rigid_body_configuration
all_32_up all_32_down all_32_contact all_32_bounce all_32_spin all_32_tumble all_32_sleep
render_batch_matches_sleeping_rigid_poses payoff_retained_seven_seconds
final_second_visual_shrink eight_second_cleanup six_simultaneous_192
repeat_active_cap_192 repeat_sleeping_cap_192 stress_ttl_cleanup seed_repeatability
sentinel_16 explicit_clear session_restart_cleanup_0 session_restart_cleanup_1
session_restart_cleanup_2 pause_freezes_debris mixed_oldest_awake
mixed_younger_sleepers sleepers_before_older_active""".split())


def report_checks(d):
    assert d["passed"] and not d["failures"], "engine assertions failed"
    assert len(d["checks"]) == len(REQUIRED), "assertion count"
    assert {c["name"] for c in d["checks"]} == REQUIRED, "assertion coverage"
    assert all(c["pass"] for c in d["checks"])
    assert d["display"] == "X11" and d["peak_count"] == 192
    assert d["engine"]["string"].startswith("4.5.1")
    assert len(d["initial"]) == 32
    for axis in range(3):
        linear = [b["v"][axis] for b in d["initial"]]
        angular = [b["w"][axis] for b in d["initial"]]
        lo, hi = (4.5, 7.5) if axis == 1 else (-3.5, 3.5)
        assert min(linear) >= lo and max(linear) <= hi
        assert len(set(linear)) == 32 and max(linear)-min(linear) > (hi-lo)*0.65, "linear variation"
        assert min(angular) >= -12 and max(angular) <= 12
        assert len(set(angular)) == 32 and max(angular)-min(angular) > 16, "angular variation"
    positions = [b["p"] for b in d["initial"]]
    assert [len({p[a] for p in positions}) for a in range(3)] == [4,2,4]
    assert all(math.dist(a,b) >= 0.33999 for i,a in enumerate(positions) for b in positions[i+1:]), "overlapping boxes"
    retire = [e for e in d["events"] if e["kind"] == "retire"]
    assert len({e["id"] for e in retire}) == len(retire), "duplicate retirement"
    assert all(8 <= e["age"] < 8.02 for e in retire if e["reason"] == "ttl"), "TTL"
    for tick, sleeping in [(630,False), (900,True)]:
        selected = [e for e in retire if e["tick"] == tick and e["reason"] == "cap"]
        assert len(selected) == 96 and all(e["sleeping"] == sleeping for e in selected), "cap selection"
    first = [e for e in retire if 1 <= e["id"] <= 32]
    assert len(first) == 32 and all(e["reason"] == "ttl" and e["age"] >= 8 for e in first), "premature payoff cleanup"
    bursts = [e for e in d["events"] if e["kind"] == "burst"]
    assert len([e for e in bursts if e["tick"] == 510]) == 8 # two remaining intact pylons + six stress bursts
    assert [e["kind"] for e in d["events"] if e["tick"] == 1] == ["burst","destroyed"], "once-only order"
    impacts = [e for e in d["events"] if e["kind"] == "impact" and e["tick"] < 1390]
    assert len(impacts) > 20 and all(e["speed"] >= 1 and e["material"] == "metal" for e in impacts)
    assert all(b["engine_tick"]-a["engine_tick"] >= 3 for a,b in zip(impacts,impacts[1:])), "global impact throttle"
    last = {}
    for e in impacts:
        assert e["engine_tick"]-last.get(e["id"],-999) >= 8, "body impact cooldown"
        last[e["id"]] = e["engine_tick"]


def load_rows(directory):
    with gzip.open(Path(directory)/"physics.csv.gz", "rt") as f:
        return [{k:float(v) for k,v in row.items()} for row in csv.DictReader(f)]


def angle(a,b):
    dot = abs(sum(a[k]*b[k] for k in ("qx","qy","qz","qw")))
    return 2*math.acos(min(1,dot))


def physics_checks(rows):
    by_id = collections.defaultdict(list)
    by_tick = collections.Counter()
    for r in rows:
        by_id[int(r["id"])].append(r)
        by_tick[int(r["tick"])] += 1
    assert max(by_tick.values()) == 192, "cap exceeded or not exercised"
    assert by_tick[1] == by_tick[420] == 32
    assert by_tick[490] == by_tick[1385] == 0, "cleanup left bodies"
    assert by_tick[510] == by_tick[630] == by_tick[900] == 192
    metrics = []
    for ident in range(1,33):
        r = by_id[ident]
        assert len(r) >= 480 and r[0]["tick"] == 1 and r[-1]["tick"] <= 482, "missing arc"
        assert all(b["tick"] == a["tick"]+1 for a,b in zip(r,r[1:])), "missing physics ticks"
        assert all(b["unix_seconds"] >= a["unix_seconds"] for a,b in zip(r,r[1:])), "timestamps"
        assert max(x["y"] for x in r) > r[0]["y"]+0.7, "no rise"
        assert min(x["vy"] for x in r) < -2, "no descent"
        # Explicit discrete 60Hz Godot damping+gravity integration, before contacts.
        errors = [abs((b["vy"]-a["vy"])*60 + 9.8 + a["vy"]*.12)
            for a,b in zip(r[:30],r[1:31])]
        assert max(errors) < 0.003, "gravity integration mismatch"
        contact = next((i for i,x in enumerate(r) if x["contacts"] > 0), None)
        assert contact is not None, "no ground collision"
        assert any(a["vy"] < -.5 and b["vy"] > .3 for a,b in zip(r[contact-1:],r[contact:])), "no rebound"
        assert any(angle(a,b) > .03 for a,b in zip(r[:30],r[1:31])), "no free spin"
        assert any(b["y"] < .5 and angle(a,b) > .015 for a,b in zip(r[contact:],r[contact+1:])), "no tumble"
        late = [x for x in r if 390 <= x["tick"] <= 420]
        assert all(x["sleeping"] == 1 and .10 < x["y"] < .30 for x in late), "not settled on ground"
        assert all(math.sqrt(sum(x[k]**2 for k in ("vx","vy","vz"))) < .015 for x in late), "settling speed"
        assert math.hypot(late[-1]["vx"],late[-1]["vz"]) < math.hypot(r[0]["vx"],r[0]["vz"])*.1, "friction failed"
        assert min(x["y"] for x in r) > .05, "fell through ground"
        assert all(x["scale"] == 1 for x in r if x["age"] <= 7), "premature shrink"
        assert .4 < next(x["scale"] for x in r if x["tick"] == 451) < .6, "missing final fade"
        metrics.append({"id":ident,"apex_m":max(x["y"] for x in r),
            "first_contact_tick":int(r[contact]["tick"]),
            "first_sleep_tick":int(next(x["tick"] for x in r if x["sleeping"])),
            "gravity_error_max":max(errors),"settled_y_m":late[-1]["y"]})
    return {"samples":len(rows), "independent_arcs":len(metrics), "bodies":metrics}


def performance(directory):
    rows = list(csv.DictReader((Path(directory)/"frames.csv").open()))
    # All 192-body scene frame intervals, no dropped outliers. Capture cost is retained.
    stress = [r for r in rows if 510 <= int(r["tick"]) < 1110 and int(r["active"]) == 192]
    assert len(stress) >= 150
    def stats(key):
        values = sorted(float(r[key]) for r in stress)
        return {"median":statistics.median(values),"p95":values[math.ceil(.95*len(values))-1],"max":max(values)}
    intervals = stats("interval_ms")
    return {"frame_samples":len(stress), "window_ticks":[510,1109], "frame_ms":intervals,
        "physics_process_ms":stats("physics_ms"), "p95_target_ms":33.3,
        "meets_p95_target":intervals["p95"] <= 33.3,
        "capture_overlap_frames":sum(int(r["capture_overlap"]) for r in stress),
        "limit":"Offscreen CPU llvmpipe reference VM; not laptop or subjective smoothness acceptance."}


def validate(directory, check_source=True):
    directory = Path(directory)
    d = json.loads((directory/"results.json").read_text())
    launch = json.loads((directory/"launch.json").read_text())
    report_checks(d)
    assert launch["returncode"] == 0
    log = (directory/"engine.log").read_text()
    assert "DESTRUCTION_TEST_DONE checks=34 failures=0" in log and "ERROR:" not in log
    assert "--headless" not in launch["command"] and "--write-movie" not in launch["command"]
    assert int(launch["environment"]["DESTRUCTION_SEED"]) == d["seed"]
    if check_source:
        for name, digest in launch["source_sha256"].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, "source differs: "+name
    images=[]
    for f in d["frames"]:
        assert f["error"] == 0 and f["observed_tick"] >= f["tick"]
        images.append(image_data(directory/f["file"], [1280,720])[1])
    if not d["no_captures"]:
        assert len(images) == 32 and len({f["sha256"] for f in images}) >= 28, "frame coverage"
    result = {"directory":str(directory),"seed":d["seed"],"assertions":len(d["checks"]),
        "performance":performance(directory),"images":images,"visual_assessment":"UNASSESSED"}
    if not d["performance_only"]:
        result["physics"] = physics_checks(load_rows(directory))
    return result


def self_test(directory):
    d=json.loads((Path(directory)/"results.json").read_text())
    report_checks(d)
    rejected=[]
    for kind in ["missing_assertion","uniform_launch","uniform_spin","short_ttl"]:
        bad=copy.deepcopy(d)
        if kind=="missing_assertion":bad["checks"].pop()
        if kind=="uniform_launch":
            for b in bad["initial"]:b["v"]=[1,6,1]
        if kind=="uniform_spin":
            for b in bad["initial"]:b["w"]=[0,0,0]
        if kind=="short_ttl":
            for e in bad["events"]:
                if e["kind"]=="retire" and e["reason"]=="ttl":e["age"]=2
        try:report_checks(bad)
        except AssertionError:rejected.append(kind)
        else:raise AssertionError("mutation accepted: "+kind)
    rows=load_rows(directory)
    for kind in ["no_gravity","no_contact","no_settling","no_cleanup"]:
        bad=[r.copy() for r in rows]
        for r in bad:
            if kind=="no_gravity":r["vy"]=5
            if kind=="no_contact":r["contacts"]=0
            if kind=="no_settling":r["sleeping"]=0
        if kind=="no_cleanup":
            extra=bad[0].copy();extra["tick"]=490;bad.append(extra)
        try:physics_checks(bad)
        except AssertionError:rejected.append(kind)
        else:raise AssertionError("mutation accepted: "+kind)
    return rejected


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("directories",nargs="+")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--negative",action="append",default=[])
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result={"runs":[validate(d) for d in a.directories],"automated_passed":True,"visual_assessment":"UNASSESSED"}
    if a.self_test:result["rejected_mutations"]=self_test(a.directories[0])
    negatives=[]
    for directory in a.negative:
        d=json.loads((Path(directory)/"results.json").read_text())
        assert d["passed"] is False
        assert json.loads((Path(directory)/"launch.json").read_text())["returncode"] == 1
        try:physics_checks(load_rows(directory))
        except AssertionError as e:negatives.append({"directory":directory,"rejected":str(e),"engine_failures":d["failures"]})
        else:raise AssertionError("runtime negative accepted")
    result["runtime_negatives"]=negatives
    text=json.dumps(result,indent=2)+"\n"
    if a.output:a.output.write_text(text)
    print(text)
