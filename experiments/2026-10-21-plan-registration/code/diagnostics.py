"""Post-outcome diagnostics of the registration run (not part of the frozen protocol).

Written after registration-v1/results.json was read, to explain its
validation failure and to complete one secondary check that register.py
skipped. It changes no frozen value.

1. Chanhu-daro magnetic arrow against IGRF 1935. register.py looked up the
   declination by source id in a field that holds a citation string, found
   none and skipped the check; here the lookup uses the plan's town and its
   magnetic label.
2. Dholavira: every registered plan system against the imagery castle, and
   the spread of the castle systems before and after registration.
3. Agreement of the two registrars, plan by plan.
4. Leave-one-out rotations of the Chanhu-daro chain's link to the imagery.
5. Planning power of the frozen P0 (Pleiades model) on the dated towns that
   now have true-north values, with their registered or imagery errors and
   their exploratory-table dates; no measured deviation enters it.
"""
import argparse
import copy
import hashlib
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[1]
TA = ROOT / "experiments" / "2026-10-21-town-axes"
sys.path.insert(0, str(HERE))
import regfit  # noqa: E402


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--nsim", type=int, default=20000)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists")
    R = json.loads(Path(a.results).read_text(encoding="utf-8"))
    table = json.loads((TA / "table-v1" / "settlement-axes.json").read_text(encoding="utf-8"))
    trow = {t["town"]: t for t in table["towns"]}
    res = {"schema_version": "1.0", "task": "plan-registration-diagnostics", "synthetic": False, "exploratory": True,
           "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # 1. Magnetic arrow at Chanhu-daro.
    pb = json.loads((TA / "measure-plan-B" / "towns" / "chanhu-daro.json").read_text(encoding="utf-8"))
    src = next(s for s in pb["sources"] if s["id"] == "mackay1943-pl4")
    am = src["north_arrow_measurement"]
    s_arrow = math.hypot(am["pick_sigma_deg"], am["drafting_sigma_deg"])
    dec = next(p["igrf_declination_deg"] for p in trow["chanhu-daro"]["plans"]
               if p["role"] == "plan-B" and p["north_reference"] == "magnetic")
    ab = R["plans"]["chanhu-daro:mackay1943-pl4"]["arrow_true_bearing"]["all points"]
    d = regfit.wrap180(ab["alpha_deg"] - dec)
    comb = math.hypot(ab["sigma_deg"], s_arrow)
    res["chanhu_daro_magnetic_arrow"] = {"alpha_deg": ab["alpha_deg"], "sigma_registration_deg": ab["sigma_deg"],
                                         "sigma_arrow_deg": s_arrow, "igrf_1935_declination_deg": dec,
                                         "difference_deg": d, "z": d / comb,
                                         "registrars_accepting": [k for k, v in R["plans"]["chanhu-daro:mackay1943-pl4"]["registrars"].items()
                                                                  if v["all_points"].get("accepted")]}

    # 2. Dholavira systems against the imagery castle.
    img = trow["dholavira"]
    rows = []
    for r in R["systems"]:
        if r["town"] != "dholavira":
            continue
        diff = regfit.wrap180(r["theta_true_deg"] - img["theta_deg"])
        cmb = math.hypot(r["sigma_true_deg"], img["sigma_theta_deg"])
        rows.append({k: r[k] for k in ("plan", "variant", "system", "part", "description", "theta_plan_deg", "alpha_deg",
                                       "theta_true_deg", "sigma_true_deg")} | {"difference_from_imagery_deg": diff,
                                                                               "z": diff / cmb})
    allp = [r for r in rows if r["variant"] == "all points"]
    res["dholavira"] = {"imagery_theta_deg": img["theta_deg"], "imagery_sigma_deg": img["sigma_theta_deg"], "systems": rows,
                        "spread_relative_to_arrows_deg": max(r["theta_plan_deg"] for r in allp) - min(r["theta_plan_deg"] for r in allp),
                        "spread_true_north_deg": max(r["theta_true_deg"] for r in allp) - min(r["theta_true_deg"] for r in allp),
                        "spread_true_north_wall_plans_deg": (lambda v: max(v) - min(v))(
                            [r["theta_true_deg"] for r in allp if "contour" not in (r["part"] or "")])}

    # 3. Registrar agreement.
    agree = []
    for pid, p in R["plans"].items():
        regs = [v["all_points"] for k, v in p["registrars"].items() if k in ("control-R1", "control-R2")]
        ok = [v for v in regs if v.get("accepted") and v.get("informative")]
        if len(ok) == 2:
            diff = regfit.wrap180(ok[1]["phi_deg"] - ok[0]["phi_deg"])
            cmb = math.hypot(ok[0]["sigma_phi_deg"], ok[1]["sigma_phi_deg"])
            agree.append({"plan": pid, "difference_deg": diff, "combined_sigma_deg": cmb, "z": diff / cmb})
    chi2 = sum(x["z"] ** 2 for x in agree)
    res["registrar_agreement"] = {"plans": agree, "chi2": chi2, "n": len(agree),
                                  "note": "dholavira fig. 6.3 and fig. 2.11 are the same drawing, so their two terms are not independent"}

    # 4. Leave-one-out at the Chanhu-daro chain's imagery link (registrar R1).
    cf = json.loads((PKG / "control-R1" / "chanhu-daro__mackay1943-pl4.json").read_text(encoding="utf-8"))
    import cptools  # noqa: E402
    plans = cptools.load_plans(cf)
    mos = cptools.load_mosaics(cf)
    loo = []
    for link in cf["links"]:
        if link["to"] != "map":
            continue
        full = regfit.fit_from_link(link, plans, mos, reveal_rotation=True)
        for i, p in enumerate(link["points"]):
            sub = regfit.fit_from_link(dict(link, points=[q for j, q in enumerate(link["points"]) if j != i]), plans, mos,
                                       reveal_rotation=True)
            loo.append({"left_out": p["id"], "feature": p.get("image_feature") or p.get("plan_feature"),
                        "phi_change_deg": regfit.wrap180(sub["phi_deg"] - full["phi_deg"]), "sigma_phi_deg": sub["sigma_phi_deg"]})
    res["chanhu_daro_R1_imagery_link_leave_one_out"] = loo

    # 5. Planning power on the dated true-north towns.
    sys.path.insert(0, str(TA))
    import astro  # noqa: E402
    import score  # noqa: E402
    expl = json.loads((TA / "exploratory-v1" / "table.json").read_text(encoding="utf-8"))
    erow = {t["town"]: t for t in expl["towns"]}
    hz = json.loads((TA / "horizon-v1" / "horizons.json").read_text(encoding="utf-8"))
    import numpy as np
    horizons = {}
    for t in hz["towns"]:
        az = np.array([p["az"] for p in t["profile"]])
        alt = np.array([p["alt_deg"] for p in t["profile"]])
        horizons[t["town"]] = (lambda x, az=az, alt=alt: float(np.interp(x % 360.0, az, alt)))
    towns = []
    for name in R["true_north_dated_towns"]:
        t = copy.deepcopy(erow[name])
        tv = R["towns"].get(name)
        if trow[name].get("theta_deg") is not None:
            t["sigma_theta_deg"] = trow[name]["sigma_theta_deg"]
            t["sigma_source"] = "imagery"
        else:
            t["sigma_theta_deg"] = tv["sigma_true_deg"]
            t["sigma_source"] = "registration"
        towns.append(t)
    stars = astro.load_stars()
    pw = score.power(towns, horizons, stars, nsim=a.nsim)
    res["planning_power_P0_pleiades"] = {"towns": [{"town": t["town"], "D_year": t["D_year"], "sigma_D": t["sigma_D"],
                                                    "sigma_theta_deg": t["sigma_theta_deg"], "sigma_source": t["sigma_source"]}
                                                   for t in towns], "power": pw, "nsim": a.nsim,
                                         "note": "uses dates and errors only; no measured deviation enters the simulation"}

    res["provenance"] = {"inputs": {a.results: sha(a.results)},
                         "code": {"diagnostics.py": sha(__file__), "regfit.py": sha(HERE / "regfit.py"),
                                  "town-axes/score.py": sha(TA / "score.py"), "town-axes/astro.py": sha(TA / "astro.py")}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("chanhu_daro_magnetic_arrow", "registrar_agreement", "chanhu_daro_R1_imagery_link_leave_one_out")}, indent=1)[:4000])
    print("dholavira spreads", res["dholavira"]["spread_relative_to_arrows_deg"], res["dholavira"]["spread_true_north_deg"],
          res["dholavira"]["spread_true_north_wall_plans_deg"])
    for r in rows:
        print(r["plan"], r["variant"], r["system"], round(r["theta_true_deg"], 2), round(r["z"], 2))
    print("power", pw)


if __name__ == "__main__":
    main()
