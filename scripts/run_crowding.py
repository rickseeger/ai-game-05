#!/usr/bin/env python3
import argparse, hashlib, json, os, signal, subprocess, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('output'); p.add_argument('--size',default='1280x720'); p.add_argument('--verify-presentation',action='store_true'); a=p.parse_args()
assert Path(a.output).name==a.output and a.output not in ('.','..')
w,h=map(int,a.size.split('x')); assert min(w,h)>=360
out=ROOT/'evidence/arena'/a.output; out.mkdir(parents=True,exist_ok=False)
godot=os.environ['GODOT_BIN']
cmd=['xvfb-run','-a','-s',f'-screen 0 {max(w,1280)}x{max(h,1024)}x24',godot,'--path',str(ROOT/'game'),'--script','res://tests/crowding_replay.gd','--rendering-method','gl_compatibility','--audio-driver','Dummy','--resolution',a.size,'--disable-vsync','--max-fps','60']
if a.verify_presentation: cmd += ['--','--verify-presentation']
env=dict(os.environ,ARENA_OUT=str(out),CROWDING_CASES=str(ROOT/'docs/node2-s133/cases.json'),LIBGL_ALWAYS_SOFTWARE='1',GODOT_SILENCE_ROOT_WARNING='1')
start=time.monotonic()
with (out/'engine.log').open('w') as f:
 child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 try: code=child.wait(timeout=90)
 except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGTERM); child.wait(); code=124
meta=dict(command=cmd,environment={k:env[k] for k in ['ARENA_OUT','CROWDING_CASES','LIBGL_ALWAYS_SOFTWARE','GODOT_SILENCE_ROOT_WARNING']},returncode=code,wall_seconds=time.monotonic()-start,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'game').rglob('*')) if f.suffix in ['.gd','.gdshader','.tscn','.godot'] and '.godot' not in f.parts})
(out/'launch.json').write_text(json.dumps(meta,indent=2)+'\n')
print((out/'engine.log').read_text()); print(json.dumps(meta,indent=2)); raise SystemExit(code)
