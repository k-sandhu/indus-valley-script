"""CC BY 1979 Helsinki font digitization. Run from the repository root."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import random
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'
TMP = RAW / 'tmp'
TMP.mkdir(parents=True, exist_ok=True)
for key in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[key] = str(TMP)
import cv2
import numpy as np
import pymupdf as fitz
import torch
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from scipy.optimize import minimize

PDF = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'
CHART = ROOT / 'research/chart_reference/manual_numeric_reference.json'
SEED = 20261007
PARAM = dict(threshold=190, render_scale=2, canvas=48, max_unit_width=72,
             max_join_gap=19, segmentation_penalty=1.0, learned_weight=0.03,
             template_weight=1.0, confidence_temperature=1.0, review_score=0.75,
             development_pages=[20, 21, 22, 25, 30, 100], evaluation_pages=[31, 79])
AUXILIARY_CODES={70:'editorial_entire_text_lost',13:'editorial_unbounded_end_damage',
                 597:'editorial_unbounded_end_damage',106:'editorial_hatched_damage_or_inaccessible_span',
                 599:'editorial_hatched_damage_or_inaccessible_span'}
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
torch.set_num_threads(4)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def render(doc, page, scale=2):
    pix = doc[page - 1].get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()


def runs(active, max_gap=0):
    ids = np.flatnonzero(active)
    if not len(ids):
        return []
    blocks = np.split(ids, np.flatnonzero(np.diff(ids) > max_gap + 1) + 1)
    return [(int(b[0]), int(b[-1] + 1)) for b in blocks]


def tight(b):
    ys, xs = np.where(b)
    return b[ys.min():ys.max()+1, xs.min():xs.max()+1] if len(xs) else np.zeros((1, 1), bool)


def canvas(b, size=48):
    b = tight(b)
    h, w = b.shape
    ratio = min((size - 8) / h, (size - 8) / w, 1.5)
    hh, ww = max(1, round(h * ratio)), max(1, round(w * ratio))
    body = cv2.resize(b.astype('float32'), (ww, hh), interpolation=cv2.INTER_AREA)
    a = np.zeros((size, size), np.float32)
    y, x = (size-hh)//2, (size-ww)//2
    a[y:y+hh, x:x+ww] = body
    return a


def shape_canvas(b):
    b=tight(b); h,w=b.shape
    a=np.zeros((64,96),bool)
    h=min(h,56);w=min(w,88)
    a[(64-h)//2:(64-h)//2+h,(96-w)//2:(96-w)//2+w]=b[:h,:w]
    return a


def templates():
    labels = json.loads(CHART.read_text(encoding='utf-8'))
    with fitz.open(PDF) as doc:
        pages = {p: render(doc, p) for p in (20, 21)}
    result = []
    for row in labels['rows']:
        p, c, r = row['pdf_page'], row['column'], row['row']
        x = (176 if p == 20 else 153) + 100.4*c
        y = 152.6 + 40.1*r
        xy = [round(x-20), round(y-19.5), round(x+31), round(y+19.5)]
        b = tight(pages[p][xy[1]:xy[3], xy[0]:xy[2]] < PARAM['threshold'])
        codes = sorted(set([row['code']] + row['alternatives']))
        result.append(dict(key=f'{p}:{c}:{r}', codes=codes, rank=row['rank'],
                           rank_candidates=sorted(set([row['rank']]+row.get('rank_alternatives', []))),
                           dashed_auxiliary=row['dashed_auxiliary'], binary=b,
                           width=int(b.shape[1]), height=int(b.shape[0]), crop_xyxy_2x=xy,
                           chart_code_confidence=row['numeric_confidence']))
    return result


def make_chart_sheets(lib, out):
    out.mkdir(parents=True, exist_ok=True)
    for start in range(0, len(lib), 80):
        sheet = Image.new('RGB', (1200, 1000), 'white')
        draw = ImageDraw.Draw(sheet)
        for j, t in enumerate(lib[start:start+80]):
            x, y = (j % 10)*120, (j//10)*125
            im = Image.fromarray(np.where(t['binary'], 0, 255).astype('uint8'))
            im = im.resize((im.width*2, im.height*2))
            sheet.paste(im, (x+(120-im.width)//2, y+12))
            draw.text((x+3, y+94), '/'.join(map(str, t['codes'])), fill='black')
            draw.text((x+3, y+108), t['key']+' rank '+str(t['rank']), fill='black')
        sheet.save(out / f'chart_{start:03d}.png', optimize=True)


def layout_orientation(gray, side):
    """Observed margin ink groups anchor rows; no row pitch extrapolation."""
    h, w = gray.shape
    regions = []
    score = 0
    for c in range(2):
        base = c*0.443*w
        if side == 'right':
            n0, n1 = round(base+0.429*w), round(base+0.470*w)
            gx0, gx1 = round(base+0.060*w), n0-3
        else:
            n0, n1 = round(base+0.095*w), round(base+0.142*w)
            gx0, gx1 = n1+3, round(base+0.440*w)
        y0, y1 = round(h*.073), round(h*.933)
        patch = gray[y0:y1, n0:n1] < PARAM['threshold']
        bands = [(a+y0,b+y0) for a,b in runs(patch.sum(1)>=2, max_gap=5) if 9<=b-a<=29]
        # A two-line field normally has 16-24 pixels of ink at 2x.
        score += sum(1 for a,b in bands if 15<=b-a<=25)
        centers = [(a+b)/2 - 7 for a,b in bands]
        # Pick a blank gap near each halfway boundary, preserving target ink.
        ink = (gray[y0:y1, gx0:gx1] < PARAM['threshold']).sum(1)
        observed=[(a+y0,b+y0) for a,b in runs(ink>=2,max_gap=3) if b-a>=8]
        extras=[(a+b)/2 for a,b in observed if centers and min(abs((a+b)/2-z) for z in centers)>21]
        for center in extras:
            bands.append((round(center+4),round(center+16)))
            centers.append(center)
        ordered=sorted(zip(centers,bands));centers=[z for z,_ in ordered];bands=[b for _,b in ordered]
        blanks = [(a+y0,b+y0) for a,b in runs(ink<2) if b-a>=2]
        edges = [y0]
        for previous, following in zip(centers, centers[1:]):
            mid = (previous+following)/2
            eligible = [(a+b)/2 for a,b in blanks if previous+7<(a+b)/2<following-7]
            edges.append(round(min(eligible, key=lambda z:abs(z-mid))) if eligible else round(mid))
        edges.append(y1)
        rows = []
        for i, ((a,b), center) in enumerate(zip(bands, centers)):
            low, high = edges[i], edges[i+1]
            # Expand first/last boundaries only to the page body, never by pitch.
            rows.append(dict(pdf_column=c, row_index=i, margin_xyxy_2x=[n0,a-2,n1,b+2],
                             glyph_xyxy_2x=[gx0,low,gx1,high], row_anchor_y_2x=center,
                             flags=(['possible_continuation_without_margin'] if center in extras else [])+
                                   ([] if len(centers)>10 else ['few_margin_anchors'])))
        regions.extend(rows)
    return score, regions


def detect_layout(gray):
    candidates = []
    for rotation in (0, 180):
        a = gray if rotation==0 else gray[::-1, ::-1].copy()
        for side in ('right','left'):
            score, rows = layout_orientation(a, side)
            candidates.append((score, rotation, side, rows, a))
    score, rotation, side, rows, a = max(candidates, key=lambda x:x[0])
    return a, rows, dict(rotation=rotation, margin_side=side, anchor_score=score,
                        competing_scores=[dict(score=x[0],rotation=x[1],side=x[2]) for x in candidates])


def ocr_lines(gray, row_records):
    """Batch margin fields in one subprocess; glyph OCR is never a token source."""
    width, slot = 380, 160
    sheet = Image.new('L', (width, slot*len(row_records)), 255)
    fields = []
    for i, row in enumerate(row_records):
        x0,y0,x1,y1 = row['margin_xyxy_2x']
        patch = gray[y0:y1,x0:x1]
        b = patch < PARAM['threshold']
        bands = [(a,z) for a,z in runs(b.sum(1)>=2, max_gap=1) if z-a>=4]
        # Keep upper identification and lower classification lines separate.
        if len(bands)>=2:
            split = round((bands[0][1]+bands[1][0])/2)
        else:
            split = patch.shape[0]//2
        for j,(a,z) in enumerate(((0,split),(split,len(patch)))):
            im = Image.fromarray(patch[a:z]).resize(((x1-x0)*5, max(1,(z-a)*5)))
            sheet.paste(im,(25,i*slot+j*80+8))
        fields.append((split,bands))
    path = TMP/'margin_batch.png'
    sheet.save(path)
    proc = subprocess.run(['tesseract',str(path),'stdout','--psm','6','-l','eng',
                           '-c','tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ','tsv'],
                          capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
    lookup = {}
    for item in csv.DictReader(io.StringIO(proc.stdout), delimiter='\t'):
        value = item.get('text','').strip()
        if not value:
            continue
        center = int(item['top'])+int(item['height'])/2
        idx = int(center//slot)
        line = int(center%slot//80)
        if idx<len(row_records):
            lookup.setdefault((idx,line), []).append((int(item['left']),value,float(item['conf'])))
    for i,row in enumerate(row_records):
        values = []
        for j in range(2):
            items = sorted(lookup.get((i,j),[]))
            values.append(dict(text=''.join(t for _,t,_ in items),
                               confidence=min((c for _,_,c in items),default=-1),
                               words=[dict(x=x,text=t,confidence=c) for x,t,c in items]))
        upper,lower = values
        row['inscription_number'] = upper['text'] if re.fullmatch(r'\d{1,4}[A-Z]?', upper['text']) else None
        row['classification_ocr_compact'] = lower['text']
        row['classification_code'] = None  # Positional blanks need a separate geometric check.
        row['margin_ocr'] = values
        if (HERE/'development/digits.npz').exists():
            x0,y0,x1,y1=row['margin_xyxy_2x']; patch=gray[y0:y1,x0:x1]
            split,_=fields[i]
            row['digit_classifier']=read_digits(patch[:split])
            digits=row['digit_classifier']['text']
            # Retain printed OCR suffixes only when both methods agree on digits.
            suffix=re.sub(r'^\d+','',upper['text']) if upper['text'].startswith(digits) else ''
            if digits and len(digits)<=4:
                row['inscription_number']=digits+suffix
            lower_digits=read_digits(patch[split:])
            row['classification_digit_classifier']=lower_digits
            literal=lower_digits['text']
            if len(literal)==4:
                row['classification_code']=literal[:2]+' '+literal[2:]
                row['flags'].append('classification_blank_position_inferred')
            elif len(literal)==5:
                row['classification_code']=literal
        if row['inscription_number'] is None:
            row['flags'].append('number_unreadable_or_continuation')
        if upper['confidence'] < 80:
            row['flags'].append('number_low_ocr_confidence')
        row['flags'].append('classification_positions_unverified')
        if 'possible_continuation_without_margin' in row['flags']:
            row['inscription_number']=None;row['classification_code']=None
    return row_records


def digit_images(patch):
    b=patch<PARAM['threshold']; bands=runs(b.any(0))
    return [(a,z,tight(b[:,a:z])) for a,z in bands if b[:,a:z].sum()>=3]


def build_digits(gray,rows):
    images=[];labels=[];origins=[]
    for row in rows:
        literal=str((1015 if row['pdf_column']==0 else 1051)+row['row_index'])
        x0,y0,x1,y1=row['margin_xyxy_2x']; patch=gray[y0:y1,x0:x1]
        bands=[(a,z) for a,z in runs((patch<PARAM['threshold']).sum(1)>=2,max_gap=1) if z-a>=4]
        if len(bands)<2:continue
        split=round((bands[0][1]+bands[1][0])/2)
        chars=digit_images(patch[:split])
        if len(chars)!=len(literal):continue
        for (a,z,b),char in zip(chars,literal):
            images.append(cv2.resize(b.astype('float32'),(16,20),interpolation=cv2.INTER_AREA));labels.append(int(char))
            origins.append(dict(column=row['pdf_column'],row=row['row_index'],digit=char))
    np.savez_compressed(HERE/'development/digits.npz',images=np.stack(images),labels=np.array(labels))
    write(HERE/'development/digits.json',dict(status='Exploratory',source='Known sequential page30 numbers 1015..1086',
          examples=len(images),counts=dict(Counter(labels)),origins=origins))


def read_digits(patch):
    data=np.load(HERE/'development/digits.npz'); library=data['images'];labels=data['labels']; chars=[]
    for a,z,b in digit_images(patch):
        image=cv2.resize(b.astype('float32'),(16,20),interpolation=cv2.INTER_AREA)
        distance=((library-image)**2).mean((1,2)); costs=np.array([distance[labels==d].min() for d in range(10)])
        order=np.argsort(costs); chars.append(dict(character=str(order[0]),x=[a,z],
            candidates=[dict(character=str(d),mse=float(costs[d])) for d in order[:3]]))
    return dict(text=''.join(c['character'] for c in chars),characters=chars,status='uncalibrated_digit_template_classifier')


class Net(torch.nn.Module):
    def __init__(self, classes):
        super().__init__()
        self.encoder=torch.nn.Sequential(torch.nn.Conv2d(1,24,5,padding=2),torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),torch.nn.Conv2d(24,48,3,padding=1),torch.nn.ReLU(),
            torch.nn.MaxPool2d(2),torch.nn.Conv2d(48,64,3,padding=1),torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d((4,4)),torch.nn.Flatten(),torch.nn.Linear(1024,128),torch.nn.ReLU())
        self.head=torch.nn.Linear(128,classes)
    def forward(self,x):
        return self.head(self.encoder(x))


def train(lib, destination):
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    if DEVICE=='cuda': torch.cuda.manual_seed_all(SEED)
    base=torch.tensor(np.stack([canvas(t['binary']) for t in lib])[:,None],device=DEVICE)
    model=Net(len(lib)).to(DEVICE); optim=torch.optim.Adam(model.parameters(),lr=.002)
    rng=np.random.default_rng(SEED); history=[]; start=time.monotonic()
    for epoch in range(36):
        losses=[]
        for step in range(16):
            ids=torch.tensor(rng.integers(0,len(lib),256),device=DEVICE)
            x=base[ids]
            angles=torch.tensor(rng.uniform(-.07,.07,256),device=DEVICE,dtype=torch.float32)
            scale=torch.tensor(rng.uniform(.90,1.12,256),device=DEVICE,dtype=torch.float32)
            theta=torch.zeros((256,2,3),device=DEVICE)
            theta[:,0,0]=torch.cos(angles)*scale; theta[:,1,1]=torch.cos(angles)*scale
            theta[:,0,1]=-torch.sin(angles)*scale; theta[:,1,0]=torch.sin(angles)*scale
            theta[:,:,2]=torch.tensor(rng.uniform(-.06,.06,(256,2)),device=DEVICE,dtype=torch.float32)
            grid=torch.nn.functional.affine_grid(theta,x.shape,align_corners=False)
            x=torch.nn.functional.grid_sample(x,grid,align_corners=False)
            if step%4==0: x=torch.nn.functional.max_pool2d(x,3,stride=1,padding=1)
            if step%4==1: x=-torch.nn.functional.max_pool2d(-x,3,stride=1,padding=1)
            x=(x+torch.randn_like(x)*.035).clamp(0,1)
            logits=model(x); loss=torch.nn.functional.cross_entropy(logits,ids)
            optim.zero_grad(); loss.backward(); optim.step(); losses.append(loss.item())
        history.append(dict(epoch=epoch,loss=float(np.mean(losses))))
        if epoch%6==0: print(json.dumps(history[-1]),flush=True)
    model.eval(); torch.save(model.state_dict(),destination)
    write(HERE/'development/training.json',dict(status='Synthetic',device=DEVICE,epochs=36,
              examples=36*16*256,history=history,seconds=time.monotonic()-start,
              augmentation='affine scale/translation/rotation, max/min stroke-width, Gaussian noise'))


class Recognizer:
    def __init__(self,lib,model_path):
        self.lib=lib; self.model=Net(len(lib)).to(DEVICE)
        self.model.load_state_dict(torch.load(model_path,map_location=DEVICE,weights_only=True)); self.model.eval()
        self.base=np.stack([shape_canvas(t['binary']) for t in lib])
        # Euclidean distance fields preserve aspect ratio on the shared canvas.
        self.dt=np.stack([distance_transform_edt(~a) for a in self.base]).astype('float32')
        self.ink=self.base
        self.dt_flat=self.dt.reshape(len(lib),-1)
        positions=[np.flatnonzero(a.ravel()) for a in self.base]
        maximum=max(len(x) for x in positions)
        self.points=np.zeros((len(lib),maximum),np.int32);self.point_weights=np.zeros((len(lib),maximum),np.float32)
        for i,pos in enumerate(positions):
            self.points[i,:len(pos)]=pos;self.point_weights[i,:len(pos)]=1/max(1,len(pos))
        self.widths=np.array([t['width'] for t in lib]); self.heights=np.array([t['height'] for t in lib])
        self.cache={}
        calibration_path=HERE/'development/calibration.json'
        self.calibration=json.loads(calibration_path.read_text()) if calibration_path.exists() else None

    def alternatives(self, binary):
        b=tight(binary); key=(b.shape,b.tobytes())
        if key in self.cache:return self.cache[key]
        a=shape_canvas(b); ink=a; dt=distance_transform_edt(~ink)
        valid=np.flatnonzero(np.abs(self.widths-b.shape[1])<=np.maximum(4,.25*self.widths))
        if not len(valid):valid=np.arange(len(self.lib))
        chamfer=np.full(len(self.lib),100.,np.float32)
        best=np.full(len(valid),100.,np.float32)
        for dy in (-3,0,3):
            for dx in (-2,0,2):
                shifted=np.roll(ink,(dy,dx),(0,1)); shifted_dt=np.roll(dt,(dy,dx),(0,1))
                qpoints=np.flatnonzero(shifted.ravel())
                distances=(self.dt_flat[np.ix_(valid,qpoints)].mean(1)+
                    (shifted_dt.ravel()[self.points[valid]]*self.point_weights[valid]).sum(1))/2
                best=np.minimum(best,distances)
        chamfer[valid]=best+.035*np.abs(self.widths[valid]-b.shape[1])
        network_canvas=canvas(b)
        with torch.inference_mode():
            logp=torch.log_softmax(self.model(torch.tensor(network_canvas[None,None],device=DEVICE)),1)[0].cpu().numpy()
        score=chamfer-PARAM['learned_weight']*logp
        order=np.argsort(score,kind='stable')[:5]
        mass=np.exp(-(score-score.min())/PARAM['confidence_temperature']); mass/=mass.sum()
        result=[]
        for idx in order:
            t=self.lib[int(idx)]
            result.append(dict(template_key=t['key'],codes=t['codes'],ranks=t['rank_candidates'],
                               dashed_auxiliary=t['dashed_auxiliary'],distance=float(chamfer[idx]),
                               combined_cost=float(score[idx]),synthetic_softmax_score=float(mass[idx])))
        self.cache[key]=result
        if len(self.cache)>25000: self.cache.clear()
        return result

    def segment(self,gray):
        b=gray<PARAM['threshold']
        comps=runs(b.sum(0)>=2)
        # Do not create units for isolated scan specks.
        comps=[(a,z) for a,z in comps if int(b[:,a:z].sum())>=3]
        n=len(comps); cost=[float('inf')]*(n+1); paths=[None]*(n+1); cost[0]=0; paths[0]=[]
        for i in range(n):
            for j in range(i,min(n,i+12)):
                x0,x1=comps[i][0],comps[j][1]
                if x1-x0>PARAM['max_unit_width']: break
                if j>i and comps[j][0]-comps[j-1][1]>PARAM['max_join_gap']:break
                body=b[:,x0:x1]; alternatives=self.alternatives(body)
                value=alternatives[0]['combined_cost']*body.sum()/100+PARAM['segmentation_penalty']
                if cost[i]+value<cost[j+1]:
                    ys=np.flatnonzero(body.any(1))
                    cost[j+1]=cost[i]+value
                    confidence=None
                    if self.calibration:
                        features=np.array([1.,alternatives[0]['combined_cost'],alternatives[1]['combined_cost']-alternatives[0]['combined_cost']])
                        confidence=float(1/(1+np.exp(-np.clip(features@np.array(self.calibration['coefficients']),-30,30))))
                    paths[j+1]=paths[i]+[dict(x_bounds=[x0,x1],y_bounds=[int(ys[0]),int(ys[-1]+1)],
                         alternatives=alternatives,confidence=confidence,confidence_status='development_logistic' if confidence is not None else 'uncalibrated_shape_score',
                         top_one_score=alternatives[0]['synthetic_softmax_score'],unit_kind='glyph_or_auxiliary_unverified')]
            if cost[i]+30<cost[i+1]:
                cost[i+1]=cost[i]+30; paths[i+1]=paths[i]+[dict(x_bounds=list(comps[i]),alternatives=[],
                     confidence=None,confidence_status='unmatched',unit_kind='unmatched_ink',top_one_score=0)]
        return paths[-1] or [],cost[-1]


def process_page(doc,page,recognizer=None,ocr=True):
    gray=render(doc,page); gray,rows,meta=detect_layout(gray)
    if ocr and rows:rows=ocr_lines(gray,rows)
    text=doc[page-1].get_text()
    for row in rows:
        row.update(occurrence_key=f'helsinki1979:pdf{page}:c{row["pdf_column"]}:r{row["row_index"]}',
                   edition='Koskenniemi-Parpola-1979',pdf_page=page,
                   page_rotation=meta['rotation'],margin_side=meta['margin_side'],
                   serialization='visual_left_to_right',physical_line_side_boundaries='unresolved')
        x0,y0,x1,y1=row['glyph_xyxy_2x']; strip=gray[y0:y1,x0:x1]
        if recognizer:
            row['units'],row['segmentation_cost']=recognizer.segment(strip)
            row['boundary_blanks']=[dict(after_unit=i,gap_pixels_2x=b['x_bounds'][0]-a['x_bounds'][1],
                 interpretation='possible_original_boundary_or_loss') for i,(a,b) in enumerate(zip(row['units'],row['units'][1:]))
                 if b['x_bounds'][0]-a['x_bounds'][1]>20]
            row['auxiliaries']=[dict(unit_index=i,kind='possible_uncertainty_underline') for i,u in enumerate(row['units'])
                               if u['alternatives'] and u['alternatives'][0]['dashed_auxiliary']]
            for i,u in enumerate(row['units']):
                if not u['alternatives']:continue
                codes=u['alternatives'][0]['codes']
                kinds={AUXILIARY_CODES[c] for c in codes if c in AUXILIARY_CODES}
                if kinds:
                    u['unit_kind']='auxiliary_candidate'
                    u['auxiliary_candidates']=sorted(kinds)
                    u['original_glyph_count']=None
                    row['auxiliaries'].append(dict(unit_index=i,kind_candidates=sorted(kinds),
                        interpretation_status='predicted_editorial_graphic',original_glyph_count=None))
            if any(u['top_one_score']<PARAM['review_score'] for u in row['units']):row['flags'].append('glyph_review')
        row['glyph_pdf_box']=oriented_to_pdf(row['glyph_xyxy_2x'], gray.shape, meta['rotation'])
        # OCR witness retained only locally, with no glyph token interpretation.
        row['ocr_number_witnesses']=[w[4] for w in doc[page-1].get_text('words') if
            row['margin_xyxy_2x'][0]/2-3<=w[0]<=row['margin_xyxy_2x'][2]/2+3 and
            row['margin_xyxy_2x'][1]/2-2<=w[1]<=row['margin_xyxy_2x'][3]/2+2] if not meta['rotation'] else []
    return gray,rows,meta


def oriented_to_pdf(box,shape,rotation):
    x0,y0,x1,y1=box
    if rotation:
        h,w=shape; x0,x1=w-x1,w-x0; y0,y1=h-y1,h-y0
    return [v/2 for v in [x0,y0,x1,y1]]


def development():
    destination=HERE/'development'; destination.mkdir(exist_ok=True)
    lib=templates(); make_chart_sheets(lib,HERE/'blind/chart_sheets')
    write(destination/'templates.json',[{k:v for k,v in t.items() if k!='binary'} for t in lib])
    if not (destination/'classifier.pt').exists():train(lib,destination/'classifier.pt')
    rec=Recognizer(lib,destination/'classifier.pt')
    with fitz.open(PDF) as doc:
        rawgray=render(doc,30);rawgray,rawrows,_=detect_layout(rawgray);build_digits(rawgray,rawrows)
        gray,rows,meta=process_page(doc,30,rec)
    write(destination/'page30_predictions.json',dict(layout=meta,rows=rows,parameters=PARAM))
    reference=json.loads((ROOT/'research/corpus/primary/font_fresh20/manual_reference.json').read_text(encoding='utf-8'))
    scores=[]; calibration_x=[];calibration_y=[]
    for ref in reference['rows']:
        row=next((r for r in rows if r['pdf_column']==ref['col_0based'] and r['row_index']==ref['row_0based']),None)
        if row is None:continue
        true=[set(t['strict_candidate_codes']) for t in ref['units']]
        item=dict(id=ref['printed_inscription_id'],reference_count=len(true),prediction_count=len(row['units']),
                  printed_number_ocr=row['inscription_number'])
        for k in (1,5):
            guesses=[set(c for a in t['alternatives'][:k] for c in a['codes']) for t in row['units']]
            item[f'top{k}_edits']=edit(guesses,true)
        if len(true)==len(row['units']):
            for u,t in zip(row['units'],true):
                if len(u['alternatives'])<2:continue
                a=u['alternatives'];calibration_x.append([1,a[0]['combined_cost'],a[1]['combined_cost']-a[0]['combined_cost']])
                calibration_y.append(float(bool(set(a[0]['codes'])&t)))
        scores.append(item)
    write(destination/'page30_evaluation.json',dict(status='Exploratory',rows=scores,
          correct_counts=sum(r['reference_count']==r['prediction_count'] for r in scores),
          top1_rows=sum(r['top1_edits']==0 for r in scores),top5_rows=sum(r['top5_edits']==0 for r in scores)))
    x=np.array(calibration_x);y=np.array(calibration_y)
    def loss(beta):
        z=x@beta
        return float(np.sum(np.logaddexp(0,z)-y*z)+.5*np.sum(beta[1:]**2))
    fitted=minimize(loss,np.zeros(3),method='BFGS')
    write(destination/'calibration.json',dict(status='Exploratory',coefficients=fitted.x.tolist(),
          target='candidate-set-compatible top-one template on equal-count development rows',examples=len(y),correct=int(y.sum()),
          fit_success=bool(fitted.success),penalty='L2=1 on nonintercept coefficients',
          limitations='Development fit; no claim of calibrated fresh-corpus confidence until reserved evaluation'))
    print(json.dumps(dict(layout=meta,rows=len(rows),scores=scores)),flush=True)


def edit(guess,truth):
    dp=list(range(len(truth)+1))
    for i,a in enumerate(guess,1):
        current=[i]
        for j,b in enumerate(truth,1):
            current.append(min(current[-1]+1,dp[j]+1,dp[j-1]+(0 if a&b else 1)))
        dp=current
    return dp[-1]


def freeze():
    if (HERE/'freeze-manifest.json').exists():raise FileExistsError('Frozen manifest already exists')
    (HERE/'chart-snapshot.json').write_bytes(CHART.read_bytes())
    manifest=dict(status='Frozen evaluation',created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        source_sha256=sha(PDF),chart_sha256=sha(HERE/'chart-snapshot.json'),code_sha256=sha(__file__),
        model_sha256=sha(HERE/'development/classifier.pt'),parameters=PARAM,seed=SEED,
        digit_classifier_sha256=sha(HERE/'development/digits.npz'),calibration_sha256=sha(HERE/'development/calibration.json'),
        python=sys.version,platform=platform.platform(),device=DEVICE,
        versions=dict(torch=torch.__version__,opencv=cv2.__version__,numpy=np.__version__,pymupdf=fitz.VersionBind),
        calibration='logistic candidate-set correctness fitted on equal-count page30 development rows',
        reference_exists=False,development_reference_sha256=sha(ROOT/'research/corpus/primary/font_fresh20/manual_reference.json'))
    write(HERE/'freeze-manifest.json',manifest)


def check_freeze():
    m=json.loads((HERE/'freeze-manifest.json').read_text())
    assert sha(PDF)==m['source_sha256']
    assert sha(__file__)==m['code_sha256']
    assert sha(HERE/'chart-snapshot.json')==m['chart_sha256']==sha(CHART)
    assert sha(HERE/'development/classifier.pt')==m['model_sha256']
    assert sha(HERE/'development/digits.npz')==m['digit_classifier_sha256']
    assert sha(HERE/'development/calibration.json')==m['calibration_sha256']
    assert PARAM==m['parameters']
    return m


def sample():
    check_freeze(); blind=HERE/'blind'; blind.mkdir(exist_ok=True)
    if (blind/'selection.json').exists():raise FileExistsError('Selection already exists')
    frame=[]
    with fitz.open(PDF) as doc:
        for page in range(PARAM['evaluation_pages'][0],PARAM['evaluation_pages'][1]+1):
            _,rows,meta=process_page(doc,page,ocr=False)
            frame.extend(rows)
        chosen=sorted(random.Random(SEED).sample(frame,60),key=lambda r:(r['pdf_page'],r['pdf_column'],r['row_index']))
        for index,row in enumerate(chosen):
            page=doc[row['pdf_page']-1]; x0,y0,x1,y1=row['glyph_pdf_box']
            nx0,ny0,nx1,ny1=oriented_to_pdf(row['margin_xyxy_2x'],
                (round(page.rect.height*2),round(page.rect.width*2)),row['page_rotation'])
            box=fitz.Rect(min(x0,nx0)-5,max(55,min(y0,ny0)-14),max(x1,nx1)+5,min(page.rect.height*.95,max(y1,ny1)+14))
            pix=page.get_pixmap(matrix=fitz.Matrix(5,5),clip=box,colorspace=fitz.csGRAY)
            im=Image.frombytes('L',(pix.width,pix.height),pix.samples)
            if row['page_rotation']:im=im.rotate(180)
            name=f'row_{index:02d}_p{row["pdf_page"]}_c{row["pdf_column"]}_r{row["row_index"]}.png'
            im.save(blind/name,optimize=True)
            row.update(sample_index=index,source_crop=name,source_crop_sha256=sha(blind/name),context_pdf_box=list(box))
    write(blind/'selection.json',dict(seed=SEED,frame_rows=len(frame),selection_count=60,
         frozen_manifest_sha256=sha(HERE/'freeze-manifest.json'),method='random.Random.sample without replacement then coordinate sort',
         rows=chosen))
    rec=Recognizer(templates(),HERE/'development/classifier.pt'); selected=[]
    with fitz.open(PDF) as doc:
        for page in sorted(set(r['pdf_page'] for r in chosen)):
            gray,rows,meta=process_page(doc,page,rec)
            for r in chosen:
                if r['pdf_page']!=page:continue
                pred=next(t for t in rows if t['pdf_column']==r['pdf_column'] and t['row_index']==r['row_index'])
                pred['sample_index']=r['sample_index']; selected.append(pred)
    selected.sort(key=lambda r:r['sample_index'])
    path=RAW/'frozen-evaluation-predictions.json'
    write(path,dict(status='Frozen evaluation',rows=selected,freeze_sha256=sha(HERE/'freeze-manifest.json')))
    write(HERE/'prediction-freeze.json',dict(created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
         predictions_path=str(path.relative_to(ROOT)),predictions_sha256=sha(path),
         selection_sha256=sha(blind/'selection.json'),rows=len(selected),reference_exists=False))
    print(json.dumps(dict(frame_rows=len(frame),selected=len(selected),predictions_sha256=sha(path))),flush=True)


def full(out):
    check_freeze(); out=Path(out)
    if out.exists():raise FileExistsError('Use a new run directory')
    out.mkdir(parents=True); cropdir=RAW/out.name/'row-crops'; cropdir.mkdir(parents=True)
    rec=Recognizer(templates(),HERE/'development/classifier.pt'); counts=Counter(); pages=[]; queue=[]; start=time.monotonic();pdf_sha=sha(PDF)
    with fitz.open(PDF) as doc, (out/'occurrences.jsonl').open('w',encoding='utf-8') as stream:
        for page in range(22,181):
            gray,rows,meta=process_page(doc,page,rec)
            for row in rows:
                x0,y0,x1,y1=row['glyph_xyxy_2x']; crop=Image.fromarray(gray[y0:y1,x0:x1])
                name=row['occurrence_key'].replace(':','_')+'.png'; crop.save(cropdir/name,optimize=True)
                row['review_crop_local']=str((cropdir/name).relative_to(ROOT))
                row['source_sha256']=pdf_sha
                row['licence']='CC BY 4.0';row['status']='Exploratory'
                if row['flags']: queue.append(dict(occurrence_key=row['occurrence_key'],inscription_number=row['inscription_number'],
                    pdf_page=page,flags=row['flags'],review_crop_local=row['review_crop_local']))
                stream.write(json.dumps(row,ensure_ascii=False)+'\n')
                counts['printed_rows']+=1; counts['drawn_unit_candidates']+=len(row['units'])
                counts['numbers_read']+=int(row['inscription_number'] is not None)
                counts['review_rows']+=bool(row['flags']); counts['unmatched_units']+=sum(not u['alternatives'] for u in row['units'])
            pages.append(dict(pdf_page=page,rows=len(rows),layout=meta,source_sha256=pdf_sha))
            print(json.dumps(dict(page=page,rows=len(rows),elapsed_seconds=round(time.monotonic()-start,1))),flush=True)
    with (out/'review-queue.jsonl').open('w',encoding='utf-8') as stream:
        for row in queue: stream.write(json.dumps(row)+'\n')
    write(out/'coverage.json',dict(status='Exploratory',counts=dict(counts),pages=pages,seconds=time.monotonic()-start,
                                 occurrence_file_sha256=sha(out/'occurrences.jsonl'),freeze_sha256=sha(HERE/'freeze-manifest.json')))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['develop','freeze','sample','full'])
    ap.add_argument('--out',default=str(HERE/'runs/2026-10-07-full-v1'));args=ap.parse_args()
    if args.command=='develop':development()
    elif args.command=='freeze':freeze()
    elif args.command=='sample':sample()
    elif args.command=='full':full(args.out)


if __name__=='__main__':main()
