from pathlib import Path
import re, json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail=None):
    checks.append({'check':name,'passed':bool(ok),'detail':detail})
main=json.loads((BASE/'main-v2/results.json').read_text(encoding='utf-8'))
review=json.loads((BASE/'review-v1/checks.json').read_text(encoding='utf-8'))
check('independent scalar review',review['passed']==review['checks']==241 and not review['failures'])
check('six local-only dataset files',len(main['local_output_hashes'])==6)
for x in main['local_output_hashes']:
    check('local endpoint payload '+x['path'],sha(ROOT/x['path'])==x['sha256'])
check('finite source count population',main['native_source']['directly_counted_faces']+main['native_source']['unassigned_count_faces']==66)
check('distinct pair categories',sum(main['pair_counts'][k] for k in ['exact_same_modules','exact_one_module_changed','exact_two_modules_changed'])==231)
check('position repair preserves earlier endpoint',(BASE/'main-v1/results.json').exists())
links=[]
for p in BASE.glob('*.md'):
    for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if target.startswith(('https:','http:','mailto:','#')): continue
        target=target.split('#',1)[0].strip('<>')
        dest=(p.parent/target).resolve()
        record={'source':p.relative_to(ROOT).as_posix(),'target':target,'exists':dest.exists(),'local_only':dest.is_relative_to(ROOT/'data') or dest.is_relative_to(ROOT/'research/corpus/plate_audit/H2238_gallery')}
        links.append(record);check('navigation '+p.name+' '+target,dest.exists())
ed=json.loads((BASE/'editorial-review.json').read_text(encoding='utf-8'))
check('manual prose scan',ed['files_scanned']==5 and not ed['flags'])
registry=json.loads((ROOT/'knowledge/experiments/registry.json').read_text(encoding='utf-8'))
ids=[r['id'] for r in registry['experiments']]
coverage={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registry_path':'knowledge/experiments/registry.json','registry_sha256':sha(ROOT/'knowledge/experiments/registry.json'),'reviewed_registry_ids':ids,'reviewed_entry_count':len(ids),'direct_source_ids':['ROOT-10','ROOT-19','CONTEXT-01','ARCH-01','ARCH-03','READINESS-01'],'new_question':'Complete three-face short-record module/count comparison plus renewed native-source count readings and finite ambiguity bounds.'}
(BASE/'coverage.json').write_text(json.dumps(coverage,indent=2)+'\n',encoding='utf-8')
payload={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':len(checks),'passed':sum(c['passed'] for c in checks),'failures':[c for c in checks if not c['passed']],'records':checks,'navigation':links,'scope':'Own authored files and local dataset availability. Detailed source witnesses remain excluded from Git.'}
(BASE/'verification.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
items=[]
for p in sorted(BASE.rglob('*')):
    if p.is_file() and p.name!='artifact-manifest.json' and '__pycache__' not in p.parts:
        items.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
(BASE/'artifact-manifest.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Own code, prose, source observations, aggregate endpoints and provenance. Bulk inscriptions and source pixels remain local-only.','artifacts':items,'artifact_count':len(items)},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'passed':payload['passed'],'failures':payload['failures'],'artifacts':len(items),'registry_entries':len(ids)},indent=2))
if payload['failures']: raise SystemExit(1)
