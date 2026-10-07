"""Caption-led D1 follow-up. Existing endpoints are never changed.

Run from the repository root with -B. Full memberships and draws stay local.
"""
from __future__ import annotations
import argparse, collections, functools, hashlib, json, math, time
from pathlib import Path
import numpy as np
from scipy.stats import hypergeom
import analyze as base

ROOT, OWN, RAW = base.ROOT, base.OWN, base.RAW
ORIGIN = 'post-launch amendment'
TARGETS = {
    'man_090': ['090'], 'twins_091': ['091'],
    'primary_union': ['090', '091'], 'modified_man': ['090', '093', '097'],
    'expanded_twins': ['091', '097'], 'expanded_union': ['090', '091', '093', '097']
}
PRIMARY = ['man_090', 'twins_091']


def save(path, value):
    if isinstance(value, dict): value = {'origin': ORIGIN, 'status': 'Exploratory', **value}
    base.save(path, value)


def table(path, rows):
    base.csv(path, [{'origin': ORIGIN, 'status': 'Exploratory', **row} for row in rows])


def arr_ci(values): return [float(x) for x in np.quantile(values, [.025, .975], axis=0)]


def denom(c, ids): return c.denom(np.asarray(ids, int))


def identify_signs(out):
    paths = ['data/normalized/mayig_sign_schema.json', 'data/normalized/mayig_wells_class_crosswalk.json',
             'research/chart_reference/manual_numeric_reference.json', 'output/chart_atlas/reference.json']
    schema = json.loads((ROOT / paths[0]).read_text(encoding='utf-8'))['signs']
    cross = json.loads((ROOT / paths[1]).read_text(encoding='utf-8'))
    manual = json.loads((ROOT / paths[2]).read_text(encoding='utf-8'))['rows']
    atlas = json.loads((ROOT / paths[3]).read_text(encoding='utf-8'))
    entries = []
    for label, cls, wells, codes, interpretation in [
        ('man', 'P013', '090', [133, 535], 'simple human glyph'),
        ('twins', 'P016', '091', [110, 692], 'paired human glyphs'),
        ('modified_man', 'P014', '093', [394], 'single human glyph with an extra internal stroke'),
        ('bracketed_alternative', 'P015', '097', [518, 150], 'single human glyph between flanking strokes')]:
        assert 'W' + wells in schema[cls]['wells_graphemes']
        assert cls in cross['by_wells_id'][wells]
        locators = []
        for code in codes:
            row = next(x for x in atlas['rows'] if x['code'] == code)
            ref = next(x for x in manual if (x['pdf_page'], x['column'], x['row']) == (row['pdf_page'], row['column'], row['row']))
            assert ref['code'] == code
            locators.append({k: row[k] for k in ['pdf_page', 'column', 'row', 'rank', 'code', 'numeric_confidence', 'dashed_auxiliary', 'image']})
        entries.append({'label': label, 'wells_code': wells, 'mayig_class': cls,
                        'graphic_observation': interpretation, 'chart_codes': codes, 'locators': locators,
                        'schema_field': f'signs.{cls}.wells_graphemes',
                        'crosswalk_field': f'by_wells_id.{wells}',
                        'mapping_scope': 'graphic candidate; the lecture slide was not independently identified'})
    save(out / 'sign_identifications.json', {'targets': TARGETS, 'identifications': entries,
         'inputs': {p: base.digest(ROOT / p) for p in paths}, 'chart_source_url': atlas.get('source_url'),
         'ambiguity': 'Mayig P015 and P016 both list Mahadevan M002 despite different graphics; do not merge their Wells classes as established equivalents.'})


def group_sample(c, ids, rng, cell):
    """One multiplicity for each whole physical component, within signatures."""
    groups = collections.defaultdict(list)
    for i in ids: groups[int(c.pid[i])].append(int(i))
    signatures = collections.defaultdict(list)
    for group, members in groups.items():
        signatures[tuple(sorted({cell(i) for i in members}))].append(group)
    multiples = collections.Counter()
    for pool in signatures.values():
        multiples.update(int(x) for x in rng.choice(pool, len(pool), replace=True))
    return np.asarray([multiples[int(c.pid[i])] for i in ids], float)


def frequency_values(c, a, b, counts, a_base=None, b_base=None, cell_key=None):
    a, b = np.asarray(a, int), np.asarray(b, int)
    aa = np.ones(len(a)) if a_base is None else np.asarray(a_base, float)
    bb = np.ones(len(b)) if b_base is None else np.asarray(b_base, float)
    cell_key = cell_key or (lambda i: (str(c.type[i]), int(c.length[i])))
    fractions = counts / np.maximum(c.known[:, None], 1)
    presence = (counts > 0).astype(float)
    core_cells = collections.defaultdict(list)
    for j, i in enumerate(b): core_cells[cell_key(i)].append(j)
    matched_f, matched_p = [], []
    for i in a:
        positions = core_cells[cell_key(i)]
        w = bb[positions]
        if not w.sum(): raise ValueError('Comparator cell lost support.')
        matched_f.append(np.average(fractions[b[positions]], weights=w, axis=0))
        matched_p.append(np.average(presence[b[positions]], weights=w, axis=0))
    matched_f, matched_p = np.asarray(matched_f), np.asarray(matched_p)
    types = sorted(set(c.type[a]))
    type_weights = c.weights(a, types, base=aa)
    if type_weights is None: raise ValueError('External type lost support.')
    raw_weights = aa * c.known[a]
    results = {}
    for j, target in enumerate(TARGETS):
        external = float(np.average(fractions[a, j], weights=raw_weights))
        core = float(np.average(matched_f[:, j], weights=raw_weights))
        te = float(np.sum(type_weights * fractions[a, j]))
        tc = float(np.sum(type_weights * matched_f[:, j]))
        pe = float(np.sum(type_weights * presence[a, j]))
        pc = float(np.sum(type_weights * matched_p[:, j]))
        results[target] = {'raw_external_fraction': external, 'matched_core_raw_fraction': core,
            'raw_excess': external - core,
            'face_weighted_excess': float(np.average(fractions[a, j] - matched_f[:, j], weights=aa)),
            'type_external_fraction': te, 'type_matched_core_fraction': tc,
            'type_excess': te - tc, 'type_external_presence': pe, 'type_matched_core_presence': pc,
            'type_presence_excess': pe - pc}
    return results


def grouped_reference(c, a, b, counts, rng, budget, kind):
    pool = sorted(set(map(int, a)) | set(map(int, b)))
    labels = {int(i): True for i in a}
    group_ids = c.pid if kind == 'physical' else c.tid
    groups = collections.defaultdict(list)
    for i in pool: groups[int(group_ids[i])].append(i)
    retained, blocks = [], collections.defaultdict(list)
    for gid, ids in sorted(groups.items()):
        cells = {(str(c.type[i]), int(c.length[i])) for i in ids}
        states = {labels.get(i, False) for i in ids}
        if len(cells) != 1 or len(states) != 1: continue
        key = (*next(iter(cells)), len(ids))
        j = len(retained)
        retained.append((ids, next(iter(states))))
        blocks[key].append(j)
    aa = [i for ids, state in retained if state for i in ids]
    bb = [i for ids, state in retained if not state for i in ids]
    core_cells = {(str(c.type[i]), int(c.length[i])) for i in bb}
    if not aa or any((str(c.type[i]), int(c.length[i])) not in core_cells for i in aa):
        return {'unit': kind, 'status': 'Failed', 'reason': 'No complete matched reference population.'}, None
    movable = sum(len(js) for js in blocks.values() if 0 < sum(retained[j][1] for j in js) < len(js))
    observed = frequency_values(c, aa, bb, counts)
    report = {'unit': kind, 'a': denom(c, aa), 'b': denom(c, bb), 'movable_units': movable,
              'effects': observed, 'reference_assumption': 'Exchangeable whole components within exact type, length and selected-face-count blocks.'}
    if not movable:
        report.update(status='Failed', reason='Unmovable grouped reference.')
        return report, None
    draws = np.empty((budget, len(TARGETS)))
    expected_margins = collections.Counter((str(c.type[i]), int(c.length[i])) for i in aa)
    for draw in range(budget):
        states = np.zeros(len(retained), bool)
        for js in blocks.values():
            chosen = rng.permutation(js)[:sum(retained[j][1] for j in js)]
            states[chosen] = True
        pa = [i for j, (ids, _) in enumerate(retained) if states[j] for i in ids]
        pb = [i for j, (ids, _) in enumerate(retained) if not states[j] for i in ids]
        assert collections.Counter((str(c.type[i]), int(c.length[i])) for i in pa) == expected_margins
        values = frequency_values(c, pa, pb, counts)
        draws[draw] = [values[t]['type_excess'] for t in TARGETS]
    p = [(1 + int(np.sum(draws[:, j] >= observed[t]['type_excess'] - 1e-12))) / (budget + 1) for j, t in enumerate(TARGETS)]
    corrected = base.holm(p[:2]) + base.holm(p[2:])
    report['tests'] = {t: {'one_sided_p': p[j], 'holm_p': corrected[j], 'correction_family': 'two primary targets' if j < 2 else 'four mapping sensitivities'} for j, t in enumerate(TARGETS)}
    report['allocations_margin_checked'] = budget
    return report, draws


def external_frequency(c, out, local, rng, budget):
    counts = np.column_stack([c.matrix[:, [c.vi[x] for x in signs if x in c.vi]].sum(1) for signs in TARGETS.values()])
    a_all = c.all[np.isin(c.region, base.EXTERNAL)]
    b_all = c.all[np.isin(c.region, base.CORE)]
    eligible = a_all[c.clear[a_all]]
    touched = set(c.tid[eligible])
    core = b_all[c.clear[b_all] & ~np.isin(c.tid[b_all], list(touched))]
    key = lambda i: (str(c.type[i]), int(c.length[i]))
    cells = collections.defaultdict(list)
    for i in core: cells[key(i)].append(int(i))
    matched, exclusions, coverage = [], [], []
    for i in eligible:
        candidates = cells.get(key(i), [])
        n = len(set(c.pid[candidates])) if candidates else 0
        coverage.append({'region': c.region[i], 'type': c.type[i], 'length': int(c.length[i]),
                         'core_faces': len(candidates), 'core_families': n, 'retained': n >= 2})
        if n >= 2: matched.append(int(i))
        else: exclusions.append({'record_id': c.rows[i]['record_id'], 'i': int(i), 'reason': 'Fewer than two exact-cell core physical families.', **coverage[-1]})
    a = np.asarray(matched, int)
    b = np.asarray(sorted({j for i in a for j in cells[key(i)]}), int)
    results = frequency_values(c, a, b, counts)
    interval_fields = ['raw_excess', 'face_weighted_excess', 'type_excess', 'type_presence_excess']
    boots = np.empty((budget, len(TARGETS), len(interval_fields)))
    for draw in range(budget):
        av = group_sample(c, a, rng, lambda i: str(c.type[i]))
        bv = group_sample(c, b, rng, key)
        values = frequency_values(c, a, b, counts, av, bv)
        boots[draw] = [[values[t][f] for f in interval_fields] for t in TARGETS]
    for j, target in enumerate(TARGETS):
        results[target]['intervals95'] = {f: [float(x) for x in np.quantile(boots[:, j, k], [.025, .975])] for k, f in enumerate(interval_fields)}
        results[target]['valid_bootstraps'] = budget
    refs = []
    for unit in ['physical', 'text']:
        ref, draws = grouped_reference(c, a, b, counts, rng, budget, unit)
        refs.append(ref)
        if draws is not None: save(local / f'external_{unit}_permutation_draws.json', {'targets': list(TARGETS), 'draws': draws.tolist()})
    membership = {'external_indices': a.tolist(), 'core_indices': b.tolist(),
                  'core_cell_members': [{'type': t, 'length': le, 'indices': cells[(t, le)]} for t, le in sorted({key(i) for i in a})],
                  'external_exclusions': exclusions}
    save(local / 'external_membership.json', membership)
    save(local / 'external_bootstrap_draws.json', {'targets': list(TARGETS), 'fields': interval_fields, 'draws': boots.tolist()})
    raw_rows = []
    for population, ids in [('external_all', a_all), ('core_all', b_all), ('external_clear', eligible), ('external_matched', a)]:
        for j, target in enumerate(TARGETS):
            raw_rows.append({'population': population, 'target': target, **denom(c, ids),
                'target_tokens': int(counts[ids, j].sum()), 'target_bearing_faces': int(np.sum(counts[ids, j] > 0)),
                'target_bearing_families': len(set(c.pid[ids[counts[ids, j] > 0]])),
                'known_token_fraction': float(counts[ids, j].sum() / c.known[ids].sum())})
    table(out / 'external_target_counts.csv', raw_rows)
    grouped_coverage = collections.Counter((r['region'], r['type'], r['length'], r['core_faces'], r['core_families'], r['retained']) for r in coverage)
    table(out / 'external_match_coverage.csv', [{'region': r, 'type': t, 'length': le, 'core_faces': cf, 'core_families': cp, 'retained': keep, 'external_faces': n} for (r, t, le, cf, cp, keep), n in sorted(grouped_coverage.items())])
    old = json.loads((RAW / 'main-2026-10-07-v1/external_predictions.json').read_text(encoding='utf-8'))
    by_id = {row['record_id']: i for i, row in enumerate(c.rows)}
    old_a = [x['i'] for x in old]
    old_b = sorted({by_id[rid] for x in old for rid in x['match_ids']})
    cell_lookup = {x['i']: (*key(x['i']), x['fold']) for x in old}
    old_key = lambda i: cell_lookup[i] if i in cell_lookup else (*key(i), int(c.fold[i]))
    old_results = frequency_values(c, old_a, old_b, counts, cell_key=old_key)
    old_boots = []
    for _ in range(budget):
        values = frequency_values(c, old_a, old_b, counts,
            group_sample(c, old_a, rng, lambda i: str(c.type[i])), group_sample(c, old_b, rng, old_key), old_key)
        old_boots.append([values[t]['type_excess'] for t in TARGETS])
    old_boots = np.asarray(old_boots)
    for j, target in enumerate(TARGETS): old_results[target]['type_excess_interval95'] = [float(x) for x in np.quantile(old_boots[:, j], [.025, .975])]
    save(out / 'external_frequency.json', {'external_all': denom(c, a_all), 'external_clear': denom(c, eligible),
        'matched_external': denom(c, a), 'matched_core': denom(c, b), 'eligible_core_after_closure_exclusion': denom(c, core),
        'removed_core_faces_by_closure': int(np.sum(c.clear[b_all])) - len(core), 'matching_minimum_core_families': 2,
        'results': results, 'grouped_references': refs,
        'original_seven_object_sensitivity': {'a': denom(c, old_a), 'b': denom(c, old_b), 'results': old_results},
        'bootstrap_scope': 'Whole physical families within sampled external types and comparator cell signatures; conditional on observed match support.'})


def harappa_units(c):
    units = []
    for pid, full_ids in enumerate(c.physical):
        ids = [i for i in full_ids if c.site[i] == 'Harappa']
        if not ids: continue
        types = sorted(set(c.type[ids])); admissible = sorted({p for i in ids for p in c.rows[i]['admissible']}, key=base.PERIODS.index)
        codes = set(s for i in ids for s in c.rows[i]['seq'] if s != '000')
        units.append({'physical': pid, 'text': int(c.tid[ids[0]]), 'indices': ids,
                      'type': types[0] if len(types) == 1 else None, 'types': types,
                      'admissible': admissible, 'period': admissible[0] if len(admissible) == 1 else 'interval' if admissible else 'undated',
                      'codes': sorted(codes), 'faces': len(ids), 'slots': int(c.length[ids].sum()),
                      'known_tokens': int(c.known[ids].sum()), 'unreadable_tokens': int((c.length[ids] - c.known[ids]).sum())})
    return units


@functools.lru_cache(maxsize=100000)
def diversity(count_tuple, m):
    counts = np.asarray([x for x in count_tuple if x], int)
    n = int(counts.sum())
    if not n or not m: return (0., 0.)
    if m > n: raise ValueError('Rarefaction exceeds sample.')
    if m == n:
        p = counts / n
        return (float(len(counts)), float(-np.sum(p * np.log2(p))))
    richness = float(np.sum(hypergeom.sf(0, n, counts, m)))
    k = np.arange(1, min(m, int(counts.max())) + 1, dtype=float)
    probs = hypergeom.pmf(k[:, None], n, counts[None, :], m)
    shannon = float(math.log2(m) - np.sum(probs * (k * np.log2(k))[:, None]) / m)
    return richness, max(0., shannon)


def count_tuple(units, transform=lambda x: x['type']):
    return tuple(sorted(collections.Counter(transform(x) for x in units).values()))


def media_effect(a, b, transform=lambda x: x['type'], m=None):
    m = min(len(a), len(b)) if m is None else m
    ar, ah = diversity(count_tuple(a, transform), len(a)); br, bh = diversity(count_tuple(b, transform), len(b))
    arr, arh = diversity(count_tuple(a, transform), m); brr, brh = diversity(count_tuple(b, transform), m)
    return np.array([br - ar, bh - ah, brr - arr, brh - arh], float)


def media_analysis(c, units, out, local, rng, allocations):
    selected = [x for x in units if x['type'] is not None]
    counts, summaries, curves = [], [], []
    periods = base.PERIODS + ['interval', 'undated']
    for p in periods:
        group = [x for x in selected if x['period'] == p]
        for t in sorted({x['type'] for x in group}):
            cell = [x for x in group if x['type'] == t]
            counts.append({'period': p, 'type': t, 'physical_families': len(cell), 'faces': sum(x['faces'] for x in cell),
                           'known_tokens': sum(x['known_tokens'] for x in cell), 'unreadable_tokens': sum(x['unreadable_tokens'] for x in cell)})
        r, h = diversity(count_tuple(group), len(group))
        face_count = collections.Counter()
        for x in group: face_count[x['type']] += x['faces']
        fr, fh = diversity(tuple(sorted(face_count.values())), sum(face_count.values()))
        row = {'period': p, 'physical_families': len(group), 'faces': sum(x['faces'] for x in group),
               'known_tokens': sum(x['known_tokens'] for x in group), 'unreadable_tokens': sum(x['unreadable_tokens'] for x in group),
               'type_richness': int(r), 'shannon_bits': h, 'effective_types': 2 ** h,
               'face_weighted_shannon_bits': fh, 'readable_families': sum(x['known_tokens'] > 0 for x in group)}
        if group:
            hdraws = [diversity(count_tuple([group[int(i)] for i in rng.integers(0, len(group), len(group))]), len(group))[1] for _ in range(999)]
            row.update(shannon_ci95_low=float(np.quantile(hdraws, .025)), shannon_ci95_high=float(np.quantile(hdraws, .975)))
        summaries.append(row)
        for m in [1, 2, 5, 10, 20, 50, 100]:
            if m <= len(group):
                rr, rh = diversity(count_tuple(group), m)
                curves.append({'period': p, 'family_budget': m, 'expected_type_richness': rr, 'expected_shannon_bits': rh})
    table(out / 'media_period_type_counts.csv', counts)
    table(out / 'media_period_summary.csv', summaries)
    table(out / 'media_rarefaction.csv', curves)
    a = [x for x in selected if x['period'] == '3B']; b = [x for x in selected if x['period'] == '3C']
    m = min(len(a), len(b)); observed = media_effect(a, b, m=m)
    boot = np.asarray([media_effect([a[int(i)] for i in rng.integers(0, len(a), len(a))],
                                  [b[int(i)] for i in rng.integers(0, len(b), len(b))], m=m) for _ in range(999)])
    pool = a + b; blocks = collections.defaultdict(list)
    for i, unit in enumerate(pool): blocks[unit['faces']].append(i)
    draws = []
    for _ in range(1999):
        pa, pb = [], []
        for positions in blocks.values():
            n = sum(i < len(a) for i in positions)
            perm = rng.permutation(positions)
            pa.extend(pool[int(i)] for i in perm[:n]); pb.extend(pool[int(i)] for i in perm[n:])
        assert len(pa) == len(a) and sum(x['faces'] for x in pa) == sum(x['faces'] for x in a)
        draws.append(media_effect(pa, pb, m=m))
    draws = np.asarray(draws)
    fields = ['raw_richness_difference', 'raw_shannon_difference_bits', 'rarefied_richness_difference', 'rarefied_shannon_difference_bits']
    effects = {f: {'effect': float(observed[j]), 'interval95': [float(v) for v in np.quantile(boot[:, j], [.025, .975])], 'valid_bootstraps': 999} for j, f in enumerate(fields)}
    ps = [(1 + int(np.sum(draws[:, j] >= observed[j] - 1e-12))) / 2000 for j in [2, 3]]
    for k, j in enumerate([2, 3]): effects[fields[j]].update(one_sided_p=ps[k], holm_p=base.holm(ps)[k])
    sensitivities = {}
    for name, aa, bb, transform in [
        ('broad_media_classes', a, b, lambda x: x['type'].split(':')[0]),
        ('excluding_uncertain_types', [x for x in a if x['type'] not in ['MISC', 'SEAL']], [x for x in b if x['type'] not in ['MISC', 'SEAL']], lambda x: x['type']),
        ('readable_families_only', [x for x in a if x['known_tokens'] > 0], [x for x in b if x['known_tokens'] > 0], lambda x: x['type'])]:
        sensitivities[name] = {'a_families': len(aa), 'b_families': len(bb), 'budget': min(len(aa), len(bb)),
            'effects': dict(zip(fields, map(float, media_effect(aa, bb, transform))))}
    interval = []
    for scenario, labels in allocations:
        aa = [x for x in selected if labels[x['physical']] == '3B']; bb = [x for x in selected if labels[x['physical']] == '3C']
        if aa and bb:
            interval.append({'scenario': scenario, 'a_families': len(aa), 'b_families': len(bb),
                             'budget': min(len(aa), len(bb)), **dict(zip(fields, map(float, media_effect(aa, bb))))})
    save(local / 'media_draws.json', {'fields': fields, 'bootstrap': boot.tolist(), 'permutation': draws.tolist(), 'interval_allocations': interval})
    table(out / 'media_interval_allocations.csv', interval)
    save(out / 'media_comparison.json', {'comparison': '3C_minus_3B', 'family_counts': {'3B': len(a), '3C': len(b)},
        'family_budget': m, 'effects': effects, 'sensitivities': sensitivities, 'mixed_type_families_excluded': sum(x['type'] is None for x in units),
        'period_resolution': '3C covers 2200–1900 BCE, including 2100; the bin cannot date a breakpoint at 2100.',
        'allocations_margin_checked': 1999, 'bootstrap_scope': 'Observed physical-family sampling by period; interval dates and excavation selection remain conditional.'})


@functools.lru_cache(maxsize=50000)
def zero_probs(n, m):
    return hypergeom.pmf(0, n, np.arange(n + 1), m)


def inventory_expectation(matrix, ids, m):
    if not ids or not m: return 0.
    incidences = matrix[np.asarray(ids, int)].sum(0).astype(int)
    return float(np.sum(1 - zero_probs(len(ids), m)[incidences]))


def strat_inventory(matrix, groups, budgets):
    absent = np.ones(matrix.shape[1])
    for key, ids in groups.items():
        incidences = matrix[np.asarray(ids, int)].sum(0).astype(int)
        absent *= zero_probs(len(ids), budgets[key])[incidences]
    return float(np.sum(1 - absent))


def early_adjusted(units, matrix, early, later, key_fn, rng, local, name):
    ga, gb = collections.defaultdict(list), collections.defaultdict(list)
    for i in early: ga[key_fn(units[i])].append(i)
    for i in later: gb[key_fn(units[i])].append(i)
    cells = sorted(k for k in ga.keys() & gb.keys() if len(ga[k]) >= 2 and len(gb[k]) >= 2)
    ga = {k: ga[k] for k in cells}; gb = {k: gb[k] for k in cells}
    if not cells: return {'status': 'Failed', 'reason': 'No common cell with at least two physical families on each side.'}
    budgets = {k: min(len(ga[k]), len(gb[k])) for k in cells}
    ar, br = strat_inventory(matrix, ga, budgets), strat_inventory(matrix, gb, budgets)
    boot = []
    for _ in range(999):
        ba = {k: [int(x) for x in rng.choice(v, len(v), replace=True)] for k, v in ga.items()}
        bb = {k: [int(x) for x in rng.choice(v, len(v), replace=True)] for k, v in gb.items()}
        boot.append(strat_inventory(matrix, ba, budgets) - strat_inventory(matrix, bb, budgets))
    pool = [i for k in cells for i in ga[k] + gb[k]]
    blocks = collections.defaultdict(list)
    states = set(early)
    for i in pool: blocks[(key_fn(units[i]), units[i]['faces'])].append(i)
    draws = []
    for _ in range(1999):
        pa, pb = {k: [] for k in cells}, {k: [] for k in cells}
        for (k, faces), positions in blocks.items():
            n = sum(i in states for i in positions)
            perm = rng.permutation(positions)
            pa[k].extend(int(i) for i in perm[:n]); pb[k].extend(int(i) for i in perm[n:])
        assert all(len(pa[k]) == len(ga[k]) and len(pb[k]) == len(gb[k]) for k in cells)
        assert sum(units[i]['faces'] for k in cells for i in pa[k]) == sum(units[i]['faces'] for k in cells for i in ga[k])
        draws.append(strat_inventory(matrix, pa, budgets) - strat_inventory(matrix, pb, budgets))
    observed = ar - br
    p = (1 + int(np.sum(np.asarray(draws) <= observed + 1e-12))) / 2000
    save(local / f'early_{name}_draws.json', {'bootstrap': boot, 'permutation': draws, 'early_cells': [{'cell': list(k), 'indices': ga[k]} for k in cells], 'later_cells': [{'cell': list(k), 'indices': gb[k]} for k in cells]})
    # Strict text closure changes the retained population if a component spans cells/periods.
    textgroups = collections.defaultdict(list)
    for i in pool: textgroups[units[i]['text']].append(i)
    tg, tblocks = [], collections.defaultdict(list)
    for ids in textgroups.values():
        cellset = {key_fn(units[i]) for i in ids}; labelset = {i in states for i in ids}
        if len(cellset) != 1 or len(labelset) != 1: continue
        k = next(iter(cellset)); idx = len(tg)
        tg.append((ids, next(iter(labelset)), k))
        tblocks[(k, len(ids), sum(units[i]['faces'] for i in ids))].append(idx)
    ta, tb = collections.defaultdict(list), collections.defaultdict(list)
    for ids, state, k in tg: (ta if state else tb)[k].extend(ids)
    tcells = sorted(k for k in ta.keys() & tb.keys() if len(ta[k]) >= 2 and len(tb[k]) >= 2)
    tbudget = {k: min(len(ta[k]), len(tb[k])) for k in tcells}
    movable = sum(len(js) for (k, _, _), js in tblocks.items() if k in tcells and 0 < sum(tg[j][1] for j in js) < len(js))
    text_ref = {'early_families': sum(len(ta[k]) for k in tcells), 'later_families': sum(len(tb[k]) for k in tcells), 'movable_components': movable}
    if not tcells or not movable:
        text_ref.update(status='Failed', reason='No movable supported homogeneous text-component reference.')
    else:
        ta = {k: ta[k] for k in tcells}; tb = {k: tb[k] for k in tcells}
        tobs = strat_inventory(matrix, ta, tbudget) - strat_inventory(matrix, tb, tbudget)
        tdraws = []
        for _ in range(1999):
            xa, xb = {k: [] for k in tcells}, {k: [] for k in tcells}
            for (k, _, _), js in tblocks.items():
                if k not in tcells: continue
                n = sum(tg[j][1] for j in js); perm = rng.permutation(js)
                for j in perm[:n]: xa[k].extend(tg[int(j)][0])
                for j in perm[n:]: xb[k].extend(tg[int(j)][0])
            assert all(len(xa[k]) == len(ta[k]) for k in tcells)
            tdraws.append(strat_inventory(matrix, xa, tbudget) - strat_inventory(matrix, xb, tbudget))
        text_ref.update(effect=float(tobs), one_sided_p=(1 + int(np.sum(np.asarray(tdraws) <= tobs + 1e-12))) / 2000, allocations_margin_checked=1999)
        save(local / f'early_{name}_text_draws.json', {'draws': tdraws})
    return {'expected_early_inventory': ar, 'expected_later_inventory': br, 'early_minus_later': observed,
            'interval95': [float(x) for x in np.quantile(boot, [.025, .975])], 'valid_bootstraps': 999,
            'one_sided_p': p, 'allocations_margin_checked': 1999,
            'selected_early_families': sum(map(len, ga.values())), 'selected_later_families': sum(map(len, gb.values())),
            'lost_early_families': len(early) - sum(map(len, ga.values())), 'lost_later_families': len(later) - sum(map(len, gb.values())),
            'total_sample_budget': sum(budgets.values()),
            'cells': [{'cell': list(k), 'early_families': len(ga[k]), 'later_families': len(gb[k]), 'sample_budget': budgets[k]} for k in cells],
            'text_component_sensitivity': text_ref}


def early_analysis(c, units, out, local, rng, allocations):
    matrix = np.zeros((len(units), c.v), bool)
    for i, unit in enumerate(units):
        for sign in unit['codes']: matrix[i, c.vi[sign]] = True
    eligible = [i for i, x in enumerate(units) if x['type'] is not None and x['known_tokens'] > 0]
    early = [i for i in eligible if units[i]['period'] in ['2', '3A']]
    later = [i for i in eligible if units[i]['period'] in ['3B', '3C']]
    observed = int(matrix[early].any(0).sum())
    draws, token_draws = [], []
    for _ in range(1999):
        ids = rng.choice(later, len(early), replace=False)
        draws.append(int(matrix[ids].any(0).sum()))
        token_draws.append(sum(units[int(i)]['known_tokens'] for i in ids))
    ea = [j for i in early for j in units[i]['indices']]; lb = [j for i in later for j in units[i]['indices']]
    early_codes = sorted({s for i in early for s in units[i]['codes']})
    table(out / 'early_sign_inventory.csv', [{'sign': s, 'early_families_bearing_sign': int(matrix[early, c.vi[s]].sum()),
        'later_families_bearing_sign': int(matrix[later, c.vi[s]].sum())} for s in early_codes])
    raw = {'early': denom(c, ea), 'later': denom(c, lb), 'early_physical_families': len(early), 'later_physical_families': len(later),
           'early_inventory': observed, 'same_family_budget': len(early), 'later_sample_mean_inventory': float(np.mean(draws)),
           'later_exact_expected_inventory': inventory_expectation(matrix, later, len(early)),
           'later_sample_interval95': [float(x) for x in np.quantile(draws, [.025, .975])],
           'early_minus_later_sample_mean': observed - float(np.mean(draws)),
           'reference_deviation_interval95': [observed - float(np.quantile(draws, .975)), observed - float(np.quantile(draws, .025))],
           'lower_tail_fraction_plus_one': (1 + sum(x <= observed for x in draws)) / 2000,
           'later_sample_known_token_mean': float(np.mean(token_draws)), 'later_sample_known_token_interval95': [float(x) for x in np.quantile(token_draws, [.025, .975])],
           'reference_scope': 'Fixed later physical-family population; sampling spread and tail fraction are not a population confidence interval or calibrated p-value.'}
    token_budget = min(int(c.known[ea].sum()), int(c.known[lb].sum()))
    token_ref = {}
    for label, ids in [('early', ea), ('later', lb)]:
        counts = c.matrix[ids].sum(0).astype(int)
        token_ref[label] = float(np.sum(hypergeom.sf(0, int(counts.sum()), counts, token_budget)))
    adjusted = {}
    for name, key_fn in [('type', lambda x: (x['type'],)), ('type_length', lambda x: (x['type'], x['slots']))]:
        adjusted[name] = early_adjusted(units, matrix, early, later, key_fn, rng, local, name)
    successful = [x for x in adjusted.values() if 'one_sided_p' in x]
    for x, p in zip(successful, base.holm([x['one_sided_p'] for x in successful])): x['holm_p'] = p
    text_successful = [x['text_component_sensitivity'] for x in successful if 'one_sided_p' in x['text_component_sensitivity']]
    for x, p in zip(text_successful, base.holm([x['one_sided_p'] for x in text_successful])): x['holm_p'] = p
    interval_rows = []
    for scenario, labels in allocations:
        aa = [i for i in eligible if labels[units[i]['physical']] in ['2', '3A']]
        bb = [i for i in eligible if labels[units[i]['physical']] in ['3B', '3C']]
        if aa and len(bb) >= len(aa):
            r = int(matrix[aa].any(0).sum()); expected = inventory_expectation(matrix, bb, len(aa))
            interval_rows.append({'scenario': scenario, 'early_families': len(aa), 'later_families': len(bb),
                'early_inventory': r, 'expected_later_same_family_budget': expected, 'early_minus_expected_later': r - expected})
    older = [i for i in eligible if units[i]['period'] in ['1', '2', '3A']]
    older_r = int(matrix[older].any(0).sum())
    table(out / 'early_interval_allocations.csv', interval_rows)
    save(local / 'early_raw_draws.json', {'inventory_draws': draws, 'known_token_draws': token_draws, 'early_unit_indices': early, 'later_unit_indices': later})
    save(out / 'early_inventory.json', {'window': '2800–2450 BCE; unambiguous 2 and 3A', 'raw_family_reference': raw,
         'token_rarefaction': {'known_token_budget': token_budget, 'expected_inventories': token_ref, 'scope': 'Uniform token sampling; descriptive effort control, not grouped inference.'},
         'adjusted': adjusted, 'period1_added': {'early_families': len(older), 'early_inventory': older_r,
             'expected_later_same_family_budget': inventory_expectation(matrix, later, len(older)),
             'early_minus_expected_later': older_r - inventory_expectation(matrix, later, len(older))},
         'exclusions': {'mixed_type_families': sum(x['type'] is None for x in units),
             'wholly_unreadable_families': sum(x['known_tokens'] == 0 for x in units),
             'interval_families': sum(x['period'] == 'interval' for x in units), 'undated_families': sum(x['period'] == 'undated' for x in units)},
         'inventory_scope': 'Readable codes in this dated export; the lecture slide set is not a verified input.'})


def allocate(units, rng):
    labels0 = {x['physical']: x['period'] for x in units}
    allocations = [('unambiguous', labels0)]
    for p in ['3B', '3C']:
        labels = dict(labels0)
        for x in units:
            if x['admissible'] == ['3B', '3C']: labels[x['physical']] = p
        allocations.append((f'all_3BC_to_{p}', labels))
    for p in ['3A', '3C']:
        labels = dict(labels0)
        for x in units:
            if x['admissible'] == ['3A', '3B', '3C']: labels[x['physical']] = p
        allocations.append((f'all_broad3_to_{p}', labels))
    for draw in range(200):
        labels = {x['physical']: str(rng.choice(x['admissible'])) if x['admissible'] else 'undated' for x in units}
        allocations.append((f'uniform_{draw:03}', labels))
    return allocations


def main():
    start = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='post-launch-2026-10-07-v1')
    args = parser.parse_args()
    if Path(args.run).name != args.run: raise ValueError('Use a fresh single directory name.')
    out, local = OWN / args.run, RAW / args.run
    if out.exists() or local.exists(): raise FileExistsError('Existing endpoints are preserved; choose a fresh run name.')
    out.mkdir(); local.mkdir()
    rng = np.random.default_rng(20261007)
    c = base.Corpus()
    audit = {'seed': 20261007, 'external_bootstrap_and_permutation': 1999, 'media_early_bootstrap': 999,
             'media_early_permutation': 1999, 'uniform_period_allocations': 200, 'population': c.denom(c.all),
             'input_sha256': base.digest(c.path), 'code_sha256': base.digest(Path(__file__)),
             'reused_analyzer_sha256': base.digest(OWN / 'analyze.py'),
             'amendment_sha256': base.digest(OWN / 'POST-LAUNCH-PROTOCOL-2026-10-07.md'),
             'coordinator_caption_check_sha256': base.digest(ROOT / 'experiments/2026-10-06-research-program/frenez-talk-check.md')}
    identify_signs(out)
    print('Sign references verified; calculating matched frequencies.', flush=True)
    external_frequency(c, out, local, rng, 1999)
    print('Matched frequencies complete; calculating family media diversity.', flush=True)
    units = harappa_units(c)
    save(local / 'harappa_units.json', {'units': units})
    allocations = allocate(units, rng)
    save(local / 'period_allocations.json', {'allocations': [{'scenario': scenario, 'labels': labels} for scenario, labels in allocations]})
    media_analysis(c, units, out, local, rng, allocations)
    print('Media diversity complete; calculating early inventory references.', flush=True)
    early_analysis(c, units, out, local, rng, allocations)
    audit['harappa_family_count'] = len(units)
    audit['elapsed_seconds'] = time.perf_counter() - start
    save(out / 'audit.json', audit)
    save(out / 'completion.json', {'elapsed_seconds': audit['elapsed_seconds'],
         'aggregate_files': sorted(p.name for p in out.iterdir()), 'local_details': local.relative_to(ROOT).as_posix()})
    print(json.dumps({'status': 'Exploratory', 'origin': ORIGIN, 'elapsed_seconds': audit['elapsed_seconds']}), flush=True)


if __name__ == '__main__':
    main()
