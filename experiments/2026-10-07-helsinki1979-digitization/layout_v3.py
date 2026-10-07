"""Exploratory layout repair, with the unchanged frozen recognizer."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import time
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
import pipeline as P

HERE=P.HERE
PARAM=dict(ocr_cluster_sigma_pt=6,minimum_peak_distance_pt=38,minimum_ocr_support=5,
           ocr_cluster_halfwidth_pt=20,field_edge_padding_pt=0.5,
           field_ink_gap_pixels=5,minimum_field_band_pixels=5,maximum_field_band_pixels=30,
           page_body_fraction=[0.073,0.933],orientation='source_header_content',
           number_edge_clearance_pt=0.8,recognizer='unchanged first-endpoint weights/templates/calibration')
PARAM.update(print_column_gap_pixels=16,print_column_minimum_ink=4000,
             print_column_maximum_width_pixels=170,ocr_batch_rows=96)


def orientation(page):
    words=page.get_text('words');height=page.rect.height
    headers=[w for w in words if 'CORPUS' in w[4].upper() and w[1]<height*.15]
    if headers:return dict(rotation=0,resolved=True,evidence='CORPUS header near page top',header_boxes=[list(w[:4]) for w in headers])
    # A missing header is a review condition; row-density comparisons never rotate.
    return dict(rotation=0,resolved=False,evidence='No readable source header; upright hypothesis requires review',header_boxes=[])


def fields(page,gray):
    width,height=page.rect.width,page.rect.height
    side='left' if 79<=page.number+1<=130 else 'right'
    ink=(gray[round(gray.shape[0]*.073):round(gray.shape[0]*.933)]<190).sum(0)
    blocks=[(a,b) for a,b in P.runs(ink>=5,max_gap=16) if b-a>=15 and ink[a:b].sum()>=4000]
    if side=='left' and len(blocks)>2 and all(b-a<170 for a,b in blocks):
        columns=[];observed=[]
        for a,b in blocks:
            gaps=[(s,t) for s,t in P.runs(ink[a:b]<5) if t-s>=2 and .25*(b-a)<s<.75*(b-a)]
            if gaps:
                s,t=min(gaps,key=lambda st:abs(sum(st)/2-(b-a)*.55));observed.append(s)
        for a,b in blocks:
            gaps=[(s,t) for s,t in P.runs(ink[a:b]<5) if t-s>=2 and .25*(b-a)<s<.75*(b-a)]
            if gaps:s,t=min(gaps,key=lambda st:abs(sum(st)/2-(b-a)*.55))
            else:s=int(np.median(observed)) if observed else round((b-a)*.55)
            columns.append(dict(center=(a+a+s)/4,left=a/2-.25,right=(a+s)/2+.25,
                                ocr_support=0,method='print-column projection and internal field/glyph gap',gap_inferred=not bool(gaps)))
        if len(columns)>2:return columns,side
    words=[w for w in page.get_text('words') if height*.073<w[1]<height*.933
           and re.fullmatch(r'[0-9]{1,4}[A-Z]?',w[4]) and 1<=w[3]-w[1]<=14 and w[2]-w[0]<=30]
    # Deduplicate overlapping OCR alternatives without trusting their literal numbers.
    unique={tuple(round(float(v)/2) for v in (w[0],w[1],w[2],w[3])):w for w in words}
    words=list(unique.values());hist=np.zeros(round(width)+1)
    for w in words:hist[round((w[0]+w[2])/2)]+=1
    smooth=gaussian_filter1d(hist,PARAM['ocr_cluster_sigma_pt'])
    peaks,_=find_peaks(smooth,distance=PARAM['minimum_peak_distance_pt'],prominence=max(.07,float(smooth.max())*.13))
    result=[]
    for peak in peaks:
        near=[w for w in words if abs((w[0]+w[2])/2-peak)<=PARAM['ocr_cluster_halfwidth_pt']]
        support=len({round(w[1]/8) for w in near})
        if support<PARAM['minimum_ocr_support']:continue
        left=float(np.quantile([w[0] for w in near],.10))-.5
        right=float(np.quantile([w[2] for w in near],.90))+.5
        result.append(dict(center=float(peak),left=left,right=right,ocr_support=support,method='OCR coordinate cluster'))
    result.sort(key=lambda r:r['center'])
    # Ordinary page types have two broad text columns. Row counts remain unconstrained.
    expected=[(c*.443+(.1185 if side=='left' else .4495))*width for c in range(2)]
    result=[min([r for r in result if abs(r['center']-x)<35],key=lambda r:abs(r['center']-x))
            for x in expected if any(abs(r['center']-x)<35 for r in result)]
    # The broad side is supplied by the source's section/header, not an ink-density orientation score.
    if len(result)<2:
        # Explicit source-specific fallback, flagged; median parity drift came from the review.
        shift=7.4 if (page.number+1)%2==0 else -3.2
        result=[]
        for c in range(2):
            base=c*.443*width
            left=base+(.095 if side=='left' else .429)*width+shift
            right=left+(.047 if side=='left' else .041)*width
            result.append(dict(center=(left+right)/2,left=left,right=right,ocr_support=0,method='review parity prior fallback'))
    return result,side


def process(doc,number,rec=None):
    page=doc[number-1];gray=P.render(doc,number);h,w=gray.shape
    fs,side=fields(page,gray);orient=orientation(page);rows=[]
    y0,y1=round(h*.073),round(h*.933)
    for column,field in enumerate(fs):
        n0,n1=round(field['left']*2),round(field['right']*2)
        previous=fs[column-1]['right'] if column else 25
        following=fs[column+1]['left'] if column+1<len(fs) else page.rect.width-20
        if side=='right':gx0=round((previous+3)*2);gx1=n0-round(PARAM['number_edge_clearance_pt']*2)
        else:gx0=n1+round(PARAM['number_edge_clearance_pt']*2);gx1=round((following-3)*2)
        n0=max(0,n0);n1=min(w,n1);gx0=max(0,gx0);gx1=min(w,gx1)
        if gx1<=gx0:continue
        patch=gray[y0:y1,n0:n1]<P.PARAM['threshold']
        bands=[(a+y0,b+y0) for a,b in P.runs(patch.sum(1)>=2,max_gap=5) if 5<=b-a<=30]
        centers=[(a+b)/2-7 for a,b in bands]
        # Blank gaps are observed on the whole glyph region; no 36/72-row assumption.
        ink=(gray[y0:y1,gx0:gx1]<P.PARAM['threshold']).sum(1)
        blanks=[(a+y0,b+y0) for a,b in P.runs(ink<2) if b-a>=2]
        edges=[y0]
        for a,b in zip(centers,centers[1:]):
            midpoint=(a+b)/2
            options=[(s+t)/2 for s,t in blanks if a+6<(s+t)/2<b-6]
            edges.append(round(min(options,key=lambda v:abs(v-midpoint))) if options else round(midpoint))
        edges.append(y1)
        for index,((a,b),center) in enumerate(zip(bands,centers)):
            flags=[]
            if not orient['resolved']:flags.append('orientation_unresolved')
            if field['method']=='review parity prior fallback':flags.append('field_offset_fallback')
            if field.get('gap_inferred'):flags.append('print_field_gap_inferred')
            row=dict(pdf_column=column,row_index=index,margin_xyxy_2x=[n0,max(y0,a-2),n1,min(y1,b+2)],
                glyph_xyxy_2x=[gx0,edges[index],gx1,edges[index+1]],row_anchor_y_2x=center,flags=flags,
                occurrence_key=f'helsinki1979-v2:pdf{number}:c{column}:r{index}',edition='Koskenniemi-Parpola-1979',pdf_page=number,
                page_rotation=0,margin_side=side,serialization='visual_left_to_right',physical_line_side_boundaries='unresolved',
                glyph_pdf_box=[gx0/2,edges[index]/2,gx1/2,edges[index+1]/2])
            rows.append(row)
    if rows:
        rows=[r for start in range(0,len(rows),96) for r in P.ocr_lines(gray,rows[start:start+96])]
    if rec:
        for row in rows:
            x0,a,x1,b=row['glyph_xyxy_2x'];row['units'],row['segmentation_cost']=rec.segment(gray[a:b,x0:x1])
            row['auxiliaries']=[]
            for i,u in enumerate(row['units']):
                if not u['alternatives']:continue
                alt=u['alternatives'][0]
                if alt['dashed_auxiliary']:row['auxiliaries'].append(dict(unit_index=i,kind='possible_uncertainty_underline'))
                kinds=sorted({P.AUXILIARY_CODES[c] for c in alt['codes'] if c in P.AUXILIARY_CODES})
                if kinds:row['auxiliaries'].append(dict(unit_index=i,kind_candidates=kinds,original_glyph_count=None))
    return gray,rows,dict(orientation=orient,margin_side=side,columns=fs,column_count=len(fs),rows=len(rows))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pages',nargs='+',type=int,default=[30,62,100,129,130,145]);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned output')
    result=[]
    with P.fitz.open(P.PDF) as doc:
        for p in args.pages:
            _,rows,meta=process(doc,p)
            result.append(dict(pdf_page=p,layout=meta,rows=rows));print(json.dumps(dict(page=p,rows=len(rows),columns=meta['column_count'])),flush=True)
    P.write(out,dict(status='Exploratory',parameters=PARAM,pages=result))


if __name__=='__main__':main()
