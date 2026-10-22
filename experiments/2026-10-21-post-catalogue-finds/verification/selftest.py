"""Check audit arithmetic, saved records and immutable inputs."""
import ast
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,interval,project,csvrows,save

def main():
    checks=[]
    def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'detail':detail})
    check('Exact interval with no successes',abs(interval(0,31)[1]-(1-.025**(1/31)))<1e-12)
    check('Exact interval with all successes',abs(interval(25,25)[0]-.025**(1/25))<1e-12)
    q,_=project('{"ignored":[{"discarded":"skip"}],"site":"Test","metadata":{"ignored":{"discarded":[1,2]},"type":"SEAL"},"object_family_id":1}')
    check('Selective identity decoder',q=={'site':'Test','metadata':{'type':'SEAL'},'object_family_id':1})
    malformed=[];validated=[]
    for p in sorted(OUT.rglob('*')):
        if not p.is_file() or p.name=='selftest-4.json':continue
        if p.suffix=='.json':
            try:json.loads(p.read_text(encoding='utf-8-sig'));validated.append(str(p.relative_to(OUT)))
            except (UnicodeDecodeError,json.JSONDecodeError):malformed.append(str(p.relative_to(OUT)))
        elif p.suffix=='.csv':
            with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,strict=True))
            if not rows or any(len(r)!=len(rows[0]) for r in rows):malformed.append(str(p.relative_to(OUT)))
            else:validated.append(str(p.relative_to(OUT)))
        elif p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'),filename=p.name)
    check('Complete saved CSV and JSON records',not malformed,malformed)
    freeze=json.loads((OUT/'blind-freeze.json').read_text(encoding='utf-8'))
    check('Original blind freeze unchanged',hashlib.sha256((OUT/freeze['file']).read_bytes()).hexdigest()==freeze['sha256'])
    check('Blind sample size',len(csvrows(OUT/'blind-assignments.csv'))==60)
    check('Blind field comparison slots',len(csvrows(OUT/'blind-sample.csv'))==600)
    check('Omission sample size',len(csvrows(OUT/'omission-sample.csv'))==40)
    rev=json.loads((OUT/'input-revision.json').read_text(encoding='utf-8'))
    drift=[]
    for r in rev['inputs']:
        if hashlib.sha256((ROOT/r['input']).read_bytes()).hexdigest()!=r['sha256']:drift.append(r['input'])
        check('Revised snapshot hash '+Path(r['snapshot']).name,hashlib.sha256((ROOT/r['snapshot']).read_bytes()).hexdigest()==r['sha256'])
    check('Live inputs still equal the revised snapshot',not drift,drift)
    original=json.loads((OUT/'sampling.json').read_text(encoding='utf-8'))
    for name,sha in original['inputs'].items():
        if Path(name).suffix=='.md':check('Frozen protocol hash '+Path(name).name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha)
    count=json.loads((OUT/'count-check.json').read_text(encoding='utf-8'))
    check('All site cells reproduce',not count['differences'])
    check('Applied decisions reproduce',not count['decision_application_differences'])
    corpus=json.loads((OUT/'corpus-access.json').read_text(encoding='utf-8'))
    check('Pinned corpus identity',corpus['sha256'].startswith('1220f559'))
    exposure=json.loads((OUT/'exposure-incidents.json').read_text(encoding='utf-8'))
    check('Exposure failure recorded',exposure['confirmed_filter_failure'] and exposure['images_opened']==0)
    status={'passed':all(r['passed'] for r in checks),'checks':checks,'validated_record_files':validated,'interpretation':'These checks validate the audit implementation and saved records. Source-review objections and unresolved inventories remain reported research outcomes.'}
    save('selftest-4.json',status)
    print('SELFTEST',status['passed'],len(checks),'checks; record files',len(validated))

if __name__=='__main__':main()
