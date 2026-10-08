"""List paths changed by the pilot-result and pilot-2 follow-up only."""
import argparse
from pathlib import Path
import workflow as W

CHANGED=['README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','registry-entry.json','sources.json',
         'workflow.py','score_pilot.py','merge.py','adjudicate.py','validate_return.py','INPUT_CONTRACT.md']
CREATED=['prepare_pilot2.py','usage_ledger.py','record_pilot.py','check_followup.py','write_followup_docs.py','inventory_followup.py','PILOT-2.md']


def inventory(out):
    out=W.owned(out)
    paths={W.HERE/n:'changed' for n in CHANGED}|{W.HERE/n:'created' for n in CREATED}
    roots=[W.HERE/'follow-up/2026-10-08-pilot2-v1',W.HERE/'pilot-2/2026-10-08-v1',
           W.RAW/'pilot2-2026-10-08-v1',W.RAW/'pilot-merge-2026-10-08-ledger-v1',
           W.RAW/'regression-2026-10-08-v4']+list(W.RAW.glob('pilot2-check-2026-10-08-v*'))
    for root in roots:
        for file in root.rglob('*'):
            if file.is_file():paths[file]='created'
    for scored in ('scored-initial','scored-final'):
        output=W.HERE/'follow-up/2026-10-08-pilot2-v1'/scored
        path=W.RAW/'pilot-2026-10-08-v2/coordinator'/('control-scores-'+W.digest(W.relative(output))[:12]+'.json')
        if path.exists():paths[path]='created'
    paths[out]='created'
    rows=[dict(path=W.relative(p),action=a,bytes=p.stat().st_size if p!=out else None,sha256=W.sha(p) if p!=out else None,
               disposition='local-only' if p.is_relative_to(W.RAW) else 'own-code-prose-aggregate') for p,a in sorted(paths.items())]
    W.write(out,dict(status='Verified computation',files=rows,paths=len(rows),changed_files=sum(r['action']=='changed' for r in rows),
                     created_files=sum(r['action']=='created' for r in rows),local_raw_files=sum(r['disposition']=='local-only' for r in rows),
                     writes_outside_owned_directories=0,source_readings_performed=0,
                     note='Follow-up scope only; coordinator-created first-pilot returns/results are reused, not attributed to this package. Frozen first-pilot outputs and initial file-manifest.json are unchanged. Self entry excludes recursive size/hash.'))
    print(f'Inventoried {len(rows)} follow-up paths')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();inventory(a.out)
