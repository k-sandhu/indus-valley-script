"""Reviewer helpers for the D2 review (independent of the package's analysis code).

Everything here re-implements the protocol text from scratch: physical grouping, the
representative-face rule, motif classes, the block permutation and the Benjamini-Hochberg
correction. The package modules are not imported.
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-sign-context-and-seals'
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'
REVIEW_RAW = RAW / 'review'
INPUT = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
MISSING_MOTIFS = {'', '-', '?', 'None', 'Unknown'}


def load_rows():
    return [json.loads(line) for line in INPUT.read_text(encoding='utf-8').splitlines()]


def components(rows):
    """Union rows that share object_family_id or a simple CISI base id (side suffix removed)."""
    parent = list(range(len(rows)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    seen = {}
    for i, r in enumerate(rows):
        keys = [('fam', r['object_family_id'])]
        m = re.fullmatch(r'([A-Za-z][A-Za-z0-9]*-\d+)[A-Za-z]?', (r.get('source_cisi') or '').strip())
        if m:
            keys.append(('cisi', m.group(1)))
        for k in keys:
            if k in seen:
                a, b = find(i), find(seen[k])
                if a != b:
                    parent[max(a, b)] = min(a, b)
            else:
                seen[k] = i
    groups = defaultdict(list)
    for i in range(len(rows)):
        groups[find(i)].append(rows[i])
    return [groups[k] for k in sorted(groups)]


def rep(faces):
    """Longest reading sequence, then smallest record_id (string order)."""
    return min(faces, key=lambda r: (-len(r['signs_reading_rtl']), r['record_id']))


def principal_and_seals(groups):
    principal = [rep(g) for g in groups if any(r['signs_reading_rtl'] for r in g)]
    seals = [rep([r for r in g if r['object_type'].startswith('SEAL')]) for g in groups
             if any(r['object_type'].startswith('SEAL') for r in g)]
    return principal, seals


def motif(raw):
    if raw.startswith('Bull1'):
        return 'unicorn'
    return None if raw in MISSING_MOTIFS else raw


def bh(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    ranked = ps[order] * len(ps) / np.arange(1, len(ps) + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(len(ps))
    out[order] = np.minimum(adj, 1)
    return out


def blocks(keys):
    d = defaultdict(list)
    for i, k in enumerate(keys):
        d[k].append(i)
    return [np.array(v) for _, v in sorted(d.items(), key=lambda kv: str(kv[0]))]


def shuffle_in_blocks(values, strata, rng):
    out = values.copy()
    for ix in strata:
        if len(ix) > 1:
            out[ix] = rng.permutation(values[ix])
    return out


def mc_p(observed, null, mode='upper'):
    """Inclusive Monte Carlo p. mode: upper, abs (uncentred), centred (two-sided about null mean)."""
    null = np.asarray(null, float)
    if mode == 'upper':
        e = np.count_nonzero(null >= observed - 1e-12)
    elif mode == 'abs':
        e = np.count_nonzero(np.abs(null) >= abs(observed) - 1e-12)
    else:
        mu = null.mean()
        e = np.count_nonzero(np.abs(null - mu) >= abs(observed - mu) - 1e-12)
    return (e + 1) / (len(null) + 1)


def wilson(k, n, z=1.959963984540054):
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, mid - half), min(1, mid + half)


def js_bits(a, b):
    a = a / a.sum()
    b = b / b.sum()
    m = (a + b) / 2
    with np.errstate(divide='ignore', invalid='ignore'):
        ta = np.where(a > 0, a * np.log2(a / m), 0.0).sum()
        tb = np.where(b > 0, b * np.log2(b / m), 0.0).sum()
    return float((ta + tb) / 2)
