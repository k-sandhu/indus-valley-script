"""Independent recomputation of Shot A's P1a, P4 and kill decision on the confirmation half.

Written after the confirmation run. It does not import confirm.py, rank_lib.py or
seal_table.py: the population, residual model, statistics and permutations are coded
again here from the rules stated in PREDICTIONS.md. Permutations use Python's
random.Random with seed 777 (confirm.py uses numpy's default generator with seed
20261013). Reading the confirmation half goes through shots_common.load_half, which logs
the access. Output: verification.json.
"""
from pathlib import Path
import json
import math
import random
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from shots_common import load_half  # noqa: E402

N = 9999
SIX = {"Mohenjo-daro", "Harappa", "Dholavira", "Lothal", "Chanhu-daro", "Kalibangan"}
OK_PRES = {"complete", "slightly chipped", "chipped", "complsete"}
HIGH = {"001", "595", "679", "820"}


def positive(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def population(rows):
    best = {}
    for r in rows:
        if not r["object_type"].startswith("SEAL"):
            continue
        f = r["object_family_id"]
        if f not in best:
            best[f] = r
            continue
        cur = best[f]
        if r["length"] > cur["length"] or (r["length"] == cur["length"] and r["record_id"] < cur["record_id"]):
            best[f] = r
    pop = []
    for f, r in best.items():
        m = r["metadata"]
        h, v = positive(m.get("horizontal(mm)")), positive(m.get("vertical(mm)"))
        if r["object_type"] not in ("SEAL:S", "SEAL:R") or h is None or v is None:
            continue
        if (m.get("preservation") or "").strip() not in OK_PRES:
            continue
        if not (r["complete_observed"] and not r["has_unknown_sign"] and r["single_line"] and r["length"] >= 2):
            continue
        pop.append({"family": f, "component": r["component"], "type": r["object_type"],
                    "site": r["site"] if r["site"] in SIX else "other", "len": min(r["length"], 9),
                    "last": r["signs_reading_rtl"][-1], "y": math.log(h) + math.log(v)})
    reps = {}
    for t in pop:
        k = t["component"]
        if k not in reps or (len(t["family"]), t["family"]) < (len(reps[k]["family"]), reps[k]["family"]):
            reps[k] = t
    return pop, list(reps.values())


def residuals(units):
    cols = [np.ones(len(units))]
    for key in ("type", "site", "len"):
        levels = sorted({t[key] for t in units})
        for lv in levels[1:]:
            cols.append(np.array([1.0 if t[key] == lv else 0.0 for t in units]))
    X = np.column_stack(cols)
    y = np.array([t["y"] for t in units])
    beta = np.linalg.pinv(X) @ y
    return y - X @ beta


def between(labels, res):
    sums, counts = {}, {}
    for l, r in zip(labels, res):
        sums[l] = sums.get(l, 0.0) + r
        counts[l] = counts.get(l, 0) + 1
    return sum(sums[l] ** 2 / counts[l] for l in sums if counts[l] >= 3)


def contrast(labels, res):
    h = [r for l, r in zip(labels, res) if l in HIGH]
    o = [r for l, r in zip(labels, res) if l not in HIGH]
    return sum(h) / len(h) - sum(o) / len(o), len(h)


def main():
    rows = load_half("confirmation", HERE)
    pop, units = population(rows)
    res = residuals(units)
    labels = [t["last"] for t in units]
    strata = {}
    for i, t in enumerate(units):
        strata.setdefault((t["type"], t["site"], t["len"]), []).append(i)
    rnd = random.Random(777)

    def shuffled():
        out = list(labels)
        for idx in strata.values():
            vals = [labels[i] for i in idx]
            rnd.shuffle(vals)
            for i, v in zip(idx, vals):
                out[i] = v
        return out

    obs_b = between(labels, res)
    obs_c, n_high = contrast(labels, res)
    null_b, null_c = [], []
    for _ in range(N):
        s = shuffled()
        null_b.append(between(s, res))
        null_c.append(contrast(s, res)[0])
    p1a_p = (1 + sum(x >= obs_b for x in null_b)) / (1 + N)
    p4_p = (1 + sum(x >= obs_c for x in null_c)) / (1 + N)
    mine = {"population_seals": len(pop), "components": len(units), "residual_sd": float(np.std(res)),
            "P1a_ratio": float(obs_b / (sum(null_b) / N)), "P1a_observed": float(obs_b), "P1a_p": p1a_p,
            "P4_difference": float(obs_c), "P4_n_high": n_high, "P4_p": p4_p}
    mine["P1a_verdict"] = "pass" if p1a_p < 0.05 else "fail"
    mine["P4_verdict"] = ("pass" if p4_p < 0.05 else "fail") if n_high >= 5 else "untestable"
    mine["kill_condition_met"] = bool(mine["P4_verdict"] != "pass" and mine["P1a_verdict"] != "pass")

    frozen = json.loads((HERE / "confirmation" / "results.json").read_text(encoding="utf-8"))
    theirs = {"population_seals": frozen["population"]["seals"], "components": frozen["population"]["components"],
              "residual_sd": frozen["population"]["residual_sd"], "P1a_observed": frozen["P1a"]["observed"],
              "P1a_ratio": frozen["P1a"]["ratio_to_null_mean"], "P1a_p": frozen["P1a"]["p_one_sided"],
              "P4_difference": frozen["P4"]["difference"], "P4_n_high": frozen["P4"]["n_high"],
              "P4_p": frozen["P4"]["p_one_sided"], "P1a_verdict": frozen["P1a"]["verdict"],
              "P4_verdict": frozen["P4"]["verdict"], "kill_condition_met": frozen["kill_condition_met"]}

    def p_tol(p):
        return 4 * math.sqrt(2 * max(p, 1 / N) * (1 - p) / N)

    checks = []
    for k in ("population_seals", "components", "P4_n_high", "P1a_verdict", "P4_verdict", "kill_condition_met"):
        checks.append({"quantity": k, "verification": mine[k], "confirm_py": theirs[k], "rule": "exact", "agree": mine[k] == theirs[k]})
    for k in ("residual_sd", "P1a_observed", "P4_difference"):
        checks.append({"quantity": k, "verification": mine[k], "confirm_py": theirs[k], "rule": "abs diff <= 1e-9",
                       "agree": abs(mine[k] - theirs[k]) <= 1e-9})
    checks.append({"quantity": "P1a_ratio", "verification": mine["P1a_ratio"], "confirm_py": theirs["P1a_ratio"],
                   "rule": "relative diff <= 0.02 (null mean is a Monte Carlo estimate)",
                   "agree": abs(mine["P1a_ratio"] - theirs["P1a_ratio"]) <= 0.02 * theirs["P1a_ratio"]})
    for k in ("P1a_p", "P4_p"):
        tol = p_tol(theirs[k])
        checks.append({"quantity": k, "verification": mine[k], "confirm_py": theirs[k],
                       "rule": f"abs diff <= 4 Monte Carlo SE of a difference of two p estimates ({tol:.4f})",
                       "agree": abs(mine[k] - theirs[k]) <= tol})
    for c in checks:
        c["agree"] = bool(c["agree"])
        for k in ("verification", "confirm_py"):
            if isinstance(c[k], (np.floating, np.integer)):
                c[k] = c[k].item()
    out = {"stage": "independent verification after the frozen confirmation run",
           "method": __doc__.strip(), "permutations": N, "seed": 777,
           "checks": checks, "all_agree": all(c["agree"] for c in checks)}
    (HERE / "verification.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({c["quantity"]: (c["verification"], c["confirm_py"], c["agree"]) for c in checks}, indent=1))
    print("all agree:", out["all_agree"])


if __name__ == "__main__":
    main()
