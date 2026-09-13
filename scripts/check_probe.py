#!/usr/bin/env python3
"""Checks recorded engine observations, not hypothetical expected motion."""
import array, csv, json, math, pathlib, subprocess, sys, wave
p = pathlib.Path(sys.argv[1])
rows = list(csv.DictReader((p / 'physics.csv').open()))
events = list(csv.DictReader((p / 'events.csv').open()))
groups = {}
for row in rows:
    r = {k: float(v) for k, v in row.items()}
    groups.setdefault(int(r['id']), []).append(r)
contact_ids = {int(e['id']) for e in events if e['event'] == 'ground_contact'}
results = []
for i, rs in sorted(groups.items()):
    first = rs[0]
    contact_tick = min((int(e['tick']) for e in events if e['event'] == 'ground_contact' and int(e['id']) == i), default=9999)
    bounce = any(r['tick'] >= contact_tick and r['vy'] > 0.25 and r['tick'] <= contact_tick + 12 for r in rs)
    spin = max(sum((r[k]-first[k])**2 for k in ('qx','qy','qz','qw')) for r in rs) > 0.1
    rising = max(r['y'] for r in rs) > first['y'] + 0.6
    falling = any(r['vy'] < -1 for r in rs)
    stable = min(r['y'] for r in rs) > 0.05 and rs[-1]['y'] < 0.4
    # Near-surface translation accompanied by rotation is tumbling/sliding evidence,
    # not a claim of pure no-slip rolling (cubes do not roll like spheres).
    tumble = any(r['tick'] > contact_tick and r['y'] < 0.5 and math.hypot(r['vx'],r['vz']) > 0.1 and math.sqrt(sum(r[k]**2 for k in ('wx','wy','wz'))) > 0.2 for r in rs)
    results.append(dict(id=i,rose=rising,fell=falling,rotated=spin,contact=i in contact_ids,bounced=bounce,ground_tumble=tumble,settled=stable,max_y=max(r['y'] for r in rs),final_y=rs[-1]['y']))
with wave.open(str(p/'audio.wav')) as w:
    rate, channels, sample_width, frames = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    assert sample_width == 2
    samples=array.array('h',w.readframes(frames))
    if sys.byteorder != 'little': samples.byteswap()
    peak=max(abs(v) for v in samples)
    rms=math.sqrt(sum(v*v for v in samples)/len(samples))
    def window_rms(t, duration=.12):
        window=samples[int(t*rate)*channels:int((t+duration)*rate)*channels]
        return math.sqrt(sum(v*v for v in window)/max(1,len(window)))
    destruction_rms=window_rms(.5)
    impact_events=[e for e in events if e['event']=='impact_sound']
    impact_rms=[window_rms(int(e['tick'])/60) for e in impact_events]
image_checks={}
for name in ('launch','airborne','collision','settled'):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p/(name+'.png')),'-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
    image_checks[name]={'width':960,'height':540,'unique_rgb_colors':len(set(zip(raw[::3],raw[1::3],raw[2::3])))}
    assert len(raw)==960*540*3
checks={
    '32_bodies':len(groups)==32,
    'all_rose_fell_rotated_contacted_settled':all(all(r[k] for k in ('rose','fell','rotated','contact','settled')) for r in results),
    'all_bounced':all(r['bounced'] for r in results),
    'ground_tumbling_observed':sum(r['ground_tumble'] for r in results)>=24,
    'rendered_nonuniform_frames':all(v['unique_rgb_colors']>100 for v in image_checks.values()),
    'distinct_frames':len({(p/(n+'.png')).read_bytes() for n in image_checks})==4,
    'captured_destruction_and_impacts':destruction_rms>10 and len(impact_rms)>0 and max(impact_rms)>10,
    'audio_not_clipped':peak<32767,
    'completed': 'PROBE_DONE ticks=420 bodies=32' in (p/'engine.log').read_text(),
    'no_engine_errors':not any(s in (p/'engine.log').read_text() for s in ('SCRIPT ERROR','ERROR:'))
}
report={'checks':checks,'passed':all(checks.values()),'physics_samples':len(rows),'bodies':results,'ground_contact_events':sum(e['event']=='ground_contact' for e in events),'impact_sound_events':len(impact_events),'audio':{'sample_rate':rate,'channels':channels,'duration_seconds':frames/rate,'peak_s16':peak,'rms_s16':rms,'destruction_window_rms':destruction_rms,'max_impact_window_rms':max(impact_rms,default=0),'path':'Godot MovieWriter mixed output; not hardware or audible validation'},'frames':image_checks}
print(json.dumps(report,indent=2))
sys.exit(0 if report['passed'] else 1)
