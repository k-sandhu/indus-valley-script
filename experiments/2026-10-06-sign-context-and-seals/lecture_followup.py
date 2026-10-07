"""Exploratory post-launch lecture comparisons; see the dated amendment.

Run from the repository root. Requires NumPy and SciPy. Original D2 code and
endpoints are read-only inputs; detailed object derivatives stay in RAW.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize, minimize_scalar
from scipy.special import expit, gammaln, logit, logsumexp
from scipy.stats import beta, chi2

import analyze as prior

OWN, ROOT, RAW = prior.OWN, prior.ROOT, prior.RAW
AMENDMENT = OWN / 'AMENDMENT-2026-10-07-LECTURE.md'
STAGE = {'status': 'Exploratory', 'stage': 'post-launch amendment',
         'protocol': AMENDMENT.name}
CORE = {'Lower Indus', 'Upper Indus', 'Inter-Riverine', 'Eastern Headwaters', 'Gujarat/Kutch'}
EXTERNAL = {'Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia'}


def save(path, result):
    prior.write(path, dict(STAGE, **result))


def centred_tail(observed, null):
    mean = float(np.mean(null))
    result = prior.tail(observed - mean, np.asarray(null) - mean, absolute=True)
    result.update(observed=float(observed), reference_mean=mean,
                  reference_95_interval=np.quantile(null, [.025, .975]).tolist(),
                  tail_rule='absolute deviation from reference mean')
    return result


def unseen(freq, units):
    f = np.asarray(freq, int)
    f1, f2 = int(np.count_nonzero(f == 1)), int(np.count_nonzero(f == 2))
    value = ((units - 1) / units * (f1 * f1 / (2 * f2) if f2 else f1 * (f1 - 1) / 2)
             if units else 0.)
    return float(value), f1, f2


def rarefy(freq, units, k):
    """Exact expected richness in a subset; combinatorial, no token resampling."""
    f = np.asarray(freq, int)
    f = f[f > 0]
    if k == 0:
        return 0.
    if k == units:
        return float(len(f))
    if not 0 <= k <= units:
        raise ValueError('Rarefaction k must be in [0, units].')
    missing = np.zeros(len(f))
    valid = units - f >= k
    log_den = gammaln(units + 1) - gammaln(k + 1) - gammaln(units - k + 1)
    missing[valid] = np.exp(gammaln(units - f[valid] + 1) - gammaln(k + 1)
                            - gammaln(units - f[valid] - k + 1) - log_den)
    return float(np.sum(1 - missing))


def curve(freq, units):
    f = np.asarray(freq, int)
    richness = int(np.count_nonzero(f))
    f0, f1, f2 = unseen(f, units)
    points = sorted(set([0, units, 2 * units] +
                        np.rint(np.linspace(0, 2 * units, 41)).astype(int).tolist() +
                        [v for v in [1, 10, 20, 50, 100, 200, 500, 1000] if v <= 2 * units]))
    out = []
    for k in points:
        if k <= units:
            value = rarefy(f, units, k)
        elif f0 > 0:
            discovery = f1 / (units * f0 + f1)
            value = richness + f0 * (-math.expm1((k - units) * math.log1p(-discovery)))
        else:
            value = float(richness)
        out.append({'sample_units': k, 'expected_richness': value,
                    'method': 'rarefaction' if k < units else 'observed' if k == units else 'extrapolation'})
    return {'units': units, 'observed_richness': richness, 'singletons': f1, 'doubletons': f2,
            'unseen_lower_bound': f0, 'asymptotic_lower_bound': richness + f0,
            'asymptotic_interpretation_available': units > 1 and f0 > 0,
            'points': out}


def richness_analysis(rows, principal, B, rng, raw):
    rr = [r for r in principal if any(s != '000' for s in r['signs_reading_rtl'])]
    sites = sorted({r['site'] for r in rr})
    codes = sorted({s for r in rr for s in r['signs_reading_rtl'] if s != '000'})
    site_id = {s: i for i, s in enumerate(sites)}
    code_id = {s: i for i, s in enumerate(codes)}
    labels = np.array([site_id[r['site']] for r in rr])
    token = np.zeros((len(rr), len(codes)), int)
    for i, r in enumerate(rr):
        for s, count in Counter(r['signs_reading_rtl']).items():
            if s != '000':
                token[i, code_id[s]] = count
    incidence = token > 0
    obj_ix, sign_ix = np.where(incidence)
    lengths = token.sum(1)
    strata = prior.blocks([(r['object_type'], int(n)) for r, n in zip(rr, lengths)])
    ns = np.bincount(labels, minlength=len(sites))
    nt = np.bincount(labels, weights=lengths, minlength=len(sites)).astype(int)

    def richness(lab):
        a = np.bincount(lab[obj_ix] * len(codes) + sign_ix,
                        minlength=len(sites) * len(codes)).reshape(len(sites), len(codes))
        return np.count_nonzero(a, axis=1)

    observed = richness(labels)
    null = np.empty((B, len(sites)), np.int16)
    for b in range(B):
        shuffled = prior.shuffle(labels, strata, rng)
        if b == 0:
            assert np.array_equal(ns, np.bincount(shuffled, minlength=len(sites)))
            assert np.array_equal(nt, np.bincount(shuffled, weights=lengths, minlength=len(sites)).astype(int))
        null[b] = richness(shuffled)
    np.save(raw / 'site_richness_null.npy', null)
    eligible = [i for i, s in enumerate(sites) if ns[i] >= 20 and s != 'Unknown']
    tests = [dict(site=sites[i], objects=int(ns[i]), readable_tokens=int(nt[i]),
                  **centred_tail(observed[i], null[:, i])) for i in eligible]
    for t, q in zip(tests, prior.bh([t['p'] for t in tests])):
        t['q_bh'] = q
    mean, sd = null.mean(0), null.std(0, ddof=1)
    variable = [i for i in eligible if sd[i] > 0]
    z = np.abs((null[:, variable] - mean[variable]) / sd[variable])
    critical = float(np.quantile(z.max(1), .95)) if variable else 0.
    for t, i in zip(tests, eligible):
        t.update(reference_sd=float(sd[i]),
                 simultaneous_95_band=[max(0., float(mean[i] - critical * sd[i])),
                                       float(mean[i] + critical * sd[i])],
                 outside_simultaneous_band=bool(sd[i] > 0 and abs(observed[i] - mean[i]) > critical * sd[i]))
    allface = defaultdict(set)
    for r in rows:
        allface[r['site']].update(s for s in r['signs_reading_rtl'] if s != '000')
    table = {r['site']: r for r in json.loads((OWN / 'site-table.json').read_text(encoding='utf-8'))['sites']}
    site_rows = []
    for i, s in enumerate(sites):
        ix = labels == i
        site_rows.append({'site': s, 'objects': int(ns[i]), 'readable_tokens': int(nt[i]),
                          'observed_richness': int(observed[i]), 'allface_richness': len(allface[s]),
                          'area_reference_ha': table.get(s, {}).get('area_reference'),
                          'site_type': table.get(s, {}).get('site_type'),
                          'token_curve': curve(token[ix].sum(0), int(nt[i])),
                          'object_curve': curve(incidence[ix].sum(0), int(ns[i])),
                          'reference_richness_mean': float(mean[i]),
                          'reference_richness_95_interval': np.quantile(null[:, i], [.025, .975]).tolist()})
    return {'sites': site_rows, 'shared_token_curve': curve(token.sum(0), int(nt.sum())),
            'shared_object_curve': curve(incidence.sum(0), len(rr)),
            'comparison': {'objects': len(rr), 'sites_in_references': sites,
                           'eligible_sites': [sites[i] for i in eligible],
                           'type_length_blocks': len(strata),
                           'movable_objects': sum(len(ix) for ix in strata if len(set(labels[ix])) > 1),
                           'object_and_token_counts_preserved': True,
                           'simultaneous_critical_abs_z': critical, 'tests': tests,
                           'shared_curve_scope': 'Acquired pooled inventories conditional on site counts, exact type and readable length.'}}


def concentration(rows, principal):
    unique = [list(t) for t in sorted({tuple(r['signs_reading_rtl']) for r in rows if r['signs_reading_rtl']})]
    views = {'all_faces': [r['signs_reading_rtl'] for r in rows],
             'principal_objects': [r['signs_reading_rtl'] for r in principal], 'unique_full_texts': unique}
    out = []
    for name, texts in views.items():
        counts = Counter(s for text in texts for s in text)
        readable = Counter({s: n for s, n in counts.items() if s != '000'})
        ranks = sorted(readable, key=lambda s: (-readable[s], s))
        for denominator in ['all_positions', 'readable_positions']:
            N = sum(counts.values()) if denominator == 'all_positions' else sum(readable.values())
            top = [{'k': k, 'codes': ranks[:k], 'count': sum(readable[s] for s in ranks[:k]),
                    'share': sum(readable[s] for s in ranks[:k]) / N,
                    'lecture_share': target,
                    'difference_percentage_points': 100 * (sum(readable[s] for s in ranks[:k]) / N - target)}
                   for k, target in [(3, .20), (6, .30), (20, .50)]]
            out.append({'view': name, 'denominator': denominator, 'texts': len(texts),
                        'positions': N, 'unreadable_positions': counts['000'],
                        'sign740_count': counts['740'], 'sign740_share': counts['740'] / N,
                        'sign740_difference_percentage_points': 100 * (counts['740'] / N - .10),
                        'top_readable_codes': top,
                        'all_code_ranking_including_placeholder':
                        [{'k': k, 'codes': sorted(counts, key=lambda s: (-counts[s], s))[:k],
                          'share_of_all_positions': sum(counts[s] for s in sorted(counts, key=lambda s: (-counts[s], s))[:k]) / sum(counts.values())}
                         for k in [3, 6, 20]] if denominator == 'all_positions' else None})
    return {'deduplication': 'Exact full normalized sequence before excluding 000; no site or physical linking by text.',
            'views': out}


def log_poisson_binomial(probabilities):
    fixed = int(sum(p == 1 for p in probabilities))
    logpmf = np.array([0.])
    for p in probabilities:
        if p == 0 or p == 1:
            continue
        next_pmf = np.full(len(logpmf) + 1, -np.inf)
        next_pmf[:-1] = logpmf + math.log1p(-p)
        next_pmf[1:] = np.logaddexp(next_pmf[1:], logpmf + math.log(p))
        logpmf = next_pmf
    return logpmf, fixed


def terminal_analysis(principal, Bboot, rng, raw):
    clean = [r for r in principal if r['complete_observed'] and r['single_line']
             and r['direction'] in {'R/L', 'L/R'} and r['signs_reading_rtl']
             and '000' not in r['signs_reading_rtl']]
    rr = [r for r in clean if len(r['signs_reading_rtl']) >= 2]
    all_groups = [('global', 'all', rr)]
    for key in ['site', 'object_type']:
        all_groups += [(key, value, [r for r in rr if r[key] == value]) for value in sorted({r[key] for r in rr})]
    output = []
    local = {}
    for level, name, rs in all_groups:
        texts = [r['signs_reading_rtl'] for r in rs]
        cs = np.array([s.count('740') for s in texts])
        probs = np.array([c / len(s) for c, s in zip(cs, texts)])
        ending = np.array([s[-1] == '740' for s in texts], int)
        observed = int(ending.sum())
        logpmf, fixed = log_poisson_binomial(probs)
        threshold = max(0, observed - fixed)
        logtail = float(logsumexp(logpmf[threshold:])) if threshold < len(logpmf) else -math.inf
        p = math.exp(max(math.log(1e-300), min(0., logtail)))
        refcdf = np.cumsum(np.exp(logpmf))
        ref_interval = [int(np.searchsorted(refcdf, q)) + fixed for q in [.025, .975]]
        delta = ending - probs
        bs = np.zeros(Bboot)
        for ix in prior.blocks([r['object_type'] for r in rs]):
            w = rng.multinomial(len(ix), np.repeat(1 / len(ix), len(ix)), size=Bboot)
            bs += w @ delta[ix]
        ci = np.quantile(bs / len(rs), [.025, .975]).tolist()
        row = {'level': level, 'group': name, 'objects': len(rs), 'sign740_occurrences': int(cs.sum()),
               'objects_with_740': int(np.count_nonzero(cs)), 'objects_ending_740': observed,
               'fraction_740_occurrences_terminal': observed / int(cs.sum()) if cs.sum() else None,
               'ending_text_rate': observed / len(rs), 'position_matched_expected_ending_objects': float(probs.sum()),
               'expected_ending_rate': float(probs.mean()), 'excess_ending_rate': float(delta.mean()),
               'excess_rate_component_bootstrap_95_ci': ci,
               'reference_ending_count_95_interval': ref_interval, 'p': p, 'log_p_upper': logtail,
               'p_floored_at_1e_300': logtail < math.log(1e-300),
               'included_in_context_correction': level != 'global' and len(rs) >= 20}
        output.append(row)
        local[re.sub(r'[^A-Za-z0-9]', '_', level + '_' + name)] = logpmf
    tests = [r for r in output if r['included_in_context_correction']]
    for r, q in zip(tests, prior.bh([r['p'] for r in tests])):
        r['q_bh_contexts'] = q
    np.savez_compressed(raw / 'terminal_logpmfs.npz', **local)
    return {'eligible_clean_principal_objects': len(clean), 'primary_length_ge_two_objects': len(rr),
            'singletons': {'objects': sum(len(r['signs_reading_rtl']) == 1 for r in clean),
                           'sign740_objects': sum(r['signs_reading_rtl'] == ['740'] for r in clean)},
            'expectation': 'One uniform anchor per physical object, conditional on its exact inventory and length.',
            'context_tests': len(tests), 'groups': output}


def period_interval(label):
    if label == 'Period 3B/C':
        return (1.5, 7.)
    if re.fullmatch(r'Period 3A(?:-\d+)?', label):
        return (0., 1.5)
    if re.fullmatch(r'Period 3B(?:-\d+)?', label):
        return (1.5, 4.)
    if re.fullmatch(r'Period 3C(?:-\d+)?', label):
        return (4., 7.)
    if label == 'Period 3':
        return (0., 7.)
    return None


def integrated_fit(intervals, y):
    pairs = sorted(set(map(tuple, intervals)))
    n = np.array([sum(tuple(t) == pair for t in intervals) for pair in pairs])
    k = np.array([sum(v for t, v in zip(intervals, y) if tuple(t) == pair) for pair in pairs])
    nodes, weights = np.polynomial.legendre.leggauss(32)
    t = np.array([(lo + hi) / 2 + nodes * (hi - lo) / 2 for lo, hi in pairs])
    weights = weights / 2

    def loss_gradient(parameters):
        a, b = parameters
        px = expit(a + b * t)
        p = np.clip(px @ weights, 1e-12, 1 - 1e-12)
        loss = -np.sum(k * np.log(p) + (n - k) * np.log1p(-p))
        factor = (n * p - k) / (p * (1 - p))
        grad = np.array([np.sum(factor * ((px * (1 - px)) @ weights)),
                         np.sum(factor * ((px * (1 - px) * t) @ weights))])
        return float(loss), grad

    fit = minimize(loss_gradient, [float(logit(np.mean(y))), 0.], jac=True,
                   method='L-BFGS-B', bounds=[(-30, 30), (-30, 30)],
                   options={'ftol': 1e-13, 'gtol': 1e-9, 'maxiter': 1000})
    a, b = fit.x
    delta = float(expit(a + 7 * b) - expit(a))
    cutoff = float(chi2.ppf(.95, 1))

    def profile(d):
        lo, hi = max(1e-9, -d + 1e-9), min(1 - 1e-9, 1 - d - 1e-9)
        def value(p0):
            start, end = logit(p0), logit(p0 + d)
            return loss_gradient([start, (end - start) / 7])[0]
        result = minimize_scalar(value, bounds=(lo, hi), method='bounded', options={'xatol': 1e-11})
        return float(2 * (result.fun - fit.fun))

    edge_lo, edge_hi = -.999999, .999999
    lower = brentq(lambda d: profile(d) - cutoff, edge_lo, delta) if profile(edge_lo) > cutoff else edge_lo
    upper = brentq(lambda d: profile(d) - cutoff, delta, edge_hi) if profile(edge_hi) > cutoff else edge_hi
    return {'model': 'Uniform latent time within each recorded interval; integrated logistic Bernoulli likelihood.',
            'optimizer_success': bool(fit.success), 'optimizer_message': str(fit.message),
            'parameter_boundary': bool(np.any(np.abs(fit.x) > 29.99)),
            'intercept': float(a), 'log_odds_per_century': float(b),
            'fitted_share_2600_BCE': float(expit(a)), 'fitted_share_1900_BCE': float(expit(a + 7 * b)),
            'fitted_share_change_1900_minus_2600': delta, 'profile_95_change_interval': [lower, upper],
            'profile_LR_at_interval_edges': [profile(lower), profile(upper)],
            'profile_LR_at_fitted_change': profile(delta), 'log_likelihood': -float(fit.fun),
            'coverage_years': 700, 'interval_counts': [{'centuries_after_2600_bounds': list(pair),
                                                      'objects': int(nn), 'unicorn': int(kk)}
                                                     for pair, nn, kk in zip(pairs, n, k)]}


def clopper(k, n, alpha=.025):
    return [float(beta.ppf(alpha / 2, k, n - k + 1)) if k else 0.,
            float(beta.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.]


def assignment_envelope(rs):
    def get(label):
        rr = [r for r in rs if label(r['metadata'].get('time', '-'))]
        return len(rr), sum(prior.motif(r['symbol']) == 'unicorn' for r in rr)
    nB, uB = get(lambda s: bool(re.fullmatch(r'Period 3B(?:-\d+)?', s)))
    nC, uC = get(lambda s: bool(re.fullmatch(r'Period 3C(?:-\d+)?', s)))
    nA, uA = get(lambda s: s == 'Period 3B/C')
    rows = []
    for ub in range(uA + 1):
        for mb in range(nA - uA + 1):
            nb, kb = nB + ub + mb, uB + ub
            nc, kc = nC + nA - ub - mb, uC + uA - ub
            ciB, ciC = clopper(kb, nb), clopper(kc, nc)
            rows.append([kc / nc - kb / nb, ciC[0] - ciB[1], ciC[1] - ciB[0]])
    rows = np.array(rows)
    return {'known_3B': {'objects': nB, 'unicorn': uB}, 'known_3C': {'objects': nC, 'unicorn': uC},
            'ambiguous_3B_C': {'objects': nA, 'unicorn': uA}, 'assignments': len(rows),
            'observed_change_C_minus_B_identified_range': [float(rows[:, 0].min()), float(rows[:, 0].max())],
            'at_least_95_confidence_envelope': [float(rows[:, 1].min()), float(rows[:, 2].max())],
            'excluded_unspecific_period3_objects': sum(r['metadata'].get('time') == 'Period 3' for r in rs),
            'method': 'Enumerate all ambiguous unicorn/minority allocations; envelope of two 97.5% Clopper-Pearson intervals.'}


def period_analysis(seals, B, Bboot, rng, raw):
    sq = [r for r in seals if r['site'] == 'Harappa' and r['object_type'] == 'SEAL:S']
    known = [r for r in sq if prior.motif(r['symbol']) is not None]
    rr = [r for r in known if period_interval(r['metadata'].get('time', '-')) is not None]
    y = np.array([prior.motif(r['symbol']) == 'unicorn' for r in rr], int)
    intervals = np.array([period_interval(r['metadata'].get('time', '-')) for r in rr])
    labels = np.array([r['metadata'].get('time', '-') for r in rr])
    tested_labels = sorted(s for s, n in Counter(labels).items() if n >= 10)
    mean_y, times = y.mean(), intervals.mean(1)

    def stats(yy):
        stat = sum((yy[labels == s].sum() - (labels == s).sum() * mean_y) ** 2 /
                   ((labels == s).sum() * mean_y * (1 - mean_y)) for s in tested_labels)
        score = float(np.dot(yy - mean_y, times - times.mean()))
        return [stat, score]

    observed = stats(y)
    strata = prior.blocks([r['object_type'] for r in rr])
    null = np.array([stats(prior.shuffle(y, strata, rng)) for _ in range(B)])
    np.save(raw / 'period_null.npy', null)
    tests = [dict(outcome='raw_period_unicorn_heterogeneity', **prior.tail(observed[0], null[:, 0])),
             dict(outcome='interval_time_unicorn_score', **prior.tail(observed[1], null[:, 1], absolute=True))]
    for test, q in zip(tests, prior.bh([t['p'] for t in tests])):
        test['q_bh'] = q
    summaries = []
    for label in sorted({r['metadata'].get('time', '-') for r in sq}):
        population = [r for r in sq if r['metadata'].get('time', '-') == label]
        selected = [r for r in population if prior.motif(r['symbol']) is not None]
        cats = Counter('unicorn' if prior.motif(r['symbol']) == 'unicorn' else
                       'Gaur' if r['symbol'] == 'Gaur' else 'other' for r in selected)
        n = len(selected)
        summary = {'period': label, 'all_square_objects': len(population), 'known_motif_objects': n,
                   'unknown_motif_objects': len(population) - n, 'counts': dict(cats),
                   'time_interval_BCE': [2600 - 100 * v for v in period_interval(label)] if period_interval(label) else None}
        if n:
            weights = rng.multinomial(n, np.array([cats[c] for c in ['unicorn', 'Gaur', 'other']]) / n, size=Bboot) / n
            summary['shares'] = {c: cats[c] / n for c in ['unicorn', 'Gaur', 'other']}
            summary['component_bootstrap_95_ci'] = {c: np.quantile(weights[:, j], [.025, .975]).tolist()
                                                    for j, c in enumerate(['unicorn', 'Gaur', 'other'])}
            summary['unicorn_wilson_95_ci'] = prior.wilson(cats['unicorn'], n)
        summaries.append(summary)
    coarse = []
    for phase in ['3A', '3B', '3C']:
        selected = [r for r in rr if re.fullmatch(r'Period ' + phase + r'(?:-\d+)?', r['metadata']['time'])]
        cats = Counter(prior.motif(r['symbol']) for r in selected)
        coarse.append({'phase': phase, 'known_motif_objects': len(selected), 'motif_counts': dict(cats),
                       'unicorn_share': cats['unicorn'] / len(selected),
                       'unicorn_wilson_95_ci': prior.wilson(cats['unicorn'], len(selected))})
    return {'population': 'Known square-seal motifs, Harappa Period 3 and subphases',
            'objects_in_tests_and_model': len(rr), 'tested_raw_labels': tested_labels,
            'tests': tests, 'raw_periods': summaries, 'unambiguous_parent_phases': coarse,
            'interval_integrated_model': integrated_fit(intervals, y),
            'ambiguous_assignment_sensitivity': assignment_envelope(rr)}


def external_analysis(groups, seals, B, rng, raw):
    external_objects = []
    for family in groups:
        if not any(r['region'] in EXTERNAL for r in family):
            continue
        r = min(family, key=lambda a: (-len(a['signs_reading_rtl']), a['record_id']))
        external_objects.append({'principal_record_id': r['record_id'], 'object_family_id': r['object_family_id'],
                                 'record_ids': '|'.join(sorted(a['record_id'] for a in family)),
                                 'source_cisi': '|'.join(sorted({a['source_cisi'] or '' for a in family})),
                                 'site': r['site'], 'region': r['region'], 'object_type': r['object_type'],
                                 'symbol': r['symbol'], 'faces': len(family)})
    prior.write(raw / 'external-objects.json', external_objects)
    with (raw / 'external-objects.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(external_objects[0]) if external_objects else ['principal_record_id'])
        writer.writeheader()
        writer.writerows(external_objects)
    summaries = []
    for region_set, name in [(CORE, 'core'), (EXTERNAL, 'external'),
                             ({'Persian Gulf', 'Mesopotamia'}, 'Gulf_Mesopotamia'),
                             ({'Other', 'South India'}, 'excluded_other_South_India')]:
        ss = [r for r in seals if r['region'] in region_set]
        for typ in ['all'] + sorted({r['object_type'] for r in ss}):
            selected = ss if typ == 'all' else [r for r in ss if r['object_type'] == typ]
            counts = Counter(prior.motif(r['symbol']) for r in selected if prior.motif(r['symbol']) is not None)
            n = sum(counts.values())
            summaries.append({'geography': name, 'object_type': typ, 'seal_objects': len(selected),
                              'known_motif_objects': n, 'unknown_motif_objects': len(selected) - n,
                              'motif_counts': dict(counts), 'unicorn_share': counts['unicorn'] / n if n else None,
                              'Gaur_share': counts['Gaur'] / n if n else None,
                              'unicorn_wilson_95_ci': prior.wilson(counts['unicorn'], n),
                              'Gaur_wilson_95_ci': prior.wilson(counts['Gaur'], n),
                              'broad_bovine_code_share': sum(counts[c] for c in ['Gaur', 'Bull', 'Bult', 'Zebu', 'Buff']) / n if n else None})
    comparisons = {}
    for name, ext in [('all_external', EXTERNAL), ('Gulf_Mesopotamia', {'Persian Gulf', 'Mesopotamia'})]:
        selected = [r for r in seals if r['region'] in CORE | ext and prior.motif(r['symbol']) is not None]
        labels = np.array([int(r['region'] in ext) for r in selected])
        uni = np.array([prior.motif(r['symbol']) == 'unicorn' for r in selected], int)
        gaur = np.array([r['symbol'] == 'Gaur' for r in selected], int)
        strata = prior.blocks([r['object_type'] for r in selected])
        def stats(lab):
            return [uni[lab == 0].mean() - uni[lab == 1].mean(), gaur[lab == 1].mean() - gaur[lab == 0].mean()]
        observed = stats(labels)
        null = np.array([stats(prior.shuffle(labels, strata, rng)) for _ in range(B)])
        np.save(raw / (name + '_motif_null.npy'), null)
        tests = [dict(outcome=outcome, **centred_tail(obs, null[:, j])) for j, (outcome, obs) in enumerate(zip(
            ['unicorn_core_minus_external_share', 'Gaur_external_minus_core_share'], observed))]
        for test, q in zip(tests, prior.bh([t['p'] for t in tests])):
            test['q_bh'] = q
        comparisons[name] = {'core_known_objects': int((labels == 0).sum()),
                             'external_known_objects': int((labels == 1).sum()),
                             'type_blocks': len(strata),
                             'movable_objects': sum(len(ix) for ix in strata if len(set(labels[ix])) > 1), 'tests': tests}
    site_counts = Counter((r['site'], r['region'], r['object_type']) for r in external_objects)
    return {'core_regions': sorted(CORE), 'external_regions': sorted(EXTERNAL),
            'external_physical_objects_all_types': len(external_objects),
            'external_object_list_local': {'json': (raw / 'external-objects.json').relative_to(ROOT).as_posix(),
                                           'csv': (raw / 'external-objects.csv').relative_to(ROOT).as_posix()},
            'external_site_type_counts': [{'site': s, 'region': reg, 'object_type': typ, 'objects': n}
                                          for (s, reg, typ), n in sorted(site_counts.items())],
            'geography_motif_summaries': summaries, 'comparisons': comparisons,
            'Gaur_mapping_scope': 'Available-code proxy for Bos gaurus; Bull/Buff/Zebu and composite scenes remain separate.'}


def run():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', default='post-launch-2026-10-07-01')
    ap.add_argument('--permutations', type=int, default=9999)
    ap.add_argument('--bootstraps', type=int, default=2000)
    args = ap.parse_args()
    out, raw = OWN / args.run, RAW / args.run
    if out.exists() or raw.exists():
        raise FileExistsError('Choose a fresh output and local raw directory.')
    out.mkdir(); raw.mkdir()
    start = time.time()
    rng = np.random.default_rng(2026100703)
    rows = [json.loads(l) for l in prior.INPUT.read_text(encoding='utf-8').splitlines()]
    groups, principal, seals, _ = prior.grouping(rows)
    tasks = [('richness.json', lambda: richness_analysis(rows, principal, args.permutations, rng, raw)),
             ('concentration.json', lambda: concentration(rows, principal)),
             ('terminal740.json', lambda: terminal_analysis(principal, args.bootstraps, rng, raw)),
             ('period-stability.json', lambda: period_analysis(seals, args.permutations, args.bootstraps, rng, raw)),
             ('external-motifs.json', lambda: external_analysis(groups, seals, args.permutations, rng, raw))]
    hashes = {}
    for file, task in tasks:
        save(out / file, task())
        hashes[file] = prior.sha(out / file)
        print(file, 'complete', round(time.time() - start, 2), 'seconds', flush=True)
    save(out / 'summary.json', {'input_sha256': prior.sha(prior.INPUT), 'amendment_sha256': prior.sha(AMENDMENT),
                              'code_sha256': prior.sha(__file__), 'reused_analysis_code_sha256': prior.sha(OWN / 'analyze.py'),
                              'coordinator_caption_check_sha256': prior.sha(ROOT / 'experiments/2026-10-06-research-program/frenez-talk-check.md'),
                              'seed': 2026100703, 'permutations': args.permutations, 'bootstraps': args.bootstraps,
                              'output_hashes': hashes, 'created_utc': datetime.now(timezone.utc).isoformat(),
                              'runtime_seconds': time.time() - start})


if __name__ == '__main__':
    run()
