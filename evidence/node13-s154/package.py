#!/usr/bin/env python3
"""Archive validation work products, NOT a game/release package."""
import hashlib,json,shutil,subprocess,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidence/node13-s154'
groups={
 'raw-natural-movie':['n13-verified-movie'],
 'raw-natural-replay':['n13-verified-replay'],
 'raw-natural-timeout':['n13-verified-timeout'],
 'raw-natural-realtime':['n13-verified-realtime'],
 'raw-regressions':['n13-verified-rules-1','n13-verified-rules-2','n13-verified-integration','n13-verified-verification'],
 'development-history':['n13-dev1','n13-dev2','n13-dev-movie','n13-dev-timeout','n13-final-movie']}
manifest={}
for archive,names in groups.items():
    members=[]
    for name in names:
        directory=ROOT/'evidence'/name
        assert directory.is_dir(),directory
        members += [p for p in directory.rglob('*') if p.is_file() and 'shader_cache' not in p.parts and p.suffix!='.avi']
    with tarfile.open(OUT/(archive+'.tar.gz'),'w:gz') as tar:
        for p in sorted(members):
            relative=str(p.relative_to(ROOT));tar.add(p,arcname=relative,recursive=False)
            manifest[relative]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size,'archive':archive+'.tar.gz'}
    print(archive,(OUT/(archive+'.tar.gz')).stat().st_size,flush=True)
(OUT/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
shutil.copy2(ROOT/'evidence/n13-verified-movie/game.mp4',OUT/'natural-session.mp4')
shutil.copy2(ROOT/'evidence/n13-verified-movie/audio.wav',OUT/'actual-game-mixer.wav')
verification={}
for name in ['movie','replay','timeout','realtime']:
    verification[name]=json.loads((ROOT/('evidence/n13-verified-'+name)/'analysis.json').read_text())
verification['replay_comparison']=json.loads((ROOT/'evidence/n13-verified-replay/comparison.json').read_text())
verification['suite']=json.loads((ROOT/'evidence/n13-verified-verification/summary.json').read_text())
verification['commands']=json.loads((ROOT/'evidence/n13-verified-verification/commands.json').read_text())
(OUT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
(OUT/'source.diff').write_bytes(subprocess.check_output(['git','diff','04832df0af77769a10db15272ed901bac1dfd669','31fe4e6db34dce8c9e94281b0f3bd5ee27b284b8','--','game','scripts'],cwd=ROOT))
# Verify every tar member against the independent source manifest immediately.
for archive in groups:
    with tarfile.open(OUT/(archive+'.tar.gz'),'r:gz') as tar:
        for member in tar.getmembers():
            data=tar.extractfile(member).read();expected=manifest[member.name]
            assert hashlib.sha256(data).hexdigest()==expected['sha256'] and len(data)==expected['size']
(OUT/'archive-verification.json').write_text(json.dumps({'passed':True,'archives':len(groups),'members':len(manifest),'excluded':'Disposable shader caches and redundant MovieWriter AVI only; original AVI hash is in launch metadata.'},indent=2)+'\n')
files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='SHA256SUMS']
(OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(OUT))+'\n' for p in sorted(files)))
