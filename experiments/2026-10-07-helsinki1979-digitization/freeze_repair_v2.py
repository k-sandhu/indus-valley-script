"""Freeze the repaired pipeline, then draw and predict a new blind source sample."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import random
import shutil
import time
import numpy as np
from PIL import Image,ImageDraw
import layout_v3 as L
import pipeline as P

HERE=P.HERE
OUT=HERE/'repair/2026-10-07-v2'
DEVELOPMENT=[22,25,30,37,62,78,100,129,130,145]
SECTIONS=[('number_order',22,78,28),('end_sorted',79,130,26),('beginning_sorted',131,180,26)]


def now():return datetime.now(timezone.utc).isoformat()


def freeze():
    if OUT.exists():raise FileExistsError('Repair endpoint exists')
    OUT.mkdir(parents=True)
    sources=['layout_v3.py','freeze_repair_v2.py','evaluate_repair.py','pipeline.py','evaluate.py','chart-snapshot.json',
             'development/classifier.pt','development/digits.npz','development/calibration.json']
    manifest=dict(status='Frozen evaluation',created_utc=now(),code_hashes={p:P.sha(HERE/p) for p in sources},
       source_sha256=P.sha(P.PDF),parameters=L.PARAM,development_pages=DEVELOPMENT,
       sample=dict(seed=2026100780,sections=SECTIONS,n=80,exclude_previous_targets=True),
       source_row_counts=dict(seed=2026100791,random_pages_per_section=6,stress_pages=[62,129,130]),
       readers='Two independent source-only readers on every row and count page; third reader adjudicates without predictions',
       release_rule=dict(minimum_unit_confidence=.90,product_unit_confidences=.90,minimum_global_row_recall=.95,
          other_global_criteria=dict(crop=.90,number=.90,count=.95,top5_whole_rows=.80),
          required=['upright resolved layout','no clipping or continuation','no auxiliary/candidate ambiguity','singleton top-one codes','numeric-witness agreement'],
          object_import_requires_reviewed_identity_and_surface=True),
       prior_evaluation_unchanged=True,recognizer_refitted=False)
    P.write(OUT/'freeze-manifest.json',manifest);print(json.dumps(dict(frozen_utc=manifest['created_utc'])),flush=True)


def chart_cards():
    folder=OUT/'blind/position-chart';folder.mkdir(parents=True)
    labels=json.loads((HERE/'chart-snapshot.json').read_text())['rows']
    with P.fitz.open(P.PDF) as doc:
        pages={p:P.render(doc,p) for p in (20,21)}
    for start in range(0,len(labels),60):
        canvas=Image.new('RGB',(1200,1200),'white');draw=ImageDraw.Draw(canvas)
        for i,label in enumerate(labels[start:start+60]):
            p,c,r=label['pdf_page'],label['column'],label['row'];x=(176 if p==20 else 153)+100.4*c;y=152.6+40.1*r
            x0,y0,x1,y1=round(x-20),round(y-19.5),round(x+31),round(y+19.5)
            im=Image.fromarray(pages[p][y0:y1,x0:x1]);im=im.resize((102,78))
            xx,yy=(i%10)*120,(i//10)*200;canvas.paste(im,(xx+8,yy+8));draw.rectangle((xx+7,yy+7,xx+111,yy+88),outline='#b0b0b0')
            codes=sorted(set([label['code']]+label['alternatives']))
            draw.text((xx+3,yy+100),'/'.join(map(str,codes)),fill='black');draw.text((xx+3,yy+120),f'{p}:{c}:{r}',fill='black')
        canvas.save(folder/f'chart_{start:03d}.png',optimize=True)


def sample():
    freeze_path=OUT/'freeze-manifest.json';manifest=json.loads(freeze_path.read_text())
    assert all(P.sha(HERE/name)==digest for name,digest in manifest['code_hashes'].items())
    if (OUT/'prediction-freeze.json').exists():raise FileExistsError('Predictions already frozen')
    blind=OUT/'blind';blind.mkdir(parents=True,exist_ok=True)
    old=json.loads((HERE/'blind/selection.json').read_text())['rows']
    frame=[];page_meta=[];started=time.monotonic()
    with P.fitz.open(P.PDF) as doc:
        for p in range(22,181):
            _,rows,meta=L.process(doc,p)
            page_meta.append(dict(pdf_page=p,layout=meta))
            for r in rows:
                r['section']=next(s for s,a,b,_ in SECTIONS if a<=p<=b)
                box=r['glyph_pdf_box'];center=(box[1]+box[3])/2
                previously_read=any(o['pdf_page']==p and o['pdf_column']==r['pdf_column'] and
                  abs(center-(o['glyph_pdf_box'][1]+o['glyph_pdf_box'][3])/2)<10 for o in old)
                if p not in DEVELOPMENT and not previously_read:frame.append(r)
            print(json.dumps(dict(frame_page=p,eligible_rows=len(frame))),flush=True)
    P.write(OUT/'frame.json',dict(status='Frozen evaluation',rows=frame,pages=page_meta,
                                 freeze_sha256=P.sha(freeze_path),seconds=time.monotonic()-started))
    rng=random.Random(2026100780);selected=[];denominators={}
    for s,a,b,n in SECTIONS:
        pool=[r for r in frame if r['section']==s];denominators[s]=len(pool)
        selected.extend(rng.sample(pool,n))
    selected.sort(key=lambda r:(r['pdf_page'],r['pdf_column'],r['row_index']))
    count_rng=random.Random(2026100791);count_pages=[]
    for s,a,b,_ in SECTIONS:count_pages.extend(count_rng.sample(list(range(a,b+1)),6))
    count_pages=sorted(set(count_pages+[62,129,130]))
    chart_cards();rec=P.Recognizer(P.templates(),HERE/'development/classifier.pt');predictions=[];locators=[]
    with P.fitz.open(P.PDF) as doc:
        for page in sorted({r['pdf_page'] for r in selected}):
            gray=P.render(doc,page)
            for index,r in enumerate(selected):
                if r['pdf_page']!=page:continue
                r=dict(r);r['sample_index']=index;x0,y0,x1,y1=r['glyph_xyxy_2x']
                r['units'],r['segmentation_cost']=rec.segment(gray[y0:y1,x0:x1]);r['auxiliaries']=[]
                predictions.append(r)
                # Source context contains the complete column and neighbouring rows; no OCR witnesses or flags.
                box=r['glyph_pdf_box'];field=r['margin_xyxy_2x'];left=min(box[0],field[0]/2)-6;right=max(box[2],field[2]/2)+9
                context=[max(0,left),max(55,box[1]-18),min(doc[page-1].rect.width,right),min(795,box[3]+18)]
                pix=doc[page-1].get_pixmap(matrix=P.fitz.Matrix(5,5),clip=P.fitz.Rect(context),colorspace=P.fitz.csGRAY)
                name=f'row_{index:03d}_pdf{page}.png';pix.save(blind/name)
                glyph_pix=doc[page-1].get_pixmap(matrix=P.fitz.Matrix(5,5),clip=P.fitz.Rect(box),colorspace=P.fitz.csGRAY)
                exact=f'exact_{index:03d}.png';glyph_pix.save(blind/exact)
                locators.append(dict(sample_index=index,pdf_page=page,section=r['section'],target_glyph_pdf_box=box,
                    context_pdf_box=context,source_crop=name,source_crop_sha256=P.sha(blind/name),exact_crop=exact,
                    exact_crop_sha256=P.sha(blind/exact),source_orientation=0))
        countfolder=blind/'page-count-source';countfolder.mkdir()
        count_detections=[]
        for page in count_pages:
            _,count_rows,count_meta=L.process(doc,page)
            count_detections.append(dict(pdf_page=page,rows=count_rows,layout=count_meta))
            pix=doc[page-1].get_pixmap(matrix=P.fitz.Matrix(2,2),colorspace=P.fitz.csGRAY);pix.save(countfolder/f'pdf{page}.png')
    P.write(OUT/'count-page-detections.json',dict(status='Frozen evaluation',pages=count_detections))
    predictions.sort(key=lambda r:r['sample_index']);locators.sort(key=lambda r:r['sample_index'])
    P.write(OUT/'predictions.json',dict(status='Frozen evaluation',rows=predictions,freeze_sha256=P.sha(freeze_path)))
    P.write(blind/'selection.json',dict(status='Frozen evaluation',seed=2026100780,denominators=denominators,rows=locators,
       count_pages=count_pages,random_count_pages=sorted(set(count_pages)-{62,129,130}),stress_pages=[62,129,130]))
    P.write(OUT/'prediction-freeze.json',dict(status='Frozen evaluation',created_utc=now(),rows=80,
       prediction_sha256=P.sha(OUT/'predictions.json'),selection_sha256=P.sha(blind/'selection.json'),
       freeze_sha256=P.sha(freeze_path),reference_exists=False,source_count_pages=count_pages,
       count_detections_sha256=P.sha(OUT/'count-page-detections.json')))
    print(json.dumps(dict(prediction_frozen=True,rows=80,count_pages=count_pages,denominators=denominators)),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['freeze','sample']);args=parser.parse_args()
    if args.command=='freeze':freeze()
    else:sample()


if __name__=='__main__':main()
