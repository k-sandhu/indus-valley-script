import json,hashlib,re
from decimal import Decimal
from pathlib import Path
P=Path('experiments/2026-10-24-object-identity-pass2');R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-object-identity-pass2')
assert not (P/'validation-v1.json').exists(), 'Frozen validation output exists; choose new version'
def load(n):return json.loads((R/n).read_text())
d=load('bridge-decisions-v1.json');t=load('target-inventory-v1.json');c=load('candidate-corpus-faces-v1.json');checks=[]
assert [x['row_id'] for x in d]==[f'PCF-DHV-{n:03d}' for n in range(5,15)];checks.append('frozen complete ten-case block')
def dec(s):
 m=re.match(r'\s*([0-9]+(?:\.[0-9]+)?)',str(s or ''));return Decimal(m[1]) if m else None
for row in d:
 expected=next(x for x in t if x['row_id']==row['row_id'])['local_family_ids'].split('|');assert {x['family_id'] for x in row['comparisons']}==set(expected);assert not row['physical_merge'] and not row['confirmation_eligibility'];checks.append('candidate preservation '+row['row_id'])
 assert row['registration'] in (R/(row['row_id']+'-catalogue.txt')).read_text();checks.append('primary accession text binding '+row['row_id'])
 exact=[]
 for cc in c:
  if cc['object_family_id'] not in expected:continue
  mm=row['measurements'];md=cc['metadata']
  if mm and all(dec(md.get(k))==dec(mm.get(v)) and dec(md.get(k)) is not None for k,v in [('h','h'),('v','v'),('th','body_thickness')]):exact.append(cc['object_family_id'])
 assert set(exact)==set(row['exact_triplet_priority_families']);checks.append('Decimal measurement comparison '+row['row_id'])
manifest=json.loads((P/'source-manifest-v1.json').read_text())
for rec in manifest['sources']+manifest['new_local_artifacts']:
 p=Path(rec['physical_path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'];checks.append('source/artifact hash '+p.name)
assert len({x['object_family_id'] for x in c})==62;assert sum(len(x['comparisons']) for x in d)==274;checks.extend(['62 candidate families','274 candidate edges'])
(R/'validation-detail-v1.json').write_text(json.dumps({'checks':checks,'passed':True},indent=2)+'\n')
(P/'validation-v1.json').write_text(json.dumps({'passed':True,'author_validation':True,'independent_review':False,'checks_passed':len(checks),'failed_checks':0,'methods':['frozen population accounting','candidate edge equality','accession text binding','independent Decimal comparison','SHA256 checks'],'detail_logical_path':'data/raw/2026-10-24-object-identity-pass2/validation-detail-v1.json'},indent=2)+'\n');print('Author checks passed:',len(checks))
