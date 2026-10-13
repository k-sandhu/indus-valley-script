"""Stage 2: is an inscription 'readable' as Sanskrit words, under the key and under permuted keys?

A skeleton is readable when it divides into stems from a lexicon, each at least m consonants,
with an optional final ending skeleton. The calibrated variant also caps the number of stems at
the maximum lemma count the published glossing uses for that skeleton length.
"""
import json
import math
import os
import re
import sys
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

from common import (CLASSES, HERE, MW_TXT, NC, RAW, dcs_lemmas_and_forms, dcs_split, frequency_strata,
                    iast_skeleton, key_options, permuted_options, sha256, slp1_skeleton, unique_texts)

ENDINGS = ("", "s", "m", "n", "y", "t", "sy")
MAXW = 12
N_PERM = 1000
N_PERM_UNIFORM = 200
SEED = 20261012

# Maximum lemmas per text by reading-skeleton length in the published glossing (stage0 summary).
GLOSS_MAX = {0: 1, 1: 2, 2: 2, 3: 3, 4: 3, 5: 4, 6: 4, 7: 5, 8: 5, 9: 5, 10: 5, 11: 5, 12: 6, 13: 6, 14: 5, 15: 6, 20: 8}


def gloss_cap(L: int) -> int:
    if L in GLOSS_MAX:
        return GLOSS_MAX[L]
    return max(6, math.ceil(0.4 * L))


def load_mw_skeletons() -> set[str]:
    out = set()
    pat = re.compile(r"<k1>([^<]+)<k2>")
    with open(MW_TXT, encoding="utf-8") as f:
        for line in f:
            if line.startswith("<L>"):
                m = pat.search(line)
                if m:
                    sk = slp1_skeleton(m.group(1))
                    if sk:
                        out.add(sk)
    return out


def load_dcs_lemma_skeletons() -> set[str]:
    split = dcs_split()
    lemmas, _ = dcs_lemmas_and_forms(split["train"] + split["heldout"])
    return {iast_skeleton(l) for l in lemmas if iast_skeleton(l)}


LEX: dict[str, set] = {}


def min_stems(s: str, lex: set, m: int) -> list:
    """minseg[i] = fewest stems covering s[:i] (inf if impossible)."""
    L = len(s)
    INF = 10 ** 6
    best = [INF] * (L + 1)
    best[0] = 0
    for i in range(1, L + 1):
        lo = max(0, i - MAXW)
        for j in range(lo, i - m + 1):
            if best[j] + 1 < best[i] and s[j:i] in lex:
                best[i] = best[j] + 1
    return best


_cache: dict = {}


def readable_flags(s: str) -> tuple:
    """Flags for (mw,m=1), (mw,m=2), (mw,m=1,calibrated), (dcs,m=1), (dcs,m=2), (dcs,m=1,calibrated)."""
    r = _cache.get(s)
    if r is not None:
        return r
    flags = []
    L = len(s)
    for name in ("mw", "dcs"):
        lex = LEX[name]
        res = {}
        for m in (1, 2):
            best = min_stems(s, lex, m)
            ok = False
            okcap = False
            for e in ENDINGS:
                j = L - len(e)
                if j <= 0 or s[j:] != e:
                    continue
                if best[j] < 10 ** 6:
                    ok = True
                    if best[j] <= gloss_cap(L):
                        okcap = True
            res[m] = (ok, okcap)
        flags.extend([res[1][0], res[2][0], res[1][1]])
    r = tuple(flags) if L > 0 else (False,) * 6
    _cache[s] = r
    return r


def text_flags(text, options) -> tuple:
    """A text is readable if any combination of its signs' skeleton options is readable."""
    combos = [""]
    for sign in text:
        combos = [c + o for c in combos for o in options[sign]]
        if len(combos) > 64:
            combos = combos[:64]
    agg = [False] * 6
    for c in set(combos):
        f = readable_flags(c)
        agg = [a or b for a, b in zip(agg, f)]
        if all(agg):
            break
    return tuple(agg)


def corpus_shares(texts, options) -> list[float]:
    tot = np.zeros(6)
    for t in texts:
        tot += np.array(text_flags(t, options), dtype=float)
    return (tot / len(texts)).tolist()


def _init(lex):
    LEX.update(lex)


def _perm_job(args):
    seed, uniform, texts, options, signs, strata = args
    rng = np.random.default_rng(seed)
    perm = permuted_options(options, signs, None if uniform else strata, rng)
    return corpus_shares(texts, perm)


LABELS = ["mw_m1", "mw_m2", "mw_m1_glosscap", "dcs_m1", "dcs_m2", "dcs_m1_glosscap"]


def main():
    t0 = time.time()
    lex = {"mw": load_mw_skeletons(), "dcs": load_dcs_lemma_skeletons()}
    LEX.update(lex)
    print("lexicon sizes", {k: len(v) for k, v in lex.items()}, round(time.time() - t0, 1), flush=True)

    texts = unique_texts(min_len=2)
    options = key_options()
    signs = sorted({s for t in texts for s in t})
    strata = frequency_strata(texts)
    key_shares = corpus_shares(texts, options)
    print("key", dict(zip(LABELS, key_shares)), flush=True)

    jobs = [(SEED + i, False, texts, options, signs, strata) for i in range(N_PERM)]
    jobs += [(SEED + 100000 + i, True, texts, options, signs, strata) for i in range(N_PERM_UNIFORM)]
    with Pool(20, initializer=_init, initargs=(lex,)) as pool:
        res = pool.map(_perm_job, jobs, chunksize=10)
    n1 = np.array(res[:N_PERM])
    n0 = np.array(res[N_PERM:])
    print("perms done", round(time.time() - t0, 1), flush=True)

    # random i.i.d. strings at Sanskrit class frequencies
    p1 = np.load(os.path.join(RAW, "sanskrit-key", "models", "skeleton_kn5.npz"))["unigram"]
    rng = np.random.default_rng(SEED + 7)
    by_len = {}
    for L in range(1, 17):
        draws = rng.choice(NC, size=(5000, L), p=p1)
        flags = np.array([readable_flags("".join(CLASSES[c] for c in row)) for row in draws], dtype=float)
        share = flags.mean(axis=0)
        by_len[str(L)] = {lab: round(float(v), 4) for lab, v in zip(LABELS, share)}
        by_len[str(L)]["effective_redundancy_bits_per_consonant"] = {
            lab: (round(-math.log2(v) / L, 4) if v > 0 else None) for lab, v in zip(LABELS, share)}

    # positive control: held-out Sanskrit word spans of 1-3 words
    from common import dcs_lines
    held = dcs_split()["heldout"]
    spans = []
    for p in held:
        for line in dcs_lines(p):
            words = [w for w in line.split() if iast_skeleton(w)]
            for k in (1, 2, 3):
                for i in range(0, max(0, len(words) - k + 1), 7):
                    spans.append((k, iast_skeleton("".join(words[i:i + k]))))
    rng2 = np.random.default_rng(SEED + 9)
    idx = rng2.choice(len(spans), size=min(6000, len(spans)), replace=False)
    ctrl = {}
    for k in (1, 2, 3):
        sel = [spans[i][1] for i in idx if spans[i][0] == k]
        fl = np.array([readable_flags(s) for s in sel], dtype=float).mean(axis=0)
        ctrl[str(k)] = {"n": len(sel), **{lab: round(float(v), 4) for lab, v in zip(LABELS, fl)}}

    def summarize(arr):
        return {lab: {"mean": round(float(arr[:, i].mean()), 4), "median": round(float(np.median(arr[:, i])), 4),
                      "p2.5": round(float(np.percentile(arr[:, i], 2.5)), 4),
                      "p97.5": round(float(np.percentile(arr[:, i], 97.5)), 4),
                      "max": round(float(arr[:, i].max()), 4)} for i, lab in enumerate(LABELS)}

    pct = {lab: round(float((n1[:, i] >= key_shares[i]).mean()), 4) for i, lab in enumerate(LABELS)}
    out = {
        "population": {"unique_texts_len_ge_2": len(texts), "signs": len(signs),
                       "texts_with_empty_key_skeleton": sum(1 for t in texts if all(options[s] == ("",) for s in t))},
        "lexicons": {"mw_headword_skeletons": len(lex["mw"]), "dcs_lemma_skeletons": len(lex["dcs"]),
                     "mw_txt_sha256": sha256(MW_TXT)},
        "endings": ENDINGS,
        "key_readable_share": dict(zip(LABELS, [round(x, 4) for x in key_shares])),
        "N1_frequency_stratified": summarize(n1),
        "N1_share_of_permutations_at_or_above_key": pct,
        "N0_uniform": summarize(n0),
        "random_strings_by_length": by_len,
        "heldout_sanskrit_word_spans": ctrl,
        "seconds": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.join(HERE, "stage2"), exist_ok=True)
    with open(os.path.join(HERE, "stage2", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    np.savez(os.path.join(RAW, "sanskrit-key", "stage2_permutation_shares.npz"), n1=n1, n0=n0)
    print(json.dumps({k: out[k] for k in ("population", "key_readable_share", "N1_frequency_stratified",
                                          "N1_share_of_permutations_at_or_above_key")}, indent=1))
    print(json.dumps(out["heldout_sanskrit_word_spans"]))
    print(json.dumps({L: {k: v for k, v in d.items() if k in ("mw_m1", "mw_m2", "mw_m1_glosscap", "dcs_m2")}
                      for L, d in by_len.items()}))


if __name__ == "__main__":
    main()
