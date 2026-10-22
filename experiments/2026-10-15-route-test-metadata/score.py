"""Score the Q-0009 crop readings and write the label mapping and coverage change.

Usage, from the repository root, after sample.py and the reading of every crop:

    python experiments/2026-10-15-route-test-metadata/score.py \
        --faces <path to data/normalized/lipi_observed_faces.jsonl> \
        --run experiments/2026-10-15-route-test-metadata/run-2026-10-15
"""
import argparse
import collections
import csv
import json
import math
from pathlib import Path

CODES = ('motif-present', 'motif-absent', 'not-decidable')
PLACEHOLDERS = ('None', '-', '?', 'Unknown', '')


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1-p)**(n-i) for i in range(k+1))


def clopper_pearson(k, n, alpha=0.05):
    if n == 0:
        return None
    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo+hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return round((lo+hi) / 2, 4)
    lower = 0.0 if k == 0 else solve(lambda p: 1 - binom_cdf(k-1, n, p) < alpha/2)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p) > alpha/2)
    return [lower, upper]


def verdict(present, absent):
    decidable = present + absent
    if decidable >= 5 and absent / decidable >= 0.9:
        return 'asserted-absence'
    if decidable and present / decidable >= 0.5:
        return 'missing-value'
    return 'mixed'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--faces', required=True)
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    run = Path(args.run)
    sample = {r['record_id']: r for r in csv.DictReader(open(run/'sample.csv', encoding='utf-8'))}
    observed = list(csv.DictReader(open(run/'observations.csv', encoding='utf-8')))
    assert {r['record_id'] for r in observed} == set(sample), 'every sampled crop needs exactly one reading'
    assert all(r['code'] in CODES for r in observed)

    strata = {}
    for name in sorted({r['stratum'] for r in observed}):
        rows = [r for r in observed if r['stratum'] == name]
        count = collections.Counter(r['code'] for r in rows)
        firm = collections.Counter(r['code'] for r in rows if r['confidence'] in ('high', 'medium'))
        present, absent = count['motif-present'], count['motif-absent']
        strata[name] = dict(
            seal_type=sorted({sample[r['record_id']]['seal_type'] for r in rows}),
            label=sorted({sample[r['record_id']]['label_class'] for r in rows}),
            crops=len(rows), counts={c: count[c] for c in CODES},
            present_share_of_decidable=round(present/(present+absent), 4) if present+absent else None,
            present_share_ci95=clopper_pearson(present, present+absent),
            verdict=verdict(present, absent),
            high_or_medium_confidence_only={c: firm[c] for c in CODES[:2]},
            verdict_high_or_medium_only=verdict(firm['motif-present'], firm['motif-absent']))
    controls_ok = strata['K']['counts']['motif-present'] >= 3

    faces = [json.loads(line) for line in open(args.faces, encoding='utf-8')]
    seal_objects = {}
    for face in faces:
        meta = face['metadata']
        if meta.get('type', '').startswith('SEAL'):
            seal_objects.setdefault(face['object_family_id'], (meta['type'], meta['symbol']))
    def status(seal_type, symbol):
        if symbol not in PLACEHOLDERS:
            return 'recorded'
        if symbol == 'None' and seal_type == 'SEAL:R':
            return 'asserted-absent'
        return 'missing-unknown'
    by_status = collections.Counter(status(t, s) for t, s in seal_objects.values())
    none_by_type = collections.Counter(t for t, s in seal_objects.values() if s == 'None')
    total = len(seal_objects)
    old_usable = sum(1 for t, s in seal_objects.values() if s not in PLACEHOLDERS or s == 'None')
    new_usable = by_status['recorded'] + by_status['asserted-absent']

    results = dict(
        date='2026-10-15', unit='seal faces (crops); coverage in seal objects (Lipi families)',
        controls_pass=controls_ok, strata=strata,
        seal_objects=total, seal_objects_with_none_by_type=dict(sorted(none_by_type.items())),
        seal_objects_by_status=dict(sorted(by_status.items())),
        seal_motif_coverage_inventory_rule=dict(objects=old_usable, percent=round(100*old_usable/total, 2)),
        seal_motif_coverage_mapping_v1=dict(objects=new_usable, percent=round(100*new_usable/total, 2)))
    (run/'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: results[k] for k in ('controls_pass', 'seal_objects_by_status', 'seal_motif_coverage_inventory_rule',
                                               'seal_motif_coverage_mapping_v1')}, indent=1))
    for name, s in strata.items():
        print(name, s['seal_type'], s['label'], s['counts'], s['present_share_ci95'], s['verdict'], s['verdict_high_or_medium_only'])


if __name__ == '__main__':
    main()
