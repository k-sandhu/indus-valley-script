"""Stage 5 (exploratory power analysis): would these tests recognize a real homophonic encoding?

Held-out text of a known language is encoded into a synthetic corpus shaped like the unique Indus
texts: the same number of texts, the same length distribution, 577 sign types with the Indus token
frequencies, and a homophonic key that gives each sign one consonant class with token quotas matched
to the language. The Stage 3g procedure then runs unchanged on the synthetic corpus: the true key's
order gain and its percentile among within-stratum permutations, constrained annealing from random
token-matched starts under each of four language models, key recovery, and transfer from half A to
half B. Comparing these values with the real Indus results shows what a successful phonetic key
would look like on these measures and whether the corpus size can separate the languages.
"""
import json
import math
import os
import time
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np

from common import HERE, frequency_strata, unique_texts
from stage3_fit import split_half
from stage3e_languages import Lang
from stage3g_constrained import StrataSwapAnnealer, token_matched

SEED = 20261012 + 5000
NAMES = ["sanskrit", "latin", "tamil", "sumerian"]

_LANG = {}


def _init(langs):
    _LANG.update(langs)


def make_corpus(lang, ivs_texts, rng):
    """Encode held-out spans of `lang` with a token-matched homophonic key over Indus sign frequencies."""
    sign_freq = Counter(s for t in ivs_texts for s in t)
    strata = frequency_strata(ivs_texts)
    key = token_matched(lang, ivs_texts, rng, strata)  # sign -> class, randomized within strata
    by_class = defaultdict(list)
    for s, c in key.items():
        by_class[c].append(s)
    choice = {c: (np.array(ss), np.array([sign_freq[s] for s in ss], dtype=float) / sum(sign_freq[s] for s in ss))
              for c, ss in by_class.items()}
    lengths = [len(t) for t in ivs_texts]
    lines = [ln for ln in lang.held_lines if sum(len(w) for w in ln) >= 2]
    texts = []
    seen = set()
    attempts = 0
    while len(texts) < len(ivs_texts) and attempts < 200000:
        attempts += 1
        L = lengths[len(texts)]
        ln = lines[rng.integers(len(lines))]
        start = rng.integers(len(ln))
        cons = [c for w in ln[start:] for c in w][:L]
        if len(cons) < L or any(c not in choice for c in cons):
            continue
        signs = []
        for c in cons:
            ss, p = choice[c]
            signs.append(str(ss[rng.choice(len(ss), p=p)]))
        t = tuple(signs)
        if t in seen:
            continue
        seen.add(t)
        texts.append((t, tuple(cons)))
    return key, texts


def job(args):
    plain, model, label, seed, fit, evals, true_key, steps = args
    lang = _LANG[model]
    rng = np.random.default_rng(seed)
    all_texts = fit if not evals else sorted({t for ts in list(evals.values()) + [fit] for t in ts})
    strata = frequency_strata(all_texts)
    start = token_matched(lang, all_texts, rng, strata)

    def score(text, v):
        return lang.score([v[s] for s in text])

    ann = StrataSwapAnnealer(fit, start, strata, score, rng)
    g0 = ann.G()
    ann.run(steps)
    res = {"plaintext": plain, "model": model, "label": label, "seed": seed, "G_start": g0, "G_fit": ann.G()}
    for k, ts in evals.items():
        res["eval_" + k] = lang.stats([[ann.v[s] for s in t] for t in ts])["G"]
    if model == plain and true_key is not None:
        cnt = Counter(s for t in fit for s in t)
        tot = sum(cnt.values())
        res["token_recovery"] = sum(n for s, n in cnt.items() if ann.v[s] == true_key[s]) / tot
        res["type_recovery"] = sum(1 for s in cnt if ann.v[s] == true_key[s]) / len(cnt)
    return res


def null_job(args):
    model, seed, texts, B = args
    lang = _LANG[model]
    rng = np.random.default_rng(seed)
    strata = frequency_strata(texts)
    v = token_matched(lang, texts, rng, strata)
    return model, lang.stats([[v[s] for s in t] for t in texts])["G"], lang.stats([[v[s] for s in t] for t in B])["G"]


def main():
    t0 = time.time()
    steps = int(os.environ.get("ANNEAL_STEPS", "300000"))
    workers = int(os.environ.get("WORKERS", "8"))
    ivs = unique_texts(min_len=2)
    langs = {n: Lang(n) for n in NAMES}
    print("languages built", round(time.time() - t0, 1), flush=True)
    rng = np.random.default_rng(SEED)
    corpora = {}
    out = {"steps": steps, "plaintexts": {}}
    for n in NAMES:
        key, pairs = make_corpus(langs[n], ivs, rng)
        texts = [p[0] for p in pairs]
        corpora[n] = (key, texts)
        L = langs[n]
        true = L.stats([[key[s] for s in t] for t in texts])
        strata = frequency_strata(texts)
        perm_g = []
        for i in range(200):
            r = np.random.default_rng(SEED + 100 + i)
            groups = defaultdict(list)
            for s in key:
                if s in strata:
                    groups[strata[s]].append(s)
            pk = dict(key)
            for g in groups.values():
                vals = [key[s] for s in g]
                for s, k in zip(g, r.permutation(len(g))):
                    pk[s] = vals[k]
            perm_g.append(L.stats([[pk[s] for s in t] for t in texts])["G"])
        perm_g = np.array(perm_g)
        out["plaintexts"][n] = {
            "texts": len(texts), "sign_types": len({s for t in texts for s in t}),
            "true_key_G": true["G"],
            "permuted_true_key": {"mean": float(perm_g.mean()), "sd": float(perm_g.std()),
                                  "max": float(perm_g.max()), "share_ge_true": float((perm_g >= true["G"]).mean())},
        }
        print(n, out["plaintexts"][n], flush=True)
    for L in langs.values():
        L.train = None
        L.held_lines = None

    jobs, nulls = [], []
    for plain in NAMES:
        key, texts = corpora[plain]
        A, B = split_half(texts)
        for model in NAMES:
            for r in range(3):
                jobs.append((plain, model, "fitA", SEED + 1000 * NAMES.index(plain) + 10 * NAMES.index(model) + r,
                             A, {"A": A, "B": B}, None, steps))
            nulls += [(model, SEED + 70000 + 1000 * NAMES.index(plain) + 50 * NAMES.index(model) + i, texts, B)
                      for i in range(30)]
        for r in range(2):
            jobs.append((plain, plain, "fit_all_recovery", SEED + 9000 + 10 * NAMES.index(plain) + r, texts,
                         {"all": texts}, key, steps))
    with Pool(workers, initializer=_init, initargs=(langs,)) as pool:
        null_res = pool.map(null_job, nulls, chunksize=5)
        runs = pool.map(job, jobs, chunksize=1)
    # attach nulls per (plaintext, model)
    k = 0
    null_tab = {}
    for plain in NAMES:
        for model in NAMES:
            chunk = null_res[k:k + 30]
            k += 30
            null_tab[f"{plain}|{model}"] = {"mean_all": float(np.mean([c[1] for c in chunk])),
                                           "sd_all": float(np.std([c[1] for c in chunk])),
                                           "mean_B": float(np.mean([c[2] for c in chunk])),
                                           "sd_B": float(np.std([c[2] for c in chunk]))}
    out["nulls"] = null_tab
    out["runs"] = runs
    out["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(HERE, "stage5"), exist_ok=True)
    with open(os.path.join(HERE, "stage5", "summary.json"), "w") as f:
        json.dump(out, f, indent=1)
    for r in runs:
        print(r["plaintext"], r["model"], r["label"], round(r["G_fit"], 3),
              {kk: round(v, 3) for kk, v in r.items() if kk.startswith("eval_") or kk.endswith("recovery")})
    print(json.dumps(null_tab, indent=0))


if __name__ == "__main__":
    main()
