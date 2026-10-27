from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
ROOT=P.parents[1]
R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-pass2')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/'source-manifest-v2.json').read_text(encoding='utf8'))
ledger=json.loads((R/'view-ledger-v1.json').read_text(encoding='utf8'))
checks=[]
def check(k,v):checks.append({'check':k,'pass':bool(v)})
check('five targets',len(ledger['targets'])==5)
check('unique targets',len({x['object'] for x in ledger['targets']})==5)
check('ledger hash',sha(R/'view-ledger-v1.json')==m['ledger_sha256'])
check('exposure hash',sha(R/'exposure-v1.json')==m['exposure_sha256'])
check('artifact manifest hash',sha(R/'artifact-manifest-v1.json')==m['artifact_manifest_sha256'])
check('D storage junction',str((ROOT/'data/raw').resolve()).lower().startswith('d:'))
check('candidate drawing not confirmed photograph',ledger['additional_witnesses'][0]['admission'].startswith('candidate'))
for s in m['sources']:
    check('source hash '+s['id'],sha(ROOT/s['logical_path'])==s['sha256'])
    if s['id']=='cisi1':check('CISI page coordinates',[n-36 for n in s['consulted_pdf_pages']]==s['printed_pages'])
for f in json.loads((R/'artifact-manifest-v1.json').read_text(encoding='utf8')):
    check('artifact '+f['path'],sha(R/f['path'])==f['sha256'])
result={'schema_version':'1.0','verification_tier':'submitted','passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks}
with (P/'validation-v1.json').open('x',encoding='utf8') as h:json.dump(result,h,indent=2)
print(result['passed'],'passed;',result['failed'],'failed')
raise SystemExit(bool(result['failed']))
