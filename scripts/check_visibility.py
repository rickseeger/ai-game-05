#!/usr/bin/env python3
"""Renderer-pixel visibility/occlusion metrics. Not a subjective visual oracle."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image

def read(p): return np.asarray(Image.open(p).convert("RGB")).astype(np.int16)
def ids(im):
    valid=(im[:,:,1]<3)&(im[:,:,2]>252)&(im[:,:,0]>25)
    return np.where(valid,np.rint(im[:,:,0]/32).astype(int),0)
def roi(im,point,half,kind):
    x,y=map(round,point); w,h=half
    a=im[max(0,y-h):y+h+1,max(0,x-w):x+w+1]
    r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    if kind=="cyan": return (b>g+5)&(g>r*1.3)&(b>95)
    return (g>b+8)&(b>r*1.2)&(g>120)
def analyze(directory):
    d=Path(directory); meta=json.loads((d/"visibility.json").read_text()); rows=[]
    launch=json.loads((d/"launch.json").read_text()); assert launch["returncode"]==0
    assert "OpenGL API" in (d/"engine.log").read_text()
    for rec in meta["records"]:
        pre=rec["prefix"]; color=read(d/(pre+"_color.png")); clean=read(d/(pre+"_clean.png")); mask=ids(read(d/(pre+"_ids.png")))
        assert list(color.shape[:2][::-1])==meta["viewport"]
        visible=[]; isolated=[]
        for i in range(7):
            solo=ids(read(d/(pre+f"_solo{i}.png")))
            isolated.append(int((solo==i+1).sum())); visible.append(int((mask==i+1).sum()))
        assert sum(isolated)>0
        landmarks={}
        for name,half,kind in [("actor",(13,10),"cyan"),("contact",(22,5),"cyan"),("exit",(28,20),"mint"),("label",(34,12),"mint")]:
            ref=roi(clean,rec[name],half,kind); actual=roi(color,rec[name],half,kind)
            # Pixel-for-pixel color-class retention, not bounding-box visibility.
            total=int(ref.sum()); retained=int((ref&actual).sum())
            landmarks[name]={"reference_pixels":total,"retained_pixels":retained,"retained_fraction":retained/total if total else None}
        seams=[]
        for axis in (0,1):
            m=np.moveaxis(mask,axis,0); c=np.moveaxis(color,axis,0).astype(float)
            edge=(m[:-1]>0)&(m[1:]>0)&(m[:-1]!=m[1:])
            diff=np.linalg.norm(c[:-1]-c[1:],axis=2)
            seams.extend(diff[edge].tolist())
        rows.append(dict(prefix=pre,visible_pixels=visible,isolated_pixels=isolated,
            visible_fraction=[v/s if s else 0.0 for v,s in zip(visible,isolated)],
            cubes_with_3_pixels=sum(v>=3 for v in visible),landmarks=landmarks,
            seam_samples=len(seams),seam_rgb_mean=float(np.mean(seams)) if seams else None))
    summary={"frames":len(rows),"minimum_cubes_with_3_pixels":min(r["cubes_with_3_pixels"] for r in rows),
        "mean_visible_fraction":float(np.mean([v for r in rows for v in r["visible_fraction"]])),
        "mean_seam_rgb":float(np.average([r["seam_rgb_mean"] for r in rows if r["seam_samples"]],weights=[r["seam_samples"] for r in rows if r["seam_samples"]])),
        "landmark_minimum_retained_fraction":{n:min(r["landmarks"][n]["retained_fraction"] for r in rows if r["landmarks"][n]["retained_fraction"] is not None) for n in rows[0]["landmarks"]}}
    return dict(directory=str(d),camera=meta["camera"],summary=summary,records=rows,limitation="Color-class retention is a sampled visibility proxy, not OCR or subjective readability. ID passes quantify depth-visible surfaces, not the recognizability of hidden faces.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory");p.add_argument("--output",required=True);a=p.parse_args()
    report=analyze(a.directory);Path(a.output).write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report["summary"],indent=2))
