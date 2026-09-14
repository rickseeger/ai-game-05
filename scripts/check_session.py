#!/usr/bin/env python3
"""Independently derive rules/order from emitted production event traces.
This checks evidence and provenance, not subjective play or an alternate rules engine.
"""
import argparse, copy, hashlib, json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]

def trace_checks(r):
    events = r["events"]
    def select(scenario, kind):
        return [e for e in events if e["scenario"] == scenario and e["kind"] == kind]
    progress = select("progress_and_radius", "progress")
    assert [e["data"]["remaining"] for e in progress] == [3,2,1,0], "distinct progression"
    assert [e["data"]["value"] for e in select("progress_and_radius", "state")] == [0,2], "locked/terminal states"
    clock = select("deadline_steps", "before_deadline")[0]
    terminal = select("deadline_steps", "state")[-1]
    assert clock["state"] == 0 and 149.98 < clock["elapsed"] < 150, "early deadline"
    assert terminal["state"] == 3 and terminal["elapsed"] == 150, "exact deadline"
    for scenario in ["death", "deadline_epsilon", "deadline_overshoot", "timeout_beats_win"]:
        assert [e["data"]["value"] for e in select(scenario, "state")] == [0,3], scenario
    assert [e["data"]["value"] for e in select("just_before_deadline_win", "state")] == [0,2]
    pause = select("pause_real_engine", "state")
    assert [e["state"] for e in pause] == [0,1,0] and pause[1]["elapsed"] == pause[2]["elapsed"], "pause clock"
    for order in ["false", "true"]:
        scenario = "same_tick_hostile_first_" + order
        died = select(scenario, "died")
        progress = [e for e in select(scenario, "progress") if e["remaining"] == 0]
        states = select(scenario, "state")
        assert len(died) == len(progress) == 1 and [e["state"] for e in states] == [0,3], "same tick outcome"
        terminal = states[-1]
        assert died[0]["tick"] == progress[0]["tick"] == terminal["tick"], "same tick provenance"
        assert died[0]["state"] == progress[0]["state"] == 0, "early terminal"
        assert events.index(terminal) > max(events.index(died[0]),events.index(progress[0])), "damage order"
        assert terminal["health"] == 0 and terminal["remaining"] == 0, "damage pass incomplete"
    progress = select("deadline_damage_order", "progress")[-1]
    terminal = select("deadline_damage_order", "state")[-1]
    assert progress["remaining"] == 2 and progress["state"] == 0 and terminal["state"] == 3
    assert progress["tick"] == terminal["tick"] and events.index(progress) < events.index(terminal), "deadline before damage"
    scenario = "combat_progression"
    hits = [e for e in select(scenario,"combat_hit") if e["data"]["damage"] == 25]
    deaths = select(scenario,"destroyed")
    bursts = select(scenario,"burst")
    sounds = [e for e in select(scenario,"audio") if e["data"]["kind"] == "break" and not e["data"]["dropped"]]
    assert len(hits) == 12 and len(deaths) == len(bursts) == len(sounds) == 3, "combat chain"
    assert {e["data"]["id"] for e in deaths} == {1,2,3}, "distinct targets"
    for death in deaths:
        target_hits = [h for h in hits if h["data"]["target"] == death["data"]["id"]]
        assert len(target_hits) == 4 and target_hits[-1]["tick"] == death["tick"]
        assert all(b["tick"]-a["tick"] >= 21 for a,b in zip(target_hits,target_hits[1:])), "fire cadence"
        burst = [b for b in bursts if b["tick"] == death["tick"]]
        assert len(burst) == 1 and sum(s["tick"] == death["tick"] and s["data"]["id"] == burst[0]["data"]["id"] for s in sounds) == 1, "same tick audio"
    assert [e["state"] for e in select(scenario,"state")] == [0,2]
    return {"combat_hits":len(hits), "distinct_pylons":len(deaths), "same_tick_orders_checked":2, "same_tick_break_sounds":len(sounds)}

def validate(directory):
    d = Path(directory)
    r = json.loads((d/"results.json").read_text())
    launch = json.loads((d/"launch.json").read_text())
    assert launch["returncode"] == 0 and "ERROR" not in (d/"engine.log").read_text()
    assert r["passed"] and len(r["checks"]) >= 55 and all(c["pass"] for c in r["checks"])
    for name,digest in launch["source_sha256"].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    result = trace_checks(r)
    image = Image.open(d/"combat-victory-fixture.png").convert("RGB")
    colors = image.getcolors(image.width*image.height)
    assert image.size == (1280,720) and len(colors) > 1000, "nontrivial rendered image"
    result.update(engine_assertions=len(r["checks"]), source_commit=launch["source_commit"], rendered_colors=len(colors))
    rejected = []
    for mutation in ["duplicate_progress", "early_deadline", "win_over_loss", "early_terminal", "late_audio", "missing_hit"]:
        bad = copy.deepcopy(r)
        if mutation == "duplicate_progress": bad["events"].append(next(e for e in bad["events"] if e["scenario"] == "progress_and_radius" and e["kind"] == "progress"))
        if mutation == "early_deadline": next(e for e in bad["events"] if e["scenario"] == "deadline_steps" and e["kind"] == "state" and e["state"] == 3)["elapsed"] = 149.99
        if mutation == "win_over_loss": next(e for e in bad["events"] if e["scenario"] == "same_tick_hostile_first_true" and e["kind"] == "state" and e["state"] == 3)["state"] = 2
        if mutation == "early_terminal": next(e for e in bad["events"] if e["scenario"] == "same_tick_hostile_first_true" and e["kind"] == "died")["state"] = 3
        if mutation == "late_audio":
            for e in bad["events"]:
                if e["kind"] == "audio": e["tick"] += 1
        if mutation == "missing_hit": bad["events"].remove(next(e for e in bad["events"] if e["scenario"] == "combat_progression" and e["kind"] == "combat_hit"))
        try: trace_checks(bad)
        except AssertionError: rejected.append(mutation)
        else: raise AssertionError("mutation accepted: " + mutation)
    result["rejected_mutations"] = rejected
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("directories", nargs="+"); a = p.parse_args()
    print(json.dumps({"passed":True, "runs":[validate(d) for d in a.directories], "limits":"Fixtures only; pixel diversity is not visual assessment; Dummy audio is not listening."}, indent=2))
