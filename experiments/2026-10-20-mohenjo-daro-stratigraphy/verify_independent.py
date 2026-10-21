"""Independent recomputation of the population, P1/P2 shares and the P4 statistic.

Written after the confirmation read without importing strat_stats.py or score.py.

    python -I experiments/2026-10-20-mohenjo-daro-stratigraphy/verify_independent.py
"""
import collections
import json
import random
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
rows = [json.loads(line) for line in open(ROOT / "data/raw/2026-10-20-mohenjo-daro-stratigraphy/confirmation-marshall1931.jsonl", encoding="utf-8")]
seals = [r for r in rows if r["object_type"].startswith("SEAL") and r["metadata"]["strat_height_ft"] is not None]
cell = collections.Counter((r["metadata"]["strat_area"], r["metadata"]["strat_section"]) for r in seals)
for r in seals:
    a, s = r["metadata"]["strat_area"], r["metadata"]["strat_section"]
    r["st"] = f"{a}/{s}" if cell[(a, s)] >= 15 else f"{a}/rest"
size = collections.Counter(r["st"] for r in seals)
seals = [r for r in seals if size[r["st"]] >= 5]
by = collections.defaultdict(list)
for r in seals:
    by[r["st"]].append(r)
for g in by.values():
    hs = sorted(r["metadata"]["strat_height_ft"] for r in g)
    n = len(g)
    for r in g:
        h = r["metadata"]["strat_height_ft"]
        lo, hi = hs.index(h), n - 1 - hs[::-1].index(h)
        r["u"] = ((lo + hi) / 2 + 0.5) / n
stock = {"740", "520", "090", "400", "151", "156", "527", "617", "621", "226", "892", "407"}


def units(field):
    merged = collections.defaultdict(list)
    for r in seals:
        t = r["text"]
        if t[field] is None or t["length"] is None or t["length"] < 2:
            continue
        key = (r["st"], tuple(t["signs"])) if t["clean"] else (r["st"], "o", r["object_family_id"])
        merged[key].append(r)
    return [(k[0], st.median([x["u"] for x in v]), v[0]["text"][field]) for k, v in merged.items()]


def eta(us, cats):
    mu = sum(us) / len(us)
    total = sum((x - mu) ** 2 for x in us)
    groups = collections.defaultdict(list)
    for x, c in zip(us, cats):
        groups[c].append(x)
    return len(us) * sum(len(v) * (sum(v) / len(v) - mu) ** 2 for v in groups.values()) / total


close = units("closing")
bottom = [v in stock for s, u, v in close if u < 1 / 3]
top = [v in stock for s, u, v in close if u >= 2 / 3]
opening = units("opening")
counts = collections.Counter(v for s, u, v in opening)
cats = [v if counts[v] >= 5 else "OTHER" for s, u, v in opening]
us = [u for s, u, v in opening]
random.seed(1)
index = collections.defaultdict(list)
for i, (s, u, v) in enumerate(opening):
    index[s].append(i)
observed = eta(us, cats)
exceed = 0
for _ in range(1999):
    perm = us[:]
    for members in index.values():
        values = [us[i] for i in members]
        random.shuffle(values)
        for i, v in zip(members, values):
            perm[i] = v
    exceed += eta(perm, cats) >= observed - 1e-12
print(json.dumps({"seals": len(seals), "strata": len(by), "closing_units": len(close),
                  "bottom_units": len(bottom), "bottom_share": sum(bottom) / len(bottom),
                  "top_units": len(top), "top_share": sum(top) / len(top),
                  "difference": sum(top) / len(top) - sum(bottom) / len(bottom),
                  "P4_observed": observed, "P4_categories": len(set(cats)), "P4_p_1999_draws": (exceed + 1) / 2000}, indent=2))
