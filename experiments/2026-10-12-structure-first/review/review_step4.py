"""Adversarial review, step 4: sample-size dependence, value definition and production series.

Usage: python -X utf8 review_step4.py --out <new dir under data/raw/2026-10-12-structure-first/>

1. Per-item measures rarefied to five tokens per qualifying item, so that items with many
   tokens do not show more distinct values merely because they have more tokens.
2. Mutual information net of its permutation mean (plug-in MI is biased upward by roughly
   (values-1)(items-1)/(2N ln 2)), divided by value entropy, for IVS and Ur III subsamples.
3. IVS with the text end removed as an item, and with value = (stroke family, count).
4. How the Ur III value is formed: units dropped, compound numbers truncated, ordinals kept.
5. Where the near-fixed combinations come from (sites and object types of the texts).
Imports the frozen step 4 functions unchanged.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step4-numerals"))
import common  # noqa: E402
import analyze_step4 as A  # noqa: E402


def rarefied(pairs, rng, n=5, reps=50):
    by = collections.defaultdict(list)
    for v, i in pairs:
        by[i].append(v)
    q = {i: v for i, v in by.items() if len(v) >= n}
    dv, ts = [], []
    for _ in range(reps):
        d, t = [], []
        for vals in q.values():
            s = rng.sample(vals, n)
            c = collections.Counter(s)
            d.append(len(c))
            t.append(c.most_common(1)[0][1] / n)
        dv.append(np.mean(d))
        ts.append(np.mean(t))
    return {"items": len(q), "distinct_values_in_5_tokens": float(np.mean(dv)), "top_share_in_5_tokens": float(np.mean(ts))}


def net_mi_ratio(pairs, nrng, perms=200):
    m = A.mi_null(pairs, nrng, perms)
    hv = A.entropy(collections.Counter(v for v, _ in pairs))
    return {"mi": m["observed"], "perm_mean": m["null_mean"], "value_entropy": hv,
            "raw_ratio": m["observed"] / hv, "net_ratio": (m["observed"] - m["null_mean"]) / hv,
            "items": len({i for _, i in pairs})}


def band(xs):
    return {"mean": float(np.mean(xs)), "p2_5": float(np.quantile(xs, .025)), "p97_5": float(np.quantile(xs, .975))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--subs", type=int, default=100)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rng = random.Random(common.SEED + 404)
    nrng = np.random.default_rng(common.SEED + 404)
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    items = common.load_clean()
    texts = [d["text"] for d in items]
    pairs, fam = A.ivs_pairs(texts, coding)
    recs = common.read_jsonl(common.BRONZE)
    u3 = A.ur3_pairs(recs)
    lb = A.linb_pairs(recs)
    res = {}

    # 1-2. rarefied item measures and net MI
    res["ivs"] = {"rarefied": rarefied(pairs, rng), "mi": net_mi_ratio(pairs, nrng, 1000)}
    rr, nm, raw = [], [], []
    for _ in range(args.subs):
        s = rng.sample(u3, len(pairs))
        r = rarefied(s, rng, reps=10)
        m = net_mi_ratio(s, nrng, 100)
        rr.append(r)
        nm.append(m["net_ratio"])
        raw.append(m["raw_ratio"])
    res["ur3_subsampled_to_ivs_tokens"] = {
        "subsamples": args.subs,
        "distinct_values_in_5_tokens": band([r["distinct_values_in_5_tokens"] for r in rr]),
        "top_share_in_5_tokens": band([r["top_share_in_5_tokens"] for r in rr]),
        "raw_mi_ratio": band(raw), "net_mi_ratio": band(nm)}
    res["linear_b_full"] = {"pairs": len(lb), "rarefied": rarefied(lb, rng), "mi": net_mi_ratio(lb, nrng, 1000)}
    print(json.dumps(res, indent=0), flush=True)

    # 3. definitions of item and value
    no_end = [(v, i) for v, i in pairs if i != "</s>"]
    famval = [(f"{f}:{v}", i) for (v, i), (f, _) in zip(pairs, fam)]
    for name, p in (("ivs_without_text_end_item", no_end), ("ivs_value_is_family_and_count", famval)):
        m = A.measures(p)
        res[name] = {k: m[k] for k in ("tokens", "qualifying_items", "mean_distinct_values_per_item",
                                       "token_weighted_top_value_share", "mi_over_value_entropy")}
        res[name]["near_fixed_items_0.8"] = sum(r["top_value_share"] >= 0.8 for r in m["items"])
        res[name]["net_mi"] = net_mi_ratio(p, nrng, 500)["net_ratio"]
    print(json.dumps({k: res[k] for k in ("ivs_without_text_end_item", "ivs_value_is_family_and_count")}), flush=True)

    # 4. Ur III value construction
    tot = unit_not_dis = compound = ordinal = 0
    units = collections.Counter()
    for r in recs:
        if r["corpus"] != "sumerian" or r["kind"] != "whole_tablet":
            continue
        w, g = r["words"], r["gold"]
        for i in range(len(w) - 1):
            if g[i] == "NUMBER" and g[i + 1] != "NUMBER" and w[i].split("(")[0].isdigit():
                tot += 1
                unit = w[i].split("(")[1].split(")")[0] if "(" in w[i] else ""
                units[unit] += 1
                unit_not_dis += unit != "diš"
                compound += i > 0 and g[i - 1] == "NUMBER"
                ordinal += "-kam" in w[i]
    res["ur3_value_construction"] = {"pairs": tot, "unit_other_than_dis": unit_not_dis,
                                     "last_token_of_compound_number": compound, "ordinal_kam": ordinal,
                                     "units": dict(units.most_common(12))}

    # 5. production context of near-fixed combinations
    ctx = {}
    want = {("520", 3), ("585", 7), ("803", 2), ("235", 2), ("806", 2)}
    for d in items:
        t = d["text"]
        for i, s in enumerate(t[:-1]):
            row = coding.get(s)
            if row and row["base"] in ("B001", "B031") and row["count"]:
                key = (t[i + 1], int(row["count"]))
                if key in want:
                    c = ctx.setdefault(f"{key[0]} after {key[1]}", {"texts": 0, "sites": collections.Counter(),
                                                                     "types": collections.Counter(), "families": 0})
                    c["texts"] += 1
                    c["families"] += len(d["families"])
                    for x in d["sites"]:
                        c["sites"][x] += 1
                    for x in d["types"]:
                        c["types"][x] += 1
    res["near_fixed_contexts"] = {k: {"texts": v["texts"], "object_families": v["families"],
                                      "sites": dict(v["sites"].most_common()), "types": dict(v["types"].most_common())}
                                  for k, v in ctx.items()}
    print(json.dumps({k: res[k] for k in ("ur3_value_construction", "near_fixed_contexts")}, indent=0), flush=True)
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
