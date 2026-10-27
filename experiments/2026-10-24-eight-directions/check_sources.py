"""Verify remaining declared source bytes without reading source interpretations."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import sys

from coordinate import ROOT, PACKAGE


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8-sig'))


def collect():
    records = []

    def add(manifest, path, sha256):
        records.append({'manifest': manifest, 'path': path, 'expected_sha256': sha256})

    office = 'experiments/2026-10-24-office-source-verification/source-manifest-v3.json'
    data = read(office)
    for row in data['sources'] + data['artifacts'] + [data['review_notes']]:
        add(office, row['physical_path'], row['sha256'])
    correction = 'experiments/2026-10-24-office-seal-evidence/modal-correction-v2.json'
    data = read(correction)
    add(correction, data['ledger_physical_path'], data['ledger_sha256'])
    lexical = 'experiments/2026-10-24-lexical-extraction-extension/source-manifest-v1.json'
    data = read(lexical)
    for row in data['output_files']:
        add(lexical, row['physical_path'], row['sha256'])
    for row in data['sources']:
        add(lexical, row['parent_manifest'], row['parent_sha256'])
    freeze = 'experiments/2026-10-24-lexical-extraction-extension/FREEZE-v3.json'
    add(lexical, freeze, data['freeze_sha256'])
    data = read(freeze)
    for path, expected in data['pins'].items():
        add(freeze, path, expected)
    for row in data['pages']:
        add(freeze, row['physical_path'], row['sha256'])
    return records


def verify(row):
    path = Path(row['path'])
    if not path.is_absolute():
        path = ROOT / path
    try:
        actual = digest(path)
        return dict(row, physical_path=str(path.resolve()), actual_sha256=actual,
                    exists=True, matches=actual == row['expected_sha256'])
    except OSError as exc:
        return dict(row, exists=path.exists(), matches=False, error=str(exc))


if __name__ == '__main__':
    target = Path(sys.argv[1])
    if target.exists():
        raise SystemExit('Refusing to overwrite a prior review.')
    with ThreadPoolExecutor(max_workers=16) as pool:
        checks = list(pool.map(verify, collect()))
    errors = [row for row in checks if not row['matches']]
    result = {'status': 'pass' if not errors else 'fail',
              'scope': 'Parent byte checks for lexical inputs and outputs, separate source review, and corrected office ledger.',
              'check_count': len(checks), 'checks': checks, 'errors': errors}
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'check_count': len(checks), 'errors': errors}, indent=2))
    raise SystemExit(bool(errors))
