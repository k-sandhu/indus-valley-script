"""List every Package M v3 file and explicitly changed living/temporary path."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];RAW=ROOT/'data/raw/2026-10-07-helsinki1979-digitization'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Use a new owned inventory')
    changed=['PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','IMPORT_INTERFACE.md','registry-entry.json','sources.json','TRACK-EXCEPTIONS.txt','write_repaired_endpoint_docs.py']
    added=['crop_v3.py','develop_crop_v3.py','inspect_crop_v3.py','prepare_crop_v3.py','evaluate_crop_v3.py','record_crop_v3.py',
        'complete_crop_v3_full.py','check_continuation_v3.py','verify_crop_v3.py','write_crop_v3_docs.py','inventory_crop_v3.py',
        'V3-CONVENTIONS.md','OPTION-B-INTERFACE.md','option-b-schema.json','HOST-FILES.txt']
    files={HERE/p:'changed' for p in changed};files.update({HERE/p:'created' for p in added})
    directories=[]
    for directory in sorted((HERE/'repair').glob('2026-10-08-*'))+[RAW/'2026-10-08-v3']:
        if not directory.exists():continue
        directories.append(directory.relative_to(ROOT).as_posix())
        directories.extend(p.relative_to(ROOT).as_posix() for p in directory.rglob('*') if p.is_dir())
        files.update({p:'created' for p in directory.rglob('*') if p.is_file() and p.resolve()!=out})
    files[RAW/'tmp/margin_batch.png']='changed temporary OCR strip; reused filename, not a frozen witness'
    result=dict(status='Verified computation',scope='Package M v3 task files; original frozen endpoints and other packages excluded',
        self_path=out.relative_to(ROOT).as_posix(),self_hash_omitted_to_avoid_recursion=True,
        directories=sorted(set(directories)),files=[dict(path=p.relative_to(ROOT).as_posix(),change=kind,bytes=p.stat().st_size,sha256=sha(p))
            for p,kind in sorted(files.items()) if p.exists()],
        no_other_paths_written=True,large_outputs_local_and_listed='HOST-FILES.txt',backup_performed=False)
    result['totals']=dict(files=len(result['files']),bytes=sum(p['bytes'] for p in result['files']))
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result['totals']))
if __name__=='__main__':main()
