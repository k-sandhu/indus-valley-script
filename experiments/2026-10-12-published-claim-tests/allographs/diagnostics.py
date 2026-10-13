#!/usr/bin/env python3
"""Post-outcome diagnostics for Study C (exploratory; not part of the frozen protocol).

Written after run-2026-10-12/summary.json had been inspected, to locate which key
groups drive the primary results. Outputs run-2026-10-12/diagnostics.json.
"""
from __future__ import annotations

import collections
import json

import numpy as np

import allograph_test as at

K = 3
SEED = 20261020


def main():
    key = at.Key(at.KEY)
    mayig = json.loads(at.MAYIG.read_text(encoding="utf-8"))
    _, unique, _ = at.load_corpus(at.CORPUS)
    weights = [1] * len(unique)
    counts = collections.Counter(s for t in unique for s in t)
    codes = sorted(counts)
    idx = {c: i for i, c in enumerate(codes)}
    sets, roots, _, _ = at.build_pairsets(key, mayig)
    mp, _ = at.minimal_pairs(unique, weights, 3)
    mats = at.Profiles(unique, weights, codes).matrices(1.0)
    n = len(codes)
    mpm = np.zeros((n, n))
    for (a, b), v in mp.items():
        mpm[idx[a], idx[b]] = mpm[idx[b], idx[a]] = v
    universe, strata = at.strata_for(codes, counts, K)
    rng = np.random.default_rng(SEED)
    sigma = at.permutations(rng, n, idx, strata, at.R_NULL)
    uset = set(universe)

    def evaluate(pairs):
        pairs = sorted(p for p in pairs if p[0] in uset and p[1] in uset)
        if not pairs:
            return None
        ia = np.array([idx[a] for a, _ in pairs])
        ib = np.array([idx[b] for _, b in pairs])
        out = {"pairs": len(pairs)}
        for name, M, high in (("mp", mpm, True), ("neighbour", mats["neighbour"], False),
                              ("position", mats["position"], False)):
            obs = M[ia, ib]
            null = M[sigma[:, ia], sigma[:, ib]]
            nm = null.mean(1)
            m = obs.mean()
            p = (1 + int(((nm >= m - 1e-12) if high else (nm <= m + 1e-12)).sum())) / (at.R_NULL + 1)
            out[name] = {"observed_sum" if name == "mp" else "observed_mean": float(obs.sum() if name == "mp" else m),
                         "null_expected_sum" if name == "mp" else "null_mean":
                             float(null.mean(0).sum() if name == "mp" else nm.mean()),
                         "p_one_sided": p}
        return out

    p1_out = sets["P1_out"]
    by_root = collections.defaultdict(list)
    for p, r in p1_out.items():
        by_root[r].append(p)
    per_root = {r: evaluate(ps) for r, ps in sorted(by_root.items())}
    per_root = {r: v for r, v in per_root.items() if v}
    loo = {}
    for r in per_root:
        loo[r] = evaluate([p for p in p1_out if p1_out[p] != r])
    worst = {m: max(loo, key=lambda r: loo[r][m]["p_one_sided"]) for m in ("mp", "neighbour")}

    p1_in = sets["P1_in"]
    without_fish = {
        "P1_out_without_root_220": loo.get("220"),
        "P1_without_root_220": evaluate([p for p, r in sets["P1"].items() if r != "220"]),
        "P1_in_without_root_220": evaluate([p for p, r in p1_in.items() if r != "220"]),
    }

    jar = {}
    for s in ("741", "742", "743", "744", "745", "746", "747", "748"):
        pair = ("740", s)
        if pair[1] in uset:
            res = evaluate([pair])
            jar[s] = {"count": counts[s], "mp": res["mp"]["observed_sum"],
                      "neighbour": res["neighbour"]["observed_mean"], "neighbour_null": res["neighbour"]["null_mean"],
                      "position": res["position"]["observed_mean"], "position_null": res["position"]["null_mean"]}
        else:
            jar[s] = {"count": counts[s], "below_k": True}

    p2 = sets["P2"]
    by_value = collections.defaultdict(list)
    for p, v in p2.items():
        by_value[v].append(p)
    p2_values = {v: evaluate(ps) for v, ps in sorted(by_value.items())}
    p2_values = {v: r for v, r in p2_values.items() if r}

    # S2 per root: mixed texts observed against the same root-wise permutation null
    rng2 = np.random.default_rng(SEED + 1)
    per_root_tokens = collections.defaultdict(lambda: ([], []))
    for t, text in enumerate(unique):
        for s in text:
            if key.kind(s) != "ligature":
                per_root_tokens[key.root(s)][0].append(t)
                per_root_tokens[key.root(s)][1].append(s)
    s2 = {}
    for r, (tids, cs) in sorted(per_root_tokens.items()):
        if len(set(cs)) < 2:
            continue
        tids = np.array(tids)
        order = np.argsort(tids, kind="stable")
        tids = tids[order]
        ids = np.unique(np.array(cs)[order], return_inverse=True)[1]
        starts = np.flatnonzero(np.r_[True, tids[1:] != tids[:-1]])
        multi = np.diff(np.r_[starts, len(tids)]) >= 2
        if not multi.any():
            continue
        obs = int(((np.minimum.reduceat(ids, starts) != np.maximum.reduceat(ids, starts)) & multi).sum())
        pc = ids[np.argsort(rng2.random((at.R_NULL, len(ids))), axis=1)]
        null = ((np.minimum.reduceat(pc, starts, axis=1) != np.maximum.reduceat(pc, starts, axis=1))
                & multi[None, :]).sum(1)
        s2[r] = {"texts_with_repeat": int(multi.sum()), "mixed_observed": obs,
                 "mixed_null_mean": float(null.mean()),
                 "p_high": (1 + int((null >= obs).sum())) / (at.R_NULL + 1),
                 "p_low": (1 + int((null <= obs).sum())) / (at.R_NULL + 1)}

    # Wells catalogue order groups similar shapes; split key pairs by code distance and
    # test adjacent pairs that the key does not group.
    def wells_distance(p):
        return abs(int(p[0]) - int(p[1]))
    nonlig = [s for s in key.signs if key.kind(s) != "ligature"]
    adjacent_nonkey = [(a, b) for a in nonlig for b in nonlig
                       if a < b and wells_distance((a, b)) <= 2 and key.root(a) != key.root(b)]
    wells = {
        "rule": "near means |Wells code difference| <= 2",
        "P1_near": evaluate([p for p in sets["P1"] if wells_distance(p) <= 2]),
        "P1_far": evaluate([p for p in sets["P1"] if wells_distance(p) > 2]),
        "P1_out_near": evaluate([p for p in p1_out if wells_distance(p) <= 2]),
        "P1_out_far": evaluate([p for p in p1_out if wells_distance(p) > 2]),
        "P1_out_far_without_root_220": evaluate([p for p in p1_out if wells_distance(p) > 2
                                                 and p1_out[p] != "220"]),
        "adjacent_pairs_not_grouped_by_key": evaluate(adjacent_nonkey),
        "adjacent_not_grouped_not_mayig": evaluate([p for p in adjacent_nonkey if p not in sets["P3"]]),
    }

    out = {"status": "post-outcome exploratory diagnostics; not part of the frozen protocol",
           "wells_order": wells,
           "k": K, "seed": SEED, "R_null": at.R_NULL,
           "P1_out_by_root": per_root,
           "P1_out_leave_one_root_out": loo,
           "P1_out_leave_one_root_out_largest_p": {m: {"root": r, "p": loo[r][m]["p_one_sided"]}
                                                   for m, r in worst.items()},
           "without_fish_root_220": without_fish,
           "jar_740_pairs": jar,
           "P2_by_value": p2_values,
           "S2_by_root": s2}
    path = at.HERE / "run-2026-10-12" / "diagnostics.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"largest_loo_p": out["P1_out_leave_one_root_out_largest_p"],
                      "without_fish": without_fish}, indent=1))


if __name__ == "__main__":
    main()
