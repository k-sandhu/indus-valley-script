"""Amendment 1 (exploratory): locality of opening, closing and middle segments of seal texts."""
import json
import os
from collections import defaultdict

import numpy as np

import analysis as A

SEED = 20261012 + 101
N_PERM = 10000
N_BOOT = 2000


def groups_by(seals, key):
    g = defaultdict(list)
    for i, f in enumerate(seals):
        k = key(f["signs_reading_rtl"])
        if k is not None:
            g[k].append(i)
    return [idx for idx in g.values() if len(idx) >= 2]


def shares(groups, labels):
    out, pw_same, pw_n = [], 0, 0
    for idx in groups:
        lab = labels[idx]
        k = len(lab)
        _, c = np.unique(lab, return_counts=True)
        same = int((c * (c - 1) // 2).sum())
        n = k * (k - 1) // 2
        out.append(same / n)
        pw_same += same
        pw_n += n
    return np.array(out), pw_same / pw_n


def main():
    rng = np.random.default_rng(SEED)
    faces = A.load()
    seals = [f for f in A.eligible_seals(faces) if len(f["signs_reading_rtl"]) >= 4]
    sites = np.array([f["site"] for f in seals])
    keys = {
        "opening_pair": lambda t: tuple(t[:2]),
        "closing_pair": lambda t: tuple(t[-2:]),
        "opening_sign": lambda t: t[0],
        "closing_sign": lambda t: t[-1],
        "middle_pair_len5plus": lambda t: tuple(t[1:3]) if len(t) >= 5 else None,
    }
    grp = {k: groups_by(seals, f) for k, f in keys.items()}
    perms = [sites[rng.permutation(len(sites))] for _ in range(N_PERM)]
    out = {"population_seals_len4plus": len(seals)}
    obs_shares = {}
    for k, g in grp.items():
        s, pw = shares(g, sites)
        obs_shares[k] = s
        null_t = np.empty(N_PERM)
        null_p = np.empty(N_PERM)
        for r, p in enumerate(perms):
            ns, npw = shares(g, p)
            null_t[r] = ns.mean()
            null_p[r] = npw
        out[k] = {"groups": len(g), "seals_in_groups": int(sum(len(i) for i in g)),
                  "L_text_weighted": float(s.mean()), "null_mean": float(null_t.mean()),
                  "null_q975": float(np.quantile(null_t, 0.975)),
                  "p_one_sided": float((1 + (null_t >= s.mean()).sum()) / (N_PERM + 1)),
                  "ratio": float(s.mean() / null_t.mean()),
                  "L_pair_weighted": pw, "pair_null_mean": float(null_p.mean()),
                  "pair_p_one_sided": float((1 + (null_p >= pw).sum()) / (N_PERM + 1)),
                  "pair_ratio": pw / float(null_p.mean())}
    # bootstrap over groups for the ratio difference opening_pair - closing_pair
    o, c = obs_shares["opening_pair"], obs_shares["closing_pair"]
    no, nc = out["opening_pair"]["null_mean"], out["closing_pair"]["null_mean"]
    diffs = []
    for _ in range(N_BOOT):
        bo = o[rng.integers(len(o), size=len(o))].mean() / no
        bc = c[rng.integers(len(c), size=len(c))].mean() / nc
        diffs.append(bo - bc)
    out["opening_minus_closing_ratio"] = {"estimate": out["opening_pair"]["ratio"] - out["closing_pair"]["ratio"],
                                          "ci95": [float(np.quantile(diffs, 0.025)), float(np.quantile(diffs, 0.975))]}
    with open(os.path.join(A.HERE, "run-2026-10-12", "segments.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("population", len(seals))
    for k in keys:
        v = out[k]
        print(k, v["groups"], v["seals_in_groups"], "L %.3f null %.3f q975 %.3f p %.4f ratio %.2f | pair %.3f/%.3f p %.4f" % (
            v["L_text_weighted"], v["null_mean"], v["null_q975"], v["p_one_sided"], v["ratio"],
            v["L_pair_weighted"], v["pair_null_mean"], v["pair_p_one_sided"]))
    print(out["opening_minus_closing_ratio"])


if __name__ == "__main__":
    main()
