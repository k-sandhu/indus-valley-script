"""Split-half rehearsal inside the discovery half (exploration step E7).

The discovery population is divided at random by component into a training half and a
test half, many times. Lexicons are built on the training half exactly as they will be
built on the full discovery half, and the candidate confirmation statistics are run on
the test half. The pass rates estimate how often each prediction would pass if the
discovery pattern were as real as it looks, with half the training data the final
lexicon will have. Output: discovery/power-split.json (aggregate rates only).
"""
from pathlib import Path
import collections
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from shots_common import load_half  # noqa: E402
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402

K, MIN_N = 3.0, 3
HIGH_CUT, LOW_CUT = 0.25, -0.10


def ratio_difference_p(B, res, st, nperm, rng, m=3):
    """Prediction 1c statistic on one sample: between-unit SS ratio of the last sign minus
    that of the first sign; whole texts permuted within strata."""
    sp = L.StratPerm(st)
    A = np.array([t["last"] for t in B], dtype=object)
    F = np.array([t["first"] for t in B], dtype=object)
    na, nf = [], []
    for _ in range(nperm):
        idx = sp.draw(rng)
        na.append(L.between_ss(list(A[idx]), res, m))
        nf.append(L.between_ss(list(F[idx]), res, m))
    na, nf = np.array(na), np.array(nf)
    d = L.between_ss(list(A), res, m) / na.mean() - L.between_ss(list(F), res, m) / nf.mean()
    dn = na / na.mean() - nf / nf.mean()
    return float((1 + (dn >= d).sum()) / (1 + nperm))


def run(reps=300, nperm=299, seed=20261012):
    rng = np.random.default_rng(seed)
    pop = L.representative(L.size_text_population(seal_table(load_half("discovery"))))
    out = {k: [] for k in ("p1a_last", "p1a_formula", "p1b_last_vs_first", "p4_last", "p1a_r_last",
                           "p1b_diff", "p4_diff", "p4_nh", "p4_nl", "p1a_first", "rearr_last",
                           "between_last_test_half", "ratio_diff_test_half", "p4_rest")}
    pooled = {"high": [], "low": [], "rest": []}
    picked_high, picked_low = collections.Counter(), collections.Counter()
    for rep in range(reps):
        side = rng.random(len(pop)) < 0.5
        A = [t for t, s in zip(pop, side) if s]
        B = [t for t, s in zip(pop, side) if not s]
        resA, _ = L.residualize(A)
        resB, _ = L.residualize(B)
        stB = L.strata_of(B)
        sc_last = L.shrunk_scores([t["last"] for t in A], resA, K, MIN_N)
        sc_form = L.shrunk_scores([t["formula"] for t in A], resA, K, MIN_N)
        sc_first = L.shrunk_scores([t["first"] for t in A], resA, K, MIN_N)
        t1 = L.score_correlation_test([t["last"] for t in B], resB, stB, sc_last, nperm, rng)
        t2 = L.score_correlation_test([t["formula"] for t in B], resB, stB, sc_form, nperm, rng)
        t0 = L.score_correlation_test([t["first"] for t in B], resB, stB, sc_first, nperm, rng)
        t3 = L.paired_score_difference_test([t["last"] for t in B], [t["first"] for t in B], resB, stB,
                                            sc_last, sc_first, nperm, rng)
        high = {u for u, v in sc_last.items() if v["score"] >= HIGH_CUT}
        low = {u for u, v in sc_last.items() if v["score"] <= LOW_CUT}
        picked_high.update(high)
        picked_low.update(low)
        for t, r in zip(B, resB):
            pooled["high" if t["last"] in high else "low" if t["last"] in low else "rest"].append(float(r))
        t4 = L.contrast_test([t["last"] for t in B], resB, stB, high, low, nperm, rng) if high and low else None
        ra = L.rearrangement_test([t["last"] for t in B], resB, sc_last, [[3, 4], [5, 9], [10, 29], [30, 100000]], nperm, rng)
        out["rearr_last"].append(ra["p_one_sided"])
        bt = L.between_ratio_test([t["last"] for t in B], resB, stB, 3, nperm, rng)
        out["between_last_test_half"].append(bt["p_one_sided"])
        out["ratio_diff_test_half"].append(ratio_difference_p(B, resB, stB, nperm, rng))
        if high:
            t5 = L.contrast_test(["H" if t["last"] in high else "O" for t in B], resB, stB, {"H"}, {"O"}, nperm, rng)
            if t5["difference"] is not None:
                out["p4_rest"].append(t5["p_one_sided"])
        out["p1a_last"].append(t1["p_one_sided"])
        out["p1a_r_last"].append(t1["r"])
        out["p1a_formula"].append(t2["p_one_sided"])
        out["p1a_first"].append(t0["p_one_sided"])
        out["p1b_last_vs_first"].append(t3["p_one_sided"])
        out["p1b_diff"].append(t3["difference"])
        if t4 and t4["difference"] is not None:
            out["p4_last"].append(t4["p_one_sided"])
            out["p4_diff"].append(t4["difference"])
            out["p4_nh"].append(t4["n_high"])
            out["p4_nl"].append(t4["n_low"])
    summary = {
        "stage": "exploration E7, discovery half only",
        "reps": reps, "permutations_per_test": nperm, "seed": seed,
        "population_components": len(pop), "k": K, "min_n": MIN_N,
        "high_cut": HIGH_CUT, "low_cut": LOW_CUT,
        "pass_rate_alpha_0.05": {
            "score_correlation_last_sign": float(np.mean(np.array(out["p1a_last"]) < 0.05)),
            "score_correlation_formula": float(np.mean(np.array(out["p1a_formula"]) < 0.05)),
            "score_correlation_first_sign": float(np.mean(np.array(out["p1a_first"]) < 0.05)),
            "closing_minus_opening_r": float(np.mean(np.array(out["p1b_last_vs_first"]) < 0.05)),
            "high_minus_low_contrast_last_sign": float(np.mean(np.array(out["p4_last"]) < 0.05)) if out["p4_last"] else None,
            "high_minus_rest_contrast_last_sign": float(np.mean(np.array(out["p4_rest"]) < 0.05)) if out["p4_rest"] else None,
            "rearrangement_calibration_last_sign": float(np.mean(np.array(out["rearr_last"]) < 0.05)),
            "between_unit_ss_last_sign_test_half_only": float(np.mean(np.array(out["between_last_test_half"]) < 0.05)),
            "closing_minus_opening_ratio_test_half_only": float(np.mean(np.array(out["ratio_diff_test_half"]) < 0.05)),
        },
        "reps_with_high_set_in_test": len(out["p4_rest"]),
        "median_test_r_last_sign": float(np.median(out["p1a_r_last"])),
        "median_closing_minus_opening_r": float(np.median(out["p1b_diff"])),
        "median_high_minus_low": float(np.median(out["p4_diff"])) if out["p4_diff"] else None,
        "median_n_high_test": float(np.median(out["p4_nh"])) if out["p4_nh"] else None,
        "median_n_low_test": float(np.median(out["p4_nl"])) if out["p4_nl"] else None,
        "reps_with_contrast": len(out["p4_last"]),
        "pooled_test_half_mean_residual": {k: {"seal_reps": len(v), "mean": float(np.mean(v)) if v else None} for k, v in pooled.items()},
        "training_half_picks_high": dict(picked_high.most_common()),
        "training_half_picks_low": dict(picked_low.most_common(15)),
    }
    return summary


if __name__ == "__main__":
    s = run()
    (HERE / "discovery").mkdir(exist_ok=True)
    (HERE / "discovery" / "power-split.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    print(json.dumps(s, indent=1))
