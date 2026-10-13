"""Simulated power of the frozen confirmation statistics (exploration step E7b).

Fake confirmation halves are drawn by resampling discovery components with replacement,
keeping each seal's type, site, length and signs. Residual sizes are then generated as
  effect + normal noise with the discovery residual SD,
where the effect is +delta for seals whose last sign is in the high set and zero
otherwise. delta = 0 is the null; delta = 0.36 is the mean held-out residual of the high
set in the split-half rehearsal (power-split.json); delta = 0.66 is the in-sample
discovery value. P1a, P1b, P1c and P4 are computed as in confirm.py, with fewer
permutations. Output: discovery/power-sim.json.
"""
from pathlib import Path
import json
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from shots_common import load_half  # noqa: E402
from seal_table import seal_table  # noqa: E402
import rank_lib as L  # noqa: E402
from power_split import ratio_difference_p  # noqa: E402


def run(reps=200, nperm=299, seed=7):
    rng = np.random.default_rng(seed)
    pop = L.representative(L.size_text_population(seal_table(load_half("discovery"))))
    res0, _ = L.residualize(pop)
    sd = float(res0.std())
    lex = json.loads((HERE / "discovery" / "lexicon.json").read_text(encoding="utf-8"))
    H = set(lex["high_set"])
    sc = lex["closing_scores_last"]
    out = {"stage": "exploration E7b, simulation on resampled discovery seals", "reps": reps,
           "permutations_per_test": nperm, "residual_sd": sd, "scenarios": []}
    for delta in (0.0, 0.36, 0.66):
        passes = {"P1a": 0, "P1b": 0, "P1c": 0, "P4": 0, "P4_untestable": 0}
        nh = []
        for _ in range(reps):
            B = [pop[i] for i in rng.integers(0, len(pop), len(pop))]
            st = L.strata_of(B)
            last = [t["last"] for t in B]
            res = rng.normal(0, sd, len(B)) + delta * np.array([l in H for l in last], float)
            if L.between_ratio_test(last, res, st, 3, nperm, rng)["p_one_sided"] < 0.05:
                passes["P1a"] += 1
            rb = L.rearrangement_test(last, res, sc, lex["score_bins"], nperm, rng)
            if rb["r"] > 0 and rb["p_one_sided"] < 0.05:
                passes["P1b"] += 1
            if ratio_difference_p(B, res, st, nperm, rng) < 0.05:
                passes["P1c"] += 1
            c = L.contrast_test(["H" if l in H else "O" for l in last], res, st, {"H"}, {"O"}, nperm, rng)
            nh.append(c["n_high"])
            if c["n_high"] < 5:
                passes["P4_untestable"] += 1
            elif c["p_one_sided"] < 0.05:
                passes["P4"] += 1
        out["scenarios"].append({"delta": delta, "pass_rates": {k: v / reps for k, v in passes.items()},
                                 "median_high_seals": float(np.median(nh))})
    return out


if __name__ == "__main__":
    s = run()
    (HERE / "discovery" / "power-sim.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    print(json.dumps(s, indent=1))
