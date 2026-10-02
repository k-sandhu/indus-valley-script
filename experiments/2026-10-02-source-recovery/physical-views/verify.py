"""Manual source/crop/accounting verification. Does not alter saved witnesses."""
from pathlib import Path
import argparse
import ast
import datetime
import hashlib
import json
import re
import fitz
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
checks=[]
hash_cache={}


def sha(p):
    p=p.resolve()
    if p not in hash_cache:hash_cache[p]=hashlib.sha256(p.read_bytes()).hexdigest()
    return hash_cache[p]


def check(name,condition,detail=None):
    checks.append({'check':name,'passed':bool(condition),'detail':detail})


def file_check(rec,label):
    p=ROOT/rec['path']
    check(label+' exists',p.is_file())
    if p.is_file():
        check(label+' sha256',sha(p)==rec['sha256'])
        check(label+' bytes',p.stat().st_size==rec['bytes'])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='verification.json')
    args=parser.parse_args()
    if Path(args.out).name!=args.out:raise ValueError('Output must be a basename in the owned directory')
    manifest=json.loads((HERE/'source-manifest.json').read_text(encoding='utf8'))
    acquired=[s for s in manifest['sources'] if s['source_kind']=='new ordinary-public acquisition']
    pdfs=[s for s in manifest['sources'] if 'path' in s]
    check('five newly acquired PDF witnesses',len(acquired)==5)
    check('eight source PDF paths',len(pdfs)==8)
    check('distinct source PDF paths',len({s['path'] for s in pdfs})==8)
    for s in pdfs:
        file_check(s,s['title'])
        p=ROOT/s['path']
        check(s['title']+' PDF header',p.read_bytes()[:5]==b'%PDF-')
        with fitz.open(p) as doc:
            check(s['title']+' readable PDF',doc.page_count>0)
            if 'pdf_page_count' in s:check(s['title']+' pages',doc.page_count==s['pdf_page_count'])
    file_check(manifest['protocol'],'prospective protocol')
    file_check(manifest['coordinate_pilot'],'retained coordinate pilot')
    o=json.loads((HERE/'observations-v2.json').read_text(encoding='utf8'))
    vv=o['views']
    fixed={'L161','L162','L163','L165','L168','L190','L193','L206'}
    check('nineteen accepted panels',len(vv)==19)
    check('eight fixed Lothal targets',set(v['object_id'] for v in vv)==fixed)
    check('unique view identifiers',len({v['view_id'] for v in vv})==19)
    cisi=[v for v in vv if v['source_id']=='cisi1']
    check('fifteen catalogue panels',len(cisi)==15)
    faces={(v['object_id'],v['source_face_label'].split()[0]) for v in cisi}
    check('fourteen labelled catalogue object faces',len(faces)==14)
    check('four colour panels',sum(v['source_id']!='cisi1' for v in vv)==4)
    check('no complete cut surfaces',all(v['complete_marked_surface'] is False for v in vv))
    check('no complete object totals',all(v['complete_object_cut_total'] is None for v in vv))
    check('no new registered Harappa images',o['harappa_new_registered_views']==[])
    for v in vv:
        key=v['view_id']
        check(key+' registered object',v['object_id'] in fixed)
        check(key+' individual caption basis',v['registration_basis']=='individual object caption in original publication')
        pdf=ROOT/v['pdf_path'];parent=ROOT/v['parent_image_path'];crop=ROOT/v['crop_path']
        check(key+' PDF hash',sha(pdf)==v['pdf_sha256'])
        check(key+' parent hash',sha(parent)==v['parent_image_sha256'])
        check(key+' crop hash',sha(crop)==v['crop_sha256'])
        original=Image.open(parent); actual=Image.open(crop).convert('RGB')
        check(key+' parent dimensions',list(original.size)==v['parent_image_dimensions'])
        check(key+' parent mode',original.mode==v['parent_mode'])
        box=v['crop_bounds_xyxy'];w,h=original.size
        check(key+' crop bounds',0<=box[0]<box[2]<=w and 0<=box[1]<box[3]<=h)
        expected=original.convert('RGB').crop(box)
        check(key+' crop pixels',expected.size==actual.size and expected.tobytes()==actual.tobytes())
        check(key+' crop dimensions',list(actual.size)==v['crop_dimensions'])
        with fitz.open(pdf) as d:
            p=d[v['pdf_page']-1];im=d.extract_image(v['xref'])
            check(key+' embedded image bytes',im['image']==parent.read_bytes())
            check(key+' original page image bounds',list(p.get_image_rects(v['xref'])[0])==v['source_page_bbox_points'])
        if v['source_id']=='cisi1':check(key+' Arabic page mapping',v['printed_page']+36==v['pdf_page'])
        check(key+' local-only pixels',v['rights_status']=='pixels local-only; authored description selected')
        low=v['separated_cut_lower_bound_in_selected_zone']
        check(key+' cut floor field',low is None or isinstance(low,int) and low>=0)
    alt=json.loads((HERE/'alternative-scan-check.json').read_text(encoding='utf8'))
    check('alternative scan seven-page scope',len(alt['checked_pages'])==7)
    check('alternative page counts',alt['old_pages']==862 and alt['alternative_pages']==431)
    old=fitz.open(ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf')
    new=fitz.open(ROOT/'data/raw/2026-10-02-source-recovery/physical-views/cisi1-rarebooks-scan.pdf')
    for row in alt['checked_pages']:
        n=row['pdf_page'];a=old.extract_image(old[n-1].get_images()[0][0])['image'];b=new.extract_image(new[n-1].get_images()[0][0])['image']
        check(f'alternative PDF{n} native bytes equal',a==b)
        check(f'alternative PDF{n} saved hashes',hashlib.sha256(a).hexdigest()==row['sha256_old']==row['sha256_alternative'])
    loc=json.loads((HERE/'record-locators.json').read_text(encoding='utf8'))
    prior=json.loads((ROOT/'experiments/2026-10-02-connections-and-priority/harappa-short-records/main-v2/source-locators.json').read_text(encoding='utf8'))
    ledger=json.loads((ROOT/'experiments/2026-10-02-six-hour/harappa-object-frame/figure4-caption-ledger.json').read_text(encoding='utf8'))
    check('eight Harappa request records',len(loc['harappa'])==8)
    for r in loc['harappa']:
        p=next(x for x in prior['registered_crop_locators'] if x['target_id'].replace('-','')==r['object_id'])
        s=next(x for x in ledger['registrations'] if x['specimen']==r['specimen'])
        check(r['object_id']+' prior join',r['registration']==p['registration'] and r['specimen']==p['specimen'])
        check(r['object_id']+' original caption join',r['registration']==s['literal'])
        group=2 if r['object_id']=='H2239' else 3
        check(r['object_id']+' production group',s['published_manufacturing_group']==group)
        check(r['object_id']+' no acquired photograph',r['new_registered_photograph'] is False)
    file_check(loc['lothal']['detailed_rows_local'],'local eight-row catalogue ledger')
    basic=json.loads((ROOT/loc['lothal']['detailed_rows_local']['path']).read_text(encoding='utf8'))
    check('basic-data target membership',{r['object_id'] for r in basic['rows']}==fixed)
    check('basic-data museum identifiers',all(r['museum_registration'].startswith('LTH SRG ') for r in basic['rows']))
    groups=json.loads((ROOT/'experiments/2026-10-02-six-hour/lothal-physical-use/graphic-coverage/results.json').read_text(encoding='utf8'))['groups']
    for gid,targets in [('G01',{'L190','L193','L206'}),('G02',{'L161','L162','L163','L165','L168'})]:
        g=next(x for x in groups if x['group_id']==gid)
        check(gid+' unchanged member joins',targets<={x.replace('-','') for x in g['object_ids']})
    packet=json.loads((HERE/'request-packet.json').read_text(encoding='utf8'))
    file_check(packet['packet'],'unsent local observation packet')
    check('request not sent',packet['status']=='locally saved; unsent')
    second=json.loads((HERE/'second-reading.json').read_text(encoding='utf8'))
    check('second reading two native panels',second['input_views']==['L190-cisi1-D','L190-cisi1-F'])
    check('second reading informed',second['reader_information'].endswith('not blinded'))
    q=json.loads((HERE/'search-log.json').read_text(encoding='utf8'))
    check('query accounting',q['query_count']==sum(len(x['queries']) for x in q['query_batches'])==37)
    for p in HERE.glob('*.py'):
        ast.parse(p.read_text(encoding='utf8'));check(p.name+' syntax',True)
    for p in HERE.glob('*.md'):
        text=p.read_text(encoding='utf8')
        for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',text):
            target=m.group(1).strip('<>')
            if re.match(r'^https?://|^#',target):continue
            check(p.name+' local link '+target,(p.parent/target.split('#')[0]).resolve().exists())
        flags=re.findall(r'\b(?:delve|foster|leverage|game.changer|groundbreaking|revolutionary|not merely|not simply)\b',text,re.I)
        check(p.name+' editorial phrase screen',not flags,flags)
    result={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope':'Manual source-byte, native-crop, registration, accounting, link and syntax checks. Caption/photo observations were separately inspected; this checker does not infer physical topology.',
        'verifier_sha256':sha(Path(__file__)),
        'checked':len(checks),'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),
        'counts':{'newly_acquired_pdfs':5,'total_source_pdf_paths':8,'accepted_publication_panels':19,
            'lothal_objects':8,'catalogue_panels':15,'catalogue_object_face_codes':14,'colour_panels':4,
            'new_registered_harappa_views':0,'complete_marked_surfaces':0,'alternative_identical_page_images':7},
        'checks':checks}
    out=HERE/args.out
    if not out.exists():out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ['checked','passed','failed','counts']}))
    if result['failed']:raise SystemExit(1)


if __name__=='__main__':main()
