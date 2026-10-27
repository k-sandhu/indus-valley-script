"""Compare inherited asset hashes with the verified migration inventory."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

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
            # Bibliographic fields often append a parenthetical description or a
            # list of page images after the actual file path. Keep the original
            # string in the audit, and resolve its first literal asset separately.
            logical=path.replace('\\','/').split(' (',1)[0].split(', ',1)[0].strip()
            r['resolved_asset_path']=logical
            prefix=str(ROOT).replace('\\','/')+'/'
            if logical.startswith(prefix):logical=logical[len(prefix):]
            p=ROOT/logical
            if not p.is_file():r.update(status='not-held-at-path',reason='The inherited path is not an available file; no replacement asset was inferred.')
            else:
                if logical in held and p.stat().st_size==held[logical]['bytes']:
                    actual=held[logical]['sha256'];basis='SHA-256 recorded and verified during the completed migration; current size also matches'
                else:
                    if logical not in cache:cache[logical]=hashlib.sha256(p.read_bytes()).hexdigest()
                    actual=cache[logical];basis='Fresh file SHA-256'
                r.update(actual_sha256=actual,basis=basis,status='match' if actual==expected else 'mismatch')
        results.append(r)
    x=dict(scope='Asset-hash lineage check, not a page-reading or archaeological verification',counts=dict(Counter(r['status'] for r in results)),
           migration_manifest_sha256=hashlib.sha256(migration.read_bytes()).hexdigest(),rows=results)
    with dest.open('x',encoding='utf-8') as f:json.dump(x,f,indent=2)
    print(json.dumps(x['counts']))

if __name__=='__main__':main()
