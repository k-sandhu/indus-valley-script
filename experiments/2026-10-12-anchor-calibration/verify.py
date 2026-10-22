"""Recompute headline values by separate code paths.

Study R statistics are recomputed with the anchor-expansion package's own frozen
aggregate() function for the published map, regenerated null draws and the fitted maps.
Study P z values use the same function's positional moments. Study L null summaries are
recomputed from the saved local draws; engine equality is in lexical/engine-verification-v2.json.
Version 2 (Amendment 1) reads the second engine check and also checks the amendment outputs;
history/verify-v1.py wrote verification.json.
"""
from collections import defaultdict
import importlib.util
import json

import numpy as np

import common as C
import roles as R

OUT = C.HERE / 'verification-v2.json'
SAMPLE = [0, 1, 2, 3, 4, 500, 998, 999]


def codex_module():
    path = C.ROOT / 'experiments/2026-10-12-anchor-expansion/context/run-v2/analyze_complete.py'
    spec = importlib.util.spec_from_file_location('codex_analyze_complete', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, C.sha(path)


def frames_for(strings):
    recs = [{'seq': s['seq'], 'physical_ids': {s['component_id']}, 'component_id': s['component_id']} for s in strings]
    out = {'all': recs}
    for name in ['discovery', 'transfer']:
        out[name] = [r for r, s in zip(recs, strings) if s['split'] == name]
    for name in ['H1', 'H2']:
        out[name] = [r for r, s in zip(recs, strings) if s['half'] == name]
    return out


def codex_family_stats(mod, frames, mapping, roles):
    """R1 families and per-family excess using the frozen aggregate()."""
    rows = {}
    for fid, codes in mapping.items():
        role = roles[fid]
        if role == 'unconstrained' or not codes:
            continue
        agg = {name: mod.aggregate(frames[name], set(codes), set()) for name in ['all', 'discovery', 'transfer', 'H2']}
        d, t = agg['discovery']['role_scores'][role], agg['transfer']['role_scores'][role]
        rows[fid] = {
            'excess_all': agg['all']['role_scores'][role]['observed_minus_expected'],
            'excess_H2': agg['H2']['role_scores'][role]['observed_minus_expected'] if agg['H2']['tokens'] else 0.0,
            'passes': (agg['all']['containing_inscriptions'] >= 5 and not d['empty_sample'] and not t['empty_sample']
                       and d['supporting_direction'] is True and t['supporting_direction'] is True)}
    return rows


def main():
    if OUT.exists():
        raise SystemExit('Refusing to overwrite')
    mod, mod_sha = codex_module()
    T = R.Tables()
    frames = frames_for(T.strings)
    summary = json.loads((C.HERE / 'roles/summary.json').read_text(encoding='utf-8'))
    fitted = json.loads((C.HERE / 'roles/fitted-maps.json').read_text(encoding='utf-8'))
    roles = dict(zip(T.fid, T.frole))
    checks = {}

    # Published map.
    pub_map = {f['id']: f['codes'] for f in T.families}
    pub = codex_family_stats(mod, frames, pub_map, roles)
    ev = R.evaluate(T, T.label0)
    checks['published_R1'] = {'codex_aggregate': sum(r['passes'] for r in pub.values()), 'this_package': ev['R1'],
                              'summary_json': summary['published']['R1']}
    checks['published_R3_all'] = {'codex_aggregate': sum(r['excess_all'] for r in pub.values()),
                                  'this_package': ev['R3_all']}
    checks['published_R3_H2'] = {'codex_aggregate': sum(r['excess_H2'] for r in pub.values()),
                                 'this_package': ev['R3_H2']}

    # Regenerated null draws, compared with the saved family excesses.
    saved = np.load(C.LOCAL / 'roles/null-draws.npz')
    rng = np.random.default_rng(np.random.SeedSequence(C.SEED, spawn_key=(R.FAMILY_SPAWN,)))
    draws = [R.permute(T, T.label0, rng) for _ in range(R.N_NULL)]
    assert all((draws[i] == saved['labels'][i]).all() for i in range(R.N_NULL))
    null_rows = []
    for i in SAMPLE:
        mapping = R.labels_to_map(T, draws[i])
        cx = codex_family_stats(mod, frames, mapping, roles)
        mine = R.evaluate(T, draws[i])
        excess_saved = saved['family_excess_all'][i]
        excess_codex = np.array([cx[T.fid[k]]['excess_all'] if T.fid[k] in cx else 0.0 for k in T.constrained])
        null_rows.append({'draw': i, 'R1_codex': sum(r['passes'] for r in cx.values()), 'R1_package': mine['R1'],
                          'max_abs_family_excess_difference': float(np.abs(excess_saved - excess_codex).max())})
    checks['null_draws'] = null_rows
    r1_draws = [R.evaluate(T, d)['R1'] for d in draws]
    checks['R1_null_recomputed'] = {'mean': float(np.mean(r1_draws)), 'sd': float(np.std(r1_draws, ddof=1)),
                                    'p': (1 + sum(x >= ev['R1'] for x in r1_draws)) / (1 + len(r1_draws)),
                                    'summary_json': {k: summary['statistics']['R1'][k] for k in ['null_mean', 'null_sd', 'p_at_or_above']}}

    # Fitted maps.
    fit_rows = {}
    for name in ['R3_exact_all_strings', 'R1_annealed_best', 'membership_fit_H1']:
        cx = codex_family_stats(mod, frames, fitted[name], roles)
        fit_rows[name] = {'R1_codex': sum(r['passes'] for r in cx.values()),
                          'R3_all_codex': sum(r['excess_all'] for r in cx.values()),
                          'R3_H2_codex': sum(r['excess_H2'] for r in cx.values())}
    fit_rows['summary_json'] = {'R1_bound': summary['statistics']['R1']['bound'],
                                'R3_bound': summary['statistics']['R3_all']['bound'],
                                'H1_fit_R3_on_H2': next(t for t in summary['transfer'] if t['fit_half'] == 'H1'
                                                        and t['variant'].startswith('membership'))['H2']['R3_fit']['published']}
    checks['fitted_maps'] = fit_rows

    # Fitted maps keep per-stratum member counts.
    counts_ok = True
    for name in ['R3_exact_all_strings', 'R2_exact_all_strings', 'R1_annealed_best', 'R5_annealed_best',
                 'membership_fit_H1', 'membership_fit_H2']:
        for fid, codes in fitted[name].items():
            a = sorted(T.strata[c] for c in codes)
            b = sorted(T.strata[c] for c in pub_map[fid])
            counts_ok &= a == b
    checks['fitted_maps_keep_stratum_counts'] = counts_ok

    # Half split isolation.
    comp_half = defaultdict(set)
    for s in T.strings:
        comp_half[s['component_id']].add(s['half'])
    checks['half_split'] = {'components_in_both_halves': sum(len(v) > 1 for v in comp_half.values()),
                            'strings': {h: int(T.masks[h].sum()) for h in ['H1', 'H2']}}

    # Study P z values from the frozen aggregate's positional moments.
    pos = json.loads((C.HERE / 'positional/summary.json').read_text(encoding='utf-8'))
    prow = {}
    for row in pos['named_codes']:
        code = row['code'][1:]
        agg = mod.aggregate(frames['all'], {code}, set())
        prow[row['code']] = {'codex_final_z': agg['positions']['final']['z'], 'package_final_z': row['final_z']}
    checks['positional'] = prow

    # Study L null summaries from saved draws.
    lex = json.loads((C.HERE / 'lexical/summary.json').read_text(encoding='utf-8'))
    ld = json.loads((C.LOCAL / 'lexical/null-draws.json').read_text(encoding='utf-8'))['draws']
    lrows = {}
    for kind in ['L1', 'L2']:
        ds = [d for d in ld if d['kind'] == kind]
        for key in ['nonempty_full_intersections_preferred', 'distinct_new_anchor_windows',
                    'codes_with_repeated_exact_residual_both_scenarios']:
            obs = lex['published'][key]
            vals = [d[key] for d in ds]
            lrows[f'{kind}:{key}'] = {'n': len(vals), 'mean': float(np.mean(vals)),
                                      'p': (1 + sum(v >= obs for v in vals)) / (1 + len(vals)),
                                      'summary_json': {k: lex['statistics'][kind][key][k] for k in ['null_mean', 'p_at_or_above']}}
    checks['lexical_null_recomputed'] = lrows
    engine = json.loads((C.HERE / 'lexical/engine-verification-v2.json').read_text(encoding='utf-8'))
    checks['lexical_engine_equal_to_frozen_function'] = (engine['all_equal']
                                                         and engine['lexical_code_sha256'] == C.sha(C.HERE / 'lexical.py'))
    checks['lexical_engine_checked_code_sha256'] = engine['lexical_code_sha256']

    # Amendment 1: corrected R1 bound map and resolution extension.
    amend = json.loads((C.HERE / 'roles/amendment-r1-bound.json').read_text(encoding='utf-8'))
    cx = codex_family_stats(mod, frames, amend['best_map'], roles)
    keeps = all(sorted(T.strata[c] for c in codes) == sorted(T.strata[c] for c in pub_map[fid])
                for fid, codes in amend['best_map'].items())
    checks['amendment_r1_bound'] = {'reported': amend['corrected_bound'],
                                    'R1_codex_on_best_map': sum(r['passes'] for r in cx.values()),
                                    'best_map_keeps_stratum_counts': keeps}
    res = json.loads((C.HERE / 'roles/amendment-resolution.json').read_text(encoding='utf-8'))
    q = C.bh([r['p'] for r in res['families']])
    checks['amendment_resolution'] = {'draws': res['draws'],
                                      'bh_recomputed_matches': all(abs(a - r['bh_q']) < 1e-12 for a, r in zip(q, res['families']))}

    tol = 1e-6
    ok = (checks['published_R1']['codex_aggregate'] == checks['published_R1']['this_package'] == checks['published_R1']['summary_json'] == 21
          and abs(checks['published_R3_all']['codex_aggregate'] - checks['published_R3_all']['this_package']) < tol
          and abs(checks['published_R3_H2']['codex_aggregate'] - checks['published_R3_H2']['this_package']) < tol
          and all(r['R1_codex'] == r['R1_package'] and r['max_abs_family_excess_difference'] < tol for r in null_rows)
          and abs(checks['R1_null_recomputed']['mean'] - summary['statistics']['R1']['null_mean']) < tol
          and fit_rows['R1_annealed_best']['R1_codex'] == summary['statistics']['R1']['bound']
          and abs(fit_rows['R3_exact_all_strings']['R3_all_codex'] - summary['statistics']['R3_all']['bound']) < tol
          and abs(fit_rows['membership_fit_H1']['R3_H2_codex'] - fit_rows['summary_json']['H1_fit_R3_on_H2']) < tol
          and counts_ok and checks['half_split']['components_in_both_halves'] == 0
          and all(abs(v['codex_final_z'] - v['package_final_z']) < tol for v in prow.values())
          and all(abs(v['mean'] - v['summary_json']['null_mean']) < tol and abs(v['p'] - v['summary_json']['p_at_or_above']) < tol
                  for v in lrows.values())
          and checks['lexical_engine_equal_to_frozen_function']
          and checks['amendment_r1_bound']['reported'] == checks['amendment_r1_bound']['R1_codex_on_best_map']
          and checks['amendment_r1_bound']['best_map_keeps_stratum_counts']
          and checks['amendment_resolution']['bh_recomputed_matches'] and res['draws'] == 10_000)
    C.write_json(OUT, {'status': 'pass' if ok else 'FAIL', 'codex_aggregate_sha256': mod_sha,
                       'code_sha256': C.sha(__file__), 'checks': checks})
    print('verification', 'pass' if ok else 'FAIL')
    assert ok


if __name__ == '__main__':
    main()
