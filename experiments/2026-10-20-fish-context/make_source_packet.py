"""Build local inspection sheets with source captions and a tracked selection log."""
from collections import defaultdict
import importlib.util
import json
from pathlib import Path
import hashlib

from PIL import Image,ImageOps,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fish_study',HERE/'study.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)


def main():
    objects=s.read_rows(s.RAW/'register-v1/objects.jsonl')
    faces=s.read_rows(s.RAW/'register-v1/faces.jsonl')
    obj={r['object_family_id']:r for r in objects}
    by_cisi={c:r['object_family_id'] for r in objects for c in r['cisi']}
    selected=[]
    def add(family,reason):
        if family not in [x[0] for x in selected]:selected.append((family,reason))
    for c in ['H-9','H-902','M-410','M-478']:
        if c in by_cisi:add(by_cisi[c],'published anchor '+c)
    candidates=[r for r in objects if r['excavation_table_rows'] and r['images']]
    for r in sorted(candidates,key=lambda x:hashlib.sha256(('source-audit-20261020|'+x['object_family_id']).encode()).hexdigest())[:4]:
        add(r['object_family_id'],'source-table sample, hash order')
    model=s.read_json(HERE/'discovery-v2/model.json');rank={x:i for i,x in enumerate(model['order']['codes'])}
    confirmation=s.sequences(s.read_rows(s.RAW/'confirmation-v1/confirmation-faces.jsonl'),seals=True)
    reversals=[r for r in confirmation if any(a in rank and b in rank and a!=b and rank[a]>rank[b] for a,b in zip(r['seq'],r['seq'][1:]))]
    for r in sorted(reversals,key=lambda x:x['source_cisi'])[:2]:add(r['object_family_id'],'reversed fish order')
    table=s.coding();fish=s.fish_codes(table)
    outside=[e for e in s.number_events(confirmation,table,fish) if e['item']=='220' and e['stroke_family']=='B001' and e['value'] not in (3,6,7)]
    face_index={r['record_id']:r for r in confirmation}
    for e in sorted(outside,key=lambda x:face_index[x['record_id']]['source_cisi'])[:2]:add(face_index[e['record_id']]['object_family_id'],'short-stroke value outside astronomical set')
    dest=s.RAW/'source-packet-v1';dest.mkdir(exist_ok=False)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',13)
    log=[];panels=[]
    image_dir=s.ROOT/'data/lipi/public/seal_images'
    for family,reason in selected:
        r=obj[family]
        # Keep several anchor views; for sample cases prefer the original object face.
        ims=list({i['file']:i for i in r['images']}.values())
        ims=sorted(ims,key=lambda i:(i['kind']!='object',i['relation']!='face-side','_A' not in i['file'],i['file']))
        if reason.startswith('published anchor'):
            ims=ims[:3]
            if 'H-902' in r['cisi']:
                ims=list({i['file']:i for i in r['images']}.values())
        else:ims=ims[:1]
        item={'object_family_id':family,'cisi':r['cisi'],'reason':reason,'files':[],'table_rows':[]}
        for t in r['excavation_table_rows']:
            item['table_rows'].append({k:t[k] for k in ['source','catalogue_no','printed_page','field_no','area','locus','level_ft','level_reference']})
        for im in ims:
            path=image_dir/im['file']
            if not path.exists():continue
            item['files'].append({'file':im['file'],'sha256':s.sha256(path),'volume':im['cisi_volume'],
                                  'pdf_page':im['cisi_pdf_page'],'kind':im['kind'],'relation':im['relation']})
            panel=Image.new('RGB',(610,540),'white');d=ImageDraw.Draw(panel)
            d.text((8,4),'; '.join(r['cisi'])+' | '+im['kind'],font=font,fill='black')
            d.text((8,29),reason,font=small,fill='black')
            d.text((8,49),im['file']+' | CISI '+im['cisi_volume']+' PDF '+im['cisi_pdf_page'],font=small,fill='black')
            with Image.open(path) as original:
                scaled=ImageOps.contain(original.convert('RGB'),(594,460))
                panel.paste(scaled,((610-scaled.width)//2,75+(460-scaled.height)//2))
            panels.append(panel)
        log.append(item)
    for start in range(0,len(panels),4):
        sheet=Image.new('RGB',(1220,1080),'#ddd')
        for j,p in enumerate(panels[start:start+4]):sheet.paste(p,((j%2)*610,(j//2)*540))
        sheet.save(dest/f'sheet-{start//4+1:02}.png')
    s.write_json(HERE/'source-selection-v1.json',{'selection':log,'objects':len(log),'panels':len(panels),
                                               'rights':'Photographs and contact sheets remain local; source identifiers and our annotations are tracked.'})
    print(json.dumps({'objects':len(log),'panels':len(panels),'sheets':(len(panels)+3)//4,'selected':[(x['cisi'],x['reason']) for x in log]},indent=2))


if __name__=='__main__':main()
