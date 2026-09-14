#!/usr/bin/env python3
"""Compare independent engine runs driven by the same recorded ordinary inputs."""
import argparse,hashlib,json
from pathlib import Path
from check_natural import rows
p=argparse.ArgumentParser();p.add_argument('original',type=Path);p.add_argument('replay',type=Path);a=p.parse_args()
x=rows(a.original/'events.jsonl.gz');y=rows(a.replay/'events.jsonl.gz')
def canonical(rows):
    result=[]
    for e in rows:
        if e['kind'] in ['hit','bolt','target_destroyed','damage','dash','progress','state','reset','terminal','end','early_extraction']:
            e={k:v for k,v in e.items() if k not in ['usec','frame','phase','collider','nodes','engine_tick']}
            # Godot collider auto-names and last-bit floating values are not gameplay.
            def clean(v):
                if isinstance(v,float):return round(v,4)
                if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k not in ['nodes','voices','body_throttle','visible_debris','collisions']}
                if isinstance(v,list):return [clean(x) for x in v]
                return v
            result.append(clean(e))
    return result
cx,cy=canonical(x),canonical(y)
if cx!=cy:
    for i,(a,b) in enumerate(zip(cx,cy)):
        if a!=b:print(json.dumps({'first_difference':i,'original':a,'replay':b},indent=2));break
assert cx==cy, 'independent exact-input runtime differs'
meta=json.loads((a.replay/'launch.json').read_text())
assert hashlib.sha256((a.replay/'replay-input.json').read_bytes()).hexdigest()==meta['replay_sha256']
result={'passed':True,'compared_events':len(cx),'scope':'Independent fresh default-engine process; replays only recorded InputEvents and observation times, no bot navigation/aim decisions. Float tolerance 0.0001; diagnostic IDs/voice occupancy excluded.'}
(a.replay/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
