"""Review response (Amendment 4): sensitivity of the key's percentile to training text and projection.

The DCS '# text' lines of the Rgveda, Atharvaveda and Arthasastra are unsandhied pausa forms with
compounds split; those of the Ramayana, Manusmrti and Satapatha are sandhied. Sandhied text writes
word-final -m before consonants as anusvara, which the main projection maps to n. Variants:
  baseline        all six texts, anusvara -> n (the Stage 3 model)
  unsandhied      Rgveda, Atharvaveda and Arthasastra only
  anusvara_m      all six texts, anusvara -> m
  both            unsandhied texts, anusvara -> m
For each, the key and 1,000 frequency-stratified permutations (the Stage 3 seeds) are scored by order
gain G, and by an order-only statistic: G minus the mean G of the same texts with their signs shuffled
within each text (20 shuffles), which removes what the choice of consonants contributes without order.
"""
import json
import math
import os
import unicodedata
from multiprocessing import Pool

import numpy as np

import common as C
from common import (HERE, NC, KneserNey, dcs_files, dcs_lines, encode, frequency_strata, key_options,
                    permuted_options, unique_texts)

SEED = 20261012
BASE = NC + 1
MOD = BASE ** 4
BOS = sum(NC * BASE ** k for k in range(4))
UNSANDHIED = ["Ṛgveda", "Atharvaveda (Śaunaka)", "Arthaśāstra"]


def skel(text, anus_m):
    text = unicodedata.normalize("NFC", text.lower())
    out, prev = [], ""
    for ch in text:
        if ch == "h" and prev in C.ASPIRABLE:
            prev = "h"
            continue
        if ch in C.IAST_SINGLE:
            c = C.IAST_SINGLE[ch]
            if anus_m and ch in "ṃṁ":
                c = "m"
            out.append(c)
        prev = ch
    return "".join(out)


def build(names, anus_m):
    train = []
    for nm in names:
        for i, p in enumerate(dcs_files(nm)):
            if i % 10 == 9:
                continue
            for line in dcs_lines(p):
                s = skel(line, anus_m)
                if s:
                    train.append(encode(s))
    m = KneserNey(5, NC).fit(train)
    uni = np.bincount([c for s in train for c in s], minlength=NC).astype(float)
    return m.dense_table().tolist(), np.log2(uni / uni.sum()).tolist(), sum(map(len, train))


_M = {}


def _init(models):
    _M.update(models)


def score(text, opts, T, U):
    ctx = BOS
    a = 0.0
    n = 0
    for sign in text:
        options = opts[sign]
        if len(options) == 1:
            seq = options[0]
        else:
            best = None
            for so in options:
                c, v = ctx, 0.0
                for x in so:
                    v += T[c][x] - U[x]
                    c = (c * BASE + x) % MOD
                if best is None or v > best[0]:
                    best = (v, so)
            seq = best[1]
        for x in seq:
            a += T[ctx][x] - U[x]
            ctx = (ctx * BASE + x) % MOD
            n += 1
    return a, n


def corpus_G(texts, opts, T, U):
    a = n = 0
    for t in texts:
        x, k = score(t, opts, T, U)
        a += x
        n += k
    return a / n


def stats(texts, opts, T, U, rng):
    g = corpus_G(texts, opts, T, U)
    sh = []
    for _ in range(20):
        st = [tuple(t[i] for i in rng.permutation(len(t))) for t in texts]
        sh.append(corpus_G(st, opts, T, U))
    return g, g - float(np.mean(sh))


def to_int(options):
    return {s: tuple(tuple(C.CID[c] for c in o) for o in v) for s, v in options.items()}


def job(args):
    variant, seed, texts, options, signs, strata = args
    T, U = _M[variant]
    perm = permuted_options(options, signs, strata, np.random.default_rng(seed))
    return variant, stats(texts, to_int(perm), T, U, np.random.default_rng(seed + 7))


def main():
    variants = {"baseline": (C.DCS_TEXTS, False), "unsandhied": (UNSANDHIED, False),
                "anusvara_m": (C.DCS_TEXTS, True), "both": (UNSANDHIED, True)}
    models, sizes = {}, {}
    for v, (names, am) in variants.items():
        T, U, n = build(names, am)
        models[v] = (T, U)
        sizes[v] = n
        print("built", v, n, flush=True)
    texts = unique_texts(min_len=2)
    options = key_options()
    signs = sorted({x for t in texts for x in t})
    strata = frequency_strata(texts)
    out = {}
    for v in variants:
        T, U = models[v]
        g, o = stats(texts, to_int(options), T, U, np.random.default_rng(SEED + 99))
        out[v] = {"train_consonants": sizes[v], "key_G": g, "key_order_only": o}
    jobs = [(v, SEED + i, texts, options, signs, strata) for v in variants for i in range(1000)]
    with Pool(int(os.environ.get("WORKERS", "8")), initializer=_init, initargs=(models,)) as pool:
        res = pool.map(job, jobs, chunksize=20)
    for v in variants:
        arr = np.array([r[1] for r in res if r[0] == v])
        d = out[v]
        for k, col in (("G", 0), ("order_only", 1)):
            key = d["key_G"] if k == "G" else d["key_order_only"]
            d[f"N1_{k}"] = {"mean": float(arr[:, col].mean()), "sd": float(arr[:, col].std()),
                            "share_ge_key": float((arr[:, col] >= key).mean()),
                            "z_key": float((key - arr[:, col].mean()) / arr[:, col].std())}
    with open(os.path.join(HERE, "stage3", "sensitivity_training.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
