"""Statistics relating Harappa seal legends to their place in a dated sequence.

The clock is chronological order within an excavation frame. In the confirmation
population (Vats's Mound F) it is Vats's stratum, numbered from the top, so Stratum VII
is the oldest and Stratum I the latest; the export assigns the strata to HARP periods
3B-1 (VII), 3B/C (VI and V), 3C-1 (IV), 3C-2 (III), 3C-3 (II) and 3C-4 (I). Every seal
gets u, the mid-rank of its stratum among the mound's seals scaled to (0, 1), so that
0 is the oldest and 1 the latest. The early third is u < 1/3 (Strata VII to V), the
late third u >= 2/3 (Strata II and I).

Nulls permute u among the analysed units within frames. In Mound F a frame is one of
Vats's trenches (or the Granary area) when it holds at least 15 seals; the remaining
cells are pooled, and frames under five seals are dropped. A test therefore asks
whether legends from older strata of the same trench differ from legends from later
strata of that trench.

The permutation machinery, the unit construction (identical complete legends in one
frame merged at their median u) and the statistics themselves come from the Mohenjo-
daro stratigraphy package (strat_stats.py, frozen there by hash), which this module
imports unchanged. What is new here is the clock, the frames, and the reading of
damaged legends: a legend whose left or right edge survives gives its closing or
opening sign even when the other end is broken.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys

import numpy as np

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
STRAT = ROOT / "experiments/2026-10-20-mohenjo-daro-stratigraphy"
sys.path.append(str(STRAT))
import strat_stats as S  # noqa: E402

MIN_FRAME_CELL = 15
MIN_FRAME = 5


# ---------------------------------------------------------------- legends

def edge_text_fields(row):
    """Positions read from the visual code. The export normalises every legend to be
    read right to left, so the leftmost sign of the visual code closes the legend and
    the rightmost opens it; '+' marks a surviving edge and '[' or ']' a break. A
    position counts when the legend is on one line, its edge survives and the sign at
    that edge is readable. Length needs both edges and every slot observed."""
    code = row["text_code_visual_ltr"].strip()
    visual = list(row["signs_visual_ltr"])
    single = bool(row["single_line"]) and "/" not in code
    left = code.startswith("+")
    right = code.endswith("+")
    complete = bool(row["complete_observed"]) and not row["has_blank_space"]
    closing = visual[0] if single and left and visual and visual[0] != "000" else None
    opening = visual[-1] if single and right and visual and visual[-1] != "000" else None
    pair = None
    if single and left and len(visual) >= 2 and "000" not in visual[:2]:
        pair = f"{visual[1]}-{visual[0]}"
    signs = list(row["signs_reading_rtl"])
    return {
        "signs": signs,
        "length": row["length"] if complete else None,
        "opening": opening,
        "closing": closing,
        "closing_pair": pair,
        "clean": complete and not row["has_unknown_sign"],
        "ordered": single and left and right,
        "both_edges": left and right,
        "visible_signs": sum(s != "000" for s in signs),
    }


def position_units(objects, field):
    """Units for an opening or closing test: legends whose sign at that position is
    read, excluding complete legends of a single sign (where opening and closing are
    the same sign). Identical complete legends in one frame are merged at their median
    u; every other legend is its own unit."""
    merged = defaultdict(list)
    for o in objects:
        t = o["text"]
        value = t[field]
        if value is None:
            continue
        if t["length"] is not None and t["length"] < 2:
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


def length_units(objects, min_length=1):
    return S.units(objects, "length", min_length=min_length)


# ---------------------------------------------------------------- clock and frames

def chronological_key(meta):
    """Older is smaller. Vats strata are numbered from the top; HARP period labels have
    an order fixed in build_inputs.py."""
    if meta["chron_source"] == "vats_stratum":
        return -meta["chron_stratum"]
    return meta["chron_period_order"]


def confirmation_frames(objects):
    cells = Counter(o["metadata"]["chron_frame_cell"] for o in objects)
    for o in objects:
        cell = o["metadata"]["chron_frame_cell"]
        o["stratum"] = cell if cells[cell] >= MIN_FRAME_CELL else "F/rest"
    sizes = Counter(o["stratum"] for o in objects)
    return [o for o in objects if sizes[o["stratum"]] >= MIN_FRAME], dict(sorted(sizes.items()))


def discovery_frames(objects):
    """Discovery frames are mound and label source (a HARP period scale and a Vats
    stratum scale are not compared with each other)."""
    for o in objects:
        m = o["metadata"]
        o["stratum"] = f"{m['chron_mound']}/{m['chron_source']}"
    objects = [o for o in objects if chronological_key(o["metadata"]) is not None]
    sizes = Counter(o["stratum"] for o in objects)
    return [o for o in objects if sizes[o["stratum"]] >= MIN_FRAME], dict(sorted(sizes.items()))


def add_clock(objects, scope="mound"):
    """u = (mid-rank of the chronological key - 0.5) / n. scope 'mound' ranks over all
    objects passed (Mound F's strata are mound-wide building levels); scope 'frame'
    ranks within each frame (discovery, where frames use different scales)."""
    groups = defaultdict(list)
    for o in objects:
        groups["all" if scope == "mound" else o["stratum"]].append(o)
    for members in groups.values():
        ranks = S.average_ranks([chronological_key(o["metadata"]) for o in members])
        for o, r in zip(members, ranks):
            o["u"] = (r - 0.5) / len(members)
    return objects


def prepare(rows, population, scope=None):
    objects = []
    for r in rows:
        o = dict(r)
        o["text"] = edge_text_fields(r)
        objects.append(o)
    if population == "confirmation":
        objects, sizes = confirmation_frames(objects)
        add_clock(objects, scope or "mound")
    else:
        objects, sizes = discovery_frames(objects)
        add_clock(objects, scope or "frame")
    return objects, sizes


def third(u):
    return 0 if u < 1 / 3 else (1 if u < 2 / 3 else 2)


# ---------------------------------------------------------------- statistics

def inventory_factory(units, min_units=8):
    """Whole-legend sign inventory against time: for every sign present in at least
    min_units legends, n_s times the squared deviation of its legends' mean u from the
    overall mean, summed and divided by the variance of u. Large when signs differ in
    the periods of the legends that carry them."""
    counts = Counter(s for r in units for s in set(r["signs"]) - {"000"})
    keep = sorted(s for s, n in counts.items() if n >= min_units)
    M = np.array([[1.0 if s in set(r["signs"]) else 0.0 for s in keep] for r in units]) if keep else np.zeros((len(units), 0))
    n = M.sum(0) if keep else np.zeros(0)

    def stat(u):
        if not keep or u.var() == 0:
            return 0.0
        mu = (M * u[:, None]).sum(0) / n
        return float(np.sum(n * (mu - u.mean()) ** 2) / u.var())
    return stat, keep


def indicator_units(objects, predicate):
    """One unit per seal (no merging) for a physical feature of the seal."""
    return [{"stratum": o["stratum"], "u": o["u"], "value": bool(predicate(o)),
             "families": [o["object_family_id"]]} for o in objects]


def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
