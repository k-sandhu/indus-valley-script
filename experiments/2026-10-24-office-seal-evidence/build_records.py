"""Validate the preserved source-relation ledger without exporting its rows."""
from pathlib import Path
import hashlib,json
PKG=Path(__file__).resolve().parent
ROOT=PKG.parents[1]
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-evidence')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((PKG/'source-manifest-v1.json').read_text(encoding='utf8'))
a=json.loads((RAW/'relations-v1.json').read_text(encoding='utf8'))['relations']
checks=[]
def check(name,value):checks.append({'check':name,'pass':bool(value)})
check('raw junction targets D',str((ROOT/'data/raw').resolve()).lower().startswith('d:'))
check('ledger digest',sha(RAW/'relations-v1.json')==manifest['detail_ledger']['sha256'])
check('unique assertion ids',len({r['assertion_id'] for r in a})==len(a))
check('assertions carry status source observer',all(all(k in r for k in ['value_status','source_id','observer','annotation_version']) for r in a))
check('twelve elephant cohort aliases',sum(r['predicate']=='excavation_alias' and r['subject'] in [f'L-{i}' for i in range(161,173)] for r in a)==12)
check('competing L164 supports preserved',sum(r['subject']=='L-164' and r['predicate']=='attachment_interpretation' for r in a)==2)
check('M895 remains unresolved',any(r['subject']=='M-895' and r['value_status']=='conflicting' for r in a))
check('deposit counts remain source separated',sum(r['subject']=='warehouse sealing deposit' and r['predicate']=='count' for r in a)==2)
for s in manifest['sources']:
 p=ROOT/s['logical_path'];check('source hash '+s['id'],sha(p)==s['sha256'])
for f in json.loads((RAW/'artifact-manifest-v1.json').read_text(encoding='utf8')):
 check('artifact hash '+f['path'],sha(RAW/f['path'])==f['sha256'])
result={'schema_version':'1.0','verification_tier':'submitted','checks':checks,'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'record_rows_exported':0}
out=PKG/'validation-v1.json'
with out.open('x',encoding='utf8') as h:json.dump(result,h,indent=2)
print(result['passed'],'passed;',result['failed'],'failed')
raise SystemExit(bool(result['failed']))
