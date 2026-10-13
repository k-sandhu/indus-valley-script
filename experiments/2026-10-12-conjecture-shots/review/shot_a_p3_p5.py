"""Exploratory review analysis: stability of Shot A's P3 and coding of the unicorn variant W (P5).

P3. The frozen statistic z(MI first sign; site) - z(MI closing formula; site), with site
labels shuffled within seal type, is recomputed on each half, on the pooled halves with
site recoded (Mohenjo-daro against the rest, Mohenjo-daro excluded, Harappa against
Mohenjo-daro), and on 100 random re-splits of the pooled components into two halves, to
measure how much the statistic moves between halves of this size.

P5. Among unicorn seals of the frozen size population (both halves), the variant W is
compared with the other variant codes and with the bare code `Bull1` (no variant), and the
W share is tabulated against catalogue fields that could record visibility rather than
carving: condition, preservation, dimension source and CISI number range.

Output: review/shot-a-p3-p5.json.
"""
import collections
import math
import re

import numpy as np

from review_common import L, load_all, write_json, STATUS
from shot_a_robustness import build, frozen_population, p4, design_factor, TYPE, SITE, LENC

rng = np.random.default_rng(777001)


def p3_stat(rows, site_of=lambda t: t["site"], nperm=499):
    sites = [site_of(t) for t in rows]
    A = [t["first"] for t in rows]
    B = [t["formula"] for t in rows]
    types = [t["type"] for t in rows]
    groups = collections.defaultdict(list)
    for i, ty in enumerate(types):
        groups[ty].append(i)
    groups = [np.array(v) for v in groups.values()]
    sarr = np.array(sites, dtype=object)
    oa, ob = L.mutual_information(A, sites), L.mutual_information(B, sites)
    na, nb = [], []
    for _ in range(nperm):
        idx = np.arange(len(sites))
        for g in groups:
            idx[g] = g[rng.permutation(len(g))]
        s = list(sarr[idx])
        na.append(L.mutual_information(A, s))
        nb.append(L.mutual_information(B, s))
    na, nb = np.array(na), np.array(nb)
    za, zb = (oa - na.mean()) / na.std(), (ob - nb.mean()) / nb.std()
    Dn = (na - na.mean()) / na.std() - (nb - nb.mean()) / nb.std()
    return {"n": len(rows), "z_first": float(za), "z_formula": float(zb), "z_difference": float(za - zb),
            "p_one_sided": float((1 + (Dn >= za - zb).sum()) / (1 + nperm)), "shuffles": nperm}


def p3_population(tab):
    return L.representative([t for t in tab if t["type"] in L.SEAL_TYPES and t["text_ok"] and t["length"] >= 2
                             and t["site"] != "Unknown"])


def cisi_bin(c):
    m = re.match(r"([A-Za-z]+)-(\d+)", c or "")
    if not m:
        return "none"
    pre, n = m.group(1), int(m.group(2))
    if pre != "M":
        return pre
    for lo, hi in ((1, 500), (501, 1000), (1001, 1500), (1501, 2100)):
        if lo <= n <= hi:
            return f"M-{lo}..{hi}"
    return "M-other"


def w_table(rows, key):
    c = collections.defaultdict(lambda: [0, 0])
    for t in rows:
        c[key(t)][0] += 1
        c[key(t)][1] += t["symbol_full"] == "Bull1:W"
    return {k: {"unicorn_seals": n, "W": w, "W_share": round(w / n, 3)} for k, (n, w) in sorted(c.items(), key=lambda kv: -kv[1][0])}


def main():
    rows = load_all()
    tab = build(rows)
    out = {"status": STATUS}

    # ---------------- P3
    pops = {h: p3_population([t for t in tab if t["half"] == h]) for h in ("discovery", "confirmation")}
    pooled = pops["discovery"] + pops["confirmation"]
    p3 = {h: p3_stat(p, nperm=1999) for h, p in pops.items()}
    p3["pooled"] = p3_stat(pooled, nperm=1999)
    p3["pooled_md_vs_rest"] = p3_stat(pooled, site_of=lambda t: "MD" if t["site"] == "Mohenjo-daro" else "rest", nperm=1999)
    nomd = [t for t in pooled if t["site"] != "Mohenjo-daro"]
    p3["pooled_without_md"] = p3_stat(nomd, nperm=1999)
    hm = [t for t in pooled if t["site"] in ("Harappa", "Mohenjo-daro")]
    p3["pooled_harappa_vs_md"] = p3_stat(hm, nperm=1999)
    for h, p in pops.items():
        p3[h + "_md_vs_rest"] = p3_stat(p, site_of=lambda t: "MD" if t["site"] == "Mohenjo-daro" else "rest", nperm=999)
        p3[h + "_without_md"] = p3_stat([t for t in p if t["site"] != "Mohenjo-daro"], nperm=999)
    # random re-splits of the pooled components
    comps = sorted({t["component"] for t in pooled})
    by_c = collections.defaultdict(list)
    for t in pooled:
        by_c[t["component"]].append(t)
    diffs = []
    for _ in range(100):
        sel = set(np.array(comps, dtype=object)[rng.random(len(comps)) < 0.5])
        a = [t for c in comps if c in sel for t in by_c[c]]
        b = [t for c in comps if c not in sel for t in by_c[c]]
        diffs.append((p3_stat(a, nperm=199)["z_difference"], p3_stat(b, nperm=199)["z_difference"]))
    d = np.array(diffs)
    p3["random_resplits"] = {
        "resplits": len(d), "shuffles_per_half": 199,
        "z_difference_mean": float(d.mean()), "z_difference_sd_over_halves": float(d.std()),
        "share_halves_z_difference_above_1.645": float(np.mean(d > 1.645)),
        "share_halves_z_difference_below_-1.645": float(np.mean(d < -1.645)),
        "share_resplits_halves_disagree_in_sign": float(np.mean(np.sign(d[:, 0]) != np.sign(d[:, 1]))),
        "mean_abs_difference_between_paired_halves": float(np.mean(np.abs(d[:, 0] - d[:, 1]))),
    }
    out["P3"] = p3

    # ---------------- P5
    spops = {h: frozen_population([t for t in tab if t["half"] == h]) for h in ("discovery", "confirmation")}
    allpop = spops["discovery"] + spops["confirmation"]
    y = np.array([t["log_area"] for t in allpop])
    X = L.base_design(allpop)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    for t, r in zip(allpop, res):
        t["_res"] = float(r)
    uni = [t for t in allpop if t["animal"] == "Bull1"]
    code = lambda t: (t["symbol_full"] or "").split(":")[1] if ":" in (t["symbol_full"] or "") else "(none)"
    p5 = {"variant_counts": dict(collections.Counter(code(t) for t in uni).most_common())}
    byv = collections.defaultdict(list)
    for t in uni:
        byv[code(t)].append(t["_res"])
    p5["mean_residual_by_variant"] = {k: {"n": len(v), "mean_residual": round(float(np.mean(v)), 3)}
                                      for k, v in sorted(byv.items(), key=lambda kv: -len(kv[1]))}
    # W against coded variants only (bare Bull1 excluded), per half
    for h, pop in spops.items():
        yy = np.array([t["log_area"] for t in pop])
        XX = L.base_design(pop)
        bb, *_ = np.linalg.lstsq(XX, yy, rcond=None)
        rr = yy - XX @ bb
        keep = [i for i, t in enumerate(pop) if t["animal"] == "Bull1" and code(t) != "(none)"]
        sub = [pop[i] for i in keep]
        lab = ["W" if code(t) == "W" else "U" for t in sub]
        r = L.contrast_test(lab, rr[keep], L.strata_of(sub), {"W"}, {"U"}, 4999, rng)
        p5[h + "_W_vs_coded_variants_only"] = {k: r[k] for k in ("difference", "n_high", "n_low", "p_one_sided")}
        keep2 = [i for i, t in enumerate(pop) if t["animal"] == "Bull1" and code(t) in ("W", "(none)")]
        sub2 = [pop[i] for i in keep2]
        lab2 = ["N" if code(t) == "(none)" else "W" for t in sub2]
        r2 = L.contrast_test(lab2, rr[keep2], L.strata_of(sub2), {"W"}, {"N"}, 4999, rng)
        p5[h + "_W_vs_bare_Bull1"] = {k: r2[k] for k in ("difference", "n_high", "n_low", "p_one_sided")}
        keep3 = [i for i, t in enumerate(pop) if t["animal"] == "Bull1" and t["condition"] in ("Fine", "Good")]
        sub3 = [pop[i] for i in keep3]
        lab3 = ["W" if code(t) == "W" else "U" for t in sub3]
        r3 = L.contrast_test(lab3, rr[keep3], L.strata_of(sub3), {"W"}, {"U"}, 4999, rng)
        p5[h + "_W_vs_other_condition_fine_or_good_only"] = {k: r3[k] for k in ("difference", "n_high", "n_low", "p_one_sided")}
    p5["W_share_by_condition"] = w_table(uni, lambda t: t["condition"])
    p5["W_share_by_preservation"] = w_table(uni, lambda t: t["preservation"])
    p5["W_share_by_dimension_source"] = w_table(uni, lambda t: t["dims_unit"])
    p5["W_share_by_site"] = w_table(uni, lambda t: t["site"])
    p5["W_share_by_cisi_range"] = w_table(uni, lambda t: cisi_bin(t["cisi"]))
    sizes = [t["size"] for t in uni]
    qs = np.quantile(sizes, [0.25, 0.5, 0.75])
    p5["W_share_by_size_quartile"] = w_table(uni, lambda t: int(np.searchsorted(qs, t["size"])))
    p5["condition_by_size_quartile_share_fine_or_good"] = {
        str(q): round(float(np.mean([t["condition"] in ("Fine", "Good") for t in uni if int(np.searchsorted(qs, t["size"])) == q])), 3)
        for q in range(4)}
    # logistic: W ~ log size + condition fine/good + site MD (+ length), plain Newton iterations
    Xl = np.column_stack([np.ones(len(uni)), [math.log(t["size"]) for t in uni],
                          [t["condition"] in ("Fine", "Good") for t in uni],
                          [t["site"] == "Mohenjo-daro" for t in uni], [t["length"] for t in uni]]).astype(float)
    yl = np.array([t["symbol_full"] == "Bull1:W" for t in uni], float)
    beta = np.zeros(Xl.shape[1])
    for _ in range(50):
        p = 1 / (1 + np.exp(-Xl @ beta))
        W = p * (1 - p)
        H = Xl.T @ (Xl * W[:, None])
        beta = beta + np.linalg.solve(H, Xl.T @ (yl - p))
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    p5["logistic_W"] = {"terms": ["intercept", "ln size", "condition Fine/Good", "Mohenjo-daro", "length"],
                        "coef": [round(float(x), 3) for x in beta], "se": [round(float(x), 3) for x in se], "n": len(uni)}
    out["P5"] = p5
    write_json("shot-a-p3-p5.json", out)
    for k, v in p3.items():
        print("P3", k, v)
    for k, v in p5.items():
        print("P5", k, v)


if __name__ == "__main__":
    main()
