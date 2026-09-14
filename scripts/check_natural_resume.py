#!/usr/bin/env python3
"""Additional independent node-13 audit: input lineage, remote unlock, impact PCM.
Run after check_natural.py; consumes raw traces and captured PCM, never the game.
No engine pass flags or precomputed analysis are accepted by these assertions.
"""
import argparse, collections, copy, hashlib, json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate
from check_natural import rows, only
ROOT = Path(__file__).resolve().parents[1]

def input_and_unlock(r):
    held = False
    pointer = False
    fired = 0
    bolts = {e["id"]: e for e in only(r, "bolt")}
    for e in r:
        k = e["kind"]
        if k in ["state", "reset"]:
            held = False
            if k == "reset": pointer = False
        elif k == "input_mouse": pointer = True
        elif k == "input_fire": held = e["pressed"]; pointer = True
        elif k == "fired":
            assert held and pointer, "fired without actual held mouse input"
            fired += 1
    assert fired > 20
    distances = []
    for h in only(r, "hit"):
        b = bolts[h["id"]]
        assert h["generation"] == b["generation"]
        offset = np.array(h["position"]) - b["position"]
        direction = np.array(b["direction"]); direction /= np.linalg.norm(direction)
        along = float(offset @ direction)
        perpendicular = float(np.linalg.norm(offset - along * direction))
        ticks = h["engine_tick"] - b["engine_tick"]
        step = b["speed"] / 60
        assert perpendicular < .002 and ticks * step - .002 <= along <= (ticks + 1) * step + .002, "hit outside real swept segment"
        distances.append(along)
    first = only(r, "initial")[0]["generation"]
    unlock = next(e for e in only(r, "progress") if e["generation"] == first and e["remaining"] == 0)
    won = next(e for e in only(r, "terminal") if e["state"] == 2)
    waiting = [e for e in only(r, "sample") if e["generation"] == first and unlock["engine_tick"] < e["engine_tick"] < won["engine_tick"]]
    assert len(waiting) > 300, "missing remote unlock gameplay"
    assert all(e["unlocked"] and e["remaining"] == 0 and not e["inside"] and e["state"] == 0 for e in waiting), "remote unlock incorrectly wins"
    assert won["inside"] and won["unlocked"]
    return {"held_input_fired_events": fired, "swept_hit_segments": len(distances), "remote_unlock_tick": unlock["tick"], "remote_unlock_playing_samples": len(waiting), "remote_unlock_active_wait_seconds": won["time"] - waiting[0]["time"]}

def impact_pcm(r, pr, sr, x):
    # Select sparse impacts from source timestamps, independently of waveform fit.
    audio = [e for e in only(r, "audio") if not e["audio"]["dropped"]]
    sparse = []; previous = -10000
    for e in audio:
        if e["audio"]["kind"] == "impact" and e["frame"] - previous >= 16: sparse.append(e)
        previous = e["frame"]
    tracks = collections.defaultdict(list)
    for row in pr:
        for b in row["bodies"]: tracks[b["id"]].append((row["engine_tick"], b))
    launches = {b["id"]: e for e in only(r, "burst") for b in e["bodies"]}
    results = []
    for e in sparse:
        a = e["audio"]; t = round(e["frame"] / 60 * sr)
        before = x[t-round(.05*sr):t]
        if len(before) != round(.05*sr) or np.max(abs(before)) > .00025: continue
        impact = next(i for i in only(r, "impact") if i["id"] == a["id"] and i["engine_tick"] == a["tick"])
        assert impact["speed"] >= 1 and launches[a["id"]]["engine_tick"] < a["tick"]
        ground = [(tick,b) for tick,b in tracks[a["id"]] if abs(tick-a["tick"]) <= 3 and b["contacts"] > 0 and "Ground" in b["colliders"]]
        assert ground, "impact lacks actual neighboring Ground contact"
        asset_path = ROOT / ("game/audio/impact_%d.wav" % a["variant"])
        rate, asset = wavfile.read(asset_path)
        # First 40ms identifies the attack before the next closely spaced impact.
        # Search only the independently bounded 0..50ms mixer delay: tonal tails
        # have periodic correlation aliases and are not onset measurements.
        idx = np.arange(round(.04*sr)) * a["pitch"] * rate / sr
        template = np.interp(idx, np.arange(len(asset)), asset.astype(float)); template -= template.mean()
        win = x[t:t+round(.09*sr)].mean(axis=1)
        corr = correlate(win, template, mode="valid", method="fft")
        energy = np.convolve(win**2, np.ones(len(template)), mode="valid")
        denom = np.sqrt(energy * np.sum(template**2))
        score = np.divide(corr, denom, out=np.zeros_like(corr), where=energy > max(float(energy.max())*1e-6, 1e-12))
        offset = int(score.argmax())
        assert .8 < score[offset] <= 1.000001 and 0 <= offset/sr < .05, "actual impact waveform/time mismatch"
        results.append({"frame":e["frame"], "body":a["id"], "burst":launches[a["id"]]["id"], "speed":impact["speed"], "ground_ticks":[t for t,b in ground], "variant":a["variant"], "pitch":a["pitch"], "asset_sha256":hashlib.sha256(asset_path.read_bytes()).hexdigest(), "normalized_correlation":float(score[offset]), "delay_ms":offset/sr*1000})
    assert len(results) >= 3, "not enough independently identified ground impact sounds"
    return results

def main():
    p = argparse.ArgumentParser(); p.add_argument("run", type=Path); p.add_argument("--output", type=Path, required=True); a = p.parse_args()
    r = rows(a.run / "events.jsonl.gz"); pr = rows(a.run / "physics.jsonl.gz")
    meta = json.loads((a.run / "launch.json").read_text())
    assert meta["movie"] and meta["returncode"] == 0
    for name, h in meta["source_sha256"].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == h
    sr, raw = wavfile.read(a.run/"audio.wav"); x = raw.astype(np.float64) / 2**(8*raw.dtype.itemsize-1)
    result = {"source_commit":meta["source_commit"], "inputs_and_unlock":input_and_unlock(r), "ground_impact_asset_matches":impact_pcm(r,pr,sr,x)}
    rejected = []
    for name in ["no_fire_press", "remote_unlock_won", "off_ray_hit"]:
        bad = copy.deepcopy(r)
        if name == "no_fire_press": bad = [e for e in bad if e["kind"] != "input_fire"]
        elif name == "off_ray_hit": only(bad,"hit")[0]["position"][1] += 1
        else: next(e for e in only(bad,"sample") if e["unlocked"] and e["state"] == 0)["state"] = 2
        try: input_and_unlock(bad)
        except AssertionError: rejected.append(name)
        else: raise AssertionError("accepted corrupted trace "+name)
    for name, z in [("silent_impact_pcm",np.zeros_like(x)),("delayed_impact_pcm",np.roll(x,sr//4,axis=0))]:
        try: impact_pcm(r,pr,sr,z)
        except AssertionError: rejected.append(name)
        else: raise AssertionError("accepted corrupted audio "+name)
    result["rejected_mutations"] = rejected; result["passed"] = True
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__ == "__main__": main()
