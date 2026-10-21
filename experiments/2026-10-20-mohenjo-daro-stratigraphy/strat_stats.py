"""Statistics relating seal legends to stratigraphic height at Mohenjo-daro.

Height is the excavator's level (Mackay, DK datum) or minus the depth below the modern
surface (Marshall). Every statistic uses u, the height rank of an object within its
excavation area scaled to (0, 1): 0 is the deepest seal of the area, 1 the highest.
Null distributions permute u among the analysed units within each area, so each area
keeps its own set of heights and only the pairing of legends with heights is broken.

Identical complete legends found in the same area are merged into one unit at their
median u before any statistic is computed, so a group of copies counts once.
"""
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CROSSWALK = ROOT / "data/normalized/mayig_wells_class_crosswalk.json"


# ---------------------------------------------------------------- objects and ranks

def seal_objects(rows, areas=None):
    """Seals with a numeric height; areas restricts to the named excavation areas."""
    out = []
    for r in rows:
        m = r["metadata"]
        if not r["object_type"].startswith("SEAL") or m["strat_height_ft"] is None:
            continue
        if areas is not None and m["strat_area"] not in areas:
            continue
        out.append(r)
    return out


def average_ranks(values):
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values))
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def add_height_rank(objects, stratum_key="strat_area"):
    """u = (average rank - 0.5) / n within each stratum, over every seal with a height."""
    groups = defaultdict(list)
    for o in objects:
        groups[o["metadata"][stratum_key]].append(o)
    for members in groups.values():
        ranks = average_ranks([o["metadata"]["strat_height_ft"] for o in members])
        for o, r in zip(members, ranks):
            o["u"] = (r - 0.5) / len(members)
            o["stratum"] = o["metadata"][stratum_key]
    return objects


def units(objects, field, min_length=2):
    """Analysis units for one text field: objects whose field is known and whose complete
    legend has at least min_length signs, with identical complete legends in the same
    stratum merged at their median u."""
    merged = defaultdict(list)
    for o in objects:
        t = o["text"]
        value = t[field] if field != "length" else t["length"]
        if value is None or t["length"] is None or t["length"] < min_length:
            continue
        key = (o["stratum"], tuple(t["signs"])) if t["clean"] else (o["stratum"], "object", o["object_family_id"])
        merged[key].append((o, value))
    out = []
    for key, members in merged.items():
        out.append({"stratum": key[0], "u": float(np.median([o["u"] for o, _ in members])),
                    "value": members[0][1], "copies": len(members),
                    "families": [o["object_family_id"] for o, _ in members],
                    "signs": members[0][0]["text"]["signs"], "text": members[0][0]["text"],
                    "object_type": members[0][0]["object_type"]})
    return out


def all_legends(objects):
    """Every seal's legend, complete or not, with identical complete legends in the same
    stratum merged at their median u. Used for variant choice, which a damaged legend
    still shows."""
    merged = defaultdict(list)
    for o in objects:
        t = o["text"]
        key = (o["stratum"], tuple(t["signs"])) if t["clean"] else (o["stratum"], "object", o["object_family_id"])
        merged[key].append(o)
    return [{"stratum": key[0], "u": float(np.median([o["u"] for o in members])),
             "families": [o["object_family_id"] for o in members], "signs": members[0]["text"]["signs"]}
            for key, members in merged.items()]


# ---------------------------------------------------------------- permutation machinery

def strata_index(rows):
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        groups[r["stratum"]].append(i)
    return [np.array(v) for v in groups.values()]


def permuted_u(u, index, rng):
    out = u.copy()
    for idx in index:
        out[idx] = u[rng.permutation(idx)]
    return out


def permutation_test(rows, statistic, draws, seed, alternative="greater"):
    """statistic(u_array) -> float. Returns observed, null mean, null sd, z and the
    permutation p-value (observed counted as one draw)."""
    rng = np.random.default_rng(seed)
    u = np.array([r["u"] for r in rows], dtype=float)
    index = strata_index(rows)
    observed = statistic(u)
    null = np.array([statistic(permuted_u(u, index, rng)) for _ in range(draws)])
    if alternative == "greater":
        p = (1 + np.sum(null >= observed - 1e-12)) / (draws + 1)
    elif alternative == "less":
        p = (1 + np.sum(null <= observed + 1e-12)) / (draws + 1)
    else:
        centre = null.mean()
        p = (1 + np.sum(np.abs(null - centre) >= abs(observed - centre) - 1e-12)) / (draws + 1)
    sd = float(null.std(ddof=1))
    return {"observed": float(observed), "null_mean": float(null.mean()), "null_sd": sd,
            "z": float((observed - null.mean()) / sd) if sd > 0 else None,
            "p": float(p), "draws": draws, "seed": seed, "alternative": alternative, "units": len(rows)}


# ---------------------------------------------------------------- statistics

def category_codes(rows, min_count):
    """Category per unit: its value if that value has at least min_count units, else OTHER."""
    counts = Counter(r["value"] for r in rows)
    keep = sorted(v for v, n in counts.items() if n >= min_count)
    labels = [r["value"] if counts[r["value"]] >= min_count else "OTHER" for r in rows]
    names = keep + (["OTHER"] if "OTHER" in labels else [])
    lookup = {name: i for i, name in enumerate(names)}
    return np.array([lookup[x] for x in labels]), names


def between_ratio_factory(codes):
    """Between-category share of the variance of u (eta squared) times n: a rank
    analysis-of-variance statistic, large when categories sit at different heights."""
    k = codes.max() + 1
    n_c = np.bincount(codes, minlength=k).astype(float)

    def stat(u):
        mean = u.mean()
        sums = np.bincount(codes, weights=u, minlength=k)
        between = np.sum(np.where(n_c > 0, (sums / np.maximum(n_c, 1) - mean) ** 2 * n_c, 0.0))
        total = np.sum((u - mean) ** 2)
        return len(u) * between / total if total > 0 else 0.0
    return stat


def stratified_spearman_factory(x, rows):
    """Spearman correlation between x and u, with x ranked within each stratum so that
    both variables are on within-area rank scales."""
    x = np.asarray(x, dtype=float)
    xr = np.empty(len(x))
    for idx in strata_index(rows):
        xr[idx] = (average_ranks(x[idx]) - 0.5) / len(idx)

    def stat(u):
        a, b = xr - xr.mean(), u - u.mean()
        denom = math.sqrt(np.sum(a * a) * np.sum(b * b))
        return float(np.sum(a * b) / denom) if denom > 0 else 0.0
    return stat


def pearson_factory(score):
    """Pearson correlation between a fixed per-unit score and u."""
    s = np.asarray(score, dtype=float)

    def stat(u):
        a, b = s - s.mean(), u - u.mean()
        denom = math.sqrt(np.sum(a * a) * np.sum(b * b))
        return float(np.sum(a * b) / denom) if denom > 0 else 0.0
    return stat


def share_difference_factory(indicator, lower=1 / 3, upper=2 / 3):
    """Share of units with the indicator in the top third of u minus the share in the
    bottom third. Thirds are fixed by u, which permutations move between units."""
    ind = np.asarray(indicator, dtype=float)

    def stat(u):
        low, high = u < lower, u >= upper
        if low.sum() == 0 or high.sum() == 0:
            return 0.0
        return float(ind[high].mean() - ind[low].mean())
    return stat


# ---------------------------------------------------------------- sign variants

def load_variant_classes():
    """Wells codes that map to exactly one Mayig class; classes with two or more such
    codes are variant sets."""
    cross = json.loads(CROSSWALK.read_text(encoding="utf-8"))
    single = {w: cls[0] for w, cls in cross["by_wells_id"].items() if len(cls) == 1}
    members = defaultdict(list)
    for w, c in single.items():
        members[c].append(w)
    return {w: c for w, c in single.items() if len(members[c]) >= 2}


def variant_tokens(objects, classes):
    """One row per (object, variant class): the variant code used. An object using two
    codes of one class contributes its most frequent code, ties to the lower code."""
    rows = []
    for o in objects:
        t = o["text"]
        by_class = defaultdict(Counter)
        for s in t["signs"]:
            if s in classes:
                by_class[classes[s]][s] += 1
        for c, codes in by_class.items():
            code = sorted(codes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
            rows.append({"stratum": o["stratum"], "u": o["u"], "class": c, "value": code,
                         "families": [o["object_family_id"]]})
    return rows


def variant_statistic_factory(rows, min_code=3, min_class=10):
    """Sum over variant classes of the between-variant height statistic, using classes
    where at least two codes each have min_code tokens and the class has min_class rows
    in those codes. Rows of other codes are dropped."""
    by_class = defaultdict(list)
    for i, r in enumerate(rows):
        by_class[r["class"]].append(i)
    parts = []
    used = []
    for c, idx in sorted(by_class.items()):
        counts = Counter(rows[i]["value"] for i in idx)
        codes = sorted(v for v, n in counts.items() if n >= min_code)
        if len(codes) < 2:
            continue
        keep = np.array([i for i in idx if rows[i]["value"] in codes])
        if len(keep) < min_class:
            continue
        lookup = {v: j for j, v in enumerate(codes)}
        parts.append((keep, np.array([lookup[rows[i]["value"]] for i in keep])))
        used.append({"class": c, "codes": {v: counts[v] for v in codes}})

    def stat(u):
        total = 0.0
        for keep, codes in parts:
            sub = u[keep]
            if np.sum((sub - sub.mean()) ** 2) == 0:
                continue
            total += between_ratio_factory(codes)(sub) - (codes.max())  # minus df: centred near zero
        return total
    return stat, used
