"""Synthetic positive and negative controls for score.py, written before any measured deviation was scored.

The positive control plants deviations from the Alcyone model at random latitudes and layout dates;
the negative control draws deviations around cardinal intent with no relation to date.
"""
import argparse
import json
from pathlib import Path

import numpy as np

import astro
from common import write_new

NAMES = ["mohenjo-daro", "harappa", "kalibangan"] + [f"synthetic-{i:02d}" for i in range(10)]
AZ = [round(float(x), 1) for x in list(np.arange(45, 135.0001, 0.1)) + list(np.arange(225, 315.0001, 0.1))]


def build(kind, seed):
    stars = astro.load_stars()
    rng = np.random.default_rng(seed)
    towns = []
    for n in NAMES:
        lat = float(rng.uniform(22, 31)); D = -float(rng.uniform(2000, 2700))
        if kind == "positive":
            th = astro.predicted_deviation("alcyone", D, lat, lambda a: 0.05, stars) + rng.normal(0, 1.2)
        else:
            th = rng.normal(0, 3.0)
        towns.append({"town": n, "lat": lat, "theta_deg": float(th), "sigma_theta_deg": 0.5, "D_year": D, "sigma_D": 150.0})
    hz = {"towns": [{"town": n, "profile": [{"az": a, "alt_deg": 0.05} for a in AZ]} for n in NAMES]}
    return {"schema_version": "1.0", "synthetic": True, "kind": kind, "seed": seed, "towns": towns}, hz


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", required=True); a = ap.parse_args()
    d = Path(a.dir)
    for kind, seed in (("positive", 1), ("negative", 2)):
        table, hz = build(kind, seed)
        print(kind, write_new(d / kind / "table.json", table), write_new(d / kind / "horizons.json", hz))


if __name__ == "__main__":
    main()
