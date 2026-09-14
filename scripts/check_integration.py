#!/usr/bin/env python3
"""Independent trace/HUD and decoded-pixel checks; no vision/readability verdict."""
import argparse, copy, hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]

def validate(r):
    assert r["passed"] and len(r["checks"]) >= 120 and all(c["pass"] for c in r["checks"])
    ss = r["snapshots"]
    named = {s["label"]: s for s in ss}
    for s in ss:
        seconds = math.ceil(max(0, 150-s["elapsed"]))
        assert f"Time: {seconds//60}:{seconds%60:02d}" in s["hud"]
        assert f"Pylons: {3-s['remaining']} / 3 destroyed" in s["hud"]
        assert f"Health: {s['health']} / 100" in s["hud"]
        assert f"Sentries: {s['sentries']}" in s["hud"]
        dash = "READY" if s["dash_remaining"] <= .00001 else f"{s['dash_remaining']:.1f}s"
        assert f"Dash: {dash}" in s["hud"]
        assert s["unlocked"] == (s["remaining"] == 0)
        assert ("Extraction: OPEN" if s["unlocked"] else "Extraction: LOCKED") in s["hud"]
        for token in ["THREE pylons", "EXTRACT alive", "WASD", "Mouse", "LMB", "Space", "Esc"]:
            assert token in s["hud"]
        if s["state"] in [2,3]:
            assert ("VICTORY" if s["state"] == 2 else "DEFEAT") in s["message"] and "R to retry" in s["message"]
        if s["state"] == 1:
            assert "PAUSED" in s["message"] and "Esc to resume" in s["message"]
    for label,state,reason in [("victory-fixture",2,""),("death-fixture",3,"death"),("timeout-fixture",3,"timeout")]:
        assert named[label]["state"] == state and named[label]["loss_reason"] == reason
    a,b = named["pause-start"],named["pause-end"]
    for field in ["elapsed","opposition_elapsed","position","fire_remaining","dash_remaining","bodies","state"]:
        assert a[field] == b[field], field
    resets = [s for s in ss if s["label"] == "reset"]
    assert len(resets) == 6
    for i,s in enumerate(resets):
        assert s["generation"] == i+2 and s["state"] == 0 and not s["paused"]
        for field in ["elapsed","clock_error","fire_remaining","dash_remaining","shots","shot_count","dash_count","bolts","bolt_visuals","bodies","rendered_bodies","audio_history","opposition_elapsed","sentries"]:
            assert s[field] == 0, field
        assert s["health"] == 100 and s["remaining"] == 3 and s["loss_reason"] == ""
        assert s["input_enabled"] and not s["held"] and not s["dash_edge"] and not s["pointer_known"] and not s["aim_valid"]
        assert s["pointer"] == [0,0] and s["velocity"] == [0,0,0] and s["position"] == [0,0,10]
        assert not any(s["voices"]) and len(s["voices"]) == 8
        assert s["next_spawn"] == 15 and s["pending"] == resets[0]["pending"]
        assert [w["id"] for w in s["pending"]] == [100,101] and all(w["left"] == 1 for w in s["pending"])
        assert [t["id"] for t in s["targets"]] == [1,2,3]
        assert all(t["health"] == 100 and t["intact"] and not t["destroyed"] and t["callbacks"] == 1 for t in s["targets"])
        assert s["marker"] == "EXTRACT [LOCKED]" and not s["panel_visible"]
        assert s["nodes"] == named["launch"]["nodes"] and s["buses"] == named["launch"]["buses"]
        for field in ["player_callbacks","burst_callbacks","impact_callbacks","pause_callbacks","restart_callbacks"]:
            assert s[field] == 1, field
        e = [e for e in r["events"] if e["phase"] == s["phase"]]
        assert [x["value"] for x in e if x["kind"] == "state"] == [[2,3,3][i%3],0]
        progress = [x["value"] for x in e if x["kind"] == "progress"]
        assert progress == ([1,0,3] if i == 0 else [2,1,0,3]), progress
    assert len([s for s in ss if s["label"] == "replay-live" and s["shots"] == 1 and s["shot_count"] == 1]) == 6
    hits = [e for e in r["events"] if e["phase"] == "default_launch" and e["kind"] == "combat_hit" and e["data"]["target"] == 3]
    assert len(hits) == 4 and all(e["data"]["damage"] == 25 for e in hits)
    assert len([e for e in r["events"] if e["phase"] == "default_launch" and e["kind"] == "audio" and e["data"]["kind"] == "break" and not e["data"]["dropped"]]) == 1
    return {"engine_assertions":len(r["checks"]),"forced_reset_cycles":len(resets),"ordinary_input_pylon_hits":len(hits)}

def pixels(out,r):
    named = {s["label"]:s for s in r["snapshots"]}
    def image(name):
        x = np.array(Image.open(out/(name+".png")).convert("RGB"))
        assert x.shape == ((720,960,3) if name == "paused-4x3" else (720,1280,3))
        assert len(np.unique(x.reshape(-1,3),axis=0)) > 1000
        return x
    images = {p.stem:image(p.stem) for p in out.glob("*.png")}
    result = {}
    for key,base,hidden,restored,rect_field in [
        ("hud","paused-visible","paused-hud-hidden","paused-restored","hud_rect"),
        ("panel","paused-visible","paused-panel-hidden","paused-restored","panel_rect"),
        ("locked_marker","extraction-locked","locked-marker-hidden","locked-marker-restored",None),
        ("open_marker","extraction-open-fixture","victory-marker-hidden","victory-marker-restored",None)]:
        x,y,z = images[base],images[hidden],images[restored]
        mask = np.any(x != y,axis=2)
        changed = int(mask.sum())
        assert changed > 100, key
        assert np.array_equal(x,z), key+" restoration"
        yy,xx = np.nonzero(mask)
        if rect_field:
            rx,ry,w,h = named[base][rect_field]
            assert xx.min() >= math.floor(rx) and xx.max() < math.ceil(rx+w) and yy.min() >= math.floor(ry) and yy.max() < math.ceil(ry+h)
        result[key] = {"changed_pixels":changed,"bounds":[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())],"restored_identical":True}
        if key.endswith("marker"):
            colors=x[mask].astype(int)
            is_color = ((colors[:,0] > colors[:,1]+20) & (colors[:,1] > colors[:,2]+20)) if key == "locked_marker" else ((colors[:,1] > colors[:,0]+40) & (colors[:,2] > colors[:,0]+30))
            result[key]["amber_or_green_pixels"] = int(is_color.sum())
            assert is_color.sum() > 30, key+" color"
    assert int(np.any(images["death-fixture"][:130] != images["timeout-fixture"][:130],axis=2).sum()) > 100
    result["captures"] = len(images)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("runs",nargs="+",type=Path);a=p.parse_args()
    summary=[]
    for out in a.runs:
        launch=json.loads((out/"launch.json").read_text()); r=json.loads((out/"results.json").read_text())
        assert launch["returncode"] == 0 and "--script" not in launch["command"] and not any(x.endswith(".tscn") for x in launch["command"])
        assert "ERROR" not in (out/"engine.log").read_text()
        for f,digest in launch["source_sha256"].items():
            assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest() == digest, f
        report=validate(r);report["pixels"]=pixels(out,r)
        rejected=[]
        for field,value in [("health",99),("remaining",2),("voices",[True]*8),("bodies",1),("player_callbacks",2),("pointer_known",True),("elapsed",1),("hud","stale HUD")]:
            corrupted=copy.deepcopy(r)
            next(s for s in corrupted["snapshots"] if s["label"] == "reset")[field]=value
            try: validate(corrupted)
            except AssertionError: rejected.append(field)
            else: raise AssertionError("accepted corrupt evidence: "+field)
        report.update(rejected_trace_mutations=rejected,source_commit=launch["source_commit"],run=str(out))
        summary.append(report)
    print(json.dumps({"passed":True,"runs":summary,"limits":"Decoded pixels prove drawing and bindings, not subjective readability. Forced terminal fixtures are not natural victories; Dummy audio is not listening; fixed FPS is not performance."},indent=2))
if __name__ == "__main__": main()
