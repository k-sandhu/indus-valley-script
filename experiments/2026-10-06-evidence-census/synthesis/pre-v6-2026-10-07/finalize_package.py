"""Expose aggregate endpoint copies, review title flags and inventory package files.

Copy/review mode refuses overwrites. Inventory mode writes a new manifest and
lists every file in the two owned roots, including preserved preliminary runs.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/synthesis'


def save(path, data):
    if path.exists():
        raise ValueError('Refusing to overwrite ' + str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--endpoint', help='Copy JSON/CSV aggregates from a completed owned endpoint')
    ap.add_argument('--inventory', help='New JSON inventory filename inside the owned package')
    args = ap.parse_args()
    if not args.endpoint and not args.inventory:
        ap.error('Choose --endpoint or --inventory')
    if args.endpoint:
        endpoint = (ROOT / args.endpoint).resolve()
        if not endpoint.is_relative_to(OWN) or endpoint == OWN:
            raise ValueError('Endpoint must be inside owned package')
        files = sorted(p for p in endpoint.iterdir() if p.suffix in ['.json', '.csv'])
        if any((OWN / p.name).exists() for p in files):
            raise ValueError('Aggregate copies already exist; preserve them')
        copies = []
        for p in files:
            shutil.copyfile(p, OWN / p.name)
            copies.append({'file': p.name, 'source': p.relative_to(ROOT).as_posix(),
                           'sha256': sha256(p.read_bytes()).hexdigest()})
        code = [{'file': p.name, 'sha256': sha256(p.read_bytes()).hexdigest()} for p in sorted(OWN.glob('*.py'))]
        save(OWN / 'OUTPUT-MANIFEST.json', {'status': 'Exploratory', 'endpoint': endpoint.relative_to(ROOT).as_posix(),
                                         'copies': copies, 'code_at_copy_time': code})
        audit = json.loads((OWN / 'source-title-audit.json').read_text(encoding='utf-8'))
        extended = {'DISC-4581a4748f51', 'DISC-a982b9029228', 'DISC-7259f17551cc', 'DISC-9e99ad200b7f'}
        reviews = [{'file': r['file'], 'record_id': r['record_id'],
                    'classification': 'extended_bookseller_or_review_metadata' if r['record_id'] in extended else 'prose_or_search_snippet_payload',
                    'action': 'Coordinator should retain exact bibliographic title and move/remove copied descriptive payload'} for r in audit['flags']]
        save(OWN / 'source-title-review.json', {'status': 'Exploratory', 'review': 'Manual inspection of flagged headers; no title text reproduced',
                                              'records': reviews, 'affected_files': audit['affected_files']})
        print(json.dumps({'copied_aggregates': len(copies), 'reviewed_title_headers': len(reviews)}))
    if args.inventory:
        target = (OWN / args.inventory).resolve()
        if not target.is_relative_to(OWN):
            raise ValueError('Inventory outside owned package')
        files = []
        for base, disposition in [(OWN, 'owned_research_outputs'), (RAW, 'local_only_raw')]:
            for p in sorted(base.rglob('*')):
                if p.is_file():
                    files.append({'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                                  'sha256': sha256(p.read_bytes()).hexdigest(), 'disposition': disposition})
        save(target, {'as_of': '2026-10-07', 'scope': 'All files in both B3 roots; includes preserved preliminary runs. The inventory lists itself separately to avoid a self-hash.',
                      'inventory_file': target.relative_to(ROOT).as_posix(), 'file_count_excluding_this_manifest': len(files), 'files': files})
        print(json.dumps({'inventory': target.name, 'listed_files': len(files)}))


if __name__ == '__main__':
    main()
