"""Inspect only Old Akkadian catalogue rows and ATF blocks; run with python -I.

Usage: python -I inspect_cdli.py --cat CSV --atf ATF --out NEW_JSONL
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path


def blocks(path):
    identity, lines, start = None, [], 0
    with path.open(encoding='utf-8-sig') as handle:
        for number, line in enumerate(handle, 1):
            if line.startswith('&'):
                if identity:
                    yield identity, lines, start
                identity, lines, start = line[1:8], [line.rstrip('\n')], number
            else:
                lines.append(line.rstrip('\n'))
    if identity:
        yield identity, lines, start


def main():
    ap = argparse.ArgumentParser()
    for arg in ('cat', 'atf', 'out'):
        ap.add_argument('--' + arg, required=True, type=Path)
    a = ap.parse_args()
    rows = {'P' + r['id_text'].zfill(6): r for r in csv.DictReader(a.cat.open(encoding='utf-8-sig', newline=''))
            if r['period'].startswith('Old Akkadian')}
    markers, counts = Counter(), Counter()
    with a.out.open('x', encoding='utf-8') as out:
        for identity, lines, start in blocks(a.atf):
            if identity not in rows:
                continue
            row = rows[identity]
            counts['old_akkadian_atf_blocks'] += 1
            if 'seal' in row['object_type'].lower() or any('seal' in line.lower() for line in lines):
                out.write(json.dumps(dict(id=identity, metadata=row, lines=lines, start=start), ensure_ascii=False) + '\n')
                counts['candidates'] += 1
                markers.update(line for line in lines if line.startswith('@') or line.startswith('#atf: lang'))
    print(json.dumps(dict(counts=counts, markers=markers), ensure_ascii=True))


if __name__ == '__main__':
    main()
