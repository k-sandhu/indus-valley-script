"""Seal table for Shot A (rank is written twice on Indus seals).

Builds one row per seal object family from a half returned by shots_common.load_half.
The same code serves the discovery exploration and the confirmation script, so the
population rules cannot drift between the two stages.

Rules
- Seal faces are those whose object_type starts with 'SEAL'.
- One face per object family: the longest face (most positions), ties broken by the
  lowest record identifier.
- Size: horizontal(mm) and vertical(mm); zero or blank means missing. Characteristic
  size is sqrt(h * v); log_area is ln(h) + ln(v). Faces whose dimensions came from an
  inch field (metadata 'h' not blank) are flagged dims_unit='inch'; others 'mm'.
- Size-eligible: both dimensions positive and preservation in SIZE_OK (complete,
  slightly chipped, chipped, and the catalogue misspelling 'complsete').
- Text-eligible: complete_observed, no unknown sign, single line, length >= 1.
- Closing units: 'last' (final sign), 'last2' (final two signs), 'formula'
  (final two signs when the final sign is 740, otherwise the final sign).
  Opening units mirror them: 'first', 'first2'.
"""
from pathlib import Path
import math
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

SIZE_OK = {"complete", "slightly chipped", "chipped", "complsete"}
JAR = "740"


def fnum(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def closing_units(signs):
    last = signs[-1]
    last2 = "-".join(signs[-2:]) if len(signs) >= 2 else None
    formula = last2 if (last == JAR and len(signs) >= 2) else last
    return {"last": last, "last2": last2, "formula": formula}


def opening_units(signs):
    return {"first": signs[0], "first2": "-".join(signs[:2]) if len(signs) >= 2 else None}


def seal_table(rows):
    fams = {}
    for r in rows:
        if not r["object_type"].startswith("SEAL"):
            continue
        key = r["object_family_id"]
        cur = fams.get(key)
        rank = (-r["length"], r["record_id"])
        if cur is None or rank < (-cur["length"], cur["record_id"]):
            fams[key] = r
    out = []
    for fam, r in sorted(fams.items()):
        m = r["metadata"]
        h, v = fnum(m.get("horizontal(mm)")), fnum(m.get("vertical(mm)"))
        th = fnum(m.get("thickness(mm)"))
        pres = (m.get("preservation") or "").strip()
        size_ok = h is not None and v is not None and pres in SIZE_OK
        text_ok = bool(r["complete_observed"] and not r["has_unknown_sign"] and r["single_line"] and r["length"] >= 1)
        signs = list(r["signs_reading_rtl"])
        row = {
            "family": fam,
            "record_id": r["record_id"],
            "cisi": r.get("source_cisi"),
            "component": r["component"],
            "site": r["site"],
            "region": r.get("region"),
            "type": r["object_type"],
            "shape": m.get("shape"),
            "boss": m.get("boss"),
            "animal": (r.get("symbol") or "None").split(":")[0],
            "symbol_full": r.get("symbol"),
            "cult": m.get("cult"),
            "material": m.get("material"),
            "preservation": pres,
            "period": m.get("period"),
            "time": m.get("time"),
            "sides": m.get("sides"),
            "h": h, "v": v, "th": th,
            "dims_unit": "inch" if (m.get("h") or "").strip() else "mm",
            "size_ok": size_ok,
            "size": math.sqrt(h * v) if size_ok else None,
            "log_area": math.log(h) + math.log(v) if size_ok else None,
            "text_ok": text_ok,
            "length": r["length"],
            "signs": signs if text_ok else None,
        }
        if text_ok:
            row.update(closing_units(signs))
            row.update(opening_units(signs))
        out.append(row)
    return out


def type_class(t):
    """Coarse seal class used as the shape covariate."""
    if t == "SEAL:S":
        return "S"
    if t == "SEAL:R":
        return "R"
    return "other"
