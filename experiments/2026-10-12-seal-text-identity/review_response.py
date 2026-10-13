"""Amendment 3 (post-review, exploratory): recomputation of the review's checks with saved output.

A. Same-site duplicate pairs by site class (Mohenjo-daro, Harappa, other) against length-stratified and
   global permutation nulls; S1 restricted to seals outside Mohenjo-daro.
B. Mixture bound: the largest share f of shared texts that could be wholly local while the observed
   text-weighted L stays within the lower 95% of the mixture distribution (length-stratified null).
C. Variant-merged texts under the length-stratified null.
D. S3 with the bigram model fitted to distinct seal texts only and to distinct non-seal texts only.
E. S4 decomposed into unicorn and non-unicorn pairs, and with "no motif" treated as its own category.
F. Amendment 1: permutation null for the difference between opening- and closing-pair ratios.
G. S5 recount: tags whose matching seals are all at other sites, and distinct texts.
"""
import json
import math
import os
from collections import Counter, defaultdict

import numpy as np

import analysis as A

SEED = 20261012 + 303
N_PERM = 10000


def strat_perm(labels, strata, rng):
    perm = labels.copy()
    for s in np.unique(strata):
        pos = np.where(strata == s)[0]
        perm[pos] = labels[pos][rng.permutation(len(pos))]
    return perm


def pair_counts_by_class(groups, sites):
    c = Counter()
    for idx in groups:
        lab = sites[idx]
        for i in range(len(lab)):
            for j in range(i + 1, len(lab)):
                if lab[i] == lab[j]:
                    c["MD" if lab[i] == "Mohenjo-daro" else "H" if lab[i] == "Harappa" else "other"] += 1
    return c


def main():
    rng = np.random.default_rng(SEED)
    faces = A.load()
    seals = A.eligible_seals(faces)
    sites = np.array([f["site"] for f in seals])
    exact = [tuple(f["signs_reading_rtl"]) for f in seals]
    lengths = np.array([len(t) for t in exact])
    g = defaultdict(list)
    for i, t in enumerate(exact):
        g[t].append(i)
    groups = [idx for idx in g.values() if len(idx) >= 2]
    out = {}

    # A
    obs = pair_counts_by_class(groups, sites)
    sims_len, sims_glob = defaultdict(list), defaultdict(list)
    for _ in range(N_PERM):
        pl = strat_perm(sites, lengths, rng)
        pg = sites[rng.permutation(len(sites))]
        cl, cg = pair_counts_by_class(groups, pl), pair_counts_by_class(groups, pg)
        for k in ("MD", "H", "other"):
            sims_len[k].append(cl[k])
            sims_glob[k].append(cg[k])
    out["A_same_site_pairs_by_class"] = {
        k: {"observed": obs[k],
            "expected_length_stratified": float(np.mean(sims_len[k])),
            "p_length_stratified": float((1 + sum(x >= obs[k] for x in sims_len[k])) / (N_PERM + 1)),
            "expected_global": float(np.mean(sims_glob[k])),
            "p_global": float((1 + sum(x >= obs[k] for x in sims_glob[k])) / (N_PERM + 1))}
        for k in ("MD", "H", "other")}
    non_md = np.where(sites != "Mohenjo-daro")[0]
    remap = {old: new for new, old in enumerate(non_md)}
    g2 = [[remap[i] for i in idx if i in remap] for idx in groups]
    g2 = [x for x in g2 if len(x) >= 2]
    out["A_outside_mohenjo_daro"] = A.permutation_test(g2, sites[non_md], rng, n=N_PERM)
    out["A_outside_mohenjo_daro"]["seals"] = int(len(non_md))

    # B
    obs_shares = []
    for idx in groups:
        lab = sites[idx]
        _, c = np.unique(lab, return_counts=True)
        k = len(lab)
        obs_shares.append((c * (c - 1) // 2).sum() / (k * (k - 1) // 2))
    L_obs = float(np.mean(obs_shares))
    null_shares = []
    for _ in range(2000):
        pl = strat_perm(sites, lengths, rng)
        row = []
        for idx in groups:
            lab = pl[idx]
            _, c = np.unique(lab, return_counts=True)
            k = len(lab)
            row.append((c * (c - 1) // 2).sum() / (k * (k - 1) // 2))
        null_shares.append(row)
    null_shares = np.array(null_shares)
    G = len(groups)
    bound = {}
    for f in [round(x, 2) for x in np.arange(0, 0.51, 0.05)]:
        k = int(round(f * G))
        sims = []
        for r in range(2000):
            row = null_shares[r].copy()
            if k:
                row[rng.choice(G, size=k, replace=False)] = 1.0
            sims.append(row.mean())
        bound[str(f)] = float(np.mean(np.array(sims) <= L_obs))
    out["B_mixture"] = {"L_observed": L_obs, "null_mean_length_stratified": float(null_shares.mean()),
                        "f_point_text_weighted": (L_obs - null_shares.mean()) / (1 - null_shares.mean()),
                        "P_mixture_at_or_below_observed_by_f": bound,
                        "f_upper_95": max(float(f) for f, p in bound.items() if p >= 0.05)}

    # C
    with open(os.path.join(A.ROOT, "data", "normalized", "mayig_wells_class_crosswalk.json"), encoding="utf-8") as f:
        cw = json.load(f)["by_wells_id"]
    merge = {w: v[0] for w, v in cw.items() if len(v) == 1}
    merged = [tuple(merge.get(x, x) for x in t) for t in exact]
    gm = defaultdict(list)
    for i, t in enumerate(merged):
        gm[t].append(i)
    gm = [idx for idx in gm.values() if len(idx) >= 2]
    out["C_merged_length_stratified"] = A.permutation_test(gm, sites, rng, n=N_PERM,
                                                           strata=np.array([len(t) for t in merged]))

    # D
    legible_all = [f for f in faces if A.legible(f, 1)]
    seal_texts = sorted({tuple(f["signs_reading_rtl"]) for f in legible_all if f["object_type"].startswith("SEAL")})
    other_texts = sorted({tuple(f["signs_reading_rtl"]) for f in legible_all if not f["object_type"].startswith("SEAL")})
    lens = Counter(len(t) for t in exact)
    obs_pairs = Counter()
    for idx in groups:
        obs_pairs[len(exact[idx[0]])] += len(idx) * (len(idx) - 1) // 2
    d = {}
    for name, train in (("seal_texts_only", seal_texts), ("non_seal_texts_only", other_texts)):
        vocab = sorted({x for t in train for x in t} | {x for t in exact for x in t})
        s, T, e, D = A.kn_bigram(train, vocab)
        coinc = A.coincidence_by_length(s, T, e, max(lens))
        exp4 = sum(math.comb(n, 2) * coinc[L][1] / coinc[L][0] ** 2 for L, n in lens.items() if L >= 4)
        obs4 = sum(v for L, v in obs_pairs.items() if L >= 4)
        d[name] = {"training_texts": len(train), "len4plus_expected": exp4, "len4plus_observed": obs4, "ratio": obs4 / exp4}
    out["D_S3_training_variants"] = d

    # E
    mot = [A.motif(f) for f in seals]
    pairs = []
    for idx in groups:
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                i, j = idx[a], idx[b]
                pairs.append((mot[i], mot[j]))
    both = [(x, y) for x, y in pairs if x and y]
    uni = [(x, y) for x, y in both if x == "Bull1" and y == "Bull1"]
    non_uni = [(x, y) for x, y in both if not (x == "Bull1" and y == "Bull1")]
    out["E_motif_pairs"] = {"pairs_with_both_motifs": len(both), "same_motif": sum(x == y for x, y in both),
                            "unicorn_unicorn": len(uni),
                            "pairs_involving_non_unicorn": len(non_uni),
                            "same_motif_among_non_unicorn": sum(x == y for x, y in non_uni)}
    mot_cat = np.array([m if m else "NONE" for m in mot])
    out["E_none_as_category"] = A.permutation_test(groups, mot_cat, rng, n=N_PERM, strata=sites)

    # F
    seg_seals = [i for i, t in enumerate(exact) if len(t) >= 4]
    ss = sites[seg_seals]
    def seg_groups(key):
        gg = defaultdict(list)
        for k, i in enumerate(seg_seals):
            gg[key(exact[i])].append(k)
        return [x for x in gg.values() if len(x) >= 2]
    go, gc = seg_groups(lambda t: t[:2]), seg_groups(lambda t: t[-2:])
    def tw(groups_, lab):
        vals = []
        for idx in groups_:
            l = lab[idx]
            _, c = np.unique(l, return_counts=True)
            k = len(l)
            vals.append((c * (c - 1) // 2).sum() / (k * (k - 1) // 2))
        return float(np.mean(vals))
    perms = [ss[rng.permutation(len(ss))] for _ in range(N_PERM)]
    null_o = np.array([tw(go, p) for p in perms])
    null_c = np.array([tw(gc, p) for p in perms])
    obs_diff = tw(go, ss) / null_o.mean() - tw(gc, ss) / null_c.mean()
    null_diff = null_o / null_o.mean() - null_c / null_c.mean()
    out["F_opening_minus_closing"] = {"observed": obs_diff, "null_q025": float(np.quantile(null_diff, 0.025)),
                                      "null_q975": float(np.quantile(null_diff, 0.975)),
                                      "p_one_sided": float((1 + (null_diff >= obs_diff).sum()) / (N_PERM + 1))}

    # G
    with open(os.path.join(A.HERE, "run-2026-10-12", "summary.json"), encoding="utf-8") as f:
        S = json.load(f)
    rows = S["S5_tags_matching_seals"]["rows"]
    only_other = [r for r in rows if all(s != r["tag_site"] for s, _ in r["seal_sites"])]
    out["G_S5_recount"] = {"rows": len(rows), "distinct_texts": len({r["text_id"] for r in rows}),
                           "rows_matching_only_other_site_seals": len(only_other),
                           "texts_matching_only_other_site_seals": len({r["text_id"] for r in only_other})}

    with open(os.path.join(A.HERE, "run-2026-10-12", "review-response.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k not in ("A_outside_mohenjo_daro", "C_merged_length_stratified", "E_none_as_category")}, indent=1))
    for k in ("A_outside_mohenjo_daro", "C_merged_length_stratified", "E_none_as_category"):
        v = out[k]
        print(k, {x: round(v["text_weighted"][x], 3) for x in ("observed", "null_mean", "p_one_sided")},
              {x: round(v["pair_weighted"][x], 3) for x in ("observed", "null_mean", "p_one_sided")})


if __name__ == "__main__":
    main()
