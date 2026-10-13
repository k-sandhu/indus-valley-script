"""Adversarial review, step 1 supplement: do near-copies across folds carry the rare-sign gain?

Usage: python -X utf8 review_step1_nearcopies.py --out <new dir under data/raw/2026-10-12-structure-first/>

Identical sequences share a component, but two texts that differ in one sign (for example the
same inscription transcribed with a variant code on different copies) can fall in different
folds. For every held-out token whose code was seen at most twice in training, this checks
whether a training text of the same length differs from the held-out text only at that
position, with a substitute code in the same coder-1 family. It then splits the frozen
per-token gain of the B_coder1 model by that property, and reruns the frozen B_coder1 test
after adding such pairs (texts of length >= 3, one substitution) to the union-find components.
"""
import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE.parents[1] / "step1-signs"))
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import analyze_step1 as A  # noqa: E402
from review_step1 import null_test  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--nulls", type=int, default=200)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    items = common.load_clean()
    texts = [d["text"] for d in items]
    folds = [d["fold"] for d in items]
    coding = common.load_coding(common.PROG / "step1-signs/sign_components_v1.tsv")
    vocab = sorted(set(coding) | {s for t in texts for s in t})
    B = common.inventories(coding, vocab)["B"]

    # one-substitution neighbours, texts of length >= 3
    frames = collections.defaultdict(list)
    for k, t in enumerate(texts):
        if len(t) >= 3:
            for i in range(len(t)):
                frames[(len(t), i, t[:i], t[i + 1:])].append(k)

    # 1. per-token split of the frozen model
    comp_idx = {c: i for i, c in enumerate(sorted({d["component"] for d in items}))}
    data = A.Data(texts, folds, vocab)
    ev = A.Evaluator(data, [comp_idx[d["component"]] for d in items])
    cls, ncls = A.class_array(data, B)
    _, _, per_tok = ev.evaluate(cls, ncls, keep_tokens=True)
    base_tok = np.concatenate([-np.log2(s["kn"]) for s in ev.splits])
    # held-out token order: by fold, then by original position
    order = [idx for k in range(5) for idx in np.where(data.fold == k)[0]]
    # recover (text index, position) for each flat token index
    flat = [(ti, p) for ti, t in enumerate(texts) for p in range(len(t))]
    rows = [(j, flat[idx][0], flat[idx][1], folds[flat[idx][0]]) for j, idx in enumerate(order)]
    train_freq = []
    for k in range(5):
        tr = data.fold != k
        train_freq.append(np.bincount(data.cur[tr], minlength=data.V))
    near = np.zeros(len(order), dtype=bool)
    rare = np.zeros(len(order), dtype=bool)
    for j, ti, p, k in rows:
        t = texts[ti]
        code = t[p]
        if train_freq[k][data.idx[code]] <= 2:
            rare[j] = True
            if len(t) >= 3:
                for other in frames[(len(t), p, t[:p], t[p + 1:])]:
                    if folds[other] != k and texts[other][p] != code and B[texts[other][p]] == B[code]:
                        near[j] = True
                        break
    gain = base_tok - per_tok
    res = {"rare_held_out_tokens_seen_le2": int(rare.sum()),
           "with_same_family_one_substitution_copy_in_training": int((rare & near).sum()),
           "mean_gain_rare_with_copy": float(gain[rare & near].mean()) if (rare & near).any() else None,
           "mean_gain_rare_without_copy": float(gain[rare & ~near].mean()),
           "total_gain_bits_from_rare_with_copy_per_sign": float(gain[rare & near].sum() / len(gain)),
           "total_gain_bits_from_rare_without_copy_per_sign": float(gain[rare & ~near].sum() / len(gain)),
           "total_gain_bits_from_other_tokens_per_sign": float(gain[~rare].sum() / len(gain))}
    print(json.dumps(res, indent=1), flush=True)

    # 2. refold with one-substitution neighbours joined
    uf = common.UnionFind()
    for d in items:
        for f in d["families"]:
            uf.union("T:" + "-".join(d["text"]), "F:" + f)
    for ks in frames.values():
        for a, b in zip(ks, ks[1:]):
            uf.union("T:" + "-".join(texts[a]), "T:" + "-".join(texts[b]))
    comps = collections.defaultdict(list)
    for k, d in enumerate(items):
        comps[uf.find("T:" + "-".join(d["text"]))].append(k)
    newfold = [0] * len(items)
    for c, ks in comps.items():
        key = min(rid for k in ks for rid in items[k]["records"])
        h = int(hashlib.sha256(f"{common.SEED}:{key}".encode()).hexdigest(), 16) % 5
        for k in ks:
            newfold[k] = h
    sizes = sorted((len(v) for v in comps.values()), reverse=True)
    cidx = {c: i for i, c in enumerate(sorted(comps))}
    comp_of_text = [0] * len(items)
    for c, ks in comps.items():
        for k in ks:
            comp_of_text[k] = cidx[c]
    data2 = A.Data(texts, newfold, vocab)
    ev2 = A.Evaluator(data2, comp_of_text)
    r, _ = null_test(ev2, data2, B, args.nulls, np.random.default_rng(common.SEED + 121))
    res["refolded"] = {"components": len(comps), "largest_components": sizes[:5],
                       "fold_sizes": dict(collections.Counter(newfold)), "baseline_bits": ev2.base_bits,
                       "B_coder1": r}
    print(json.dumps(res["refolded"], indent=1), flush=True)
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
