#!/usr/bin/env python3
"""Negative controls ensure the evidence checker does not pass silence/static motion."""
import csv, json, pathlib, shutil, subprocess, sys, tempfile, wave
root=pathlib.Path(__file__).resolve().parents[1]
checker=root/'scripts/check_probe.py'
results={}
with tempfile.TemporaryDirectory() as td:
    sample=pathlib.Path(td)/'sample'
    shutil.copytree(root/'evidence/run1',sample)
    def check(name,expected):
        run=subprocess.run([sys.executable,str(checker),str(sample)],capture_output=True,text=True)
        report=json.loads(run.stdout)
        assert (run.returncode==0)==expected, (name,run.stdout,run.stderr)
        results[name]={'expected_pass':expected,'actual_pass':report['passed'],'failed_checks':[k for k,v in report['checks'].items() if not v]}
    check('recorded_baseline',True)
    with wave.open(str(sample/'audio.wav')) as w:
        params=w.getparams()
    with wave.open(str(sample/'audio.wav'),'wb') as w:
        w.setparams(params);w.writeframes(bytes(params.nframes*params.nchannels*params.sampwidth))
    check('reject_silence',False)
    shutil.copy2(root/'evidence/run1/audio.wav',sample/'audio.wav')
    rows=list(csv.DictReader((sample/'physics.csv').open()))
    for r in rows:
        r.update(y='0.17',vy='0',qx='0',qy='0',qz='0',qw='1',wx='0',wy='0',wz='0')
    with (sample/'physics.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    check('reject_static_physics',False)
print(json.dumps(results,indent=2))
