"""Inventory only paths created or changed for the fourth follow-up."""
from pathlib import Path
import argparse
import json
import record_repaired_endpoint as R

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REC=HERE/'repair/2026-10-08-endpoint-record-v1'
RAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-endpoint-inspection-v1'
CHANGED=['README.md','REPORT.md','PROTOCOL.md','RETROSPECTIVE.md','registry-entry.json','sources.json','OPTION-B-INTERFACE.md','write_crop_v3_docs.py']
CREATED=['record_v3_endpoint.py','inspect_v3_endpoint.py','audit_v3_endpoint_windows.py','write_v3_endpoint_docs.py','verify_v3_endpoint_record.py','inventory_v3_endpoint_record.py']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=REC/'changed-paths.json')
    args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():
        raise ValueError('Use a fresh owned inventory path')
    paths=[HERE/p for p in CHANGED+CREATED]
    paths+=list(p for p in REC.rglob('*') if p.is_file())
    paths+=list(p for p in RAW.rglob('*') if p.is_file())
    rows=[]
    for p in sorted(set(paths)):
        if p==out:continue
        rows.append(dict(path=p.relative_to(ROOT).as_posix(),
                         action='changed' if p.parent==HERE and p.name in CHANGED else 'created',
                         bytes=p.stat().st_size,sha256=R.sha(p)))
    result=dict(status='Verified computation',scope='Fourth follow-up only; excludes coordinator-created readings, references and metrics',
                self_path=out.relative_to(ROOT).as_posix(),self_hash_omitted_to_avoid_recursion=True,
                files=rows,file_count_excluding_self=len(rows),
                changed_files=sum(r['action']=='changed' for r in rows),created_files_excluding_self=sum(r['action']=='created' for r in rows),
                total_bytes_excluding_self=sum(r['bytes'] for r in rows),
                newly_created_bytes_excluding_self=sum(r['bytes'] for r in rows if r['action']=='created'))
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))


if __name__=='__main__':main()
