"""Stage 1: held-out entropy and redundancy of full Sanskrit text and of the key's skeleton.

Outputs: stage1/summary.json (tracked); models in data/raw/.../sanskrit-key/models (local).
"""
import json
import math
import os
import time
from collections import Counter

import numpy as np

from common import (CLASSES, HERE, NC, RAW, KneserNey, dcs_lines, dcs_split, encode, iast_phonemes,
                    iast_skeleton, sha256)

MODELS = os.path.join(RAW, "sanskrit-key", "models")


def corpus(paths, kind):
    seqs = []
    for p in paths:
        for line in dcs_lines(p):
            if kind == "skeleton":
                s = iast_skeleton(line)
                if s:
                    seqs.append(encode(s))
            else:
                toks = iast_phonemes(line)
                if toks and toks[0] == " ":
                    toks = toks[1:]
                if toks and toks[-1] == " ":
                    toks = toks[:-1]
                if toks:
                    seqs.append(toks)
    return seqs


def cross_entropy(model, seqs):
    total, n = 0.0, 0
    for s in seqs:
        total += model.logprob_seq(s)
        n += len(s)
    return -total / n, n


def main():
    t0 = time.time()
    split = dcs_split()
    os.makedirs(MODELS, exist_ok=True)
    out = {"dcs_files": {k: len(v) for k, v in split.items()}}

    # ---- skeleton
    train = corpus(split["train"], "skeleton")
    held = corpus(split["heldout"], "skeleton")
    out["skeleton"] = {
        "alphabet": CLASSES, "alphabet_size": NC,
        "train_lines": len(train), "train_symbols": sum(map(len, train)),
        "heldout_lines": len(held), "heldout_symbols": sum(map(len, held)),
    }
    uni = Counter(c for s in train for c in s)
    tot = sum(uni.values())
    p1 = np.array([uni[i] / tot for i in range(NC)])
    h0 = -sum(p1[c] * math.log2(p1[c]) for c in range(NC))
    held_uni = -sum(math.log2(p1[c]) for s in held for c in s) / sum(map(len, held))
    out["skeleton"]["class_frequencies"] = {CLASSES[i]: round(float(p1[i]), 5) for i in range(NC)}
    out["skeleton"]["unigram_entropy_train"] = round(h0, 4)
    out["skeleton"]["unigram_cross_entropy_heldout"] = round(held_uni, 4)
    res = {}
    for order in (2, 3, 4, 5):
        m = KneserNey(order, NC).fit(train)
        h, n = cross_entropy(m, held)
        res[str(order)] = {"cross_entropy_bits": round(h, 4), "redundancy": round(1 - h / math.log2(NC), 4)}
        print("skeleton order", order, res[str(order)], round(time.time() - t0, 1), flush=True)
        if order == 5:
            table = m.dense_table()
            np.savez(os.path.join(MODELS, "skeleton_kn5.npz"), table=table, unigram=p1)
    out["skeleton"]["by_order"] = res

    # ---- full phoneme text with spaces
    trainf = corpus(split["train"], "full")
    heldf = corpus(split["heldout"], "full")
    vocab = sorted(set(t for s in trainf for t in s))
    vid = {t: i for i, t in enumerate(vocab)}
    trainf_i = [[vid[t] for t in s] for s in trainf]
    heldf_i = [[vid[t] for t in s if t in vid] for s in heldf]
    out["full"] = {"alphabet": vocab, "alphabet_size": len(vocab),
                   "train_symbols": sum(map(len, trainf_i)), "heldout_symbols": sum(map(len, heldf_i))}
    resf = {}
    for order in (3, 4, 5):
        m = KneserNey(order, len(vocab)).fit(trainf_i)
        h, n = cross_entropy(m, heldf_i)
        resf[str(order)] = {"cross_entropy_bits": round(h, 4), "redundancy": round(1 - h / math.log2(len(vocab)), 4)}
        print("full order", order, resf[str(order)], round(time.time() - t0, 1), flush=True)
        del m
    out["full"]["by_order"] = resf

    # ---- unicity distance with the preprint's N = 330 and formula d = N / rho
    N = 330
    rho_skel = res["5"]["redundancy"]
    rho_full = resf["5"]["redundancy"]
    out["unicity"] = {
        "preprint": {"N": N, "rho": 0.7, "d_characters": round(N / 0.7, 1)},
        "full_text_measured": {"N": N, "rho": rho_full, "d": round(N / rho_full, 1)},
        "skeleton_measured": {"N": N, "rho": rho_skel, "d_consonants": round(N / rho_skel, 1)},
    }
    out["model_files"] = {"skeleton_kn5.npz": sha256(os.path.join(MODELS, "skeleton_kn5.npz"))}
    out["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(HERE, "stage1"), exist_ok=True)
    with open(os.path.join(HERE, "stage1", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out["unicity"]))


if __name__ == "__main__":
    main()
