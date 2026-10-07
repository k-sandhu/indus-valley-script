"""Compare the complete package with its preserved initial file manifest."""
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
    ap.add_argument('--output', default='FILE-MANIFEST-FOLLOWUP-2026-10-07.json')
    args = ap.parse_args()
    dest = (OWN / args.output).resolve()
    if dest.parent != OWN or dest.exists():
        raise ValueError('Choose a fresh manifest filename within the owned directory.')
    original = json.loads((OWN / 'FILE-MANIFEST.json').read_text(encoding='utf-8'))
    baseline = {v['path']: v for v in original['files']}
    baseline['experiments/2026-10-06-sign-context-and-seals/FILE-MANIFEST.json']['sha256'] = hashlib.sha256((OWN / 'FILE-MANIFEST.json').read_bytes()).hexdigest()
    files = []
    for folder in [OWN, RAW]:
        for p in sorted(folder.rglob('*')):
            if not p.is_file():
                continue
            key = p.relative_to(ROOT).as_posix()
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            change = 'created' if key not in baseline else 'unchanged' if baseline[key]['sha256'] == digest else 'modified'
            files.append({'path': key, 'change': change, 'local_only': folder == RAW,
                          'bytes': p.stat().st_size, 'sha256': digest,
                          'plot_dependency': 'plot-deps-2026-10-07/' in key})
    files.append({'path': dest.relative_to(ROOT).as_posix(), 'change': 'created',
                  'local_only': False, 'bytes': None, 'sha256': None, 'plot_dependency': False,
                  'note': 'Self-entry intentionally omits recursive size/hash.'})
    changed = [f for f in files if f['change'] != 'unchanged']
    result = {'stage': 'post-launch amendment', 'prepared_utc': datetime.now(timezone.utc).isoformat(),
              'baseline_manifest': 'FILE-MANIFEST.json', 'all_files': len(files),
              'created': sum(f['change'] == 'created' for f in files),
              'modified': sum(f['change'] == 'modified' for f in files),
              'unchanged': sum(f['change'] == 'unchanged' for f in files),
              'changed_owned_files': sum(not f['local_only'] for f in changed),
              'changed_local_raw_files': sum(f['local_only'] for f in changed),
              'new_local_plot_dependency_files': sum(f['plot_dependency'] for f in changed),
              'missing_baseline_paths': sorted(set(baseline) - {f['path'] for f in files}),
              'changed_paths': [f['path'] for f in changed], 'files': sorted(files, key=lambda f: f['path'])}
    if result['missing_baseline_paths']:
        raise AssertionError('An initial package file is missing.')
    dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print({k: result[k] for k in ['created', 'modified', 'unchanged', 'changed_owned_files',
                                 'changed_local_raw_files', 'new_local_plot_dependency_files']})


if __name__ == '__main__':
    run()
