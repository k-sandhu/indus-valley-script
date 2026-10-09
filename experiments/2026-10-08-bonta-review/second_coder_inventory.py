"""Inventory current contents and the second-coding phase without altering endpoints."""
from pdf_followup import ROOT, OWN, RAW, read, write, sha


def main():
    baseline_name = 'history/2026-10-09-before-second-coder/baseline-files.json'
    baseline = {r['path']: r['sha256'] for r in read(OWN / baseline_name)}
    rows = []
    registration_script = (OWN / 'register_second_coder.py').relative_to(ROOT).as_posix()
    for directory in (OWN, RAW):
        for path in sorted(directory.rglob('*')):
            if not path.is_file() or path.name in ('FILES.json', 'SECOND-CODER-FILES.json'):
                continue
            if '.git' in path.parts or '__pycache__' in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            digest = sha(path)
            action = ('Created' if relative not in baseline else
                      'Preserved' if baseline[relative] == digest else 'Changed')
            row = {'path': relative, 'bytes': path.stat().st_size, 'sha256': digest,
                   'phase_action': action,
                   'location': 'local raw' if path.is_relative_to(RAW) else 'owned'}
            if relative == registration_script:
                row['phase_action'] = 'Created'
                row['basis'] = 'Created for this phase before the baseline file census.'
            rows.append(row)
    write(OWN / 'FILES.json', {
        'date': '2026-10-09', 'phase': 'Independent second coding',
        'inventory_exclusions': ['FILES.json', 'SECOND-CODER-FILES.json', '__pycache__', '.git'],
        'rights': 'Third-party payloads and record-level derivatives are local raw only.',
        'baseline': baseline_name, 'files': rows})
    delta = [row for row in rows if row['phase_action'] != 'Preserved']
    delta.extend([
        {'path': (OWN / 'FILES.json').relative_to(ROOT).as_posix(),
         'phase_action': 'Changed', 'sha256': sha(OWN / 'FILES.json'), 'location': 'owned'},
        {'path': (OWN / 'SECOND-CODER-FILES.json').relative_to(ROOT).as_posix(),
         'phase_action': 'Created', 'sha256': None, 'location': 'owned',
         'basis': 'Self hash omitted to avoid recursion.'}])
    counts = {'created_paths': sum(row['phase_action'] == 'Created' for row in delta),
              'changed_paths': sum(row['phase_action'] == 'Changed' for row in delta),
              'preserved_existing_files': sum(row['phase_action'] == 'Preserved' for row in rows)}
    write(OWN / 'SECOND-CODER-FILES.json', {
        'date': '2026-10-09', 'phase': 'Independent second coding',
        'baseline': baseline_name, **counts, 'files': delta})
    print({'current_inventory_files': len(rows), **counts})


if __name__ == '__main__':
    main()
