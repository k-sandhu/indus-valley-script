"""Exploration 3: substitution frames and paradigm classes among frequent signs.

Two signs share a frame when they occur with the same immediate left and right
neighbours (text edges count as neighbours) in distinct intact single-line texts. The
output lists, for each sign with at least ten discovery tokens, the signs it shares most
frames with, and a hierarchical grouping by frame-vector cosine similarity.
Writes discovery/frames_summary.json (sign codes and counts only).
"""
import collections
import json
import math

from common_b import DISC, UNKNOWN, ends, load_discovery, otype_group

rows = load_discovery()
tok = collections.Counter(s for r in rows for s in r["signs_reading_rtl"] if s != UNKNOWN)
freq = {s for s, n in tok.items() if n >= 10}

distinct = set()
for r in rows:
    si, ei = ends(r)
    seq = tuple(r["signs_reading_rtl"])
    if r["single_line"] and si and ei and seq and UNKNOWN not in seq:
        distinct.add((otype_group(r["object_type"]), seq))

frames = collections.defaultdict(collections.Counter)      # sign -> frame counts
left = collections.defaultdict(collections.Counter)
right = collections.defaultdict(collections.Counter)
for g, seq in distinct:
    ext = ("^",) + seq + ("$",)
    for i in range(1, len(ext) - 1):
        s = ext[i]
        frames[s][(ext[i - 1], ext[i + 1])] += 1
        left[s][ext[i - 1]] += 1
        right[s][ext[i + 1]] += 1


def cos(a, b):
    num = sum(a[k] * b.get(k, 0) for k in a)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


def ctx(s):
    v = collections.Counter()
    for k, n in left[s].items():
        v[("L", k)] += n
    for k, n in right[s].items():
        v[("R", k)] += n
    return v


out = {}
signs = sorted(freq, key=lambda s: -tok[s])
vecs = {s: ctx(s) for s in signs}
for s in signs:
    shared = collections.Counter()
    for t in signs:
        if t == s:
            continue
        k = set(frames[s]) & set(frames[t])
        if k:
            shared[t] = sum(min(frames[s][f], frames[t][f]) for f in k)
    sims = sorted(((round(cos(vecs[s], vecs[t]), 3), t) for t in signs if t != s), reverse=True)[:6]
    out[s] = {"tokens": tok[s], "shared_frames_top": shared.most_common(6), "context_cosine_top": sims}

# simple agglomerative clustering on context cosine (average linkage), cut at 0.35
clusters = [[s] for s in signs]


def csim(a, b):
    return sum(cos(vecs[x], vecs[y]) for x in a for y in b) / (len(a) * len(b))


while True:
    best, bi, bj = 0.0, -1, -1
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            v = csim(clusters[i], clusters[j])
            if v > best:
                best, bi, bj = v, i, j
    if best < 0.35:
        break
    clusters[bi] = clusters[bi] + clusters[bj]
    del clusters[bj]
clusters = sorted(clusters, key=lambda c: -sum(tok[s] for s in c))
(DISC / "frames_summary.json").write_text(json.dumps({"per_sign": out, "context_clusters_cos0.35": clusters}, indent=1), encoding="utf-8")
for c in clusters:
    if len(c) > 1:
        print(c)
