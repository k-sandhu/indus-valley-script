"""Review response (Amendment 4): readability reachable by fitting the key's values within strata.

Starting from frequency-stratified permutations of the key's option sets, hill-climbing over
within-stratum swaps maximizes the share of unique texts readable with stems of at least two
consonants (Monier-Williams or DCS lemmas). The key itself reads 96.0% (MW) and 94.8% (DCS).
"""
import json
import os
from collections import defaultdict
from multiprocessing import Pool

import numpy as np

import stage2_readability as s2
from common import HERE, frequency_strata, key_options, permuted_options, unique_texts

SEED = 20261012 + 2200
STEPS = 20000

_LEX = {}


def _init(lex):
    _LEX.update(lex)


def make_ok(lex):
    memo = {}

    def ok(s):
        r = memo.get(s)
        if r is None:
            best = s2.min_stems(s, lex, 2)
            n = len(s)
            r = any(n - len(e) > 0 and s.endswith(e) and best[n - len(e)] < 10 ** 6 for e in s2.ENDINGS)
            memo[s] = r
        return r
    return ok


def text_ok(t, opts, ok):
    combos = [""]
    for x in t:
        combos = [c + o for c in combos for o in opts[x]][:64]
    return any(ok(c) for c in set(combos) if c)


def job(args):
    lexname, seed, texts, options, strata = args
    ok = make_ok(_LEX[lexname])
    rng = np.random.default_rng(seed)
    signs = sorted({x for t in texts for x in t})
    opts = permuted_options(options, signs, strata, rng)
    groups = defaultdict(list)
    for s in signs:
        groups[strata[s]].append(s)
    groups = [g for g in groups.values() if len(g) > 1]
    w = np.array([len(g) for g in groups], dtype=float)
    w /= w.sum()
    where = defaultdict(list)
    for i, t in enumerate(texts):
        for x in set(t):
            where[x].append(i)
    cur = [text_ok(t, opts, ok) for t in texts]
    total = sum(cur)
    start = total / len(texts)
    for _ in range(STEPS):
        g = groups[rng.choice(len(groups), p=w)]
        a, b = g[rng.integers(len(g))], g[rng.integers(len(g))]
        if a == b or opts[a] == opts[b]:
            continue
        opts[a], opts[b] = opts[b], opts[a]
        aff = set(where[a]) | set(where[b])
        new = {k: text_ok(texts[k], opts, ok) for k in aff}
        delta = sum(new.values()) - sum(cur[k] for k in aff)
        if delta >= 0:
            for k, v in new.items():
                cur[k] = v
            total += delta
        else:
            opts[a], opts[b] = opts[b], opts[a]
    return {"lexicon": lexname, "seed": seed, "start_share": start, "fitted_share": total / len(texts)}


def main():
    lex = {"mw": s2.load_mw_skeletons(), "dcs": s2.load_dcs_lemma_skeletons()}
    texts = unique_texts(min_len=2)
    options = key_options()
    strata = frequency_strata(texts)
    jobs = [(name, SEED + 10 * i + k, texts, options, strata) for k, name in enumerate(("mw", "dcs")) for i in range(3)]
    with Pool(6, initializer=_init, initargs=(lex,)) as pool:
        res = pool.map(job, jobs)
    with open(os.path.join(HERE, "stage2", "summary.json"), encoding="utf-8") as f:
        st2 = json.load(f)
    out = {"steps": STEPS, "runs": res,
           "key": {"mw_m2": st2["key_readable_share"]["mw_m2"], "dcs_m2": st2["key_readable_share"]["dcs_m2"]},
           "N1_max": {"mw_m2": st2["N1_frequency_stratified"]["mw_m2"]["max"],
                      "dcs_m2": st2["N1_frequency_stratified"]["dcs_m2"]["max"]}}
    with open(os.path.join(HERE, "stage2", "fitted_readability.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
