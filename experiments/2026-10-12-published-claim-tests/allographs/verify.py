#!/usr/bin/env python3
"""Independent recomputation of Study C headline numbers.

Shares no code with allograph_test.py. Minimal pairs come from brute-force Hamming
comparison of equal-length texts, divergences from scipy.spatial.distance.jensenshannon,
the null from a separately written stratified permutation with its own seed and fewer
replicates, and the jar expectation from Monte Carlo shuffles. Writes
run-2026-10-12/verification.json.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.spatial.distance import jensenshannon

here = Path(__file__).resolve().parent
repo = here.parents[2]
RUN = here / (sys.argv[1] if len(sys.argv) > 1 else "run-2026-10-12")
summary = json.loads((RUN / "summary.json").read_text(encoding="utf-8"))

# ---------------- key
table = {}
with open(repo / "data/lipi/src/assets/data/xlits.csv", encoding="utf-8", newline="") as fh:
    for row in csv.reader(fh):
        if row[0] == "sign":
            continue
        table[row[0]] = (row[1], row[2])
del table["000"], table["999"]
is_lig = {s: "-" in c for s, (x, c) in table.items()}
parent = {s: (c if (not is_lig[s] and c != s) else s) for s, (x, c) in table.items()}
root = dict(parent)
for _ in range(20):  # fixed-point iteration instead of pointer chasing
    root = {s: root[r] for s, r in root.items()}
bases = sorted(s for s, (x, c) in table.items() if c == s)


def value(s):
    x, c = table[s]
    if x:
        return x
    if is_lig[s]:
        return "".join(value(p) for p in c.split("-")[::-1])
    return value(c)


def pool(v):
    cons = [("s" if ch == "h" else ch) for ch in v if ch.lower() not in "aiueo"]
    return "".join(cons) if cons else "V:" + v.lower()


# ---------------- corpus
texts = []
with open(repo / "data/normalized/lipi_clean_rtl_singleline.jsonl", encoding="utf-8") as fh:
    for line in fh:
        if line.strip():
            texts.append(tuple(json.loads(line)["signs_reading_rtl"]))
uniq = sorted(set(texts))
cnt = Counter(s for t in uniq for s in t)
mayig = json.loads((repo / "data/normalized/mayig_wells_class_crosswalk.json").read_text(encoding="utf-8"))["by_wells_id"]

checks = {}


def check(name, mine, theirs, tol=0.0):
    ok = (mine == theirs) if tol == 0 else abs(mine - theirs) <= tol
    checks[name] = {"independent": mine, "summary": theirs, "agree": bool(ok)}


inv = summary["inventory"]
check("base_signs", len(bases), inv["base_signs"])
check("ligatures", sum(is_lig.values()), inv["ligatures"])
check("variants", sum(1 for s in table if not is_lig[s] and parent[s] != s), inv["variants"])
check("roots_attested", len({root[s] for s in table if not is_lig[s] and cnt[s] > 0}), inv["roots_attested"])
base_vals = Counter(pool(value(s)) for s in bases)
check("distinct_pooled_values_of_bases", len(base_vals), inv["distinct_pooled_values_of_bases"])
code_vals = Counter(pool(value(s)) for s in table if not is_lig[s])
big = {v for v, n in code_vals.items() if n >= 10}
share = sum(n for s, n in cnt.items() if s in table and not is_lig[s] and pool(value(s)) in big) / sum(cnt.values())
check("token_share_values_shared_by_10plus_codes", round(share, 10),
      round(inv["token_share_values_shared_by_10plus_codes_unique_texts"], 10))

# ---------------- pair sets at k = 3
K = 3
ok3 = {s for s, n in cnt.items() if n >= K}
nonlig = [s for s in table if not is_lig[s]]
P1 = {tuple(sorted((a, b))) for a in nonlig for b in nonlig if a < b and root[a] == root[b]}
P2 = {(a, b) for a, b in combinations(bases, 2) if pool(value(a)) == pool(value(b))}
P3 = {(a, b) for a, b in combinations(sorted(mayig), 2) if set(mayig[a]) & set(mayig[b])}
P1_in = P1 & P3
P1_out = {p for p in P1 if p[0] in mayig and p[1] in mayig} - P3
sets = {name: sorted(p for p in s if p[0] in ok3 and p[1] in ok3)
        for name, s in {"P1": P1, "P1_in": P1_in, "P1_out": P1_out, "P2": P2, "P3": P3}.items()}
for name, pairs in sets.items():
    check(f"pairs_k3_{name}", len(pairs), summary["analyses"]["primary_k3"]["sets"][name]["pairs"])

# ---------------- minimal pairs by brute-force Hamming comparison
codes = sorted(cnt)
ix = {c: i for i, c in enumerate(codes)}
MP = np.zeros((len(codes), len(codes)))
by_len = defaultdict(list)
for t in uniq:
    by_len[len(t)].append([ix[s] for s in t])
for L, rows in by_len.items():
    if L < 3:
        continue
    A = np.array(rows)
    diff = A[:, None, :] != A[None, :, :]
    ham = diff.sum(2)
    ii, jj = np.nonzero(np.triu(ham == 1, 1))
    for i, j in zip(ii, jj):
        pos = int(np.argmax(diff[i, j]))
        a, b = A[i, pos], A[j, pos]
        MP[a, b] += 1
        MP[b, a] += 1

# ---------------- divergences with scipy
BOS = len(codes)
left = np.zeros((len(codes), len(codes) + 1))
right = np.zeros_like(left)
posn = np.zeros((len(codes), 3))
for t in uniq:
    for i, s in enumerate(t):
        left[ix[s], ix[t[i - 1]] if i else BOS] += 1
        right[ix[s], ix[t[i + 1]] if i + 1 < len(t) else BOS] += 1
        posn[ix[s], 0 if i == 0 else (2 if i == len(t) - 1 else 1)] += 1


def smoothed(M):
    bg = M.sum(0) / M.sum()
    return (M + bg) / (M.sum(1, keepdims=True) + 1.0)


SL, SR, SP = smoothed(left), smoothed(right), smoothed(posn)


def stat(name, a, b):
    if name == "mp":
        return MP[a, b]
    if name == "neighbour":
        return 0.5 * (jensenshannon(SL[a], SL[b], base=2) ** 2 + jensenshannon(SR[a], SR[b], base=2) ** 2)
    return jensenshannon(SP[a], SP[b], base=2) ** 2


for name, pairs in sets.items():
    for m in ("mp", "neighbour", "position"):
        mine = float(np.mean([stat(m, ix[a], ix[b]) for a, b in pairs]))
        theirs = summary["analyses"]["primary_k3"]["sets"][name]["measures"][m]["observed_mean"]
        check(f"observed_k3_{name}_{m}", round(mine, 9), round(theirs, 9), tol=1e-9)

# ---------------- independent null: stratified relabelling, 500 replicates, own seed
universe = sorted(ok3)
levels = defaultdict(list)
for s in universe:
    levels[int(math.log2(cnt[s]))].append(s)
groups, pending = [], []
for lv in sorted(levels, reverse=True):
    pending += levels[lv]
    if len(pending) >= 5:
        groups.append(pending)
        pending = []
if pending:
    groups[-1] += pending
rnd = random.Random(777)
R = 500
nulls = {(n, m): [] for n in ("P1", "P1_out", "P2", "P3") for m in ("mp", "neighbour")}
pair_cache = {}
for _ in range(R):
    relabel = {}
    for g in groups:
        shuffled = g[:]
        rnd.shuffle(shuffled)
        relabel.update(zip(g, shuffled))
    for n in ("P1", "P1_out", "P2", "P3"):
        for m in ("mp", "neighbour"):
            vals = []
            for a, b in sets[n]:
                x, y = sorted((ix[relabel[a]], ix[relabel[b]]))
                key = (m, x, y)
                if key not in pair_cache:
                    pair_cache[key] = stat(m, x, y)
                vals.append(pair_cache[key])
            nulls[(n, m)].append(np.mean(vals))
fam = summary["analyses"]["primary_k3"]["primary_family_holm"]
for (n, m), vals in nulls.items():
    obs = summary["analyses"]["primary_k3"]["sets"][n]["measures"][m]["observed_mean"]
    vals = np.array(vals)
    p = (1 + ((vals >= obs - 1e-12) if m == "mp" else (vals <= obs + 1e-12)).sum()) / (R + 1)
    theirs = fam[f"{n}:{m}"]["p"]
    checks[f"null_p_k3_{n}_{m}"] = {"independent_R500": float(p), "summary_R2000": theirs,
                                    "same_side_of_0.05": bool((p < 0.05) == (theirs < 0.05))}

# ---------------- S1 jar direction by Monte Carlo
strokes = {"740": 0, "741": 1, "742": 2, "743": 2, "744": 2, "745": 3, "746": 3, "747": 3, "748": 4}
eligible, obs_order, obs_final = [], 0, 0
for t in uniq:
    seq = [strokes[s] for s in t if s in strokes]
    if len(seq) >= 2 and max(seq) > 0:
        eligible.append(seq)
        obs_order += all(seq[i] >= seq[i + 1] for i in range(len(seq) - 1))
        obs_final += seq[-1] == 0
rs = random.Random(778)
mc_order = mc_final = 0
MC = 4000
for _ in range(MC):
    for seq in eligible:
        sh = seq[:]
        rs.shuffle(sh)
        mc_order += all(sh[i] >= sh[i + 1] for i in range(len(sh) - 1))
        mc_final += sh[-1] == 0
s1 = summary["secondary"]["S1_jar_direction"]
check("S1_texts", len(eligible), s1["texts"])
check("S1_non_increasing_observed", obs_order, s1["non_increasing"]["observed"])
check("S1_final_unstroked_observed", obs_final, s1["final_unstroked"]["observed"])
check("S1_non_increasing_expected_MC", round(mc_order / MC, 2), round(s1["non_increasing"]["expected"], 2), tol=0.5)
check("S1_final_unstroked_expected_MC", round(mc_final / MC, 2), round(s1["final_unstroked"]["expected"], 2), tol=0.5)

# ---------------- S2 observed mixed texts
for include_jar, label in ((False, "S2_variant_consistency"), (True, "S2_variant_consistency_with_jar")):
    mixed = 0
    for t in uniq:
        per = defaultdict(set)
        n_per = Counter()
        for s in t:
            if s in table and not is_lig[s]:
                per[root[s]].add(s)
                n_per[root[s]] += 1
        for r, members in per.items():
            if r == "740" and not include_jar:
                continue
            group_codes = {s for s in nonlig if root[s] == r and cnt[s] > 0}
            if len(group_codes) >= 2 and n_per[r] >= 2 and len(members) > 1:
                mixed += 1
    check(f"{label}_mixed_observed", mixed, summary["secondary"][label]["mixed_observed"])

# ---------------- S3 conjunct decomposition
present = set(uniq)
matches = occ = 0
for t in uniq:
    for i, s in enumerate(t):
        if s in table and is_lig[s]:
            occ += 1
            comps = tuple(table[s][1].split("-")[::-1])
            matches += (t[:i] + comps + t[i + 1:]) in present
check("S3_occurrences", occ, summary["secondary"]["S3_conjunct_decomposition"]["occurrences"])
check("S3_matches", matches, summary["secondary"]["S3_conjunct_decomposition"]["matching_occurrences"])

all_agree = all(v.get("agree", v.get("same_side_of_0.05")) for v in checks.values())
result = {"all_agree": all_agree, "checks": checks}
(RUN / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"all_agree": all_agree,
                  "disagreements": [k for k, v in checks.items() if not v.get("agree", v.get("same_side_of_0.05"))]},
                 indent=1))
