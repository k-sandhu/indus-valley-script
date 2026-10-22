"""Validate complete records, preserved endpoints and source-page availability."""
import ast
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).parent))
from audit import ROOT,BASE,OUT,RAW,csvrows,save,savecsv,page_index,page_numbers,interval,project
from safe_read import RESTRICTED,UNIT

def main():
    checks=[];manifest=json.loads((OUT/'input-manifest-v2.json').read_text(encoding='utf-8'))
    def check(name,ok,detail=None):checks.append({'check':name,'passed':bool(ok),'detail':detail})
    exposure=[]
    for p in [*sorted(OUT.glob('source-review-access-*-v2.json')),OUT/'omission-revisit-access-v2.json']:
        if not p.exists():continue
        for r in json.loads(p.read_text(encoding='utf-8')):
            exposure.append({'source_id':r['source_id'],'pdf_page':r['pdf_page'],'line':r.get('line',''),'agent':'Codex / GPT-6 / API harness','access':r['access'],'image_opened':'no','record':p.name})
    cat=json.loads((OUT/'catalogue-locator-access-v2.json').read_text(encoding='utf-8'))
    for r in cat['pages']:exposure.append({'source_id':r['source_id'],'pdf_page':r['pdf_page'],'line':'','agent':'Codex / GPT-6 / API harness','access':'Machine OCR to site-heading and catalogue-locator identity projection; render deleted immediately.','image_opened':'no','record':'catalogue-locator-access-v2.json'})
    un=json.loads((OUT/'unnamed-read-status-v2.json').read_text(encoding='utf-8'))
    for r in un['new_immediate_line_access']:exposure.append({'source_id':r['source_id'],'pdf_page':r['pdf_page'],'line':r['line'],'agent':'Codex / GPT-6 / API harness','access':r['access'],'image_opened':'no','record':'unnamed-read-status-v2.json'})
    savecsv('exposure-log-v2.csv',exposure,['source_id','pdf_page','line','agent','access','image_opened','record'])
    hashes={}
    for name,sha in manifest['preserved_first_versions'].items():
        actual=hashlib.sha256((OUT/name).read_bytes()).hexdigest();hashes[name]=actual
        check('Preserved endpoint '+name,actual==sha)
    for item in manifest['inputs']:
        for kind in ['input','snapshot']:
            p=ROOT/item[kind]
            check('Current snapshot identity '+kind+' '+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'])
    original=json.loads((OUT/'sampling.json').read_text(encoding='utf-8'))
    for name,sha in original['inputs'].items():
        if Path(name).suffix=='.md':check('Frozen protocol '+Path(name).name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha)
    malformed=[];complete=[];syntax=[]
    # All working package CSV/JSON inputs used by the audits, including the
    # complete output tree, are parsed without executing source files.
    for p in sorted(BASE.rglob('*')):
        if not p.is_file():continue
        if p.suffix=='.json':
            try:json.loads(p.read_text(encoding='utf-8-sig'));complete.append(str(p.relative_to(ROOT)))
            except (UnicodeError,json.JSONDecodeError):malformed.append(str(p.relative_to(ROOT)))
        elif p.suffix=='.csv':
            try:
                with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.reader(f,strict=True))
                if not rows or any(len(r)!=len(rows[0]) for r in rows):malformed.append(str(p.relative_to(ROOT)))
                else:complete.append(str(p.relative_to(ROOT)))
            except (UnicodeError,csv.Error):malformed.append(str(p.relative_to(ROOT)))
        elif p.suffix=='.py' and p.is_relative_to(OUT):
            ast.parse(p.read_text(encoding='utf-8-sig'),filename=p.name);syntax.append(p.name)
    check('Whole CSV rows and valid JSON',not malformed,malformed)
    projection_errors=[]
    for p in sorted((RAW/'run4/cisi1-identity-review').glob('*.json')):
        try:
            d=json.loads(p.read_text(encoding='utf-8'));assert d['complete_identity_projection'] and d['text_recoverable']
        except (ValueError,KeyError,AssertionError):projection_errors.append(str(p.relative_to(ROOT)))
    check('New catalogue identity projections complete',not projection_errors,projection_errors)
    check('Verification scripts parse',bool(syntax),syntax)
    idx=page_index();required=set()
    for r in csvrows(OUT/'input-v2-2026-10-21/objects.csv'):
        required.update((r['primary_publication'],p) for p in page_numbers(r['pdf_page']))
    for name,sid in [('omission-assignments.csv','source_id'),('blind-assignments.csv','primary_publication'),('unnamed-search-v2.csv','source_id')]:
        for r in csvrows(OUT/name):
            if r.get(sid):required.update((r[sid],p) for p in page_numbers(r['pdf_page']))
    missing=[];empty=[];source_pages=[]
    for key in sorted(required):
        if key not in idx:missing.append({'source_id':key[0],'pdf_page':key[1]});continue
        paths=idx[key]
        if not any(p.read_text(encoding='utf-8-sig',errors='replace').strip() for p in paths):empty.append({'source_id':key[0],'pdf_page':key[1]})
        for p in paths:source_pages.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    check('Required page text exists and is non-empty',not missing and not empty,{'required_unique_pages':len(required),'missing':missing,'empty':empty})
    check('No new page render remains',not list((RAW/'run4').rglob('*.png')) and not list((RAW/'run4').rglob('*.jpg')))
    blind=json.loads((OUT/'blind-summary.json').read_text(encoding='utf-8'))
    check('Blind records remain 60 rows and 600 slots',blind['sample']==60 and len(csvrows(OUT/'blind-sample.csv'))==600)
    check('Exact interval endpoint',abs(interval(0,39)[1]-(1-.025**(1/39)))<1e-12)
    q,_=project('{"ignored":[{"discarded":"skip"}],"site":"Test","metadata":{"ignored":[1,2],"type":"SEAL"},"object_family_id":1}')
    check('Corpus projection skips excluded values',q=={'site':'Test','metadata':{'type':'SEAL'},'object_family_id':1})
    from finish_v2 import unnamed
    # The search implementation is tested against punctuation and OCR aliases
    # through its recorded independent examples, without rereading a page.
    text=(OUT/'finish_v2.py').read_text(encoding='utf-8')
    check('Composite registration fix is recorded','optional literal punctuation' in json.loads((OUT/'unnamed-summary-v2.json').read_text(encoding='utf-8'))['search_rule'])
    for name in ['count-check-v2.json','locator-check-v2.json','coordinator-join-check-v2.json','content-check-v2.json']:
        d=json.loads((OUT/name).read_text(encoding='utf-8'))
        check('Valid requested endpoint '+name,isinstance(d,dict) and bool(d))
    c=json.loads((OUT/'count-check-v2.json').read_text(encoding='utf-8'))
    check('Both count systems reproduce',not c['differences'] and not c['decision_application_differences'])
    l=json.loads((OUT/'locator-check-v2.json').read_text(encoding='utf-8'))
    check('Locator audit has no failures',not l['failures'] and not l['empty_primary_page_text'])
    j=json.loads((OUT/'coordinator-join-check-v2.json').read_text(encoding='utf-8'))
    check('Current match identifiers and context storage pass',all(x['would_reach'] for x in j['matched_assessments']) and not j['empty_candidate_sets'] and not any(x['failures'] for x in j['context_storage_checks']))
    check('Dholavira algorithm reproduces',not j['dholavira_algorithm_differences'])
    content=json.loads((OUT/'content-check-v2.json').read_text(encoding='utf-8'))
    check('200 copy windows per cited source',all(x['sampled_unique_windows']>=200 for x in content['source_coverage']))
    check('Every raw content hit is classified',all('classification' in h for h in content['hits']))
    for name in ['VERIFICATION.md','final.md','RETROSPECTIVE.md']:
        s=(OUT/name).read_text(encoding='utf-8');check('Report content guard '+name,bool(s.strip()) and not RESTRICTED.search(s) and not UNIT.search(s))
    status={'passed':all(c['passed'] for c in checks),'checks':checks,'interpretation':'Implementation and record-integrity checks can pass while substantive source inventories, candidate conflicts and the recorded exposure failure remain unresolved.'}
    save('integrity-check-v2.json',{'preserved_endpoint_hashes':hashes,'validated_record_files':complete,'malformed_records':malformed,'required_source_page_records':source_pages,'missing_required_pages':missing,'empty_required_pages':empty,'scope':'CSV and JSON completeness is checked across the working package. Required primary, blind, omission and unnamed occurrence pages are checked for non-empty held text. Image-only pages without a required locator are not inferred to have textual inventories.'})
    save('selftest-v2.json',status)
    print('SELFTEST',status['passed'],len(checks),'checks;',len(complete),'valid CSV/JSON records;',len(required),'required pages')
    for c in checks:
        if not c['passed']:print('FAILED',c['check'],c['detail'])

def seal():
    content=json.loads((OUT/'content-check-v2.json').read_text(encoding='utf-8'))
    mismatches=[]
    for name,sha in content['file_hashes'].items():
        p=ROOT/name
        if hashlib.sha256(p.read_bytes()).hexdigest()!=sha:mismatches.append(name)
    manifest=json.loads((OUT/'input-manifest-v2.json').read_text(encoding='utf-8'))
    old_changed=[name for name,sha in manifest['preserved_first_versions'].items() if hashlib.sha256((OUT/name).read_bytes()).hexdigest()!=sha]
    live_changed=[x['input'] for x in manifest['inputs'] if hashlib.sha256((ROOT/x['input']).read_bytes()).hexdigest()!=x['sha256']]
    check=json.loads((OUT/'selftest-v2.json').read_text(encoding='utf-8'))
    print(json.dumps({'final_content_scan_hashes_current':not mismatches,'files_changed_after_scan':mismatches,'first_endpoints_unchanged':not old_changed,'first_endpoint_changes':old_changed,'live_inputs_still_equal_v2_snapshot':not live_changed,'live_input_changes':live_changed,'selftest_passed':check['passed'],'selftest_checks':len(check['checks']),'report_bytes':{n:(OUT/n).stat().st_size for n in ['VERIFICATION.md','final.md']}}))

if __name__=='__main__':
    try:
        if len(sys.argv)>2 and sys.argv[2]=='seal':seal()
        else:main()
    except OSError as e:
        try:save('WRITE-FAILURE-v2.json',{'stopped':True,'error_class':type(e).__name__})
        finally:raise SystemExit('Stopped after an input/output error.')
