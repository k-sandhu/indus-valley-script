"""Inventory only files authored or modified for this review response."""
import json
from parse_catalogue import ROOT, RAW, RUN, sha, write_json

MODIFIED=['PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','sources.json','registry-entry.json','parse_catalogue.py','verify.py','parser-validation-v2.json']
CREATED=['review_response.py','update_review_sources.py','make_review_summaries.py','verify_review_response.py','compare_review_runs.py','check_review_package.py',
         'review_response_inventory.py','parser-validation-review-response.json','review-response-research-log.json','review-response-verification.json',
         'review-response-frozen-verification.json','review-response-reproduction.json','review-response-final-checks.json']
OWNED_DIRS=['history','summary-tables-review-response','runs/2026-10-07-review-response','runs/2026-10-07-review-response-v2',
            'runs/2026-10-07-review-response-v3','runs/2026-10-07-review-response-v4']
RAW_DIRS=['revision-searches','revision-literature','2026-10-07-review-response','2026-10-07-review-response-v2',
          '2026-10-07-review-response-v3','2026-10-07-review-response-v4']

def main():
    files={RUN/f:'modified' for f in MODIFIED if (RUN/f).is_file()}
    files.update({RUN/f:'created' for f in CREATED if (RUN/f).is_file()})
    dirs=[]
    for base,names in [(RUN,OWNED_DIRS),(RAW,RAW_DIRS)]:
        for name in names:
            folder=base/name
            if not folder.exists():continue
            dirs.append(folder.relative_to(ROOT).as_posix())
            dirs += [p.relative_to(ROOT).as_posix() for p in folder.rglob('*') if p.is_dir()]
            files.update({p:'created' for p in folder.rglob('*') if p.is_file()})
    target=RUN/'REVIEW-RESPONSE-FILES.json';items=[]
    for p,action in sorted(files.items(),key=lambda t:t[0].as_posix()):
        items.append({'path':p.relative_to(ROOT).as_posix(),'action':action,'bytes':p.stat().st_size,'sha256':sha(p),
                      'area':'local-only raw' if p.is_relative_to(RAW) else 'owned'})
    items.append({'path':target.relative_to(ROOT).as_posix(),'action':'created','bytes':None,'sha256':None,'area':'owned','note':'Self hash/size omitted to avoid recursion.'})
    created=sum(r['bytes'] or 0 for r in items if r['action']=='created')
    write_json(target,{'status':'Verified computation','scope':'Current files created or modified by the review response only; coordinator review files and frozen outputs were not changed.',
               'modified_files_n':len(MODIFIED),'created_files_n':sum(r['action']=='created' for r in items),'all_files_n':len(items),
               'created_bytes_excluding_inventory':created,'created_mib_excluding_inventory':created/1024**2,
               'directories_created':sorted(set(dirs)),'files':items})
    print(json.dumps({'files':len(items),'modified':len(MODIFIED),'created_mib':created/1024**2}))

if __name__=='__main__':main()
