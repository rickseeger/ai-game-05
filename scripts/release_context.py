"""Source provenance for both Git checkouts and immutable release manifests."""
import hashlib, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def source_commit():
    if (ROOT / "RELEASE.json").exists():
        return json.loads((ROOT / "RELEASE.json").read_text())["source_revision"]
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
def source_status():
    if (ROOT / "RELEASE.json").exists():
        manifest = json.loads((ROOT / "RELEASE.json").read_text())
        changed = [n for n, spec in manifest["files"].items() if not (ROOT/n).is_file() or hashlib.sha256((ROOT/n).read_bytes()).hexdigest() != spec["sha256"]]
        if changed: raise RuntimeError("Modified release files: " + repr(changed))
        return "verified release manifest; no Git metadata distributed"
    return subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True)
def baseline_digest(name):
    return json.loads((ROOT / "release/accepted-production.json").read_text())["files"][name]
