#!/usr/bin/env python3
"""Independent production bolt/death-to-audio telemetry check, NOT listening."""
import argparse, copy, json
from pathlib import Path

def check(r):
    assert r["passed"] and all(c["pass"] for c in r["checks"])
    bursts = [e for e in r["events"] if e["kind"] == "burst"]
    plays = [a for a in r["audio_events"] if not a["dropped"]]
    breaks = [a for a in plays if a["kind"] == "break"]
    assert len(bursts) >= 2 and {16,32} <= {b["bodies"] for b in bursts}, "pylon and sentinel not exercised"
    assert len(breaks) == len(bursts), "once-only burst count"
    assert all(sum(a["id"] == b["id"] and a["tick"] == b["engine_tick"] for a in breaks) == 1 for b in bursts), "same-tick burst route"
    impacts = [a for a in plays if a["kind"] == "impact"]
    sources = {(i["id"],i["tick"]) for i in r["impact_sources"] if i["speed"] >= 1}
    assert impacts and all((a["id"], a["tick"]) in sources for a in impacts), "real thresholded impact route"
    assert all(1 <= a["active"] <= 8 and 0 <= a["slot"] < 8 for a in plays), "voice bound"
    return dict(engine_assertions=len(r["checks"]), breaks=len(breaks), impacts=len(impacts), peak_slots=max(a["active"] for a in plays), same_tick=True)

if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("--self-test",action="store_true");a=p.parse_args()
    r=json.loads((a.directory/"results.json").read_text());result=check(r)
    if a.self_test:
        rejected=[]
        for name in ["wrong_tick","duplicate_break","missing_contact","nine_voices"]:
            bad=copy.deepcopy(r)
            if name == "wrong_tick":
                for e in bad["audio_events"]: e["tick"]+=1
            elif name == "duplicate_break": bad["audio_events"].append(next(e for e in bad["audio_events"] if e["kind"] == "break"))
            elif name == "missing_contact": bad["impact_sources"] = []
            else:
                for e in bad["audio_events"]: e["active"] = 9
            try: check(bad)
            except AssertionError: rejected.append(name)
            else: raise AssertionError("accepted mutation: "+name)
        result["rejected_mutations"]=rejected
    result["listening"]="NONE; event routing only"
    print(json.dumps(result,indent=2))
