"""Inspect retained PDF containers and inventory package paths without downloads."""
import hashlib
import json
from pathlib import Path
import fitz

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/c-north-india'

def main():
    pdfs=[]
    for p in sorted(RAW.glob('*.pdf')):
        item=dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size)
        try:
            with fitz.open(p) as document:
                item.update(pages=len(document),container_opens=True)
        except Exception as exc:
            item.update(container_opens=False,error=str(exc))
        pdfs.append(item)
    report=dict(status='Verified computation' if all(p['container_opens'] for p in pdfs) else 'Failed',
                pdfs=pdfs,limitation='Opening PDF containers establishes readability, not page completeness or source authenticity.')
    (RAW/'pdf-integrity.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    # Only remove the cache of this package's own curated module.
    cache=OUT/'__pycache__'
    if cache.exists():
        for p in cache.glob('evidence_notes.*.pyc'):
            assert p.resolve().is_relative_to(OUT.resolve())
            p.unlink()
        if not any(cache.iterdir()):cache.rmdir()
    baseline=json.loads((RAW/'recovery-audit.json').read_text(encoding='utf-8'))
    prior={x['path']:x for x in baseline['entries']}
    entries=[]
    target=OUT/'file-manifest.json'
    for base in [OUT,RAW]:
        for p in sorted(base.rglob('*')):
            if not p.is_file() or p==target:continue
            path=p.relative_to(ROOT).as_posix()
            item=dict(path=path,bytes=p.stat().st_size,directory='owned' if base==OUT else 'local raw')
            if base==OUT:
                item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
            old=prior.get(path)
            item['recovery_comparison']=('added after recovery audit' if not old else
                'changed after recovery audit' if item.get('sha256') and old.get('sha256')!=item['sha256'] else
                'changed size after recovery audit' if old['bytes']!=item['bytes'] else 'retained from recovery audit')
            entries.append(item)
    manifest=dict(status='Verified computation',entries=entries,
        manifest_path=target.relative_to(ROOT).as_posix(),
        note='Lists all retained owned files and raw witnesses, including earlier work. The manifest itself is named here without a recursive hash. Deleted temporary render paths are in local raw cleanup-manifest.json.',
        owned_files=sum(x['directory']=='owned' for x in entries)+1,
        raw_files=sum(x['directory']=='local raw' for x in entries),
        owned_bytes_excluding_manifest=sum(x['bytes'] for x in entries if x['directory']=='owned'),
        raw_bytes=sum(x['bytes'] for x in entries if x['directory']=='local raw'))
    target.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(pdf_files=len(pdfs),failed_pdfs=[p['path'] for p in pdfs if not p['container_opens']],
        owned_files=manifest['owned_files'],raw_files=manifest['raw_files'],raw_bytes=manifest['raw_bytes'])))

if __name__=='__main__':main()
