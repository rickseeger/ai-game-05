#!/usr/bin/env python3
"""Independent signal/event/pixel validation. Numerical gates are not listening.
Dependencies: numpy, scipy. No model/vision/perceptual conclusions.
"""
import argparse, copy, csv, hashlib, json, subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import resample_poly, correlate
ROOT=Path(__file__).resolve().parents[1]
def load_wav(path):
    sr,x=wavfile.read(path)
    return sr,x.astype(np.float64)/2**(8*x.dtype.itemsize-1)
def peak(x):return float(np.max(np.abs(x)))
def signal_checks(r,x,sr):
    assert peak(x)<=.801, "limiter ceiling/headroom"
    assert not np.any(np.abs(x)>=.9999), "full-scale clipping"
    assert peak(resample_poly(x,4,1,axis=0))<.86, "intersample headroom"
    groups=r["timeline"]
    def window(e,start,end):
        t=e["frame"]/60
        return x[round((t+start)*sr):round((t+end)*sr)]
    def onset(e,threshold):
        z=window(e,-.05,.08)
        hits=np.flatnonzero(np.max(np.abs(z),axis=1)>threshold)
        assert len(hits), "missing attack"
        delay=float(hits[0]/sr-.05)
        assert 0<=delay<.05, "attack out of sync"
        return delay*1000
    selected=[groups[i] for i in [0,1,6,7,8]] # quiet preceding windows, no overlapping old impact
    timings=[{"phase":e["phase"],"frame":e["frame"],"onset_delay_ms":onset(e,.02 if e["phase"]=="crowded_default" else .002),"peak_first_800ms":peak(window(e,0,.8))} for e in selected]
    first_impact=next(e for e in r["source"] if e["kind"]=="impact")
    impact_delay=onset(first_impact,.001)
    silences={e["phase"]:peak(window(e,.08,.9)) for e in groups if e["phase"] in ["muted","zero_master"]}
    assert all(v<1e-7 for v in silences.values()), "mute/zero control leaks"
    low=next(e for e in groups if e["phase"]=="low_sfx")
    maximum=next(e for e in groups if e["phase"]=="max_single")
    ratio=peak(window(low,0,.8))/peak(window(maximum,0,.8))
    assert .15<ratio<.40, "SFX control ineffective"
    attack=window(groups[0],.03,.20).mean(axis=1)
    power=np.abs(np.fft.rfft(attack*np.hanning(len(attack))))**2
    frequencies=np.fft.rfftfreq(len(attack),1/sr)
    low_fraction=float(power[(frequencies>=35)&(frequencies<=200)].sum()/power.sum())
    assert low_fraction>.25, "missing low-frequency body"
    return {"sample_rate":sr,"channels":x.shape[1],"duration_s":len(x)/sr,"sample_peak":peak(x),"sample_peak_dbfs":float(20*np.log10(peak(x))),"true_peak_4x":peak(resample_poly(x,4,1,axis=0)),"clipped_samples":int(np.sum(np.abs(x)>=.9999)),"rms":float(np.sqrt(np.mean(x*x))),"isolated_break_onsets":timings,"first_emitted_contact_event_frame":first_impact["frame"],"first_emitted_impact_onset_delay_ms":impact_delay,"silence_after_80ms":silences,"low_to_max_single_peak_ratio":ratio,"attack_35_200hz_energy_fraction":low_fraction}
def routing_checks(r):
    assert r["passed"] and all(c["pass"] for c in r["checks"])
    plays=[e for e in r["audio"] if e["phase"]!="unit_muted" and not e["dropped"]]
    keys={(e["kind"],e["id"],e["engine_tick"]) for e in r["source"]}
    assert all((e["kind"],e["id"],e["tick"]) in keys for e in plays), "not same-tick source routing"
    assert all(1<=e["active"]<=8 and 0<=e["slot"]<8 for e in plays), "unbounded voices"
    impacts=[e for e in r["source"] if e["kind"]=="impact"]
    assert len(impacts)>50
    previous=-100; bodies={}
    for e in impacts:
        assert e["contacts"]>0 and e["pending_speed"]>=1 and e["speed"]>=1, "not thresholded solver contact"
        assert e["engine_tick"]-previous>=3, "global throttle"
        assert e["engine_tick"]-bodies.get(e["id"],-100)>=8, "body cooldown"
        previous=e["engine_tick"];bodies[e["id"]]=previous
    variants={k:[e["variant"] for e in plays if e["kind"]==k] for k in ["break","impact"]}
    for kind,count in [("break",4),("impact",6)]:
        assert len(set(variants[kind]))==count, "variation absent"
        assert all(a!=b for a,b in zip(variants[kind],variants[kind][1:])), "immediate sample repeats"
    return {"assertions":len(r["checks"]),"source_breaks":sum(e["kind"]=="break" for e in r["source"]),"source_impacts":len(impacts),"runtime_voice_requests":len(plays),"same_tick_matched":len(plays),"max_active_slots":max(e["active"] for e in plays),"burst_sample_variants":len(set(variants["break"])),"impact_sample_variants":len(set(variants["impact"])),"steals":sum(e["stolen"] for e in plays)}
def pixels(path,r):
    cmd=["ffmpeg","-v","error","-i",str(path),"-vf","crop=16:16:1198:128,scale=1:1","-f","rawvideo","-pix_fmt","rgb24","pipe:1"]
    a=np.frombuffer(subprocess.check_output(cmd),np.uint8).reshape(-1,3)
    red=np.flatnonzero((a[:,0]>180)&(a[:,1]<50)&(a[:,2]<50)).tolist()
    assert red==[e["frame"] for e in r["timeline"]], "rendered damage markers do not match event clock"
    cmd=["ffmpeg","-v","error","-i",str(path),"-vf","crop=980:430:100:180,scale=196:86","-f","rawvideo","-pix_fmt","gray","pipe:1"]
    gray=np.frombuffer(subprocess.check_output(cmd),np.uint8).reshape(-1,86,196).astype(int)
    f=r["timeline"][0]["frame"]
    changed=int(np.sum(np.abs(gray[f+30]-gray[f])>8))
    assert changed>100,"arena image does not change during physical flight"
    return {"frames":len(a),"marker_frames":red,"changed_downsampled_arena_pixels_launch_to_flight":changed,"visual_judgment":"UNASSESSED: numeric rendering/timestamp checks only"}
def playback(out, original, original_sr):
    data={}
    for name in ["playback-monitor.wav","live.wav"]:
        sr,x=load_wav(out/name)
        assert peak(x)>.1 and not np.any(np.abs(x)>=.9999)
        data[name]={"duration_s":len(x)/sr,"peak":peak(x),"clipped_samples":int(np.sum(np.abs(x)>=.9999))}
    rate,monitor=load_wav(out/"playback-monitor.wav")
    assert rate==original_sr and len(monitor)>=len(original)
    correlation=correlate(monitor[:,0], original[:,0], mode="valid", method="fft")
    offset=int(np.argmax(correlation))
    captured=monitor[offset:offset+len(original)]
    similarity=float(np.sum(captured*original)/np.sqrt(np.sum(captured*captured)*np.sum(original*original)))
    # Fidelity diagnostic is separate from exercising a playback path. This host
    # drops/drifts loopback samples; never promote nonzero transport to listening.
    data["delivered_wav_to_monitor"]={"offset_samples":offset,"normalized_correlation":similarity,"lossless_fidelity_gate_passed":similarity>.99,"limitation":"Full-recording fixed-offset fidelity failed on this virtual transport; do not use its clock for synchronization or listening claims"}
    meta=json.loads((out/"playback.json").read_text())
    assert meta["paplay_rc"]==0 and meta["engine_rc"]==0 and meta["hardware_playback_rc"]!=0
    data["live_routing"]=routing_checks(json.loads((out/"results.json").read_text()))
    data["listening"]="NONE. paplay -> PulseAudio null sink -> monitor is verified sample transport, not audible speakers or human listening. ALSA hw:0 failed."
    probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-count_frames","-select_streams","v:0","-show_entries","stream=nb_read_frames","-of","json",str(out/"live.mkv")]))
    data["live_video_frames"]=int(probe["streams"][0]["nb_read_frames"])
    data["live_video_limitation"]="External capture is supplemental, not used for precise sync; inspect live-encode.log for dropped frames. Primary MovieWriter video/PCM supplies the verified common clock."
    return data
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("--transport",type=Path);p.add_argument("--self-test",action="store_true");a=p.parse_args()
    r=json.loads((a.directory/"results.json").read_text());sr,x=load_wav(a.directory/"runtime.wav")
    meta=json.loads((a.directory/"launch.json").read_text())
    for f,h in meta["source_sha256"].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
    result={"routing":routing_checks(r),"signal":signal_checks(r,x,sr),"rendering":pixels(a.directory/"runtime.mp4",r)}
    frames=list(csv.DictReader((a.directory/"frames.csv").open()))
    assert max(int(f["active_voices"]) for f in frames)==8
    assert all(int(f["active_voices"])==0 for f in frames[-50:])
    assert max(int(f["active_bodies"]) for f in frames)==192
    raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(a.directory/"runtime.mp4"),"-vn","-f","f32le","-acodec","pcm_f32le","pipe:1"])
    aac=np.frombuffer(raw,dtype=np.float32)
    result["aac_preview"]={"decoded_peak":peak(aac),"clipped_samples":int(np.sum(abs(aac)>=1))}
    assert peak(aac)<1
    if a.transport:result["transport"]=playback(a.transport,x,sr)
    if a.self_test:
        rejected=[]
        for mutation in ["clip","silence","delay_250ms","mute_leak","route_wrong_tick","no_contact","no_variation","voices_9"]:
            bad=copy.deepcopy(r);z=x.copy()
            if mutation=="clip":z[100:110]=1
            if mutation=="silence":z[:]=0
            if mutation=="delay_250ms":z=np.roll(z,round(.25*sr),axis=0)
            if mutation=="mute_leak":z[round(10.5*sr):round(10.7*sr)]=.1
            if mutation=="route_wrong_tick":
                for e in bad["audio"]:e["tick"]+=1
            if mutation=="no_contact":
                for e in bad["source"]:
                    if e["kind"]=="impact":e["contacts"]=0
            if mutation=="no_variation":
                for e in bad["audio"]:e["variant"]=0
            if mutation=="voices_9":
                for e in bad["audio"]:e["active"]=9
            try:routing_checks(bad);signal_checks(bad,z,sr)
            except AssertionError:rejected.append(mutation)
            else:raise AssertionError("mutation incorrectly accepted: "+mutation)
        result["rejected_mutations"]=rejected
    result["audible_quality"]="UNVERIFIED: no subjective listening. Strong attack/weight is the synthesis/tuning intent, not an observed perception."
    (a.directory/"analysis.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
