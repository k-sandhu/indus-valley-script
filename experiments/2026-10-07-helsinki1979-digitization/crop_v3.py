"""Ink-aware Helsinki printed-line layout and unit windows, retaining the matcher."""
from __future__ import annotations
import json
from pathlib import Path
import math
import numpy as np
import pipeline as P
import layout_v3 as OLD

PARAM=dict(layout_scale=4,recognition_scale=2,threshold=190,field_search_padding_pt=10,
    digit_component_height_pt=[1,6.5],digit_component_width_pt=[.3,7.5],digit_component_min_area_pt2=.5,
    text_line_join_pt=2.5,field_pair_center_distance_pt=[3.5,8.5],field_pad_pt=.35,
    repeated_field_horizontal_padding_pt=4,
    exclude_field_search_edge_components=True,
    field_to_glyph_center_pt=2.25,body_y_pt=[60,795],minimum_glyph_component_area_pt2=.10,
    row_padding_pt=.35,continuation_anchor_distance_pt=10,continuation_cluster_pt=5,
    underline_height_max_pt=1.3,underline_dash_width_pt=[.5,3],underline_group_gap_pt=2.5,
    underline_group_span_pt=[9,17],underline_min_dashes=3,underline_to_body_max_gap_pt=4,
    short_tick_height_max_pt=3.5,tick_tall_height_ratio=3.5,tick_separation_min_pt=1.3,
    component_projection_min_pixels=1,unit_segmentation_penalty=1.0,max_join_gap_2x=19,
    max_unit_width_2x=72,model='unchanged original CNN/templates/scores/calibration',
    continuation_ownership='preceding numbered line in same printed column; provisional')


def components(binary,ox=0,oy=0):
    n,labels,stats,_=P.cv2.connectedComponentsWithStats(binary.astype('uint8'),8)
    return [dict(x=int(x)+ox,y=int(y)+oy,w=int(w),h=int(h),area=int(a),label=i+1)
            for i,(x,y,w,h,a) in enumerate(stats[1:])]


def text_lines(comps):
    groups=[]
    for c in sorted(comps,key=lambda c:c['y']+c['h']/2):
        center=c['y']+c['h']/2
        if groups and abs(center-groups[-1]['center'])<=PARAM['text_line_join_pt']*4:
            g=groups[-1];g['components'].append(c);g['bottom']=max(g['bottom'],c['y']+c['h'])
            g['top']=min(g['top'],c['y']);g['center']=np.average([x['y']+x['h']/2 for x in g['components']],weights=[x['area'] for x in g['components']])
        else:groups.append(dict(top=c['y'],bottom=c['y']+c['h'],center=center,components=[c]))
    for g in groups:
        g['center']=(g['top']+g['bottom'])/2
        g['left']=min(c['x'] for c in g['components']);g['right']=max(c['x']+c['w'] for c in g['components'])
    return groups


def field_pairs(gray,field,column):
    scale=4;h,w=gray.shape;pad=PARAM['field_search_padding_pt']
    x0=max(0,round((field['left']-pad)*scale));x1=min(w,round((field['right']+pad)*scale))
    y0,y1=[round(x*scale) for x in PARAM['body_y_pt']]
    cc=components(gray[y0:y1,x0:x1]<PARAM['threshold'],x0,y0)
    lo,hi=PARAM['digit_component_height_pt'];wl,wh=PARAM['digit_component_width_pt']
    small=[c for c in cc if lo<=c['h']/scale<=hi and wl<=c['w']/scale<=wh and c['area']/16>=PARAM['digit_component_min_area_pt2']
           and c['x']>x0 and c['x']+c['w']<x1]
    def pair_lines(items):
        lines=text_lines(items);pairs=[];i=0
        while i<len(lines)-1:
            upper=lines[i]
            candidates=[(j,line) for j,line in enumerate(lines[i+1:i+4],i+1)
                if PARAM['field_pair_center_distance_pt'][0]<=(line['center']-upper['center'])/scale<=PARAM['field_pair_center_distance_pt'][1]
                and len(line['components'])>=2 and (line['right']-line['left'])/scale>=10]
            if candidates:
                lower_index,lower=candidates[0]
                if len(upper['components'])>=2 or abs((upper['left']+upper['right'])/8-field['center'])<8:
                    padpx=PARAM['field_pad_pt']*scale
                    box=[min(upper['left'],lower['left'])-padpx,upper['top']-padpx,
                         max(upper['right'],lower['right'])+padpx,lower['bottom']+padpx]
                    pairs.append(dict(margin_pdf_box=[x/scale for x in box],
                        upper_box_pdf=[upper['left']/scale,upper['top']/scale,upper['right']/scale,upper['bottom']/scale],
                        lower_box_pdf=[lower['left']/scale,lower['top']/scale,lower['right']/scale,lower['bottom']/scale],
                        anchor=(upper['top']+lower['bottom'])/8-PARAM['field_to_glyph_center_pt'],column=column))
                    i=lower_index+1;continue
            i+=1
        return pairs
    pairs=pair_lines(small)
    if len(pairs)>=5:
        # The repeated classification band supplies the print field's horizontal bounds.
        left=float(np.median([p['lower_box_pdf'][0] for p in pairs]))-PARAM['repeated_field_horizontal_padding_pt']
        right=float(np.median([p['lower_box_pdf'][2] for p in pairs]))+PARAM['repeated_field_horizontal_padding_pt']
        pairs=pair_lines([c for c in small if left*4<=c['x'] and c['x']+c['w']<=right*4])
    return pairs


def glyph_lines(gray,fields,side):
    h,w=gray.shape;numbered=[];layouts=[]
    all_pairs=[field_pairs(gray,f,i) for i,f in enumerate(fields)]
    all_bounds=[(min(p['margin_pdf_box'][0] for p in ps),max(p['margin_pdf_box'][2] for p in ps))
                if ps else (f['left'],f['right']) for f,ps in zip(fields,all_pairs)]
    for col,field in enumerate(fields):
        pairs=all_pairs[col]
        if not pairs:
            layouts.append(dict(column=col,numbered_lines=0,flags=['no_field_pairs']));continue
        # Use all actual field blocks, not an OCR quantile, to define column edges.
        actual_left=min(p['margin_pdf_box'][0] for p in pairs);actual_right=max(p['margin_pdf_box'][2] for p in pairs)
        previous=all_bounds[col-1][1]+.1 if col else 25
        following=all_bounds[col+1][0]-.1 if col+1<len(fields) else 575
        left=previous if side=='right' else actual_right+.1
        right=actual_left-.1 if side=='right' else following
        # Expand to per-row field extremes later; mask field ink before line grouping.
        if side=='right':right=max(p['margin_pdf_box'][0] for p in pairs)-.1
        else:left=min(p['margin_pdf_box'][2] for p in pairs)+.1
        x0,x1=max(0,math.floor(left*4)),min(w,math.ceil(right*4))
        y0,y1=[round(v*4) for v in PARAM['body_y_pt']]
        mask=gray[y0:y1,x0:x1]<PARAM['threshold']
        for p in [p for ps in all_pairs for p in ps]:
            fx0,fy0,fx1,fy1=[round(v*4) for v in p['margin_pdf_box']]
            a,b=max(0,fy0-y0),min(mask.shape[0],fy1-y0)
            c,d=max(0,fx0-x0),min(mask.shape[1],fx1-x0)
            if a<b and c<d:mask[a:b,c:d]=False
        cc=components(mask,x0,y0)
        cc=[c for c in cc if c['area']/16>=PARAM['minimum_glyph_component_area_pt2']]
        anchors=[p['anchor'] for p in pairs];extra=[]
        # Tall source components locate unnumbered continuation lines without a row-count prior.
        candidates=[c for c in cc if c['h']/4>=8 and min(abs((c['y']+c['h']/2)/4-a) for a in anchors)>PARAM['continuation_anchor_distance_pt']]
        for c in sorted(candidates,key=lambda c:c['y']+c['h']/2):
            center=(c['y']+c['h']/2)/4
            if extra and abs(center-extra[-1])<PARAM['continuation_cluster_pt']:extra[-1]=(extra[-1]+center)/2
            else:extra.append(center)
        records=[dict(anchor=p['anchor'],pair=p) for p in pairs]+[dict(anchor=a,pair=None) for a in extra]
        records.sort(key=lambda r:r['anchor'])
        owned=[[] for _ in records]
        for c in cc:
            center=(c['y']+c['h']/2)/4
            # A dashed underline belongs to the closest preceding body, not the following line.
            is_dash=c['h']/4<=PARAM['underline_height_max_pt'] and .5<=c['w']/4<=3
            distances=[abs(center-r['anchor']-(7.7 if is_dash else 0)) for r in records]
            idx=int(np.argmin(distances))
            if distances[idx] <= (5 if is_dash else 10):owned[idx].append(c)
        out=[];parent=None
        for index,(record,ink) in enumerate(zip(records,owned)):
            if not ink:continue
            minx=min(c['x'] for c in ink)/4;maxx=max(c['x']+c['w'] for c in ink)/4
            miny=min(c['y'] for c in ink)/4;maxy=max(c['y']+c['h'] for c in ink)/4
            pair=record['pair'];padding=PARAM['row_padding_pt']
            if pair:
                fieldbox=pair['margin_pdf_box']
                if side=='right':maxx=min(maxx,fieldbox[0]-.1)
                else:minx=max(minx,fieldbox[2]+.1)
            box=[max(left,minx-padding),miny-padding,min(right,maxx+padding),maxy+padding]
            if pair:
                if side=='right':box[2]=min(box[2],fieldbox[0]-.05)
                else:box[0]=max(box[0],fieldbox[2]+.05)
            flags=[]
            if pair is None:flags.append('continuation_ownership_provisional')
            if box[2]<=box[0] or box[3]<=box[1]:continue
            row=dict(pdf_column=col,row_index=len(out),row_anchor_y_2x=record['anchor']*2,
                glyph_pdf_box=box,glyph_xyxy_2x=[round(x*2) for x in box],margin_side=side,
                margin_pdf_box=pair['margin_pdf_box'] if pair else None,
                margin_xyxy_2x=[round(v*2) for v in pair['margin_pdf_box']] if pair else None,
                field_line_boxes_pdf=[pair['upper_box_pdf'],pair['lower_box_pdf']] if pair else [],
                line_kind='numbered' if pair else 'continuation',flags=flags,
                ink_components=ink,layout_anchor_pdf=record['anchor'])
            if pair:parent=len(out)
            row['parent_row_index']=parent if pair is None else None
            out.append(row)
        numbered.extend(out)
        layouts.append(dict(column=col,field=field,numbered_lines=len(pairs),continuation_lines=len(extra),printed_lines=len(out),
            actual_field_bounds_pdf=[actual_left,actual_right],column_bounds_pdf=[left,right]))
    return numbered,layouts


def process(doc,page_number,rec=None,read_fields=True):
    page=doc[page_number-1];gray4=P.render(doc,page_number,4);gray2=P.render(doc,page_number,2)
    fields,side=OLD.fields(page,gray2);rows,columns=glyph_lines(gray4,fields,side)
    orient=OLD.orientation(page)
    for row in rows:
        row.update(pdf_page=page_number,section=section(page_number),edition='Koskenniemi-Parpola-1979',
            page_rotation=0,serialization='visual_left_to_right',physical_line_side_boundaries='unresolved',
            occurrence_key=f'helsinki1979-v3:pdf{page_number}:c{row["pdf_column"]}:r{row["row_index"]}',
            segment_id=f'pdf{page_number}:c{row["pdf_column"]}:r{row["row_index"]}',quarantined=True)
        if not orient['resolved']:row['flags'].append('orientation_header_unresolved')
    lookup={(r['pdf_column'],r['row_index']):r for r in rows}
    for row in rows:
        parent=lookup.get((row['pdf_column'],row['parent_row_index']))
        row['text_occurrence_key']=parent['occurrence_key'] if parent else row['occurrence_key']
        row['continuation_of']=parent['occurrence_key'] if parent else None
    if read_fields:
        main=[r for r in rows if r['line_kind']=='numbered']
        for start in range(0,len(main),96):P.ocr_lines(gray2,main[start:start+96])
        for row in main:
            upper=row['margin_ocr'][0];literal=upper['text']
            # The fixed digit library contains no letters. Keep a well-formed OCR suffix witness.
            if P.re.fullmatch(r'\d{1,4}[A-Z]+',literal) and upper['confidence']>=50:
                row['inscription_number']=literal;row['flags'].append('letter_suffix_from_ocr')
        for row in rows:
            if row['line_kind']=='continuation':
                parent=lookup.get((row['pdf_column'],row['parent_row_index']))
                row['inscription_number']=parent.get('inscription_number') if parent else None
                row['classification_code']=None;row['number_field_present']=False
            else:row['number_field_present']=True
    if rec:
        for row in rows:
            row['units'],row['segmentation_cost']=segment_units(gray4,gray2,row,rec)
            row['auxiliaries']=[dict(unit_index=i,kind='uncertainty_underline') for i,u in enumerate(row['units']) if u.get('underline_pdf_box')]
            row['minimum_unit_confidence']=min((u['confidence'] for u in row['units']),default=None)
            row['confidence_product']=math.prod(u['confidence'] for u in row['units']) if row['units'] else None
    return gray4,gray2,rows,dict(orientation=orient,columns=columns,column_count=len(fields),
        printed_lines=len(rows),numbered_lines=sum(r['line_kind']=='numbered' for r in rows),
        continuation_lines=sum(r['line_kind']=='continuation' for r in rows))


def section(page):return 'number_order' if page<=78 else 'end_sorted' if page<=130 else 'beginning_sorted'


def underline_groups(cc):
    dashes=[c for c in cc if c['h']/4<=PARAM['underline_height_max_pt'] and PARAM['underline_dash_width_pt'][0]<=c['w']/4<=PARAM['underline_dash_width_pt'][1]]
    groups=[]
    for c in sorted(dashes,key=lambda c:(round((c['y']+c['h']/2)/4),c['x'])):
        possible=[g for g in groups if abs((c['y']+c['h']/2)-g['yc'])<=3 and 0<=c['x']-g['right']<=PARAM['underline_group_gap_pt']*4]
        if possible:
            g=possible[-1];g['dashes'].append(c);g['right']=c['x']+c['w'];g['yc']=np.mean([x['y']+x['h']/2 for x in g['dashes']])
        else:groups.append(dict(left=c['x'],right=c['x']+c['w'],yc=c['y']+c['h']/2,dashes=[c]))
    result=[]
    # Consecutive 5-dash cells can touch: split long groups at the large periodic gap.
    for g in groups:
        if len(g['dashes'])<PARAM['underline_min_dashes']:continue
        ds=g['dashes'];chunks=[ds[i:i+5] for i in range(0,len(ds),5)] if len(ds)>6 else [ds]
        for chunk in chunks:
            a=min(c['x'] for c in chunk);b=max(c['x']+c['w'] for c in chunk)
            if len(chunk)>=3 and PARAM['underline_group_span_pt'][0]<=(b-a)/4<=PARAM['underline_group_span_pt'][1]:
                result.append(dict(box=[a,min(c['y'] for c in chunk),b,max(c['y']+c['h'] for c in chunk)],dashes=chunk))
    return result


def segment_units(gray4,gray2,row,rec):
    box=row['glyph_pdf_box'];a,b,c,d=[math.floor(x*4) for x in box];mask=gray4[b:d,a:c]<PARAM['threshold']
    cc=components(mask,a,b);groups=underline_groups(cc)
    body=mask.copy()
    for g in groups:
        x0,y0,x1,y1=g['box'];body[max(0,y0-b):min(body.shape[0],y1-b),max(0,x0-a):min(body.shape[1],x1-a)]=False
    # Use the unchanged original matcher at its original pixel scale.
    body2=P.cv2.resize(body.astype('uint8'),(max(1,round(body.shape[1]/2)),max(1,round(body.shape[0]/2))),interpolation=P.cv2.INTER_AREA)>0
    comps=P.runs(body2.any(0));comps=[(x,z) for x,z in comps if body2[:,x:z].sum()>=3]
    forced=[]
    for (x,z),(xx,zz) in zip(comps,comps[1:]):
        yy=np.flatnonzero(body2[:,x:z].any(1));yyy=np.flatnonzero(body2[:,xx:zz].any(1))
        h1=yy[-1]-yy[0]+1;h2=yyy[-1]-yyy[0]+1
        if min(h1,h2)/2<=PARAM['short_tick_height_max_pt'] and max(h1,h2)>=PARAM['tick_tall_height_ratio']*min(h1,h2) and (xx-z)/2>=PARAM['tick_separation_min_pt']:
            forced.append((z+xx)/2)
    count=len(comps);cost=[float('inf')]*(count+1);paths=[None]*(count+1);cost[0]=0;paths[0]=[]
    for i in range(count):
        for j in range(i,min(count,i+12)):
            x0,x1=comps[i][0],comps[j][1]
            if x1-x0>PARAM['max_unit_width_2x']:break
            if j>i and comps[j][0]-comps[j-1][1]>PARAM['max_join_gap_2x']:break
            if any(x0<f<x1 for f in forced):break
            binary=body2[:,x0:x1];alts=rec.alternatives(binary)
            value=alts[0]['combined_cost']*binary.sum()/100+PARAM['unit_segmentation_penalty']
            if cost[i]+value<cost[j+1]:cost[j+1]=cost[i]+value;paths[j+1]=paths[i]+[(x0,x1)]
    units=[]
    for x0,x1 in paths[-1] or []:
        # Associate a whole dashed sign slot to its glyph-body center before matching.
        absolute=(a+(x0+x1))/4
        near=[g for g in groups if g['box'][0]/4<=absolute<=g['box'][2]/4]
        absx0=a+x0*2;absx1=a+x1*2
        if near:absx0=min(absx0,min(g['box'][0] for g in near));absx1=max(absx1,max(g['box'][2] for g in near))
        X0,X1=math.floor(absx0/2),math.ceil(absx1/2);Y0,Y1=math.floor(b/2),math.ceil(d/2)
        binary=gray2[Y0:Y1,X0:X1]<PARAM['threshold'];alts=rec.alternatives(binary)
        features=np.array([1.,alts[0]['combined_cost'],alts[1]['combined_cost']-alts[0]['combined_cost']])
        confidence=float(1/(1+np.exp(-np.clip(features@np.array(rec.calibration['coefficients']),-30,30))))
        units.append(dict(x_bounds=[X0-round(box[0]*2),X1-round(box[0]*2)],y_bounds=[0,Y1-Y0],
            unit_pdf_box=[X0/2,Y0/2,X1/2,Y1/2],alternatives=alts,confidence=confidence,
            confidence_status='unchanged_development_logistic_not_recalibrated',unit_kind='glyph_or_auxiliary_unverified',
            underline_pdf_box=[v/4 for v in near[0]['box']] if near else None))
    return units,float(cost[-1]) if math.isfinite(cost[-1]) else None
