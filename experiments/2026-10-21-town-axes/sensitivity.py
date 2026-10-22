"""Sensitivity checks of PROTOCOL.md; reported beside the frozen result, never replacing it.

For each variant the town list is rebuilt, the stage-1 target choice is repeated on the discovery towns,
and P0 (all towns) and P3 (confirmation towns) are recomputed.
"""
import argparse
import copy
import json
from pathlib import Path

import numpy as np
from scipy import stats

import astro
import score
from common import BASE, finite, provenance, write_new


def choose(disc, horizons, stars, k, flat):
    best = None
    for name, _, _ in astro.TARGETS:
        c = sum(x["chi2"] for x in score.chi2_terms(disc, name, horizons, stars, k=k, flat=flat))
        if best is None or c < best[1]:
            best = (name, c)
    return best


def evaluate(towns, horizons, stars, k=0.30, flat=False):
    towns = [t for t in towns if t.get("theta_deg") is not None and t.get("D_year") is not None]
    disc = [t for t in towns if t["town"] in score.DISCOVERY]
    conf = [t for t in towns if t["town"] not in score.DISCOVERY]
    out = {"n_all": len(towns), "n_confirmation": len(conf)}
    if len(towns) >= 3:
        th = [t["theta_deg"] for t in towns]; D = [t["D_year"] for t in towns]
        r, p, how = score.perm_p(th, D, n_random=50000)
        out.update(pearson_r=finite(r, 4), p_one_sided=finite(p, 5), spearman_rho=finite(stats.spearmanr(th, D).statistic, 4))
    if len(disc) >= 2 and conf:
        name, c = choose(disc, horizons, stars, k, flat)
        chi_star = sum(x["chi2"] for x in score.chi2_terms(conf, name, horizons, stars, k=k, flat=flat))
        var0 = [t["sigma_theta_deg"] ** 2 + score.SIGMA_INT ** 2 for t in conf]
        const = sum(t["theta_deg"] / (t["sigma_theta_deg"] ** 2 + 1) for t in disc) / sum(1 / (t["sigma_theta_deg"] ** 2 + 1) for t in disc)
        out.update(chosen_target=name, chi2_target=finite(chi_star, 3),
                   chi2_cardinal=finite(sum(t["theta_deg"] ** 2 / v for t, v in zip(conf, var0)), 3),
                   chi2_constant=finite(sum((t["theta_deg"] - const) ** 2 / v for t, v in zip(conf, var0)), 3))
    return out


def variant_towns(table, which):
    base = [t for t in table["towns"]]
    out = []
    for t in base:
        u = copy.deepcopy(t)
        if which == "intcal20_dates":
            u["D_year"] = t.get("D_14C_year"); u["sigma_D"] = t.get("sigma_D_14C") or t.get("sigma_D") or 200.0
        elif which == "first_occupation_dates":
            u["D_year"] = t.get("D_first_occupation_year"); u["sigma_D"] = t.get("sigma_D") or 200.0
        elif which in ("img_A_only", "img_B_only"):
            key = "A" if which.endswith("A_only") else "B"
            u["theta_deg"] = t.get(f"theta_img_{key}")
            se = t.get(f"se_img_{key}")
            u["sigma_theta_deg"] = max(se, 0.3) if se is not None else None
        elif which == "plan_true_north":
            u["theta_deg"] = t.get("theta_plan_true"); u["sigma_theta_deg"] = t.get("sigma_plan_true")
        out.append(u)
    return out


def all_systems(table):
    out = []
    for t in table["towns"]:
        for s in t.get("systems_all", []):
            if s.get("deviation_deg") is None or (s.get("D_year") or t.get("D_year")) is None:
                continue
            out.append({"town": f'{t["town"]}:{s["role"]}:{s["id"]}', "lat": t["lat"], "theta_deg": s["deviation_deg"],
                        "sigma_theta_deg": max(s.get("se_deg") or 0.3, 0.3), "D_year": s.get("D_year") or t["D_year"],
                        "sigma_D": s.get("sigma_D") or t["sigma_D"], "_horizon_town": t["town"]})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True); ap.add_argument("--horizons", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    stars = astro.load_stars()
    table, _, horizons = score.load(a.table, a.horizons)
    res = {"schema_version": "1.0", "task": "town-axes-sensitivity", "synthetic": False, "variants": {}}
    base = table["towns"]
    for label, kw in (("primary", {}), ("extinction_k020", {"k": 0.20}), ("extinction_k045", {"k": 0.45}),
                      ("no_extinction", {"k": None}), ("flat_horizon", {"flat": True})):
        res["variants"][label] = evaluate(base, horizons, stars, **kw)
    for which in ("intcal20_dates", "first_occupation_dates", "img_A_only", "img_B_only", "plan_true_north"):
        res["variants"][which] = evaluate(variant_towns(table, which), horizons, stars)
    systems = all_systems(table)
    hz2 = {s["town"]: horizons[s["_horizon_town"]] for s in systems}
    th = [s["theta_deg"] for s in systems]; D = [s["D_year"] for s in systems]
    if len(systems) >= 3:
        r, p, _ = score.perm_p(th, D, n_random=50000)
        res["variants"]["every_system"] = {"n_systems": len(systems), "pearson_r": finite(r, 4), "p_one_sided": finite(p, 5),
                                           "note": "systems from all measurers are not independent; descriptive only"}
    res["provenance"] = provenance([a.table, a.horizons, BASE / "stars-v1.json"], [BASE / "sensitivity.py", BASE / "score.py", BASE / "astro.py", BASE / "common.py"])
    print(write_new(a.out, res))


if __name__ == "__main__":
    main()
