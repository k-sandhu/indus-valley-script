"""Record source provenance, plate coverage and independently checked aggregates."""
import csv,hashlib,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,x):
 with p.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False)
frame=json.loads((HERE/'frame.json').read_text()); annotations=json.loads((HERE/'annotations.json').read_text())
source_specs=[
 ('Laursen2010','Steffen Terp Laursen',2010,"The westward transmission of Indus Valley sealing technology: origin and development of the ‘Gulf Type’ seal and other administrative technologies in Early Dilmun, c.2100–2000 BC",'data/raw/2026-10-06-chronology-region/review-response-sources-2026-10-07-v1/laursen2010.pdf','https://www.harappa.com/sites/default/files/pdf/The_westward_transmission_of_Indus_Valle.pdf','Table1 printed pp100–102, Fig8 p109, Fig9 p111, Fig10 p112, Fig11 p116; contextual discussion pp120–122'),
 ('Gadd1932','C. J. Gadd',1932,'Seals of ancient Indian style found at Ur','data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad/gadd1932.pdf','https://ignca.gov.in/Asi_data/33779.pdf','offprint pp13–14 (PDF24–25), PlateIII (PDF26)'),
 ('CISI1','J. P. Joshi and Asko Parpola (eds)',1987,'Corpus of Indus Seals and Inscriptions 1: Collections in India','research/literature/sources/joshi_parpola_1987_cisi1.pdf',None,'PDF136,137,161,371,388; held scan page identities checked by independent review'),
 ('CISI2','Sayid Ghulam Mustafa Shah and Asko Parpola (eds)',1991,'Corpus of Indus Seals and Inscriptions 2: Collections in Pakistan','data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf',None,'PDF214; held scan locator from image index; checked by independent review')]
import fitz
sources=[]
for ident,authors,year,title,path,url,loc in source_specs:
 p=ROOT/path
 sources.append(dict(id=ident,authors=authors,year=year,title=title,path=path,url=url,locators=loc,bytes=p.stat().st_size,sha256=sha(p),format='PDF',pages=len(fitz.open(p)),access='read-only reuse of held source on 20 October 2026; original acquisition is preserved in predecessor packages',rights_status='rights-unverified',rights_observation='No redistribution permission established by this audit; source PDF, crops, extracted text and detailed derivatives remain local-only.'))
put(HERE/'source-manifest.json',dict(sources=sources,transformations=['Laursen PDF pages rendered locally at 2x; UTF-8 extraction local-only','Gadd contact sheet and PDF24–26 rendered locally','Source joins and aggregate eligibility observations tracked; no full sign strings copied']))
plate=[]
for n in list(range(1,29))+[56]:
 status='drawing in impression polarity; Wells-code agreement unresolved'
 if n==28:status='Linear-Elamite label in Figure11; outside Indus-string comparison'
 if n==11:status='pseudo-script identified in text p99; no forced code string'
 if n==56:status='two V-shaped fill marks in iconographic field, text p99; no assumed continuous text'
 plate.append(dict(table1_number=n,figure11_printed_page=116,figure11_pdf_page=21,status=status,grey_missing_interval=n in [4,6,7,10,12,14,17,18,19],joined_records=[r['record_id'] for r in annotations if r['table1_number']==n]))
put(HERE/'plate-observations.json',plate)
put(HERE/'audit-summary.json',dict(frame_faces=len(frame),frame_families=len({r['family'] for r in frame}),indexed_image_faces=sum(bool(r['images']) for r in frame),indexed_images=sum(len(r['images']) for r in frame),faces_without_indexed_image=sum(not r['images'] for r in frame),secure_table1_join_faces=sum(r['table1_number'] is not None for r in annotations),secure_table1_objects=len({r['table1_number'] for r in annotations if r['table1_number'] is not None}),figure11_entries=len(plate),figure11_indus_or_indus_related_entries=28,figure11_linear_elamite_entries=1,code_verified_foreign_faces=0,source_supported_form_exclusions=['2977.1'],uncertain_text_exclusion_sensitivity=['2913.1'],new_calendar_dated_south_asian_objects=0,scope='complete within fixed export SEAL:C frame and complete Figure11 plate; no worldwide completeness claim'))
# An independent expression checks all headline point means against their old inputs.
old=ROOT/'experiments/2026-10-12-published-claim-tests/foreign-finds/run-2026-10-12/objects.csv'
w=[r for r in csv.DictReader(old.open()) if r['group']=='west_asia' and r['object_type']=='SEAL:C' and r['scorable']=='True' and r['record_id']!='6000.1']
s=[json.loads(l) for l in (ROOT/'data/raw/2026-10-12-decipherment-claim-tests/foreign-finds/run-2026-10-12/peripheral_rows.jsonl').read_text().splitlines()]
s=[r for r in s if r.get('peripheral_group')=='south_asian_round' and r['object_type']=='SEAL:C' and r['scorable']]
results=json.loads((HERE/'sensitivity.json').read_text())
checks={}
for key,excluded in [('circular_only',[]),('circular_exclude_tablet',['2977.1']),('circular_exclude_tablet_and_uncertain_composition',['2977.1','2913.1'])]:
 ss=[r for r in s if r['record_id'] not in excluded]
 value=sum(float(r['u_surprisal']) for r in w)/len(w)-sum(r['u_surprisal'] for r in ss)/len(ss)
 checks[key]=abs(value-results['variants'][key]['difference'])<1e-12
checks['annotation_hash_unchanged']=sha(HERE/'annotations.json')==json.loads((HERE/'annotation-freeze.json').read_text())['annotations_sha256']
checks['frame_hash_unchanged']=sha(HERE/'frame.json')==json.loads((HERE/'frame-freeze.json').read_text())['frame_sha256']
checks['one_to_one_records']=len({r['record_id'] for r in annotations})==len(frame)==33
checks['duplicate_witness_same_table1_object']=next(r for r in annotations if r['record_id']=='3898.1')['table1_number']==next(r for r in annotations if r['record_id']=='6000.1')['table1_number']
put(HERE/'author-verification.json',dict(author='GPT-6.1-Sol / Codex desktop',tier='author verification, not independent reproduction',checks=checks,passed=all(checks.values()),source_review='Separate blind reviewer package; its source observations are independently authored. Full component-out inference beyond family removal requires adjudicated aliases.',code_hashes={p.name:sha(p) for p in [HERE/'audit.py',HERE/'sensitivity_v2.py',HERE/'finish.py']}))
print(json.dumps(json.loads((HERE/'audit-summary.json').read_text()),indent=2))
