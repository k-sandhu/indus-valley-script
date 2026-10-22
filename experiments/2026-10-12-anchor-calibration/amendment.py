"""Amendment 1, written after the frozen outputs and an independent review were seen.

1. Corrected R1 bound: the version-1 annealer did not initialize containing-string counts.
2. Resolution extension: 10,000 further within-stratum draws for per-family p and BH q,
   because 1,000 draws cannot give q <= 0.01 unless six families sit at the p floor.
3. Supplementary values cited in REPORT.md that no earlier output contained.
No frozen output is changed.
"""
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import time

import numpy as np

import common as C
import positional as P
import roles as R

OUT_BOUND = C.HERE / 'roles/amendment-r1-bound.json'
OUT_RES = C.HERE / 'roles/amendment-resolution.json'
OUT_SUP = C.HERE / 'diagnostics-supplement.json'
BOUND_SPAWN, RES_SPAWN = 4, 5
N_EXTRA = 10_000

_T = None


def _init():
    global _T
    _T = R.Tables()


def bound_job(args):
    restart, seed = args
    rng = np.random.default_rng(seed)
    start = R.permute(_T, _T.label0, rng)
    t0 = time.time()
    ann = R.R1Annealer(_T, start, rng)
    assert (ann.contain == R.evaluate(_T, start)['containing']).all()
    best, lab = ann.run(R.ANNEAL_STEPS)
    ev = R.evaluate(_T, lab)
    assert ev['R1'] == best
    return {'restart': restart, 'seed': seed, 'start_value': R.evaluate(_T, start)['R1'], 'best': best,
            'seconds': time.time() - t0, 'labels': lab.tolist(), 'evaluation': R.scalar_view(ev)}


def resolution(T):
    rng = np.random.default_rng(np.random.SeedSequence(C.SEED, spawn_key=(RES_SPAWN,)))
    ev_pub = R.evaluate(T, T.label0, frames=('all', 'discovery', 'transfer'))
    fam = defaultdict(list)
    scal = defaultdict(list)
    for _ in range(N_EXTRA):
        ev = R.evaluate(T, R.permute(T, T.label0, rng), frames=('all', 'discovery', 'transfer'))
        for k in T.constrained:
            fam[k].append(ev['families']['all']['m'][k] - ev['families']['all']['e'][k])
        for key in ['R1', 'R2', 'R3_all', 'R5_compatible']:
            scal[key].append(ev[key])
    rows, pvals = [], []
    for k in T.constrained:
        x = float(ev_pub['families']['all']['m'][k] - ev_pub['families']['all']['e'][k])
        d = np.array(fam[k])
        p = (1 + int((d >= x - C.TOL).sum())) / (1 + N_EXTRA)
        pvals.append(p)
        rows.append({'family_id': T.fid[k], 'role': T.frole[k], 'excess': x, 'null_mean': float(d.mean()),
                     'null_sd': float(d.std(ddof=1)), 'draws_at_or_above': int((d >= x - C.TOL).sum()), 'p': p})
    for row, q in zip(rows, C.bh(pvals)):
        row['bh_q'] = q
    rows.sort(key=lambda r: r['p'])
    scalars = {key: C.null_summary(ev_pub[key], vals) for key, vals in scal.items()}
    return {'draws': N_EXTRA, 'seed_entropy': C.SEED, 'spawn_key': [RES_SPAWN],
            'families_q_at_most_0.01': [r['family_id'] for r in rows if r['bh_q'] <= 0.01],
            'families_q_at_most_0.05': [r['family_id'] for r in rows if r['bh_q'] <= 0.05],
            'families': rows, 'statistics': scalars}


def supplement(T):
    out = {}
    prior = C.read_json('experiments/2026-10-11-bonta-adversarial/run-v6/catalogue-data.json')
    v6 = {r['code']: r for r in prior['rows']}
    st = P.code_statistics(T.strings, T.codes)
    fam = {c: f for f in T.families for c in f['codes']}
    ranking = {}
    for b in range(len(C.FREQ_BINS)):
        members = [c for c in T.codes if T.strata[c] == b and st[c]['final_z'] is not None]
        top = sorted(members, key=lambda c: (-st[c]['final_z'], c))[:10]
        ranking[str(b)] = {'bin': C.FREQ_BINS[b], 'codes': len(members), 'top_final_z': [
            {'code': 'W' + c, 'final_z': st[c]['final_z'], 'tokens': st[c]['tokens'],
             'october_11_tier': v6[c]['tier'], 'october_11_meaning': v6[c]['meaning'],
             'anchor_expansion_family': fam[c]['id'] if c in fam else None,
             'anchor_expansion_role': fam[c]['role'] if c in fam else None} for c in top],
            'top_nonfinal_z': [{'code': 'W' + c, 'nonfinal_z': st[c]['nonfinal_z']}
                               for c in sorted(members, key=lambda c: (-st[c]['nonfinal_z'], c))[:10]]}
    out['final_z_rankings_by_stratum'] = ranking
    containing = [s for s in T.strings if '740' in s['seq']]
    out['W740'] = {'strings_containing': len(containing),
                   'strings_ending_in_W740': sum(s['seq'][-1] == '740' for s in containing)}
    comp = defaultdict(lambda: [0, None])
    for s in T.strings:
        comp[s['component_id']][0] += 1
        comp[s['component_id']][1] = s['half']
    sizes = sorted(((n, h) for n, h in comp.values()), reverse=True)
    out['half_split_components'] = {
        'components': len(comp), 'largest_component_strings': sizes[0][0], 'largest_component_half': sizes[0][1],
        'five_largest': [{'strings': n, 'half': h} for n, h in sizes[:5]],
        'components_per_half': dict(Counter(h for _, h in comp.values()))}
    # L2 window-count mode: regenerate placements from the saved seeds.
    import lexical as L
    entries, unique, pairs, anchors = L.load_inputs()
    bin_of, count = L.strata_for(unique)
    draws = [d for d in json.loads((C.LOCAL / 'lexical/null-draws.json').read_text(encoding='utf-8'))['draws']
             if d['kind'] == 'L2']
    on002, other = [], []
    for d in draws:
        _, holders = L.permute_L2(pairs, anchors, bin_of, count, np.random.default_rng(d['seed']))
        (on002 if '002' in holders else other).append(d['distinct_new_anchor_windows'])
    out['L2_windows_by_W002_placement'] = {
        'top_stratum_anchor': ['W' + a for a in anchors if bin_of(a) == 7],
        'top_stratum_targets': [{'code': 'W' + c, 'tokens': count[c]} for c in sorted(count)
                                if bin_of(c) == 7 and (c not in pairs or c in anchors)],
        'draws_placing_an_anchor_on_W002': len(on002),
        'windows_when_on_W002': {'mean': float(np.mean(on002)), 'min': int(min(on002)), 'max': int(max(on002))},
        'windows_otherwise': {'mean': float(np.mean(other)), 'min': int(min(other)), 'max': int(max(other))}}
    return out


def main():
    for path in [OUT_BOUND, OUT_RES, OUT_SUP]:
        if path.exists():
            raise SystemExit('Refusing to overwrite ' + str(path))
    C.check_pins()
    t0 = time.time()
    T = R.Tables()
    seeds = np.random.SeedSequence(C.SEED, spawn_key=(BOUND_SPAWN,)).generate_state(R.RESTARTS)
    with ProcessPoolExecutor(max_workers=R.RESTARTS, initializer=_init) as pool:
        bound_future = pool.map(bound_job, [(r, int(s)) for r, s in enumerate(seeds)])
        res = resolution(T)
        sup = supplement(T)
        runs = list(bound_future)
    frozen = json.loads((C.HERE / 'roles/summary.json').read_text(encoding='utf-8'))
    pub_r1 = frozen['published']['R1']
    best = max(r['best'] for r in runs)
    best_run = max(runs, key=lambda r: r['best'])
    mean = frozen['statistics']['R1']['null_mean']
    common = {'status': 'Amendment 1; post-outcome and post-review', 'code_sha256': C.sha(__file__),
              'roles_code_sha256': C.sha(C.HERE / 'roles.py'), 'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md')}
    C.write_json(OUT_BOUND, {**common,
                             'reason': 'Version-1 R1Annealer left containing-string counts at zero, so its objective was wrong; its reported 47 is an achieved value.',
                             'version_1_bound': frozen['statistics']['R1']['bound'], 'corrected_bound': best,
                             'published': pub_r1, 'null_mean': mean,
                             'share_of_achievable_gain': (pub_r1 - mean) / (max(best, frozen['statistics']['R1']['bound']) - mean),
                             'seed_entropy': C.SEED, 'spawn_key': [BOUND_SPAWN], 'proposals_per_restart': R.ANNEAL_STEPS,
                             'runs': [{k: v for k, v in r.items() if k != 'labels'} for r in runs],
                             'best_map': R.labels_to_map(T, np.array(best_run['labels']))})
    C.write_json(OUT_RES, {**common, 'reason': 'Per-family BH q cannot reach 0.01 with 1,000 draws unless six families are at the p floor.', **res})
    C.write_json(OUT_SUP, {**common, 'reason': 'Values cited in REPORT.md without an earlier saved output.', **sup})
    print('corrected R1 bound', best, [r['best'] for r in runs], 'time', time.time() - t0)
    print('q<=0.01', res['families_q_at_most_0.01'], 'q<=0.05', res['families_q_at_most_0.05'])
    for r in res['families'][:6]:
        print(r['family_id'], round(r['excess'], 1), r['draws_at_or_above'], r['p'], round(r['bh_q'], 4))
    print({k: (v['p_at_or_above'], round(v['z'], 2)) for k, v in res['statistics'].items()})


if __name__ == '__main__':
    main()
