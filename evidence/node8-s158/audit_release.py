import hashlib, json, platform, subprocess, tarfile, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
repo=ROOT/"repo"
artifact=ROOT/"dist/breakwater-linux-x86_64.tar.gz"
rebuilt=ROOT/"dist/rebuilt-linux-x86_64.tar.gz"
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(["git",*args],cwd=repo)
with tarfile.open(artifact) as t:
    members=t.getmembers()
    assert len({m.name for m in members})==len(members)
    blobs={m.name.removeprefix("breakwater-linux-x86_64/"):t.extractfile(m).read() for m in members}
manifest=json.loads(blobs["RELEASE.json"])
source=manifest["source_revision"]
assert source=="42e3bd348b22590ba504ef5ebcb55dbd8443e652"
assert not git("diff",manifest["accepted_game_revision"],source,"--","game")
checked=[]
for name,meta in manifest["files"].items():
    assert sha(blobs[name])==meta["sha256"]
    if name.startswith("runtime/"):continue
    original="docs/linux-release.txt" if name=="README.txt" else name
    assert blobs[name]==git("show",source+":"+original),name
    checked.append(name)
production=[line.split("\t")[1] for line in git("ls-tree","-r",source,"--","game").decode().splitlines()]
assert all(name in blobs for name in production)
assets=json.loads(blobs["game/audio/provenance.json"])
for name,meta in assets["assets"].items():assert sha(blobs["game/audio/"+name])==meta["sha256"]
assert "MIT" in assets["license"]
assert b"Permission is hereby granted" in blobs["LICENSE"]
assert b"Permission is hereby granted" in blobs["release/licenses/Godot-LICENSE.txt"]
assert len(blobs["release/licenses/Godot-COPYRIGHT.txt"])>10000
engine=blobs["runtime/Godot_v4.5.1-stable_linux.x86_64"]
assert engine[:4]==b"\x7fELF" and engine[4]==2 and engine[5]==1 and int.from_bytes(engine[18:20],"little")==62
assert artifact.read_bytes()==rebuilt.read_bytes()
result={"passed":True,"artifact":str(artifact),"bytes":artifact.stat().st_size,"sha256":sha(artifact.read_bytes()),"rebuilt_sha256":sha(rebuilt.read_bytes()),"byte_identical_rebuild":True,"source_revision":source,"accepted_game_revision":manifest["accepted_game_revision"],"archive_members":len(members),"git_blobs_verified":len(checked),"complete_game_files":len(production),"audio_assets_verified":len(assets["assets"]),"engine_elf":"ELF64 little-endian x86-64","licenses_verified":["LICENSE","release/licenses/Godot-LICENSE.txt","release/licenses/Godot-COPYRIGHT.txt","game/audio/provenance.json"],"assembly_python":platform.python_version(),"assembly_zlib":zlib.ZLIB_VERSION,"build_command":"python3 repo/scripts/build_linux_release.py --source "+source+" --engine-zip /opt/g-harness/workspace/G12/node_8_step_157/repo/.tools/godot.zip --output dist/rebuilt-linux-x86_64.tar.gz"}
(ROOT/"audit.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result,indent=2))
