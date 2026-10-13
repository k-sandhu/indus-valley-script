"""Stage 3g (post-outcome repair of Stage 3e): constrained optimization that keeps letter frequencies.

Stage 3e's free assignment let the optimizer place most signs on a rare class, where the order-gain
statistic is inflated by the unigram term (Latin reached 8.5 bits per consonant). This stage removes
that route. Swaps are allowed only between signs in the same frequency stratum, so the token-level
class distribution stays close to the starting one.

Part 1, Sanskrit with the key's own option multiset: the start is a frequency-stratified permutation
(an N1 draw), so the search explores exactly the space that N1 samples.

Part 2, four languages: each starts from a token-matched single-class assignment (signs in descending
frequency take the class with the largest remaining token quota under that language's unigram),
randomized by permutation within strata, then optimized by within-stratum swaps. Fifty random starts
per language give that space's null distribution.
"""
import json
import math
import os
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

import stage3_fit as s3
from common import HERE, RAW, frequency_strata, key_options, permuted_options, unique_texts
from stage3e_languages import Lang
from stage3_fit import scramble, split_half

SEED = 20261012 + 900


class StrataSwapAnnealer:
    """Swap annealing restricted to sign pairs in the same frequency stratum.

    `score(text, values)` returns (llr, ll, n); values map sign -> value usable by score.
    """

    def __init__(self, texts, values, strata, score, rng):
        self.texts, self.v, self.score, self.rng = texts, dict(values), score, rng
        signs = sorted({s for t in texts for s in t})
        groups = defaultdict(list)
        for s in signs:
            groups[strata[s]].append(s)
        self.groups = [g for g in groups.values() if len(g) > 1]
        self.weights = np.array([len(g) for g in self.groups], dtype=float)
        self.weights /= self.weights.sum()
        self.where = {s: [] for s in signs}
        for i, t in enumerate(texts):
            for s in set(t):
                self.where[s].append(i)
        self.cache = [score(t, self.v) for t in texts]
        self.A = sum(c[0] for c in self.cache)
        self.N = sum(c[2] for c in self.cache)

    def G(self):
        return self.A / self.N

    def run(self, steps, t0=2e-3, t1=2e-6):
        rng = self.rng
        lr = math.log(t1 / t0)
        acc = 0
        for step in range(steps):
            temp = t0 * math.exp(lr * step / steps)
            g = self.groups[rng.choice(len(self.groups), p=self.weights)]
            i, j = rng.integers(len(g)), rng.integers(len(g))
            if i == j:
                continue
            a, b = g[i], g[j]
            if self.v[a] == self.v[b]:
                continue
            self.v[a], self.v[b] = self.v[b], self.v[a]
            dA = dN = 0.0
            upd = {}
            for k in set(self.where[a]) | set(self.where[b]):
                sc = self.score(self.texts[k], self.v)
                upd[k] = sc
                dA += sc[0] - self.cache[k][0]
                dN += sc[2] - self.cache[k][2]
            delta = (self.A + dA) / (self.N + dN) - self.A / self.N
            if delta >= 0 or rng.random() < math.exp(delta / temp):
                self.A += dA
                self.N += dN
                for k, sc in upd.items():
                    self.cache[k] = sc
                acc += 1
            else:
                self.v[a], self.v[b] = self.v[b], self.v[a]
        return acc


# ----------------------------------------------------------------------------- part 1: key multiset

def key_score(text, v):
    return s3.score_text(text, v)


def job_key(args):
    s3.load_model()
    label, seed, fit, evals, options, strata, steps = args
    rng = np.random.default_rng(seed)
    signs = sorted({s for t in fit for s in t} | {s for ts in evals.values() for t in ts for s in t})
    start = s3.to_int(permuted_options(options, signs, strata, rng))
    ann = StrataSwapAnnealer(fit, start, strata, key_score, rng)
    g0 = ann.G()
    acc = ann.run(steps)
    res = {"part": "key_multiset", "label": label, "seed": seed, "G_start": g0, "G_fit": ann.G(), "accepted": acc}
    for k, ts in evals.items():
        res["eval_" + k] = s3.corpus_stats(ts, ann.v)
    return res


# ----------------------------------------------------------------------------- part 2: languages

_LANG = {}


def _init(langs):
    _LANG.update(langs)


def token_matched(lang, texts, rng, strata):
    cnt = defaultdict(int)
    for t in texts:
        for s in t:
            cnt[s] += 1
    total = sum(cnt.values())
    quota = np.array(lang.p1) * total
    assign = {}
    for s in sorted(cnt, key=lambda x: (-cnt[x], x)):
        c = int(np.argmax(quota))
        assign[s] = c
        quota[c] -= cnt[s]
    # randomize within strata
    groups = defaultdict(list)
    for s in assign:
        groups[strata[s]].append(s)
    out = dict(assign)
    for g in groups.values():
        vals = [assign[s] for s in g]
        perm = rng.permutation(len(g))
        for s, k in zip(g, perm):
            out[s] = vals[k]
    return out


def lang_score_factory(lang):
    def score(text, v):
        return lang.score([v[s] for s in text])
    return score


def job_lang(args):
    name, label, seed, fit, evals, strata, steps, all_texts = args
    lang = _LANG[name]
    rng = np.random.default_rng(seed)
    start = token_matched(lang, all_texts, rng, strata)
    score = lang_score_factory(lang)
    ann = StrataSwapAnnealer(fit, start, strata, score, rng)
    g0 = ann.G()
    acc = ann.run(steps)
    res = {"part": "language", "language": name, "label": label, "seed": seed, "G_start": g0, "G_fit": ann.G(),
           "accepted": acc}
    for k, ts in evals.items():
        res["eval_" + k] = lang.stats([[ann.v[s] for s in t] for t in ts])
    return res


def job_lang_null(args):
    name, seed, texts, strata, A, B = args
    lang = _LANG[name]
    rng = np.random.default_rng(seed)
    v = token_matched(lang, texts, rng, strata)
    return {"language": name, "all": lang.stats([[v[s] for s in t] for t in texts])["G"],
            "B": lang.stats([[v[s] for s in t] for t in B])["G"]}


def main():
    t0 = time.time()
    steps = int(os.environ.get("ANNEAL_STEPS", "300000"))
    workers = int(os.environ.get("WORKERS", "8"))
    texts = unique_texts(min_len=2)
    A, B = split_half(texts)
    strata = frequency_strata(texts)
    options = key_options()
    out = {"steps": steps}

    # part 1
    jobs = [("real", SEED + r, texts, {"all": texts}, options, strata, steps) for r in range(4)]
    for k in range(2):
        sc = scramble(texts, SEED + 2000 + k)
        jobs += [(f"scrambled{k}", SEED + 3000 + 10 * k + r, sc, {"scrambled": sc, "real": texts}, options, strata,
                  steps) for r in range(2)]
    jobs += [("fitA", SEED + 4000 + r, A, {"A": A, "B": B}, options, strata, steps) for r in range(4)]
    with Pool(workers) as pool:
        out["key_multiset"] = pool.map(job_key, jobs, chunksize=1)
    print("part1", round(time.time() - t0, 1), flush=True)
    for r in out["key_multiset"]:
        print(r["label"], round(r["G_start"], 3), round(r["G_fit"], 3),
              {k: round(v["G"], 3) for k, v in r.items() if k.startswith("eval_")}, flush=True)

    # part 2
    names = ["sanskrit", "latin", "tamil", "sumerian"]
    langs = {n: Lang(n) for n in names}
    rng = np.random.default_rng(SEED + 77)
    out["languages"] = {}
    for n, L in langs.items():
        refs = L.references([len(t) for t in texts], rng)
        out["languages"][n] = {"classes": "".join(L.classes), "heldout_cross_entropy": L.heldout_H,
                               "references": refs}
        L.train = None
        L.held_lines = None
    print("languages built", round(time.time() - t0, 1), flush=True)
    jobs2 = []
    for n in names:
        jobs2 += [(n, "real", SEED + 100 * r + 1, texts, {"all": texts}, strata, steps, texts) for r in range(3)]
        jobs2 += [(n, "fitA", SEED + 100 * r + 2, A, {"A": A, "B": B}, strata, steps, texts) for r in range(3)]
        for k in range(2):
            sc = scramble(texts, SEED + 2000 + k)
            jobs2.append((n, "scrambled", SEED + 100 * k + 3, sc, {"scrambled": sc, "real": texts}, strata, steps, texts))
    nulls = [(n, SEED + 50000 + i, texts, strata, A, B) for n in names for i in range(50)]
    with Pool(workers, initializer=_init, initargs=(langs,)) as pool:
        null_res = pool.map(job_lang_null, nulls, chunksize=5)
        out["language_runs"] = pool.map(job_lang, jobs2, chunksize=1)
    for n in names:
        allv = np.array([r["all"] for r in null_res if r["language"] == n])
        bv = np.array([r["B"] for r in null_res if r["language"] == n])
        out["languages"][n]["null_token_matched"] = {"mean_all": float(allv.mean()), "sd_all": float(allv.std()),
                                                     "mean_B": float(bv.mean()), "sd_B": float(bv.std())}
    out["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.join(HERE, "stage3g"), exist_ok=True)
    with open(os.path.join(HERE, "stage3g", "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for n in names:
        d = out["languages"][n]
        print(n, {k: round(v["G"], 3) for k, v in d["references"].items()}, d["null_token_matched"])
    for r in out["language_runs"]:
        print(r["language"], r["label"], round(r["G_start"], 3), round(r["G_fit"], 3),
              {k: round(v["G"], 3) for k, v in r.items() if k.startswith("eval_")})


if __name__ == "__main__":
    main()
