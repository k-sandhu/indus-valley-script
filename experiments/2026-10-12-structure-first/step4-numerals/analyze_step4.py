"""Step 4: do the stroke numerals behave like counts or like fixed lexical numbers?

Usage: python -X utf8 analyze_step4.py --out <run_dir>

Implements PROTOCOL.md step 4. IVS numeral tokens are codes in the short-stroke
(B001) and tall-stroke (B031) families with a count in the coding table; the
item is the next sign in reading order. Ur III items are the next non-numeral
word after a numeral; Linear B items are the logogram before a numeral.
"""
import argparse
import collections
import json
import math
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402

MIN_ITEM = 5


def entropy(c):
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else 0.0


def mutual_information(pairs):
    v = collections.Counter(a for a, _ in pairs)
    x = collections.Counter(b for _, b in pairs)
    j = collections.Counter(pairs)
    return entropy(v) + entropy(x) - entropy(j)


def measures(pairs):
    """pairs: list of (value, item). Returns item-level and corpus-level measures."""
    by_item = collections.defaultdict(collections.Counter)
    for val, item in pairs:
        by_item[item][val] += 1
    nvals = len({v for v, _ in pairs})
    q = {i: c for i, c in by_item.items() if sum(c.values()) >= MIN_ITEM}
    rows = []
    for i, c in q.items():
        n = sum(c.values())
        rows.append({"item": i, "tokens": n, "distinct_values": len(c),
                     "norm_entropy": entropy(c) / math.log2(nvals) if nvals > 1 else 0.0,
                     "top_value_share": c.most_common(1)[0][1] / n, "top_value": c.most_common(1)[0][0]})
    hv = entropy(collections.Counter(v for v, _ in pairs))
    mi = mutual_information(pairs)
    tok = sum(r["tokens"] for r in rows)
    return {"tokens": len(pairs), "distinct_values": nvals, "qualifying_items": len(rows),
            "qualifying_tokens": tok,
            "mean_distinct_values_per_item": float(np.mean([r["distinct_values"] for r in rows])) if rows else None,
            "token_weighted_top_value_share": (sum(r["top_value_share"] * r["tokens"] for r in rows) / tok) if tok else None,
            "mean_norm_entropy": float(np.mean([r["norm_entropy"] for r in rows])) if rows else None,
            "value_entropy_bits": hv, "mutual_information_bits": mi,
            "mi_over_value_entropy": mi / hv if hv else None, "items": sorted(rows, key=lambda r: -r["tokens"])}


def mi_null(pairs, rng, perms=10000):
    vals = np.array([v for v, _ in pairs], dtype=object)
    items = [i for _, i in pairs]
    obs = mutual_information(pairs)
    null = []
    for _ in range(perms):
        p = rng.permutation(len(vals))
        null.append(mutual_information(list(zip(vals[p], items))))
    null = np.array(null)
    return {"observed": obs, "null_mean": float(null.mean()), "null_p95": float(np.quantile(null, .95)),
            "p_value": float((1 + (null >= obs).sum()) / (1 + perms))}


def jsd(a, b):
    keys = set(a) | set(b)
    na, nb = sum(a.values()), sum(b.values())
    P = np.array([a[k] / na for k in keys])
    Q = np.array([b[k] / nb for k in keys])
    M = (P + Q) / 2
    def kl(x, y):
        m = x > 0
        return float((x[m] * np.log2(x[m] / y[m])).sum())
    return 0.5 * kl(P, M) + 0.5 * kl(Q, M)


def ivs_pairs(texts, coding):
    pairs = []
    fam_pairs = []
    for t in texts:
        for i, s in enumerate(t):
            row = coding.get(s)
            if row and row["base"] in ("B001", "B031") and row["count"]:
                item = t[i + 1] if i + 1 < len(t) else "</s>"
                if coding.get(item, {}).get("base") in ("B001", "B031"):
                    continue  # numeral followed by numeral: not an item
                pairs.append((int(row["count"]), item))
                fam_pairs.append((row["base"], item))
    return pairs, fam_pairs


def ur3_pairs(recs):
    pairs = []
    for r in recs:
        if r["corpus"] != "sumerian" or r["kind"] != "whole_tablet":
            continue
        w, g = r["words"], r["gold"]
        for i in range(len(w) - 1):
            if g[i] == "NUMBER" and g[i + 1] != "NUMBER":
                m = w[i].split("(")[0]
                if m.isdigit():
                    pairs.append((int(m), w[i + 1]))
    return pairs


def linb_pairs(recs):
    pairs = []
    for r in recs:
        if r["corpus"] != "mycenaean" or r["kind"] != "natural_line":
            continue
        w, g = r["words"], r["gold"]
        for i in range(1, len(w)):
            if g[i] == "NUMBER" and g[i - 1] == "LOGOGRAM" and w[i].isdigit():
                pairs.append((int(w[i]), w[i - 1]))
    return pairs


def subsample(pairs, n, rng, reps=200):
    out = []
    for _ in range(reps):
        s = rng.sample(pairs, min(n, len(pairs)))
        m = measures(s)
        out.append({k: m[k] for k in ("qualifying_items", "mean_distinct_values_per_item",
                                       "token_weighted_top_value_share", "mean_norm_entropy",
                                       "mi_over_value_entropy")})
    agg = {}
    for k in out[0]:
        vals = [o[k] for o in out if o[k] is not None]
        agg[k] = {"mean": float(np.mean(vals)), "p2_5": float(np.quantile(vals, .025)),
                  "p97_5": float(np.quantile(vals, .975))} if vals else None
    return agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(common.SEED + 4)
    prng = random.Random(common.SEED + 4)
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    items = common.load_clean()
    texts = [d["text"] for d in items]
    pairs, fam_pairs = ivs_pairs(texts, coding)
    summary = {"protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"),
               "coding_sha256": common.sha256(common.PROG / "step1-signs/sign_components_v1.tsv")}
    summary["ivs_clean"] = measures(pairs)
    summary["ivs_clean_mi_null"] = mi_null(pairs, rng)
    # short against tall following-sign distributions
    short = collections.Counter(i for f, i in fam_pairs if f == "B001")
    tall = collections.Counter(i for f, i in fam_pairs if f == "B031")
    obs = jsd(short, tall)
    labs = np.array([f for f, _ in fam_pairs])
    its = [i for _, i in fam_pairs]
    null = []
    for _ in range(10000):
        p = rng.permutation(labs)
        a = collections.Counter(i for f, i in zip(p, its) if f == "B001")
        b = collections.Counter(i for f, i in zip(p, its) if f == "B031")
        null.append(jsd(a, b))
    null = np.array(null)
    summary["short_vs_tall"] = {"short_tokens": sum(short.values()), "tall_tokens": sum(tall.values()),
                                "jsd_bits": obs, "null_mean": float(null.mean()),
                                "p_value": float((1 + (null >= obs).sum()) / (1 + len(null))),
                                "short_top_items": short.most_common(8), "tall_top_items": tall.most_common(8)}
    # sensitivity: all complete faces, distinct texts
    faces = common.read_jsonl(common.FACES)
    allt = sorted({tuple(f["signs_reading_rtl"]) for f in faces
                   if f["complete_observed"] and not f["has_unknown_sign"] and f["length"] > 0})
    p_all, _ = ivs_pairs(allt, coding)
    summary["ivs_all_faces"] = measures(p_all)
    summary["ivs_all_faces_mi_null"] = mi_null(p_all, rng, 2000)
    # comparisons
    recs = common.read_jsonl(common.BRONZE)
    u3 = ur3_pairs(recs)
    lb = linb_pairs(recs)
    summary["ur3_full"] = {k: v for k, v in measures(u3).items() if k != "items"}
    summary["ur3_full"]["top_items"] = measures(u3)["items"][:10]
    summary["linear_b_full"] = {k: v for k, v in measures(lb).items() if k != "items"}
    summary["linear_b_full"]["top_items"] = measures(lb)["items"][:10]
    n = len(pairs)
    summary["ur3_subsampled_to_ivs"] = subsample(u3, n, prng)
    summary["linear_b_subsampled_to_ivs"] = subsample(lb, n, prng) if len(lb) >= 50 else {"note": "fewer than 50 numeral-logogram pairs", "pairs": len(lb)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str) + "\n", encoding="utf-8")
    s = summary
    print(json.dumps({"ivs": {k: s["ivs_clean"][k] for k in ("tokens", "qualifying_items", "mean_distinct_values_per_item",
                                                            "token_weighted_top_value_share", "mi_over_value_entropy")},
                      "mi_null": s["ivs_clean_mi_null"], "short_vs_tall": {k: s["short_vs_tall"][k] for k in ("jsd_bits", "p_value")},
                      "ur3_sub": s["ur3_subsampled_to_ivs"], "linb": s["linear_b_full"].get("tokens")}, indent=0, default=str))


if __name__ == "__main__":
    main()
