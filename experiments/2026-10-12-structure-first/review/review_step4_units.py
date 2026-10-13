"""Adversarial review, step 4 supplement: both corpora with system-distinguished values.

Usage: python -X utf8 review_step4_units.py --out <new dir under data/raw/2026-10-12-structure-first/>

IVS value = stroke family plus count (short 3 differs from tall 3); Ur III value = digit plus
unit as written (1(u) differs from 1(diš) and 1(barig)). Frozen measures and the frozen
subsampling to the IVS token count are reused, together with the five-token rarefaction from
review_step4.py.
"""
import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step4-numerals"))
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import analyze_step4 as A  # noqa: E402
from review_step4 import band, rarefied  # noqa: E402


def ur3_unit_pairs(recs):
    pairs = []
    for r in recs:
        if r["corpus"] != "sumerian" or r["kind"] != "whole_tablet":
            continue
        w, g = r["words"], r["gold"]
        for i in range(len(w) - 1):
            if g[i] == "NUMBER" and g[i + 1] != "NUMBER" and w[i].split("(")[0].isdigit() and "(" in w[i]:
                pairs.append((w[i].split(")")[0] + ")", w[i + 1]))
    return pairs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--subs", type=int, default=200)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(common.SEED + 405)
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    texts = [d["text"] for d in common.load_clean()]
    pairs, fam = A.ivs_pairs(texts, coding)
    ivs = [(f"{f}:{v}", i) for (v, i), (f, _) in zip(pairs, fam)]
    u3 = ur3_unit_pairs(common.read_jsonl(common.BRONZE))
    keys = ("qualifying_items", "mean_distinct_values_per_item", "token_weighted_top_value_share", "mi_over_value_entropy")
    m = A.measures(ivs)
    res = {"ivs_family_and_count": {k: m[k] for k in keys}, "ivs_rarefied": rarefied(ivs, rng),
           "ur3_pairs": len(u3), "ur3_distinct_values": len({v for v, _ in u3})}
    subs = [A.measures(rng.sample(u3, len(ivs))) for _ in range(args.subs)]
    res["ur3_digit_and_unit_subsampled"] = {k: band([s[k] for s in subs]) for k in keys}
    rr = [rarefied(rng.sample(u3, len(ivs)), rng, reps=10) for _ in range(min(args.subs, 100))]
    res["ur3_digit_and_unit_rarefied"] = {k: band([r[k] for r in rr]) for k in ("distinct_values_in_5_tokens", "top_share_in_5_tokens")}
    print(json.dumps(res, indent=1))
    (out / "summary.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
