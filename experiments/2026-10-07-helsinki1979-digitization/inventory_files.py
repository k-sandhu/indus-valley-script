"""Inventory only the two owned directories and newly installed distributions."""
import hashlib
import json
from collections import Counter
from importlib.metadata import distribution
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-07-helsinki1979-digitization'
MANIFEST = HERE / 'file-manifest.jsonl'
SUMMARY = HERE / 'file-manifest-summary.json'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def main():
    counts = Counter()
    sizes = Counter()
    records = []
    for scope, base in [('owned', HERE), ('local_raw', RAW)]:
        for path in sorted(base.rglob('*')):
            if not path.is_file():
                continue
            # Self sizes/hashes would recurse; both artifacts are separately listed below.
            if path in (MANIFEST, SUMMARY):
                continue
            relative = str(path.relative_to(ROOT)).replace('\\', '/')
            size = path.stat().st_size
            records.append(dict(scope=scope, path=relative, bytes=size, sha256=sha(path)))
            counts[scope] += 1
            sizes[scope] += size
    for name in ('pymupdf', 'opencv-python-headless', 'jsonschema', 'attrs',
                 'jsonschema-specifications', 'referencing', 'rpds-py'):
        dist = distribution(name)
        for relative in sorted(dist.files or [], key=str):
            path = Path(dist.locate_file(relative)).resolve()
            if not path.is_file():
                continue
            size = path.stat().st_size
            scope = 'new_dependency:' + name
            records.append(dict(scope=scope, path=str(path), bytes=size, sha256=sha(path)))
            counts[scope] += 1
            sizes[scope] += size
    for path in (MANIFEST, SUMMARY):
        records.append(dict(scope='owned', path=str(path.relative_to(ROOT)).replace('\\', '/'),
                            bytes=None, sha256=None, reason='self-referential inventory artifact'))
    with MANIFEST.open('w', encoding='utf-8') as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    result = dict(status='Verified computation', counts=dict(counts), bytes_excluding_self=dict(sizes),
                  total_bytes_excluding_self=sum(sizes.values()), manifest_sha256=sha(MANIFEST),
                  self_files=['file-manifest.jsonl', 'file-manifest-summary.json'],
                  measurement_note='All present owned/raw files and installed distribution-record files. '
                                   'Existing source PDFs and pre-existing environment files are excluded. '
                                   'No payload is copied by this inventory.')
    SUMMARY.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
