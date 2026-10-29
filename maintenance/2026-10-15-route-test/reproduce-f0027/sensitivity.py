"""Exploratory: does F-0027 depend on the single-line, one-face-per-object population?

Chosen after the recount matched. Counts pairs of distinct seal objects (Lipi families) that share an
identical complete text of six or more signs, first among every complete seal face with no unknown sign at
a South Asian site (multi-line faces and second faces included), then with sites outside South Asia added.
Reading order is the export's reading-order sequence; for a multi-line face it is the export's concatenation.
Usage, from the repository root:

    python experiments/2026-10-15-route-test/reproduce-f0027/sensitivity.py \
        --faces <path to data/normalized/lipi_observed_faces.jsonl> \
        --out experiments/2026-10-15-route-test/reproduce-f0027/run-2026-10-15/sensitivity.json
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

OUTSIDE_REGIONS = {'Persian Gulf', 'Mesopotamia', 'Central Asia'}
OUTSIDE_SITES = {'Susa', 'Luristan'}


def shared_pairs(faces, south_asia_only):
    families = defaultdict(set)
    for f in faces:
        signs = f['signs_reading_rtl']
        if not f['object_type'].startswith('SEAL') or not f['complete_observed'] or f['has_unknown_sign']:
            continue
        if len(signs) < 6:
            continue
        outside = f['region'] in OUTSIDE_REGIONS or f['site'] in OUTSIDE_SITES or f['site'] in ('Unknown', '', None)
        if south_asia_only and outside:
            continue
        families[tuple(signs)].add(f['object_family_id'])
    shared = [ids for ids in families.values() if len(ids) > 1]
    return dict(distinct_texts=len(families), objects=len(set().union(*families.values())) if families else 0,
                texts_on_two_or_more_objects=len(shared),
                object_pairs=sum(len(ids) * (len(ids) - 1) // 2 for ids in shared),
                family_ids_of_shared_texts=sorted(sorted(ids, key=int) for ids in shared))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--faces', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    faces = [json.loads(line) for line in open(args.faces, encoding='utf-8')]
    result = dict(status='exploratory, chosen after the recount matched', unit='seal objects (Lipi families)',
                  all_faces_south_asia=shared_pairs(faces, True), all_faces_all_sites=shared_pairs(faces, False))
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f'{out} exists; write to a new path')
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: {x: y for x, y in v.items() if x != 'family_ids_of_shared_texts'} if isinstance(v, dict) else v
                      for k, v in result.items()}, indent=1))
    print(result['all_faces_all_sites']['family_ids_of_shared_texts'])


if __name__ == '__main__':
    main()
