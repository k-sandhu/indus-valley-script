"""Split-half reliability of the per-sign period measures on the discovery seals.

For each kind of measure (a sign anywhere in the legend, an opening sign, a closing
sign) the discovery units are halved at random 500 times. Each half gives every sign
the mean period rank u of the legends that carry it; the correlation of those means
across signs with at least three units in both halves is the split-half reliability,
and a shrunken score learned on one half is correlated with u on the other half (the
transfer). Low values mean that a sign's period, as far as these seals show it, is
mostly noise; the drift tests then rest on the omnibus statistics, whose power is
stated separately.

    python -P experiments/2026-10-20-harappa-legend-periods/reliability.py OUT_JSON
"""
from collections import defaultdict
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


def keys(r, kind):
    return {s for s in r["signs"] if s != "000"} if kind == "any" else {r["value"]}


def split_half(units, kind, rng, rounds=500, min_units=3, k=5):
    rel, transfer = [], []
    for _ in range(rounds):
        idx = rng.permutation(len(units))
        a = [units[i] for i in idx[: len(units) // 2]]
        b = [units[i] for i in idx[len(units) // 2:]]

        def means(rows):
            acc = defaultdict(list)
            for r in rows:
                for s in keys(r, kind):
                    acc[s].append(r["u"])
            return {s: (float(np.mean(v)), len(v), (sum(v) + k * 0.5) / (len(v) + k)) for s, v in acc.items()}
        ma, mb = means(a), means(b)
        common = [s for s in ma if s in mb and ma[s][1] >= min_units and mb[s][1] >= min_units]
        if len(common) >= 4:
            rel.append(np.corrcoef([ma[s][0] for s in common], [mb[s][0] for s in common])[0, 1])
        pairs = [(np.mean([ma[s][2] for s in keys(r, kind) if s in ma]), r["u"]) for r in b if any(s in ma for s in keys(r, kind))]
        if len(pairs) > 3:
            x, y = np.array(pairs).T
            if x.std() > 0:
                transfer.append(np.corrcoef(x, y)[0, 1])
    rel, transfer = np.array(rel), np.array(transfer)
    out = {"rounds": rounds, "rounds_with_four_common_signs": int(len(rel)),
           "transfer_r_mean": float(transfer.mean()), "transfer_r_sd": float(transfer.std()),
           "transfer_share_positive": float((transfer > 0).mean())}
    if len(rel):
        out.update({"per_sign_split_half_r": float(np.nanmean(rel)),
                    "spearman_brown": float(2 * np.nanmean(rel) / (1 + np.nanmean(rel)))})
    return out


def main():
    out_path = Path(sys.argv[1])
    if out_path.exists():
        raise SystemExit("output exists")
    objects, frames = P.prepare(P.read_rows(DISCOVERY), "discovery")
    rng = np.random.default_rng(13)
    record = {"seals": len(objects), "frames": frames,
              "any_position": split_half(S.all_legends(objects), "any", rng),
              "opening": split_half(P.position_units(objects, "opening"), "slot", rng),
              "closing": split_half(P.position_units(objects, "closing"), "slot", rng),
              "reference_mohenjo_daro": "experiments/2026-10-20-mohenjo-daro-stratigraphy/discovery-v2/exploration.json, split_half (Mackay DK-G, 625 seals)"}
    out_path.write_text(json.dumps(P.jsonable(record), indent=2) + "\n", encoding="utf-8")
    print(json.dumps(P.jsonable(record), indent=1))


if __name__ == "__main__":
    main()
