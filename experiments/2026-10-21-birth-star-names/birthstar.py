"""Shared definitions for the birth-star study: fish compounds, comparison units and class statistics.

The compound and position rules follow PROTOCOL.md, Part 2. The statistics are those of Part 1,
applied identically to Brahmi name elements and to Indus units.
"""
from collections import Counter
import csv
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CODING = ROOT / "experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv"


def coding(path=CODING):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return {r["code"].strip(): r for r in csv.DictReader(f, delimiter="\t")}


def families(table):
    fish = {c for c, r in table.items() if r["base"] == "B220"}
    strokes = {c for c, r in table.items() if r["base"] in ("B001", "B031")}
    return fish, strokes


def is_seal(row):
    return str(row.get("object_type", "")).strip().upper().split(":")[0] == "SEAL"


def norm(sign):
    return str(sign).strip().zfill(3)


def legends(rows):
    """Distinct clean right-to-left single-line seal texts, one representative per sequence."""
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: str(r.get("record_id", ""))):
        if not r.get("clean_rtl_singleline") or not is_seal(r):
            continue
        seq = tuple(norm(s) for s in r["signs_reading_rtl"])
        if not seq or seq in seen:
            continue
        seen.add(seq)
        out.append({"seq": seq, "component": r.get("component"), "record_id": r.get("record_id"),
                    "site": r.get("site"), "cisi": r.get("source_cisi")})
    return out


def units(seq, fish, strokes):
    """Segment one legend into fish compounds and other units.

    A fish compound is a maximal run of fish signs with the stroke group immediately before it.
    Every other sign that is not a stroke group is one unit with its immediately preceding
    stroke group as prefix. A unit is final when its last sign is the last sign of the legend.
    """
    out, i, n = [], 0, len(seq)
    while i < n:
        s = seq[i]
        prefix = seq[i - 1] if i > 0 and seq[i - 1] in strokes else "-"
        if s in fish:
            j = i
            while j < n and seq[j] in fish:
                j += 1
            run = seq[i:j]
            out.append({"kind": "fish", "T1": prefix + "|" + "+".join(run), "T0": "+".join(run),
                        "T3": [(prefix if k == 0 else "-") + "|" + c for k, c in enumerate(run)],
                        "run": run, "prefix": prefix, "start": i, "end": j - 1, "final": j == n})
            i = j
        elif s in strokes:
            i += 1
        else:
            out.append({"kind": "other", "T1": prefix + "|" + s, "T0": s, "T3": [prefix + "|" + s],
                        "run": (s,), "prefix": prefix, "start": i, "end": i, "final": i == n - 1})
            i += 1
    return out


def collect(legend_rows, fish, strokes, unit="T1", include_final=False):
    """Tokens of fish compounds and of the comparison vocabulary under one unit and position rule."""
    fish_tokens, other_tokens, initial_tokens = [], [], []
    for lg in legend_rows:
        us = units(lg["seq"], fish, strokes)
        for k, u in enumerate(us):
            if u["final"] and not include_final:
                continue
            types = u["T3"] if unit == "T3" else [u[unit]]
            if u["kind"] == "fish":
                fish_tokens += types
            else:
                other_tokens += types
                if k == 0:
                    initial_tokens += types
    return fish_tokens, other_tokens, initial_tokens


def stats(tokens):
    c = Counter(tokens)
    n = sum(c.values())
    s = len(c)
    if n == 0:
        return {"N": 0, "S": 0}
    freqs = np.array(sorted(c.values(), reverse=True), dtype=float)
    f1 = int(np.sum(freqs == 1))
    f2 = int(np.sum(freqs == 2))
    p = freqs / n
    h = float(-np.sum(p * np.log(p)))
    out = {"N": int(n), "S": int(s), "f1": f1, "f2": f2,
           "chao1": float(s + f1 * (f1 - 1) / (2 * (f2 + 1))),
           "entropy_nats": h, "normalised_entropy": float(h / math.log(s)) if s > 1 else None,
           "top_share": float(freqs[0] / n), "singleton_share": float(f1 / s), "novelty_good_turing": float(f1 / n),
           "zipf_slope": zipf(freqs)}
    return out


def zipf(freqs):
    if len(freqs) < 3:
        return None
    x = np.log(np.arange(1, len(freqs) + 1))
    y = np.log(freqs)
    return float(np.polyfit(x, y, 1)[0])


STAT_KEYS = ("S", "chao1", "normalised_entropy", "top_share", "singleton_share", "novelty_good_turing", "zipf_slope")


def matched(pool, n, draws, seed):
    """Statistics of `draws` subsamples of size n drawn without replacement from a token pool."""
    rng = np.random.default_rng(seed)
    pool = np.array(pool, dtype=object)
    res = {k: [] for k in STAT_KEYS}
    for _ in range(draws):
        st = stats(list(rng.choice(pool, size=n, replace=False)))
        for k in STAT_KEYS:
            res[k].append(np.nan if st.get(k) is None else st[k])
    return {k: np.array(v, dtype=float) for k, v in res.items()}


def summarise(arr):
    a = arr[~np.isnan(arr)]
    if not len(a):
        return None
    return {"mean": float(np.mean(a)), "p02_5": float(np.percentile(a, 2.5)), "median": float(np.median(a)),
            "p97_5": float(np.percentile(a, 97.5))}


def compare(target, draws_by_key):
    """Share of matched draws whose statistic exceeds, or falls below, the target class."""
    out = {}
    for k, arr in draws_by_key.items():
        a = arr[~np.isnan(arr)]
        t = target.get(k)
        if t is None or not len(a):
            continue
        out[k] = {"target": t, "matched": summarise(arr),
                  "share_draws_above_target": float(np.mean(a > t)),
                  "share_draws_below_target": float(np.mean(a < t))}
    return out


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [(c - r) / d, (c + r) / d]


def modifier_pairs(fish_sign_counts, table, min_count=2):
    """Which modifiers distinguish two attested fish variants, and on how many bases.

    A variant is the set of modifiers of a fish code. A contrast m applies to base b when b and
    b plus m are both attested at least min_count times (codes with identical modifier sets pooled).
    """
    variant_counts = Counter()
    for code, cnt in fish_sign_counts.items():
        mods = frozenset(m for m in table[code]["mods"].split(";") if m)
        variant_counts[mods] += cnt
    attested = {v for v, c in variant_counts.items() if c >= min_count}
    mods_all = sorted({m for v in variant_counts for m in v})
    out = {}
    for m in mods_all:
        pairs = []
        for v in sorted(attested, key=lambda v: sorted(v)):
            if m in v:
                continue
            w = v | {m}
            if w in attested:
                a, b = variant_counts[v], variant_counts[w]
                pairs.append({"base": "+".join(sorted(v)) or "plain", "with": "+".join(sorted(w)),
                              "base_count": a, "with_count": b, "ratio": b / a})
        out[m] = {"bases": len(pairs), "pairs": pairs,
                  "all_ratios_within_third_to_three": bool(pairs) and all(1 / 3 <= p["ratio"] <= 3 for p in pairs)}
    return {"variant_counts": {"+".join(sorted(v)) or "plain": c for v, c in variant_counts.items()}, "contrasts": out}
