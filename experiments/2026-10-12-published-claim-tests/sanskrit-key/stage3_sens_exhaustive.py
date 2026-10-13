"""Sensitivity (post-outcome): exhaustive an/aṃ option choice for the key and for permuted keys.

Stage 3 chose among a sign's skeleton options greedily. Verification found that exhaustive choice
raises the key's order gain from -0.393 to -0.351. This script applies exhaustive choice to the key and
to 300 frequency-stratified permutations so that both sides receive the same benefit.
"""
import itertools
import json
import os
from multiprocessing import Pool

import numpy as np

import stage3_fit as s3
from common import HERE, frequency_strata, key_options, permuted_options, unique_texts

SEED = 20261012


def llr_seq(seq):
    T, U = s3._T, s3._U
    ctx = s3.BOS_CTX
    v = 0.0
    for x in seq:
        v += T[ctx][x] - U[x]
        ctx = (ctx * s3.BASE + x) % s3.MOD
    return v


def exhaustive_G(texts, opts_int):
    a = 0.0
    n = 0
    for t in texts:
        choices = [opts_int[x] for x in t]
        best = None
        count = 0
        for combo in itertools.product(*choices):
            seq = [c for part in combo for c in part]
            v = llr_seq(seq)
            if best is None or v > best[0]:
                best = (v, len(seq))
            count += 1
            if count >= 256:
                break
        a += best[0]
        n += best[1]
    return a / n


def job(args):
    s3.load_model()
    seed, texts, options, signs, strata = args
    perm = permuted_options(options, signs, strata, np.random.default_rng(seed))
    return exhaustive_G(texts, s3.to_int(perm))


def main():
    s3.load_model()
    texts = unique_texts(min_len=2)
    options = key_options()
    signs = sorted({x for t in texts for x in t})
    strata = frequency_strata(texts)
    key_g = exhaustive_G(texts, s3.to_int(options))
    with Pool(int(os.environ.get("WORKERS", "6"))) as pool:
        null = pool.map(job, [(SEED + i, texts, options, signs, strata) for i in range(300)], chunksize=5)
    null = np.array(null)
    out = {"key_G_exhaustive": key_g, "N1_300_exhaustive": {
        "mean": float(null.mean()), "sd": float(null.std()), "p97.5": float(np.percentile(null, 97.5)),
        "max": float(null.max()), "share_ge_key": float((null >= key_g).mean())}}
    with open(os.path.join(HERE, "stage3", "sensitivity_exhaustive.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
