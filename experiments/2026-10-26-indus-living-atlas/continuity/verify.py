"""Check register integrity and local source bytes; does not verify historical claims."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STORAGE = Path('D:/projects/indus_valley_script').resolve()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    args=parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    checks=[]
    def check(name,ok,detail=''):
        checks.append({'name':name,'passed':bool(ok),'detail':detail})
    def read(path):
        return json.loads(path.read_text(encoding='utf-8'))
    source_data=read(HERE/'sources.json')
    evidence_data=read(HERE/'evidence.json')
    sources=source_data['sources']
    evidence=evidence_data['evidence']
    sids=[s['id'] for s in sources]
    eids=[e['id'] for e in evidence]
    check('source_ids_unique',len(sids)==len(set(sids)))
    check('evidence_ids_unique',len(eids)==len(set(eids)))
    check('bounded_source_count',len(sources)==12)
    check('expected_evidence_count',len(evidence)==16)
    check('junction', (ROOT/'data/raw').resolve()==STORAGE/'data/raw')
    by_id={s['id']:s for s in sources}
    for s in sources:
        required=['id','title','authors','year','url','citation','lineage','inspected_scope','rights','access_depth','witnesses']
        check('source_fields_'+s['id'],all(k in s and s[k] is not None for k in required))
        check('source_url_'+s['id'],s['url'].startswith('https://'))
        check('source_year_'+s['id'],1800<=s['year']<=2026)
        for w in s['witnesses']:
            p=ROOT/w['logical_path']
            check('source_exists_'+w['logical_path'],p.is_file())
            if p.is_file():
                check('source_hash_'+w['logical_path'],hashlib.sha256(p.read_bytes()).hexdigest()==w['sha256'])
                check('source_size_'+w['logical_path'],p.stat().st_size==w['bytes'])
                check('source_physical_'+w['logical_path'],p.resolve()==Path(w['physical_path']).resolve())
                check('source_storage_'+w['logical_path'],p.resolve().is_relative_to(STORAGE))
    for e in evidence:
        required=['id','source_id','title','authors','year','url','locator','observation','interpretation','chronology',
                  'date_range_bce','geography','marker_domain','confidence','statement_kind','independence','scenario_implications']
        check('evidence_fields_'+e['id'],all(k in e for k in required))
        check('evidence_source_'+e['id'],e['source_id'] in by_id)
        s=by_id[e['source_id']]
        check('evidence_bibliography_'+e['id'],all(e[k]==s[k] for k in ['title','authors','year','url']))
        dates=e['date_range_bce']
        check('evidence_dates_'+e['id'],dates is None or (len(dates)==2 and dates[0]>=dates[1]>0))
        check('evidence_dependence_'+e['id'],bool(e['independence'].get('group')))
    freeze=read(HERE/'protocol-freeze-v1.json')
    check('protocol_unchanged',hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest()==freeze['sha256'])
    check('dholavira_exception_explicit', all(t in by_id['B2015']['inspected_scope'] for t in ['103','104']))
    dholavira=next(e for e in evidence if e['id']=='E06')
    check('dholavira_writing_and_weights',all(t in dholavira['marker_domain'] for t in ['writing','weights']))
    check('alamgirpur_uncertainty_explicit',next(e for e in evidence if e['id']=='E15')['date_range_bce'] is None)
    check('gandal_author_corrected','Kavita Gangal' in by_id['G2012']['authors'])
    check('chapter_end_page_inspected','191–219' in by_id['KM2004']['citation'])
    for d in read(HERE/'derivatives-v1.json')['derivatives']:
        p=ROOT/d['logical_path']
        check('derivative_'+d['logical_path'],p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256'])
    for md in HERE.glob('*.md'):
        for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',md.read_text(encoding='utf-8')):
            if not target.startswith(('https://','http://','#')):
                p=(md.parent/target.split('#')[0]).resolve()
                if p==args.out.resolve():
                    continue
                check('markdown_link_'+md.name+':'+label,p.exists(),str(p))
    raw_paths=sorted({w['logical_path'] for s in sources for w in s['witnesses']}|
                     {d['logical_path'] for d in read(HERE/'derivatives-v1.json')['derivatives']})
    run=subprocess.run(['git','check-ignore','--stdin','-z'],input=b''.join(p.encode()+b'\0' for p in raw_paths),
                       cwd=ROOT,capture_output=True)
    ignored=set(run.stdout.decode('utf-8').split('\0'))
    check('all_raw_paths_ignored',all(p in ignored for p in raw_paths),f'{len(raw_paths)} local-only files checked')
    registry=read(ROOT/'knowledge/registry/attempts/INDUS-MARKER-CONTINUITY-2026-10-26.json')
    check('registry_source_review',registry['status_class']=='source-review')
    for p in registry['evidence']:
        check('registry_evidence_'+p,(ROOT/p).exists() or (ROOT/p).resolve()==args.out.resolve())
    input_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir()
                  if p.is_file() and p.suffix in ['.md','.py'] or (p.is_file() and p.name in ['sources.json','evidence.json','derivatives-v1.json'])}
    result={'schema_version':'1.0','study':'INDUS-MARKER-CONTINUITY-2026-10-26','created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'status_class':'source-review','verification_tier':'submitted','scope':'Same-contributor register, source-byte and link checks; no independent historical review.',
        'python':sys.version,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':input_hashes,
        'summary':{'checks':len(checks),'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
                   'sources':len(sources),'evidence_rows':len(evidence),'raw_paths':len(raw_paths)},'checks':checks}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary'],indent=2))
    return 0 if all(c['passed'] for c in checks) else 1

if __name__=='__main__':
    raise SystemExit(main())
