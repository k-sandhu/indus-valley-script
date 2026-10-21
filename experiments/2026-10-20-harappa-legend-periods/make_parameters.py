"""Derive the closing stock and write the parameters frozen with the predictions.

The closing stock is the union of two stocks defined by one rule (a sign closing at
least five legends of two or more signs, with at least half of its occurrences in final
position): the stock of Mackay's DK-G seals at Mohenjo-daro, frozen by the stratigraphy
package, and the stock of every Harappa seal outside the confirmation population. No
date enters the Harappa stock. Its out-of-sample share is estimated by deriving the
Harappa part on one random half of the pool and measuring the union on the other.

    python -P experiments/2026-10-20-harappa-legend-periods/make_parameters.py OUT_JSON CONSTANTS_JSON
"""
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import explore_discovery as E  # noqa: E402

DKG = E.DKG


def main():
    out_path, constants_path = Path(sys.argv[1]), Path(sys.argv[2])
    if out_path.exists():
        raise SystemExit("output exists")
    constants = json.loads(constants_path.read_text(encoding="utf-8"))
    pool = E.harappa_pool()
    dkg = json.loads(DKG.read_text(encoding="utf-8"))
    harappa, counts, _ = E.closing_stock(pool)
    union = sorted(set(dkg["closing_stock"]) | set(harappa), key=lambda s: (s not in dkg["closing_stock"], s))
    rng = np.random.default_rng(20261021)
    shares = []
    for _ in range(200):
        idx = rng.permutation(len(pool))
        a = [pool[i] for i in idx[: len(pool) // 2]]
        b = [pool[i] for i in idx[len(pool) // 2:]]
        stock_a, _, _ = E.closing_stock(a, min_final=3)
        shares.append(E.share(b, set(dkg["closing_stock"]) | set(stock_a))["share"])
    record = {
        "closing_stock": union,
        "closing_stock_sources": {"dkg": dkg["closing_stock"], "harappa_pool": harappa, "harappa_pool_counts": counts},
        "closing_stock_share_pool_in_sample": E.share(pool, set(union)),
        "closing_stock_share_pool_cross_validated": {"mean": float(np.mean(shares)), "quantiles_05_50_95": [float(x) for x in np.quantile(shares, [0.05, 0.5, 0.95])],
                                                     "rule": "Harappa part derived on a random half of the pool with the threshold scaled to 3 closing legends, union with DK-G, share on the other half; 200 splits"},
        "dkg_stock_share_pool": E.share(pool, set(dkg["closing_stock"])),
        "rules": {"closing_stock": "union of the DK-G stock (stratigraphy package, discovery-v2/frozen-parameters.json) and the Harappa pool stock: signs closing at least 5 legends of two or more signs whose closing is read, with at least half their occurrences in those legends final",
                  "pool": "every Harappa seal family outside Vats's Mound F stratified seals, legend chosen by build_inputs.legend_face, positions read by period_stats.edge_text_fields"},
    }
    record.update(constants)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k != "rules"}, indent=1))


if __name__ == "__main__":
    main()
