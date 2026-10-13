"""Shot A exploration on the discovery half. Writes discovery/*.json and the frozen
lexicon used by confirm.py. Never reads the confirmation half.

Steps (numbered as in EXPLORATION.md)
E1 population, E2 base size model, E3 closing and opening units against residual size,
E4 unit tables and grade scores, E5 sign-by-position scan, E6 cross-validation,
E7 split-half rehearsal (power_split.py), E8 identical legends, E9 site specificity,
E10 iconography and size, E11 discrete size grades, E12 other checks,
E13 the high closing set, E14 frozen lexicon.

Run: python explore.py   (about two minutes)
"""
from pathlib import Path
import collections
import json
import math
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from shots_common import load_half, ROOT, sha256  # noqa: E402
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402

OUT = HERE / "discovery"
RAW = ROOT / "data/raw/2026-10-12-conjecture-shots/shot-a-rank"
NPERM = 4999
K, MIN_N = 3.0, 3
HIGH_SET = ["001", "595", "679", "820"]
UNITS = ["last", "formula", "last2", "first", "first2"]
SCORE_BINS = [[3, 4], [5, 9], [10, 29], [30, 100000]]


def dump(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def dump_raw(name, obj):
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")


def w_length_tradeoff(pop, rng, ndraw=999):
    """Logistic regression of the unicorn W variant on ln size, text length and site class
    among unicorn square seals; length permuted within site class x size quintile."""
    from scipy.optimize import minimize
    U = [t for t in pop if t["type"] == "SEAL:S" and t["animal"] == "Bull1"]
    y = np.array([1.0 if t["symbol_full"] == "Bull1:W" else 0.0 for t in U])
    ls = np.array([math.log(t["size"]) for t in U])
    ln = np.array([t["length"] for t in U], float)
    X = np.column_stack([np.ones(len(U)), ls - ls.mean(), ln - ln.mean(), L.onehot([L.site6(t["site"]) for t in U])])

    def fit(Xm, start):
        f = lambda bb: np.sum(np.logaddexp(0, Xm @ bb) - y * (Xm @ bb))
        return minimize(f, start, method="BFGS").x

    b = fit(X, np.zeros(X.shape[1]))
    q = np.digitize(ls, np.quantile(ls, [0.2, 0.4, 0.6, 0.8]))
    sp = L.StratPerm([(L.site6(t["site"]), int(qq)) for t, qq in zip(U, q)])
    null = []
    for _ in range(ndraw):
        X2 = X.copy()
        X2[:, 2] = ln[sp.draw(rng)] - ln.mean()
        null.append(fit(X2, b)[2])
    null = np.array(null)
    return {"n": len(U), "w": int(y.sum()), "coef_log_size": float(b[1]), "coef_length": float(b[2]),
            "null_mean_coef_length": float(null.mean()), "p_more_negative": float((1 + (null <= b[2]).sum()) / (1 + ndraw)),
            "draws": ndraw}


def main():
    rows = load_half("discovery")
    table = seal_table(rows)
    C = collections.Counter

    # E1 population ------------------------------------------------------------
    seals_all = [t for t in table]
    pop_all = L.size_text_population(table)
    pop = L.representative(pop_all)
    res, r2 = L.residualize(pop)
    strata = L.strata_of(pop)
    dump_raw("discovery-population.json", [
        {k: t[k] for k in ("family", "record_id", "cisi", "component", "site", "type", "length", "signs",
                           "size", "log_area", "dims_unit", "animal", "symbol_full", "cult", "boss")}
        | {"residual": float(r)} for t, r in zip(pop, res)])
    dump("population.json", {
        "stage": "E1, discovery half",
        "seal_families": len(seals_all),
        "size_ok": sum(t["size_ok"] for t in seals_all),
        "text_ok": sum(t["text_ok"] for t in seals_all),
        "population_rule": "type SEAL:S or SEAL:R, both dimensions positive, preservation complete/slightly chipped/chipped, complete single-line text without unknown sign, length >= 2",
        "population_seals": len(pop_all),
        "population_components": len(pop),
        "by_type": dict(C(t["type"] for t in pop)),
        "by_site": dict(C(t["site"] for t in pop).most_common()),
        "by_length": {str(k): v for k, v in sorted(C(t["length"] for t in pop).items())},
        "by_dims_unit": dict(C(t["dims_unit"] for t in pop)),
        "square_size_mm": {"n": int(sum(t["type"] == "SEAL:S" for t in pop)),
                           "mean": float(np.mean([t["size"] for t in pop if t["type"] == "SEAL:S"])),
                           "quantiles_5_25_50_75_95": [float(x) for x in np.percentile([t["size"] for t in pop if t["type"] == "SEAL:S"], [5, 25, 50, 75, 95])]},
        "rectangular_size_mm": {"n": int(sum(t["type"] == "SEAL:R" for t in pop)),
                                "mean": float(np.mean([t["size"] for t in pop if t["type"] == "SEAL:R"]))},
    })

    # E2 base model ----------------------------------------------------------------
    y = np.array([t["log_area"] for t in pop])
    X = L.base_design(pop)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    names = ["intercept"]
    for lab, vals in (("type", [t["type"] for t in pop]), ("site", [L.site6(t["site"]) for t in pop]),
                      ("length", [L.len_class(t["length"]) for t in pop])):
        names += [f"{lab}={v}" for v in sorted(set(vals))[1:]]
    sq_by_len = {}
    for n in range(2, 11):
        s = [t["size"] for t in pop if t["type"] == "SEAL:S" and t["length"] == n]
        if s:
            sq_by_len[str(n)] = {"n": len(s), "mean_mm": float(np.mean(s)), "sd_mm": float(np.std(s))}
    dump("base-model.json", {
        "stage": "E2", "outcome": "ln(h mm) + ln(v mm)", "r2": r2,
        "residual_sd_log_area": float(res.std()),
        "coefficients": dict(zip(names, [float(x) for x in b])),
        "square_seal_size_by_length": sq_by_len,
        "movable_seals_in_strata": L.StratPerm(strata).movable,
    })

    # E3 unit tests ------------------------------------------------------------------
    rng = np.random.default_rng(3)
    e3 = {"stage": "E3", "permutations": NPERM, "tests": []}
    for u in UNITS:
        for m in (3, 5, 8):
            t = L.between_ratio_test([x[u] for x in pop], res, strata, m, NPERM, rng)
            t["unit"] = u
            e3["tests"].append(t)
    without_h = [x["last"] if x["last"] not in HIGH_SET else None for x in pop]
    e3["last_without_high_set"] = [L.between_ratio_test(without_h, res, strata, m, NPERM, rng) for m in (3, 5, 8)]
    formula_without_h = [x["formula"] if x["last"] not in HIGH_SET else None for x in pop]
    e3["formula_without_high_set"] = [L.between_ratio_test(formula_without_h, res, strata, m, NPERM, rng) for m in (3, 5, 8)]
    x740 = [x["formula"] if x["last"] == "740" else None for x in pop]
    e3["x740_formulas_only"] = [L.between_ratio_test(x740, res, strata, m, NPERM, rng) for m in (3, 5)]

    def ratio_difference(ua, ub, m):
        sp = L.StratPerm(strata)
        A = np.array([x[ua] for x in pop], dtype=object)
        B = np.array([x[ub] for x in pop], dtype=object)
        na, nb = [], []
        for _ in range(NPERM):
            idx = sp.draw(rng)
            na.append(L.between_ss(list(A[idx]), res, m))
            nb.append(L.between_ss(list(B[idx]), res, m))
        na, nb = np.array(na), np.array(nb)
        oa, ob = L.between_ss(list(A), res, m), L.between_ss(list(B), res, m)
        d = oa / na.mean() - ob / nb.mean()
        dn = na / na.mean() - nb / nb.mean()
        return {"closing_unit": ua, "opening_unit": ub, "min_n": m, "closing_ratio": float(oa / na.mean()),
                "opening_ratio": float(ob / nb.mean()), "difference": float(d),
                "p_one_sided": float((1 + (dn >= d).sum()) / (1 + NPERM)), "permutations": NPERM}

    e3["closing_minus_opening"] = [ratio_difference(a, b_, m) for a, b_ in (("last", "first"), ("formula", "first"), ("last2", "first2")) for m in (3, 5)]
    dump("unit-size-tests.json", e3)

    # E4 unit tables -------------------------------------------------------------------
    tables = {}
    for u in UNITS:
        g = L.unit_groups([x[u] for x in pop], res)
        tables[u] = sorted([{"unit": k, "n": len(v), "mean_residual": float(np.mean(v)),
                             "score_k3": float(sum(v) / (len(v) + K)),
                             "sites": dict(C(x["site"] for x in pop if x[u] == k).most_common(4))}
                            for k, v in g.items() if len(v) >= MIN_N], key=lambda d: d["score_k3"])
    dump("unit-tables.json", {"stage": "E4", "k": K, "min_n": MIN_N,
                              "note": "residual = ln area minus base model (type, site class, length class); score = sum of residuals / (n + k)",
                              "tables": tables})

    # E5 sign by position scan ------------------------------------------------------------
    sd = float(res.std())
    stats = collections.defaultdict(lambda: collections.defaultdict(list))
    for t, r in zip(pop, res):
        n = len(t["signs"])
        seen = set()
        for i, s in enumerate(t["signs"]):
            zone = "close" if i >= n - 2 else ("open" if i < 2 else "mid")
            if n < 4:
                zone = "close" if i == n - 1 else ("open" if i == 0 else "mid")
            for z in (zone, "any"):
                if (s, z) not in seen:
                    seen.add((s, z))
                    stats[s][z].append(float(r))
    scan = []
    for s, d in stats.items():
        v = d["any"]
        if len(v) >= 5:
            scan.append({"sign": s, "n_any": len(v), "mean_any": float(np.mean(v)),
                         "z_any": float(np.mean(v) / (sd / math.sqrt(len(v)))),
                         **{f"n_{z}": len(d[z]) for z in ("open", "mid", "close")},
                         **{f"mean_{z}": (float(np.mean(d[z])) if d[z] else None) for z in ("open", "mid", "close")}})
    scan.sort(key=lambda d: d["z_any"])
    dump("sign-zone-scan.json", {"stage": "E5", "zones": "texts of 4+ signs: open = first two, close = last two; shorter texts: first, last, middle",
                                 "signs_tested": len(scan), "rows": scan})

    # E6 cross-validation ----------------------------------------------------------------
    def cv(unit, k, reps=20, folds=5):
        lab = [x[unit] for x in pop]
        rs = []
        for rep in range(reps):
            r_ = np.random.default_rng(rep)
            f = r_.integers(0, folds, len(pop))
            pred = np.zeros(len(pop))
            for i in range(folds):
                tr = f != i
                sc = L.shrunk_scores([l for l, mm in zip(lab, tr) if mm], res[tr], k, 1)
                for j in np.where(~tr)[0]:
                    pred[j] = sc[lab[j]]["score"] if lab[j] in sc else 0.0
            rs.append(L.corr(pred, res))
        return {"unit": unit, "k": k, "mean_r": float(np.mean(rs)), "sd_r": float(np.std(rs))}

    dump("cross-validation.json", {"stage": "E6", "design": "5-fold by seal (one per component), 20 repetitions; residuals from the full discovery base model",
                                   "rows": [cv(u, k) for u in UNITS for k in (1, 3, 5, 10, 20)]})

    # E8 identical legends -------------------------------------------------------------------
    rng = np.random.default_rng(8)
    p2 = L.identical_legend_test(pop_all, NPERM, rng)
    groups, pairs = L.identical_pairs(pop_all)
    la = [t["log_area"] for t in pop_all]
    grp_rows, grp_raw = [], []
    for gi, g in enumerate(groups):
        grp_rows.append({"group": gi, "length": pop_all[g[0]]["length"], "last": pop_all[g[0]]["last"],
                         "seals": [{"cisi": pop_all[i]["cisi"], "site": pop_all[i]["site"], "type": pop_all[i]["type"],
                                    "size_mm": round(pop_all[i]["size"], 2), "animal": pop_all[i]["animal"]} for i in g]})
        grp_raw.append({"group": gi, "text": "-".join(pop_all[g[0]]["signs"]), "cisi": [pop_all[i]["cisi"] for i in g]})
    sub = {}
    for lab, sel in (("same_site", lambda a, b_: pop_all[a]["site"] == pop_all[b_]["site"]),
                     ("different_site", lambda a, b_: pop_all[a]["site"] != pop_all[b_]["site"])):
        pp = [(a, b_) for a, b_ in pairs if sel(a, b_)]
        sub[lab] = {"pairs": len(pp), "mean_abs_dlogarea": float(np.mean([abs(la[a] - la[b_]) for a, b_ in pp]))}
    sealing_rows = [{"cisi": r["source_cisi"], "type": r["object_type"], "site": r["site"],
                     "h_mm": r["metadata"].get("horizontal(mm)"), "v_mm": r["metadata"].get("vertical(mm)")}
                    for r in rows if r.get("source_cisi") in ("K-82", "M-1697", "M-712")]
    dump("identical-legends.json", {"stage": "E8 (prediction 2 statistic on the discovery half)", "test": p2,
                                    "subsets": sub, "groups": grp_rows,
                                    "sealing_K82_and_matching_seals": sealing_rows})
    dump_raw("identical-legends-texts.json", grp_raw)

    # E9 site specificity -------------------------------------------------------------------------
    rng = np.random.default_rng(9)
    p3pop = L.representative([t for t in table if t["type"] in L.SEAL_TYPES and t["text_ok"] and t["length"] >= 2
                              and t["site"] != "Unknown"])
    e9 = {"stage": "E9", "population": "SEAL:S/SEAL:R, clean text, length >= 2, named site, one per component",
          "n": len(p3pop), "shuffles": 1999, "tests": []}
    for a, b_ in (("first", "formula"), ("first", "last"), ("first2", "last2"), ("first2", "formula")):
        e9["tests"].append(L.site_specificity_test(p3pop, a, b_, 1999, rng))
    # alternative statistics tried first: same-site share of pairs sharing a unit, pooled over pairs
    # and averaged over units; shuffles of site within seal type
    sites = [t["site"] for t in p3pop]
    by_type = collections.defaultdict(list)
    for i, t in enumerate(p3pop):
        by_type[t["type"]].append(i)
    by_type = [np.array(v) for v in by_type.values()]
    site_arr = np.array(sites, dtype=object)
    shuffles = []
    for _ in range(1999):
        idx = np.arange(len(sites))
        for g_ in by_type:
            idx[g_] = g_[rng.permutation(len(g_))]
        shuffles.append(list(site_arr[idx]))

    def pair_shares(labels, sts):
        g_ = collections.defaultdict(list)
        for l_, s_ in zip(labels, sts):
            g_[l_].append(s_)
        same = tot = 0.0
        per = []
        for v in g_.values():
            if len(v) < 2:
                continue
            c_ = C(v)
            k_ = sum(x * (x - 1) / 2 for x in c_.values())
            n_ = len(v) * (len(v) - 1) / 2
            same += k_
            tot += n_
            per.append(k_ / n_)
        return same / tot, float(np.mean(per))

    alt = []
    for u in ("first", "last", "formula"):
        lab_ = [t[u] for t in p3pop]
        o = pair_shares(lab_, sites)
        nl = np.array([pair_shares(lab_, s_) for s_ in shuffles])
        alt.append({"unit": u, "pooled_pairs_ratio": float(o[0] / nl[:, 0].mean()),
                    "pooled_pairs_p": float((1 + (nl[:, 0] >= o[0]).sum()) / 2000),
                    "per_unit_ratio": float(o[1] / nl[:, 1].mean()),
                    "per_unit_p": float((1 + (nl[:, 1] >= o[1]).sum()) / 2000)})
    e9["same_site_pair_shares"] = alt
    dump("site-specificity.json", e9)

    # E10 iconography --------------------------------------------------------------------------------
    rng = np.random.default_rng(10)

    def cult_fn(c):
        return ("F" if c.endswith("F") else "N" if c.endswith("N") else None) if c and len(c) == 3 and c[0] in "SRH" else None

    def known(a):
        return a if a not in ("-", "None", "Unknown") else None

    e10 = {"stage": "E10", "note": "residuals from the E2 base model; labels permuted within E2 strata",
           "animal": L.between_ratio_test([known(t["animal"]) if t["type"] == "SEAL:S" else None for t in pop], res, strata, 5, NPERM, rng),
           "cult_F_vs_N": L.contrast_test([cult_fn(t["cult"]) for t in pop], res, strata, {"F"}, {"N"}, NPERM, rng),
           "unicorn_W_vs_other": L.ornament_test(pop, res, NPERM, rng),
           "boss": L.between_ratio_test([t["boss"] if t["boss"] != "-" else None for t in pop], res, strata, 5, NPERM, rng)}
    g = L.unit_groups([known(t["animal"]) if t["type"] == "SEAL:S" else None for t in pop], res)
    e10["animal_means"] = sorted([{"animal": k, "n": len(v), "mean_residual": float(np.mean(v))} for k, v in g.items() if len(v) >= 5], key=lambda d: d["mean_residual"])
    g = L.unit_groups([t["symbol_full"] if t["animal"] == "Bull1" else None for t in pop], res)
    e10["unicorn_variant_means"] = sorted([{"variant": k, "n": len(v), "mean_residual": float(np.mean(v))} for k, v in g.items() if len(v) >= 5], key=lambda d: d["mean_residual"])
    uni = [t for t in table if t["type"] == "SEAL:S" and t["animal"] == "Bull1" and t["size_ok"]]
    bins = [0, 18, 21, 24, 27, 30, 34, 40, 80]
    e10["w_rate_by_size_mm"] = [{"from": lo, "to": hi, "n": len(s), "w_share": float(np.mean([t["symbol_full"] == "Bull1:W" for t in s])) if s else None}
                                for lo, hi in zip(bins[:-1], bins[1:]) for s in [[t for t in uni if lo <= t["size"] < hi]]]
    mid = [t for t in uni if 24 <= t["size"] < 32]
    e10["w_rate_by_length_size_24_32mm"] = [{"length": n, "n": len(s), "w_share": float(np.mean([t["symbol_full"] == "Bull1:W" for t in s]))}
                                            for n in range(1, 10) for s in [[t for t in mid if t["length"] == n]] if s]
    e10["w_length_tradeoff_logistic"] = w_length_tradeoff(pop, np.random.default_rng(18))
    # closing-sign test after adding image codes to the base model
    icon = ["W" if t["symbol_full"] == "Bull1:W" else "U" if t["animal"] == "Bull1" else "none" if t["animal"] in ("None", "-") else "other" for t in pop]
    fn = [cult_fn(t["cult"]) or "?" for t in pop]
    Xi = np.column_stack([L.base_design(pop), L.onehot(icon), L.onehot(fn)])
    bi, *_ = np.linalg.lstsq(Xi, y, rcond=None)
    res_i = y - Xi @ bi
    e10["last_sign_after_image_adjustment"] = {
        "model": "base model plus unicorn-W / other unicorn / no animal / other animal, plus cult F / N / other",
        "r2": float(1 - res_i.var() / y.var()),
        "tests": [L.between_ratio_test([x["last"] for x in pop], res_i, strata, m, NPERM, rng) for m in (3, 5)],
        "high_set_contrast": L.contrast_test(["H" if x["last"] in HIGH_SET else "O" for x in pop], res_i, strata, {"H"}, {"O"}, NPERM, rng)}
    dump("iconography.json", e10)

    # E11 size grades -------------------------------------------------------------------------------------
    from sklearn.mixture import GaussianMixture
    e11 = {"stage": "E11"}
    r_side = (res / 2).reshape(-1, 1)
    e11["gmm_residual_log_side"] = [{"k": k, "bic": float(GaussianMixture(k, random_state=0, n_init=5).fit(r_side).bic(r_side))} for k in range(1, 5)]
    sq = np.log(np.array([t["size"] for t in pop if t["type"] == "SEAL:S"])).reshape(-1, 1)
    e11["gmm_raw_log_size_square"] = [{"k": k, "bic": float(GaussianMixture(k, random_state=0, n_init=5).fit(sq).bic(sq))} for k in range(1, 5)]
    e11["histogram_2mm_square"] = {}
    for unit in ("mm", "inch"):
        s = [t["size"] for t in pop if t["type"] == "SEAL:S" and t["dims_unit"] == unit]
        h, e = np.histogram(s, bins=np.arange(8, 72, 2))
        e11["histogram_2mm_square"][unit] = {"n": len(s), "counts": {str(int(a)): int(c) for a, c in zip(e[:-1], h) if c}}
    dump("size-grades.json", e11)

    # E12 other checks --------------------------------------------------------------------------------------
    e12 = {"stage": "E12"}
    val = {"001": 1, "002": 2, "003": 3, "004": 4, "005": 5, "006": 6, "007": 7, "031": 1, "032": 2, "033": 3, "034": 4}
    from scipy import stats as ss
    nums = [(max(val[s] for s in t["signs"] if s in val), r) for t, r in zip(pop, res) if any(s in val for s in t["signs"])]
    e12["numeral_max_value_vs_residual"] = {"n": len(nums), "spearman": float(ss.spearmanr([a for a, _ in nums], [b_ for _, b_ in nums])[0]),
                                            "p": float(ss.spearmanr([a for a, _ in nums], [b_ for _, b_ in nums])[1])}
    occ, first, fin = C(), C(), C()
    for r in rows:
        if r["complete_observed"] and not r["has_unknown_sign"] and r["single_line"] and r["length"] >= 2:
            s = r["signs_reading_rtl"]
            occ.update(s)
            first[s[0]] += 1
            fin[s[-1]] += 1
    fprop = [(fin[t["last"]] + 0.5) / (occ[t["last"]] + 1) for t in pop]
    iprop = np.array([(first[t["last"]] + 0.5) / (occ[t["last"]] + 1) for t in pop])
    e12["final_propensity_of_last_sign_vs_residual"] = {"spearman": float(ss.spearmanr(fprop, res)[0]), "p": float(ss.spearmanr(fprop, res)[1])}
    e12["initial_propensity_of_last_sign_vs_residual"] = {"spearman": float(ss.spearmanr(iprop, res)[0]), "p": float(ss.spearmanr(iprop, res)[1]),
                                                          "n_opener_like_last_sign_gt_0.3": int((iprop > 0.3).sum()),
                                                          "mean_residual_opener_like": float(res[iprop > 0.3].mean())}
    pos = {s: {"first": 0, "mid": 0, "last": 0} for s in HIGH_SET + ["740", "520", "390", "400"]}
    for r in rows:
        if r["complete_observed"] and not r["has_unknown_sign"] and r["single_line"] and r["length"] >= 2:
            s = r["signs_reading_rtl"]
            for i, x in enumerate(s):
                if x in pos:
                    pos[x]["first" if i == 0 else "last" if i == len(s) - 1 else "mid"] += 1
    e12["positions_all_object_types"] = pos
    by_area = collections.defaultdict(list)
    for t, r in zip(pop, res):
        if t["site"] == "Mohenjo-daro":
            by_area[(rows_by_rid[t["record_id"]]["metadata"].get("area-section") or "")[:2]].append(float(r))
    e12["mohenjo_daro_area_prefix"] = sorted([{"area": k, "n": len(v), "mean_residual": float(np.mean(v))} for k, v in by_area.items() if len(v) >= 5], key=lambda d: d["mean_residual"])
    dump("other-checks.json", e12)

    # E13 high closing set ---------------------------------------------------------------------------------
    rng = np.random.default_rng(13)
    H = set(HIGH_SET)
    lab = ["H" if x["last"] in H else "O" for x in pop]
    e13 = {"stage": "E13", "high_set": HIGH_SET,
           "selection": "post hoc: the four last signs with discovery n >= 3 and shrunken score >= 0.25 (E4 table 'last')",
           "contrast_high_minus_rest": L.contrast_test(lab, res, strata, {"H"}, {"O"}, NPERM, rng)}
    e13["drop_one"] = []
    for h in HIGH_SET:
        hh = H - {h}
        lab2 = ["H" if x["last"] in hh else ("X" if x["last"] == h else "O") for x in pop]
        t = L.contrast_test(lab2, res, strata, {"H"}, {"O"}, 1999, rng)
        e13["drop_one"].append({"dropped": h, "difference": t["difference"], "n_high": t["n_high"], "p_one_sided": t["p_one_sided"]})
    for name, sel in (("square_only", lambda x: x["type"] == "SEAL:S"), ("mohenjo_daro_only", lambda x: x["site"] == "Mohenjo-daro")):
        sp_ = [x for x in pop if sel(x)]
        r_, _ = L.residualize(sp_)
        e13[name] = L.contrast_test(["H" if x["last"] in H else "O" for x in sp_], r_, L.strata_of(sp_), {"H"}, {"O"}, 1999, rng)
    e13["seals"] = [{"cisi": x["cisi"], "site": x["site"], "type": x["type"], "length": x["length"], "last": x["last"],
                     "size_mm": round(x["size"], 2), "residual": round(float(r), 3), "symbol": x["symbol_full"]}
                    for x, r in zip(pop, res) if x["last"] in H]
    in_pop = {t["record_id"] for t in pop}
    e13["other_seal_faces_ending_in_high_sign"] = [
        {"cisi": r["source_cisi"], "record_id": r["record_id"], "site": r["site"], "type": r["object_type"],
         "preservation": r["metadata"].get("preservation"), "h_mm": r["metadata"].get("horizontal(mm)"),
         "v_mm": r["metadata"].get("vertical(mm)"), "length": r["length"], "last": r["signs_reading_rtl"][-1],
         "complete_observed": r["complete_observed"], "has_unknown_sign": r["has_unknown_sign"], "single_line": r["single_line"]}
        for r in rows if r["object_type"].startswith("SEAL") and r["length"] >= 2 and r["signs_reading_rtl"][-1] in H
        and r["record_id"] not in in_pop]
    e13["closing_pairs_of_high_seals"] = dict(C(r["signs_reading_rtl"][-2] + "-" + r["signs_reading_rtl"][-1] for r in rows
                                                if r["object_type"].startswith("SEAL") and r["length"] >= 2 and r["complete_observed"]
                                                and not r["has_unknown_sign"] and r["signs_reading_rtl"][-1] in H).most_common())
    e13["high_last_sign_on_other_object_types"] = dict(C(r["object_type"] for r in rows if not r["object_type"].startswith("SEAL")
                                                         and r["length"] >= 2 and r["complete_observed"] and not r["has_unknown_sign"]
                                                         and r["signs_reading_rtl"][-1] in H))
    full_texts = C("-".join(r["signs_reading_rtl"]) for r in rows if r["complete_observed"] and not r["has_unknown_sign"])
    high_faces = [r for r in rows if r["object_type"].startswith("SEAL") and r["length"] >= 2 and r["complete_observed"]
                  and not r["has_unknown_sign"] and r["signs_reading_rtl"][-1] in H]
    e13["legend_minus_last_sign_found_as_complete_text"] = {
        "seal_faces_checked": len(high_faces),
        "faces_whose_shortened_legend_occurs_elsewhere": sum(1 for r in high_faces if full_texts["-".join(r["signs_reading_rtl"][:-1])] > 0)}
    dump("high-closers.json", e13)

    # E14 frozen lexicon ---------------------------------------------------------------------------------------
    lex = {
        "stage": "E14, frozen input for confirm.py; built on the discovery half only",
        "base_model": "ln(h)+ln(v) ~ type + site class (Mohenjo-daro, Harappa, Dholavira, Lothal, Chanhu-daro, Kalibangan, other) + length class (2..8, 9+)",
        "k": K, "min_n": MIN_N, "score_bins": SCORE_BINS,
        "closing_scores_last": L.shrunk_scores([x["last"] for x in pop], res, K, MIN_N),
        "opening_scores_first": L.shrunk_scores([x["first"] for x in pop], res, K, MIN_N),
        "high_set": HIGH_SET,
    }
    dump("lexicon.json", lex)
    print("lexicon sha256", sha256(OUT / "lexicon.json"))


rows_by_rid = {}

if __name__ == "__main__":
    rows_by_rid.update({r["record_id"]: r for r in load_half("discovery")})
    main()
