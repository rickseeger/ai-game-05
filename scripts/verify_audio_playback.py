#!/usr/bin/env python3
"""Real PulseAudio transport + null-sink monitor; explicitly NOT human listening.
Requires an already-ready private PulseAudio server in PULSE_SERVER. Never starts
or modifies a system/user default audio daemon. Saves all subprocess outcomes.
"""
import argparse, datetime, hashlib, json, os, select, signal, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument("output");p.add_argument("--wav", type=Path, required=True);a=p.parse_args()
out=ROOT / "evidence/audio" / a.output;out.mkdir(parents=True,exist_ok=False)
env=dict(os.environ, GODOT_SILENCE_ROOT_WARNING="1", LIBGL_ALWAYS_SOFTWARE="1", AUDIO_OUT=str(out), XDG_DATA_HOME=str(out/"userdata"))
assert env.get("PULSE_SERVER"), "Supply a ready private PulseAudio socket"
meta={"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(), "pulse_server":env["PULSE_SERVER"], "listening":"NONE: null sink routes and discards samples. Worker cannot hear. No physical soundcard exists on this host.", "commands":[]}
def run(cmd, name, timeout=60):
    meta["commands"].append(cmd)
    r=subprocess.run(cmd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    (out/name).write_text(r.stdout);return r.returncode
run(["aplay","-l"],"hardware.txt")
run(["pactl","info"],"pulse-info.txt")
assert run(["pactl","list","sinks","short"],"sinks.txt")==0
# Exercise physical ALSA path explicitly; record failure rather than claiming a listen.
meta["hardware_playback_rc"]=run(["aplay","-D","hw:0",str(a.wav.resolve())],"hardware-playback.txt")
processes=[];logs=[]
try:
    # Monitor the available null-sink playback path while paplay sends the actual WAV.
    cmd=["parec","--device=g12_audio_validation.monitor","--file-format=wav","--format=s16le","--rate=48000","--channels=2",str(out/"playback-monitor.wav")]
    meta["commands"].append(cmd)
    log=(out/"parec.log").open("w");logs.append(log)
    monitor=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT);processes.append(monitor)
    deadline=time.monotonic()+10
    while True:
        state=subprocess.check_output(["pactl","list","source-outputs","short"],env=env,text=True)
        if state.strip(): break
        assert monitor.poll() is None and time.monotonic()<deadline
        time.sleep(.05) # readiness polling, not a blind start delay
    (out/"monitor-ready.txt").write_text(state)
    meta["paplay_rc"]=run(["paplay","--device=g12_audio_validation",str(a.wav.resolve())],"paplay.txt")
    # paplay completion does not mean parec flushed its buffered samples. Keep
    # recording actual monitor output through a bounded drain window; never pad
    # or manufacture PCM. This cannot repair dropped/drifting virtual transport.
    import wave
    with wave.open(str(a.wav), "rb") as original:
        minimum_bytes = round((original.getnframes()/original.getframerate()+1.0)*48000)*4+44
    deadline = time.monotonic()+5
    while (out/"playback-monitor.wav").stat().st_size < minimum_bytes:
        assert monitor.poll() is None and time.monotonic() < deadline, "monitor drain timeout"
        time.sleep(.05)
    meta["monitor_drain_minimum_bytes"] = minimum_bytes
    monitor.send_signal(signal.SIGINT);meta["parec_rc"]=monitor.wait(timeout=10)
    assert meta["paplay_rc"]==0
    # New real-time rendered engine process, external screen + Pulse monitor capture.
    rfd,wfd=os.pipe()
    xcmd=["Xvfb","-displayfd",str(wfd),"-screen","0","1280x720x24","-nolisten","tcp"]
    log=(out/"xvfb.log").open("w");logs.append(log)
    xvfb=subprocess.Popen(xcmd,pass_fds=[wfd],stdout=log,stderr=subprocess.STDOUT);processes.append(xvfb);os.close(wfd)
    assert select.select([rfd],[],[],10)[0]
    env["DISPLAY"]=":"+os.read(rfd,64).decode().strip();os.close(rfd)
    cmd=["ffmpeg","-y","-nostdin","-thread_queue_size","1024","-f","x11grab","-framerate","30","-video_size","1280x720","-i",env["DISPLAY"],"-thread_queue_size","1024","-f","pulse","-i","g12_audio_validation.monitor","-c:v","libx264","-preset","ultrafast","-crf","20","-threads","1","-pix_fmt","yuv420p","-c:a","pcm_s16le","-progress","pipe:1",str(out/"live.mkv")]
    meta["commands"].append(cmd)
    log=(out/"live-encode.log").open("w");logs.append(log)
    recorder=subprocess.Popen(cmd,env=env,stdout=subprocess.PIPE,stderr=log);processes.append(recorder)
    assert select.select([recorder.stdout],[],[],15)[0], "recorder not ready"
    (out/"recorder-ready.txt").write_bytes(os.read(recorder.stdout.fileno(),4096))
    godot=os.environ.get("GODOT_BIN",str(ROOT/".tools/Godot_v4.5.1-stable_linux.x86_64"))
    cmd=[godot,"--path",str(ROOT/"game"),"res://destruction_demo.tscn","--audio-driver","PulseAudio","--rendering-method","gl_compatibility","--resolution","1280x720","--disable-vsync","--max-fps","60","--","--audio-test"]
    meta["engine_rc"]=run(cmd,"engine.log",timeout=120)
    recorder.send_signal(signal.SIGINT)
    recorder.communicate(timeout=20);meta["live_recorder_rc"]=recorder.returncode
    assert meta["engine_rc"]==0
    assert json.loads((out/"results.json").read_text())["driver"]=="PulseAudio"
    run(["ffmpeg","-y","-i",str(out/"live.mkv"),"-vn","-c:a","pcm_s16le",str(out/"live.wav")],"live-extract.log")
finally:
    for proc in reversed(processes):
        if proc.poll() is None:
            proc.terminate();proc.wait(timeout=10)
    for log in logs:log.close()
    meta["wav_sha256"]=hashlib.sha256(a.wav.read_bytes()).hexdigest()
    meta["source_sha256"]={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/"game").rglob("*") if f.is_file() and ".godot" not in f.parts and f.suffix!=".uid"}
    (out/"playback.json").write_text(json.dumps(meta,indent=2)+"\n")
print(json.dumps(meta,indent=2))
