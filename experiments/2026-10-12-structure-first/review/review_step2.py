"""Adversarial review, step 2: production series in 2b/2c and the power of 2d.

Usage: python -X utf8 review_step2.py --out <new dir under data/raw/2026-10-12-structure-first/>

1. 2b and 2c recomputed after removing near-duplicate text pairs (Levenshtein distance <= 1,
   or one text a contiguous part of the other), which are the expected product of one mould,
   die or casting series transcribed with a variant or a damaged sign.
2. 2d power: matching-animal seals are given k times the hit rate that each class's
   specific n-grams show on other seals, and the frozen permutation test is applied.
Imports the frozen step 2 functions unchanged.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step2-image-text"))
import common  # noqa: E402
import analyze_step2 as A  # noqa: E402


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def contained(a, b):
    if len(a) > len(b):
        a, b = b, a
    return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))


def near_dup(a, b):
    return lev(a, b) <= 1 or contained(a, b)


def test_2b_nodup(types, rng, perms):
    grams = [A.ngrams(t, (2,)) or {t} for t, _, _ in types]
    labs = np.array([l for _, l, _ in types])
    n = len(types)
    iu = np.triu_indices(n, 1)
    keep, vals = [], []
    nd_same = nd_total = 0
    for i, j in zip(*iu):
        d = near_dup(types[i][0], types[j][0])
        u = grams[i] | grams[j]
        v = len(grams[i] & grams[j]) / len(u) if u else 0.0
        if d:
            nd_total += 1
            nd_same += labs[i] == labs[j]
        keep.append(not d)
        vals.append(v)
    keep = np.array(keep)
    vals = np.array(vals)
    a, b = iu[0][keep], iu[1][keep]
    v = vals[keep]

    def stat(lab):
        same = lab[a] == lab[b]
        return v[same].mean() - v[~same].mean() if same.any() and (~same).any() else 0.0

    obs = stat(labs)
    null = np.array([stat(rng.permutation(labs)) for _ in range(perms)])
    same_all = labs[iu[0]] == labs[iu[1]]
    return {"text_types": n, "near_duplicate_pairs": nd_total, "near_duplicate_pairs_same_class": int(nd_same),
            "same_class_pairs": int(same_all.sum()),
            "same_class_pairs_with_overlap": int(((vals > 0) & same_all).sum()),
            "same_class_pairs_with_overlap_that_are_near_duplicates": int(((vals > 0) & same_all & ~keep).sum()),
            "difference_without_near_duplicates": float(obs), "null_mean": float(null.mean()),
            "p_value": float((1 + (null >= obs).sum()) / (1 + perms))}


def test_2c_nodup(types, rng, perms):
    labs = np.array([l for _, l, _ in types])
    n = len(labs)
    shared = np.array([[len(A.ngrams(types[i][0]) & A.ngrams(types[j][0]))
                        if i != j and not near_dup(types[i][0], types[j][0]) else -1 for j in range(n)]
                       for i in range(n)])

    def predict(lab):
        freq = collections.Counter(lab)
        correct = 0
        for i in range(n):
            row = shared[i]
            best = row.max()
            if best <= 0:
                pred = max(freq, key=lambda c: (freq[c] - (lab[i] == c), c))
            else:
                cands = collections.Counter(lab[j] for j in np.where(row == best)[0])
                top = max(cands.values())
                tied = [c for c, v in cands.items() if v == top]
                pred = max(tied, key=lambda c: (freq[c] - (lab[i] == c), c))
            correct += pred == lab[i]
        return correct / n

    obs = predict(labs)
    null = np.array([predict(rng.permutation(labs)) for _ in range(perms)])
    return {"accuracy_without_near_duplicate_neighbours": float(obs),
            "majority_rate": collections.Counter(labs).most_common(1)[0][1] / n,
            "null_mean": float(null.mean()), "p_value": float((1 + (null >= obs).sum()) / (1 + perms))}


def power_2d(copper, seals, rng, ks, sims, perms):
    """Re-create the frozen 2d hit vectors, then inject enrichment on matching seals."""
    class_grams = collections.defaultdict(set)
    all_grams = collections.defaultdict(set)
    for o in copper.values():
        if not o["labels"]:
            continue
        for t in o["texts"]:
            g = A.ngrams(t, (2, 3))
            for lab in o["labels"]:
                class_grams[lab] |= g
            for x in g:
                all_grams[x] |= o["labels"]
    specific = {lab: {g for g in gs if all_grams[g] == {lab}} for lab, gs in class_grams.items()}
    pairs = set()
    for o in seals.values():
        if len(o["labels"]) == 1:
            lab = next(iter(o["labels"]))
            for t in o["texts"]:
                pairs.add((t, lab))
    pairs = sorted(pairs)
    labs = np.array([p[1] for p in pairs])
    classes = sorted(c for c in specific if specific[c] and c in set(labs))
    hit = {c: np.array([bool(A.ngrams(t, (2, 3)) & specific[c]) for t, _ in pairs]) for c in classes}
    base = {}
    for c in classes:
        other = labs != c
        base[c] = {"matching_seals": int((labs == c).sum()), "other_seal_hit_rate": float(hit[c][other].mean()),
                   "expected_matching_hits_under_null": float(hit[c].sum() * (labs == c).mean())}

    def pval(h):
        obs = sum(int((h[c] & (labs == c)).sum()) for c in classes)
        null = np.array([sum(int((h[c] & (p == c)).sum()) for c in classes)
                         for p in (rng.permutation(labs) for _ in range(perms))])
        return obs, (1 + (null >= obs).sum()) / (1 + perms)

    out = {"per_class": base, "expected_total_under_null": sum(b["expected_matching_hits_under_null"] for b in base.values())}
    pw = {}
    for k in ks:
        sig = 0
        obs_list = []
        for _ in range(sims):
            h = {}
            for c in classes:
                v = hit[c].copy()
                m = labs == c
                p = min(1.0, k * base[c]["other_seal_hit_rate"])
                v[m] = rng.random(m.sum()) < p
                h[c] = v
            obs, p = pval(h)
            obs_list.append(obs)
            sig += p < 0.05
        pw[str(k)] = {"power_p_lt_0.05": sig / sims, "mean_matching_hits": float(np.mean(obs_list))}
        print("k", k, pw[str(k)], flush=True)
    out["power_by_enrichment"] = pw
    # same, excluding the unicorn class from the statistic (it carries half the null expectation)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--perms", type=int, default=2000)
    ap.add_argument("--sims", type=int, default=200)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    faces = common.read_jsonl(common.FACES)
    rng = np.random.default_rng(common.SEED + 202)
    res = {}
    for name, types in (("copper", {"TAB:C"}), ("bas_relief", {"TAB:B"}), ("incised", {"TAB:I"})):
        objs = A.objects(faces, types)
        tt = A.text_types(objs)
        res[name] = {"2b": test_2b_nodup(tt, rng, args.perms), "2c": test_2c_nodup(tt, rng, args.perms)}
        print(name, json.dumps(res[name]), flush=True)
    copper = A.objects(faces, {"TAB:C"})
    seals = A.objects(faces, {"SEAL", "SEAL:S", "SEAL:R", "SEAL:C", "SEAL:CY"})
    res["2d_power"] = power_2d(copper, seals, rng, ks=(2, 5, 10, 20), sims=args.sims, perms=500)
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
