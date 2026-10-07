"""Check preserved endpoints and dated review amendments without fitting or writing."""
import hashlib
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def check(entry):
    path = ROOT / entry['path']
    assert path.stat().st_size == entry['bytes'], f'Size changed: {path}'
    assert digest(path) == entry['sha256'], f'Hash changed: {path}'


def main():
    record = json.loads((OWN / 'followup-2026-10-07.json').read_text(encoding='utf-8'))
    check(record['historical_inventory'])
    for entry in record['preserved_critical_endpoints'] + record['local_raw_new_files']:
        check(entry)
    amendments = {entry['path']: entry for entry in record['amended_files']}
    inventory = json.loads((OWN / 'file-manifest.json').read_text(encoding='utf-8'))
    preserved = 0
    for entry in inventory['files']:
        if entry['sha256'] is None:
            continue
        if entry['path'] in amendments:
            amendment = amendments[entry['path']]
            assert entry['sha256'] == amendment['before_sha256']
            assert entry['bytes'] == amendment['before_bytes']
            check({'path': amendment['original_witness'],
                   'bytes': amendment['before_bytes'],
                   'sha256': amendment['before_sha256']})
        else:
            check(entry)
            preserved += 1
    for entry in record['amended_files'] + record['added_files'] + record['review_evidence']:
        check(entry)
    prefix = record['protocol_original_prefix']
    original = (ROOT / prefix['original_witness']).read_bytes()
    assert (OWN / 'PROTOCOL.md').read_bytes().startswith(original)
    assert hashlib.sha256(original).hexdigest() == prefix['sha256']
    parsed = 0
    for base in (OWN, ROOT / 'data/raw/2026-10-06-modern-restoration'):
        for path in base.rglob('*.json'):
            try:
                json.loads(path.read_bytes())
            except (UnicodeError, json.JSONDecodeError) as error:
                raise ValueError(f'Invalid JSON: {path}') from error
            parsed += 1
    print(json.dumps({'status': 'Verified computation',
        'preserved_historical_hashes': preserved,
        'amended_files_verified': len(record['amended_files']),
        'added_files_verified': len(record['added_files']),
        'review_evidence_hashes_verified': len(record['review_evidence']),
        'json_files_parsed': parsed,
        'original_protocol_prefix_preserved': True,
        'files_written': 0, 'models_fitted': 0}))


if __name__ == '__main__':
    main()
