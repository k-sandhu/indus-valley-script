"""Inspect source data without importing any acquired code; run with python -I.

Usage: python -I inspect_inputs.py --held PATH --manifest PATH --out PATH
"""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def safe_members(archive):
    for name in archive.namelist():
        if PurePosixPath(name).is_absolute() or PureWindowsPath(name).is_absolute() or PureWindowsPath(name).drive or '..' in PurePosixPath(name.replace('\\', '/')).parts:
            raise ValueError('unsafe archive member')


def main():
    ap = argparse.ArgumentParser()
    for arg in ('held', 'manifest', 'out'):
        ap.add_argument('--' + arg, required=True, type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    with args.held.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    expected = manifest['source_hashes']['sumerian-ur3-v1.json']
    if isinstance(expected, dict):
        expected = expected['sha256']
    assert digest == expected, (digest, expected)
    with zipfile.ZipFile(args.held) as archive:
        safe_members(archive)
        catname = next(n for n in archive.namelist() if n.endswith('/catalogue.json'))
        cat = json.loads(archive.read(catname))
        (args.out / 'catalogue.json').write_text(json.dumps(cat, ensure_ascii=False), encoding='utf-8')
        names = [n for n in archive.namelist() if '/corpusjson/' in n and n.endswith('.json')]
        names.sort(key=lambda n: hashlib.sha256(f'20261012:{Path(n).stem}'.encode()).hexdigest())
        examples = []
        for name in names:
            data = json.loads(archive.read(name))
            if '"seal' in json.dumps(data):
                (args.out / Path(name).name).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
                examples.append(name)
                if len(examples) == 4:
                    break
    result = {'bytes': args.held.stat().st_size, 'sha256': digest, 'expected_sha256': expected,
              'matches': True, 'entries': len(names), 'samples': examples}
    (args.out / 'verification.json').write_text(json.dumps(result, indent=1), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
