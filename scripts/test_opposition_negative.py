#!/usr/bin/env python3
"""Serial-only actual-engine negative control. Restores source even on failure."""
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "game/sentry.gd"
original = source.read_text()
assert original.count("const AIM_TIME := 0.6") == 1
out = ROOT / "evidence/opposition/negative-short-aim"
assert not out.exists(), "fresh output required"
try:
    source.write_text(original.replace("const AIM_TIME := 0.6", "const AIM_TIME := 0.2"))
    run = subprocess.run(["python3", str(ROOT/"scripts/run_opposition.py"), out.name, "--scenario", "focused"], cwd=ROOT)
    result = json.loads((out/"results.json").read_text())
    assert run.returncode == 1 and not result["passed"] and "aim_36_ticks" in result["failures"]
    report = {"rejected": True, "mutation": "sentry AIM_TIME 0.6 -> 0.2", "failed_checks": result["failures"], "runner_returncode":run.returncode}
finally:
    source.write_text(original)
assert source.read_text() == original
report["source_restored"] = True
(out/"negative-control.json").write_text(json.dumps(report, indent=2)+"\n")
print(json.dumps(report, indent=2))
