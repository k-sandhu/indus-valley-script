"""Check prior endpoint preservation, registry retention and frozen reviews."""
import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASELINE = '420ef6fddfe544c037f101f73bad3bf27f6cf9ed'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='integration-checks.json')
    args = parser.parse_args()
    out = HERE / args.output
    if out.exists():
        raise FileExistsError('Preserve previous checks; choose another output')
    checks = []
    prior_registry = json.loads(subprocess.check_output(
        ['git', 'show', BASELINE + ':knowledge/experiments/registry.json'], cwd=ROOT))
    current = json.loads((ROOT / 'knowledge/experiments/registry.json').read_text(encoding='utf-8'))
    old = prior_registry['experiments']
    checks.append({'check': 'prior registry objects preserved',
                   'pass': current['experiments'][:len(old)] == old,
                   'prior_entries': len(old), 'current_entries': len(current['experiments'])})
    tree = subprocess.check_output(['git', 'ls-tree', '-r', BASELINE, '--',
        'experiments/2026-10-02-connections-and-priority',
        'experiments/2026-10-02-decipherment-readiness'], cwd=ROOT).decode('utf-8')
    prior_files = []
    for line in tree.splitlines():
        meta, name = line.split('\t', 1)
        path = ROOT / name
        content = path.read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
        passed = actual == meta.split()[2]
        prior_files.append({'path': name, 'sha256': sha256(path), 'unchanged': passed})
    checks.append({'check': 'previous dated endpoints preserve Git bytes',
                   'pass': all(p['unchanged'] for p in prior_files), 'files': len(prior_files)})
    manifest_specs = [('oxus/verification.json', 'owned_output_files'),
                      ('susa/endpoint-manifest.json', 'files'),
                      ('south-india/endpoint-manifest.json', 'files'),
                      ('south-india/independent-review.json', 'reviewed_files'),
                      ('physical-views/artifact-manifest.json', 'artifacts'),
                      ('integration-review-v2.json', 'reviewed_files')]
    reviewed_files = []
    for relative, key in manifest_specs:
        manifest = json.loads((HERE / relative).read_text(encoding='utf-8'))
        for item in manifest[key]:
            path = ROOT / item['path']
            passed = sha256(path) == item['sha256']
            reviewed_files.append({'manifest': relative, 'path': item['path'], 'hash_matches': passed})
    checks.append({'check': 'frozen endpoint and reviewed hashes',
                   'pass': all(p['hash_matches'] for p in reviewed_files), 'files': len(reviewed_files)})
    result_specs = [('oxus/results-v2.json', 'status', 'pass'),
                    ('susa/validation.json', 'status', 'pass'),
                    ('south-india/verification.json', 'passed', True),
                    ('south-india/independent-review.json', 'status', 'passed after two corrections'),
                    ('physical-views/verification-v2.json', 'failed', 0)]
    for relative, key, expected in result_specs:
        record = json.loads((HERE / relative).read_text(encoding='utf-8'))
        checks.append({'check': relative, 'pass': record[key] == expected,
                       'actual': record[key]})
    for path in sorted(HERE.rglob('*.py')):
        ast.parse(path.read_text(encoding='utf-8'))
    checks.append({'check': 'new Python syntax', 'pass': True,
                   'files': len(list(HERE.rglob('*.py')))})
    result = {'baseline_commit': BASELINE, 'status': 'pass' if all(c['pass'] for c in checks) else 'fail',
              'checks': checks, 'prior_files': prior_files, 'frozen_reviewed_files': reviewed_files,
              'scope': 'Preservation, saved check outcomes and syntax; source meanings require the linked visual reviews.'}
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'checks': len(checks),
                      'prior_files': len(prior_files), 'reviewed_hashes': len(reviewed_files)}))
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
