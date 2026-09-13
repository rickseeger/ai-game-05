#!/usr/bin/env python3
"""Engineering regression guardrails on real pixels; NOT perceptual acceptance."""
import argparse,copy,json
from pathlib import Path
from check_visibility import analyze
from check_dense_visibility import analyze as dense

def guard(r):
    rows=r["records"]
    cases=json.loads((Path(__file__).resolve().parents[1]/"docs/node2-s133/cases.json").read_text())
    assert {x["prefix"] for x in rows}=={c["id"]+f"_{s:02d}" for c in cases for s in [0,6,12,18,24]}
    assert len(rows)==40
    for row in rows:
        assert len(row["visible_pixels"])==len(row["isolated_pixels"])==7
        assert all(0<=v<=s for v,s in zip(row["visible_pixels"],row["isolated_pixels"]))
        assert row["cubes_with_3_pixels"]>=3 and sum(row["visible_pixels"])>=60
        for n,minimum in dict(actor=.60,contact=.70,exit=.75,label=.98).items():
            m=row["landmarks"][n]
            assert m["reference_pixels"]>=25 and m["retained_fraction"]>=minimum,(row["prefix"],n,m)

def dense_guard(r):
    assert len(r["records"])==6
    assert [x["prefix"] for x in r["records"]]==[f"dense_{t:03d}" for t in [1,12,30,60,90,120]]
    for row in r["records"]:
        assert len(row["visible_pixels"])==192 and row["cubes_with_3_pixels"]>=125
        assert row["debris_pixels"]>=5000 and row["shadow_darkened_non_debris_pixels"]>=1000
        assert row["sentries"]==2
        for n,minimum in dict(actor=.25,contact=.60,exit=.50,label=.75).items():
            m=row["landmarks"][n]
            assert m["retained_pixels"]>=64 and m["retained_fraction"]>=minimum,(row["prefix"],n,m)

def run(a):
    reports=[analyze(d) for d in a.analytic]; dense_reports=[dense(d) for d in a.dense]
    for r in reports: guard(r)
    for r in dense_reports: dense_guard(r)
    negatives=[]
    for mode in ["missing_frame","lost_actor","lost_label","lost_debris"]:
        r=copy.deepcopy(reports[0])
        if mode=="missing_frame":r["records"].pop()
        elif mode=="lost_actor":r["records"][0]["landmarks"]["actor"]["retained_fraction"]=0
        elif mode=="lost_label":r["records"][0]["landmarks"]["label"]["retained_fraction"]=0
        else:r["records"][0]["visible_pixels"]=[0]*7
        try:guard(r)
        except AssertionError:negatives.append(mode)
        else:raise AssertionError("missed negative "+mode)
    # Historical baseline is measured again, not forged negative evidence.
    before=[analyze(d) for d in a.before]
    comparisons=[]
    for b,r in zip(before,reports):
        bm=json.loads((Path(b["directory"])/"visibility.json").read_text());am=json.loads((Path(r["directory"])/"visibility.json").read_text())
        assert [x["poses"] for x in bm["records"]]==[x["poses"] for x in am["records"]]
        bs=b["summary"];s=r["summary"]
        assert s["mean_visible_fraction"]>bs["mean_visible_fraction"]+.015
        assert s["landmark_minimum_retained_fraction"]["actor"]>bs["landmark_minimum_retained_fraction"]["actor"]+.05
        try:guard(b)
        except AssertionError:baseline_rejected=True
        else:baseline_rejected=False
        assert baseline_rejected
        comparisons.append(dict(before=b["directory"],after=r["directory"],identical_poses=True,before_summary=bs,after_summary=s,baseline_rejected=baseline_rejected))
    return dict(passed=True,analytic=reports,dense=dense_reports,comparisons=comparisons,rejected_mutations=negatives,
        limitation="Sampled engineering bounds chosen to preserve identity cues, not a new acceptance contract. Dense bursts still occlude most cyan body pixels briefly; human motion/readability judgment remains required.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--analytic",nargs="+",required=True);p.add_argument("--dense",nargs="+",required=True);p.add_argument("--before",nargs="+",required=True);p.add_argument("--output",required=True);a=p.parse_args();r=run(a);Path(a.output).write_text(json.dumps(r,indent=2)+"\n");print(json.dumps({k:v for k,v in r.items() if k not in ["analytic","dense"]},indent=2))
