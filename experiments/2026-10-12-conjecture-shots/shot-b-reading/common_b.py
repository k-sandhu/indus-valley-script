"""Shared loading for Shot B (working reading).

Construction uses the discovery half only, with every withheld field removed. The strip
list adds `class` to the coordinator's list: on inspection its codes (for example `UC`)
appear to record the field animal of seals, so it is treated as withheld.
"""
from pathlib import Path
import collections
import csv
import json
import sys

SHOT = Path(__file__).resolve().parent
PKG = SHOT.parent
ROOT = PKG.parents[1]
sys.path.insert(0, str(PKG))
import shots_common  # noqa: E402

RAW = ROOT / "data/raw/2026-10-12-conjecture-shots/shot-b-reading"
DISC = SHOT / "discovery"

STRIP = ('site', 'region', 'symbol', 'horizontal(mm)', 'vertical(mm)', 'thickness(mm)', 'h', 'v', 'th',
         'material', 'period', 'phase', 'time', 'depth', 'cult', 'boss', 'area-section', 'block-house',
         'room-grid', 'excavation-idno', 'color', 'shape', 'cross-section', 'class')

UNKNOWN = "000"
SHORT = {f"{i:03d}": i for i in range(1, 8)}          # 001-007, short strokes 1-7
TALL = {"031": 1, "032": 2, "033": 3, "034": 4}


def otype_group(t):
    t = t or ""
    if t.startswith("SEAL"):
        return "SEAL"
    if t.startswith("TAB:B"):
        return "TAB:B"
    if t.startswith("TAB:I"):
        return "TAB:I"
    if t.startswith("TAB:C"):
        return "TAB:C"
    if t.startswith("POT") or t.startswith("POsT"):
        return "POT"
    if t.startswith("TAG"):
        return "TAG"
    return "OTHER"


def load_discovery():
    return shots_common.load_half("discovery", strip=STRIP)


def ends(r):
    """(start_intact, end_intact) in reading order from the visual LTR code.

    The visual code is already normalized so that reading runs right to left; its left
    end is the reading end and its right end the reading start.
    """
    t = r["text_code_visual_ltr"]
    return (t.endswith("+"), t.startswith("+"))


def components_table():
    rows = {}
    with open(ROOT / "experiments/2026-10-12-structure-first/step1-signs/sign_components_v1.tsv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            rows[row["code"]] = row
    return rows


def mayig_descriptions():
    schema = json.loads((ROOT / "data/normalized/mayig_sign_schema.json").read_text(encoding="utf-8"))
    cw = json.loads((ROOT / "data/normalized/mayig_wells_class_crosswalk.json").read_text(encoding="utf-8"))
    out = {}
    for w, classes in cw["by_wells_id"].items():
        out[w] = "; ".join(f"{c}: {schema['signs'].get(c, {}).get('description', '').strip()}" for c in classes)
    return out


def prior_meanings():
    return json.loads((DISC / "prior_project_meanings.json").read_text(encoding="utf-8"))
