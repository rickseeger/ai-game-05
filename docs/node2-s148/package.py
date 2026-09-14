#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "docs/node2-s148"
E = ROOT / "evidence/node2-s148"
E.mkdir(exist_ok=False)
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, data):
    (D / name).write_text(json.dumps(data, indent=2) + chr(10))
prior_path = ROOT / "evidence/node2-s138/runtime-evidence.tar.xz"
prior = json.loads((ROOT / "docs/node2-s138/node9-handoff.json").read_text())
prior_manifest = {r["path"]:r for r in json.loads((ROOT / "docs/node2-s138/artifact-manifest.json").read_text())}
with tarfile.open(prior_path) as t:
    for name in prior["production_frames"]:
        assert hashlib.sha256(t.extractfile(name).read()).hexdigest() == prior_manifest[name]["sha256"]
video = ROOT / "evidence/audio-node5-s147/runtime.mp4"
probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames,duration", "-of", "json", str(video)], text=True))
assert not subprocess.check_output(["git", "diff", "7ee3d568eaa81d4095c7b1d4a75f331318054c38", "HEAD", "--", "game"], cwd=ROOT)
audio_summary = json.loads((ROOT / "evidence/audio-node5-s147/summary.json").read_text())
markers = audio_summary["audio"]["signal"]["isolated_break_onsets"]
save("node9-handoff.json", {
    "destination": "G12 node 9 exact-release Linux human playtest",
    "current_tested_source": json.loads((D / "provenance.json").read_text())["source_revision"],
    "subjective_visual_judgment": "UNASSESSED; no reliable vision tool. Technical passes are not perceptual readability or satisfaction.",
    "fresh_camera_archive": "evidence/node2-s148/runtime-evidence.tar.gz",
    "fresh_camera_frames": ["evidence/arena/n2-s148-" + size + "/" + f + ".png" for size in ["720p", "4x3"] for f in ["overview", "northwest", "northeast", "airborne", "resized"]],
    "prior_dense_evidence": {"archive": str(prior_path.relative_to(ROOT)), "sha256": sha(prior_path),
        "extraction_command": "tar -xJf evidence/node2-s138/runtime-evidence.tar.xz",
        "source_revision": "954782e0fb5b6b535ce99168795872ae56ad4c16",
        "production_frames": prior["production_frames"], "frame_hashes_reverified": True,
        "note": "Historical captured sequence, NOT a new dense rerun or continuous recording. Diagnostics pause simulation; only *_color.png is production appearance."},
    "existing_motion_recording": {"path": str(video.relative_to(ROOT)), "sha256": sha(video), "ffprobe": probe,
        "source_revision": audio_summary["source_revision"], "game_source_matches_current": True,
        "review_cues_seconds": [{"phase": m["phase"], "render_frame": m["frame"], "seconds": m["frame"] / 60.0} for m in markers if m["phase"] in ["single_default", "crowded_default", "max_overload"]],
        "note": "Existing node5 MovieWriter capture of actual renderer and physics, offline common clock. Not a fresh node2 run, natural combat, real-time FPS or subjective audio evidence; do not use sparse supplemental live.mkv for timing."},
    "review_questions": [
        "Can you keep track of the blue actor, its ground position and incoming threats through crowded bursts while moving and aiming in the exact release?",
        "Are airborne trajectories, landing/contact and depth clear at rear corners and after resizing? Is the locked view comfortable?",
        "Can you identify the extraction ring and label through debris? Are near-ground overlaps tolerable rather than confusing?",
        "Does brief actor occlusion disrupt decisions? Historical tick-12 cyan-region retention is 27.23% / 37.05%, recovering at tick 30 to 94.34% / 84.75%. These sparse local color samples are not whole-body visibility percentages or continuous duration bounds.",
        "The tour_0360_12 seven-cube diagnostic has only three pieces with at least three ID pixels despite all centers in frame. Does overlap obscure action in motion? Do not require every fragment visible.",
        "Historical dense tick 120 has escaped below-floor fragments outside the configured camera envelope (IDs 111 and 128 at 720p; 128 at 4:3). Is boundary behavior distracting? If so route to destruction/boundary owner, not speculative camera expansion.",
        "On the exact final release, are destruction, perceived weight and visual/audio payoff satisfying? This worker has neither seen nor heard them subjectively."],
    "restrictions": ["No new dense/analytic experiments or numerical redefinition of visual satisfaction.", "No input/combat/destruction/audio/root or durable node acceptance.", "Final playtest judges the exact release; stored fixture recordings are supporting references, not release signoff."]})
raw_dirs = [ROOT / ("evidence/arena/n2-s148-" + s) for s in ["720p", "4x3", "negative", "tour"]]
files = sorted([p for d in raw_dirs for p in d.iterdir() if p.is_file()] + list((D / "logs").iterdir()) + [D / "initial-wrapper-syntax-error.log"])
manifest = [{"path": str(p.relative_to(ROOT)), "size": p.stat().st_size, "sha256": sha(p),
    "saved_utc": datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat()} for p in files]
save("artifact-manifest.json", manifest)
archive = E / "runtime-evidence.tar.gz"
with tarfile.open(archive, "w:gz") as t:
    for p in files:
        t.add(p, arcname=str(p.relative_to(ROOT)))
with tarfile.open(archive) as t:
    assert len(t.getmembers()) == len(manifest)
    for entry in manifest:
        data = t.extractfile(entry["path"]).read()
        assert len(data) == entry["size"] and hashlib.sha256(data).hexdigest() == entry["sha256"]
    with tempfile.TemporaryDirectory(prefix="archive-verify-", dir=D) as td:
        t.extractall(td, filter="data")
        args = [sys.executable, str(ROOT / "scripts/check_arena.py"), "evidence/arena/n2-s148-720p", "evidence/arena/n2-s148-4x3", "--negative-dir", "evidence/arena/n2-s148-negative", "--tour-dir", "evidence/arena/n2-s148-tour", "--self-test"]
        checked = subprocess.run(args, cwd=td, capture_output=True, text=True)
        assert checked.returncode == 0, checked.stderr
        recheck = json.loads(checked.stdout)
        assert recheck == json.loads((D / "arena-checks.json").read_text())
assert not subprocess.check_output(["git", "diff", "HEAD", "--", "game", "scripts"], cwd=ROOT)
save("verification.json", {"archive_member_count": len(manifest), "png_count": sum(p.suffix == ".png" for p in files),
    "archive_sha256": sha(archive), "all_members_hash_size_verified": True,
    "extracted_archive_checker": {"command": args, "cwd": "fresh temporary archive extraction (removed after verification)", "returncode": checked.returncode, "results_equal_original": True},
    "game_and_existing_scripts_unchanged": True, "production_technical_failures": [],
    "expected_negative_camera_failures": recheck["negative_camera"]["failures"],
    "initial_wrapper_syntax_error": "Retained in archive. Escaped-newline typo repaired before any engine launch; not a renderer defect.",
    "scope": "Assigned execution finished only. Independent controller decides durable acceptance."})
(E / "SHA256SUMS").write_text(sha(archive) + "  " + str(archive.relative_to(ROOT)) + chr(10))
# Remove only this worker temporary raw duplicates after lossless readback AND extracted checker pass.
for d in raw_dirs:
    shutil.rmtree(d)
shutil.rmtree(D / "logs")
(D / "initial-wrapper-syntax-error.log").unlink()
print(json.dumps({"archive": str(archive.relative_to(ROOT)), "members": len(manifest), "pngs": sum(p.suffix == ".png" for p in files), "extracted_checker_passed": recheck["passed"]}, indent=2))
