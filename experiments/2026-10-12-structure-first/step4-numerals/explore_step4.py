"""Step 4, post-outcome exploration (labelled Exploratory): item heterogeneity and the two-stroke question.

Usage: python -X utf8 explore_step4.py --out <run_dir>

Written after run-2026-10-12 showed that some following signs take a near-fixed
value while others take many. Three questions, none in the protocol:
1. How many qualifying items are near-fixed (top value share >= 0.8) in IVS,
   and how many in Ur III subsamples of the same size?
2. Do the frozen measures change when value 2 (codes 002, 012, 032) is excluded,
   since a pair of strokes may be a separate sign rather than a numeral?
3. Do short and tall strokes differ in how fixed their items are?
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402
from analyze_step4 import ivs_pairs, measures, ur3_pairs  # noqa: E402


def fixed_share(m, thr=0.8):
    rows = m["items"]
    return {"qualifying_items": len(rows), "near_fixed_items": sum(r["top_value_share"] >= thr for r in rows),
            "near_fixed_share": (sum(r["top_value_share"] >= thr for r in rows) / len(rows)) if rows else None,
            "spread_items_5plus_values": sum(r["distinct_values"] >= 5 for r in rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    texts = [d["text"] for d in common.load_clean()]
    pairs, fam = ivs_pairs(texts, coding)
    res = {"status": "Exploratory, post-outcome", "ivs": fixed_share(measures(pairs))}
    u3 = ur3_pairs(common.read_jsonl(common.BRONZE))
    rng = random.Random(common.SEED + 40)
    sub = [fixed_share(measures(rng.sample(u3, len(pairs)))) for _ in range(200)]
    res["ur3_subsampled"] = {k: {"mean": float(np.mean([s[k] for s in sub])),
                                 "p2_5": float(np.quantile([s[k] for s in sub], .025)),
                                 "p97_5": float(np.quantile([s[k] for s in sub], .975))}
                             for k in ("qualifying_items", "near_fixed_items", "near_fixed_share", "spread_items_5plus_values")}
    no2 = [(v, i) for v, i in pairs if v != 2]
    m2 = measures(no2)
    res["ivs_without_value_2"] = {k: m2[k] for k in ("tokens", "qualifying_items", "mean_distinct_values_per_item",
                                                     "token_weighted_top_value_share", "mi_over_value_entropy")}
    res["ivs_without_value_2"].update(fixed_share(m2))
    sub2 = []
    for _ in range(200):
        s = measures(rng.sample(u3, len(no2)))
        sub2.append({k: s[k] for k in ("mean_distinct_values_per_item", "token_weighted_top_value_share", "mi_over_value_entropy")})
    res["ur3_subsampled_to_without_2"] = {k: {"mean": float(np.mean([s[k] for s in sub2])),
                                              "p2_5": float(np.quantile([s[k] for s in sub2], .025)),
                                              "p97_5": float(np.quantile([s[k] for s in sub2], .975))} for k in sub2[0]}
    for famname in ("B001", "B031"):
        fp = [(v, i) for (v, i), (f, _) in zip(pairs, fam) if f == famname]
        mm = measures(fp)
        res[f"family_{famname}"] = {k: mm[k] for k in ("tokens", "qualifying_items", "mean_distinct_values_per_item",
                                                      "token_weighted_top_value_share")}
        res[f"family_{famname}"].update(fixed_share(mm))
        res[f"family_{famname}"]["items"] = [{k: r[k] for k in ("item", "tokens", "distinct_values", "top_value", "top_value_share")}
                                             for r in mm["items"][:12]]
    vals = collections.Counter(v for v, _ in pairs)
    res["value_distribution"] = dict(sorted(vals.items()))
    (out / "summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("family")}, indent=0))
    for f in ("family_B001", "family_B031"):
        print(f, {k: res[f][k] for k in res[f] if k != "items"})


if __name__ == "__main__":
    main()
