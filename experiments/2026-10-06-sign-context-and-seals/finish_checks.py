"""Recompute exploratory reference tails and all recorded BH corrections.

This complements verify.py's frozen endpoint and arithmetic checks. Run from
the repository root; choose fresh --output names for later reviewer checks.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import false_discovery_control

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exploratory', default='exploratory-2026-10-07-01')
    ap.add_argument('--supplement', default='verification-supplement-2026-10-07-01')
    ap.add_argument('--output', default='final-checks-2026-10-07-01.json')
    args = ap.parse_args()
    dest = OWN / args.output
    if dest.exists():
        raise FileExistsError('Choose a fresh check filename.')
    load = lambda name: json.loads((OWN / name).read_text(encoding='utf-8'))
    checks = []

    def check(name, result):
        checks.append({'check': name, 'passed': bool(result)})
        if not result:
            raise AssertionError(name)

    def bh(name, tests, field='q_bh'):
        q = false_discovery_control([t['p'] for t in tests], method='bh')
        check(name, np.allclose(q, [t[field] for t in tests], rtol=0, atol=1e-12))

    e = load(args.exploratory + '/results.json')
    nu = np.load(RAW / args.exploratory / 'site_size_grouped_null.npy')
    tails = 0
    for j, key in enumerate(['3', '20']):
        tests = e['site_size_grouped_permutation'][key]['tests']
        bh('exploratory size BH ' + key, tests)
        for i, t in enumerate(tests):
            count = np.count_nonzero(np.abs(nu[:, j, i]) >= abs(t['observed']) - 1e-12)
            check('exploratory size tail ' + key + ' ' + t['sign'],
                  count == t['exceedances'] and (count + 1) / (len(nu) + 1) == t['p'])
            tails += 1
    mt = e['motif_length_conditioned']['tests']
    bh('length-conditioned five-outcome BH', mt[:-1], 'q_bh_five_variable_outcomes')
    nu = np.load(RAW / args.exploratory / 'motif_length_conditioned_null.npy')
    for j, t in enumerate(mt):
        count = (np.count_nonzero(nu[:, j] >= t['observed'] - 1e-12) if j < 3 else
                 np.count_nonzero(np.abs(nu[:, j]) >= abs(t['observed']) - 1e-12))
        check('length-conditioned tail ' + t['outcome'],
              count == t['exceedances'] and (count + 1) / (len(nu) + 1) == t['p'])
        tails += 1
    check('length-conditioned mean difference fixed in every draw',
          np.allclose(nu[:, -1], mt[-1]['observed'], rtol=0, atol=1e-12))
    for key, fn in [('analysis_code_sha256', 'analyze.py'),
                    ('sensitivity_code_sha256', 'sensitivity.py'),
                    ('amendment_sha256', 'AMENDMENT-2026-10-07.md')]:
        check('exploratory frozen hash ' + fn,
              hashlib.sha256((OWN / fn).read_bytes()).hexdigest() == e[key])
    s = load('run-2026-10-07-01/sign-analysis.json')
    bh('site BH', s['site_omnibus']['tests'])
    for key, result in s['size_comparisons'].items():
        bh('original size BH ' + key, result['tests'])
    m = load('run-2026-10-07-01/motif-association.json')
    for key in ['primary_rare', 'all_nonunicorn_sensitivity']:
        bh('motif BH ' + key, m[key]['tests'])
    by_site = [t for value in m['by_site'].values() for t in value['tests']]
    bh('18 site/outcome BH', by_site, 'q_bh_across_sites_and_outcomes')
    bh('dimension BH', load('run-2026-10-07-01/dimensions.json')['tests'])
    a = OWN / 'supplement-2026-10-07-01/dimension-coverage.json'
    b = OWN / args.supplement / 'dimension-coverage.json'
    check('supplement deterministic bytes', a.read_bytes() == b.read_bytes())
    result = {'status': 'Verified computation', 'checks': checks,
              'passed': len(checks), 'failed': 0, 'exploratory_tails_recomputed': tails,
              'BH_implementation': 'scipy.stats.false_discovery_control, method=bh',
              'exploratory': args.exploratory, 'supplement_replicate': args.supplement}
    dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(len(checks), 'final checks passed;', tails, 'exploratory tails recomputed')


if __name__ == '__main__':
    run()
