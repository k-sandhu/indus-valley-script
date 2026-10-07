"""Inventory the two package-owned directories without changing research outputs.

Run from the repository root:
python experiments/2026-10-06-sign-context-and-seals/inventory.py
Use --output with a fresh filename for a later snapshot. The manifest includes
itself with no hash, avoiding a recursive hash definition.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='FILE-MANIFEST.json')
    args = ap.parse_args()
    dest = (OWN / args.output).resolve()
    if dest.parent != OWN or dest.exists():
        raise ValueError('Choose a new manifest filename inside the owned directory.')
    files = []
    modified = {OWN / 'PROTOCOL.md', OWN / 'acquire_sources.py'}
    for folder in (OWN, RAW):
        for p in sorted(folder.rglob('*')):
            if p.is_file():
                files.append({
                    'path': p.relative_to(ROOT).as_posix(),
                    'change': 'modified' if p in modified else 'created',
                    'local_only': folder == RAW,
                    'bytes': p.stat().st_size,
                    'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                })
    files.append({'path': dest.relative_to(ROOT).as_posix(), 'change': 'created',
                  'local_only': False, 'bytes': None, 'sha256': None,
                  'note': 'Manifest self-entry intentionally has no size/hash.'})
    result = {
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'Every file in the two owned directories at package completion; no shared file edits.',
        'file_count': len(files),
        'owned_file_count': sum(not f['local_only'] for f in files),
        'local_raw_file_count': sum(f['local_only'] for f in files),
        'payload_bytes_excluding_manifest': sum(f['bytes'] or 0 for f in files),
        'files': sorted(files, key=lambda f: f['path']),
    }
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(result['file_count'], 'paths:', result['owned_file_count'], 'owned,',
          result['local_raw_file_count'], 'local raw')


if __name__ == '__main__':
    run()
