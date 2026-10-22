"""Study P: positional statistics of the October 11 leading codes within their frequency strata.

A single meaning moved to another code of the same stratum takes that code's statistic,
so the permutation distribution is the exact distribution over the stratum's codes.
"""
from collections import defaultdict
import math

import numpy as np

import common as C

OUT = C.HERE / 'positional'
NAMED = {  # code: (published statistic used as support, published value)
    '151': ('final', 9.436), '154': ('final', 6.752), '156': ('final', 5.447), '158': ('closing', None),
    '161': ('final', 5.101), '400': ('final', 19.514), '527': ('final', 10.079), '617': ('final', 5.462),
    '142': ('nonfinal', -3.618),
}


def code_statistics(strings, codes):
    """Final-position z with fixed analytic moments and closing-block counts, per code."""
    obs = defaultdict(float); exp = defaultdict(float); var = defaultdict(float)
    tokens = defaultdict(int); closing = defaultdict(int); closing_exp = defaultdict(float)
    for s in strings:
        seq = s['seq']
        L = len(seq)
        counts = defaultdict(int)
        for slot, c in enumerate(seq):
            counts[c] += 1
            tokens[c] += 1
            closing[c] += C.role_flags(seq, slot)['closing']
        obs[seq[-1]] += 1
        for c, n in counts.items():
            p = n / L
            exp[c] += p
            var[c] += p * (1 - p)
            closing_exp[c] += C.code_role_expectation(seq, c)['closing']
    rows = {}
    for c in codes:
        z = (obs[c] - exp[c]) / math.sqrt(var[c]) if var[c] > 0 else None
        rows[c] = {'tokens': tokens[c], 'final': obs[c], 'final_expectation': exp[c], 'final_z': z,
                   'nonfinal_z': -z if z is not None else None,
                   'closing': closing[c], 'closing_expectation': closing_exp[c],
                   'closing_excess': closing[c] - closing_exp[c],
                   'closing_share': closing[c] / tokens[c] if tokens[c] else None}
    return rows


def rank_in(values, target):
    """1-based rank from the top, ties counted at or above."""
    return int(sum(v >= target - C.TOL for v in values))


def main():
    if OUT.exists():
        raise SystemExit('Refusing to overwrite an existing endpoint')
    inputs = C.check_pins()
    strings = C.load_strings()
    prior = C.read_json('experiments/2026-10-11-bonta-adversarial/run-v6/catalogue-data.json')
    codes = sorted(r['code'] for r in prior['rows'])
    strata, count = C.strata_of(strings, codes)
    stats = code_statistics(strings, codes)
    by_stratum = defaultdict(list)
    for c in codes:
        if strata[c] >= 0 and stats[c]['final_z'] is not None:
            by_stratum[strata[c]].append(c)
    out = []
    for code, (kind, published) in NAMED.items():
        st = stats[code]
        members = by_stratum[strata[code]]
        row = {'code': 'W' + code, 'stratum': strata[code], 'stratum_bin': C.FREQ_BINS[strata[code]],
               'stratum_codes': len(members), 'published_support_statistic': kind,
               'published_value': published, **{k: st[k] for k in st}}
        for name in ['final_z', 'nonfinal_z', 'closing_excess', 'closing_share']:
            values = [stats[c][name] for c in members]
            target = st[name]
            top = max(members, key=lambda c: (stats[c][name], c))
            row[name + '_rank'] = rank_in(values, target)
            row[name + '_share_at_or_above'] = rank_in(values, target) / len(values)
            row[name + '_stratum_max'] = {'code': 'W' + top, 'value': stats[top][name]}
            row[name + '_stratum_median'] = float(np.median(values))
            row[name + '_stratum_codes_above_3'] = int(sum(v > 3 for v in values)) if name.endswith('_z') else None
        out.append(row)
    reproduced = {('W' + c): abs(stats[c]['final_z'] - v) < 5e-4 for c, (k, v) in NAMED.items()
                  if v is not None and k == 'final'}
    reproduced['W142'] = abs(stats['142']['final_z'] - NAMED['142'][1]) < 5e-4
    assert all(reproduced.values()), reproduced
    stratum_rows = {}
    for b, members in sorted(by_stratum.items()):
        z = [stats[c]['final_z'] for c in members]
        stratum_rows[str(b)] = {'bin': C.FREQ_BINS[b], 'codes': len(members),
                                'final_z_above_3': int(sum(v > 3 for v in z)),
                                'final_z_below_minus_3': int(sum(v < -3 for v in z)),
                                'final_z_max': max(z), 'final_z_median': float(np.median(z))}
    C.write_json(OUT / 'summary.json', {
        'status': 'Exact within-stratum distribution of published positional statistics',
        'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md'), 'code_sha256': C.sha(__file__), 'inputs': inputs,
        'population_strings': len(strings),
        'statistic_definitions': {
            'final_z': 'final-position count minus its within-string bag-shuffle expectation, over the square root of the fixed analytic variance, summed over the 1,859 distinct strings',
            'closing': 'last, or directly before terminal W400/W740 (anchor-expansion closing role)'},
        'published_values_reproduced': reproduced, 'named_codes': out, 'strata': stratum_rows})
    for r in out:
        print(r['code'], r['stratum_bin'], r['stratum_codes'], round(r['final_z'], 3), r['final_z_rank'],
              r['final_z_stratum_max'], r['closing_excess_rank'])


if __name__ == '__main__':
    main()
