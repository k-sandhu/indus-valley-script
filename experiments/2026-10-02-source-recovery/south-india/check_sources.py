"""Check saved source bytes, actual formats and observation page coordinates.

This checks preservation and coordinate consistency. Archaeological readings
require the separate visual review; the script does not extract their meaning.
"""
import argparse
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-02-source-recovery/south-india'
PRIOR = ROOT / 'data/raw/2026-10-02-connections-and-priority/south-india'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='verification.json')
    args = parser.parse_args()
    out = HERE / args.output
    if out.exists():
        raise FileExistsError('Use a new output name; preserve earlier checks')
    checks = []
    acquisitions = []
    for manifest in sorted(HERE.glob('*.acquisition.json')):
        record = json.loads(manifest.read_text(encoding='utf-8'))
        path = ROOT / record['local_path']
        content = path.read_bytes()
        checks.append({'check': str(manifest.name) + ' bytes',
                       'pass': len(content) == record['bytes'] and digest(path) == record['sha256']})
        is_pdf = content.startswith(b'%PDF-')
        item = {'manifest': manifest.name, 'path': record['local_path'],
                'http_status': record['http_status'], 'actual_pdf': is_pdf,
                'bytes': len(content), 'sha256': digest(path)}
        if is_pdf:
            with fitz.open(path) as doc:
                item['pdf_pages'] = len(doc)
        acquisitions.append(item)
    vol2 = PRIOR / 'inscribed-potsherds-vol2-2026.pdf'
    checks.append({'check': 'inherited volume II exact bytes', 'pass': digest(vol2) ==
                   '4e845dd57bd1ef2433f30b74afd7cb6427e5acae2d6fe631a6510dd6b97d28dc'})
    records = json.loads((HERE / 'observations.json').read_text(encoding='utf-8'))
    page_checks = []
    for record in records['observations']:
        source = (PRIOR if record['source'].startswith('inscribed-') else RAW) / record['source']
        with fitz.open(source) as doc:
            valid = all(1 <= loc['pdf_page'] <= len(doc) for loc in record['locators'])
            page_checks.append({'id': record['id'], 'source_sha256': digest(source),
                                'locators': record['locators'], 'pages_in_bounds': valid})
            checks.append({'check': record['id'] + ' page bounds', 'pass': valid})
    checks.append({'check': 'one object registration per observation', 'pass':
                   len({r['id'] for r in records['observations']}) == len(records['observations'])})
    derivatives = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                    'sha256': digest(p)} for p in sorted(RAW.glob('*.png'))]
    result = {'study': 'TN-SOURCE-02', 'scope': __doc__.strip(),
              'passed': all(c['pass'] for c in checks), 'checks': checks,
              'acquisitions': acquisitions, 'observation_coordinates': page_checks,
              'local_only_derivatives': derivatives,
              'visual_review': 'independent-review.json'}
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'acquisitions': len(acquisitions),
                      'local_only_pngs': len(derivatives)}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
