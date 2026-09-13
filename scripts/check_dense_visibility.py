#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from check_visibility import read,roi

def analyze(directory):
    d=Path(directory);meta=json.loads((d/"dense.json").read_text());rows=[]
    assert json.loads((d/"launch.json").read_text())["returncode"]==0
    log=(d/"engine.log").read_text();assert "OpenGL API" in log and "ERROR" not in log
    for rec in meta["records"]:
        pre=rec["prefix"];color=read(d/(pre+"_color.png"));clean=read(d/(pre+"_clean.png"));mask=read(d/(pre+"_ids.png")); no_shadow=read(d/(pre+"_no_shadows.png"))
        # 8x8x3 palette uses coarse levels, tolerating Compatibility sRGB byte rounding.
        index=np.rint((mask-np.array([16,16,16]))/np.array([32,32,64])).astype(int)
        reconstructed=index*np.array([32,32,64])+16
        valid=(abs(reconstructed-mask).max(2)<=6)&(abs(mask-color).max(2)>10)&(index[:,:,0]>=0)&(index[:,:,0]<8)&(index[:,:,1]>=0)&(index[:,:,1]<8)&(index[:,:,2]>=0)&(index[:,:,2]<3)
        ids=index[:,:,0]+8*index[:,:,1]+64*index[:,:,2]
        counts=np.bincount(ids[valid],minlength=192)
        assert rec["count"]==192 and len(counts)==192
        landmarks={}
        for name,half,kind in [("actor",(13,10),"cyan"),("contact",(22,5),"cyan"),("exit",(28,20),"mint"),("label",(34,12),"mint")]:
            ref=roi(clean,rec[name],half,kind);actual=roi(color,rec[name],half,kind)
            total=int(ref.sum());retained=int((ref&actual).sum())
            landmarks[name]=dict(reference_pixels=total,retained_pixels=retained,retained_fraction=retained/total if total else None)
        shadow=(no_shadow.astype(float).mean(2)-color.astype(float).mean(2)>10)&~valid
        rows.append(dict(prefix=pre,visible_pixels=counts.tolist(),cubes_with_3_pixels=int((counts>=3).sum()),debris_pixels=int(counts.sum()),
            shadow_darkened_non_debris_pixels=int(shadow.sum()),landmarks=landmarks,sentries=rec["sentries"],health=rec["health"]))
    perspective={}
    for name in ["near","far"]:
        a=read(d/("perspective_"+name+".png"));perspective[name+"_pixels"]=int(((a[:,:,0]>250)&(a[:,:,1]<3)&(a[:,:,2]>250)).sum())
    assert perspective["near_pixels"]>perspective["far_pixels"]*1.5>0
    return dict(directory=str(d),perspective=perspective,records=rows,limitations="ID pass changes only materials, not depth/poses. Palette quantization excludes antialiased boundary pixels. Shadow difference includes world and actor shadows. Physics is paused during diagnostics, not eased during the live intervals.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory");p.add_argument("--output",required=True);a=p.parse_args();r=analyze(a.directory);Path(a.output).write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(dict(perspective=r["perspective"],frames=[{k:v for k,v in x.items() if k!="visible_pixels"} for x in r["records"]]),indent=2))
