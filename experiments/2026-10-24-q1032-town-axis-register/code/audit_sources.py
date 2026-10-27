"""Compare inherited asset hashes with the verified migration inventory."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    dest=Path(a.out)
    if dest.exists():raise SystemExit('Preserve the earlier source audit.')
    migration=Path('D:/projects/indus_valley_script/migration-2026-10-24.json')
    held={r['relative_path']:r for r in json.loads(migration.read_text(encoding='utf-8'))['files']}
    sources=[json.loads(l) for l in (Path(a.run)/'sources.jsonl').read_text(encoding='utf-8').splitlines()]
    results=[];cache={}
    for source in sources:
        m=source['metadata']; expected=m.get('sha256',m.get('source_sha256',m.get('composite_sha256')))
        path=next((m.get(k) for k in ['file','local_path','source_path','composite_path','logical_path'] if isinstance(m.get(k),str)),None)
        if not path and isinstance(m.get('url_or_path'),str):
            path=next((s.strip() for s in m['url_or_path'].split(';') if s.strip().startswith(('data/','research/'))),None)
        if not path and isinstance(m.get('composite'),dict):
            path=m['composite'].get('path');expected=m['composite'].get('sha256')
        r=dict(source_id=source['source_id'],path=path,expected_sha256=expected)
        if not path or not expected:
            r.update(status='not-computable',reason='A local asset path and a matching SHA-256 are not both supplied at this metadata level; original source record remains referenced.')
        else:
            # One bibliographic entry can name OCR and page images with different
            # hashes. Resolve literal assets and preserve which one matches.
            written=path.replace('\\','/')
            candidates=[written] if (ROOT/written).is_file() else re.findall(r'(?:data|research)/[^;\n]*?\.(?:pdf|txt|html|jsonl|json|bin|png|jpe?g|tiff?)',written)
            if not candidates:candidates=[written.split(' (',1)[0].split(', ',1)[0].strip()]
            folders={str(Path(c).parent).replace('\\','/') for c in candidates}
            names=re.findall(r'(?<![/\w])([\w.-]+\.(?:pdf|txt|html|jsonl|json|bin|png|jpe?g|tiff?))',written)
            candidates+=sorted({folder+'/'+name for folder in folders for name in names})
            prefix=str(ROOT).replace('\\','/')+'/'
            assets=[]
            for logical in dict.fromkeys(candidates):
                if logical.startswith(prefix):logical=logical[len(prefix):]
                p=ROOT/logical
                if not p.is_file():continue
                if logical in held and p.stat().st_size==held[logical]['bytes']:
                    actual=held[logical]['sha256'];basis='SHA-256 recorded and verified during the completed migration; current size also matches'
                else:
                    if logical not in cache:cache[logical]=hashlib.sha256(p.read_bytes()).hexdigest()
                    actual=cache[logical];basis='Fresh file SHA-256'
                assets.append(dict(path=logical,actual_sha256=actual,basis=basis))
            matches=[q for q in assets if q['actual_sha256']==expected]
            r.update(available_assets=assets,matching_asset_paths=[q['path'] for q in matches])
            if matches:r.update(status='match',reason='Expected hash matches at least one explicitly referenced asset; other assets retain their own hashes.')
            elif assets:r.update(status='mismatch',reason='Available referenced assets do not match the declared hash.')
            else:r.update(status='not-held-at-path',reason='No literal referenced asset is available; no replacement was inferred.')
        results.append(r)
    x=dict(scope='Asset-hash lineage check, not a page-reading or archaeological verification',counts=dict(Counter(r['status'] for r in results)),
           migration_manifest_sha256=hashlib.sha256(migration.read_bytes()).hexdigest(),rows=results)
    with dest.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2)
    print(json.dumps(x['counts']))

if __name__=='__main__':main()
