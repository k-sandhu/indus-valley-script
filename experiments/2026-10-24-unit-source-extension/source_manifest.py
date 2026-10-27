"""Write source hashes without publishing detailed annotations."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PKG=Path(__file__).resolve().parent;RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension')
def entry(p):
 p=Path(p);return {'physical_path':str(p.resolve()),'logical_path':('data/raw/2026-10-24-unit-source-extension/'+p.relative_to(RAW).as_posix()) if p.is_relative_to(RAW) else p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
manifest=json.loads((ROOT/'data/MANIFEST.json').read_text(encoding='utf8'))
def find(x):
 if isinstance(x,dict):
  if x.get('id') in ['cisi-1','cisi-2']:yield x
  for v in x.values():yield from find(v)
 elif isinstance(x,list):
  for v in x:yield from find(v)
sources=[]
for r in find(manifest):
 sources.append({'id':r['id'],'title':r['title'],'rights':r['rights'],'url':r['fetch']['url'],'access':'held witness; rendering during this run','witness':entry(ROOT/r['local_paths'][0])})
flyer=ROOT/'data/raw/2026-10-12-data-inventory/web-checks-v1/witnesses/indology-2020-01-16-cisi-3-2-flyer.pdf'
sources.append({'id':'cisi-publisher-flyer','title':'The Corpus of Indus Seals and Inscriptions (CISI)','access':'held publisher flyer, entire one-page text extracted and displayed','rights':{'status':'rights-unverified'},'witness':entry(flyer),'supports':'CISI 3.1 (2010), ISBN 978-951-41-1040-5; CISI 3.2 (2019, released January 2020), ISBN 978-951-41-1134-1; Chanhu-daro in part 2','source_url_status':'held acquisition basename; signed attachment URL not republished'})
sources.append({'id':'CISI31-bibliography','title':'Corpus of Indus Seals and Inscriptions: Volume 3: New material, untraced objects, and collections outside India and Pakistan, Part 1: Mohenjo-daro and Harappa','editors':['Asko Parpola','B. M. Pande','Petteri Koskikallio'],'year':2010,'url':'https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-volume-3-new-material-untr/','access':'web search snippet displayed; direct retrieval HTTP 403; no plates accessed','rights':{'status':'rights-unverified'}})
corrections={'misnamed_held_source':{'path':'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/cisi3-stream.pdf','bytes':12058624,'pages_opened_by_pymupdf':0,'identity':'incomplete download from CISI 1 URL, not a CISI 3 witness','source_url':'https://ignca.gov.in/Asi_data/76884.pdf','comparison':'same URL and advertised 31,508,998 bytes as held CISI 1 manifest'},'new_legacy_route':json.loads((RAW/'retrieval.json').read_text(encoding='utf8')),'incorrect_bibliographic_url':{'url':'https://list.indology.info/pipermail/indology/2020-January/051630.html','actual_title':'[INDOLOGY] Announcement of a Fellowship for PhD study in Buddhism at Leiden','disposition':'unrelated response, excluded from CISI source evidence; original request record preserved'},'confirmed_bibliography':'held publisher flyer used for volume scope and ISBNs'}
(RAW/'route-corrections.json').write_text(json.dumps(corrections,indent=2)+'\n',encoding='utf8')
out={'producing_code':[entry(p) for p in PKG.glob('*.py')], 'schema_version':'1.0','created_utc':datetime.now(timezone.utc).isoformat(),'sources':sources,'new_local_files':[entry(p) for p in RAW.rglob('*') if p.is_file()],'rights_rule':'new images, records and detailed derivatives local-only; source rights unverified','correction_summary':'76884.pdf identifies CISI 1; unrelated Indology response excluded; publisher flyer fixes volume scopes','frozen_artifacts':[entry(ROOT/p) for p in ['experiments/2026-10-20-seal-legend-units/FROZEN-v2.json','experiments/2026-10-20-seal-legend-units/predictions.json','bench/spent.json']]}
with (PKG/'SOURCE-MANIFEST-v2.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
print('sources',len(sources),'new local files',len(out['new_local_files']))
