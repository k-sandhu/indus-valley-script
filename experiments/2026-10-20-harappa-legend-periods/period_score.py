"""Score the predictions of the Harappa legend-periods shot on one population.

The same function runs the rehearsal on the discovery seals, the planted-effect power
simulation and, frozen by hash, the single confirmation read of Vats's Mound F seals.
The closing stock and the test thresholds are read from a frozen JSON file.

Fixity (P1, P2) is scored as equivalence and level. Drift tests (P3 to P7) have three
outcomes: "drift" when the permutation p-value is at most 0.05 and survives the
single-deletion influence rule, "no drift" when p exceeds 0.10, and "inconclusive"
otherwise. The positive control (PC) asks whether rectangular seals become commoner
through the sequence, the change in seal form that HARP dated to Period 3C.
"""
import math

import numpy as np

import period_stats as P
from period_stats import S

DRIFT = ("P3", "P4", "P5", "P6", "P7")
INFLUENCE_UNITS = 10
INFLUENCE_P = 0.10
NO_DRIFT_P = 0.10
DRIFT_P = 0.05


# ---------------------------------------------------------------- fixity

def bootstrap_difference(rows, indicator, draws, seed):
    """Late-third minus early-third share with 90% and 95% percentile intervals,
    resampling units with replacement within frames."""
    rng = np.random.default_rng(seed)
    ind = np.asarray(indicator, dtype=float)
    u = np.array([r["u"] for r in rows])
    index = S.strata_index(rows)
    observed = S.share_difference_factory(ind)(u)
    values = np.empty(draws)
    for b in range(draws):
        pick = np.concatenate([rng.choice(idx, len(idx), replace=True) for idx in index])
        low, high = u[pick] < 1 / 3, u[pick] >= 2 / 3
        values[b] = ind[pick][high].mean() - ind[pick][low].mean() if low.any() and high.any() else 0.0
    q = np.quantile(values, [0.025, 0.05, 0.95, 0.975])
    return {"observed": float(observed), "interval90": [float(q[1]), float(q[2])], "interval95": [float(q[0]), float(q[3])],
            "draws": draws, "seed": seed, "units": len(rows),
            "early_units": int(np.sum(u < 1 / 3)), "late_units": int(np.sum(u >= 2 / 3)),
            "early_share": float(ind[u < 1 / 3].mean()) if np.any(u < 1 / 3) else None,
            "late_share": float(ind[u >= 2 / 3].mean()) if np.any(u >= 2 / 3) else None}


def equivalence_outcome(res, frozen):
    """pass: 90% bootstrap interval inside (-margin, margin). fail: two-sided
    permutation p (u permuted within frames) at most 0.05 and the estimate at least
    fail_size in absolute value. Otherwise inconclusive. The percentile bootstrap is
    used only for the equivalence side; at these sample sizes its 95% interval excluded
    zero in 7.7% of null populations, while the permutation test keeps its level."""
    margin, fail_size = frozen["equivalence_margin"], frozen["fail_size"]
    lo90, hi90 = res["interval90"]
    if -margin < lo90 and hi90 < margin:
        return "pass"
    if res["perm_p"] <= DRIFT_P and abs(res["observed"]) >= fail_size:
        return "fail"
    return "inconclusive"


def influence_equivalence(rows, indicator, frozen, draws, seed):
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
        res = bootstrap_difference(rows[:i] + rows[i + 1:], np.delete(ind, i), draws, seed + 3000 + k)
        inside = -frozen["equivalence_margin"] < res["interval90"][0] and res["interval90"][1] < frozen["equivalence_margin"]
        out.append({"families": rows[i]["families"], "interval90": res["interval90"], "outcome": "pass" if inside else "outside"})
    return {"single_unit": out, "rule_met": all(x["outcome"] == "pass" for x in out)}


# ---------------------------------------------------------------- drift

def drift_outcome(p, influence_ok=True):
    if p <= DRIFT_P and influence_ok:
        return "drift"
    if p > NO_DRIFT_P:
        return "no drift"
    return "inconclusive"


def influence_permutation(rows, factory, draws, seed, alternative):
    """Re-test after deleting, one at a time, the INFLUENCE_UNITS units whose deletion
    moves the statistic most toward its null (lower, or nearer the null centre for a
    two-sided test)."""
    u = np.array([r["u"] for r in rows])
    base = factory(rows)(u)
    drops = []
    for i in range(len(rows)):
        sub = rows[:i] + rows[i + 1:]
        value = factory(sub)(np.array([r["u"] for r in sub]))
        drops.append((abs(value) - abs(base) if alternative == "two-sided" else value - base, i))
    worst = [i for _, i in sorted(drops)[:INFLUENCE_UNITS]]
    single = []
    for k, i in enumerate(worst):
        sub = rows[:i] + rows[i + 1:]
        res = S.permutation_test(sub, factory(sub), draws, seed + 1000 + k, alternative)
        single.append({"families": rows[i]["families"], "stratum": rows[i]["stratum"], "p": res["p"]})
    strata = []
    for k, name in enumerate(sorted({r["stratum"] for r in rows})):
        sub = [r for r in rows if r["stratum"] != name]
        if len(sub) < 3:
            continue
        res = S.permutation_test(sub, factory(sub), draws, seed + 2000 + k, alternative)
        strata.append({"dropped": name, "z": res["z"], "p": res["p"]})
    max_p = max(s["p"] for s in single) if single else None
    return {"single_unit": single, "max_single_p": max_p, "single_rule_met": max_p is not None and max_p <= INFLUENCE_P,
            "leave_frame_out": strata}


def holm(pvalues):
    names = sorted(pvalues, key=lambda k: pvalues[k])
    m = len(names)
    adjusted, running = {}, 0.0
    for j, k in enumerate(names):
        running = max(running, min(1.0, (m - j) * pvalues[k]))
        adjusted[k] = running
    return adjusted


# ---------------------------------------------------------------- the predictions

def factories(objects, frozen):
    """Units and statistic factories of every drift test and the positive control."""
    k = frozen["min_category"]

    def slot_factory(rows):
        codes, _ = S.category_codes(rows, k)
        return S.between_ratio_factory(codes)

    def variant_factory(rows):
        return S.variant_statistic_factory(rows)[0]

    def length_factory(rows):
        return S.stratified_spearman_factory([r["value"] for r in rows], rows)

    def inventory_factory(rows):
        return P.inventory_factory(rows, frozen["inventory_min_units"])[0]

    def pearson(rows):
        return S.pearson_factory([r["value"] for r in rows])

    opening = P.position_units(objects, "opening")
    closing = P.position_units(objects, "closing")
    legends = P.length_units(objects)
    variants = S.variant_tokens([{"stratum": r["stratum"], "u": r["u"], "object_family_id": r["families"][0],
                                  "text": {"signs": r["signs"]}} for r in S.all_legends(objects)], S.load_variant_classes())
    inventory_rows = S.all_legends(objects)
    rect = P.indicator_units(objects, lambda o: o["object_type"] == "SEAL:R")
    return {"P3": (opening, slot_factory, "greater"),
            "P4": (variants, variant_factory, "greater"),
            "P5": (legends, length_factory, "two-sided"),
            "P6": (inventory_rows, inventory_factory, "greater"),
            "P7": (closing, slot_factory, "greater"),
            "PC": (rect, pearson, "greater")}


def score_predictions(objects, frozen, draws=9999, boot=9999, seed=20261021, influence=True, only=None):
    wanted = set(only) if only is not None else {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "PC"}
    stock = set(frozen["closing_stock"])
    out = {}
    closing = P.position_units(objects, "closing")
    ind = [r["value"] in stock for r in closing]
    if "P1" in wanted:
        p1 = bootstrap_difference(closing, ind, boot, seed + 1)
        flags = np.asarray(ind, dtype=float)

        def share_factory(rows):
            keep = {id(r) for r in rows}
            return S.share_difference_factory(np.array([f for r, f in zip(closing, flags) if id(r) in keep]))
        perm = S.permutation_test(closing, share_factory(closing), draws, seed + 2, "two-sided")
        p1["perm_p"] = perm["p"]
        p1["perm_null_sd"] = perm["null_sd"]
        p1["outcome"] = equivalence_outcome(p1, frozen)
        if influence and p1["outcome"] == "pass":
            p1["influence"] = influence_equivalence(closing, ind, frozen, min(boot, 1999), seed + 1)
            if not p1["influence"]["rule_met"]:
                p1["outcome"] = "inconclusive"
        if influence and p1["outcome"] == "fail":
            p1["influence"] = influence_permutation(closing, share_factory, min(draws, 2999), seed + 50, "two-sided")
            if not p1["influence"]["single_rule_met"]:
                p1["outcome"] = "inconclusive"
        out["P1"] = p1
    if "P2" in wanted:
        u = np.array([r["u"] for r in closing])
        early = np.array(ind, dtype=float)[u < 1 / 3]
        level = float(early.mean()) if len(early) else None
        after = float((early.sum() - 1) / (len(early) - 1)) if len(early) > 1 and early.sum() > 0 else None
        threshold = frozen["early_share_threshold"]
        out["P2"] = {"early_units": int(len(early)), "early_share": level, "share_after_worst_single_deletion": after,
                     "threshold": threshold,
                     "outcome": "pass" if level is not None and level >= threshold and (after or 0) >= threshold else "fail"}

    built = factories(objects, frozen)
    for key, (rows, factory, alternative) in built.items():
        if key not in wanted:
            continue
        if len(rows) < 3:
            out[key] = {"units": len(rows), "p": 1.0, "outcome": "no drift" if key != "PC" else "fail", "note": "too few units"}
            continue
        res = S.permutation_test(rows, factory(rows), draws, seed + 10 + DRIFT.index(key) if key in DRIFT else seed + 30, alternative)
        if key == "P4":
            res["classes"] = S.variant_statistic_factory(rows)[1]
        if key == "P6":
            res["signs"] = len(P.inventory_factory(rows, frozen["inventory_min_units"])[1])
        if key in ("P3", "P7"):
            res["categories"] = len(S.category_codes(rows, frozen["min_category"])[1])
        out[key] = res

    present = [k for k in DRIFT if k in out]
    family = {k: out[k]["p"] for k in present}
    if "P1" in out:
        family["P1"] = out["P1"]["perm_p"]
    adjusted = holm(family) if family else {}
    if "P1" in out:
        out["P1"]["holm_p"] = adjusted["P1"]
    for k in present:
        res = out[k]
        res["holm_p"] = adjusted[k]
        ok = True
        if influence and res["p"] <= DRIFT_P:
            rows, factory, alternative = built[k]
            res["influence"] = influence_permutation(rows, factory, min(draws, 2999), seed + 100 * (DRIFT.index(k) + 1), alternative)
            ok = res["influence"]["single_rule_met"]
        res["outcome"] = drift_outcome(res["p"], ok)
    if "PC" in out and "outcome" not in out["PC"]:
        out["PC"]["outcome"] = "pass" if out["PC"]["p"] <= 0.05 else "fail"
    return out


# ---------------------------------------------------------------- credence

def credence(results, frozen, start):
    """Joint rule frozen in PREDICTIONS.json: add each prediction's effect; a "no drift"
    or a P1 pass adds half its gain when the positive control fails; the kill condition
    (a P1 fail or a drift whose Holm-adjusted p over P1 and P3-P7 is at most 0.05)
    overrides; clamp to [0.02, 0.90]."""
    effects = frozen["effects"]
    control = results["PC"]["outcome"] == "pass"
    steps, total = {}, start
    for k in ("P1", "P2") + DRIFT:
        outcome = results[k]["outcome"]
        delta = effects[k][outcome]
        if not control and delta > 0 and k != "P2":
            delta *= 0.5
        steps[k] = delta
        total += delta
    kill_fixity = results["P1"]["outcome"] == "fail" and results["P1"]["holm_p"] <= DRIFT_P
    kill_drift = [k for k in DRIFT if results[k]["outcome"] == "drift" and results[k]["holm_p"] <= DRIFT_P]
    dead = kill_fixity or bool(kill_drift)
    value = 0.02 if dead else min(0.90, max(0.02, total))
    status = "dead" if dead else ("strengthened" if value > start else "weakened")
    return {"start": start, "steps": steps, "sum": round(total, 4), "credence": round(value, 4), "status": status,
            "positive_control_passed": control, "kill_fixity": kill_fixity, "kill_drift": kill_drift}
