"""Count motif placeholders and draw the fixed Q-0009 seal sample.

Reads the local Lipi faces file and the tracked face-image index and writes
placeholder counts, the sample table and input hashes into a new run directory.
Usage, from the repository root:

    python experiments/2026-10-15-route-test-metadata/sample.py \
        --faces <path to data/normalized/lipi_observed_faces.jsonl> \
        --out experiments/2026-10-15-route-test-metadata/run-2026-10-15
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

SALT = 'Q-0009-2026-10-15|'
INDEX = Path('experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv')
PLACEHOLDERS = ('None', '-', '?', 'Unknown', '')
STRATA = [  # id, type test, symbol test, n (None = all eligible)
    ('A', lambda t: t == 'SEAL:S', lambda s: s == 'None', 12),
    ('B', lambda t: t == 'SEAL:S', lambda s: s == '-', 8),
    ('C', lambda t: t == 'SEAL:R', lambda s: s == 'None', 8),
    ('D', lambda t: t == 'SEAL', lambda s: s == '-', 4),
    ('E', lambda t: t.startswith('SEAL'), lambda s: s in ('?', 'Unknown'), None),
    ('K', lambda t: t == 'SEAL:S', lambda s: s not in PLACEHOLDERS, 4),
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def group(object_type):
    for prefix, name in (('SEAL', 'seal'), ('TAB:B', 'tablet-bas-relief'), ('TAB:I', 'tablet-incised'),
                         ('TAB:C', 'tablet-copper'), ('TAG', 'tag-or-sealing'), ('POT', 'pottery')):
        if object_type.startswith(prefix):
            return name
    return 'other'


def label_class(value):
    return value if value in PLACEHOLDERS else 'named'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--faces', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    faces = [json.loads(line) for line in open(args.faces, encoding='utf-8')]
    links = collections.defaultdict(list)
    with open(INDEX, encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            if row['relation'] == 'face-side' and row['kind'] == 'object':
                links[row['record_id']].append(row)

    counts = {'symbol': collections.Counter(), 'cult': collections.Counter(), 'seal_symbol_by_type': collections.Counter()}
    objects = collections.defaultdict(set)
    for face in faces:
        meta = face['metadata']
        kind = group(meta.get('type', ''))
        for field in ('symbol', 'cult'):
            counts[field][(kind, label_class(meta.get(field, '')))] += 1
        if kind == 'seal':
            counts['seal_symbol_by_type'][(meta['type'], label_class(meta['symbol']))] += 1
            objects[label_class(meta['symbol'])].add(face['object_family_id'])
    placeholder_counts = {
        'unit': 'faces',
        'symbol_by_object_group': [dict(group=g, label=l, faces=n) for (g, l), n in sorted(counts['symbol'].items())],
        'cult_by_object_group': [dict(group=g, label=l, faces=n) for (g, l), n in sorted(counts['cult'].items())],
        'seal_symbol_by_seal_type': [dict(type=t, label=l, faces=n)
                                     for (t, l), n in sorted(counts['seal_symbol_by_type'].items())],
        'seal_objects_by_symbol_label': {l: len(ids) for l, ids in sorted(objects.items())},
        'seal_faces': sum(counts['seal_symbol_by_type'].values()),
        'seal_objects': len(set().union(*objects.values())),
    }

    rows, eligible = [], {}
    for stratum, type_test, symbol_test, n in STRATA:
        pool = [f for f in faces
                if type_test(f['metadata'].get('type', '')) and symbol_test(f['metadata'].get('symbol', ''))
                and links.get(f['record_id'])]
        eligible[stratum] = len(pool)
        pool.sort(key=lambda f: hashlib.sha256((SALT + f['record_id']).encode()).hexdigest())
        for rank, face in enumerate(pool if n is None else pool[:n], 1):
            crop = sorted(links[face['record_id']], key=lambda r: r['file'])[0]
            rows.append(dict(stratum=stratum, rank=rank, record_id=face['record_id'],
                             object_family_id=face['object_family_id'], cisi=face['metadata'].get('cisi', ''),
                             seal_type=face['metadata']['type'], label_class=label_class(face['metadata']['symbol']),
                             file=crop['file'], file_sha256=crop['sha256']))
    with open(out/'sample.csv', 'w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    placeholder_counts['eligible_faces_by_stratum'] = eligible
    (out/'placeholder-counts.json').write_text(json.dumps(placeholder_counts, indent=2) + '\n', encoding='utf-8')
    hashes = {'lipi_observed_faces.jsonl': sha256(args.faces), str(INDEX.as_posix()): sha256(INDEX),
              'sample.py': sha256(Path(__file__)), 'PROTOCOL.md': sha256(Path(__file__).with_name('PROTOCOL.md'))}
    (out/'input-hashes.json').write_text(json.dumps(hashes, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sample_rows': len(rows), 'eligible': eligible}))


if __name__ == '__main__':
    main()
