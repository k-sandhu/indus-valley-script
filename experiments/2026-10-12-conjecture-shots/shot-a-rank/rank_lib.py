"""Statistics shared by the Shot A exploration (discovery half) and confirm.py.

Every function takes rows already built by seal_table.seal_table, so the discovery and
confirmation stages use identical populations, covariates, statistics and nulls.

Conventions
- Size outcome: log_area = ln(horizontal mm) + ln(vertical mm).
- Base model (fitted separately on whichever half is analysed): intercept, seal type
  (SEAL:S or SEAL:R), site in six named classes plus 'other', and text length as a
  factor (2, 3, ..., 8, 9 or more). Residuals from this model are the 'residual size'.
- Strata for permutation: (type, site class, length class). Labels move only within a
  stratum, so every null keeps the type, site and length composition of each label.
- One seal per component for every analysis except identical legends: the face of the
  family with the smallest identifier (shorter identifier first, as in shots_common).
  Identical complete texts of two or more signs on seals always share a component, so
  this keeps duplicated legends together and counts each legend once.
"""
import collections
import itertools
import math

import numpy as np

BIG_SITES = ("Mohenjo-daro", "Harappa", "Dholavira", "Lothal", "Chanhu-daro", "Kalibangan")
SEAL_TYPES = ("SEAL:S", "SEAL:R")
LEN_CAP = 9


def site6(s):
    return s if s in BIG_SITES else "other"


def len_class(n):
    return min(n, LEN_CAP)


def representative(rows):
    """One row per component: smallest family identifier (shorter first)."""
    best = {}
    for t in rows:
        k = t["component"]
        key = (len(t["family"]), t["family"])
        if k not in best or key < (len(best[k]["family"]), best[k]["family"]):
            best[k] = t
    return [best[k] for k in sorted(best, key=lambda c: (len(c), c))]


def size_text_population(table):
    """Seals of type S or R with usable dimensions, a clean text and at least two signs."""
    return [t for t in table if t["type"] in SEAL_TYPES and t["size_ok"] and t["text_ok"] and t["length"] >= 2]


def onehot(vals):
    levels = sorted(set(vals))
    if len(levels) < 2:
        return np.zeros((len(vals), 0))
    return np.column_stack([[1.0 if v == L else 0.0 for v in vals] for L in levels[1:]])


def base_design(rows):
    return np.column_stack([
        np.ones(len(rows)),
        onehot([t["type"] for t in rows]),
        onehot([site6(t["site"]) for t in rows]),
        onehot([len_class(t["length"]) for t in rows]),
    ])


def residualize(rows):
    y = np.array([t["log_area"] for t in rows])
    X = base_design(rows)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    return res, float(1 - res.var() / y.var())


def strata_of(rows):
    return [(t["type"], site6(t["site"]), len_class(t["length"])) for t in rows]


class StratPerm:
    """Permutation of positions within strata."""

    def __init__(self, strata):
        groups = collections.defaultdict(list)
        for i, s in enumerate(strata):
            groups[s].append(i)
        self.groups = [np.array(v) for v in groups.values() if len(v) > 1]
        self.n = len(strata)
        self.movable = int(sum(len(g) for g in self.groups))

    def draw(self, rng):
        idx = np.arange(self.n)
        for g in self.groups:
            idx[g] = g[rng.permutation(len(g))]
        return idx


# ---------------------------------------------------------------- unit scores (P1, P4)

def unit_groups(labels, res):
    g = collections.defaultdict(list)
    for l, r in zip(labels, res):
        if l is not None:
            g[l].append(float(r))
    return g


def shrunk_scores(labels, res, k=3.0, min_n=3):
    """Empirical-Bayes style grade score: sum of residuals / (n + k), units with n >= min_n."""
    g = unit_groups(labels, res)
    return {u: {"n": len(v), "mean_residual": float(np.mean(v)), "score": float(sum(v) / (len(v) + k))}
            for u, v in g.items() if len(v) >= min_n}


def between_ss(labels, res, min_n):
    g = unit_groups(labels, res)
    return float(sum(len(v) * np.mean(v) ** 2 for v in g.values() if len(v) >= min_n))


def between_ratio_test(labels, res, strata, min_n, nperm, rng):
    """Between-unit sum of squares of residual size against labels permuted within strata."""
    sp = StratPerm(strata)
    lab = np.array(labels, dtype=object)
    obs = between_ss(labels, res, min_n)
    null = np.array([between_ss(list(lab[sp.draw(rng)]), res, min_n) for _ in range(nperm)])
    g = unit_groups(labels, res)
    return {
        "statistic": "between-unit sum of squares of residual log area, units with n >= min_n",
        "min_n": min_n,
        "units": int(sum(1 for v in g.values() if len(v) >= min_n)),
        "seals_in_units": int(sum(len(v) for v in g.values() if len(v) >= min_n)),
        "observed": obs,
        "null_mean": float(null.mean()),
        "ratio_to_null_mean": float(obs / null.mean()) if null.mean() > 0 else None,
        "p_one_sided": float((1 + (null >= obs).sum()) / (1 + nperm)),
        "permutations": nperm,
        "movable_seals": sp.movable,
    }


def score_vector(labels, scores):
    return np.array([scores[l]["score"] if l in scores else np.nan for l in labels])


def corr(a, b):
    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def score_correlation_test(labels, res, strata, scores, nperm, rng):
    """Pearson r between frozen unit scores and residual size, over seals whose unit is scored.

    Null: unit labels permuted within strata over the whole population (unscored seals
    take part in the permutation), so each draw re-selects which seals carry scored units.
    """
    sp = StratPerm(strata)
    lab = np.array(labels, dtype=object)

    def stat(lv):
        s = score_vector(lv, scores)
        m = ~np.isnan(s)
        return corr(s[m], res[m]), int(m.sum())

    obs, n = stat(list(lab))
    null = np.array([stat(list(lab[sp.draw(rng)]))[0] for _ in range(nperm)])
    return {"r": obs, "n_scored": n, "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "p_one_sided": float((1 + (null >= obs).sum()) / (1 + nperm)), "permutations": nperm}


def rearrangement_test(labels, res, scores, bins, nreps, rng):
    """Calibration: r of the frozen scores against r when the same scores are rearranged
    among scored units of similar discovery frequency (bins of discovery n)."""
    units = sorted(scores)

    def bin_of(n):
        for i, (lo, hi) in enumerate(bins):
            if lo <= n <= hi:
                return i
        return len(bins)

    by_bin = collections.defaultdict(list)
    for u in units:
        by_bin[bin_of(scores[u]["n"])].append(u)
    s = score_vector(labels, scores)
    m = ~np.isnan(s)
    obs = corr(s[m], res[m])
    lab = [l for l, keep in zip(labels, m) if keep]
    rr = res[m]
    null = []
    for _ in range(nreps):
        new = {}
        for b, us in by_bin.items():
            perm = rng.permutation(len(us))
            for u, j in zip(us, perm):
                new[u] = scores[us[j]]["score"]
        null.append(corr(np.array([new[l] for l in lab]), rr))
    null = np.array(null)
    return {"r": obs, "rearrangement_mean": float(null.mean()), "rearrangement_sd": float(null.std()),
            "z": float((obs - null.mean()) / null.std()) if null.std() > 0 else None,
            "p_one_sided": float((1 + (null >= obs).sum()) / (1 + nreps)), "rearrangements": nreps,
            "bins": bins, "units_per_bin": {str(bins[b]) if b < len(bins) else "other": len(v) for b, v in by_bin.items()}}


def paired_score_difference_test(labels_a, labels_b, res, strata, scores_a, scores_b, nperm, rng):
    """r(closing scores) minus r(opening scores); texts move as wholes within strata."""
    sp = StratPerm(strata)
    la = np.array(labels_a, dtype=object)
    lb = np.array(labels_b, dtype=object)

    def r_of(lv, scores):
        s = score_vector(lv, scores)
        m = ~np.isnan(s)
        return corr(s[m], res[m])

    obs_a, obs_b = r_of(list(la), scores_a), r_of(list(lb), scores_b)
    d = obs_a - obs_b
    null = []
    for _ in range(nperm):
        idx = sp.draw(rng)
        null.append(r_of(list(la[idx]), scores_a) - r_of(list(lb[idx]), scores_b))
    null = np.array(null)
    return {"r_closing": obs_a, "r_opening": obs_b, "difference": d, "null_mean": float(null.mean()),
            "null_sd": float(null.std()), "p_one_sided": float((1 + (null >= d).sum()) / (1 + nperm)),
            "permutations": nperm}


def contrast_test(labels, res, strata, high, low, nperm, rng):
    """Mean residual of seals whose unit is in `high` minus mean of those in `low`."""
    sp = StratPerm(strata)
    lab = np.array(labels, dtype=object)

    def stat(lv):
        h = np.array([l in high for l in lv])
        lo = np.array([l in low for l in lv])
        if h.sum() == 0 or lo.sum() == 0:
            return np.nan, int(h.sum()), int(lo.sum())
        return float(res[h].mean() - res[lo].mean()), int(h.sum()), int(lo.sum())

    obs, nh, nl = stat(list(lab))
    if nh == 0 or nl == 0:
        return {"difference": None, "n_high": nh, "n_low": nl, "p_one_sided": None, "permutations": 0,
                "note": "no seals in one of the two groups"}
    null = np.array([stat(list(lab[sp.draw(rng)]))[0] for _ in range(nperm)])
    null = null[~np.isnan(null)]
    h = np.array([l in high for l in labels])
    lo = np.array([l in low for l in labels])
    other = ~(h | lo)
    return {"difference": obs, "n_high": nh, "n_low": nl,
            "mean_high": float(res[h].mean()) if nh else None,
            "mean_low": float(res[lo].mean()) if nl else None,
            "mean_other": float(res[other].mean()) if other.sum() else None,
            "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "p_one_sided": float((1 + (null >= obs).sum()) / (1 + len(null))), "permutations": int(len(null))}


# ---------------------------------------------------------------- identical legends (P2)

def identical_pairs(rows):
    by = collections.defaultdict(list)
    for i, t in enumerate(rows):
        by["-".join(t["signs"])].append(i)
    groups = [v for v in by.values() if len(v) >= 2]
    pairs = [(a, b) for g in groups for a, b in itertools.combinations(g, 2)]
    return groups, pairs


def identical_legend_test(rows, ndraw, rng):
    """Mean |difference in log area| within identical-text pairs, against pairs in which one
    member (chosen at random) is replaced by a seal of the same type, length and site class
    from a different component."""
    groups, pairs = identical_pairs(rows)
    la = np.array([t["log_area"] for t in rows])
    key = lambda t: (t["type"], t["length"], site6(t["site"]))
    pool = collections.defaultdict(list)
    for i, t in enumerate(rows):
        pool[key(t)].append(i)
    cands = {}
    usable = []
    for a, b in pairs:
        ca = [j for j in pool[key(rows[a])] if rows[j]["component"] != rows[b]["component"]]
        cb = [j for j in pool[key(rows[b])] if rows[j]["component"] != rows[a]["component"]]
        if ca and cb:
            cands[(a, b)] = (np.array(ca), np.array(cb))
            usable.append((a, b))
    obs = float(np.mean([abs(la[a] - la[b]) for a, b in usable])) if usable else None
    null = []
    for _ in range(ndraw):
        d = []
        for a, b in usable:
            ca, cb = cands[(a, b)]
            if rng.random() < 0.5:
                d.append(abs(la[a] - la[cb[rng.integers(len(cb))]]))
            else:
                d.append(abs(la[b] - la[ca[rng.integers(len(ca))]]))
        null.append(np.mean(d))
    null = np.array(null)
    return {"groups": len(groups), "seals_in_groups": int(sum(len(g) for g in groups)),
            "pairs": len(pairs), "usable_pairs": len(usable),
            "observed_mean_abs_dlogarea": obs, "null_mean": float(null.mean()) if len(null) else None,
            "ratio": float(obs / null.mean()) if len(null) and obs is not None else None,
            "p_one_sided_smaller": float((1 + (null <= obs).sum()) / (1 + ndraw)) if len(null) else None,
            "draws": ndraw}


# ---------------------------------------------------------------- site specificity (P3)

def mutual_information(labels, sites):
    n = len(labels)
    j = collections.Counter(zip(labels, sites))
    a = collections.Counter(labels)
    b = collections.Counter(sites)
    return float(sum(c / n * math.log(c * n / (a[x] * b[y])) for (x, y), c in j.items()))


def entropy(labels):
    c = collections.Counter(labels)
    n = len(labels)
    return float(-sum(v / n * math.log(v / n) for v in c.values()))


def site_specificity_test(rows, unit_a, unit_b, nperm, rng):
    """z(MI(unit_a; site)) - z(MI(unit_b; site)), z taken against site labels shuffled
    within seal type. The same shuffles serve both units, so each z is measured against
    the null distribution generated by that unit's own frequency spectrum (entropy)."""
    sites = [t["site"] for t in rows]
    types = [t["type"] for t in rows]
    A = [t[unit_a] for t in rows]
    Bv = [t[unit_b] for t in rows]
    groups = collections.defaultdict(list)
    for i, ty in enumerate(types):
        groups[ty].append(i)
    groups = [np.array(v) for v in groups.values()]
    sites_arr = np.array(sites, dtype=object)
    oa, ob = mutual_information(A, sites), mutual_information(Bv, sites)
    na, nb = [], []
    for _ in range(nperm):
        idx = np.arange(len(sites))
        for g in groups:
            idx[g] = g[rng.permutation(len(g))]
        s = list(sites_arr[idx])
        na.append(mutual_information(A, s))
        nb.append(mutual_information(Bv, s))
    na, nb = np.array(na), np.array(nb)
    za, zb = (oa - na.mean()) / na.std(), (ob - nb.mean()) / nb.std()
    D = za - zb
    Dn = (na - na.mean()) / na.std() - (nb - nb.mean()) / nb.std()
    return {"n": len(rows), "unit_a": unit_a, "unit_b": unit_b,
            "distinct_a": len(set(A)), "distinct_b": len(set(Bv)),
            "entropy_a": entropy(A), "entropy_b": entropy(Bv),
            "mi_a": oa, "mi_a_null_mean": float(na.mean()), "z_a": float(za),
            "p_a": float((1 + (na >= oa).sum()) / (1 + nperm)),
            "mi_b": ob, "mi_b_null_mean": float(nb.mean()), "z_b": float(zb),
            "p_b": float((1 + (nb >= ob).sum()) / (1 + nperm)),
            "z_difference": float(D), "p_one_sided": float((1 + (Dn >= D).sum()) / (1 + nperm)),
            "permutations": nperm}


# ---------------------------------------------------------------- unicorn ornament (P5)

def ornament_test(rows, res, nperm, rng):
    """Among unicorn seals (animal code Bull1) of the population: residual size of the
    catalogue variant Bull1:W minus that of the other Bull1 variants. The W/other label
    moves within strata among unicorn seals only; residuals come from the base model
    fitted on the whole population."""
    keep = [i for i, t in enumerate(rows) if t["animal"] == "Bull1"]
    sub = [rows[i] for i in keep]
    lab = ["W" if t.get("symbol_full") == "Bull1:W" else "U" for t in sub]
    out = contrast_test(lab, res[keep], strata_of(sub), {"W"}, {"U"}, nperm, rng)
    out["unicorn_seals"] = len(sub)
    return out
