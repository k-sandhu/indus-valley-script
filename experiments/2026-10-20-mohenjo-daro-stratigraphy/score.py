"""Score predictions P1-P9 of the Mohenjo-daro stratigraphy shot on one population.

The same function runs the rehearsal on Mackay's DK-G seals, the planted-effect power
simulation and, frozen by hash, the single confirmation read of Marshall's areas.
Parameters that come from the discovery population (closing stock, closing formulae,
non-final sign heights) are read from a frozen JSON file.
"""
from collections import Counter, defaultdict
import json
import math

import numpy as np

import strat_stats as S

MARGIN = 0.20          # equivalence margin for top-third minus bottom-third shares
BOTTOM_SHARE = 0.60    # minimum stock share among bottom-third legends
MIN_CATEGORY = 5       # sign categories with fewer units are pooled as OTHER
INFLUENCE_UNITS = 10   # units re-tested one at a time for the influence rule
INFLUENCE_P = 0.10     # p-value each single-unit deletion must keep
DRIFT = ("P4", "P5", "P6", "P7", "P8")


# ---------------------------------------------------------------- strata

def assign_strata(objects, min_cell=15, min_stratum=5):
    """Stratum for depth ranking. Marshall measured depth below the local modern surface,
    so a stratum is an excavation section (Marshall's area letter with the export's
    section) when that cell has at least min_cell seals with a depth; other cells of the
    area are pooled under the area letter. Strata with fewer than min_stratum seals are
    dropped. Mackay's levels share the DK datum, so his DK-area seals form one stratum."""
    cells = Counter((o["metadata"]["strat_area"], o["metadata"]["strat_section"]) for o in objects)
    keep = []
    for o in objects:
        m = o["metadata"]
        cell = (m["strat_area"], m["strat_section"])
        if m["strat_source"] == "mackay1938":
            m["strat_stratum"] = m["strat_area"]
        else:
            m["strat_stratum"] = f"{cell[0]}/{cell[1]}" if cells[cell] >= min_cell else f"{cell[0]}/rest"
        keep.append(o)
    sizes = Counter(o["metadata"]["strat_stratum"] for o in keep)
    return [o for o in keep if sizes[o["metadata"]["strat_stratum"]] >= min_stratum], dict(sorted(sizes.items()))


def prepare(rows, areas=None):
    objects = S.seal_objects(rows, areas)
    objects, sizes = assign_strata(objects)
    S.add_height_rank(objects, stratum_key="strat_stratum")
    return objects, sizes


# ---------------------------------------------------------------- helpers

def bootstrap_share_difference(rows, indicator, draws, seed):
    """90% percentile interval of top-third minus bottom-third share, resampling units
    with replacement within strata."""
    rng = np.random.default_rng(seed)
    ind = np.asarray(indicator, dtype=float)
    u = np.array([r["u"] for r in rows])
    index = S.strata_index(rows)
    stat = S.share_difference_factory(ind)
    observed = stat(u)
    values = np.empty(draws)
    for b in range(draws):
        pick = np.concatenate([rng.choice(idx, len(idx), replace=True) for idx in index])
        low, high = u[pick] < 1 / 3, u[pick] >= 2 / 3
        values[b] = ind[pick][high].mean() - ind[pick][low].mean() if low.any() and high.any() else 0.0
    lo, hi = np.quantile(values, [0.05, 0.95])
    return {"observed": float(observed), "interval90": [float(lo), float(hi)], "draws": draws, "seed": seed,
            "units": len(rows), "bottom_units": int(np.sum(u < 1 / 3)), "top_units": int(np.sum(u >= 2 / 3)),
            "bottom_share": float(ind[u < 1 / 3].mean()) if np.any(u < 1 / 3) else None,
            "top_share": float(ind[u >= 2 / 3].mean()) if np.any(u >= 2 / 3) else None}


def equivalence_outcome(result, margin=MARGIN):
    lo, hi = result["interval90"]
    if -margin < lo and hi < margin:
        return "pass"
    if abs(result["observed"]) >= margin:
        return "fail"
    return "inconclusive"


def influence_permutation(rows, factory, draws, seed, alternative="greater"):
    """Drop single units: the INFLUENCE_UNITS whose deletion lowers the observed statistic
    most are re-tested with a full permutation each; also drop each stratum in turn."""
    u = np.array([r["u"] for r in rows])
    base = factory(rows)(u)
    drops = []
    for i in range(len(rows)):
        sub = rows[:i] + rows[i + 1:]
        drops.append((factory(sub)(np.array([r["u"] for r in sub])) - base, i))
    sign = 1 if alternative == "greater" else -1
    worst = [i for _, i in sorted(drops, key=lambda d: sign * d[0])[:INFLUENCE_UNITS]]
    single = []
    for k, i in enumerate(worst):
        sub = rows[:i] + rows[i + 1:]
        res = S.permutation_test(sub, factory(sub), draws, seed + 1000 + k, alternative)
        single.append({"families": rows[i]["families"], "stratum": rows[i]["stratum"], "p": res["p"],
                       "observed": res["observed"]})
    strata = []
    for k, name in enumerate(sorted({r["stratum"] for r in rows})):
        sub = [r for r in rows if r["stratum"] != name]
        res = S.permutation_test(sub, factory(sub), draws, seed + 2000 + k, alternative)
        strata.append({"dropped": name, "z": res["z"], "p": res["p"]})
    max_p = max(s["p"] for s in single) if single else None
    return {"single_unit": single, "max_single_p": max_p,
            "single_rule_met": max_p is not None and max_p <= INFLUENCE_P,
            "leave_stratum_out": strata,
            "direction_kept_every_stratum": all((s["z"] or 0) > 0 for s in strata)}


def influence_equivalence(rows, indicator, draws, seed):
    ind = np.asarray(indicator, dtype=float)
    u = np.array([r["u"] for r in rows])
    base = S.share_difference_factory(ind)(u)
    shifts = []
    for i in range(len(rows)):
        keep = np.ones(len(rows), bool)
        keep[i] = False
        shifts.append((abs(S.share_difference_factory(ind[keep])(u[keep]) - base), i))
    worst = [i for _, i in sorted(shifts, reverse=True)[:INFLUENCE_UNITS]]
    out = []
    for k, i in enumerate(worst):
        sub = rows[:i] + rows[i + 1:]
        sub_ind = np.delete(ind, i)
        res = bootstrap_share_difference(sub, sub_ind, draws, seed + 3000 + k)
        out.append({"families": rows[i]["families"], "interval90": res["interval90"],
                    "outcome": equivalence_outcome(res)})
    return {"single_unit": out, "rule_met": all(x["outcome"] == "pass" for x in out)}


def holm(pvalues):
    names = sorted(pvalues, key=lambda k: pvalues[k])
    m = len(names)
    adjusted, running = {}, 0.0
    for j, k in enumerate(names):
        running = max(running, min(1.0, (m - j) * pvalues[k]))
        adjusted[k] = running
    return adjusted


# ---------------------------------------------------------------- the predictions

def score_predictions(objects, frozen, draws=9999, boot=9999, seed=20261020, influence=True, only=None):
    """only: optional set of prediction ids to compute (power simulations); the frozen
    confirmation run computes all of them."""
    if only is not None:
        return score_subset(objects, frozen, draws, boot, seed, only)
    stock = set(frozen["closing_stock"])
    formulae = set(frozen["closing_formulae"])
    scores = frozen["nonfinal_scores"]
    out = {}

    # P1, P2: closing stock fixed through the sequence and present at its bottom
    close = S.units(objects, "closing")
    ind = [r["value"] in stock for r in close]
    p1 = bootstrap_share_difference(close, ind, boot, seed + 1)
    p1["outcome"] = equivalence_outcome(p1)
    if influence and p1["outcome"] == "pass":
        p1["influence"] = influence_equivalence(close, ind, min(boot, 1999), seed + 1)
        if not p1["influence"]["rule_met"]:
            p1["outcome"] = "inconclusive"
    out["P1"] = p1

    u = np.array([r["u"] for r in close])
    bottom = np.array(ind, dtype=float)[u < 1 / 3]
    share = float(bottom.mean()) if len(bottom) else None
    worst_drop = float((bottom.sum() - 1) / (len(bottom) - 1)) if len(bottom) > 1 and bottom.sum() > 0 else None
    out["P2"] = {"bottom_units": int(len(bottom)), "bottom_share": share, "share_after_worst_single_deletion": worst_drop,
                 "outcome": "pass" if share is not None and share >= BOTTOM_SHARE and (worst_drop or 0) >= BOTTOM_SHARE else "fail"}

    # P3: two-sign closing formulae fixed through the sequence
    pairs = S.units(objects, "closing_pair")
    find = [r["value"] in formulae for r in pairs]
    p3 = bootstrap_share_difference(pairs, find, boot, seed + 3)
    p3["outcome"] = equivalence_outcome(p3)
    if influence and p3["outcome"] == "pass":
        p3["influence"] = influence_equivalence(pairs, find, min(boot, 1999), seed + 3)
        if not p3["influence"]["rule_met"]:
            p3["outcome"] = "inconclusive"
    out["P3"] = p3

    # P4: opening signs sit at different heights
    opening = S.units(objects, "opening")

    def slot_factory(rows):
        codes, _ = S.category_codes(rows, MIN_CATEGORY)
        return S.between_ratio_factory(codes)
    p4 = S.permutation_test(opening, slot_factory(opening), draws, seed + 4)
    p4["categories"] = len(S.category_codes(opening, MIN_CATEGORY)[1])
    out["P4"] = p4

    # P5: opening drift exceeds closing drift on the same legends
    open_rows = [r for r in opening if r["text"]["closing"] is not None]
    close_rows = [dict(r, value=r["text"]["closing"]) for r in open_rows]
    out["P5"] = contrast_test(open_rows, close_rows, slot_factory, draws, seed + 5)

    # P6: variant choice within sign classes changes with height
    classes = S.load_variant_classes()
    legends = S.units(objects, "length", min_length=1)
    variants = S.variant_tokens([{"stratum": r["stratum"], "u": r["u"], "object_family_id": r["families"][0],
                                  "text": {"signs": r["signs"]}} for r in S.all_legends(objects)], classes)

    def variant_factory(rows):
        return S.variant_statistic_factory(rows)[0]
    p6 = S.permutation_test(variants, variant_factory(variants), draws, seed + 6)
    p6["classes"] = S.variant_statistic_factory(variants)[1]
    out["P6"] = p6

    # P7: legends grow longer upward
    def length_factory(rows):
        return S.stratified_spearman_factory([r["value"] for r in rows], rows)
    out["P7"] = S.permutation_test(legends, length_factory(legends), draws, seed + 7)

    # P8: heights of non-final signs learned in DK-G predict height in other areas
    scored = []
    for r in S.units(objects, "length", min_length=2):
        values = [scores[s] for s in r["signs"][:-1] if s in scores]
        if values:
            scored.append(dict(r, value=float(np.mean(values))))

    def transfer_factory(rows):
        return S.pearson_factory([r["value"] for r in rows])
    out["P8"] = S.permutation_test(scored, transfer_factory(scored), draws, seed + 8) if len(scored) > 2 else {"p": 1.0, "units": len(scored)}

    # P9 (auxiliary): rectangular seals rise through the sequence
    seals = [{"stratum": o["stratum"], "u": o["u"], "value": o["object_type"] == "SEAL:R",
              "families": [o["object_family_id"]]} for o in objects]
    out["P9"] = S.permutation_test(seals, transfer_factory(seals), draws, seed + 9)

    # pass rules for the drift tests, Holm across P4-P8, influence for passes
    factories = {"P4": (opening, slot_factory), "P6": (variants, variant_factory),
                 "P7": (legends, length_factory), "P8": (scored, transfer_factory), "P9": (seals, transfer_factory)}
    adjusted = holm({k: out[k]["p"] for k in DRIFT})
    for k in DRIFT + ("P9",):
        res = out[k]
        res["holm_p"] = adjusted.get(k)
        res["outcome"] = "pass" if res["p"] <= 0.05 else "fail"
        if influence and res["outcome"] == "pass" and k in factories:
            rows, factory = factories[k]
            res["influence"] = influence_permutation(rows, factory, min(draws, 2999), seed + 100 * int(k[1:]))
            if not res["influence"]["single_rule_met"]:
                res["outcome"] = "fail"
        if k in DRIFT:
            res["weight"] = 1.0 if res["outcome"] == "pass" and adjusted[k] <= 0.05 else (0.5 if res["outcome"] == "pass" else 0.0)
    return out


def score_subset(objects, frozen, draws, boot, seed, only):
    """The same statistics and pass rules as score_predictions, for a subset of
    predictions and without the influence rule or Holm weights."""
    out = {}
    if only & {"P1", "P2"}:
        close = S.units(objects, "closing")
        ind = [r["value"] in set(frozen["closing_stock"]) for r in close]
        if "P1" in only:
            out["P1"] = bootstrap_share_difference(close, ind, boot, seed + 1)
            out["P1"]["outcome"] = equivalence_outcome(out["P1"])
        if "P2" in only:
            u = np.array([r["u"] for r in close])
            bottom = np.array(ind, dtype=float)[u < 1 / 3]
            out["P2"] = {"bottom_share": float(bottom.mean()),
                         "outcome": "pass" if bottom.mean() >= BOTTOM_SHARE else "fail"}
    if "P3" in only:
        pairs = S.units(objects, "closing_pair")
        find = [r["value"] in set(frozen["closing_formulae"]) for r in pairs]
        out["P3"] = bootstrap_share_difference(pairs, find, boot, seed + 3)
        out["P3"]["outcome"] = equivalence_outcome(out["P3"])

    def slot_factory(rows):
        codes, _ = S.category_codes(rows, MIN_CATEGORY)
        return S.between_ratio_factory(codes)
    opening = S.units(objects, "opening")
    if "P4" in only:
        out["P4"] = S.permutation_test(opening, slot_factory(opening), draws, seed + 4)
    if "P5" in only:
        open_rows = [r for r in opening if r["text"]["closing"] is not None]
        close_rows = [dict(r, value=r["text"]["closing"]) for r in open_rows]
        out["P5"] = contrast_test(open_rows, close_rows, slot_factory, draws, seed + 5)
    legends = S.units(objects, "length", min_length=1)
    if "P6" in only:
        variants = S.variant_tokens([{"stratum": r["stratum"], "u": r["u"], "object_family_id": r["families"][0],
                                      "text": {"signs": r["signs"]}} for r in S.all_legends(objects)], S.load_variant_classes())
        out["P6"] = S.permutation_test(variants, S.variant_statistic_factory(variants)[0], draws, seed + 6)
    if "P7" in only:
        out["P7"] = S.permutation_test(legends, S.stratified_spearman_factory([r["value"] for r in legends], legends), draws, seed + 7)
    if "P8" in only:
        scored = []
        for r in S.units(objects, "length", min_length=2):
            values = [frozen["nonfinal_scores"][s] for s in r["signs"][:-1] if s in frozen["nonfinal_scores"]]
            if values:
                scored.append(dict(r, value=float(np.mean(values))))
        out["P8"] = S.permutation_test(scored, S.pearson_factory([r["value"] for r in scored]), draws, seed + 8)
    if "P9" in only:
        seals = [{"stratum": o["stratum"], "u": o["u"], "value": o["object_type"] == "SEAL:R"} for o in objects]
        out["P9"] = S.permutation_test(seals, S.pearson_factory([r["value"] for r in seals]), draws, seed + 9)
    for k in ("P4", "P5", "P6", "P7", "P8", "P9"):
        if k in out:
            out[k]["outcome"] = "pass" if out[k]["p"] <= 0.05 else "fail"
    return out


def contrast_test(open_rows, close_rows, slot_factory, draws, seed):
    """D = z(opening) - z(closing), each statistic standardised by its own null, with the
    same permutation of heights applied to both slots (they share legends)."""
    rng = np.random.default_rng(seed)
    u = np.array([r["u"] for r in open_rows])
    index = S.strata_index(open_rows)
    f_open, f_close = slot_factory(open_rows), slot_factory(close_rows)
    obs = np.array([f_open(u), f_close(u)])
    null = np.empty((draws, 2))
    for d in range(draws):
        v = S.permuted_u(u, index, rng)
        null[d] = f_open(v), f_close(v)
    mean, sd = null.mean(0), null.std(0, ddof=1)
    z_obs = (obs - mean) / sd
    z_null = (null - mean) / sd
    d_obs = z_obs[0] - z_obs[1]
    d_null = z_null[:, 0] - z_null[:, 1]
    p = (1 + np.sum(d_null >= d_obs - 1e-12)) / (draws + 1)
    return {"units": len(open_rows), "z_opening": float(z_obs[0]), "z_closing": float(z_obs[1]),
            "observed": float(d_obs), "null_sd": float(d_null.std(ddof=1)), "p": float(p), "draws": draws, "seed": seed}


# ---------------------------------------------------------------- credence

EFFECTS = {"P1": {"pass": 0.05, "inconclusive": -0.03, "fail": None},
           "P2": {"pass": 0.03, "fail": -0.10},
           "P3": {"pass": 0.03, "inconclusive": -0.02, "fail": -0.05},
           "P4": {"pass": 0.08, "fail": -0.06},
           "P5": {"pass": 0.06, "fail": -0.04},
           "P6": {"pass": 0.05, "fail": -0.04},
           "P7": {"pass": 0.04, "fail": -0.03},
           "P8": {"pass": 0.05, "fail": -0.01}}


def credence(results, start):
    """Joint rule: add each prediction's effect (drift passes scaled by their Holm weight),
    clamp to [0.02, 0.90]; the kill condition overrides."""
    steps = {}
    total = start
    for k, eff in EFFECTS.items():
        outcome = results[k]["outcome"]
        delta = eff[outcome]
        if delta is None:
            continue
        if k in DRIFT and outcome == "pass":
            delta *= results[k]["weight"]
        steps[k] = delta
        total += delta
    killed_fixity = results["P1"]["outcome"] == "fail"
    killed_drift = all(results[k]["outcome"] == "fail" for k in ("P4", "P5", "P6", "P7"))
    value = 0.02 if (killed_fixity or killed_drift) else min(0.90, max(0.02, total))
    status = "dead" if (killed_fixity or killed_drift) else ("strengthened" if value > start else "weakened")
    return {"start": start, "steps": steps, "sum": round(total, 4), "credence": round(value, 4), "status": status,
            "kill_fixity": killed_fixity, "kill_drift": killed_drift}
