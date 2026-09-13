#!/usr/bin/env python3
"""Compare actual fixed-step traces, including every repeated stress burst.
Wall timestamps and post-stress async timer fixture are not deterministic keys.
No poses are generated; all telemetry comes from the unchanged engine test.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path


def summarize(directory):
    digest = hashlib.sha256()
    metrics = {}
    count = 0
    with gzip.open(Path(directory) / "physics.csv.gz", "rt") as file:
        for row in csv.DictReader(file):
            tick, ident = int(row["tick"]), int(row["id"])
            if tick >= 1390:
                continue
            normalized = {k: v for k, v in row.items() if k != "unix_seconds"}
            digest.update((json.dumps(normalized, sort_keys=True) + "\n").encode())
            count += 1
            if tick < 510:
                continue
            y, vy = float(row["y"]), float(row["vy"])
            q = tuple(float(row[k]) for k in ["qx", "qy", "qz", "qw"])
            m = metrics.setdefault(ident, {"first_tick": tick, "start_y": y, "up": False,
                "down": False, "contact": False, "bounce": False, "spin": False,
                "tumble": False, "sleep": False, "previous_vy": vy, "previous_q": q,
                "last_tick": tick, "max_age": 0.0})
            turn = 2 * math.acos(min(1, abs(sum(a*b for a,b in zip(q, m["previous_q"])))))
            m["up"] |= y > m["start_y"] + .4
            m["down"] |= vy < -1
            m["contact"] |= int(row["contacts"]) > 0
            m["bounce"] |= m["contact"] and m["previous_vy"] < -.5 and vy > .3
            m["spin"] |= turn > .03
            m["tumble"] |= m["contact"] and y < .5 and turn > .015
            m["sleep"] |= row["sleeping"] == "1"
            m["max_age"] = max(m["max_age"], float(row["age"]))
            m.update(previous_q=q, previous_vy=vy, last_tick=tick)
    grouped = {}
    for tick in [510, 630, 900]:
        group = [m for m in metrics.values() if m["first_tick"] == tick]
        assert len(group) == (192 if tick == 510 else 96)
        grouped[tick] = {"bodies": len(group), **{key: sum(m[key] for m in group)
            for key in ["up", "down", "contact", "bounce", "spin", "tumble", "sleep"]}}
        for key in ["up", "down", "contact", "spin"]:
            assert all(m[key] for m in group), f"stress burst {tick} missing {key}"
    return {"directory": str(directory), "samples_before_tick_1390": count,
            "physics_sha256_without_wall_time": digest.hexdigest(), "stress_bursts": grouped,
            "limitation": "Cap retires some active bodies early; natural sleep not required of those retired at age 2s."}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("baseline")
    p.add_argument("corrected")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    before, after = summarize(a.baseline), summarize(a.corrected)
    match = before["physics_sha256_without_wall_time"] == after["physics_sha256_without_wall_time"]
    result = {"baseline": before, "corrected": after, "identical_fixed_step_physics": match,
              "visual_assessment": "UNASSESSED"}
    a.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    assert match, "fixed-step physics changed"
