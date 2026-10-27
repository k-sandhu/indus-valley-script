"""Render local technical annotations over audited source-plan crops.

All source pixels, detailed annotation positions and derivative images stay on D.
This script reads those positions rather than copying third-party traces to Git.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west')
OUT = RAW / 'boards-v2'
CREAM = '#F7F4ED'
INK = '#182C30'
TEAL = '#207D80'
RUST = '#BA573B'
MUTED = '#56676A'
PALE = '#E2E8E4'

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)

def lines(draw, text, f, width):
    result = []
    for paragraph in text.split('\n'):
        row = ''
        for word in paragraph.split():
            candidate = f'{row} {word}'.strip()
            if row and draw.textlength(candidate, font=f) > width:
                result.append(row)
                row = word
            else:
                row = candidate
        result.append(row)
    return result

def paragraph(draw, text, xy, width, f, fill=INK, leading=None):
    x, y = xy
    step = leading or int(f.size * 1.3)
    for row in lines(draw, text, f, width):
        draw.text((x, y), row, font=f, fill=fill)
        y += step
    return y

def apply(matrix, point):
    return (np.asarray(matrix) @ np.array([*point, 1.0]))[:2]

def dashed(draw, points, fill, width=3, dash=12):
    for p, q in zip(points, points[1:]):
        p, q = np.asarray(p, dtype=float), np.asarray(q, dtype=float)
        n = float(np.linalg.norm(q-p))
        if not n:
            continue
        for start in np.arange(0, n, dash*2):
            a = p+(q-p)*(start/n)
            b = p+(q-p)*(min(start+dash,n)/n)
            draw.line([tuple(a),tuple(b)],fill=fill,width=width)

def main():
    OUT.mkdir(exist_ok=False)
    specs = load(RAW/'annotations-v1.json')['boards']
    panels = {p['id']:p for p in load(HERE/'plan-panels.json')['panels']}
    measured = {m['id']:m for m in load(HERE/'measurements.json')['measurements']}
    traces = load(RAW/'traces-v1.json')
    trace_metrics = {m['id']:m for m in traces['measurements']}
    registration = load(RAW/'measurement-v1/registration-details.json')
    assets = []
    for spec in specs:
        canvas = Image.new('RGB',(2600,1800),CREAM)
        d = ImageDraw.Draw(canvas)
        d.rectangle((0,0,2600,17),fill=TEAL)
        d.text((55,44),spec['title'],font=font(56,True),fill=INK)
        d.text((58,122),f"{spec['id']}  |  Original excavation source with project annotations  |  Local-only",font=font(25),fill=MUTED)
        image_box = (52,190,1640,1480)
        boxes = []
        if len(spec['panels']) == 1:
            boxes = [image_box]
        elif spec['id']=='PW-V03':
            boxes = [(52,190,1135,1480),(1155,500,1640,1300)]
        else:
            boxes = [(52,190,1640,860),(52,885,1640,1480)]
        mappings = {}
        for pid, box in zip(spec['panels'],boxes):
            p=panels[pid]
            im=Image.open(p['crop_physical_path']).convert('RGB')
            x0,y0,x1,y1=box
            d.rectangle(box,fill='white',outline=PALE,width=2)
            short_locator=p['locator'] if p['pdf_page_index'] is not None else 'slide '+p['locator'].rsplit('slide ',1)[-1]
            label=f"{pid}  |  {short_locator}"
            d.text((x0+15,y0+10),label,font=font(23,True),fill=TEAL)
            avail_w,avail_h=x1-x0-30,y1-y0-60
            scale=min(avail_w/im.width,avail_h/im.height)
            size=(round(im.width*scale),round(im.height*scale))
            ox=x0+15+(avail_w-size[0])/2
            oy=y0+50+(avail_h-size[1])/2
            canvas.paste(im.resize(size,Image.Resampling.LANCZOS),(round(ox),round(oy)))
            mappings[pid]=(ox,oy,scale)

        def display(pid, point):
            ox,oy,s=mappings[pid]
            return (ox+point[0]*s,oy+point[1]*s)

        if spec.get('registration_overlay'):
            a=np.asarray(registration['PW-P01']['pixel_to_grid_offset_matrix'])
            b=np.linalg.inv(np.asarray(registration['PW-P02']['pixel_to_grid_offset_matrix']))
            crop=panels['PW-P02']['parent_pixel_to_crop_pixel_matrix']
            for poly in traces['early_cart_track_centerlines']['polylines']:
                dest=[display('PW-P02',apply(crop,apply(b,apply(a,p)))) for p in poly]
                d.line(dest,fill='white',width=11)
                d.line(dest,fill=RUST,width=6)
            for c in registration['PW-P02']['controls']:
                x,y=display('PW-P02',apply(crop,c['pixel']))
                d.line((x-9,y,x+9,y),fill='white',width=8)
                d.line((x,y-9,x,y+9),fill='white',width=8)
                d.line((x-9,y,x+9,y),fill=TEAL,width=4)
                d.line((x,y-9,x,y+9),fill=TEAL,width=4)
            window=traces['registration']['declared_geometric_window']
            coords=[(e-2355,n-1015) for e,n in [(window['easting'][0],window['northing'][0]),(window['easting'][1],window['northing'][0]),(window['easting'][1],window['northing'][1]),(window['easting'][0],window['northing'][1]),(window['easting'][0],window['northing'][0])]]
            dest=[display('PW-P02',apply(crop,apply(b,p))) for p in coords]
            dashed(d,dest,TEAL,3,14)

        for mid in spec['metrics']:
            t=trace_metrics[mid]
            pts=[display(t['panel'],p) for p in t['feature_endpoints']]
            d.line(pts,fill='white',width=13)
            d.line(pts,fill=RUST,width=6)
            for x,y in pts:
                d.ellipse((x-7,y-7,x+7,y+7),fill=RUST,outline='white',width=2)
            pts=[display(t['panel'],p) for p in t['scale_endpoints']]
            d.line(pts,fill=TEAL,width=4)
            for x,y in pts:
                d.ellipse((x-5,y-5,x+5,y+5),fill=TEAL)

        for i, point in enumerate(spec['points'],1):
            x,y=display(point['panel'],point['point'])
            r=17
            d.ellipse((x-r,y-r,x+r,y+r),fill=RUST,outline='white',width=3)
            label=str(i)
            width=d.textlength(label,font=font(20,True))
            d.text((x-width/2,y-12),label,font=font(20,True),fill='white')

        # One reading note covers every local width on this board.
        x,y,w=1695,193,845
        y=paragraph(d,spec['caption'],(x,y),w,font(31),leading=42)+30
        d.line((x,y,x+w,y),fill=PALE,width=3)
        y+=24
        for i,point in enumerate(spec['points'],1):
            y=paragraph(d,f"{i}. {point['label']}",(x,y),w,font(25,True),fill=RUST,leading=34)+8
        if spec['points']:
            y+=15
        for note in spec['notes']:
            d.rectangle((x,y+10,x+8,y+18),fill=TEAL)
            y=paragraph(d,note,(x+23,y),w-23,font(26),leading=35)+16
        if spec['metrics']:
            y+=8
            for mid in spec['metrics']:
                m=measured[mid]
                lo,hi=m['digitization_sensitivity_metres']
                label=f"{mid}: {m['metres']:.1f} m [{lo:.1f}, {hi:.1f}]"
                y=paragraph(d,label,(x,y),w,font(29,True),fill=RUST)+10
            y=paragraph(d,'Rust: measured opening. Teal: source scale endpoints. Brackets give endpoint-reading bounds; original survey and drawing error remain unknown.',(x,y+5),w,font(23),fill=MUTED,leading=30)
        if y>1485:
            raise ValueError(f"Sidebar overflows: {spec['id']} ends at {y}")
        fy=1515
        d.line((55,fy-16,2545,fy-16),fill=PALE,width=3)
        cited=[]
        for pid in spec['sources']:
            p=panels[pid]
            if p['source_id'] not in cited:
                same=[panels[k] for k in spec['sources'] if panels[k]['source_id']==p['source_id']]
                loc='; '.join(f"{q['locator']} (PDF index {q['pdf_page_index']})" if q['pdf_page_index'] is not None else q['locator'] for q in same)
                text=f"{p['source_id']} | {p['source_title']} | {loc}"
                fy=paragraph(d,text,(58,fy),2480,font(22),fill=INK,leading=28)+3
                fy=paragraph(d,p['source_url'],(58,fy),2480,font(17),fill=MUTED,leading=23)+12
                cited.append(p['source_id'])
        if fy>1788:
            raise ValueError(f"Source footer overflows: {spec['id']} ends at {fy}")
        path=OUT/f"{spec['id']}.png"
        canvas.save(path)
        assets.append({
            'id':spec['id'],'physical_path':str(path),'logical_path':f"data/raw/2026-10-24-shared-infrastructure-plan-test/plans-west/boards-v2/{spec['id']}.png",
            'sha256':sha(path),'title':spec['title'],'caption':spec['caption'],
            'source_panels':[{'panel_id':pid,'source_id':panels[pid]['source_id'],'title':panels[pid]['source_title'],'locator':panels[pid]['locator'],'pdf_page_index':panels[pid]['pdf_page_index'],'url':panels[pid]['source_url'],'source_sha256':panels[pid]['parent_source_sha256']} for pid in spec['sources']],
            'local_only':True,'rights_status':'rights-unverified source crops and annotated derivatives',
            'image_pixels':[2600,1800],
            'annotation_positions_path':str(RAW/'annotations-v1.json'),
            'annotation_positions_sha256':sha(RAW/'annotations-v1.json'),
            'measurement_ids':spec['metrics'],'registration_id':'PW-R01' if spec.get('registration_overlay') else None,
            'source_pixel_policy':'Actual audited source crops with manual technical annotations. Display resampling preserves aspect ratio; no generated archaeological reconstruction.'})
    (HERE/'visual-assets.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),'assets':assets,'full_panel_gallery_path':str(RAW/'crops-v1'),'board_specification_sha256':sha(RAW/'annotations-v1.json')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    thumbs=[]
    for a in assets:
        im=Image.open(a['physical_path'])
        im.thumbnail((780,540))
        thumbs.append(im)
    contact=Image.new('RGB',(780*3,540*4),CREAM)
    for i,im in enumerate(thumbs):
        contact.paste(im,((i%3)*780,(i//3)*540))
    contact.save(OUT/'contact-sheet.png')
    print(json.dumps({'boards':len(assets),'output':str(OUT),'manifest':str(HERE/'visual-assets.json')}))

if __name__=='__main__':
    main()
