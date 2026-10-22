"""Prepare blinded identities. Run with Python isolated mode from the root."""
import collections
import csv
import hashlib
import json
import math
import random
import re
import subprocess
from pathlib import Path

ROOT = Path.cwd()
BASE = ROOT / 'experiments/2026-10-21-post-catalogue-finds'
OUT = BASE / 'verification'

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path, data, fields):
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)

def main():
    obj = rows(BASE / 'objects.csv')
    print('Object table headers:', list(obj[0]))
    parts = collections.defaultdict(list)
    for r in obj:
        tag = r.get('extracted_by', '')
        m = re.search(r'(?:run|part)[ -]?2?([NGDPEF])\b', tag, re.I)
        if not m:
            m = re.search(r'PCF-([NGDPEF])-', r.get('provisional_row_id', ''))
        if not m:
            m = re.search(r'2([NGDPEF])', tag, re.I)
        part = m.group(1).upper() if m else tag
        parts[part].append(r)
    n = min(60, len(obj))
    allocation = {p: min(5, len(v)) for p, v in parts.items()}
    if len(obj) <= 60:
        allocation = {p: len(v) for p, v in parts.items()}
    else:
        # Constrained proportional allocation, filled by largest remaining deficit.
        while sum(allocation.values()) < n:
            p = max((p for p in sorted(parts) if allocation[p] < len(parts[p])),
                    key=lambda p: n * len(parts[p]) / len(obj) - allocation[p])
            allocation[p] += 1
    rng = random.Random(20261021)
    page_groups = collections.defaultdict(list)
    for r in obj:
        page_groups[r['primary_publication'], r['pdf_page']].append(r['row_id'])
    selected = []
    for p in sorted(parts):
        for r in rng.sample(parts[p], allocation[p]):
            selected.append({k: r[k] for k in ('row_id', 'site', 'primary_publication', 'pdf_page')} | {
                'registration_or_position': r['registration'] or 'position:' + str(page_groups[r['primary_publication'], r['pdf_page']].index(r['row_id']) + 1)})
    write_csv(OUT / 'blind-assignments.csv', selected,
              ['row_id','site','primary_publication','pdf_page','registration_or_position'])
    manifest = {'seed': 20261021, 'population': len(obj), 'sample': len(selected),
                'part_populations': {p:len(v) for p,v in sorted(parts.items())},
                'part_allocations': allocation,
                'allocation_rule': 'Minimum five per available part, then largest proportional deficit; stable sorted part order and original table row order.',
                'inputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                           [BASE/'objects.csv', BASE/'sites.csv', BASE/'join-decisions.csv', BASE/'PROTOCOL.md', BASE/'AMENDMENT-1.md']}}
    (OUT/'sampling.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))
    print('BLIND ASSIGNMENTS')
    for r in selected:
        print(json.dumps(r))
    for folder in ('acquisition', 'acquisition-web', 'matching', 'review', 'extraction'):
        for p in sorted((BASE/folder).rglob('*.csv')):
            with p.open(encoding='utf-8-sig', newline='') as f:
                reader = csv.reader(f)
                print(str(p.relative_to(BASE)), next(reader, []))
    raw = ROOT/'data/raw/2026-10-21-post-catalogue-finds'
    for p in sorted(raw.glob('run*/text')):
        print('TEXT ROOT', str(p.relative_to(ROOT)), len(list(p.glob('*'))))

if __name__ == '__main__':
    try:
        main()
    except OSError as e:
        try:
            (OUT/'WRITE-FAILURE.txt').write_text('Stopped after an input/output error: '+type(e).__name__+'\n', encoding='utf-8')
        finally:
            raise SystemExit('Stopped after an input/output error.')
