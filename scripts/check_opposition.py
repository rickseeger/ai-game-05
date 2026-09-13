#!/usr/bin/env python3
"""Independent event/trace/video checks; never a visual readability judgment."""
import argparse, copy, hashlib, json, math, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def require(value, message):
    if not value:
        raise AssertionError(message)

def natural(r, trace):
    events = r["events"]
    def of(kind): return [e for e in events if e["kind"] == kind]
    require(r["scenario"] in ("active", "inactive"), "natural scenario required")
    require(len(trace) == r["ticks"] and [s["tick"] for s in trace] == list(range(1, r["ticks"]+1)), "continuous trace")
    require(all(0 <= s["health"] <= 100 and len(s["enemies"]) <= 6 and s["debris"] <= 192 for s in trace), "runtime caps")
    require(all(b["health"] <= a["health"] for a,b in zip(trace,trace[1:])), "no healing")
    require(all(abs(s["time"] - s["tick"]/60) < 0.018 for s in trace), "normal simulation clock")
    warnings = {e["entity"]: e for e in of("spawn_warning")}
    spawns = {e["entity"]: e for e in of("spawn")}
    require(len([e for e in warnings.values() if e["tick"] == 0]) == 2, "two initial warnings")
    for e in spawns.values():
        require(e["distance"] >= 8 and e["engine_tick"]-warnings[e["entity"]]["engine_tick"] == 60, "spawn spacing and full warning")
    require(of("aim") and of("attack"), "active attacks exist")
    for e in of("attack"):
        aims = [x for x in of("aim") if x["entity"] == e["entity"] and x["engine_tick"] <= e["engine_tick"]]
        require(aims and e["engine_tick"]-aims[-1]["engine_tick"] == 36, "36 tick attack cue")
        previous = [x for x in of("attack") if x["entity"] == e["entity"] and x["engine_tick"] < e["engine_tick"]]
        require(not previous or e["engine_tick"]-previous[-1]["engine_tick"] >= 108, "attack cycle not accelerated")
        require(math.dist(spawns[e["entity"]]["position"], e["position"]) > 1, "sentry approaches")
    bolts = {e["id"]: e for e in of("bolt")}
    hits = of("hit")
    require(len({e["id"] for e in hits}) == len(hits), "once only bolt hit")
    for e in hits:
        b = bolts[e["id"]]
        require(e["tick"] >= b["tick"], "hit follows bolt")
        require(b["speed"] == (24 if b["friendly"] else 8), "projectile speed")
    health = 100
    for e in of("player_damage"):
        health = max(0, health-15)
        require(e["amount"] == 15 and e["health"] == health, "meaningful damage accounting")
        require(any(x["engine_tick"] == e["engine_tick"] and not x["friendly"] and x["damage"] == 15 for x in hits), "damage from actual collision")
    require(health == r["health"] and of("player_damage"), "final health accounting")
    if r["scenario"] == "inactive":
        require(r["health"] == 0 and r["state"] == 3 and r["ticks"] <= 3600, "inactivity loses")
        require(len(of("player_damage")) == 7 and len(of("player_died")) == 1, "seven hits one death")
        require(not of("player_fired") and not of("input_fire") and not of("input_key"), "genuinely inactive")
        require(all(math.dist(s["player"], trace[0]["player"]) < 0.01 for s in trace), "inactive remains stationary")
    else:
        require(r["health"] > 0 and r["state"] == 0 and r["ticks"] >= 1800 and not of("player_died"), "counterplay survives")
        require(len(of("destroyed")) >= 2 and len(of("player_dash")) == 1 and of("input_fire"), "input counterplay exists")
        require(of("player_fired")[0]["tick"] > of("player_damage")[0]["tick"], "responds after genuine threat")
        fired = of("player_fired")
        require(all(b["tick"]-a["tick"] >= 21 for a,b in zip(fired,fired[1:])), "normal player fire cadence")
        for death in of("destroyed"):
            damage = [e for e in of("sentry_damage") if e["entity"] == death["entity"]]
            require([e["health"] for e in damage] == [25,0] and all(e["amount"] == 25 for e in damage), "two hit destruction")
            require(all(any(h["target"] == death["entity"] and h["friendly"] and h["damage"] == 25 and h["tick"] == e["tick"] for h in hits) for e in damage), "counterplay swept hits")
            require(any(e["tick"] == death["tick"] and e["bodies"] >= 16 for e in of("burst")), "same tick physical destruction")
            require(not any(e["entity"] == death["entity"] and e["tick"] > death["tick"] for e in of("attack")), "destroyed threat stops attacking")
            require(all(not any(e["id"] == death["entity"] for e in s["enemies"]) for s in trace if s["tick"] > death["tick"]), "target removed")
    return {"scenario": r["scenario"], "ticks": r["ticks"], "seconds": r["ticks"]/60, "health": r["health"], "attacks":len(of("attack")), "damage_hits":len(of("player_damage")), "destroyed":len(of("destroyed"))}

def validate(directory):
    d = Path(directory)
    r = json.loads((d/"results.json").read_text())
    launch = json.loads((d/"launch.json").read_text())
    require(r["passed"] and all(c["pass"] for c in r["checks"]), "engine checks")
    require(launch["returncode"] == 0 and launch["validated_runner_success"], "runner success")
    require(not any(s in (d/"engine.log").read_text() for s in ("SCRIPT ERROR", "ERROR:")), "engine errors")
    for name,digest in launch["source_sha256"].items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, "tested source unchanged: "+name)
    result = {"directory": str(d), "engine_assertions":len(r["checks"])}
    if r["scenario"] != "focused":
        result.update(natural(r,json.loads((d/"trace.json").read_text())))
    else:
        required = {"aim_36_ticks", "cycle_108_ticks", "cover_stops_enemy_bolt", "fourth_player_bolt_removes_cover", "destroyed_cover_exposes_player", "second_bolt_once_only_death", "sixteen_service_fragments", "collider_and_mesh_removed_before_burst", "counterfire_interrupts_telegraphed_attack", "spawn_cap_six", "pause_freezes_aim_and_bolt", "input_restart_cleans_threats"}
        require(required <= {c["name"] for c in r["checks"]}, "focused coverage")
    if r["frames"]:
        frames = r["frames"]
        require(all(f["error"] == 0 for f in frames), "capture writes")
        require(all(0 <= b["observed_tick"]-a["observed_tick"] <= 3 for a,b in zip(frames,frames[1:])), "continuous capture ticks")
        require(frames[-1]["observed_tick"] >= r["ticks"], "capture includes outcome")
        video = json.loads(subprocess.check_output(["ffprobe","-v","error","-count_frames","-show_streams","-of","json",str(d/"runtime.mp4")],text=True))["streams"][0]
        require(int(video["nb_read_frames"]) == len(frames) and video["width"] == 1280 and video["height"] == 720, "real decoded movie matches trace")
        subprocess.run(["ffmpeg","-v","error","-i",str(d/"runtime.mp4"),"-f","null","-"],check=True)
        result["decoded_frames"] = len(frames)
    return result

def self_test(active, inactive):
    ra = json.loads((Path(active)/"results.json").read_text())
    ta = json.loads((Path(active)/"trace.json").read_text())
    ri = json.loads((Path(inactive)/"results.json").read_text())
    ti = json.loads((Path(inactive)/"trace.json").read_text())
    rejected = []
    for name in ("short_telegraph","no_damage","no_destruction","no_burst","duplicate_hit","inactive_fires","healing"):
        r,t = copy.deepcopy((ri,ti) if name == "inactive_fires" else (ra,ta))
        if name == "short_telegraph": next(e for e in r["events"] if e["kind"] == "attack")["engine_tick"] -= 1
        elif name == "no_damage": next(e for e in r["events"] if e["kind"] == "player_damage")["amount"] = 0
        elif name == "no_destruction": r["events"] = [e for e in r["events"] if e["kind"] != "destroyed"]
        elif name == "no_burst": r["events"] = [e for e in r["events"] if e["kind"] != "burst"]
        elif name == "duplicate_hit": r["events"].append(next(e for e in r["events"] if e["kind"] == "hit"))
        elif name == "inactive_fires": r["events"].append({"kind":"input_fire"})
        elif name == "healing": t[-1]["health"] = 100
        try: natural(r,t)
        except AssertionError: rejected.append(name)
        else: raise AssertionError("accepted mutation: "+name)
    return rejected

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directories", nargs="+")
    p.add_argument("--self-test", nargs=2, metavar=("ACTIVE","INACTIVE"))
    a = p.parse_args()
    result = {"runs":[validate(d) for d in a.directories], "visual_assessment":"UNASSESSED; decoding is not perception"}
    if a.self_test: result["rejected_mutations"] = self_test(*a.self_test)
    result["passed"] = True
    print(json.dumps(result,indent=2))
