"""Write predictions.json: pass bounds for every pool size and the power of each prediction.

Usage: python -P experiments/2026-10-20-seal-legend-units/make_predictions.py --calibration <json> --out experiments/2026-10-20-seal-legend-units/predictions.json

Bounds come from beta-binomial predictive distributions (uniform prior, the held-set counts as
data) and, for the kill bound, from the within-legend shuffle null of the calibration. Bounds are
tabulated for pool sizes 1 to 400 so the scorer only looks them up. AMENDMENT-2.md fixes the
populations: P1 to P3 single-line seal legends, P4 divided seal legends.
"""
import argparse
import functools
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402
from calibrate import mcnemar_one_sided  # noqa: E402

mcnemar = functools.lru_cache(maxsize=None)(mcnemar_one_sided)

NMAX = 400
SIMS = 40000
SIZES = [10, 20, 30, 50, 80, 100, 150]
EXPECTED = {"cisi31": 50, "post_catalogue_20": 20, "post_catalogue_50": 50, "both_pools": 80}
# known divided seals, catalogue reading order (AMENDMENT-2.md): longer line ends in a stock closing
P4_KNOWN, P4_KNOWN_N, P4_CHANCE = 37, 59, 0.222
P4_MIN_FACES = 3


def bb_quantile(x, n_obs, n, q, rng):
    p = rng.beta(1 + x, 1 + n_obs - x, size=SIMS)
    return float(np.quantile(rng.binomial(n, p) / n, q))


def binom_tail(k, n, p):
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calibration", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    cal = json.loads(args.calibration.read_text(encoding="utf-8"))
    rng = np.random.default_rng(20261021)
    s1, s2, s3 = cal["S1_closing_coverage"], cal["S2_end_start_asymmetry"], cal["S3_opening_known_elsewhere"]
    n = cal["held_legends"]
    p1 = s1["count"] / n
    p0 = s1["shuffle_null_mean"]
    p3 = s3["held_known"] / s3["held_scored"]
    share3 = s3["share_of_legends_scored"]
    # S2 discordance structure on H: b legends with only the end pair known, c with only the start pair
    pb, pc = s2["discordant_end"] / n, s2["discordant_start"] / n

    bounds = {"P1": {"lower": {}, "kill": {}}, "P3": {"upper": {}}}
    for k in range(1, NMAX + 1):
        bounds["P1"]["lower"][str(k)] = bb_quantile(s1["count"], n, k, 0.025, rng)
        bounds["P1"]["kill"][str(k)] = float(np.quantile(rng.binomial(k, p0, size=SIMS) / k, 0.975))
        bounds["P3"]["upper"][str(k)] = bb_quantile(s3["held_known"], s3["held_scored"], k, 0.975, rng)

    def power_p1(k):
        lo = bounds["P1"]["lower"][str(k)]
        out = {"lower_bound": lo, "kill_bound": bounds["P1"]["kill"][str(k)]}
        for label, p in (("held_rate", p1), ("held_rate_minus_0.15", p1 - 0.15), ("held_rate_minus_0.25", p1 - 0.25),
                         ("shuffle_null", p0)):
            out[f"p_pass_if_{label}"] = float(np.mean(rng.binomial(k, p, size=SIMS) / k >= lo - 1e-12))
        return out

    def power_p2(k, sims=20000):
        def rate(qb, qc):
            draws = rng.multinomial(k, [qb, qc, 1 - qb - qc], size=sims)
            return float(np.mean([(b > c) and mcnemar(int(b), int(c)) < 0.05 for b, c, _ in draws]))
        half = (pb + pc) / 2
        return {"p_pass_if_held_rates": rate(pb, pc), "p_pass_if_half_the_asymmetry": rate(half + (pb - pc) / 4, half - (pb - pc) / 4),
                "p_pass_if_no_asymmetry": rate(half, half)}

    def power_p3(k_legends):
        k = max(1, int(round(k_legends * share3)))
        hi = bounds["P3"]["upper"][str(k)]
        out = {"openings_scored": k, "upper_bound": hi}
        for label, p in (("held_rate", p3), ("held_rate_plus_0.20", p3 + 0.20), ("formulaic_openings_0.9", 0.9)):
            out[f"p_pass_if_{label}"] = float(np.mean(rng.binomial(k, min(p, 1.0), size=SIMS) / k <= hi + 1e-12))
        return out

    def power_p4(k):
        need = next((j for j in range(k + 1) if j / k >= 0.5 and binom_tail(j, k, P4_CHANCE) < 0.05), None)
        if k < P4_MIN_FACES or need is None:
            return {"faces_needed_to_pass": None, "p_pass_if_known_rate": 0.0, "p_pass_if_chance": 0.0}
        return {"faces_needed_to_pass": need, "p_pass_if_known_rate": binom_tail(need, k, P4_KNOWN / P4_KNOWN_N),
                "p_pass_if_chance": binom_tail(need, k, P4_CHANCE)}

    power = {"P1": {"by_size": {str(k): power_p1(k) for k in SIZES}, "expected": {e: power_p1(k) for e, k in EXPECTED.items()}},
             "P2": {"by_size": {str(k): power_p2(k) for k in SIZES}, "expected": {e: power_p2(k) for e, k in EXPECTED.items()}},
             "P3": {"by_size": {str(k): power_p3(k) for k in SIZES}, "expected": {e: power_p3(k) for e, k in EXPECTED.items()}},
             "P4": {"by_faces": {str(k): power_p4(k) for k in (1, 2, 3, 4, 5, 6, 8, 10, 15, 20)}}}
    spec = {"frozen_version": cal["version"], "calibration_sha256": U.sha256(args.calibration),
            "statistic_families": ["seal_legend_closing_structure", "line_division_unit_boundary"],
            "held_values": {"P1_coverage": p1, "P1_shuffle_null": p0, "P2_end_known": s2["held_end_known"],
                            "P2_start_known": s2["held_start_known"], "P3_opening_known": p3,
                            "P4_known_divided_seals": P4_KNOWN / P4_KNOWN_N, "P4_chance": P4_CHANCE},
            "thresholds": {"P2_alpha": 0.05, "P4_min_faces": P4_MIN_FACES, "P4_share": 0.5, "P4_alpha": 0.05},
            "power": power, "bounds": bounds}
    U.write_json(args.out, spec)
    print(json.dumps(power, indent=1)[:7000])


if __name__ == "__main__":
    main()
