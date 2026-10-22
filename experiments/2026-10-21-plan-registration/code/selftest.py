"""Synthetic checks of the frozen fit, error model and sign conventions.

1. Sign test: a synthetic plan drawn at a known rotation, with an arrow to
   true north and a line of known true bearing, passed through the same
   mosaic and link code the registrars use; the recovered arrow bearing must
   be 0 and the line's true deviation must equal its input.
2. Coverage: 4,000 synthetic registrations per configuration with control
   points drawn from the classes of the protocol; we report how often the
   true rotation lies within 1 and 2 stated sigmas.
3. Misidentification: one control point moved to a wrong feature 60 m away;
   we report how often the acceptance rules reject the registration.
Writes one JSON file and refuses to overwrite it.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regfit  # noqa: E402
from register import convert_system  # noqa: E402

SEED = 20261021


def lonlat_to_px(lon, lat, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180.0) / 360.0 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def synthetic_link(rng, phi_true, m_per_px, classes, lat0=29.47, lon0=74.13, spread_m=200.0, z=18, noise=True,
                   wrong=None):
    """Build plan pixels and mosaic pixels for ground points; return link, plans, mosaics."""
    gm = regfit.ground_m_per_px(lat0, z)
    gx0, gy0 = lonlat_to_px(lon0, lat0, z)
    mosaic = {"zoom": z, "origin_global_px": [int(gx0) - 2000, int(gy0) - 2000], "ground_m_per_px": gm}
    n = len(classes)
    G = rng.uniform(-spread_m, spread_m, size=(n, 2))
    pts = []
    c, s = math.cos(math.radians(-phi_true)), math.sin(math.radians(-phi_true))
    for i, cl in enumerate(classes):
        e, nn = G[i]
        sig = regfit.CLASS_SIGMA_M[cl] / math.sqrt(2)
        pe, pn = (e, nn)
        ie, inn = (e, nn)
        if noise:
            pe, pn = e + rng.normal(0, sig), nn + rng.normal(0, sig)
            ie, inn = e + rng.normal(0, sig), nn + rng.normal(0, sig)
        if wrong is not None and i == wrong:
            ang = rng.uniform(0, 2 * math.pi)
            ie, inn = ie + 60 * math.cos(ang), inn + 60 * math.sin(ang)
        # plan: right-handed coordinates R(-phi) G / scale, then page pixels (x, -y) + offset
        X = (c * pe - s * pn) / m_per_px
        Y = (s * pe + c * pn) / m_per_px
        plan_px = [1000 + X, 1000 - Y]
        # imagery: ground metres to global pixels (local linearisation is exact enough over 1 km)
        mx = gx0 + ie / gm - mosaic["origin_global_px"][0]
        my = gy0 - inn / gm - mosaic["origin_global_px"][1]
        pts.append({"id": f"p{i}", "class": cl, "plan_px": plan_px, "mosaic": "m", "mosaic_px": [mx, my]})
    link = {"plan": "syn", "to": "map", "points": pts}
    plans = {"syn": {"scale_bar_m_per_px": m_per_px}}
    return link, plans, {"m": mosaic}


def sign_test():
    rng = np.random.default_rng(SEED)
    out = []
    for phi_true in (-17.0, -3.0, 0.0, 8.5, 31.0):
        link, plans, mosaics = synthetic_link(rng, phi_true, 0.5, ["A"] * 5, noise=False)
        r = regfit.fit_from_link(link, plans, mosaics, reveal_rotation=True)
        # An arrow drawn to true north has page azimuth phi_true (see regfit's docstring).
        arrow_page_az = phi_true
        alpha = regfit.wrap180(arrow_page_az - r["phi_deg"])
        # A line of true bearing 12.0 has page azimuth 12.0 + phi_true; relative to the arrow, 12.0.
        theta_plan = regfit.fold45((12.0 + phi_true) - arrow_page_az)
        th, _ = convert_system(theta_plan, 0.5, 0.3, alpha, r["sigma_phi_deg"])
        out.append({"phi_true_deg": phi_true, "phi_fit_deg": r["phi_deg"], "alpha_deg": alpha,
                    "theta_true_recovered_deg": th, "ok": abs(alpha) < 0.01 and abs(th - 12.0) < 0.01})
    return out


def coverage(n_trials=4000):
    rng = np.random.default_rng(SEED + 1)
    configs = {
        "3 points, class C, 200 m": (["C"] * 3, 200.0),
        "4 points, class C, 200 m": (["C"] * 4, 200.0),
        "4 points, classes A B C C, 300 m": (["A", "B", "C", "C"], 300.0),
        "6 points, classes B C, 300 m": (["B", "B", "B", "C", "C", "C"], 300.0),
        "5 points, class A, 100 m": (["A"] * 5, 100.0),
    }
    res = {}
    for name, (classes, spread) in configs.items():
        within1 = within2 = acc = 0
        sigmas = []
        for _ in range(n_trials):
            phi = rng.uniform(-30, 30)
            link, plans, mosaics = synthetic_link(rng, phi, 0.5, classes, spread_m=spread)
            r = regfit.fit_from_link(link, plans, mosaics, reveal_rotation=True)
            if not r["accepted"]:
                continue
            acc += 1
            d = abs(regfit.wrap180(r["phi_deg"] - phi))
            within1 += d <= r["sigma_phi_deg"]
            within2 += d <= 2 * r["sigma_phi_deg"]
            sigmas.append(r["sigma_phi_deg"])
        res[name] = {"trials": n_trials, "accepted": acc, "within_1_sigma": within1 / acc, "within_2_sigma": within2 / acc,
                     "median_sigma_phi_deg": float(np.median(sigmas))}
    return res


def misidentification(n_trials=2000):
    rng = np.random.default_rng(SEED + 2)
    res = {}
    for name, classes in {"4 points, class C": ["C"] * 4, "5 points, classes B C": ["B", "B", "C", "C", "C"]}.items():
        rej = 0
        bad_within2 = 0
        for _ in range(n_trials):
            phi = rng.uniform(-30, 30)
            link, plans, mosaics = synthetic_link(rng, phi, 0.5, classes, spread_m=200.0, wrong=0)
            r = regfit.fit_from_link(link, plans, mosaics, reveal_rotation=True)
            if not r["accepted"]:
                rej += 1
            elif abs(regfit.wrap180(r["phi_deg"] - phi)) <= 2 * r["sigma_phi_deg"]:
                bad_within2 += 1
        res[name] = {"trials": n_trials, "rejected_fraction": rej / n_trials,
                     "accepted_and_within_2_sigma_fraction": bad_within2 / n_trials}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists; write to a new path")
    here = Path(__file__).resolve().parent
    res = {"schema_version": "1.0", "task": "plan-registration-selftest", "synthetic": True, "seed": SEED,
           "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "sign_test": sign_test(), "coverage": coverage(), "misidentification_60m": misidentification(),
           "provenance": {"code": {f: hashlib.sha256((here / f).read_bytes()).hexdigest()
                                   for f in ("regfit.py", "register.py", "selftest.py")}}}
    res["sign_test_passes"] = all(r["ok"] for r in res["sign_test"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("sign_test_passes", "coverage", "misidentification_60m")}, indent=1))


if __name__ == "__main__":
    main()
