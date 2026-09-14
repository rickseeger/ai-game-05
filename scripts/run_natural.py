#!/usr/bin/env python3
"""Default production entry + opt-in input-only driver, private user settings."""
import argparse,datetime,gzip,hashlib,json,os,signal,subprocess,time
from pathlib import Path
from release_context import source_commit, source_status
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--mode',choices=['victory','timeout'],default='victory');p.add_argument('--movie',action='store_true');p.add_argument('--fixed',action='store_true');p.add_argument('--frames',action='store_true');p.add_argument('--replay',type=Path);a=p.parse_args()
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
godot=Path(os.environ.get('GODOT_BIN',ROOT/'.tools/Godot_v4.5.1-stable_linux.x86_64')).resolve()
cmd=['xvfb-run','-a','-s','-screen 0 1280x1024x24',str(godot),'--path',str(ROOT/'game'),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--resolution','1280x720','--disable-vsync','--verbose']
if a.movie:cmd+=['--write-movie',str(out/'game.avi'),'--fixed-fps','60']
elif a.fixed:cmd+=['--fixed-fps','60']
else:cmd+=['--max-fps','60']
cmd+=['--','--natural-test']
env=dict(os.environ,NATURAL_OUT=str(out),NATURAL_MODE=a.mode,NATURAL_MOVIE=str(int(a.movie or a.frames)),XDG_DATA_HOME=str(out/'userdata'),LIBGL_ALWAYS_SOFTWARE='1',GODOT_SILENCE_ROOT_WARNING='1')
if a.replay:
    with gzip.open(a.replay/'events.jsonl.gz','rt') as f:original=[json.loads(l) for l in f]
    payload=[e for e in original if e['kind'].startswith('input_') or e['kind'] in ['early_extraction','pause_start','pause_end','end']]
    (out/'replay-input.json').write_text(json.dumps(payload))
    env['NATURAL_REPLAY']=str(out/'replay-input.json')
meta={'command':cmd,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':source_commit(),'source_status':source_status(),'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/'game').rglob('*') if f.is_file() and '.godot' not in f.parts},'engine_sha256':hashlib.sha256(godot.read_bytes()).hexdigest(),'mode':a.mode,'replay_source':str(a.replay) if a.replay else None,'replay_sha256':hashlib.sha256((out/'replay-input.json').read_bytes()).hexdigest() if a.replay else None,'frames':a.frames,'movie':a.movie,'fixed':a.fixed or a.movie,'environment':{k:env[k] for k in ['NATURAL_OUT','NATURAL_MODE','XDG_DATA_HOME','LIBGL_ALWAYS_SOFTWARE']},'uname':list(os.uname())}
(out/'launch.json').write_text(json.dumps(meta,indent=2))
t=time.monotonic()
with (out/'engine.log').open('w') as log:
    proc=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try:rc=proc.wait(timeout=1200)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid,signal.SIGTERM);proc.wait();rc=124
meta.update(returncode=rc,wall_seconds=time.monotonic()-t)
(out/'launch.json').write_text(json.dumps(meta,indent=2))
print((out/'engine.log').read_text())
if a.movie and (out/'game.avi').exists():
    with (out/'encode.log').open('w') as log:
        subprocess.run(['ffmpeg','-y','-i',str(out/'game.avi'),'-map','0:v','-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-threads','2','-map','0:a','-c:a','aac',str(out/'game.mp4'),'-map','0:a','-c:a','pcm_s32le',str(out/'audio.wav')],stdout=log,stderr=subprocess.STDOUT,check=True)
    (out/'video.json').write_text(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'game.mp4')],text=True))
    meta['original_avi_sha256']=hashlib.sha256((out/'game.avi').read_bytes()).hexdigest()
    (out/'launch.json').write_text(json.dumps(meta,indent=2))
    (out/'game.avi').unlink()
for f in out.glob('*.jsonl'):
    with gzip.open(str(f)+'.gz','wb') as z:z.write(f.read_bytes())
    f.unlink()
print(json.dumps({'returncode':rc,'wall_seconds':meta['wall_seconds'],'output':str(out)}))
assert rc==0 and 'SCRIPT ERROR' not in (out/'engine.log').read_text()
raise SystemExit(rc)
