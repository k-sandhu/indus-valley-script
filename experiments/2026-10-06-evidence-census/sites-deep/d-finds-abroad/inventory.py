"""List and hash all package files; verify without changing the manifest."""
import argparse, hashlib, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
OWNED = pathlib.Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    target = OWNED / 'file-manifest.json'
    records = []
    for directory, handling in [(OWNED, 'Code, paraphrased observations and aggregate outputs'),
                                (RAW, 'Local-only third-party witnesses and acquisition logs')]:
        for path in sorted(directory.rglob('*')):
            if path.is_file() and path != target:
                data = path.read_bytes()
                records.append(dict(path=path.relative_to(ROOT).as_posix(), bytes=len(data),
                                    sha256=hashlib.sha256(data).hexdigest(), handling=handling))
    records.append(dict(path=target.relative_to(ROOT).as_posix(), sha256=None,
                        handling='Manifest self-reference; own hash intentionally omitted'))
    records.sort(key=lambda value: value['path'])
    result = dict(date='2026-10-07', scope='Every file created or changed in the two owned package directories',
                  files=len(records), owned_files=sum(x['path'].startswith('experiments/') for x in records),
                  raw_files=sum(x['path'].startswith('data/') for x in records), records=records)
    payload = (json.dumps(result, indent=2) + '\n').encode('utf-8')
    if args.verify:
        assert target.read_bytes() == payload, 'Inventory differs'
    elif target.exists():
        assert target.read_bytes() == payload, 'Existing inventory differs; preserve it and choose a new endpoint'
    else:
        target.write_bytes(payload)
    print(json.dumps({key:result[key] for key in ('files', 'owned_files', 'raw_files')}))

if __name__ == '__main__':
    main()
