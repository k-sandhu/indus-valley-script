"""Post-outcome diagnostics for Study R, added after the frozen outputs were seen.

The R3 null is bimodal. This script decomposes the published and permuted total excess by
stratum, conditions on whether W740 receives a closing label, and recomputes the headline
statistics with W740 removed from every map. It changes no frozen output.
"""
import numpy as np

import common as C
import roles as R

OUT = C.HERE / 'roles/diagnostics-post-outcome.json'


def main():
    if OUT.exists():
        raise SystemExit('Refusing to overwrite')
    T = R.Tables()
    saved = np.load(C.LOCAL / 'roles/null-draws.npz')
    labs = saved['labels']
    X = T.code_value('all', 'x')
    i740 = T.ci['740']

    def per_code_excess(labels):
        ridx = T.role_index(labels)
        out = np.zeros(len(T.codes))
        ok = ridx >= 0
        out[ok] = X[np.flatnonzero(ok), ridx[ok]]
        return out

    pub = per_code_excess(T.label0)
    null = np.array([per_code_excess(l) for l in labs])
    strata = {}
    for b, idx in T.groups.items():
        p = float(pub[idx].sum())
        d = null[:, idx].sum(axis=1)
        strata[str(b)] = {'bin': C.FREQ_BINS[b] if b >= 0 else None, 'assigned_codes': len(idx),
                          'published_excess': p, 'null_mean': float(d.mean()), 'null_sd': float(d.std(ddof=1)),
                          'p_at_or_above': (1 + int((d >= p - C.TOL).sum())) / (1 + len(d))}
    closing740 = np.array([T.frole[l[i740]] == 'closing' for l in labs])
    evs = [R.evaluate(T, l, frames=('all', 'discovery', 'transfer', 'H2')) for l in labs]
    ev_pub = R.evaluate(T, T.label0, frames=('all', 'discovery', 'transfer', 'H2'))
    cond = {}
    for key in ['R1', 'R2', 'R3_all', 'R5_compatible', 'R3_H2']:
        vals = np.array([e[key] for e in evs])
        cond[key] = {'W740_closing_draws': C.null_summary(ev_pub[key], vals[closing740]),
                     'W740_other_draws': C.null_summary(ev_pub[key], vals[~closing740])}
    # Remove W740 from every map: its label becomes unassigned in the published map and in each draw.
    def without740(labels):
        new = labels.copy()
        new[i740] = -1
        return new
    ev_pub_wo = R.evaluate(T, without740(T.label0), frames=('all', 'discovery', 'transfer', 'H2'))
    evs_wo = [R.evaluate(T, without740(l), frames=('all', 'discovery', 'transfer', 'H2')) for l in labs]
    wo = {key: C.null_summary(ev_pub_wo[key], [e[key] for e in evs_wo])
          for key in ['R1', 'R2', 'R3_all', 'R5_compatible', 'R3_H2']}
    C.write_json(OUT, {
        'status': 'Exploratory post-outcome diagnostic; written after roles/summary.json was seen',
        'code_sha256': C.sha(__file__), 'protocol_sha256': C.sha(C.HERE / 'PROTOCOL.md'),
        'W740': {'tokens': float(T.code_frame['all']['n'][i740]), 'published_family': T.fid[T.label0[i740]],
                 'closing_excess': float(X[i740, C.ROLES.index('closing')]),
                 'top_stratum_assigned_codes': len(T.groups[7]),
                 'top_stratum_closing_labels': int(sum(T.frole[T.label0[i]] == 'closing' for i in T.groups[7])),
                 'draws_with_closing_label': int(closing740.sum())},
        'R3_by_stratum': strata,
        'conditional_on_W740_label': cond,
        'W740_removed_from_every_map': wo,
        'scope': 'W740 is removed by unassigning it; its tokens stay in every string and expectation.'})
    print('W740 closing draws', int(closing740.sum()))
    for k, v in cond.items():
        print(k, 'given W740 closing: p', round(v['W740_closing_draws']['p_at_or_above'], 3),
              'z', None if v['W740_closing_draws']['z'] is None else round(v['W740_closing_draws']['z'], 2))
    for k, v in wo.items():
        print('without W740', k, v['published'], round(v['null_mean'], 1), round(v['null_sd'], 1), 'p', round(v['p_at_or_above'], 3))
    for b, v in strata.items():
        print(b, v['bin'], round(v['published_excess'], 1), round(v['null_mean'], 1), round(v['null_sd'], 1), round(v['p_at_or_above'], 3))


if __name__ == '__main__':
    main()
