#!/usr/bin/env python3
"""Hard gate for the EXISTING destruction workload, window and 33.3ms target.
The legacy checker reports this target but does not fail its process on a miss.
This adds enforcement without modifying that checker or the measured workload.
"""
import argparse
import json
from pathlib import Path
from check_destruction import performance, validate


def check_target(directory):
    report = json.loads((Path(directory) / "results.json").read_text())
    assert report["performance_only"] and report["no_captures"], "use original lightweight performance mode"
    result = validate(directory)
    stats = result["performance"]
    assert stats["p95_target_ms"] == 33.3 and stats["window_ticks"] == [510, 1109]
    assert stats["capture_overlap_frames"] == 0
    assert stats["meets_p95_target"], f"p95 {stats["frame_ms"]["p95"]}ms exceeds original 33.3ms target"
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("directories", nargs="+")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    runs = []
    for directory in args.directories:
        try:
            result = check_target(directory)
            runs.append({"directory": directory, "passed": True, "result": result})
        except AssertionError as error:
            runs.append({"directory": directory, "passed": False, "error": str(error),
                         "performance": performance(directory)})
    output = {"passed": all(run["passed"] for run in runs), "runs": runs, "visual_assessment": "UNASSESSED"}
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if output["passed"] else 1)
