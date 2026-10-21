"""Post-outcome check (exploratory): do the Mound F period signs behave alike elsewhere?

After the read, signs 806, 817 and 233 carried most of the inventory drift in Mound F
(absent or nearly absent from the early third), while 390 and 590 faded. This script
reports, for those signs and for legend length, the mean period rank in the discovery
seals (ranked within each frame) and the mean height rank in Mackay's DK-G seals at
Mohenjo-daro (both populations already examined), with a within-frame permutation
p-value for each sign's mean rank. Nothing here is confirmation.

    python -P experiments/2026-10-20-harappa-legend-periods/post_outcome_signs.py OUT_JSON
"""
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import period_stats as P  # noqa: E402
from period_stats import S  # noqa: E402

ROOT = PACKAGE.parents[1]
DISCOVERY = ROOT / "data/raw/2026-10-20-harappa-legend-periods/discovery-harappa-labelled.jsonl"
CONFIRMATION = ROOT / "data/raw/2026-10-20-harappa-legend-periods/confirmation-mound-f-vats.jsonl"
MACKAY = ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy/discovery-mackay1938.jsonl"
SIGNS = ("806", "817", "233", "900", "390", "590", "741")


def mackay_objects():
    out = []
    for r in P.read_rows(MACKAY):
        m = r["metadata"]
        if r["object_type"].startswith("SEAL") and m.get("strat_area") == "DK" and m.get("strat_height_ft") is not None:
            o = dict(r)
            o["text"] = P.edge_text_fields(r)
            o["stratum"] = "DK"
            out.append(o)
    ranks = S.average_ranks([o["metadata"]["strat_height_ft"] for o in out])
    for o, k in zip(out, ranks):
        o["u"] = (k - 0.5) / len(out)
    return out


def describe(objects, seed):
    rows = S.all_legends(objects)
    u = np.array([r["u"] for r in rows])
    out = {"legends": len(rows), "signs": {}}
    for k, s in enumerate(SIGNS):
        flag = np.array([s in set(r["signs"]) for r in rows], float)
        n = int(flag.sum())
        if n == 0:
            out["signs"][s] = {"legends": 0}
            continue
        res = S.permutation_test(rows, lambda v, f=flag: float((f * v).sum() / f.sum() - v.mean()), 9999, seed + k, "two-sided")
        out["signs"][s] = {"legends": n, "mean_u": float(u[flag > 0].mean()),
                           "by_third": [int(np.sum((flag > 0) & (np.array([P.third(x) for x in u]) == t))) for t in range(3)],
                           "p_two_sided": res["p"]}
    legends = P.length_units(objects)
    out["mean_length_by_third"] = [float(np.mean([r["value"] for r in legends if P.third(r["u"]) == t])) for t in range(3)]
    res = S.permutation_test(legends, S.stratified_spearman_factory([r["value"] for r in legends], legends), 9999, seed + 50, "two-sided")
    out["length_r"] = res["observed"]
    out["length_p_two_sided"] = res["p"]
    out["legends_by_third"] = [int(np.sum([P.third(x) == t for x in u])) for t in range(3)]
    return out


def main():
    out_path = Path(sys.argv[1])
    if out_path.exists():
        raise SystemExit("output exists")
    disc, _ = P.prepare(P.read_rows(DISCOVERY), "discovery")
    conf, _ = P.prepare(P.read_rows(CONFIRMATION), "confirmation")
    record = {"status": "exploratory, computed after the frozen read",
              "mound_f_confirmation": describe(conf, 300),
              "harappa_discovery": describe(disc, 400),
              "mohenjo_daro_dk_g": describe(mackay_objects(), 500)}
    out_path.write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(P.jsonable(record), indent=1))


if __name__ == "__main__":
    main()
