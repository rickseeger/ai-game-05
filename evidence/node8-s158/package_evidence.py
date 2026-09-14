import hashlib,json,shutil,tarfile
from pathlib import Path
root=Path(__file__).resolve().parent
fresh=root/"fresh-run"
def sha(p):return hashlib.file_digest(p.open("rb"),"sha256").hexdigest()
def read(p):return json.loads((fresh/p).read_text())
verification=read("verification.json")
assert verification["passed"] and verification["unchanged_release_members_after_tests"]
assert all(c["returncode"]==0 for c in verification["commands"] if c["required"])
movie=read("natural-movie/analysis.json"); rt=read("natural-realtime/analysis.json"); supplement=read("natural-supplement.json")
rules=read("rules-checks.log"); integration=read("integration-checks.log")
metrics={"passed":True,"required_commands_passed":sum(c["required"] for c in verification["commands"]),"natural_rules":movie["rules"],"pylon_arcs":movie["physics"]["pylon_arcs"],"physics_samples":movie["physics"]["samples"],"decoded_frames":movie["pixels"]["decoded_frames"],"png_captures":len(movie["pixels"]["captures"]),"audio":movie["audio"],"impact_pcm_matches":len(supplement["ground_impact_asset_matches"]),"natural_negative_controls":len(movie["rejected_mutations"])+len(supplement["rejected_mutations"]),"realtime_performance":rt["performance"],"rules_assertions_per_run":[r["engine_assertions"] for r in rules["runs"]],"integration":integration["runs"][0]}
(root/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n")
shutil.copy2(fresh/"verification.json",root/"verification.json")
shutil.copy2(root/"repo/docs/linux-release.txt",root/"LINUX-RELEASE.txt")
files=sorted(p for p in fresh.rglob("*") if p.is_file() and "fresh directory with spaces" not in p.relative_to(fresh).parts)
manifest={str(p.relative_to(fresh)):{"bytes":p.stat().st_size,"sha256":sha(p)} for p in files}
archive=root/"fresh-validation.tar.gz"
with tarfile.open(archive,"w:gz") as t:
    for p in files:t.add(p,arcname=str(p.relative_to(fresh)),recursive=False)
with tarfile.open(archive) as t:
    assert len(t.getmembers())==len(manifest)
    for m in t.getmembers():
        assert hashlib.sha256(t.extractfile(m).read()).hexdigest()==manifest[m.name]["sha256"]
(root/"capture-index.json").write_text(json.dumps({"archive":archive.name,"sha256":sha(archive),"files":manifest,"readback_verified":True},indent=2)+"\n")
print(json.dumps({"archive_bytes":archive.stat().st_size,"archive_sha256":sha(archive),"archived_files":len(manifest),"required_commands_passed":metrics["required_commands_passed"]},indent=2))
