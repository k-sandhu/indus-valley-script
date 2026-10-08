"""Inspect print components around known development field columns."""
import json
from pathlib import Path
import pipeline as P
import layout_v3 as OLD

OUT=P.RAW/'2026-10-08-v3/development-inspection'
OUT.mkdir(parents=True,exist_ok=True)
records=[]
with P.fitz.open(P.PDF) as doc:
    for number in [23,66,74,112,129,130,139,167,173]:
        gray=P.render(doc,number,4);small=P.render(doc,number,2)
        fs,side=OLD.fields(doc[number-1],small)
        columns=[]
        for col,f in enumerate(fs):
            left=max(0,round((f['left']-8)*4));right=min(gray.shape[1],round((f['right']+8)*4))
            patch=(gray[240:3160,left:right]<190).astype('uint8')
            n,labels,stats,cent=P.cv2.connectedComponentsWithStats(patch,8)
            comps=[dict(x=(left+x)/4,y=(240+y)/4,w=w/4,h=h/4,area=area/16) for x,y,w,h,area in stats[1:] if 1.0<=h/4<=6.5 and .3<=w/4<=7.5 and area/16>=.5]
            columns.append(dict(index=col,field=f,components=comps))
        records.append(dict(page=number,side=side,columns=columns))
        P.Image.fromarray(gray).save(OUT/f'page{number}_4x.png')
        print(json.dumps(dict(page=number,columns=len(fs),first_field=columns[0]['field'],first_components=columns[0]['components'][:25])),flush=True)
P.write(OUT/'components.json',records)
