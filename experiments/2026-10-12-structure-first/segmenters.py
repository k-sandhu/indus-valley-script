"""Unsupervised segmenters and alternation statistics shared by steps 3 and 5.

Every function takes texts as tuples of unit labels and returns, for each text, a
sorted list of internal boundary positions i (a boundary between t[i-1] and t[i]).
"""
import collections
import math
import random

START, END = "<s>", "</s>"


# ------------------------------------------------------------------ branching entropy
def _entropy(counter):
    n = sum(counter.values())
    return -sum(v / n * math.log2(v / n) for v in counter.values()) if n else 0.0


def branching_entropy(texts):
    nxt = collections.defaultdict(collections.Counter)
    for t in texts:
        s = (START,) + tuple(t) + (END,)
        for i in range(1, len(s)):
            nxt[(s[i - 1],)][s[i]] += 1
            if i >= 2:
                nxt[(s[i - 2], s[i - 1])][s[i]] += 1
    H = {k: _entropy(v) for k, v in nxt.items()}
    out = []
    for t in texts:
        s = (START,) + tuple(t)
        b = []
        for i in range(1, len(t)):
            j = i + 1  # index in s of the sign after the candidate boundary
            rises = []
            rises.append(H.get((s[j - 1],), 0.0) - H.get((s[j - 2],), 0.0))
            if j >= 3:
                rises.append(H.get((s[j - 2], s[j - 1]), 0.0) - H.get((s[j - 3], s[j - 2]), 0.0))
            if sum(rises) / len(rises) > 0:
                b.append(i)
        out.append(b)
    return out


# ------------------------------------------------------------------ greedy n-gram
def greedy_ngram(texts, min_texts=3, nmax=4):
    seen = collections.Counter()
    for t in set(map(tuple, texts)):
        grams = set()
        for n in range(2, nmax + 1):
            for i in range(len(t) - n + 1):
                grams.add(t[i:i + n])
        seen.update(grams)
    freq = {g for g, c in seen.items() if c >= min_texts}
    out = []
    for t in texts:
        i, b = 0, []
        while i < len(t):
            step = 1
            for n in range(min(nmax, len(t) - i), 1, -1):
                if tuple(t[i:i + n]) in freq:
                    step = n
                    break
            i += step
            if i < len(t):
                b.append(i)
        out.append(b)
    return out


# ------------------------------------------------------------------ DP unigram (Goldwater et al. 2009)
class DPSeg:
    def __init__(self, texts, alpha=20.0, p_boundary=0.5, rho=2.0, seed=20261014):
        self.texts = [tuple(t) for t in texts]
        self.alpha = alpha
        self.pb = p_boundary
        self.rho = rho
        self.inv = len({u for t in self.texts for u in t})
        self.rng = random.Random(seed)
        self.counts = collections.Counter()
        self.n = 0
        self.nu = 0  # utterance-final words
        self.bounds = []
        for t in self.texts:
            b = [i for i in range(1, len(t)) if self.rng.random() < 0.5]
            self.bounds.append(set(b))
            for w in self._words(t, b):
                self.counts[w] += 1
                self.n += 1
            self.nu += 1

    @staticmethod
    def _words(t, b):
        cuts = [0] + sorted(b) + [len(t)]
        return [t[cuts[k]:cuts[k + 1]] for k in range(len(cuts) - 1)]

    def p0(self, w):
        return self.pb * (1 - self.pb) ** (len(w) - 1) * (1.0 / self.inv) ** len(w)

    def sweep(self, temp):
        for ti, t in enumerate(self.texts):
            if len(t) < 2:
                continue
            b = self.bounds[ti]
            for i in range(1, len(t)):
                left = max([x for x in b if x < i], default=0)
                right = min([x for x in b if x > i], default=len(t))
                final = right == len(t)
                w1 = t[left:right]
                w2, w3 = t[left:i], t[i:right]
                # remove current analysis
                if i in b:
                    self.counts[w2] -= 1
                    self.counts[w3] -= 1
                    self.n -= 2
                else:
                    self.counts[w1] -= 1
                    self.n -= 1
                n, a = self.n, self.alpha
                # utterance-final word count after removing the current analysis
                nu = self.nu - 1 if final else self.nu
                # hypothesis 1: no boundary; w1 ends the text if final
                p1 = (self.counts[w1] + a * self.p0(w1)) / (n + a)
                p1 *= ((nu if final else n - nu) + self.rho / 2) / (n + self.rho)
                # hypothesis 2: boundary; w2 never ends the text, w3 does if final
                p2 = (self.counts[w2] + a * self.p0(w2)) / (n + a)
                p2 *= (n - nu + self.rho / 2) / (n + self.rho)
                p2 *= (self.counts[w3] + (1 if w2 == w3 else 0) + a * self.p0(w3)) / (n + 1 + a)
                p2 *= ((nu if final else n - nu + 1) + self.rho / 2) / (n + 1 + self.rho)
                if temp != 1.0:
                    p1, p2 = p1 ** (1 / temp), p2 ** (1 / temp)
                if self.rng.random() < p2 / (p1 + p2):
                    b.add(i)
                    self.counts[w2] += 1
                    self.counts[w3] += 1
                    self.n += 2
                else:
                    b.discard(i)
                    self.counts[w1] += 1
                    self.n += 1

    def run(self, sweeps=2000):
        for s in range(sweeps):
            temp = max(1.0, 10.0 * (1 - s / (0.9 * sweeps)) + 1.0) if s < 0.9 * sweeps else 1.0
            self.sweep(temp)
        return [sorted(b) for b in self.bounds]


def dp_unigram(texts, sweeps=2000, seed=20261014):
    return DPSeg(texts, seed=seed).run(sweeps)


# ------------------------------------------------------------------ evaluation and units
def units(text, bounds):
    cuts = [0] + list(bounds) + [len(text)]
    return [tuple(text[cuts[k]:cuts[k + 1]]) for k in range(len(cuts) - 1)]


def boundary_scores(gold, pred, texts):
    tp = fp = fn = 0
    wt = wp = wc = 0
    for g, p, t in zip(gold, pred, texts):
        g, p = set(g), set(p)
        tp += len(g & p)
        fp += len(p - g)
        fn += len(g - p)
        gw = collections.Counter(_spans(g, len(t)))
        pw = collections.Counter(_spans(p, len(t)))
        wt += sum(gw.values())
        wp += sum(pw.values())
        wc += sum((gw & pw).values())
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    wprec = wc / wp if wp else 0.0
    wrec = wc / wt if wt else 0.0
    wf1 = 2 * wprec * wrec / (wprec + wrec) if wprec + wrec else 0.0
    return {"boundary_precision": prec, "boundary_recall": rec, "boundary_f1": f1,
            "word_precision": wprec, "word_recall": wrec, "word_f1": wf1}


def _spans(b, n):
    cuts = [0] + sorted(b) + [n]
    return [(cuts[k], cuts[k + 1]) for k in range(len(cuts) - 1)]


def alternation(unit_types):
    """Kober-style alternation over distinct units (tuples of signs)."""
    stems = collections.defaultdict(set)
    for u in set(unit_types):
        if len(u) >= 3:
            stems[u[:-1]].add(u[-1])
    alt = {s: f for s, f in stems.items() if len(f) >= 2}
    finals = collections.Counter()
    for f in alt.values():
        for x in f:
            finals[x] += 1
    pairs_total = sum(len(f) for f in alt.values())
    top5 = sum(v for _, v in finals.most_common(5))
    return {"stems": len(stems), "alternating_stems": len(alt),
            "alternation_rate": len(alt) / len(stems) if stems else 0.0,
            "finals_involved": len(finals),
            "top5_final_share": top5 / pairs_total if pairs_total else 0.0}
