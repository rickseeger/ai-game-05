#!/usr/bin/env python3
"""Decode on/off/restored production-beam captures; numerical visibility only."""
import argparse, hashlib, json, math, subprocess
from pathlib import Path


def compare(on, off, restored, width, height, endpoints):
    assert len(on) == len(off) == len(restored) == width * height * 3, "RGB dimensions"
    assert on == restored, "restored frame must exactly match frozen original"
    a, b = endpoints
    assert all(0 <= p[0] < width and 0 <= p[1] < height for p in endpoints), "cue endpoints on screen"
    x0 = max(0, math.floor(min(a[0], b[0])) - 5)
    x1 = min(width, math.ceil(max(a[0], b[0])) + 6)
    y0 = max(0, math.floor(min(a[1], b[1])) - 5)
    y1 = min(height, math.ceil(max(a[1], b[1])) + 6)
    changed = red = 0
    columns = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            i = (y * width + x) * 3
            c, d = on[i:i+3], off[i:i+3]
            different = max(abs(u-v) for u,v in zip(c,d)) > 30
            changed += different
            if different and c[0] > 150 and c[0] > 1.6*c[1] and c[0] > 1.6*c[2]:
                red += 1
                columns.add(x)
    assert red >= 20, "real red cue must contribute at least 20 changed ROI pixels"
    # This fixture deliberately presents a horizontal beam across the screen.
    assert len(columns) >= abs(a[0]-b[0]) * 0.5, "cue red pixels span half projected beam"
    return {"roi": [x0,y0,x1,y1], "changed_pixels": changed,
            "red_changed_pixels": red, "red_columns": len(columns),
            "restored_identical": True}


def validate(directory):
    d = Path(directory)
    m = json.loads((d/"cue-render.json").read_text())
    frames = m["frames"]
    assert [f["visible"] for f in frames] == [True, False, True]
    assert all(b["unix_seconds"] >= a["unix_seconds"] for a,b in zip(frames,frames[1:]))
    images = [subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(d/f["file"]),
              "-f", "rawvideo", "-pix_fmt", "rgb24", "-threads", "1", "-"]) for f in frames]
    params = (m["width"], m["height"], m["endpoints"])
    result = compare(*images, *params)
    rejected = []
    for name, samples in [("absent_beam", [images[1]]*3),
                           ("swapped_visibility", [images[1],images[0],images[1]]),
                           ("not_restored", [images[0],images[1],images[1]])]:
        try:
            compare(*samples, *params)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError("accepted pixel negative control: " + name)
    result.update(passed=True, directory=str(d), rejected_mutations=rejected,
                  files={f["file"]: hashlib.sha256((d/f["file"]).read_bytes()).hexdigest() for f in frames},
                  limitation="Isolated frozen fixture; not a human readability/fun judgment or dense-scene guarantee")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directory")
    a = p.parse_args()
    print(json.dumps(validate(a.directory), indent=2))
