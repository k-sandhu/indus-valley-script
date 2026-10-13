"""Exploration 2: recurring texts, n-grams and edge segments by object group.

Full sign sequences are written only under data/raw/.../shot-b-reading/. The tracked
output discovery/segments_summary.json holds counts.
"""
import collections
import json

from common_b import DISC, RAW, UNKNOWN, ends, load_discovery, otype_group

rows = load_discovery()
RAW.mkdir(parents=True, exist_ok=True)

by_group_texts = collections.defaultdict(collections.Counter)   # complete faces, raw counts
distinct = collections.defaultdict(set)
for r in rows:
    si, ei = ends(r)
    seq = tuple(r["signs_reading_rtl"])
    if not seq or UNKNOWN in seq or not (si and ei):
        continue
    g = otype_group(r["object_type"])
    by_group_texts[g][seq] += 1
    distinct[g].add(seq)

ngr = {n: collections.defaultdict(collections.Counter) for n in (2, 3, 4)}
first2 = collections.defaultdict(collections.Counter)
last2 = collections.defaultdict(collections.Counter)
lengths = collections.defaultdict(collections.Counter)
for g, texts in distinct.items():
    for seq in texts:
        lengths[g][len(seq)] += 1
        for n in (2, 3, 4):
            for i in range(len(seq) - n + 1):
                ngr[n][g][seq[i:i + n]] += 1
        if len(seq) >= 3:
            first2[g][seq[:2]] += 1
            last2[g][seq[-2:]] += 1

out = {"top_texts": {}, "ngrams": {}, "first2": {}, "last2": {}}
for g, c in by_group_texts.items():
    out["top_texts"][g] = [["-".join(k), v] for k, v in c.most_common(40)]
for n in ngr:
    out["ngrams"][n] = {g: [["-".join(k), v] for k, v in c.most_common(60)] for g, c in ngr[n].items()}
out["first2"] = {g: [["-".join(k), v] for k, v in c.most_common(40)] for g, c in first2.items()}
out["last2"] = {g: [["-".join(k), v] for k, v in c.most_common(40)] for g, c in last2.items()}
(RAW / "segments_discovery.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

summary = {g: {"complete_faces": sum(by_group_texts[g].values()), "distinct_texts": len(distinct[g]),
               "length_distribution_distinct": dict(sorted(lengths[g].items()))} for g in distinct}
(DISC / "segments_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
