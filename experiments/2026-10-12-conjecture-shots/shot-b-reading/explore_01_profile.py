"""Exploration 1: profile every sign on the discovery half.

Writes discovery/sign_profile.tsv (aggregate counts per sign) and
discovery/profile_summary.json. No withheld field is loaded.
"""
import collections
import json
import math

from common_b import (DISC, UNKNOWN, components_table, ends, load_discovery, mayig_descriptions,
                      otype_group, prior_meanings)

rows = load_discovery()
comp = components_table()
desc = mayig_descriptions()
prior = prior_meanings()
NUMERAL = {c for c, r in comp.items() if r["base"] in ("B001", "B031")}

tok = collections.Counter()
tok_type = collections.defaultdict(collections.Counter)
faces_with = collections.Counter()
for r in rows:
    g = otype_group(r["object_type"])
    for s in r["signs_reading_rtl"]:
        if s == UNKNOWN:
            continue
        tok[s] += 1
        tok_type[s][g] += 1
    for s in set(r["signs_reading_rtl"]):
        faces_with[s] += 1

# distinct intact single-line texts, keyed by sequence and object group
distinct = {}
for r in rows:
    si, ei = ends(r)
    seq = tuple(r["signs_reading_rtl"])
    if not (r["single_line"] and si and ei) or UNKNOWN in seq or not seq:
        continue
    distinct.setdefault((otype_group(r["object_type"]), seq), r)

pos = collections.defaultdict(collections.Counter)
prev_ = collections.defaultdict(collections.Counter)
next_ = collections.defaultdict(collections.Counter)
dist_tok = collections.Counter()
after_num = collections.Counter()
before_num = collections.Counter()
lens = collections.defaultdict(list)
for (g, seq), r in distinct.items():
    n = len(seq)
    for i, s in enumerate(seq):
        dist_tok[s] += 1
        lens[s].append(n)
        if n == 1:
            pos[s]["solo"] += 1
        elif i == 0:
            pos[s]["initial"] += 1
        elif i == n - 1:
            pos[s]["final"] += 1
        else:
            pos[s]["medial"] += 1
        p = seq[i - 1] if i > 0 else "^"
        q = seq[i + 1] if i < n - 1 else "$"
        prev_[s][p] += 1
        next_[s][q] += 1
        if p in NUMERAL:
            after_num[s] += 1
        if q in NUMERAL:
            before_num[s] += 1


def entropy(c):
    t = sum(c.values())
    return -sum(v / t * math.log2(v / t) for v in c.values() if v) if t else 0.0


cols = ["code", "tokens", "faces", "distinct_tokens", "SEAL", "TAB:B", "TAB:I", "TAB:C", "POT", "TAG", "OTHER",
        "initial", "medial", "final", "solo", "mean_len", "after_numeral", "before_numeral",
        "top_prev", "top_next", "prev_entropy", "next_entropy", "base", "mods", "count", "mayig", "prior_meaning"]
lines = ["\t".join(cols)]
for s, n in tok.most_common():
    c = comp.get(s, {})
    tp = ",".join(f"{a}:{b}" for a, b in prev_[s].most_common(4))
    tn = ",".join(f"{a}:{b}" for a, b in next_[s].most_common(4))
    vals = [s, n, faces_with[s], dist_tok[s]] + [tok_type[s][g] for g in ("SEAL", "TAB:B", "TAB:I", "TAB:C", "POT", "TAG", "OTHER")]
    vals += [pos[s][k] for k in ("initial", "medial", "final", "solo")]
    vals += [round(sum(lens[s]) / len(lens[s]), 2) if lens[s] else "", after_num[s], before_num[s], tp, tn,
             round(entropy(prev_[s]), 2), round(entropy(next_[s]), 2), c.get("base", ""), c.get("mods", ""),
             c.get("count", ""), desc.get(s, ""), (prior.get(s) or {}).get("meaning", "")]
    lines.append("\t".join(str(v).replace("\t", " ") for v in vals))
(DISC / "sign_profile.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")

summary = {
    "faces": len(rows),
    "tokens_known": sum(tok.values()),
    "sign_types": len(tok),
    "signs_with_10_or_more_tokens": sum(1 for v in tok.values() if v >= 10),
    "tokens_in_signs_10_plus": sum(v for v in tok.values() if v >= 10),
    "distinct_intact_single_line_texts": len(distinct),
    "faces_by_object_group": collections.Counter(otype_group(r["object_type"]) for r in rows),
}
(DISC / "profile_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
