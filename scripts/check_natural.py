#!/usr/bin/env python3
"""Independent assertions over input, combat, session, solver, rendered and PCM evidence.
No rules fixture or supplied pass flags are accepted as natural-play evidence.
"""
import argparse,collections,copy,gzip,hashlib,json,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parents[1]
def rows(p):
    with gzip.open(p,'rt') as f:return [json.loads(l) for l in f]
def only(r,k):return [e for e in r if e['kind']==k]
def check_rules(r,mode):
    initial=only(r,'initial')[0];g=initial['generation'];term=only(r,'terminal');resets=only(r,'reset')
    assert [e['state'] for e in term]==([2,3] if mode=='victory' else [3]), 'natural outcomes'
    assert len(resets)==len(term), 'retry count'
    env=only(r,'environment')[0];assert env['display']=='X11' and env['physics_hz']==60
    pa=only(r,'pause_start')[0];pb=only(r,'pause_end')[0]
    for k in ['state','time','health','p','enemies','bolts','debris','opposition_time']:assert pa[k]==pb[k], 'pause '+k
    assert pb['tick']-pa['tick']==60 and pa['state']==1
    for reset in resets:
        expected={'state':0,'time':0,'health':100,'p':[0,0,10],'remaining':3,'unlocked':False,'inside':False,'reason':'',
          'enemies':[],'pending':2,'bolts':0,'debris':0,'visible_debris':0,'shots':0,'player_shots':0,'dashes':0,'dash_left':0,
          'fire_left':0,'held':{},'pointer_known':False,'aim_valid':False,'opposition_time':0,'next_spawn':15,'next_enemy':102,
          'voices':0,'body_throttle':0,'clock_error':0,'buses':initial['buses'],'nodes':initial['nodes'],
          'master':initial['master'],'sfx':initial['sfx'],'muted':initial['muted'],'targets':initial['targets']}
        for k,value in expected.items():assert reset[k]==value, 'reset '+k
        retry=[e for e in only(r,'input_key') if e['generation']==reset['generation']-1 and e['pressed'] and e['code']==82]
        assert retry and retry[-1]['engine_tick']==reset['engine_tick'], 'ordinary R boundary'
        later=[e for e in only(r,'sample') if e['generation']==reset['generation'] and e['time']>2.5]
        assert later and later[0]['shots']>=4 and np.linalg.norm(np.array(later[0]['p'])-[0,0,10])>1, 'fresh movement/fire'
        assert any(e['generation']==reset['generation'] for e in only(r,'target_destroyed')), 'fresh pylon combat'
    # Each observed target destruction is downstream of four independent swept
    # player bolt hits, which themselves have a real fired signal/input lineage.
    bolts={e['id']:e for e in only(r,'bolt')}
    deaths=only(r,'target_destroyed')
    for e in deaths:
        hits=[h for h in only(r,'hit') if h['generation']==e['generation'] and h['target']==e['id'] and h['damage']>0]
        assert len(hits)==4 and sum(h['damage'] for h in hits)==100, 'four real hits'
        assert hits[-1]['engine_tick']==e['engine_tick'], 'destruction hit tick'
        for h in hits:
            b=bolts[h['id']];assert b['friendly'] and h['friendly'] and b['damage']==25 and b['engine_tick']<=h['engine_tick']
            fired=[f for f in only(r,'fired') if f['generation']==e['generation'] and f['engine_tick']==b['engine_tick']]
            assert len(fired)==1 and np.allclose(fired[0]['p'],b['position']), 'normal player fire origin'
        t=next(t for t in e['snapshot']['targets'] if t['id']==e['id'])
        assert t['destroyed'] and not t['intact'] and t['health']==0
        assert any(b['engine_tick']==e['engine_tick'] and b['p']==e['p'] and len(b['bodies'])==32 for b in only(r,'burst')), 'pylon physical burst'
    for e in only(r,'progress'):
        if e['remaining']==3:assert any(x['engine_tick']==e['engine_tick'] for x in resets)
        else:
            d=[x for x in deaths if x['generation']==e['generation'] and x['engine_tick']<=e['engine_tick']]
            assert len({x['id'] for x in d})==3-e['remaining'] and d[-1]['engine_tick']==e['engine_tick'], 'distinct destruction progress'
    for t in term:
        if t['state']==2:
            assert t['unlocked'] and t['remaining']==0 and t['inside'] and t['health']>0 and t['time']<150, 'victory eligibility'
            assert np.linalg.norm(np.array(t['p'])[[0,2]]-[0,-10])<=1.5
        elif t['reason']=='death':
            ds=[e for e in only(r,'damage') if e['generation']==t['generation']]
            assert len(ds)==7 and all(e['amount']==15 for e in ds) and t['health']==0 and t['time']<150, 'natural lethal pressure'
            for d in ds:assert any(h['engine_tick']==d['engine_tick'] and not h['friendly'] and h['damage']==15 and h['target']==0 for h in only(r,'hit')), 'real threat hit'
        else:assert t['reason']=='timeout' and t['time']==150 and t['health']>0, 'natural deadline'
    if mode=='victory':
        early=only(r,'early_extraction');assert len(early)==1 and early[0]['inside'] and not early[0]['unlocked'] and early[0]['remaining']==3 and early[0]['state']==0
        assert len([e for e in deaths if e['generation']==g])==3
        assert only(r,'dash') and max(d['distance'] for d in only(r,'dash'))>2.9
    # Tick-to-tick continuity disallows hidden position, clock or health jumps.
    samples=only(r,'sample')
    for a,b in zip(samples,samples[1:]):
        if a['generation']!=b['generation']:continue
        dt=b['time']-a['time'];assert -.000001<=dt<=1/60+.000001, 'clock continuity'
        ds=[d for d in only(r,'damage') if d['generation']==a['generation'] and a['engine_tick']<=d['engine_tick']<b['engine_tick']]
        assert b['health']==max(0,a['health']-sum(d['amount'] for d in ds)), 'health continuity'
        dash=[d for d in only(r,'dash') if a['engine_tick']<=d['engine_tick']<b['engine_tick']]
        assert np.linalg.norm(np.array(b['p'])-a['p'])<=5/60+.01+sum(d['distance'] for d in dash), 'movement continuity'
        assert b['unlocked']==(b['remaining']==0)
        if b['state']==2:assert b['inside'] and b['unlocked']
    end=only(r,'end')[-1];assert end['reason']=='finished' and end['snapshot']['state']==0
    return {'terminals':[{'generation':e['generation'],'state':e['state'],'reason':e['reason'],'active_seconds':e['time'],'health':e['health'],'shots':e['shots']} for e in term],
        'resets':len(resets),'destructions':len(deaths),'hits':len(only(r,'hit')),'threat_attacks':len(only(r,'attack')),'input_events':sum(e['kind'].startswith('input_') for e in r),'samples':len(samples)}

def check_physics(r,pr):
    tracks=collections.defaultdict(list)
    for sample in pr:
        for b in sample['bodies']:tracks[b['id']].append(b)
    details=[]
    for burst in only(r,'burst'):
        launch=burst['bodies'];assert len(launch) in [16,32]
        assert all(4.5<=b['v'][1]<=7.5 for b in launch), 'upward launch'
        assert len({tuple(b['v']) for b in launch})==len(launch) and len({tuple(b['w']) for b in launch})==len(launch), 'random velocity/spin'
        if len(launch)!=32 or burst['generation']!=only(r,'initial')[0]['generation']:continue
        for first in launch:
            tr=tracks[first['id']];assert len(tr)>350
            pos=np.array([b['p'] for b in tr]);vel=np.array([b['v'] for b in tr]);spin=np.array([b['w'] for b in tr]);age=np.array([b['age'] for b in tr])
            assert pos[:,1].max()>first['p'][1]+.6 and np.any(vel[:,1]<-1), 'gravity descent'
            air=(age>.05)&(age<.35);acc=np.diff(vel[:,1])[air[:-1]]*60
            assert -11.0<float(np.median(acc))<-8.8, 'gravity acceleration'
            ground=[i for i,b in enumerate(tr) if 'Ground' in b.get('colliders',[]) and b['contacts']>0]
            assert ground, 'real ground collision'
            contact=ground[0]
            assert np.any(vel[max(0,contact-3):contact+25,1]>.3), 'subsequent bounce'
            rolling=[i for i in ground if age[i]>age[contact]+.25 and np.linalg.norm(spin[i])>.2 and np.linalg.norm(vel[i,[0,2]])>.03]
            assert rolling, 'ground rolling motion'
            assert np.linalg.norm(vel[-1])<.15 or tr[-1]['sleeping'], 'eventual settling'
            details.append({'id':first['id'],'burst':burst['id'],'max_height':float(pos[:,1].max()),'gravity_median':float(np.median(acc)),'first_ground_age':float(age[contact]),'rolling_samples':len(rolling),'last_speed':float(np.linalg.norm(vel[-1])),'sleeping':tr[-1]['sleeping']})
    assert len(details)==96, 'three full 32-cube pylon tracks'
    return {'pylon_arcs':len(details),'samples':sum(len(v) for v in tracks.values()),'tracks':details}

def check_audio(r,sr,x):
    assert sr==48000 and x.ndim==2 and x.shape[1]==2
    assert .02<float(abs(x).max())<.81 and not np.any(abs(x)>=.9999), 'non-silent unclipped mixer'
    sources={(e['kind'],e['id'],e['engine_tick']) for e in r if e['kind'] in ['burst','impact']}
    audio=[e for e in only(r,'audio') if not e['audio']['dropped']]
    for e in audio:
        a=e['audio'];kind='burst' if a['kind']=='break' else 'impact'
        assert (kind,a['id'],a['tick']) in sources and a['tick']==e['engine_tick'], 'same-tick mixer source'
        assert 1<=a['active']<=8 and 0<=a['slot']<8
    # Preselect sparse source events from trace, then require a quiet signal
    # window and a real measured onset 0..50ms later. No waveform is synthesized.
    candidates=[];last=-1000
    for e in audio:
        if e['frame']-last>=16:candidates.append(e)
        last=e['frame']
    onsets=[]
    for e in candidates:
        t=e['frame']/60;z=x[round((t-.05)*sr):round((t+.1)*sr)]
        if len(z)!=round(.15*sr) or abs(z[:round(.05*sr)]).max()>.00025:continue
        hits=np.flatnonzero(abs(z).max(axis=1)>.0005)
        assert len(hits), 'missing source attack'
        delay=hits[0]/sr-.05
        assert 0<=delay<.05, 'mixer attack synchronization'
        onsets.append({'kind':e['audio']['kind'],'frame':e['frame'],'delay_ms':delay*1000,'peak':float(abs(z).max())})
    assert sum(e['kind']=='break' for e in onsets)>=3 and sum(e['kind']=='impact' for e in onsets)>=3, 'sparse break/impact onsets'
    first=only(r,'burst')[0]['frame']/60
    assert abs(x[:round(first*sr)]).max()<.000001, 'silence before first physical source'
    return {'sample_rate':sr,'channels':2,'seconds':len(x)/sr,'peak':float(abs(x).max()),'rms':float(np.sqrt(np.mean(x*x))),'clipped_samples':int(np.sum(abs(x)>=.9999)),'matched_sources':len(audio),'onsets':onsets}

def check_pixels(out,r):
    # Decode every video frame; compare sparse original PNG readbacks against
    # their exact recorded movie frame, independently of the engine event flags.
    cmd=['ffmpeg','-v','error','-i',str(out/'game.mp4'),'-vf','scale=320:180','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
    rgb=np.frombuffer(subprocess.check_output(cmd),np.uint8).reshape(-1,180,320,3)
    assert len(rgb)>1000 and rgb.std()>15
    captures=only(r,'capture');checks=[]
    for e in captures:
        f=e['captured_frame'];img=Image.open(out/e['file']).convert('RGB');assert img.size==(1280,720) and e['error']==0
        small=np.asarray(img.resize((320,180),Image.Resampling.BILINEAR)).astype(float)
        error=float(abs(small-rgb[f]).mean());assert error<3, 'PNG/video timestamp match'
        a=np.asarray(img);orange=(a[:,:,0]>a[:,:,1]*1.2)&(a[:,:,1]>a[:,:,2]*1.4)&(a[:,:,0]>110)
        projected=e.get('projected_bodies',[]);matched=0
        for b in projected:
            x,y=map(round,b['pixel']);patch=orange[max(0,y-5):min(720,y+6),max(0,x-5):min(1280,x+6)]
            matched+=bool(patch.size and patch.any())
        checks.append({'frame':f,'png_movie_mae':error,'projected_bodies':len(projected),'orange_near_projected':matched})
    assert sum(e['orange_near_projected'] for e in checks)>200, 'rendered fragment pixel presence'
    flight=[]
    for b in only(r,'burst'):
        f=b['frame']
        if f+90>=len(rgb):continue
        # Central arena ROI excludes HUD and settings, not a subjective metric.
        changed=int(np.sum(np.max(abs(rgb[f+30,35:150].astype(int)-rgb[f,35:150].astype(int)),axis=2)>12))
        assert changed>30, 'rendered destruction activity'
        flight.append({'burst':b['id'],'frame':f,'changed_arena_pixels_30_frames_later':changed})
    return {'decoded_frames':len(rgb),'captures':checks,'flight_differences':flight,'subjective':'UNASSESSED'}

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--self-test',action='store_true');a=p.parse_args();out=a.output
    meta=json.loads((out/'launch.json').read_text());assert meta['returncode']==0
    assert '--natural-test' in meta['command'] and '--script' not in meta['command'] and not any(v.endswith('.tscn') for v in meta['command']), 'default entry'
    for name,h in meta['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h, 'source '+name
    r=rows(out/'events.jsonl.gz');result={'source_commit':meta['source_commit'],'rules':check_rules(r,meta['mode'])}
    if meta['mode']=='victory':result['physics']=check_physics(r,rows(out/'physics.jsonl.gz'))
    if meta['movie']:
        sr,x=wavfile.read(out/'audio.wav');x=x.astype(np.float64)/2**(8*x.dtype.itemsize-1)
        result['audio']=check_audio(r,sr,x);result['pixels']=check_pixels(out,r)
    fr=rows(out/'frames.jsonl.gz');interval=np.array([x['interval_usec']/1000 for x in fr[10:]])
    result['performance']={'fixed_fps':meta['fixed'],'wall_seconds':meta['wall_seconds'],'frame_interval_ms':dict(zip(['p50','p95','p99'],map(float,np.percentile(interval,[50,95,99])))),'mean_observed_fps':1000/float(interval.mean()),'max_frame_ms':float(interval.max()),'note':'Offline fixed-FPS evidence is NOT real-time performance. Unfixed run measures this software-rendered host including observation overhead; not Rick hardware.'}
    if a.self_test:
        rejected=[]
        for name in ['win_locked','missing_hit','missing_retry','reset_dirty','health_jump','no_early_entry']:
            bad=copy.deepcopy(r)
            if name=='win_locked':only(bad,'terminal')[0]['unlocked']=False
            elif name=='missing_hit':bad.remove(next(e for e in only(bad,'hit') if e['target']==1 and e['damage']>0))
            elif name=='missing_retry':bad=[e for e in bad if not(e['kind']=='input_key' and e['code']==82)]
            elif name=='reset_dirty':only(bad,'reset')[0]['debris']=1
            elif name=='health_jump':only(bad,'sample')[150]['health']=42
            else:only(bad,'early_extraction')[0]['inside']=False
            try:check_rules(bad,meta['mode'])
            except AssertionError:rejected.append(name)
            else:raise AssertionError('accepted mutation '+name)
        if meta['movie']:
            for name,z in [('silent',np.zeros_like(x)),('delayed',np.roll(x,sr//4,axis=0)),('clipped',np.ones_like(x))]:
                try:check_audio(r,sr,z)
                except AssertionError:rejected.append(name)
                else:raise AssertionError('accepted audio mutation '+name)
        result['rejected_mutations']=rejected
    result['passed']=True
    (out/'analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['physics','pixels']},indent=2))
if __name__=='__main__':main()
