"""Inventory current package files and the PDF-review response delta."""
from pdf_followup import ROOT, OWN, RAW, read, write, sha


def main():
    baseline_name = 'history/2026-10-09-before-pdf-review/baseline-files.json'
    old = {r['path']: r['sha256'] for r in read(OWN / baseline_name)}
    rows = []
    registration = (OWN / 'register_pdf_review.py').relative_to(ROOT).as_posix()
    for base in (OWN, RAW):
        for path in sorted(base.rglob('*')):
            if not path.is_file() or path.name in ['FILES.json', 'PDF-REVIEW-FILES.json']:
                continue
            if '.git' in path.parts or '__pycache__' in path.parts:
                continue
            name = path.relative_to(ROOT).as_posix(); digest = sha(path)
            row = {'path': name, 'bytes': path.stat().st_size, 'sha256': digest,
                   'phase_action': ('Created' if name not in old else
                                    'Preserved' if old[name] == digest else 'Changed'),
                   'location': 'local raw' if path.is_relative_to(RAW) else 'owned'}
            if name == registration:
                row['phase_action'] = 'Created'
                row['basis'] = 'Created for this response before the baseline census.'
            rows.append(row)
    write(OWN / 'FILES.json', {'date': '2026-10-09', 'phase': 'PDF-extension review response',
        'inventory_exclusions': ['FILES.json', 'PDF-REVIEW-FILES.json', '.git', '__pycache__'],
        'rights': 'Third-party witnesses, source rows, renders and per-query predictions remain local raw.',
        'baseline': baseline_name, 'files': rows})
    changed = [r for r in rows if r['phase_action'] != 'Preserved']
    changed += [
        {'path': (OWN / 'FILES.json').relative_to(ROOT).as_posix(), 'phase_action': 'Changed',
         'sha256': sha(OWN / 'FILES.json'), 'location': 'owned'},
        {'path': (OWN / 'PDF-REVIEW-FILES.json').relative_to(ROOT).as_posix(), 'phase_action': 'Created',
         'sha256': None, 'location': 'owned', 'basis': 'Self hash omitted.'}]
    counts = {'created_paths': sum(r['phase_action'] == 'Created' for r in changed),
              'changed_paths': sum(r['phase_action'] == 'Changed' for r in changed),
              'preserved_existing_files': sum(r['phase_action'] == 'Preserved' for r in rows)}
    write(OWN / 'PDF-REVIEW-FILES.json', {'date': '2026-10-09', 'phase': 'PDF-extension review response',
        'baseline': baseline_name, **counts, 'files': changed})
    print({'current_inventory_files': len(rows), **counts})


if __name__ == '__main__':
    main()
