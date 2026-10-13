"""Shot B confirmation: score the frozen gloss map on the confirmation half.

Written before predictions were frozen and NOT run on real data before freezing.
Usage:
  python confirm.py                 # real run; requires frozen PREDICTIONS.md and .sha256
  python confirm.py --synthetic     # dry run on the discovery half with randomly generated
                                    # withheld fields (no real withheld value is read)
  python confirm.py --synthetic --plant   # same, with planted effects (power check)

Implements PREDICTIONS.md exactly: per-sign effect sizes on withheld variables, five
component contrasts between gloss classes, a within-band rearrangement null of the
gloss records (10,000 permutations), the primary score S = z1 + z2 (P1 and P2, as set
at the coordinator's review), the individual tests of P3 to P5 and three secondary
checks. Outputs aggregate statistics only.
"""
import argparse
import collections
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

SHOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SHOT.parent))
import shots_common  # noqa: E402

SEED = 20261012
N_PERM = 10000
UNKNOWN = "000"
MISSING = {None, "", "-", "None", "?", "NA", "N/A", "n/a", "none", "unknown", "Unknown"}
UNICORN = "Bull1"
HARAPPA, MOHENJO = "Harappa", "Mohenjo-daro"
MIN_UNITS = 8          # eligibility for site, size, unicorn and period effects
MIN_UNITS_STOCK = 5    # eligibility for the Harappa/Mohenjo-daro stock effect
MIN_SITE_UNITS = 20    # sites with fewer seal units are pooled as "other"
MIN_PERIOD_UNITS = 10  # period values with fewer units are pooled as "other"
G_DRAWS = 2000         # multinomial draws for the bias of the G statistic
NUM_STROKES = {"001": 1, "002": 2, "003": 3, "004": 4, "005": 5, "013": 3, "016": 6, "017": 7,
               "031": 1, "032": 2, "033": 3, "034": 4, "035": 5}
SHEAF = {"390", "405", "407"}


def clean(v):
    if v is None:
        return None
    v = str(v).strip()
    return None if v in MISSING else v


def mm(v):
    v = clean(v)
    if v is None or not re.fullmatch(r"\d+(\.\d+)?", v):
        return None
    x = float(v)
    return x if x > 0 else None


def motif(r):
    m = clean(r.get("symbol"))
    if m is None:
        return None
    return clean(m.split(":")[0])


def group(t):
    t = t or ""
    for p in ("TAB:B", "TAB:I", "TAB:C"):
        if t.startswith(p):
            return p
    if t.startswith("SEAL"):
        return "SEAL"
    if t.startswith("POT") or t.startswith("POsT"):
        return "POT"
    if t.startswith("TAG"):
        return "TAG"
    return "OTHER"


def subtype(t):
    if t.startswith("SEAL:S"):
        return "S"
    if t.startswith("SEAL:R"):
        return "R"
    return "other"


def modal(xs):
    xs = [x for x in xs if x is not None]
    return collections.Counter(xs).most_common(1)[0][0] if xs else None


# --------------------------------------------------------------------------------------
# families and units
# --------------------------------------------------------------------------------------
def families(rows):
    fam = collections.defaultdict(list)
    for r in rows:
        fam[r["object_family_id"]].append(r)
    out = []
    for fid, rs in fam.items():
        signs = set()
        for r in rs:
            signs.update(s for s in r["signs_reading_rtl"] if s != UNKNOWN)
        md = [r.get("metadata", {}) for r in rs]
        area = None
        for m in md:
            h, v = mm(m.get("horizontal(mm)")), mm(m.get("vertical(mm)"))
            if h and v:
                area = h * v
                break
        out.append({
            "family": fid,
            "component": rs[0]["component"],
            "group": group(rs[0]["object_type"]),
            "subtype": subtype(rs[0]["object_type"]),
            "signs": signs,
            "last_sequences": [tuple(r["signs_reading_rtl"]) for r in rs],
            "length": max(r["length"] for r in rs),
            "site": modal([clean(r.get("site")) for r in rs]),
            "motif": modal([motif(r) for r in rs]),
            "period": modal([clean(m.get("period")) for m in md]),
            "material": modal([clean(m.get("material")) for m in md]),
            "area": area,
        })
    return out


def categorical_units(fams, key):
    """Units = (split component, value); sign set is the union over member families."""
    u = collections.defaultdict(set)
    for f in fams:
        v = f[key]
        if v is None:
            continue
        u[(f["component"], v)].update(f["signs"])
    return [(v, s) for (c, v), s in u.items()]


def size_units(fams):
    by = collections.defaultdict(list)
    for f in fams:
        if f["area"]:
            by[f["component"]].append(f)
    out = []
    for c, fs in by.items():
        signs = set().union(*(f["signs"] for f in fs))
        out.append({"logarea": float(np.mean([math.log2(f["area"]) for f in fs])),
                    "length": min(max(f["length"] for f in fs), 12),
                    "subtype": modal([f["subtype"] for f in fs]),
                    "signs": signs})
    return out


# --------------------------------------------------------------------------------------
# per-sign effect sizes
# --------------------------------------------------------------------------------------
def g_stat(obs, n, p):
    e = n * p
    m = obs > 0
    return 2.0 * float(np.sum(obs[m] * np.log(obs[m] / e[m])))


_g_cache = {}


def g_null_mean(n, p, rng_seed):
    key = (n, tuple(np.round(p, 12)))
    if key not in _g_cache:
        rng = np.random.default_rng(rng_seed + n)
        draws = rng.multinomial(n, p, size=G_DRAWS)
        _g_cache[key] = float(np.mean([g_stat(d.astype(float), n, p) for d in draws]))
    return _g_cache[key]


def concentration_effect(units, codes, min_cat, min_units):
    """Bias-corrected KL concentration (nats per unit) of each sign's category distribution."""
    cnt = collections.Counter(v for v, _ in units)
    cats = sorted(v for v, n in cnt.items() if n >= min_cat)
    def cat(v):
        return v if v in cats else "__other__"
    allcats = cats + (["__other__"] if any(v not in cats for v in cnt) else [])
    idx = {c: i for i, c in enumerate(allcats)}
    p = np.zeros(len(allcats))
    for v, n in cnt.items():
        p[idx[cat(v)]] += n
    p = p / p.sum()
    eff, ns = {}, {}
    for s in codes:
        obs = np.zeros(len(allcats))
        for v, ss in units:
            if s in ss:
                obs[idx[cat(v)]] += 1
        n = int(obs.sum())
        ns[s] = n
        if n >= min_units:
            eff[s] = (g_stat(obs, n, p) - g_null_mean(n, p, SEED)) / (2.0 * n)
    return eff, ns, {"categories": allcats, "background": dict(zip(allcats, map(float, p))), "units": len(units)}


def share_effect(units, codes, is_pos, min_units):
    vals = [1.0 if is_pos(v) else 0.0 for v, _ in units]
    p0 = float(np.mean(vals)) if vals else float("nan")
    eff, ns = {}, {}
    for s in codes:
        xs = [x for x, (_, ss) in zip(vals, units) if s in ss]
        ns[s] = len(xs)
        if len(xs) >= min_units:
            eff[s] = float(np.mean(xs)) - p0
    return eff, ns, {"units": len(units), "background_share": p0}


def size_effect(units, codes, min_units):
    if len(units) < 30:
        return {}, {}, {"units": len(units), "note": "too few units"}
    subs = sorted({u["subtype"] for u in units})
    X = []
    for u in units:
        row = ([1.0] + [1.0 if u["subtype"] == s else 0.0 for s in subs[1:]]
               + [1.0 if u["length"] == L else 0.0 for L in range(2, 13)])
        X.append(row)
    X = np.array(X)
    y = np.array([u["logarea"] for u in units])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    eff, ns = {}, {}
    for s in codes:
        rs = [r for r, u in zip(res, units) if s in u["signs"]]
        ns[s] = len(rs)
        if len(rs) >= min_units:
            eff[s] = float(np.mean(rs))
    return eff, ns, {"units": len(units), "residual_sd": float(np.std(res)), "coef": beta.tolist(), "subtypes": subs}


# --------------------------------------------------------------------------------------
# components and the rearrangement null
# --------------------------------------------------------------------------------------
def group_diff(eff_arr, elig, a_mask, b_mask):
    a = elig & a_mask
    b = elig & b_mask
    if not a.any() or not b.any():
        return float("nan")
    return float(eff_arr[a].mean() - eff_arr[b].mean())


def run(rows, out_path, label):
    gm = json.loads((SHOT / "GLOSS-MAP.json").read_text(encoding="utf-8"))
    recs = gm["signs"]
    codes = [x["code"] for x in recs]
    K = len(codes)
    cls = np.array([x["class"] for x in recs])
    official = np.array([x["official"] for x in recs])
    local = np.array([x["locality"] == "local" for x in recs])
    stock = np.array([x["stock"] for x in recs])
    cells = collections.defaultdict(list)
    for i, x in enumerate(recs):
        cells[(x["band"]["frequency"], x["band"]["position"])].append(i)
    cells = [np.array(v) for v in cells.values()]

    fams = families(rows)
    seals = [f for f in fams if f["group"] == "SEAL"]
    diag = {"faces": len(rows), "families": len(fams), "seal_families": len(seals)}

    site_units = categorical_units(seals, "site")
    e_site, n_site, d_site = concentration_effect(site_units, codes, MIN_SITE_UNITS, MIN_UNITS)
    s_units = size_units(seals)
    e_size, n_size, d_size = size_effect(s_units, codes, MIN_UNITS)
    square = [f for f in seals if f["subtype"] == "S"]
    ani_units = categorical_units(square, "motif")
    e_uni, n_uni, d_uni = share_effect(ani_units, codes, lambda v: v == UNICORN, MIN_UNITS)
    hm_units = [(v, s) for v, s in site_units if v in (HARAPPA, MOHENJO)]
    e_har, n_har, d_har = share_effect(hm_units, codes, lambda v: v == HARAPPA, MIN_UNITS_STOCK)
    per_units = categorical_units(seals, "period")
    per_cnt = collections.Counter(v for v, _ in per_units)
    period_ok = len(per_units) >= 100 and sum(1 for n in per_cnt.values() if n >= MIN_PERIOD_UNITS) >= 2
    if period_ok:
        e_per, n_per, d_per = concentration_effect(per_units, codes, MIN_PERIOD_UNITS, MIN_UNITS)
    else:
        e_per, n_per, d_per = {}, {}, {"units": len(per_units), "note": "not computable"}
    diag.update({"site": d_site, "size": d_size, "unicorn": d_uni, "harappa_vs_mohenjo": d_har, "period": d_per,
                 "unicorn_category_present": any(v == UNICORN for v, _ in ani_units),
                 "motif_categories": dict(collections.Counter(v for v, _ in ani_units).most_common(12))})

    def arr(e):
        a = np.full(K, np.nan)
        for i, s in enumerate(codes):
            if s in e:
                a[i] = e[s]
        return a, ~np.isnan(a)

    A = {k: arr(e) for k, e in (("site", e_site), ("size", e_size), ("unicorn", e_uni),
                                ("stock", e_har), ("period", e_per))}

    def components(perm):
        c, off, loc, stk = cls[perm], official[perm], local[perm], stock[perm]
        name = c == "NAME"
        t = {}
        t["P1_site_local_vs_pan"] = group_diff(*A["site"], loc, ~loc)
        t["P2_size_official_vs_other"] = group_diff(*A["size"], off, ~off)
        t["P3_unicorn_official_vs_name"] = group_diff(*A["unicorn"], off, name)
        t["P4_harappa_stockH_vs_stockMD"] = group_diff(*A["stock"], stk == "H", stk == "MD")
        t["P5_period_name_vs_pan"] = group_diff(*A["period"], name, ~loc) if period_ok else float("nan")
        return t

    ident = np.arange(K)
    actual = components(ident)
    rng = np.random.default_rng(SEED)

    def permute(fixed_numerals=False):
        perm = ident.copy()
        for cell in cells:
            idx = cell
            if fixed_numerals:
                idx = np.array([i for i in cell if cls[i] != "NUM"])
                if len(idx) < 2:
                    continue
            perm[idx] = rng.permutation(perm[idx])
        return perm

    def null(fixed_numerals=False):
        sims = collections.defaultdict(list)
        for _ in range(N_PERM):
            t = components(permute(fixed_numerals))
            for k, v in t.items():
                sims[k].append(v)
        return {k: np.array(v) for k, v in sims.items()}

    PRIMARY = ["P1_site_local_vs_pan", "P2_size_official_vs_other"]
    INDIVIDUAL = ["P3_unicorn_official_vs_name", "P4_harappa_stockH_vs_stockMD", "P5_period_name_vs_pan"]

    def standardise(actual, sims):
        """Per-component rearrangement statistics and standardised null draws."""
        comp, znull = {}, {}
        for k, a in actual.items():
            s = sims[k]
            ok = ~np.isnan(s)
            if math.isnan(a) or ok.sum() < N_PERM * 0.5 or np.std(s[ok]) == 0:
                comp[k] = {"actual": a, "computable": False}
                continue
            mu, sd = float(np.mean(s[ok])), float(np.std(s[ok]))
            p1 = float((1 + np.sum(s[ok] >= a)) / (1 + ok.sum()))
            comp[k] = {"actual": a, "computable": True, "null_mean": mu, "null_sd": sd,
                       "z": (a - mu) / sd, "p_one_sided": p1,
                       "null_95th": float(np.percentile(s[ok], 95)),
                       "rearrangements_with_empty_group": int((~ok).sum())}
            znull[k] = np.where(ok, (s - mu) / sd, 0.0)
        return comp, znull

    def combine(comp, znull, keys):
        keys = [k for k in keys if comp[k].get("computable")]
        if not keys:
            return {"computable": False, "components_used": []}
        S = float(sum(comp[k]["z"] for k in keys))
        Snull = np.sum(np.vstack([znull[k] for k in keys]), axis=0)
        p95 = float(np.percentile(Snull, 95))
        return {"components_used": keys, "S": S, "null_mean": float(Snull.mean()), "null_sd": float(Snull.std()),
                "null_95th": p95, "percentile_of_S": float(100.0 * np.mean(Snull < S)),
                "p_one_sided": float((1 + np.sum(Snull >= S)) / (1 + len(Snull))),
                "distance_sd": float((S - Snull.mean()) / Snull.std()),
                "pass": bool(S > p95)}

    sims = null(False)
    comp, znull = standardise(actual, sims)
    comb = combine(comp, znull, PRIMARY)
    for k in INDIVIDUAL:
        if comp[k].get("computable"):
            comp[k]["pass"] = bool(comp[k]["p_one_sided"] < 0.05)
    sims_fixed = null(True)
    comp_f, znull_f = standardise(actual, sims_fixed)
    comb_f = combine(comp_f, znull_f, PRIMARY)
    five = combine(comp, znull, PRIMARY + INDIVIDUAL)   # descriptive reference only, no pass rule
    five.pop("pass", None)
    # kill condition (evaluated only if the primary test fails)
    p1, p2 = comp[PRIMARY[0]], comp[PRIMARY[1]]
    both_below = bool(p1.get("computable") and p2.get("computable") and p1["z"] < 0 and p2["z"] < 0)
    if comb.get("computable", True) and comb.get("components_used"):
        dead = (not comb["pass"]) and (comb["distance_sd"] <= 0 or both_below)
    else:
        dead = None
    verdict = {"primary_pass": comb.get("pass"), "P1_and_P2_both_below_mean": both_below, "kill_condition_met": dead}

    # group sizes of the actual map for each component (eligible signs)
    name_ = cls == "NAME"
    groups = {
        "P1": {"local": int((A["site"][1] & local).sum()), "pan": int((A["site"][1] & ~local).sum())},
        "P2": {"official": int((A["size"][1] & official).sum()), "other": int((A["size"][1] & ~official).sum())},
        "P3": {"official": int((A["unicorn"][1] & official).sum()), "name": int((A["unicorn"][1] & name_).sum())},
        "P4": {"stock_H": int((A["stock"][1] & (stock == "H")).sum()), "stock_MD": int((A["stock"][1] & (stock == "MD")).sum())},
        "P5": {"name": int((A["period"][1] & name_).sum()), "pan": int((A["period"][1] & ~local).sum())},
    }

    # ----- secondary checks (reported individually, not in the combined score) ---------
    secondary = {}
    # S1 material: COMM signs less often on steatite, within object group
    mats = [f for f in fams if f["material"] is not None]
    steat_present = any("steat" in f["material"].lower() for f in mats)
    if steat_present and len(mats) >= 100:
        gmean = collections.defaultdict(list)
        for f in mats:
            gmean[f["group"]].append(1.0 if "steat" in f["material"].lower() else 0.0)
        gm_ = {g: float(np.mean(v)) for g, v in gmean.items()}
        cu = collections.defaultdict(list)
        for f in mats:
            cu[f["component"]].append(f)
        units = []
        for c, fs in cu.items():
            r = float(np.mean([(1.0 if "steat" in f["material"].lower() else 0.0) - gm_[f["group"]] for f in fs]))
            units.append((r, set().union(*(f["signs"] for f in fs))))
        e = {}
        for s in codes:
            xs = [r for r, ss in units if s in ss]
            if len(xs) >= MIN_UNITS:
                e[s] = float(np.mean(xs))
        ea, el = arr(e)
        def t_mat(perm):
            c = cls[perm]
            return group_diff(ea, el, c != "COMM", c == "COMM")
        a = t_mat(ident)
        s = np.array([t_mat(permute()) for _ in range(N_PERM)])
        s = s[~np.isnan(s)]
        secondary["S1_material_comm_less_steatite"] = {"actual": a, "null_mean": float(s.mean()), "null_sd": float(s.std()),
                                                        "p_one_sided": float((1 + np.sum(s >= a)) / (1 + len(s))),
                                                        "units": len(units),
                                                        "pass": bool((1 + np.sum(s >= a)) / (1 + len(s)) < 0.05)}
    else:
        secondary["S1_material_comm_less_steatite"] = {"computable": False, "families_with_material": len(mats)}
    # residuals for S2 and S3 (seal components with size)
    if d_size.get("coef"):
        subs = d_size["subtypes"]
        beta = np.array(d_size["coef"])
        by = collections.defaultdict(list)
        for f in seals:
            if f["area"]:
                by[f["component"]].append(f)
        resid = {}
        for c, fs in by.items():
            st = modal([f["subtype"] for f in fs])
            ln = min(max(f["length"] for f in fs), 12)
            x = np.array([1.0] + [1.0 if st == s_ else 0.0 for s_ in subs[1:]] +
                         [1.0 if ln == L else 0.0 for L in range(2, 13)])
            resid[c] = (float(np.mean([math.log2(f["area"]) for f in fs])) - float(x @ beta), fs)
        # S2: legends ending 740-400 larger than legends ending 740-090
        r400, r090 = [], []
        for c, (r, fs) in resid.items():
            ends_ = {seq[-2:] for f in fs for seq in f["last_sequences"] if len(seq) >= 2 and UNKNOWN not in seq}
            if ("740", "400") in ends_:
                r400.append(r)
            elif ("740", "090") in ends_:
                r090.append(r)
        if r400 and r090:
            from scipy.stats import mannwhitneyu
            u = mannwhitneyu(r400, r090, alternative="greater")
            secondary["S2_det_400_larger_than_090"] = {"n400": len(r400), "n090": len(r090),
                                                       "mean400": float(np.mean(r400)), "mean090": float(np.mean(r090)),
                                                       "p_one_sided": float(u.pvalue), "pass": bool(u.pvalue < 0.05)}
        else:
            secondary["S2_det_400_larger_than_090"] = {"computable": False, "n400": len(r400), "n090": len(r090)}
        # S3: grade numeral before a final sheaf sign rises with seal size
        pairs = []
        for c, (r, fs) in resid.items():
            for f in fs:
                for seq in f["last_sequences"]:
                    if len(seq) >= 2 and seq[-1] in SHEAF and seq[-2] in NUM_STROKES and seq[-2] != "002":
                        pairs.append((NUM_STROKES[seq[-2]], r))
                        break
                else:
                    continue
                break
        if len(pairs) >= 8:
            from scipy.stats import spearmanr
            rho = spearmanr([a for a, _ in pairs], [b for _, b in pairs])
            secondary["S3_grade_numeral_size"] = {"n": len(pairs), "rho": float(rho.statistic),
                                                  "p_two_sided": float(rho.pvalue),
                                                  "pass": bool(rho.statistic > 0 and rho.pvalue / 2 < 0.05)}
        else:
            secondary["S3_grade_numeral_size"] = {"computable": False, "n": len(pairs)}

    eligible = {k: int(A[k][1].sum()) for k in A}
    result = {"label": label, "seed": SEED, "permutations": N_PERM, "diagnostics": diag,
              "eligible_signs": eligible, "group_sizes_actual_map": groups,
              "primary": comb, "verdict": verdict, "components": comp,
              "sensitivity_numerals_fixed": {"components": comp_f, "primary": comb_f},
              "reference_five_component_sum": five,
              "secondary": secondary,
              "per_sign_effects": {k: {s: round(v, 5) for s, v in e.items()} for k, e in
                                   (("site", e_site), ("size", e_size), ("unicorn", e_uni),
                                    ("harappa", e_har), ("period", e_per))}}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1, default=float), encoding="utf-8")
    print(json.dumps({"primary": comb, "verdict": verdict,
                      "components": {k: {kk: v.get(kk) for kk in ("actual", "z", "p_one_sided", "pass")}
                                     for k, v in comp.items()},
                      "numerals_fixed": comb_f, "five_component_reference": five,
                      "eligible": eligible, "groups": groups, "secondary": secondary}, indent=1, default=float))
    return result


# --------------------------------------------------------------------------------------
# synthetic dry run: discovery faces with randomly generated withheld fields
# --------------------------------------------------------------------------------------
def synthetic_rows(plant=False):
    from common_b import load_discovery  # stripped discovery half
    rows = load_discovery()
    rng = np.random.default_rng(7)
    gm = json.loads((SHOT / "GLOSS-MAP.json").read_text(encoding="utf-8"))
    cls = {x["code"]: x for x in gm["signs"]}
    sites = ["Mohenjo-daro", "Harappa", "Lothal", "Kalibangan", "Chanhu-daro", "Dholavira", "Banawali", "Rare1", "Rare2"]
    sp = np.array([0.55, 0.22, 0.06, 0.05, 0.04, 0.04, 0.02, 0.01, 0.01])
    motifs = ["Bull1", "Bull2", "Elephant", "Rhinoceros", "Tiger", "Goat"]
    mp = np.array([0.75, 0.08, 0.06, 0.05, 0.04, 0.02])
    by_fam = {}
    out = []
    for r in rows:
        f = r["object_family_id"]
        if f not in by_fam:
            names = [s for s in r["signs_reading_rtl"] if cls.get(s, {}).get("class") == "NAME"]
            offs = [s for s in r["signs_reading_rtl"] if cls.get(s, {}).get("official")]
            p = sp.copy()
            if plant and names:
                k = int(names[0]) % 3      # each name sign leans to one of three sites
                p = p.copy(); p[k] += 0.6; p = p / p.sum()
            site = sites[rng.choice(len(sites), p=p)]
            base = 20.0 + 1.2 * r["length"] + rng.normal(0, 3)
            if plant and offs:
                base *= 1.25
            by_fam[f] = {"site": site, "symbol": motifs[rng.choice(len(motifs), p=mp)] + ":x",
                         "h": round(max(base, 5), 1), "v": round(max(base + rng.normal(0, 1), 5), 1),
                         "period": rng.choice(["IIIA", "IIIB", "IIIC", "-"], p=[0.2, 0.2, 0.1, 0.5]),
                         "material": rng.choice(["Steatite", "Terracotta", "Faience", "-"], p=[0.6, 0.2, 0.1, 0.1])}
        m = by_fam[f]
        r = dict(r)
        r["site"] = m["site"]
        r["symbol"] = m["symbol"]
        md = dict(r["metadata"])
        md.update({"horizontal(mm)": str(m["h"]), "vertical(mm)": str(m["v"]), "period": m["period"],
                   "material": m["material"]})
        r["metadata"] = md
        out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--plant", action="store_true")
    a = ap.parse_args()
    if a.synthetic:
        rows = synthetic_rows(plant=a.plant)
        name = "synthetic_dryrun_planted.json" if a.plant else "synthetic_dryrun_null.json"
        run(rows, SHOT / "discovery" / name, "synthetic " + ("planted" if a.plant else "null"))
    else:
        rows = shots_common.load_half("confirmation", SHOT)
        run(rows, SHOT / "confirmation" / "results.json", "confirmation")


if __name__ == "__main__":
    main()
