"""Stage 1 (target choice on three towns) and stage 2 (frozen predictions) of PROTOCOL.md.

python score.py stage1 --table table-v1/settlement-axes.json --horizons horizon-v1/horizons.json --out discovery-v1/choice.json
python score.py stage2 --table ... --horizons ... --choice discovery-v1/choice.json --out confirmation-v1/results.json
"""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import math

import numpy as np
from scipy import stats

import astro
from common import BASE, finite, provenance, sha256_file, write_new

DISCOVERY = ("mohenjo-daro", "harappa", "kalibangan")
SIGMA_INT = 1.0
CODE = [BASE / "score.py", BASE / "astro.py", BASE / "common.py"]


def load(table_path, horizon_path):
    table = json.loads(Path(table_path).read_text(encoding="utf-8"))
    hz = json.loads(Path(horizon_path).read_text(encoding="utf-8"))
    horizons = {}
    for t in hz["towns"]:
        az = np.array([p["az"] for p in t["profile"]])
        alt = np.array([p["alt_deg"] for p in t["profile"]])
        horizons[t["town"]] = (lambda a, az=az, alt=alt: float(np.interp(a % 360.0, az, alt)))
    towns = [t for t in table["towns"] if t.get("theta_deg") is not None and t.get("D_year") is not None]
    return table, towns, horizons


def model(target, town, horizons, stars, k=0.30, flat=False, year=None):
    lat = town["lat"]
    hz = horizons[town["town"]]
    y = town["D_year"] if year is None else year
    th = astro.predicted_deviation(target, y, lat, hz, stars, k=k, flat=flat)
    rate = astro.deviation_rate(target, y, lat, hz, stars, k=k, flat=flat)
    return th, rate


def chi2_terms(towns, target, horizons, stars, **kw):
    terms = []
    for t in towns:
        th, rate = model(target, t, horizons, stars, **kw)
        var = t["sigma_theta_deg"] ** 2 + (rate * t["sigma_D"]) ** 2 + SIGMA_INT ** 2
        terms.append({"town": t["town"], "theta_obs": t["theta_deg"], "theta_pred": finite(th, 4),
                      "rate_deg_per_century": finite(rate * 100, 4), "sigma_total": finite(math.sqrt(var), 4),
                      "chi2": (t["theta_deg"] - th) ** 2 / var})
    return terms


def stage1(a):
    stars = astro.load_stars()
    table, towns, horizons = load(a.table, a.horizons)
    disc = [t for t in towns if t["town"] in DISCOVERY]
    if len(disc) < 2:
        raise SystemExit("fewer than two discovery towns with deviation and date")
    rows = []
    for name, _, _ in astro.TARGETS:
        terms = chi2_terms(disc, name, horizons, stars)
        rows.append({"target": name, "chi2": sum(x["chi2"] for x in terms), "towns": terms})
    best = min(rows, key=lambda r: r["chi2"])  # min keeps the first in protocol order on ties
    crit = stats.chi2.ppf(0.99, len(disc))
    out = {
        "schema_version": "1.0", "task": "town-axes-stage1", "synthetic": False,
        "discovery_towns": [t["town"] for t in disc], "sigma_int_deg": SIGMA_INT,
        "candidates": [{**r, "chi2": finite(r["chi2"], 4), "towns": [{**x, "chi2": finite(x["chi2"], 4)} for x in r["towns"]]} for r in rows],
        "chosen_target": best["target"], "chosen_chi2": finite(best["chi2"], 4),
        "chi2_99th_percentile": finite(crit, 4), "fails_on_discovery": bool(best["chi2"] > crit),
        "provenance": provenance([a.table, a.horizons, BASE / "stars-v1.json"], CODE),
    }
    digest = write_new(a.out, out)
    Path(a.out).with_suffix(".sha256").write_text(f"{digest}  {Path(a.out).name}\n", encoding="utf-8")
    print(digest)


def perm_p(x, y, n_random=200000, seed=20261021):
    """One-sided permutation p-value for Pearson r(x, y) > observed, exact when n <= 9."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    r0 = np.corrcoef(x, y)[0, 1]
    n = len(x)
    xc = (x - x.mean()) / np.linalg.norm(x - x.mean())
    yc = (y - y.mean()) / np.linalg.norm(y - y.mean())
    if n <= 9:
        rs = np.array([xc[list(p)] @ yc for p in itertools.permutations(range(n))])
        return float(r0), float(np.mean(rs >= r0 - 1e-12)), "exact"
    rng = np.random.default_rng(seed)
    hits, done = 0, 0
    while done < n_random:
        m = min(20000, n_random - done)
        idx = np.argsort(rng.random((m, n)), axis=1)
        rs = xc[idx] @ yc
        hits += int(np.sum(rs >= r0 - 1e-12)); done += m
    return float(r0), (hits + 1) / (n_random + 1), f"{n_random} random permutations"


def wls(theta, D, sig):
    w = 1.0 / (np.asarray(sig) ** 2 + SIGMA_INT ** 2)
    X = np.vstack([np.ones_like(D), D]).T
    W = np.diag(w)
    beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ np.asarray(theta))
    return beta


def bootstrap_slope(theta, D, sig, n=20000, seed=20261021):
    rng = np.random.default_rng(seed)
    theta, D, sig = map(np.asarray, (theta, D, sig))
    out = []
    for _ in range(n):
        i = rng.integers(0, len(D), len(D))
        if np.ptp(D[i]) == 0:
            continue
        out.append(wls(theta[i], D[i], sig[i])[1])
    return np.percentile(out, [2.5, 97.5]), len(out)


def p0(towns):
    th = [t["theta_deg"] for t in towns]; D = [t["D_year"] for t in towns]
    n = len(towns)
    if n < 3:
        return {"n": n, "computable": False}
    r, p, how = perm_p(th, D)
    rho = stats.spearmanr(th, D).statistic
    loo = [float(np.corrcoef(np.delete(th, i), np.delete(D, i))[0, 1]) for i in range(n)]
    beta = wls(np.array(th), np.array(D, float), [t["sigma_theta_deg"] for t in towns])
    ci, nb = bootstrap_slope(th, np.array(D, float), [t["sigma_theta_deg"] for t in towns])
    passed = bool(p < 0.05 and rho > 0 and min(loo) > 0)
    return {"n": n, "computable": True, "pearson_r": finite(r, 4), "p_one_sided": finite(p, 6), "p_method": how,
            "spearman_rho": finite(rho, 4), "leave_one_out_min_r": finite(min(loo), 4),
            "leave_one_out_r": {t["town"]: finite(v, 4) for t, v in zip(towns, loo)},
            "wls_slope_deg_per_century": finite(beta[1] * 100, 4), "wls_intercept_deg": finite(beta[0], 4),
            "slope_ci95_deg_per_century": [finite(ci[0] * 100, 4), finite(ci[1] * 100, 4)], "bootstrap_resamples_used": nb,
            "passes": passed, "decided": n >= 8}


def stage2(a):
    stars = astro.load_stars()
    choice_text = Path(a.choice).read_text(encoding="utf-8")
    recorded = Path(a.choice).with_suffix(".sha256").read_text(encoding="utf-8").split()[0]
    if hashlib.sha256(choice_text.encode("utf-8")).hexdigest() != recorded:
        raise SystemExit("stage-1 choice does not match its recorded hash")
    choice = json.loads(choice_text)
    table, towns, horizons = load(a.table, a.horizons)
    conf = [t for t in towns if t["town"] not in DISCOVERY]
    disc = [t for t in towns if t["town"] in DISCOVERY]
    res = {"schema_version": "1.0", "task": "town-axes-stage2", "synthetic": False,
           "n_all": len(towns), "n_confirmation": len(conf), "chosen_target": choice["chosen_target"]}
    # P0
    res["P0_all"] = p0(towns)
    res["P0_confirmation"] = p0(conf)
    # Model slopes for P1
    th = np.array([t["theta_deg"] for t in towns]); D = np.array([t["D_year"] for t in towns], float)
    sig = np.array([t["sigma_theta_deg"] for t in towns])
    alc = [model("alcyone", t, horizons, stars) for t in towns]
    ald = [model("aldebaran", t, horizons, stars) for t in towns]
    pred_alc = np.array([x[0] for x in alc])
    slope_pred = wls(pred_alc, D, sig)[1]
    ci = res["P0_all"].get("slope_ci95_deg_per_century") or [None, None]
    frac_pos = float(np.mean(th > 0)) if len(th) else None
    strongly_neg = [t["town"] for t in towns if t["theta_deg"] < -2 * t["sigma_theta_deg"]]
    contains = ci[0] is not None and ci[0] <= slope_pred * 100 <= ci[1]
    excl0 = ci[0] is not None and (ci[0] > 0 or ci[1] < 0)
    res["P1_pleiades"] = {"fraction_clockwise": finite(frac_pos, 4), "towns_below_minus_2_sigma": strongly_neg,
                          "model_slope_deg_per_century": finite(slope_pred * 100, 4), "fitted_slope_ci95": ci,
                          "ci_contains_model_slope": bool(contains), "ci_excludes_zero": bool(excl0),
                          "passes": bool(frac_pos is not None and frac_pos >= 0.8 and not strongly_neg and contains and excl0),
                          "per_town": [{"town": t["town"], "theta_obs": t["theta_deg"], "theta_alcyone": finite(x[0], 4)} for t, x in zip(towns, alc)]}
    # P2
    eligible = [(t, x[0]) for t, x in zip(towns, ald) if x[0] is not None and abs(x[0]) > 0.5]
    match = [np.sign(t["theta_deg"]) == np.sign(p) for t, p in eligible]
    res["P2_aldebaran"] = {"n_eligible": len(eligible), "fraction_sign_match": finite(np.mean(match), 4) if match else None,
                           "passes": bool(len(eligible) >= 8 and np.mean(match) >= 0.8) if match else False,
                           "per_town": [{"town": t["town"], "theta_obs": t["theta_deg"], "theta_aldebaran": finite(p, 4), "sign_match": bool(m)} for (t, p), m in zip(eligible, match)]}
    # P3
    target = choice["chosen_target"]
    terms = chi2_terms(conf, target, horizons, stars)
    const = sum(t["theta_deg"] / (t["sigma_theta_deg"] ** 2 + SIGMA_INT ** 2) for t in disc) / sum(1 / (t["sigma_theta_deg"] ** 2 + SIGMA_INT ** 2) for t in disc)
    var0 = [t["sigma_theta_deg"] ** 2 + SIGMA_INT ** 2 for t in conf]
    chi_card = [t["theta_deg"] ** 2 / v for t, v in zip(conf, var0)]
    chi_const = [(t["theta_deg"] - const) ** 2 / v for t, v in zip(conf, var0)]
    chi_star = [x["chi2"] for x in terms]
    n = len(conf)
    loo = []
    for i in range(n):
        s, c, k = sum(chi_star) - chi_star[i], sum(chi_card) - chi_card[i], sum(chi_const) - chi_const[i]
        loo.append(bool(s < c and s < k))
    p_fit = float(stats.chi2.sf(sum(chi_star), n)) if n else None
    res["P3_chosen_target"] = {"target": target, "n": n, "chi2_target": finite(sum(chi_star), 4),
                               "chi2_cardinal": finite(sum(chi_card), 4), "chi2_constant_offset": finite(sum(chi_const), 4),
                               "constant_offset_deg": finite(const, 4), "chi2_probability_target": finite(p_fit, 6),
                               "ordering_survives_leave_one_out": bool(all(loo)) if loo else None,
                               "passes": bool(n > 0 and sum(chi_star) < sum(chi_card) and sum(chi_star) < sum(chi_const) and p_fit > 0.05),
                               "per_town": [{**x, "chi2": finite(x["chi2"], 4)} for x in terms]}
    # Power (no measured deviation used)
    res["power"] = power(towns, horizons, stars)
    # D1
    md = next((t for t in towns if t["town"] == "mohenjo-daro"), None)
    if md:
        s2 = 2 * md["sigma_theta_deg"]
        res["D1_mohenjo_daro"] = {"theta": md["theta_deg"], "sigma": md["sigma_theta_deg"],
                                  "wanzke_tables_7_2_within_2_sigma": bool(abs(md["theta_deg"] - 7.2) <= s2),
                                  "wanzke_p37_1_to_2_within_2_sigma": bool(min(abs(md["theta_deg"] - x) for x in np.linspace(1, 2, 101)) <= s2)}
    # Credence
    P0 = res["P0_all"]
    if P0.get("computable") and P0["decided"] and not P0["passes"]:
        cred, status = 0.02, "dead"
    elif P0.get("computable") and P0["decided"] and P0["passes"]:
        cred, status = (0.40, "strengthened") if res["P3_chosen_target"]["passes"] else (0.15, "open")
    else:
        cred, status = 0.10, "open"
    res["credence_rule"] = {"prior": 0.10, "posterior": cred, "status": status}
    res["provenance"] = provenance([a.table, a.horizons, a.choice, BASE / "stars-v1.json"], CODE)
    print(write_new(a.out, res))


def power(towns, horizons, stars, nsim=20000, nperm=1999, seed=20261021):
    """P0 pass rate when deviations follow the Alcyone model with the towns' dates and errors."""
    n = len(towns)
    if n < 3:
        return None
    D = np.array([t["D_year"] for t in towns], float)
    sD = np.array([t["sigma_D"] for t in towns], float)
    sT = np.array([t["sigma_theta_deg"] for t in towns], float)
    base = np.array([model("alcyone", t, horizons, stars)[0] for t in towns])
    rate = np.array([model("alcyone", t, horizons, stars)[1] for t in towns])
    rng = np.random.default_rng(seed)
    Dc = (D - D.mean()) / np.linalg.norm(D - D.mean())
    perms = np.argsort(rng.random((nperm, n)), axis=1)
    PD = Dc[perms]
    passes = 0
    for _ in range(nsim):
        true = D + rng.normal(0, sD)
        th = base + rate * (true - D) + rng.normal(0, np.sqrt(sT ** 2 + SIGMA_INT ** 2))
        tc = th - th.mean(); tc /= np.linalg.norm(tc)
        r0 = tc @ Dc
        p = (np.sum(PD @ tc >= r0 - 1e-12) + 1) / (nperm + 1)
        if p >= 0.05:
            continue
        if stats.spearmanr(th, D).statistic <= 0:
            continue
        ok = True
        for i in range(n):
            if np.corrcoef(np.delete(th, i), np.delete(D, i))[0, 1] <= 0:
                ok = False; break
        passes += ok
    return {"n_sim": nsim, "n_perm_per_sim": nperm, "p0_pass_rate": finite(passes / nsim, 4),
            "model": "Alcyone deviation at each town's layout date plus Gaussian date, measurement and builders' errors"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["stage1", "stage2"])
    ap.add_argument("--table", required=True); ap.add_argument("--horizons", required=True)
    ap.add_argument("--choice"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    stage1(a) if a.stage == "stage1" else stage2(a)


if __name__ == "__main__":
    main()
