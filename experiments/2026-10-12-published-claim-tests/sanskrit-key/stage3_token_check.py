"""Review response (Amendment 4): token distributions and deletion in the key and the Stage 3 optima.

Uses the greedy option choice that Stage 3 scores. For the key and each saved Stage 3 optimum, reports
sign tokens left without a consonant, texts left with an empty skeleton, consonant count, class shares
and Kullback-Leibler divergence from the Sanskrit training unigram. Also rescores each optimum after
shuffling its own skeleton consonants within each text, which keeps its composition and removes order.
"""
import json
import math
import os

import numpy as np

import stage3_fit as s3
from common import CID, CLASSES, HERE, NC, RAW, key_options, unique_texts


def greedy_classes(text, opts_int):
    T, U = s3._T, s3._U
    ctx = s3.BOS_CTX
    out = []
    empty = 0
    for sign in text:
        options = opts_int[sign]
        if len(options) == 1:
            seq = options[0]
        else:
            best = None
            for so in options:
                c, v = ctx, 0.0
                for x in so:
                    v += T[c][x] - U[x]
                    c = (c * s3.BASE + x) % s3.MOD
                if best is None or v > best[0]:
                    best = (v, so)
            seq = best[1]
        if not seq:
            empty += 1
        for x in seq:
            out.append(x)
            ctx = (ctx * s3.BASE + x) % s3.MOD
    return out, empty


def describe(texts, opts_int, rng):
    p1 = np.exp2(np.array(s3._U))
    p1 = p1 / p1.sum()
    counts = np.zeros(NC)
    empty_tokens = 0
    empty_texts = 0
    seqs = []
    for t in texts:
        cl, e = greedy_classes(t, opts_int)
        empty_tokens += e
        empty_texts += not cl
        for x in cl:
            counts[x] += 1
        seqs.append(cl)
    q = counts / counts.sum()
    kl = float(sum(q[i] * math.log2(q[i] / p1[i]) for i in range(NC) if q[i] > 0))
    shuffled = [tuple(str(x) for x in np.array(s)[rng.permutation(len(s))]) for s in seqs if s]
    single = {str(x): ((x,),) for x in range(NC)}
    return {"sign_tokens": int(sum(len(t) for t in texts)), "tokens_without_consonant": int(empty_tokens),
            "texts_with_empty_skeleton": int(empty_texts), "consonants": int(counts.sum()),
            "kl_from_sanskrit_unigram_bits": kl,
            "class_shares": {CLASSES[i]: round(float(q[i]), 4) for i in range(NC)},
            "G_after_within_text_consonant_shuffle": s3.corpus_stats(shuffled, single)["G"]}


def main():
    s3.load_model()
    texts = unique_texts(min_len=2)
    key = s3.to_int(key_options())
    rng = np.random.default_rng(4242)
    out = {"key": {**describe(texts, key, rng), "G": s3.corpus_stats(texts, key)["G"]}}
    with open(os.path.join(RAW, "sanskrit-key", "stage3_assignments.json"), encoding="utf-8") as f:
        ann = json.load(f)
    out["optima"] = []
    for a in ann:
        opts = dict(key)
        for s, v in a["assignment"].items():
            opts[s] = tuple(tuple(CID[c] for c in o) for o in v)
        evaluated_on = texts
        if a["label"].startswith("scrambled"):
            evaluated_on = s3.scramble(texts, 20261012 + 2000 + int(a["label"][-1]))
        elif a["label"] == "fitA":
            evaluated_on = s3.split_half(texts)[0]
        elif a["label"] == "longest50":
            evaluated_on = sorted(texts, key=lambda t: (-len(t), t))[:50]
        d = describe(evaluated_on, opts, rng)
        d.update({"label": a["label"], "seed": a["seed"], "G_fit": a["G_fit"]})
        out["optima"].append(d)
    with open(os.path.join(HERE, "stage3", "token_check.json"), "w") as f:
        json.dump(out, f, indent=1)
    k = out["key"]
    print("key", {x: k[x] for x in ("tokens_without_consonant", "texts_with_empty_skeleton", "consonants",
                                    "kl_from_sanskrit_unigram_bits", "G", "G_after_within_text_consonant_shuffle")},
          "m share", k["class_shares"]["m"])
    for d in out["optima"]:
        print(d["label"], round(d["G_fit"], 3), d["tokens_without_consonant"], d["texts_with_empty_skeleton"],
              d["consonants"], round(d["kl_from_sanskrit_unigram_bits"], 3),
              round(d["G_after_within_text_consonant_shuffle"], 3))


if __name__ == "__main__":
    main()
