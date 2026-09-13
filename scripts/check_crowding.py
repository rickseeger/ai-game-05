#!/usr/bin/env python3
"""Technical preservation/capture check, expressly NOT a perceptual-readability oracle."""
import hashlib, json, subprocess
from pathlib import Path
from check_arena import image_data
ROOT=Path(__file__).resolve().parents[1]
def old(path): return subprocess.check_output(['git','show','3e2072699e640b98cb9b788b199eb659f5eec914:'+path],cwd=ROOT,text=True)
def now(path): return (ROOT/path).read_text()
def section(s,start,end=None): return s.split(start,1)[1].split(end,1)[0] if end else s.split(start,1)[1]
def verify():
 preservation={
 'camera_byte_identical':old('game/arena_camera.gd')==now('game/arena_camera.gd'),
 'ring_batch_function_byte_identical':section(old('game/arena.gd'),'static func ring','static func label')==section(now('game/arena.gd'),'static func ring','static func label'),
 'fixture_poses_byte_identical':section(old('game/arena_preview.gd'),'func set_fixture','func _process')==section(now('game/arena_preview.gd'),'func set_fixture','func _process'),
 'destruction_constants_identical':old('game/destruction.gd').split('func _ready')[0]==now('game/destruction.gd').split('func _ready')[0],
 'destruction_motion_cap_lifetime_render_batch_update_identical':section(old('game/destruction.gd'),'func _process')==section(now('game/destruction.gd'),'func _process'),
 'rigid_body_script_identical':old('game/debris_block.gd')==now('game/debris_block.gd'),
 'player_fixed_step_and_input_identical':section(old('game/player.gd'),'func _physics_process')==section(now('game/player.gd'),'func _physics_process'),
 'destruction_workload_identical':old('game/tests/destruction_tests.gd')==now('game/tests/destruction_tests.gd')}
 assert all(preservation.values()),preservation
 cases=json.loads((ROOT/'docs/node2-s133/cases.json').read_text()); pairs=[]
 for before,after in [('n2-s133-before-720p-v2','n2-s133-after-720p-v2'),('n2-s133-before-4x3','n2-s133-after-4x3-v2')]:
  bd=ROOT/'evidence/arena'/before; ad=ROOT/'evidence/arena'/after
  b=json.loads((bd/'sequence.json').read_text()); a=json.loads((ad/'sequence.json').read_text())
  assert b['records']==a['records'], 'Any change to poses, projection or sampled times invalidates this A/B replay'
  assert len(a['records'])==40 and len(a['checks'])==225 and len(set(a['checks']))==225
  for case in cases:
   if 'original' in case:
    r=next(r for r in a['records'] if r['case']==case['id'] and r['step']==12)
    assert max(abs(r['at'][0]-case['original']['x']),abs(r['at'][2]-case['original']['z']),abs(r['height']-case['original']['height']))<0.00001
  images=[]
  for d in (bd,ad):
   assert json.loads((d/'launch.json').read_text())['returncode']==0
   log=(d/'engine.log').read_text(); assert 'OpenGL API' in log and 'ERROR' not in log
   for r in a['records']: images.append(image_data(d/r['file'],a['viewport'])[1])
  pairs.append(dict(before=before,after=after,identical_records=len(a['records']),assertions=len(a['checks']),images=images))
 visions=[]
 for p in sorted((ROOT/'docs/node2-s133').glob('*vision.json')):
  v=json.loads(p.read_text()); assert v['response']['success'] is True, p
  assert hashlib.sha256((ROOT/v['image']).read_bytes()).hexdigest()==v['sha256'],p
  visions.append(str(p.relative_to(ROOT)))
 return dict(passed=True,preservation=preservation,pairs=pairs,verified_vision_records=visions,limitation='Frame containment, checks and hashes do not prove perceptual readability. Read the saved pixel-grounded analyses and review.md.')
if __name__=='__main__': print(json.dumps(verify(),indent=2))
