"""Refresh authorized top-level copies from v6; frozen directories stay unchanged."""
from pathlib import Path
from hashlib import sha256
import json
import shutil
import argparse

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--amendments', default='amendments-2026-10-07-v6')
    ap.add_argument('--marker', default='v6-publication.json')
    args = ap.parse_args()
    marker = (OWN / args.marker).resolve()
    if not marker.is_relative_to(OWN):
        raise ValueError('Publication marker outside owned directory')
    if marker.exists():
        raise ValueError('v6 already published; preserve endpoint')
    endpoint = OWN / 'main-2026-10-07-v6'
    amendments = (OWN / args.amendments).resolve()
    if not amendments.is_relative_to(OWN):
        raise ValueError('Amendments outside owned directory')
    copies = []
    for directory in [endpoint, amendments]:
        for p in sorted(directory.iterdir()):
            if p.is_file() and p.suffix in ['.json', '.csv']:
                shutil.copyfile(p, OWN / p.name)
                copies.append({'file': p.name, 'source': p.relative_to(ROOT).as_posix(), 'sha256': sha256(p.read_bytes()).hexdigest()})
    manifest = {'status': 'Exploratory', 'endpoint': endpoint.relative_to(ROOT).as_posix(), 'amendments': amendments.relative_to(ROOT).as_posix(),
        'copies': copies, 'previous_top_level_state': 'pre-v6-2026-10-07/', 'existing_endpoints_changed': False,
        'input_state': 'Post coordinator title trims; upstream batch file manifests predate title edits',
        'code_at_copy_time': [{'file': p.name, 'sha256': sha256(p.read_bytes()).hexdigest()} for p in sorted(OWN.glob('*.py'))]}
    (OWN / 'OUTPUT-MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    marker.write_text(json.dumps({'date': '2026-10-07', 'copied_files': len(copies), 'manifest': 'OUTPUT-MANIFEST.json'}, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'copied_files': len(copies)}))


if __name__ == '__main__':
    main()
