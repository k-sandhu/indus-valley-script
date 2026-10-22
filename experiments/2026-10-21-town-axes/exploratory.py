"""Secondary analysis of AMENDMENT-1.md: plan-based deviations for towns without a primary (imagery) value.

python exploratory.py --table table-v1/settlement-axes.json --out exploratory-v1/table.json
The extended table is then scored with score.py stage1 and stage2 into exploratory-v1/.
"""
from pathlib import Path
import argparse
import json
import math

from common import BASE, finite, provenance, write_new

FLOOR = 0.3


def plan_main_values(t):
    """Each plan measurer's declared main system, relative to its own arrow; magnetic plans IGRF-corrected when possible."""
    out = []
    for p in t.get("plans", []):
        if not p.get("is_main") or p.get("deviation_deg") is None:
            continue
        v = p["deviation_deg"]
        if p.get("north_reference") == "magnetic" and p.get("deviation_true_igrf_deg") is not None:
            v = p["deviation_true_igrf_deg"]
        out.append({"role": p["role"], "value": v, "se": p.get("se_deg"), "north_reference": p.get("north_reference"), "part": p.get("part")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    table = json.loads(Path(a.table).read_text(encoding="utf-8"))
    deltas = []
    for t in table["towns"]:
        if t.get("theta_deg") is None or not str(t.get("theta_basis", "")).startswith("imagery"):
            continue
        for p in plan_main_values(t):
            deltas.append({"town": t["town"], "role": p["role"], "north_reference": p["north_reference"], "plan_part": p["part"],
                           "delta_deg": p["value"] - t["theta_deg"]})
    n_towns = len({d["town"] for d in deltas})
    if n_towns >= 3:
        bias = sum(d["delta_deg"] for d in deltas) / len(deltas)
        s_delta = math.sqrt(sum(d["delta_deg"] ** 2 for d in deltas) / len(deltas))
    else:
        bias, s_delta = None, 3.0
    towns = []
    for t in table["towns"]:
        u = dict(t)
        if t.get("theta_deg") is None:
            vals = plan_main_values(t)
            if vals:
                w = [1 / max(v["se"] or FLOOR, 1e-3) ** 2 for v in vals]
                m = sum(v["value"] * wi for v, wi in zip(vals, w)) / sum(w)
                se = 1 / math.sqrt(sum(w))
                half = abs(vals[0]["value"] - vals[1]["value"]) / 2 if len(vals) == 2 else 0.0
                sig = math.sqrt(max(se, half, FLOOR) ** 2 + s_delta ** 2)
                u.update(theta_deg=finite(m, 4), sigma_theta_deg=finite(sig, 4),
                         theta_basis="plans, north not stated (Amendment 1)", plan_roles=[v["role"] for v in vals])
        towns.append(u)
    out = {"schema_version": "1.0", "task": "town-axes-exploratory-table", "synthetic": False, "exploratory": True,
           "rule": "AMENDMENT-1.md", "plan_north_calibration": {"n_differences": len(deltas), "n_towns": n_towns,
                                                                 "bias_deg": finite(bias, 4), "rms_deg": finite(s_delta, 4), "differences": [{**d, "delta_deg": finite(d["delta_deg"], 4)} for d in deltas]},
           "towns": towns, "provenance": provenance([Path(a.table)], [BASE / "exploratory.py", BASE / "common.py"])}
    print(write_new(a.out, out))


if __name__ == "__main__":
    main()
