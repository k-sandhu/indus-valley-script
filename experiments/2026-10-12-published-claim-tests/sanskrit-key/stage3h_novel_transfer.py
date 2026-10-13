"""Review response (Amendment 4): transfer to half-B texts without near-duplicates in half A.

The review found that 334 of 927 half-B texts lie within one edit of a half-A text and 84 are
substrings of longer half-A texts. 'Novel' B keeps only texts with no half-A text within one
substitution, insertion or deletion and that are not contiguous substrings of a half-A text. For the
real corpus and for the Stage 5 synthetic corpora (regenerated with the same seed), constrained
annealing on half A (Stage 3g procedure, same seeds) is scored on all of B and on novel B, against 30
token-matched random starts scored on the same sets.
"""
import json
import os
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

from common import HERE, frequency_strata, unique_texts
from stage3_fit import split_half
from stage3e_languages import Lang
from stage3g_constrained import StrataSwapAnnealer, token_matched
from stage5_power import NAMES, SEED as S5SEED, make_corpus

SEED = 20261012 + 900  # Stage 3g seed base


def deletion_keys(t):
    keys = {t}
    for i in range(len(t)):
        keys.add(t[:i] + t[i + 1:])
    return keys


def novel_B(A, B):
    index = defaultdict(set)
    for i, t in enumerate(A):
        for k in deletion_keys(t):
            index[k].add(i)
    joined = ["|" + "|".join(t) + "|" for t in A]
    out = []
    near = sub = 0
    for t in B:
        close = any(index.get(k) for k in deletion_keys(t))
        s = "|" + "|".join(t) + "|"
        contained = any(s in j for j in joined)
        near += close
        sub += contained
        if not close and not contained:
            out.append(t)
    return out, {"B": len(B), "within_one_edit_of_A": near, "substring_of_A": sub, "novel": len(out)}


_LANG = {}


def _init(langs):
    _LANG.update(langs)


def fit_job(args):
    corpus, model, seed, A, evals, steps = args
    lang = _LANG[model]
    rng = np.random.default_rng(seed)
    allt = sorted({t for ts in list(evals.values()) + [A] for t in ts})
    strata = frequency_strata(allt)
    start = token_matched(lang, allt, rng, strata)

    def score(text, v):
        return lang.score([v[s] for s in text])

    ann = StrataSwapAnnealer(A, start, strata, score, rng)
    ann.run(steps)
    return {"corpus": corpus, "model": model, "seed": seed,
            **{k: lang.stats([[ann.v[s] for s in t] for t in ts])["G"] for k, ts in evals.items()}}


def null_job(args):
    corpus, model, seed, allt, evals = args
    lang = _LANG[model]
    rng = np.random.default_rng(seed)
    v = token_matched(lang, allt, rng, frequency_strata(allt))
    return {"corpus": corpus, "model": model,
            **{k: lang.stats([[v[s] for s in t] for t in ts])["G"] for k, ts in evals.items()}}


def main():
    t0 = time.time()
    steps = int(os.environ.get("ANNEAL_STEPS", "300000"))
    ivs = unique_texts(min_len=2)
    langs = {n: Lang(n) for n in NAMES}
    rng5 = np.random.default_rng(S5SEED)
    corpora = {"indus": ivs}
    for n in NAMES:
        _, pairs = make_corpus(langs[n], ivs, rng5)
        corpora[f"synthetic_{n}"] = [p[0] for p in pairs]
    for L in langs.values():
        L.train = None
        L.held_lines = None
    out = {"steps": steps, "splits": {}}
    fits, nulls = [], []
    for cname, texts in corpora.items():
        A, B = split_half(texts)
        Bn, info = novel_B(A, B)
        out["splits"][cname] = info
        evals = {"B": B, "B_novel": Bn}
        for mi, m in enumerate(NAMES):
            for r in range(3):
                fits.append((cname, m, SEED + 100 * r + 2 + 7 * mi, A, evals, steps))
            for i in range(30):
                nulls.append((cname, m, SEED + 60000 + 100 * mi + i, texts, evals))
    print("splits", out["splits"], round(time.time() - t0, 1), flush=True)
    with Pool(int(os.environ.get("WORKERS", "8")), initializer=_init, initargs=(langs,)) as pool:
        null_res = pool.map(null_job, nulls, chunksize=10)
        fit_res = pool.map(fit_job, fits, chunksize=1)
    table = {}
    for cname in corpora:
        table[cname] = {}
        for m in NAMES:
            nr = [r for r in null_res if r["corpus"] == cname and r["model"] == m]
            fr = [r for r in fit_res if r["corpus"] == cname and r["model"] == m]
            row = {}
            for k in ("B", "B_novel"):
                mu, sd = float(np.mean([r[k] for r in nr])), float(np.std([r[k] for r in nr]))
                g = float(np.mean([r[k] for r in fr]))
                row[k] = {"fit_mean": g, "null_mean": mu, "null_sd": sd, "z": (g - mu) / sd}
            table[cname][m] = row
    out["transfer"] = table
    out["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, "stage3g", "novel_transfer.json"), "w") as f:
        json.dump(out, f, indent=1)
    for cname, rows in table.items():
        print(cname, {m: (round(r["B"]["z"], 1), round(r["B_novel"]["z"], 1)) for m, r in rows.items()})


if __name__ == "__main__":
    main()
