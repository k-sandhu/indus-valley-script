"""Power of the frozen decision rules before any Tamil compound is looked up.

Parpola's hits are simulated as Binomial(N, k * r) for N templates whose random-word
hit rate is r, for effect sizes k (k = 1: his words do no better than random words).
Each simulated outcome is scored with the frozen rules of PROTOCOL.md: the ratio of hit
rates, its bootstrap interval over templates and the leave-one-out influence criterion.

    python experiments/2026-10-22-rebus-blind-templates/code/power.py OUT.json
"""
import json
import sys
from pathlib import Path

import numpy as np

SEED = 20261022
SIMS = 2000
BOOT = 2000


def decide(h, r, rng, boot=BOOT):
    """h: 0/1 hits per template; r: random-word hit rate per template."""
    n = len(h)
    R = r.sum()
    ratio = h.sum() / R if R > 0 else float("inf")
    idx = rng.integers(0, n, (boot, n))
    rs = r[idx].sum(1)
    ratios = np.where(rs > 0, h[idx].sum(1) / np.where(rs > 0, rs, 1), np.inf)
    lo, hi = np.quantile(ratios, [0.025, 0.975])
    loo = [(h.sum() - h[i]) / (R - r[i]) if R - r[i] > 0 else float("inf") for i in range(n)]
    passed = ratio < 2 and max(loo) < 3
    killed = ratio >= 3 and lo > 1.5 and min(loo) >= 2
    return passed, killed


def main(out):
    out = Path(out)
    if out.exists():
        print("refusing to overwrite", out)
        return 1
    rng = np.random.default_rng(SEED)
    grid = []
    for n in (20, 30, 40, 60):
        for r0 in (0.02, 0.05, 0.10, 0.20, 0.30):
            for k in (1, 2, 3, 5):
                p = min(1.0, k * r0)
                passes = kills = 0
                sims = SIMS // 4  # the bootstrap inside each simulation dominates the cost
                for _ in range(sims):
                    h = (rng.random(n) < p).astype(float)
                    r = np.full(n, r0)
                    a, b = decide(h, r, rng, boot=500)
                    passes += a
                    kills += b
                grid.append({"templates": n, "random_rate": r0, "effect": k, "parpola_rate": p,
                             "simulations": sims, "p_pass": passes / sims, "p_kill": kills / sims})
    res = {"schema_version": "1.0", "task": "rebus-blind-templates/power", "synthetic": True,
           "parameters": {"seed": SEED, "bootstrap_per_simulation": 500,
                          "rule": "pass: ratio < 2 and every leave-one-out ratio < 3; kill: ratio >= 3, "
                                  "bootstrap 2.5% bound > 1.5 and every leave-one-out ratio >= 2"},
           "grid": grid}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for g in grid:
        if g["templates"] in (30, 40):
            print(g["templates"], g["random_rate"], g["effect"], round(g["p_pass"], 3), round(g["p_kill"], 3))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
