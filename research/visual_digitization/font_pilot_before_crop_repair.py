"""Fresh plotted-font matching pilot; no linguistic or sequential prior."""
from __future__ import annotations
import json,sys,time,hashlib
from pathlib import Path
import numpy as np
import cv2
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from visual_transcription import render,mask,trim_x,match
OUT=ROOT/'research/visual_digitization/fresh_font_pilot'

def crop_library():
    labels=json.loads((ROOT/'research/chart_reference/manual_numeric_reference_provisional.json').read_text())
    pages={p:render(p) for p in [20,21]};output=[]
    for r in labels['rows']:
        p,c,row=r['pdf_page'],r['column'],r['row'];x=(176 if p==20 else 153)+100.4*c;y=152.6+40.1*row
        crop=pages[p][round(y-19.5):round(y+19.5),round(x-31):round(x+31)]
        b=trim_x(mask(crop))
        if b is None:continue
        # Preserve vertical height and scanned chart uncertainty auxiliaries.
        ys=np.flatnonzero(b.any(axis=1));b=b[ys[0]:ys[-1]+1]
        png=OUT/'templates'/f'p{p}_c{c}_r{row}.png';png.parent.mkdir(parents=True,exist_ok=True)
        Image.fromarray(np.where(b,0,255).astype('uint8')).save(png)
        output.append({'key':f'{p}:{c}:{row}','code_ocr':{'value':str(r['code'])},'rank_ocr':{'value':str(r['rank'])},
            'code_manual':r['code'],'numeric_alternatives':r['alternatives'],'dashed_auxiliary':r['dashed_auxiliary'],
            'binary':b,'source_row':r,'crop_xyxy_2x':[round(x-31),round(y-19.5),round(x+31),round(y+19.5)]})
    (OUT/'template_metadata.json').write_text(json.dumps([{k:v for k,v in x.items() if k!='binary'} for x in output],indent=2))
    return output

def candidates(strip,library):
    b=mask(strip); projected=b.sum(axis=0)>=2
    edges=np.diff(np.r_[False,projected,False].astype(int)); comps=list(zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)))
    choices={}
    for i in range(len(comps)):
        for j in range(i,min(len(comps),i+12)):
            x0,x1=comps[i][0],comps[j][1]
            if x1-x0>68:break
            if j>i and comps[j][0]-comps[j-1][1]>20:break
            bb=b[:,x0:x1];ys=np.flatnonzero(bb.any(axis=1))
            if not len(ys):continue
            bb=bb[ys[0]:ys[-1]+1]
            alternatives=match(bb,library)
            if alternatives:choices[i,j+1]={'x_bounds':[int(x0),int(x1)],'alternatives':alternatives,
                'shape_cost':alternatives[0]['distance_pixels']*float(bb.sum())/100}
    return comps,choices

def paths(comps,choices,penalty):
    n=len(comps);cost=[float('inf')]*(n+1);path=[None]*(n+1);cost[0]=0;path[0]=[]
    for i in range(n):
        if path[i] is None:continue
        for (a,j),item in choices.items():
            if a!=i:continue
            value=cost[i]+item['shape_cost']+penalty
            if value<cost[j]:cost[j]=value;path[j]=path[i]+[item]
        if cost[i]+30<cost[i+1]:
            cost[i+1]=cost[i]+30;path[i+1]=path[i]+[{'x_bounds':list(map(int,comps[i])),'alternatives':[],'unmatched':True}]
    return path[n],cost[n]

def main():
    OUT.mkdir(parents=True,exist_ok=True);start=time.monotonic();library=crop_library();page=render(30);rows=[]
    for col,(x0,x1,id0) in enumerate([(150,512,1015),(680,1036,1051)]):
        for row in range(3,8):
            y=round(155+40.25*row);strip=page[y-19:y+20,x0:x1]
            components,choices=candidates(strip,library);variants={}
            for penalty in [.5,1,2,4]:
                tokens,cost=paths(components,choices,penalty);variants[str(penalty)]={'tokens':tokens,'cost':cost}
            record={'id':id0+row,'column':col,'row':row,'crop_xyxy_2x':[x0,y-19,x1,y+20],
                'variants':variants,'scope':'Provisional glyph and segmentation predictions; printed-row physical sides unknown.'}
            rows.append(record)
            Image.fromarray(strip).resize((strip.shape[1]*3,strip.shape[0]*3)).save(OUT/f'row_{id0+row}.png')
            (OUT/'predictions_before_gold.json').write_text(json.dumps({'rows':rows,'complete':len(rows)==10,
                'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'manual_labels_sha256':hashlib.sha256((ROOT/'research/chart_reference/manual_numeric_reference_provisional.json').read_bytes()).hexdigest(),
                'runtime_seconds':time.monotonic()-start},indent=2))
            print(json.dumps({'id':id0+row,'tokens_by_penalty':{k:len(v['tokens']) for k,v in variants.items()},'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':main()
