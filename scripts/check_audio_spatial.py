#!/usr/bin/env python3
"""Paired real destruction capture: identical samples isolate distance and pan.
Numerical checks are not listening. Run with audio numpy/scipy environment.
"""
import argparse, copy, hashlib, json
from pathlib import Path
import numpy as np
from scipy.io import wavfile
ROOT = Path(__file__).resolve().parents[1]
def measure(directory):
    r = json.loads((directory / "results.json").read_text())
    assert r["passed"] and all(c["pass"] for c in r["checks"])
    sr, pcm = wavfile.read(directory / "runtime.wav")
    x = pcm.astype(np.float64) / 2**(8*pcm.dtype.itemsize-1)
    assert sr == 48000 and x.shape[1] == 2
    assert np.max(np.abs(x)) < .801 and np.max(np.abs(x)) > .1
    values = {}
    breaks = [e for e in r["audio"] if e["kind"] == "break"]
    assert len(breaks) == len(r["source"]) == 4
    assert len({(e["variant"], e["pitch"], e["gain_db"]) for e in breaks}) == 1
    for e, b in zip(r["source"], breaks):
        assert e["id"] == b["id"] and e["tick"] == b["tick"]
        # Early attack ends before the first contact: no debris-tail contamination.
        impacts = [a for a in r["audio"] if a["kind"] == "impact" and a["phase"] == e["phase"]]
        assert impacts and min(a["frame"] for a in impacts) > e["frame"] + 27
        z = x[round(e["frame"]/60*sr):round((e["frame"]/60+.45)*sr)]
        values[e["phase"]] = dict(distance=e["listener_distance"],
            rms=float(np.sqrt(np.mean(z*z))), peak=float(np.max(np.abs(z))),
            channels=np.sqrt(np.mean(z*z, axis=0)).tolist())
    return values

def validate(v):
    ratio = v["far"]["rms"] / v["near"]["rms"]
    expected = v["near"]["distance"] / v["far"]["distance"]
    assert .55 < ratio < .8, "arena distance cue absent or excessive"
    assert abs(ratio - expected) < .035, "not inverse-distance attenuation"
    assert v["left"]["channels"][0] > v["left"]["channels"][1] * 1.1, "left panning absent/reversed"
    assert v["right"]["channels"][1] > v["right"]["channels"][0] * 1.1, "right panning absent/reversed"
    assert abs(v["left"]["rms"] / v["right"]["rms"] - 1) < .01
    return dict(far_to_near_rms=ratio, expected_inverse_distance=expected)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory", type=Path)
    p.add_argument("--before", type=Path)
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    meta = json.loads((a.directory / "launch.json").read_text())
    for f,h in meta["source_sha256"].items():
        assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest() == h, f
    values = measure(a.directory)
    report = dict(measurements=values, checks=validate(values),
        listening="NONE: actual stereo mixer measurements, not subjective quality")
    if a.before:
        old = measure(a.before)
        try: validate(old)
        except AssertionError as e: report["baseline_failure"] = str(e)
        else: raise AssertionError("baseline did not reproduce missing distance cue")
        report["baseline_measurements"] = old
    if a.self_test:
        rejected = []
        for mutation in ["no_distance", "no_pan", "reversed_pan"]:
            bad = copy.deepcopy(values)
            if mutation == "no_distance": bad["far"]["rms"] = bad["near"]["rms"]
            if mutation == "no_pan": bad["left"]["channels"] = [1, 1]
            if mutation == "reversed_pan": bad["left"]["channels"].reverse()
            try: validate(bad)
            except AssertionError: rejected.append(mutation)
            else: raise AssertionError("checker missed " + mutation)
        report["rejected_mutations"] = rejected
    (a.directory / "spatial-analysis.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))
