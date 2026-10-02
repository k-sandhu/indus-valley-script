"""Freeze this manual review's owned prose, source context and exact artifact list."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
CAPTURE = BASE / 'captured-2026-10-02-1100'
REVIEW = BASE / 'reviewed-2026-10-02-1100'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    if (BASE / 'verification.json').exists() or (BASE / 'artifact-manifest.json').exists():
        raise RuntimeError('Preserve previous final endpoints.')
    checks = []

    def check(name, passed, detail=None):
        checks.append(dict(check=name, passed=bool(passed), detail=detail))

    summary = read(CAPTURE / 'summary.json')
    reviewed = read(REVIEW / 'verification.json')
    check('accepted independent review passes', reviewed['checks_total'] == reviewed['checks_passed'] == 824)
    check('core navigation totals', summary['local_link_occurrences'] == 747 and summary['occurrences_by_category']['selected'] == 725 and summary['occurrences_by_category']['local-only'] == 22 and summary['unique_local_targets']['local-only'] == 18 and summary['unique_local_targets']['missing'] == 0)
    check('prospective protocol unchanged', summary['protocol_sha256'] == digest(BASE / 'PROTOCOL.md'))
    check('accepted executed scanner source', summary['code_sha256'] == digest(CAPTURE / 'code_snapshot.py') == digest(ROOT / 'tools/verify_checkout_navigation.py'))
    for relative, expected in reviewed['capture_hashes'].items():
        check('capture bytes preserved ' + relative, digest(ROOT / relative) == expected)
    for original, snapshot in summary['document_snapshots'].items():
        check('captured document and source context ' + original, digest(ROOT / snapshot) == summary['document_hashes'][original])
    live_changes = [name for name, sha in summary['document_hashes'].items() if digest(ROOT / name) != sha]
    check('core documents still match accepted capture', not live_changes, live_changes)
    routes = read(REVIEW / 'local-only-source-routes.json')
    check('source route completeness', len(routes) == 18 and {r['target'] for r in routes} == set(summary['targets']['local-only']))
    for row in routes:
        check('route evidence unchanged ' + row['target'], all(digest(ROOT / name) == expected for name, expected in row['record_hashes'].items()))
    earlier = read(BASE / 'reviewed-2026-10-02-1059/verification.json')
    check('initial concurrent-document failures retained', earlier['checks_total'] == 814 and earlier['checks_passed'] == 810)
    intermediate = read(BASE / 'reviewed-2026-10-02-1057/verification.json')
    check('intermediate snapshot refinement retained', intermediate['checks_total'] == intermediate['checks_passed'] == 823)
    package = read(REVIEW / 'reconstructable-authored-result.json')
    check('authored package preserves its result', package['reconstructed_sha256'] == package['original_sha256'] and package['chunks'] == 8)
    check('authored credential-pattern check', read(CAPTURE / 'credential-chunk-check.json')['total_known_matches'] == 0)
    editorial = read(BASE / 'editorial-review.json')
    check('four new prose documents reviewed', editorial['files_scanned'] == 4 and not editorial['flags'])
    for path in sorted(BASE.glob('*.md')):
        for destination in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in destination and not destination.startswith('#'):
                check('own prose navigation ' + path.name + ': ' + destination, (path.parent / destination.split('#')[0]).exists())
    for path in [ROOT / 'tools/verify_checkout_navigation.py', BASE / 'review_capture.py', Path(__file__)]:
        compile(path.read_text(encoding='utf-8'), str(path), 'exec')
        check('helper syntax ' + path.name, True)
    result = dict(completed_utc=datetime.now(timezone.utc).isoformat(), accepted_capture=CAPTURE.relative_to(ROOT).as_posix(), accepted_review=REVIEW.relative_to(ROOT).as_posix(), checks_total=len(checks), checks_passed=sum(r['passed'] for r in checks), checks=checks, unchanged_core_document_hashes=summary['document_hashes'])
    write(BASE / 'verification.json', result)
    files = [p for p in BASE.rglob('*') if p.is_file() and p.name != 'artifact-manifest.json' and '__pycache__' not in p.parts]
    files.append(ROOT / 'tools/verify_checkout_navigation.py')
    write(BASE / 'artifact-manifest.json', dict(scope='Own availability analysis, project-authored document snapshots, source routes and manual helpers; no copied third-party witnesses', files=[dict(path=p.relative_to(ROOT).as_posix(), bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(files)]))
    print(json.dumps(dict(checks=result['checks_total'], passed=result['checks_passed'], failures=[r for r in checks if not r['passed']], artifacts=len(files))))


if __name__ == '__main__':
    main()
