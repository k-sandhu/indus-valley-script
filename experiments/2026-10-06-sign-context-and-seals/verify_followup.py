"""Check follow-up results, exact references and preserved prior endpoints."""
import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.special import logsumexp
from scipy.stats import false_discovery_control

import analyze as prior
import lecture_followup as new


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--original', default='post-launch-2026-10-07-02')
    ap.add_argument('--replicate', default='verification-post-launch-2026-10-07-02')
    ap.add_argument('--output', default='checks-post-launch-2026-10-07-02.json')
    args = ap.parse_args()
    dest = prior.OWN / args.output
    if dest.exists():
        raise FileExistsError('Choose a fresh check filename.')
    checks = []
    def check(name, value):
        checks.append({'check': name, 'passed': bool(value)})
        if not value:
            raise AssertionError(name)
    def load(file):
        return json.loads((prior.OWN / args.original / file).read_text(encoding='utf-8'))
    summary = load('summary.json')
    for key, p in [('input_sha256', prior.INPUT), ('amendment_sha256', new.AMENDMENT),
                   ('code_sha256', Path(new.__file__)), ('reused_analysis_code_sha256', prior.OWN / 'analyze.py')]:
        check('hash ' + key, prior.sha(p) == summary[key])
    for name, h in summary['output_hashes'].items():
        check('endpoint hash ' + name, prior.sha(prior.OWN / args.original / name) == h)
        if name != 'external-motifs.json':
            check('rerun hash ' + name, prior.sha(prior.OWN / args.replicate / name) == h)
        else:
            original = load(name)
            replicate = json.loads((prior.OWN / args.replicate / name).read_text(encoding='utf-8'))
            for key, value in original['external_object_list_local'].items():
                check('external rerun path ' + key,
                      replicate['external_object_list_local'][key] == value.replace('/' + args.original + '/', '/' + args.replicate + '/'))
            replicate['external_object_list_local'] = original['external_object_list_local']
            check('external aggregate rerun with path normalization', original == replicate)
            for suffix in ['json', 'csv']:
                check('external object list rerun ' + suffix,
                      prior.sha(prior.RAW / args.original / ('external-objects.' + suffix)) ==
                      prior.sha(prior.RAW / args.replicate / ('external-objects.' + suffix)))
    preserved = json.loads((prior.OWN / 'preservation-2026-10-07-02.json').read_text(encoding='utf-8'))
    for f in preserved['immutable_pins']:
        check('prior endpoint ' + f['path'], prior.sha(prior.ROOT / f['path']) == f['sha256'])
    check('prior manifest unchanged', prior.sha(prior.OWN / 'FILE-MANIFEST.json') == preserved['old_manifest_sha256'])
    old = json.loads((prior.OWN / 'FILE-MANIFEST.json').read_text(encoding='utf-8'))
    pins = {f['path']: f['sha256'] for f in old['files']}
    for file in preserved['mutable_living_documents']:
        original_path = (prior.OWN / file).relative_to(prior.ROOT).as_posix()
        check('archived living document ' + file,
              prior.sha(prior.OWN / preserved['archive'] / file) == pins[original_path])
    rows = [json.loads(l) for l in prior.INPUT.read_text(encoding='utf-8').splitlines()]
    _, principal, seals, _ = prior.grouping(rows)
    c = load('concentration.json')
    for view in c['views']:
        if view['view'] == 'all_faces':
            texts = [r['signs_reading_rtl'] for r in rows]
        elif view['view'] == 'principal_objects':
            texts = [r['signs_reading_rtl'] for r in principal]
        else:
            texts = {tuple(r['signs_reading_rtl']) for r in rows if r['signs_reading_rtl']}
        counts = Counter(s for seq in texts for s in seq)
        readable = Counter({s: n for s, n in counts.items() if s != '000'})
        N = sum(counts.values()) if view['denominator'] == 'all_positions' else sum(readable.values())
        check('concentration counts ' + view['view'] + '/' + view['denominator'],
              (len(texts), N, counts['740']) == (view['texts'], view['positions'], view['sign740_count']))
        rank = sorted(readable, key=lambda s: (-readable[s], s))
        check('concentration top ranks ' + view['view'] + '/' + view['denominator'],
              all(t['codes'] == rank[:t['k']] and t['count'] == sum(readable[s] for s in rank[:t['k']])
                  and abs(t['share'] - t['count'] / N) < 1e-15 for t in view['top_readable_codes']))
    # Compare the rarefaction formula with full enumeration of a small population.
    tokens = [0, 0, 0, 1, 2]
    for k in range(6):
        enumerated = np.mean([len(set(s)) for s in itertools.combinations(tokens, k)])
        check('exact small rarefaction k=' + str(k), abs(new.rarefy([3, 1, 1], 5, k) - enumerated) < 1e-12)
    check('Chao positive doubleton formula', new.unseen([1, 1, 1, 2, 4], 9) == (4., 3, 1))
    check('Chao zero doubleton formula', new.unseen([1, 1, 3], 5) == (.8, 2, 0))
    richness = load('richness.json')
    for site in richness['sites']:
        selected = [r for r in principal if r['site'] == site['site'] and any(s != '000' for s in r['signs_reading_rtl'])]
        codes = {s for r in selected for s in r['signs_reading_rtl'] if s != '000'}
        tokens_n = sum(sum(s != '000' for s in r['signs_reading_rtl']) for r in selected)
        check('site inventory ' + site['site'], (len(selected), tokens_n, len(codes)) ==
              (site['objects'], site['readable_tokens'], site['observed_richness']))
        for key in ['token_curve', 'object_curve']:
            cv = site[key]
            values = [v['expected_richness'] for v in cv['points']]
            at = next(v for v in cv['points'] if v['sample_units'] == cv['units'])
            check('curve limits/monotonicity ' + site['site'] + '/' + key,
                  values[0] == 0 and all(b >= a - 1e-9 for a, b in zip(values, values[1:]))
                  and at['expected_richness'] == len(codes) and cv['points'][-1]['sample_units'] == 2 * cv['units'])
    null = np.load(prior.RAW / args.original / 'site_richness_null.npy')
    names = richness['comparison']['sites_in_references']
    for t in richness['comparison']['tests']:
        values = null[:, names.index(t['site'])]
        mean = values.mean()
        exceed = np.count_nonzero(np.abs(values - mean) >= abs(t['observed'] - mean) - 1e-12)
        check('richness tail ' + t['site'], exceed == t['exceedances'] and (exceed + 1) / (len(values) + 1) == t['p'])
    def bh(name, tests, field='q_bh'):
        check(name, np.allclose(false_discovery_control([t['p'] for t in tests]), [t[field] for t in tests], rtol=0, atol=1e-12))
    bh('richness BH', richness['comparison']['tests'])
    # Conditional block construction guarantees both object and token counts.
    rr = [r for r in principal if any(s != '000' for s in r['signs_reading_rtl'])]
    length = np.array([sum(s != '000' for s in r['signs_reading_rtl']) for r in rr])
    labels = np.array([names.index(r['site']) for r in rr])
    strata = prior.blocks([(r['object_type'], int(n)) for r, n in zip(rr, length)])
    object_n, token_n = np.bincount(labels), np.bincount(labels, weights=length)
    rng = np.random.default_rng(55)
    for i in range(100):
        lab = prior.shuffle(labels, strata, rng)
        check('object/token preservation draw ' + str(i), np.array_equal(np.bincount(lab), object_n)
              and np.array_equal(np.bincount(lab, weights=length), token_n))
    terminal = load('terminal740.json')
    clean = [r for r in principal if r['complete_observed'] and r['single_line'] and r['direction'] in {'R/L', 'L/R'}
             and len(r['signs_reading_rtl']) >= 2 and '000' not in r['signs_reading_rtl']]
    pmfs = np.load(prior.RAW / args.original / 'terminal_logpmfs.npz')
    import re
    for t in terminal['groups']:
        selected = clean if t['level'] == 'global' else [r for r in clean if r[t['level']] == t['group']]
        cs = [r['signs_reading_rtl'].count('740') for r in selected]
        p = [c / len(r['signs_reading_rtl']) for c, r in zip(cs, selected)]
        y = sum(r['signs_reading_rtl'][-1] == '740' for r in selected)
        check('terminal counts ' + t['level'] + '/' + t['group'],
              (len(selected), sum(cs), y) == (t['objects'], t['sign740_occurrences'], t['objects_ending_740'])
              and abs(sum(p) - t['position_matched_expected_ending_objects']) < 1e-10)
        logpmf = pmfs[re.sub(r'[^A-Za-z0-9]', '_', t['level'] + '_' + t['group'])]
        fixed = int(sum(v == 1 for v in p))
        support = np.arange(len(logpmf)) + fixed
        check('terminal PMF moments ' + t['level'] + '/' + t['group'],
              abs(logsumexp(logpmf)) < 1e-10 and abs(np.dot(support, np.exp(logpmf)) - sum(p)) < 1e-9)
        tail = float(logsumexp(logpmf[max(0, y - fixed):]))
        check('terminal log tail ' + t['level'] + '/' + t['group'], abs(tail - t['log_p_upper']) < 1e-10)
    probs = [.2, .3, .4]
    exact = np.zeros(4)
    for z in itertools.product([0, 1], repeat=3):
        exact[sum(z)] += math.prod(p if v else 1 - p for v, p in zip(z, probs))
    check('small Poisson-binomial full enumeration', np.allclose(np.exp(new.log_poisson_binomial(probs)[0]), exact, atol=1e-15))
    bh('terminal context BH', [t for t in terminal['groups'] if t['included_in_context_correction']], 'q_bh_contexts')
    periods = load('period-stability.json')
    null = np.load(prior.RAW / args.original / 'period_null.npy')
    for j, t in enumerate(periods['tests']):
        values = np.abs(null[:, j]) if j == 1 else null[:, j]
        target = abs(t['observed']) if j == 1 else t['observed']
        exceed = np.count_nonzero(values >= target - 1e-12)
        check('period tail ' + t['outcome'], exceed == t['exceedances'] and (exceed + 1) / (len(values) + 1) == t['p'])
    bh('period BH', periods['tests'])
    fit = periods['interval_integrated_model']
    check('interval model converges away from boundaries', fit['optimizer_success'] and not fit['parameter_boundary'])
    check('profile endpoints hit chi-square threshold', np.allclose(fit['profile_LR_at_interval_edges'], 3.841458820694, atol=1e-7))
    check('profile at fitted change zero', abs(fit['profile_LR_at_fitted_change']) < 1e-6)
    check('ambiguous assignment enumeration 720', periods['ambiguous_assignment_sensitivity']['assignments'] == 720)
    e = load('external-motifs.json')
    for key, value in e['comparisons'].items():
        null = np.load(prior.RAW / args.original / (key + '_motif_null.npy'))
        for j, t in enumerate(value['tests']):
            mean = null[:, j].mean()
            exceed = np.count_nonzero(np.abs(null[:, j] - mean) >= abs(t['observed'] - mean) - 1e-12)
            check('external tail ' + key + '/' + t['outcome'],
                  exceed == t['exceedances'] and (exceed + 1) / (len(null) + 1) == t['p'])
        bh('external BH ' + key, value['tests'])
    for row in e['geography_motif_summaries']:
        check('external motif count sum ' + row['geography'] + '/' + row['object_type'],
              sum(row['motif_counts'].values()) == row['known_motif_objects']
              and row['known_motif_objects'] + row['unknown_motif_objects'] == row['seal_objects'])
    external = json.loads((prior.RAW / args.original / 'external-objects.json').read_text(encoding='utf-8'))
    check('external list unique physical families', len(external) == e['external_physical_objects_all_types']
          == len({r['object_family_id'] for r in external}))
    prior.write(dest, {'status': 'Verified computation', 'stage': 'post-launch amendment',
                       'passed': len(checks), 'failed': 0, 'checks': checks,
                       'original': args.original, 'replicate': args.replicate,
                       'scope': 'Preservation, deterministic outputs, count/curve invariants, exact terminal references and corrected reference tails.'})
    print(len(checks), 'checks passed; zero failures')


if __name__ == '__main__':
    run()
