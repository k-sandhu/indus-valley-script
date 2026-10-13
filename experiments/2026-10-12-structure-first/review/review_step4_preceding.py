"""Adversarial review, step 4 supplement: item = preceding sign instead of following sign.

Usage: python -X utf8 review_step4_preceding.py --out <new dir under data/raw/2026-10-12-structure-first/>

Step 6 found the preceding sign carries at least as much excess information about the stroke
value as the following sign. This reruns the frozen step 4 measures with the preceding sign
(or text start) as the item, skipping numerals preceded by numerals, and compares with the
frozen following-sign definition and the frozen Ur III subsamples.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step4-numerals"))
import common  # noqa: E402
import analyze_step4 as A  # noqa: E402


def preceding_pairs(texts, coding):
    pairs = []
    for t in texts:
        for i, s in enumerate(t):
            row = coding.get(s)
            if row and row["base"] in ("B001", "B031") and row["count"]:
                item = t[i - 1] if i > 0 else "<s>"
                if coding.get(item, {}).get("base") in ("B001", "B031"):
                    continue
                pairs.append((int(row["count"]), item))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    texts = [d["text"] for d in common.load_clean()]
    keys = ("tokens", "qualifying_items", "mean_distinct_values_per_item", "token_weighted_top_value_share",
            "mi_over_value_entropy")
    fol, _ = A.ivs_pairs(texts, coding)
    pre = preceding_pairs(texts, coding)
    rng = np.random.default_rng(common.SEED + 408)
    res = {}
    for name, p in (("following_frozen_definition", fol), ("preceding", pre)):
        m = A.measures(p)
        res[name] = {k: m[k] for k in keys}
        res[name]["near_fixed_items_0.8"] = sum(r["top_value_share"] >= 0.8 for r in m["items"])
        mn = A.mi_null(p, rng, 2000)
        res[name]["net_mi_over_value_entropy"] = (mn["observed"] - mn["null_mean"]) / m["value_entropy_bits"]
        res[name]["top_items"] = [{k: r[k] for k in ("item", "tokens", "distinct_values", "top_value", "top_value_share")}
                                  for r in m["items"][:8]]
    print(json.dumps(res, indent=1))
    (out / "summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
