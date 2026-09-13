#!/usr/bin/env python3
"""Validate engine reports AND decode actual PNG pixels; no subjective quality claim."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct
import subprocess


def report_checks(report):
    assert report["passed"] is True and report["failures"] == [], "engine assertions failed"
    checks = report["checks"]
    assert len(checks) == 337 and all(c["pass"] is True for c in checks), "missing/failed assertions"
    names = [c["name"] for c in checks]
    assert len(set(names)) == len(names), "duplicate assertions"
    for prefix, count in [("frustum_", 144), ("ground_aim_roundtrip_", 36),
                          ("locked_camera_", 36), ("cube_min_pixels_", 36)]:
        assert sum(n.startswith(prefix) for n in names) == count, prefix
    for name in ["true_perspective_Camera3D", "rendering_enabled", "exact_24m_ground",
                 "live_resize_dimensions", "live_resize_refits_camera", "perspective_depth_scale"]:
        assert name in names, name
    assert report["renderer"] == "gl_compatibility" and report["display"] != "headless"
    assert report["minimum_frame_margin"] >= .045
    assert report["minimum_cube_pixels"] >= 4


def image_data(path, expected):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    width, height = struct.unpack(">II", data[16:24])
    assert [width, height] == list(expected), (path, width, height, expected)
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-threads", "1", "-"])
    assert len(raw) == width * height * 3
    colors = len(set(zip(raw[::3], raw[1::3], raw[2::3])))
    assert colors > 200, "blank or trivial frame"
    return raw, {"file": path.name, "width": width, "height": height,
        "distinct_colors": colors, "sha256": hashlib.sha256(data).hexdigest()}


def validate(directory):
    directory = Path(directory)
    report = json.loads((directory / "results.json").read_text())
    report_checks(report)
    launch = json.loads((directory / "launch.json").read_text())
    assert launch["returncode"] == 0
    log = (directory / "engine.log").read_text()
    assert "ARENA_TEST_DONE checks=337 failures=0" in log and "OpenGL API" in log
    assert "SCRIPT ERROR" not in log and "ERROR:" not in log
    names = [c["file"] for c in report["captures"]]
    assert names == [n + ".png" for n in ["overview", "southwest", "northwest", "northeast", "southeast", "airborne"]]
    width, height = map(int, report["viewport"])
    frames = []
    for capture in report["captures"]:
        raw, frame = image_data(directory / capture["file"], [width, height])
        x, y = map(int, capture["projected_cube"])
        gold = 0
        for px in range(max(0, x-6), min(width, x+7)):
            for py in range(max(0, y-6), min(height, y+7)):
                r, g, b = raw[(py*width+px)*3:(py*width+px)*3+3]
                # Image.get_pixel exposes float32 channels, then GDScript compares doubles.
                # Match that boundary behavior (e.g. byte 102 -> 0.40000000596),
                # rather than incorrectly moving the threshold during byte scaling.
                r, g, b = [struct.unpack("f", struct.pack("f", v / 255.0))[0] for v in (r, g, b)]
                gold += r > .4 and r > g*1.08 and g > b*1.15
        assert gold >= 3 and gold == capture["gold_pixels"], "projected airborne cube pixels missing"
        frame["gold_pixels"] = gold
        frames.append(frame)
    assert len(set(f["sha256"] for f in frames)) == 6, "unchanging fixtures"
    _, resized = image_data(directory / "resized.png", report["resized_viewport"])
    frames.append(resized)
    return {"directory": str(directory), "assertions": len(report["checks"]),
        "camera_position": report["camera_position"], "resized_camera_position": report["resized_camera_position"],
        "minimum_frame_margin": report["minimum_frame_margin"],
        "minimum_cube_pixels": report["minimum_cube_pixels"], "frames": frames}


def negative(directory):
    directory = Path(directory)
    report = json.loads((directory / "results.json").read_text())
    assert report["passed"] is False
    assert json.loads((directory / "launch.json").read_text())["returncode"] == 1
    assert sum(n.startswith("frustum_") for n in report["failures"]) == 144
    try:
        report_checks(report)
    except AssertionError:
        return {"directory": str(directory), "rejected": True, "failures": len(report["failures"])}
    raise AssertionError("narrow camera accepted")


def tour(directory):
    directory = Path(directory)
    assert json.loads((directory / "launch.json").read_text())["returncode"] == 0
    frames = json.loads((directory / "tour.json").read_text())["frames"]
    assert len(frames) == 720
    assert len({(f["camera_x"], f["camera_y"], f["camera_z"]) for f in frames}) == 1
    for axis in ("x", "z"):
        assert min(f[axis] for f in frames) < -10.9 and max(f[axis] for f in frames) > 10.9
    assert max(f["height"] for f in frames) > 7.9
    log = (directory / "engine.log").read_text()
    assert "ARENA_TOUR_DONE frames=720" in log and "ERROR:" not in log
    images = [image_data(directory / ("tour_%04d.png" % f), [1280,720])[1]
        for f in [1,120,240,360,480,600]]
    assert len({f["sha256"] for f in images}) == 6
    intervals = sorted(f["delta"] * 1000 for f in frames[10:])
    return {"frames": len(frames), "elapsed_engine_seconds": frames[-1]["elapsed"],
        "median_frame_ms_after_warmup": statistics.median(intervals),
        "p95_frame_ms_after_warmup": intervals[math.ceil(.95*len(intervals))-1],
        "peak_fixture_height": max(f["height"] for f in frames), "images": images,
        "limit": "Preview only, seven nonphysical cubes. NOT the 192-body benchmark or laptop FPS."}


def self_test(directory):
    baseline = json.loads((Path(directory)/"results.json").read_text())
    report_checks(baseline)
    rejected = []
    for kind in ["missing_assertion", "duplicate_assertion", "failed_assertion", "clipped_frustum", "headless"]:
        bad = copy.deepcopy(baseline)
        if kind == "missing_assertion": bad["checks"].pop()
        if kind == "duplicate_assertion": bad["checks"][1] = bad["checks"][0]
        if kind == "failed_assertion": bad["checks"][0]["pass"] = False
        if kind == "clipped_frustum": bad["minimum_frame_margin"] = -0.1
        if kind == "headless": bad["display"] = "headless"
        try:
            report_checks(bad)
        except AssertionError:
            rejected.append(kind)
        else:
            raise AssertionError("negative accepted: " + kind)
    return rejected


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directories", nargs="+")
    p.add_argument("--negative-dir")
    p.add_argument("--tour-dir")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    result = {"runs": [validate(d) for d in a.directories]}
    if a.negative_dir: result["negative_camera"] = negative(a.negative_dir)
    if a.tour_dir: result["tour"] = tour(a.tour_dir)
    if a.self_test: result["checker_negative_controls_rejected"] = self_test(a.directories[0])
    result["passed"] = True
    print(json.dumps(result, indent=2))
