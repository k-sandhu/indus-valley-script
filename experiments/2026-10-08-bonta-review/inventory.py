"""Inventory Package Q and its response, excluding reviewer files/supplied witnesses."""
from pathlib import Path
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'

def main():
    baseline=json.loads((OWN/'history/2026-10-08-before-review-response/FILES.json').read_text(encoding='utf-8'))
    previous={r['path']:r for r in baseline['files']}
    rows=[]
    for base,kind in [(OWN,'owned'),(RAW,'local_raw')]:
        for p in sorted(base.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(base)
            if any(part.startswith('.') for part in rel.parts):continue
            if kind=='owned' and (rel.parts[0]=='review' or rel.as_posix()=='REVIEW.md'):continue
            relative=p.relative_to(ROOT).as_posix()
            if kind=='local_raw' and relative not in previous and not rel.parts[0].startswith('response-'):continue
            if kind=='owned' and rel.as_posix() in ('FILES.json','RESPONSE-FILES.json'):continue
            sha=hashlib.sha256(p.read_bytes()).hexdigest()
            action='created' if relative not in previous else ('changed' if sha!=previous[relative].get('sha256') else 'preserved')
            rows.append({'path':relative,'category':kind,'action':action,
              'bytes':p.stat().st_size,'sha256':sha})
    # The two inventories reference one another; omit their circular hashes.
    for name in ('FILES.json','RESPONSE-FILES.json'):
        relative=(OWN/name).relative_to(ROOT).as_posix()
        rows.append({'path':relative,'category':'owned','action':'changed' if relative in previous else 'created',
                     'sha256':None,'note':'Inventory pair; circular hashes omitted'})
    frozen_prefixes=['experiments/2026-10-08-bonta-review/'+name+'/' for name in ('run-2026-10-08-v1','run-replay-2026-10-08-01')]
    frozen_prefixes += ['data/raw/2026-10-08-bonta-review/'+name+'/' for name in ('run-2026-10-08-v1','run-replay-2026-10-08-01')]
    frozen_rows=[r for r in rows if any(r['path'].startswith(prefix) for prefix in frozen_prefixes)]
    preservation={'frozen_run_files_checked':len(frozen_rows),'frozen_run_files_preserved':sum(r['action']=='preserved' for r in frozen_rows),
                  'basis':'Hashes in the preserved initial FILES.json; includes owned aggregates and local raw derivatives.'}
    if preservation['frozen_run_files_checked']!=preservation['frozen_run_files_preserved']:
        raise SystemExit('A frozen run file differs from the original inventory')
    x={'scope':'Current Package Q files, with response actions relative to the preserved initial inventory. Reviewer files and supplied unchanged witnesses excluded. No writes outside owned/local raw directories.',
       'owned_files':sum(r['category']=='owned' for r in rows),'local_raw_files':sum(r['category']=='local_raw' for r in rows),
       'preservation_checks':preservation,
       'files':rows}
    (OWN/'FILES.json').write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
    changes=[r for r in rows if r['action']!='preserved']
    (OWN/'RESPONSE-FILES.json').write_text(json.dumps({'date':'2026-10-08','scope':'Every path created or changed during the review response; protected reviewer and frozen outputs were preserved.',
        'created_files':sum(r['action']=='created' for r in changes),'changed_files':sum(r['action']=='changed' for r in changes),'files':changes},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in x.items() if k!='files'},indent=2))

if __name__=='__main__':main()
