"""Adversarial review: check the DPSeg Gibbs conditional against the exact joint probability.

Usage: python -X utf8 check_dpseg.py

Under the Goldwater, Griffiths and Johnson (2009) unigram model the joint probability of a
segmentation is a Chinese-restaurant term over word tokens times a beta-binomial term for
utterance-final versus non-final words. For any boundary site, the Gibbs ratio
P(boundary) / P(no boundary) must equal the ratio of the two joint probabilities. This
script draws random states on a small corpus, computes p1 and p2 with the same formulas as
segmenters.DPSeg.sweep (copied verbatim, temperature 1), and compares p2/p1 with the
brute-force joint ratio.
"""
import collections
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import segmenters as S  # noqa: E402


def log_joint(seg, texts, alpha, pb, rho, inv):
    words = [w for t, b in zip(texts, seg) for w in S.units(t, sorted(b))]
    finals = len(texts)
    n = len(words)
    lp = 0.0
    seen = collections.Counter()
    for i, w in enumerate(words):
        p0 = pb * (1 - pb) ** (len(w) - 1) * (1.0 / inv) ** len(w)
        lp += math.log((seen[w] + alpha * p0) / (i + alpha))
        seen[w] += 1
    lp += (math.lgamma(finals + rho / 2) + math.lgamma(n - finals + rho / 2) - 2 * math.lgamma(rho / 2)
           + math.lgamma(rho) - math.lgamma(n + rho))
    return lp


def main():
    rng = random.Random(7)
    alphabet = "abcde"
    texts = [tuple(rng.choice(alphabet) for _ in range(rng.randint(1, 6))) for _ in range(12)]
    worst = 0.0
    checks = 0
    for trial in range(300):
        m = S.DPSeg(texts, seed=trial)
        ti = rng.choice([k for k, t in enumerate(texts) if len(t) >= 2])
        t = m.texts[ti]
        i = rng.randint(1, len(t) - 1)
        b = m.bounds[ti]
        # code's conditional, copied from DPSeg.sweep with temp = 1
        left = max([x for x in b if x < i], default=0)
        right = min([x for x in b if x > i], default=len(t))
        final = right == len(t)
        w1, w2, w3 = t[left:right], t[left:i], t[i:right]
        counts = collections.Counter(m.counts)
        nn = m.n
        if i in b:
            counts[w2] -= 1
            counts[w3] -= 1
            nn -= 2
        else:
            counts[w1] -= 1
            nn -= 1
        a = m.alpha
        nu = m.nu - 1 if final else m.nu
        p1 = (counts[w1] + a * m.p0(w1)) / (nn + a)
        p1 *= ((nu if final else nn - nu) + m.rho / 2) / (nn + m.rho)
        p2 = (counts[w2] + a * m.p0(w2)) / (nn + a)
        p2 *= (nn - nu + m.rho / 2) / (nn + m.rho)
        p2 *= (counts[w3] + (1 if w2 == w3 else 0) + a * m.p0(w3)) / (nn + 1 + a)
        p2 *= ((nu if final else nn - nu + 1) + m.rho / 2) / (nn + 1 + m.rho)
        with_b = [set(x) for x in m.bounds]
        without_b = [set(x) for x in m.bounds]
        with_b[ti].add(i)
        without_b[ti].discard(i)
        lr = (log_joint(with_b, m.texts, m.alpha, m.pb, m.rho, m.inv)
              - log_joint(without_b, m.texts, m.alpha, m.pb, m.rho, m.inv))
        worst = max(worst, abs(math.log(p2 / p1) - lr))
        checks += 1
    print({"checks": checks, "max_abs_log_ratio_difference": worst})


if __name__ == "__main__":
    main()
