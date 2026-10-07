"""Small second-follow-up delta inventory; never opens online-only plot files."""
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import analyze as main


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='revision-manifest-2026-10-07.json')
    args = parser.parse_args()
    destination = (main.OWN / args.output).resolve()
    if destination.parent != main.OWN or destination.exists():
        raise FileExistsError(destination)
    prior_path = main.OWN / 'FILE-MANIFEST-RECOVERY-2026-10-07.json'
    prior = json.loads(prior_path.read_text())
    known = {f['path']: f for f in prior['files']}
    records = []
    allowed_changes = {'PROTOCOL.md', 'README.md', 'REPORT.md', 'RETROSPECTIVE.md',
                       'registry-entry.json', 'sources.json', 'SOURCE-NOTES.md'}
    for folder in (main.OWN, main.RAW):
        for base, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in {'review', 'plot-deps-2026-10-07'}]
            for name in sorted(files):
                path = Path(base) / name
                if path == main.OWN / 'REVIEW.md':
                    continue  # existing reviewer input, not a contributor change
                key = path.relative_to(main.ROOT).as_posix()
                digest = main.sha(path)
                old = known.get(key)
                if old and (old['sha256'] == digest or path == prior_path):
                    continue
                change = 'modified' if old else 'created'
                if change == 'modified':
                    assert path.parent == main.OWN and name in allowed_changes, key
                records.append({'path': key, 'change': change, 'bytes': path.stat().st_size,
                                'sha256': digest, 'local_only': folder == main.RAW})
    maintenance = json.loads((main.OWN / 'revision-maintenance-2026-10-07.json').read_text())
    records.append({'path': maintenance['removed_duplicate']['path'], 'change': 'removed duplicate',
                    'canonical': maintenance['removed_duplicate']['canonical'],
                    'sha256': maintenance['removed_duplicate']['sha256']})
    records.append({'path': destination.relative_to(main.ROOT).as_posix(), 'change': 'created',
                    'sha256': None, 'bytes': None, 'local_only': False,
                    'note': 'Self-entry omits recursive size/hash.'})
    main.write(destination, {'stage': 'post-review amendment',
        'prepared_utc': datetime.now(timezone.utc).isoformat(),
        'baseline': prior_path.name, 'baseline_sha256': main.sha(prior_path),
        'read_only_review_sha256': main.sha(main.OWN / 'REVIEW.md'),
        'excluded_preexisting_inputs': ['REVIEW.md', 'review/', 'data/raw/2026-10-06-sign-context-and-seals/review/'],
        'online_only_plotting': {'files': 1670, 'opened_or_reinstalled': False,
            'availability_evidence': 'REVIEW.md; review/manifest-recheck.json'},
        'created': sum(r['change'] == 'created' for r in records),
        'modified': sum(r['change'] == 'modified' for r in records),
        'removed_duplicate': 1, 'files': sorted(records, key=lambda r: r['path'])})
    print('Revision paths', len(records), 'created', sum(r['change'] == 'created' for r in records),
          'modified', sum(r['change'] == 'modified' for r in records))


if __name__ == '__main__':
    run()
