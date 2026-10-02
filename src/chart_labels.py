"""Recognize ONLY decimal inventory labels, with a source-font reference set.

The first 13 independently read cells form the training set; later cells are
reserved for evaluation. This never OCRs or interprets the Indus glyphs.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image,ImageDraw
import visual_transcription as v

ROOT=v.ROOT
OUT=v.OUT


def runs(profile):
    edges=np.diff(np.r_[False,profile,False].astype(int))
    return list(zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)))


def digits(gray,x,y):
    patch=gray[y-15:y+23,x-51:x-21]<190
    # Rank and stable code have distinct baselines; retain the lower dense line.
    ys=runs(patch.any(axis=1))
    if not ys:return [],None
    # A single blank scan row separates the two printed baselines. Bridging
    # it would join upper ranks to lower codes and poison digit prototypes.
    viable=[(a,b) for a,b in ys if b-a>=5 and patch[a:b].sum()>=8]
    if not viable:return [],None
    a,b=max(viable,key=lambda ab:ab[1])
    line=patch[a:b]
    xx=runs(line.any(axis=0))
    return [line[:,c:d] for c,d in xx],line


def distance(a,b):
    h=max(a.shape[0],b.shape[0])+6;w=max(a.shape[1],b.shape[1])+6
    values=[]
    for dy in [-1,0,1]:
        aa=np.zeros((h,w),bool);bb=np.zeros((h,w),bool)
        aa[3:3+a.shape[0],(w-a.shape[1])//2:(w-a.shape[1])//2+a.shape[1]]=a
        bb[3+dy:3+dy+b.shape[0],(w-b.shape[1])//2:(w-b.shape[1])//2+b.shape[1]]=b
        values.append((distance_transform_edt(~aa)[bb].mean()+distance_transform_edt(~bb)[aa].mean())/2
                      +.08*abs(a.shape[1]-b.shape[1])+.03*abs(a.shape[0]-b.shape[0]))
    return min(values)


def main():
    gold=json.loads((ROOT/'research/corpus/primary/1979_chart_pdf20_column0_manual.json').read_text())
    images={p:v.render(p) for p in [20,21]}
    centers={p:{c:v.row_centers(images[p],round(x+100.4*c),n) for c in range(10)}
             for p,x,n in [(20,176,35),(21,153,35)]}
    font=[];errors=[]
    for row in gold['rows'][:13]:
        r=row['row_0based'];parts,line=digits(images[20],176,centers[20][0][r])
        code=row['printed_code']
        if len(parts)!=len(code):errors.append({'row':r,'code':code,'segments':len(parts)});continue
        font.extend((label,part,r) for label,part in zip(code,parts))
    if set(k for k,_,_ in font)!=set('0123456789'):raise ValueError('Training set does not cover all digits')
    predictions=[]
    for page,x0,n in [(20,176,35),(21,153,35)]:
        for col in range(10):
            x=round(x0+100.4*col)
            for row,y in enumerate(centers[page][col]):
                parts,line=digits(images[page],x,y)
                choices=[]
                for part in parts:
                    scores=sorted((min(distance(part,b) for k,b,_ in font if k==label),label)
                                  for label in '0123456789')
                    choices.append({'digit':scores[0][1],'distance':float(scores[0][0]),
                                    'margin':float(scores[1][0]-scores[0][0])})
                predictions.append({'key':f'{page}:{col}:{row}','code_font':''.join(z['digit'] for z in choices),
                                    'digits':choices,'status':'UNVERIFIED source-font numerical prediction'})
    lookup={z['key']:z for z in predictions}
    evaluation=[dict(row,predicted=lookup[f"20:0:{row['row_0based']}"]['code_font']) for row in gold['rows'][13:]]
    result={'source_sha256':gold['source_sha256'],'training_rows':'PDF20 col0 rows0..12; manually transcribed independently',
            'training_segmentation_errors':errors,'training_digit_prototypes':len(font),
            'heldout_first_column':{'n':len(evaluation),'correct':sum(z['predicted']==z['printed_code'] for z in evaluation),
                                   'records':evaluation},'predictions':predictions,
            'caution':'Geometry was developed on this chart. This is an exploratory numeric-label test, not a population accuracy estimate.'}
    (OUT/'font_label_predictions_unverified.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['training_segmentation_errors','training_digit_prototypes']},indent=2))
    print(json.dumps(result['heldout_first_column'],indent=2))


if __name__=='__main__':main()
