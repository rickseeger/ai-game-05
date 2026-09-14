#!/usr/bin/env python3
"""Serial reproducible natural-play suite. Use a fresh output prefix."""
import argparse,datetime,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('prefix');a=p.parse_args();assert Path(a.prefix).name==a.prefix and a.prefix not in ('.','..')
out=ROOT/'evidence'/(a.prefix+'-verification');out.mkdir(exist_ok=False)
base='evidence/'+a.prefix;commands=[]
def run(args,name):
    cmd=[sys.executable]+args
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (out/name).open('w') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=1800)
    commands.append({'command':cmd,'utc':started,'returncode':r.returncode,'output':name})
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n');print(name,r.returncode,flush=True)
    if r.returncode:raise SystemExit(r.returncode)
run(['scripts/run_natural.py',base+'-movie','--movie'],'movie.log')
run(['scripts/check_natural.py',base+'-movie','--self-test'],'movie-checks.log')
run(['scripts/run_natural.py',base+'-replay','--movie','--replay',base+'-movie'],'replay.log')
run(['scripts/check_natural.py',base+'-replay','--self-test'],'replay-checks.log')
run(['scripts/compare_natural_replay.py',base+'-movie',base+'-replay'],'comparison.log')
run(['scripts/run_natural.py',base+'-timeout','--mode','timeout','--fixed','--frames'],'timeout.log')
run(['scripts/check_natural.py',base+'-timeout'],'timeout-checks.log')
run(['scripts/run_natural.py',base+'-realtime'],'realtime.log')
run(['scripts/check_natural.py',base+'-realtime'],'realtime-checks.log')
for i in (1,2):run(['scripts/run_session.py',base+'-rules-'+str(i)],'rules-'+str(i)+'.log')
run(['scripts/check_session.py',base+'-rules-1',base+'-rules-2'],'rules-checks.log')
run(['scripts/run_integration.py',base+'-integration'],'integration.log')
run(['scripts/check_integration.py',base+'-integration'],'integration-checks.log')
summary={'passed':True,'commands':len(commands),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
