#!/usr/bin/env python3
"""Focused post-render projection/occlusion investigation. Run from repository root."""
import argparse, datetime, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from PIL import Image
p=argparse.ArgumentParser()
p.add_argument("--prefix", default="n2-s138")
p.add_argument("--output", default="docs/node2-s138/concerns.json")
a=p.parse_args()
def load(p): return json.loads(Path(p).read_text())
def project(points,camera,viewport):
    c=np.array(camera); back=c-np.array([0,2,0]); back=back/np.linalg.norm(back)
    right=np.cross([0,1,0],back); right=right/np.linalg.norm(right); up=np.cross(back,right)
    delta=np.array(points)-c; depth=-(delta@back)
    focal=viewport[1]/(2*math.tan(math.radians(52)/2))
    return np.stack([viewport[0]/2+focal*(delta@right)/depth,viewport[1]/2-focal*(delta@up)/depth],axis=1),depth
sys.path.insert(0,"scripts")
from check_visibility import analyze
from check_dense_visibility import analyze as dense
report={"dense":[],"analytic":[],"timestamp_semantics":"UTC filesystem save times (not fabricated engine timestamps); dense simulation time is tick/60, paused during diagnostics; analytic steps are fixture offsets, not live elapsed time.","frames":[]}
for suffix in ["720p","4x3"]:
    d=Path("evidence/arena")/(a.prefix+"-dense-"+suffix)
    meta=load(d/"dense.json"); metrics=dense(d); rows=[]; previous=None
    oracle,_=project([[0,0,-10],[-3.6,.15,-10]],meta["camera"],meta["viewport"])
    assert np.max(np.abs(oracle-np.array([meta["records"][0]["exit"],meta["records"][0]["label"]])))<.001
    for rec,m in zip(meta["records"],metrics["records"]):
        pts=np.array([b["position"] for b in rec["poses"]]); xy,depth=project(pts,meta["camera"],meta["viewport"])
        ground=pts.copy(); ground[:,1]=0; gxy,_=project(ground,meta["camera"],meta["viewport"])
        margins=np.minimum(xy,np.array(meta["viewport"])-xy)
        assert depth.min()>.1 and depth.max()<160
        envelope=(np.abs(pts[:,0])<=13)&(np.abs(pts[:,2])<=13)&(pts[:,1]>=0)&(pts[:,1]<=8)
        assert (margins[envelope]>0).all()
        image=np.asarray(Image.open(d/(rec["prefix"]+"_color.png")).convert("RGB")).astype(float)
        diff=None if previous is None else float(np.abs(image-previous).mean())
        if diff is not None: assert diff>0
        previous=image
        rows.append(dict(tick=rec["tick"],simulation_seconds=rec["tick"]/60,
            actor_region_retained=m["landmarks"]["actor"]["retained_fraction"],
            actor_retained_pixels=m["landmarks"]["actor"]["retained_pixels"],
            offscreen_centers=[dict(id=rec["poses"][i]["id"],position=pts[i].tolist(),projected=xy[i].tolist()) for i in range(len(pts)) if margins[i].min()<0],minimum_center_margin_pixels=float(margins.min()), depth_range=[float(depth.min()),float(depth.max())],
            airborne_centers_above_1m=int((pts[:,1]>1).sum()),
            max_height=float(pts[:,1].max()),max_projected_height_separation_pixels=float(np.linalg.norm(xy-gxy,axis=1).max()),
            color_frame_mean_absolute_difference_from_previous=diff))
    report["dense"].append(dict(size=suffix,records=rows,
        limitation="Center frustum checks are not whole-cube visibility; actor measure is local cyan-class retention, not body visibility or recognition. Sparse samples do not bound continuous occlusion duration."))
    d=Path("evidence/arena")/(a.prefix+"-analytic-"+suffix)
    meta=load(d/"visibility.json"); metrics=analyze(d); worst=[]
    for rec,m in zip(meta["records"],metrics["records"]):
        if m["cubes_with_3_pixels"]!=3: continue
        xy,depth=project([pose[0] for pose in rec["poses"]],meta["camera"],meta["viewport"])
        margins=np.minimum(xy,np.array(meta["viewport"])-xy)
        assert margins.min()>0
        worst.append(dict(prefix=rec["prefix"],visible_pixels=m["visible_pixels"],isolated_pixels=m["isolated_pixels"],minimum_center_margin_pixels=float(margins.min())))
    assert worst
    report["analytic"].append(dict(size=suffix,three_of_seven_cases=worst,
        inference="Every cube center in these cases is on-screen. Compare individual and combined ID pixels to separate world occlusion from inter-fragment overlap; isolated zero pixels do not establish a missing mesh. No all-fragments-visible requirement is imposed."))
for d in sorted(Path("evidence/arena").glob(a.prefix+"-*")):
    for f in sorted(d.glob("*.png")):
        report["frames"].append(dict(path=str(f),saved_utc=datetime.datetime.fromtimestamp(f.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
report["frame_count"]=len(report["frames"])
report["passed"]=True
Path(a.output).write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="frames"},indent=2))
