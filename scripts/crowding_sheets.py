#!/usr/bin/env python3
"""Contact sheets of real captures: only crop/nearest-neighbor enlarge, never synthesize scene pixels."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, sys
root=Path(__file__).resolve().parents[1]
for name in sys.argv[1:]:
 d=root/'evidence/arena'/name; data=json.loads((d/'sequence.json').read_text()); dest=root/'docs/node2-s133'/name; dest.mkdir(exist_ok=True)
 manifest=[]
 for case in sorted(set(r['case'] for r in data['records'])):
  rows=[r for r in data['records'] if r['case']==case]
  centers=[r[k] for r in rows for k in ['actor_screen','cluster_screen']]
  # Include extraction/P3 reference region as well as actor/airborne cluster.
  w,h=data['viewport']; cx=sum(p[0] for p in centers)/len(centers); cy=sum(p[1] for p in centers)/len(centers)
  box=(max(0,min(w-250,int(cx-125))), max(0,min(h-280,int(cy-140))))
  box=(*box,box[0]+250,box[1]+280)
  sheet=Image.new('RGB',(1250,680),(13,19,27)); draw=ImageDraw.Draw(sheet)
  center=Image.open(d/rows[2]['file']).convert('RGB'); center.thumbnail((640,360)); sheet.paste(center,(0,20))
  draw.text((650,40),name+' / '+case,fill='white'); draw.text((650,65),'Chronological native 250x280 crops; fixed box '+str(box),fill='white')
  for i,r in enumerate(rows):
   im=Image.open(d/r['file']).convert('RGB'); sheet.paste(im.crop(box),(i*250,400)); draw.text((i*250+5,380),'offset %.2fs'%r['offset_seconds'],fill='white')
  path=dest/(case+'.png'); sheet.save(path)
  manifest.append(dict(sheet=str(path.relative_to(root)),sources=[str((d/r['file']).relative_to(root)) for r in rows],crop=box,order='left to right, 0.1s intervals',scale='native crop; overview thumbnail only'))
 (dest/'sheets.json').write_text(json.dumps(manifest,indent=2)+'\n')
