"""Post-outcome planning: power of the frozen P0 if the eleven dated towns had true-north deviations.

Uses the exploratory table's dates and date errors, sets every deviation error to a stated value, and runs the
protocol's power simulation (Alcyone model plus Gaussian errors). No measured deviation enters the simulation.
"""
import argparse, copy
import astro, score
from common import BASE, finite, provenance, write_new

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--table", required=True); ap.add_argument("--horizons", required=True)
    ap.add_argument("--out", required=True); a = ap.parse_args()
    stars = astro.load_stars()
    _, towns, hz = score.load(a.table, a.horizons)
    res = {"schema_version": "1.0", "task": "town-axes-planning-power", "synthetic": True, "exploratory": True,
           "n_towns": len(towns), "towns": [t["town"] for t in towns], "scenarios": {}}
    for sig in (0.5, 1.0, 2.0):
        u = [dict(copy.deepcopy(t), sigma_theta_deg=sig) for t in towns]
        res["scenarios"][f"sigma_theta_{sig}"] = score.power(u, hz, stars, nsim=5000)
    res["provenance"] = provenance([a.table, a.horizons], [BASE / "planning_power.py", BASE / "score.py", BASE / "astro.py"])
    print(write_new(a.out, res))

if __name__ == "__main__":
    main()
