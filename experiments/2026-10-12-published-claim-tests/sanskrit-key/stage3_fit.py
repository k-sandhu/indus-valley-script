"""Stage 3: sequential Sanskrit-likeness of the key, permuted keys and optimized keys.

Order gain G = sum over texts [log2 P5(s) - log2 P1(s)] / sum |s|, with P5 the order-5 skeleton
Kneser-Ney model (start-padded) and P1 the class unigram, both trained on DCS text.
Optimized keys are found by simulated annealing over value swaps between signs, which keeps
the key's exact multiset of value options.
"""
import hashlib
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

from common import (CID, HERE, NC, RAW, dcs_lines, dcs_split, encode, frequency_strata, iast_skeleton,
                    key_options, permuted_options, unique_texts)

MODEL = os.path.join(RAW, "sanskrit-key", "models", "skeleton_kn5.npz")
SEED = 20261012
BASE = NC + 1
MOD = BASE ** 4

_T = None
_U = None


def load_model():
    global _T, _U
    if _T is None:
        z = np.load(MODEL)
        _T = z["table"].tolist()  # nested lists are faster than numpy scalars in pure Python loops
        _U = np.log2(z["unigram"]).tolist()
    return _T, _U


def bos_ctx() -> int:
    c = 0
    for _ in range(4):
        c = c * BASE + NC
    return c


BOS_CTX = bos_ctx()


def score_text(text, opts_int):
    """Greedy choice among a sign's options; returns (llr, ll, n)."""
    T, U = _T, _U
    ctx = BOS_CTX
    llr = ll = 0.0
    n = 0
    for sign in text:
        options = opts_int[sign]
        if len(options) == 1:
            seq = options[0]
        else:
            best = None
            for seqo in options:
                c = ctx
                v = 0.0
                for x in seqo:
                    v += T[c][x] - U[x]
                    c = (c * BASE + x) % MOD
                if best is None or v > best[0]:
                    best = (v, seqo)
            seq = best[1]
        for x in seq:
            lp = T[ctx][x]
            ll += lp
            llr += lp - U[x]
            ctx = (ctx * BASE + x) % MOD
            n += 1
    return llr, ll, n


def to_int(options):
    return {s: tuple(tuple(CID[c] for c in o) for o in v) for s, v in options.items()}


def corpus_stats(texts, opts_int):
    a = b = 0.0
    n = 0
    for t in texts:
        x, y, k = score_text(t, opts_int)
        a += x
        b += y
        n += k
    return {"G": a / n if n else 0.0, "LL": b / n if n else 0.0, "n": n}


class Annealer:
    def __init__(self, texts, opts_int, rng):
        self.texts = texts
        self.opts = dict(opts_int)
        self.rng = rng
        self.signs = sorted({s for t in texts for s in t})
        self.where = {s: [] for s in self.signs}
        for i, t in enumerate(texts):
            for s in set(t):
                self.where[s].append(i)
        self.cache = [score_text(t, self.opts) for t in texts]
        self.A = sum(c[0] for c in self.cache)
        self.N = sum(c[2] for c in self.cache)

    def G(self):
        return self.A / self.N

    def run(self, steps, t_start, t_end):
        signs = self.signs
        ns = len(signs)
        rng = self.rng
        accepted = 0
        log_ratio = math.log(t_end / t_start)
        for step in range(steps):
            temp = t_start * math.exp(log_ratio * step / steps)
            i, j = rng.integers(ns), rng.integers(ns)
            if i == j:
                continue
            a, b = signs[i], signs[j]
            if self.opts[a] == self.opts[b]:
                continue
            affected = set(self.where[a]) | set(self.where[b])
            self.opts[a], self.opts[b] = self.opts[b], self.opts[a]
            dA = dN = 0.0
            new = {}
            for k in affected:
                sc = score_text(self.texts[k], self.opts)
                new[k] = sc
                dA += sc[0] - self.cache[k][0]
                dN += sc[2] - self.cache[k][2]
            g_old = self.A / self.N
            g_new = (self.A + dA) / (self.N + dN)
            delta = g_new - g_old
            if delta >= 0 or rng.random() < math.exp(delta / temp):
                self.A += dA
                self.N += dN
                for k, sc in new.items():
                    self.cache[k] = sc
                accepted += 1
            else:
                self.opts[a], self.opts[b] = self.opts[b], self.opts[a]
        return accepted


def scramble(texts, seed):
    rng = np.random.default_rng(seed)
    out = []
    for t in texts:
        p = rng.permutation(len(t))
        out.append(tuple(t[k] for k in p))
    return out


def split_half(texts):
    a, b = [], []
    for t in texts:
        h = hashlib.md5("-".join(t).encode()).digest()[0]
        (a if h % 2 == 0 else b).append(t)
    return a, b


# ----------------------------------------------------------------------------- jobs

def job_perm(args):
    load_model()
    seed, uniform, texts, options, signs, strata = args
    rng = np.random.default_rng(seed)
    perm = permuted_options(options, signs, None if uniform else strata, rng)
    return corpus_stats(texts, to_int(perm))


def job_anneal(args):
    load_model()
    label, seed, fit_texts, eval_sets, options, signs, strata, steps = args
    rng = np.random.default_rng(seed)
    start = permuted_options(options, signs, strata, rng)
    ann = Annealer(fit_texts, to_int(start), rng)
    g0 = ann.G()
    acc = ann.run(steps, 2e-3, 2e-6)
    res = {"label": label, "seed": seed, "steps": steps, "accepted": acc, "G_start": g0, "G_fit": ann.G()}
    for name, ts in eval_sets.items():
        res["eval_" + name] = corpus_stats(ts, ann.opts)
    # keep the optimized assignment for later inspection (sign -> option tuple)
    res["assignment"] = {s: ["".join("kgcjtdnpbmyrlvs"[x] for x in o) for o in ann.opts[s]] for s in ann.signs}
    return res


def _score_skeletons(skels):
    texts = [tuple(str(x) for x in s) for s in skels if s]
    opts = {str(x): ((x,),) for x in range(NC)}
    st = corpus_stats(texts, opts)
    st["texts"] = len(texts)
    st["mean_consonants"] = float(np.mean([len(s) for s in skels if s]))
    return st


def sanskrit_span_reference(key_lengths):
    """Order gain of held-out Sanskrit spans scored from a start symbol, and of i.i.d. letter strings.

    Line-initial spans match the scoring of inscriptions, which also begin at the start symbol.
    Mid-line spans begin at a word boundary inside a line. The i.i.d. strings follow the class
    unigram and the key's skeleton-length distribution.
    """
    load_model()
    rng = np.random.default_rng(SEED + 11)
    out = {"line_initial": {}, "mid_line": {}}
    held = dcs_split()["heldout"]
    lines = [l for p in held for l in dcs_lines(p)]
    for k in (1, 2, 3, 4):
        initial, mid = [], []
        for line in lines:
            ws = [w for w in line.split() if iast_skeleton(w)]
            if len(ws) >= k:
                initial.append(tuple(encode(iast_skeleton("".join(ws[:k])))))
            for i in range(1, max(1, len(ws) - k + 1), 5):
                mid.append(tuple(encode(iast_skeleton("".join(ws[i:i + k])))))
        for name, spans in (("line_initial", initial), ("mid_line", mid)):
            idx = rng.choice(len(spans), size=min(5000, len(spans)), replace=False)
            out[name][str(k)] = _score_skeletons([spans[i] for i in idx])
    p1 = np.exp2(np.array(_U))
    p1 = p1 / p1.sum()
    iid = [tuple(rng.choice(NC, size=L, p=p1)) for L in key_lengths if L > 0]
    out["iid_unigram_strings_key_lengths"] = _score_skeletons(iid)
    return out


def published_reading_reference():
    """Skeletons of the published readings (with their inserted consonants), unique by skeleton."""
    path = os.path.join(RAW, "sanskrit-key", "stage0_rows.jsonl")
    seen = set()
    sk = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            s = r["reading_skeleton"]
            if r["length"] >= 2 and s and s not in seen:
                seen.add(s)
                sk.append(tuple(encode(s)))
    return _score_skeletons(sk)


def main():
    t0 = time.time()
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    load_model()
    texts = unique_texts(min_len=2)
    options = key_options()
    signs = sorted({s for t in texts for s in t})
    strata = frequency_strata(texts)
    outdir = os.path.join(HERE, "stage3")
    os.makedirs(outdir, exist_ok=True)
    local = os.path.join(RAW, "sanskrit-key")

    longest = sorted(texts, key=lambda t: (-len(t), t))[:50]
    A, B = split_half(texts)
    key_int = to_int(options)
    summary = {
        "population": {"unique_texts": len(texts), "signs": len(signs), "half_A": len(A), "half_B": len(B),
                       "longest50_min_length": len(longest[-1])},
        "key": {"all": corpus_stats(texts, key_int), "A": corpus_stats(A, key_int), "B": corpus_stats(B, key_int),
                "longest50": corpus_stats(longest, key_int)},
    }
    key_lengths = []
    for t in texts:
        key_lengths.append(score_text(t, key_int)[2])
    summary["sanskrit_word_span_reference"] = sanskrit_span_reference(key_lengths)
    summary["published_reading_skeletons"] = published_reading_reference()
    print("key", summary["key"], flush=True)
    print("reference", summary["sanskrit_word_span_reference"], flush=True)

    with Pool(20) as pool:
        # permutation nulls on the full population and on the evaluation subsets
        perm_jobs = [(SEED + i, False, texts, options, signs, strata) for i in range(1000)]
        perm_jobs += [(SEED + 50000 + i, True, texts, options, signs, strata) for i in range(200)]
        perm_jobs += [(SEED + 60000 + i, False, B, options, signs, strata) for i in range(300)]
        perm_jobs += [(SEED + 70000 + i, False, longest, options, signs, strata) for i in range(300)]
        res = pool.map(job_perm, perm_jobs, chunksize=5)
        n1 = np.array([[r["G"], r["LL"]] for r in res[:1000]])
        n0 = np.array([[r["G"], r["LL"]] for r in res[1000:1200]])
        n1B = np.array([[r["G"], r["LL"]] for r in res[1200:1500]])
        n1L = np.array([[r["G"], r["LL"]] for r in res[1500:1800]])
        print("perms", round(time.time() - t0, 1), flush=True)

        def summ(arr, keyval):
            return {"mean_G": float(arr[:, 0].mean()), "sd_G": float(arr[:, 0].std()),
                    "p97.5_G": float(np.percentile(arr[:, 0], 97.5)), "max_G": float(arr[:, 0].max()),
                    "share_ge_key_G": float((arr[:, 0] >= keyval["G"]).mean()),
                    "mean_LL": float(arr[:, 1].mean()), "share_ge_key_LL": float((arr[:, 1] >= keyval["LL"]).mean())}

        summary["N1_all"] = summ(n1, summary["key"]["all"])
        summary["N0_all"] = summ(n0, summary["key"]["all"])
        summary["N1_B"] = summ(n1B, summary["key"]["B"])
        summary["N1_longest50"] = summ(n1L, summary["key"]["longest50"])
        print({k: summary[k] for k in ("N1_all", "N0_all", "N1_B", "N1_longest50")}, flush=True)

        steps = int(os.environ.get("ANNEAL_STEPS", "400000"))
        jobs = []
        for r in range(8):
            jobs.append(("real", SEED + 1000 + r, texts, {"all": texts}, options, signs, strata, steps))
        for k in range(3):
            sc = scramble(texts, SEED + 2000 + k)
            for r in range(2):
                jobs.append((f"scrambled{k}", SEED + 3000 + 10 * k + r, sc, {"scrambled": sc, "real": texts},
                             options, signs, strata, steps))
        for r in range(4):
            jobs.append(("fitA", SEED + 4000 + r, A, {"A": A, "B": B}, options, signs, strata, steps))
        for r in range(4):
            jobs.append(("longest50", SEED + 5000 + r, longest, {"longest50": longest, "all": texts}, options,
                         signs, strata, steps))
        ann = pool.map(job_anneal, jobs, chunksize=1)
    print("anneal", round(time.time() - t0, 1), flush=True)
    with open(os.path.join(local, "stage3_assignments.json"), "w", encoding="utf-8") as f:
        json.dump(ann, f)
    summary["anneal"] = [{k: v for k, v in r.items() if k != "assignment"} for r in ann]
    summary["seconds"] = round(time.time() - t0, 1)
    with open(os.path.join(outdir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    np.savez(os.path.join(local, "stage3_null_arrays.npz"), n1=n1, n0=n0, n1B=n1B, n1L=n1L)
    for r in summary["anneal"]:
        print(r, flush=True)


if __name__ == "__main__":
    main()
