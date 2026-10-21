import json, pathlib, hashlib, re, datetime
import fitz
R=pathlib.Path('.'); P=R/'experiments/2026-10-20-farmana-reserve-review'; L=R/'data/raw/2026-10-20-farmana-reserve-review'; A=R/'data/raw/2026-10-20-fresh-test-collection'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log={'reviewer':'GPT-6.1-Sol / Codex desktop / reserve_identity_review','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'independent acquisition reviewer','access':[],'prediction_or_model_files_opened':False,'bench_run':False,'orientation_restriction':'README, INDEX, global experiment registry and DATA/model-bearing orientation withheld under explicit blind-review instruction. Acquisition protocol and retrospective read. REPRODUCING opening read for procedure only.'}
def access(path,operation):
 log['access'].append({'path':str(path),'operation':operation}); (L/'ACCESS-LOG.json').write_text(json.dumps(log,indent=2))
manifest=json.loads((R/'experiments/2026-10-20-fresh-test-collection/reservation-manifest.json').read_text())
checks=[]
for key in ['local_object_register','payload_hash_manifest','access_log']:
 x=manifest[key]; p=R/x['path']; access(p,'hash bytes'); checks.append({'path':str(p),'match':sha(p)==x['sha256']})
access(A/'payload-hashes.json','read hash entries only')
for x in json.loads((A/'payload-hashes.json').read_text())['files']:
 p=R/x['path']; access(p,'hash bytes only'); checks.append({'path':str(p),'match':p.exists() and sha(p)==x['sha256'],'bytes_match':p.exists() and p.stat().st_size==x['bytes']})
access(A/'objects.jsonl','identity metadata and source coordinates; no sign decoding')
rows=[json.loads(l) for l in (A/'objects.jsonl').read_text().splitlines()]
access(A/'farmana.pdf','bounded page text for labels/captions/context, no sign decoding'); d=fitz.open(A/'farmana.pdf')
out=[]; pages=set()
for r in rows:
 n=r['source_identifier']; num=n.removeprefix('S-'); cc=[]
 for c in r['source_coordinates']:
  pg=c['pdf_page']; pages.add(pg); t=d[pg-1].get_text(); lines=t.splitlines()
  cc.append({'pdf_page':pg,'printed_page_matches':str(c.get('printed_page','')) in lines,'identifier_present':bool(re.search(r'(?<!\d)'+re.escape(num)+r'(?!\d)',t)),'captions':[l for l in lines if l.startswith('Figure') or l.startswith('Table')]})
 ww=[]
 for w in r['image_witnesses']:
  p=A/w['local_page_image']; ww.append({'kind':w['kind'],'pdf_page':w['pdf_page'],'exists':p.exists(),'sha256':sha(p) if p.exists() else None})
 out.append({'object_id':r['object_id'],'source_identifier':n,'disposition':r['disposition'],'coordinates':cc,'images':ww,'trench':r.get('trench'),'phase':r.get('phase'),'source_conflict':r.get('source_conflict'),'physical_faces':'unknown; retained views do not establish complete physical coverage','dimensions':r.get('dimensions',{'value':None,'value_status':'not-in-object-register; source-table-review-required'})})
(L/'identity-checks.json').write_text(json.dumps(out,indent=2))
for pg in sorted(pages|{231,232,233,385,386,387,388,389}):
 access(f'{A}/farmana.pdf#page={pg}','complete page text processed; caption/context review')
 t=d[pg-1].get_text(); (L/f'page-{pg:04d}.txt').write_text(t)
(P/'hash-verification.json').write_text(json.dumps({'checks':checks,'checked':len(checks),'failures':sum(not x['match'] for x in checks)},indent=2))
print(json.dumps({'hash_checks':len(checks),'hash_failures':sum(not x['match'] for x in checks),'rows':len(out),'pages':sorted(pages),'identifier_failures':[x['object_id'] for x in out if not all(c['identifier_present'] for c in x['coordinates'])],'local_identity_checks':str(L/'identity-checks.json')}))
