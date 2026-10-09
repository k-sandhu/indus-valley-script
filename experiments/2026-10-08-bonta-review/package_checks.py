"""Check deliverables, local links, annotation structure and auxiliary replays."""
from pathlib import Path
import argparse, collections, hashlib, json, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='package-checks.json');a=ap.parse_args()
    dest=OWN/a.output
    if dest.exists():raise FileExistsError(dest)
    checks=[]
    def check(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
    for name in ['README.md','PROTOCOL.md','PROTOCOL-registered.md','REPORT.md','RETROSPECTIVE.md','sources.json','registry-entry.json','claims.jsonl','claims.md','FILES.json']:
        check('required '+name,(OWN/name).is_file())
    for name in ['validation-audit','distribution-sensitivities']:
        check(name+' replay',sha(OWN/(name+'.json'))==sha(OWN/(name+'-replay.json')))
    parsed=[]
    for p in OWN.rglob('*.json'):
        try:read(p);parsed.append(p.name)
        except Exception as e:check('JSON '+p.name,False,str(e))
    check('JSON parses',len(parsed)>0,{'files':len(parsed)})
    rows=[json.loads(z) for z in (OWN/'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    coverage=read(OWN/'ledger-coverage.json')
    check('claim coverage count',len(rows)==coverage['claim_records'])
    check('claim coverage types',dict(collections.Counter(r['type'] for r in rows))==coverage['by_type'])
    unresolved=read(OWN/'run-2026-10-08-v1/concordance.json')
    check('no invented Helsinki codes',all(not r['helsinki1979_confirmed_codes'] for r in unresolved['mappings']))
    links=[]
    for p in OWN.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if target.startswith(('http://','https://','#')):continue
            target=target.split('#')[0]
            if target:links.append((p.name,target,(p.parent/target).exists()))
    check('local Markdown links',all(v for _,_,v in links),{'checked':len(links),'missing':[(p,t) for p,t,v in links if not v]})
    v=read(OWN/'verification-v2.json')
    check('independent numerical verification',v['status']=='Verified computation' and v['passed']==v['total']==54)
    inputs=read(OWN/'input-checks.json')
    check('supplied page derivative',inputs['page_derivative_identical'] and inputs['page_segments']==260)
    check('caption duration',inputs['captions']==12 and inputs['caption_duration_seconds']==33133)
    nature=[p for p in inputs['pdf_payload_checks'] if 'mukhopadhyay' in p['path']]
    check('interstitial recorded',bool(nature) and all(not p['has_PDF_magic'] for p in nature))
    registry=read(OWN/'registry-entry.json')
    fields={'id','theme','status','question','outcome','challenge','remedy','evidence','retry_when'}
    check('registry schema fields',set(registry)==fields)
    check('registry evidence links',all((ROOT/p).exists() for p in registry['evidence']))
    r=subprocess.run([sys.executable,'tools/review_prose.py','--path','experiments/2026-10-08-bonta-review','--no-write'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    prose=json.loads(r.stdout);check('manual prose scan',r.returncode==0 and not prose['flags'],prose)
    answer={'status':'Verified computation' if all(c['passed'] for c in checks) else 'Failed','passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,
      'scope':'Package structure and arithmetic checks; source sampling and expert transcription remain required.'}
    dest.write_text(json.dumps(answer,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in answer.items() if k!='checks'},indent=2))
    if answer['status']=='Failed':
        print(json.dumps([c for c in checks if not c['passed']],indent=2));raise SystemExit(1)

if __name__=='__main__':main()
