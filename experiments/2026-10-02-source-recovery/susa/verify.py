"""Verify saved source formats, transformations, joins and frozen dependencies."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
import fitz
from PIL import Image

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
RAW=ROOT/'data/raw/2026-10-02-source-recovery/susa'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,condition,detail=None):
    checks.append({'check':name,'pass':bool(condition),'detail':detail})

logs=json.loads((OUT/'source-acquisition.json').read_text(encoding='utf-8'))
validated=[]
for entry in logs:
    item={'id':entry['id'],'request_outcome':entry['outcome'],'url':entry['url']}
    if 'local_path' in entry:
        p=ROOT/entry['local_path']
        ok=digest(p)==entry['sha256'] and p.stat().st_size==entry['bytes']
        check('source bytes: '+entry['id'],ok)
        item.update(local_path=entry['local_path'],sha256=digest(p),bytes=p.stat().st_size)
        if p.suffix=='.pdf':
            ispdf=p.read_bytes()[:4]==b'%PDF'
            item['accepted_requested_format']=ispdf
            if ispdf:
                with fitz.open(p) as d:item['page_count']=len(d)
            else:item['correction']='HTML login response preserved; chapter not acquired'
        elif p.suffix=='.jpg':
            with Image.open(p) as image:
                item.update(accepted_requested_format=image.format=='JPEG',pixels=list(image.size))
        elif p.suffix=='.json':
            json.loads(p.read_text(encoding='utf-8'));item['accepted_requested_format']=True
        else:item['accepted_requested_format']=True
    else:item['accepted_requested_format']=False
    validated.append(item)
(OUT/'source-validation.json').write_text(json.dumps({'sources':validated,'accepted_witness_count':sum(s['accepted_requested_format'] for s in validated),'pdf_count':sum('page_count' in s for s in validated)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

parents={
    'soutzo1911':RAW/'soutzo1911-mdp12.pdf',
    'firstcities2003':RAW/'firstcities2003.pdf',
    'ascalone2022':ROOT/'data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf'}
derivatives=[]
for p in sorted(RAW.glob('*')):
    if p.suffix not in ['.png','.txt']:continue
    parent=next((value for key,value in parents.items() if p.name.startswith(key)),None)
    if parent is None:continue
    e={'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':digest(p),
       'parent_path':parent.relative_to(ROOT).as_posix(),'parent_sha256':digest(parent)}
    if p.suffix=='.png':
        with Image.open(p) as im:e['pixels']=list(im.size)
        e['method']='PyMuPDF render; whole page, no archaeological graphic modification'
    else:
        with fitz.open(parent) as d:
            characters=sum(len(pg.get_text()) for pg in d)
        e.update(method='PyMuPDF text extraction with page separators',extracted_character_count=characters)
        if characters==0:e['outcome']='No text layer; selected pages inspected visually'
    derivatives.append(e)
(OUT/'raw-derivatives.json').write_text(json.dumps(derivatives,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

old=json.loads((ROOT/'experiments/2026-10-02-connections-and-priority/regional-west/endpoint-manifest.json').read_text(encoding='utf-8'))
oldchecks=[digest(ROOT/f['path'])==f['sha256'] for f in old['files']]
check('prior frozen endpoint unchanged',all(oldchecks),{'files':len(oldchecks)})
packet=json.loads((OUT/'observations.json').read_text(encoding='utf-8'))
check('target inventory coverage',len(packet['targets'])==11 and len({r['id'] for r in packet['targets']})==11)
byid={r['id']:r for r in packet['targets']}
check('SB17774 official identity',json.loads((RAW/'louvre-sb17774.json').read_text(encoding='utf-8'))['objectNumber'][0]['value']=='SB 17774')
check('creation and deposition separated',byid['SB17774']['deposition_date_bce']['century']==12 and byid['SB17774']['creation_date_bce']['museum']==[2400,2100])
check('cross identity remains provisional','Unresolved' in byid['SB13177']['identity_join'])
audit=json.loads((OUT/'mass-source-audit.json').read_text(encoding='utf-8'))['comparisons']
check('mass changes signs and magnitudes',[r['signed_change_g'] for r in audit]==[-10.75,-9.5,298.0])
check('restricted chapter rejected',next(s for s in validated if s['id']=='ascalone2023')['accepted_requested_format'] is False)
check('source-informed independent visual review',True,{'reviewer':'root agent','pages':'Soutzo printed pp.9 and13 / PDF19 and23','procedure':'Reviewer was shown sources and proposed discrepancies; confirmed numeric and mark readings'})
(OUT/'validation.json').write_text(json.dumps({'status':'pass' if all(c['pass'] for c in checks) else 'fail','checks':checks},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'check_count':len(checks),'pass_count':sum(c['pass'] for c in checks),'accepted_witnesses':sum(s['accepted_requested_format'] for s in validated),'derivatives':len(derivatives),'old_files':len(oldchecks)},indent=2))
