"""Stage 5b (exploratory): repetition of sign n-grams across halves, real versus synthetic corpora.

For the unique Indus texts and for the four synthetic Indus-shaped corpora of Stage 5 (regenerated
with the same seed), report the share of half-B bigram and trigram tokens (with start and end
symbols) already attested in half A, and the share of half-B texts sharing at least one trigram
with half A. Higher reuse explains why fitted keys transfer under any language model.
"""
import json
import os
from collections import Counter

import numpy as np

from common import HERE, unique_texts
from stage3_fit import split_half
from stage3e_languages import Lang
from stage5_power import NAMES, SEED, make_corpus


def ngrams(t, n):
    seq = ("<s>",) + tuple(t) + ("</s>",)
    return [seq[i:i + n] for i in range(len(seq) - n + 1)]


def reuse(texts):
    A, B = split_half(texts)
    out = {}
    for n in (2, 3):
        seen = {g for t in A for g in ngrams(t, n)}
        toks = [g for t in B for g in ngrams(t, n)]
        out[f"B_{n}gram_tokens_seen_in_A"] = sum(g in seen for g in toks) / len(toks)
    seen3 = {g for t in A for g in ngrams(t, 3) if "<s>" not in g and "</s>" not in g}
    out["B_texts_sharing_an_internal_trigram_with_A"] = float(np.mean(
        [any(g in seen3 for g in ngrams(t, 3) if "<s>" not in g and "</s>" not in g) for t in B]))
    cnt = Counter(g for t in texts for g in ngrams(t, 2))
    tot = sum(cnt.values())
    out["bigram_type_token_ratio"] = len(cnt) / tot
    return out


def main():
    ivs = unique_texts(min_len=2)
    res = {"indus_unique_texts": reuse(ivs)}
    rng = np.random.default_rng(SEED)  # same seed and order as stage5_power
    for n in NAMES:
        lang = Lang(n)
        _, pairs = make_corpus(lang, ivs, rng)
        res[f"synthetic_{n}"] = reuse([p[0] for p in pairs])
        print(n, res[f"synthetic_{n}"], flush=True)
    print("indus", res["indus_unique_texts"])
    os.makedirs(os.path.join(HERE, "stage5"), exist_ok=True)
    with open(os.path.join(HERE, "stage5", "ngram_reuse.json"), "w") as f:
        json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
