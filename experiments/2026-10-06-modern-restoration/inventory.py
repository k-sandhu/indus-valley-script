"""Inventory created research files and local witnesses without moving them."""
from collections import Counter
import argparse
import json
from importlib import metadata
from pathlib import Path
import sys
from data import OWN, ROOT, RAW, digest, save

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true', help='Check all recorded hashes without writing files.')
    args = parser.parse_args()
    out = OWN / 'file-manifest.json'
    if args.verify:
        record = json.loads(out.read_text(encoding='utf-8'))
        checked = 0
        for entry in record['files']:
            if entry['sha256'] is None:
                continue
            path = Path(entry['path'])
            if not path.is_absolute():
                path = ROOT / path
            assert path.stat().st_size == entry['bytes'], f'Size changed: {path}'
            assert digest(path) == entry['sha256'], f'Hash changed: {path}'
            checked += 1
        print(json.dumps({'recorded_hashes_verified': checked, 'files_written': 0}))
        return
    if out.exists():
        raise FileExistsError(out)
    files, directories = [], []
    for root, handling in [(OWN, 'code-protocol-aggregate-or-prose'), (RAW, 'local-only')]:
        directories.append(str(root.relative_to(ROOT)).replace('\\', '/'))
        for path in sorted(root.rglob('*')):
            relative = str(path.relative_to(ROOT)).replace('\\', '/')
            if path.is_dir():
                directories.append(relative)
            elif path.is_file():
                files.append({'path': relative, 'bytes': path.stat().st_size,
                    'sha256': digest(path), 'handling': handling})
    installed = []
    for package in ['matplotlib', 'contourpy', 'cycler', 'fonttools', 'kiwisolver',
            'packaging', 'pillow', 'pyparsing']:
        distribution = metadata.distribution(package)
        installed.append({'package': package, 'version': distribution.version})
        for entry in distribution.files or []:
            path = Path(distribution.locate_file(entry)).resolve()
            assert path.is_relative_to(Path(sys.prefix).resolve())
            if path.is_file():
                files.append({'path': str(path).replace('\\', '/'),
                    'bytes': path.stat().st_size, 'sha256': digest(path),
                    'handling': 'authorized-plot-dependency', 'package': package})
    files.append({'path': str(out.relative_to(ROOT)).replace('\\', '/'),
        'sha256': None, 'bytes': None, 'handling': 'manifest-self-reference'})
    cleanup = json.loads((OWN / 'storage-cleanup.json').read_text(encoding='utf-8'))
    temporary = json.loads((OWN / 'temporary-cleanup.json').read_text(encoding='utf-8'))
    save(out, {'status': 'Verified computation', 'files': files, 'directories': directories,
        'removed_inner_seed_arrays': cleanup['files'],
        'removed_temporary_files': temporary['removed_files'],
        'counts': dict(Counter(f['handling'] for f in files)),
        'plot_packages_installed_in_authorized_environment': installed,
        'local_raw_bytes': sum(f['bytes'] for f in files if f['handling'] == 'local-only'),
        'note': 'No preexisting frozen endpoint or repository file outside the two assigned research directories was edited. Plotting packages were installed in the explicitly authorized CUDA environment; their recorded installation paths are included. The manifest lists itself without a circular hash.'})
    print(len(files), 'files inventoried')

if __name__ == '__main__':
    main()
