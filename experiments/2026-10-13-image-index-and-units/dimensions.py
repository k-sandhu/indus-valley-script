"""Dimension units audit (question card Q-1020): unit, precision, source and agreement of
every local size value.

Usage (from the repository root):
    python -P experiments/2026-10-13-image-index-and-units/dimensions.py --out experiments/2026-10-13-image-index-and-units/run-2026-10-13/dimensions

Inputs (local): data/normalized/lipi_observed_faces.jsonl (Lipi as-recorded fields h, v, th
and millimetre fields), data/normalized/indus_website_observed.jsonl (older website export,
WIDTH, HEIGHT, THICKNESS), data/mayig/corpus (checked for size fields), and the October 12
split with Shot A's seal_table.py and rank_lib.py, imported read-only. The output directory
must not exist. Outputs hold identifiers, numbers, units, classes and flags; no sign
sequences.
"""
import argparse
import collections
import csv
import glob
import hashlib
import json
import math
import pathlib
import re
import sys

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
WEBSITE = ROOT / "data/normalized/indus_website_observed.jsonl"
WEBSITE_SQL = ROOT / "data/indus_website/population-script.sql"
MAYIG = ROOT / "data/mayig/corpus"
SPLIT = ROOT / "data/raw/2026-10-12-conjecture-shots/split.json"
SHOT_A = ROOT / "experiments/2026-10-12-conjecture-shots/shot-a-rank"
INV = ROOT / "experiments/2026-10-12-data-inventory"

AXES = [("horizontal", "h", "horizontal(mm)", "WIDTH"),
        ("vertical", "v", "vertical(mm)", "HEIGHT"),
        ("thickness", "th", "thickness(mm)", "THICKNESS")]
FACTORS = [("inch", 25.4), ("cm", 10.0), ("mm", 1.0)]
EXACT, ROUNDED, APPROX = 0.051, 0.51, 0.6
NUM = r"(?:\d+(?:\.\d*)?|\.\d+)"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def decimals(text):
    text = text.strip()
    return len(text.split(".")[1]) if "." in text else 0


def parse_recorded(raw):
    """Parse a Lipi as-recorded size string (fields h, v, th)."""
    out = {"raw": raw, "markers": [], "unit_stated": None, "values": [], "value_texts": [], "parse": "empty"}
    if raw is None or not raw.strip():
        return out
    s = raw.strip()
    if "(ext)" in s:
        out["markers"].append("extant")
        s = s.replace("(ext)", "")
    if "(estimated)" in s:
        out["markers"].append("estimated")
        s = s.replace("(estimated)", "")
    if s.endswith("ht."):
        out["markers"].append("note-ht")
        s = s[:-3]
    if "+?" in s:
        out["markers"].append("at-least-uncertain")
        s = s.replace("+?", "")
    elif s.endswith("?"):
        out["markers"].append("uncertain")
        s = s[:-1]
    if "+" in s:
        out["markers"].append("at-least")
        s = s.replace("+", "")
    s = s.strip()
    m = re.fullmatch(r"(.*?)(cm|mm)", s)
    if m:
        out["unit_stated"] = m.group(2)
        s = m.group(1).strip()
    if s == "?":
        out["parse"] = "placeholder"
        return out
    if ".." in s:
        out["markers"].append("double-dot-typo")
        s = s.replace("..", ".")
    parts = [p.strip() for p in s.split("-")]
    if len(parts) == 2 and parts[1].lower() == "missing":
        out["markers"].append("range-upper-missing")
        parts = parts[:1]
    texts = []
    for p in parts:
        if re.fullmatch(NUM, p):
            texts.append(p)
        else:
            out["parse"] = "malformed"
            return out
    out["value_texts"] = texts
    out["values"] = [float(t) for t in texts]
    out["parse"] = "range" if len(texts) == 2 else "number"
    return out


def parse_mm(raw):
    out = {"raw": raw, "values": [], "value_texts": [], "parse": "empty"}
    if raw is None or not str(raw).strip():
        return out
    s = str(raw).strip()
    m = re.fullmatch(rf"({NUM})\s*-\s*({NUM})", s)
    if m:
        out["value_texts"] = [m.group(1), m.group(2)]
        out["values"] = [float(m.group(1)), float(m.group(2))]
        out["parse"] = "range"
        return out
    if re.fullmatch(NUM, s):
        out["value_texts"] = [s]
        out["values"] = [float(s)]
        out["parse"] = "number"
        return out
    out["parse"] = "malformed"
    return out


def fit_class(diff):
    if diff <= EXACT:
        return "exact"
    if diff <= ROUNDED:
        return "rounded"
    if diff <= APPROX:
        return "approximate"
    return "mismatch"


GRID_DENOMS = (2, 4, 8, 16, 32)


def inch_grid(value, text):
    """Smallest denominator D in GRID_DENOMS with value within half a unit of the last
    recorded decimal of a multiple of 1/D; None if none fits."""
    tol = 0.5 * 10 ** (-decimals(text)) + 1e-9
    for d in GRID_DENOMS:
        if abs(value - round(value * d) / d) <= tol:
            return d
    return None


def chance_grid_share(dec):
    """Share of all values with `dec` decimals in [0, 1) that fit each grid by chance."""
    n = 10 ** dec
    counts = collections.Counter()
    for k in range(n):
        v = k / n
        g = inch_grid(v, f"{v:.{dec}f}")
        counts[g] += 1
    cum = {}
    run = 0
    for d in GRID_DENOMS:
        run += counts.get(d, 0)
        cum[d] = round(run / n, 4)
    return cum


def digit_slip(a_text, b_text):
    """True when two numeric strings differ by one digit or one adjacent transposition."""
    a, b = a_text.replace(".", ""), b_text.replace(".", "")
    if len(a) != len(b) or a == b:
        return False
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diff) == 1:
        return True
    return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]


def fmt1(x):
    return f"{x:.1f}"


def classify_axis(rec, mm, other_recorded):
    """Unit of record, fit of the millimetre value and flags for one face and axis."""
    flags = list(rec["markers"])
    res = {"unit_of_record": None, "unit_basis": None, "fit": None, "fit_diff_mm": None,
           "recorded_decimals": None, "recorded_precision": None, "inch_grid": None,
           "mm_decimals": None, "precision_mm": None, "value_from_record_mm": None,
           "mismatch_cause": None}
    mm_vals = mm["values"]
    mm_pos = [v for v in mm_vals if v > 0]
    if mm["parse"] == "malformed":
        flags.append("mm-malformed")
    if mm["parse"] == "range":
        if mm_vals[0] == 0:
            flags.append("range-zero-lower")
        if mm_vals[0] > mm_vals[1]:
            flags.append("range-reversed")
    if mm["value_texts"]:
        res["mm_decimals"] = max(decimals(t) for t in mm["value_texts"])
    has_rec = rec["parse"] in ("number", "range") and any(v > 0 for v in rec["values"])
    if rec["parse"] == "malformed":
        flags.append("recorded-malformed")
    if rec["parse"] == "placeholder":
        flags.append("recorded-placeholder")
    if rec["parse"] == "range" and rec["values"][0] > rec["values"][1]:
        flags.append("range-reversed")

    if not has_rec:
        if mm_pos:
            res["unit_of_record"] = "mm (not stated)"
            res["unit_basis"] = "millimetre field only"
            d = res["mm_decimals"] or 0
            res["precision_mm"] = 10 ** (-d)
        elif mm["parse"] in ("number",) and mm_vals == [0.0]:
            flags.append("placeholder-zero")
        elif mm["parse"] == "empty":
            flags.append("empty")
        return res, flags

    texts = rec["value_texts"]
    vals = rec["values"]
    res["recorded_decimals"] = max(decimals(t) for t in texts)
    if not mm_pos:
        flags.append("conversion-missing" if mm["parse"] in ("number", "range") else "mm-missing")
        if rec["unit_stated"]:
            res["unit_of_record"] = rec["unit_stated"]
            res["unit_basis"] = "stated in the recorded string"
        else:
            guess = "inch" if max(vals) < 10 else "mm"
            res["unit_of_record"] = guess
            res["unit_basis"] = "magnitude only (no millimetre value to compare)"
        factor = dict(FACTORS)[res["unit_of_record"]]
        res["value_from_record_mm"] = [round(v * factor, 3) for v in vals]
        res["recorded_precision"] = f"{10 ** (-res['recorded_decimals']):g} {res['unit_of_record']}"
        if res["unit_of_record"] == "inch":
            res["inch_grid"] = max((inch_grid(v, t) or 0) for v, t in zip(vals, texts)) or None
            res["precision_mm"] = round(25.4 * 10 ** (-res["recorded_decimals"]), 3)
        else:
            res["precision_mm"] = round(factor * 10 ** (-res["recorded_decimals"]), 3)
        return res, flags

    # pair recorded values with millimetre values (ranges by position)
    pairs = []
    if len(vals) == len(mm_vals):
        # ranges are compared end to end after sorting, since some strings are reversed
        rv = sorted(zip(vals, texts))
        mv = sorted(zip(mm_vals, mm["value_texts"]))
        pairs = [(a[0], b[0], a[1], b[1]) for a, b in zip(rv, mv)]
    elif len(vals) == 1 and len(mm_vals) == 2:
        # a single recorded value against a millimetre range: pair it with the end it fits
        unit_try = [rec["unit_stated"]] if rec["unit_stated"] else [u for u, _ in FACTORS]
        ends = [(abs(mm_vals[i] - dict(FACTORS)[u] * vals[0]), i) for i in (0, 1) for u in unit_try if mm_vals[i] > 0]
        i = min(ends)[1] if ends else 1
        pairs = [(vals[0], mm_vals[i], texts[0], mm["value_texts"][i])]
        flags.append("recorded-number-vs-mm-range-" + ("min" if i == 0 else "max"))
    elif len(vals) == 2 and len(mm_vals) == 1:
        unit_try = [rec["unit_stated"]] if rec["unit_stated"] else [u for u, _ in FACTORS]
        ends = [(abs(mm_vals[0] - dict(FACTORS)[u] * vals[i]), i) for i in (0, 1) for u in unit_try if vals[i] > 0]
        i = min(ends)[1] if ends else 1
        pairs = [(vals[i], mm_vals[0], texts[i], mm["value_texts"][0])]
        flags.append("recorded-range-vs-mm-number")
    pairs = [p for p in pairs if p[1] > 0 and p[0] > 0]
    if not pairs:
        flags.append("unpairable")
        return res, flags

    candidates = FACTORS if not rec["unit_stated"] else [(rec["unit_stated"], dict(FACTORS)[rec["unit_stated"]])]
    best = None
    for unit, factor in candidates:
        worst = max(abs(m - factor * v) for v, m, _, _ in pairs)
        if best is None or worst < best[2]:
            best = (unit, factor, worst)
    unit, factor, worst = best
    fit = fit_class(worst)
    if fit == "mismatch" and not rec["unit_stated"]:
        # report against the inch reading for plain numbers below 10 and mm otherwise
        unit = "inch" if max(vals) < 10 else "mm"
        factor = dict(FACTORS)[unit]
        worst = max(abs(m - factor * v) for v, m, _, _ in pairs)
    res["unit_of_record"] = unit
    res["unit_basis"] = ("stated in the recorded string" if rec["unit_stated"]
                         else "factor that maps the recorded number to the millimetre field")
    res["fit"] = fit
    res["fit_diff_mm"] = round(worst, 3)
    res["value_from_record_mm"] = [round(v * factor, 3) for v in vals]
    res["recorded_precision"] = f"{10 ** (-res['recorded_decimals']):g} {unit}"
    if unit == "inch":
        res["inch_grid"] = max((inch_grid(v, t) or 0) for v, t in zip(vals, texts)) or None
    res["precision_mm"] = round(factor * 10 ** (-res["recorded_decimals"]), 3)
    if unit == "inch" and max(vals) >= 10:
        flags.append("implausible-inch")
    if unit == "mm" and not rec["unit_stated"]:
        flags.append("mm-in-recorded-field")
    if unit == "inch" and any(abs(m - v) <= 0.051 for v, m, _, _ in pairs):
        flags.append("unconverted")
    if fit == "mismatch":
        v, m, t, mt = max(pairs, key=lambda p: abs(p[1] - factor * p[0]))
        conv = factor * v
        cause = None
        for u2, f2 in FACTORS:
            if u2 != unit and abs(m - f2 * v) <= APPROX:
                cause = f"unit slip (fits {u2})"
        if cause is None:
            for ov in other_recorded:
                if ov and abs(m - factor * ov) <= APPROX:
                    cause = "axis exchange (fits another axis's recorded value)"
        if cause is None and (digit_slip(fmt1(conv), fmt1(m)) or digit_slip(t, f"{m / factor:.{max(1, decimals(t))}f}")):
            cause = "one-digit difference (possible typing slip)"
        if cause is None and abs(m - conv) <= 0.5 * factor * 10 ** (-decimals(t)) + 0.6:
            cause = "rounding of a finer original"
        if cause is None:
            cause = "different value (source or measurement)"
        res["mismatch_cause"] = cause
    return res, flags


def implausible(axis, values_mm, group):
    flags = []
    for v in values_mm:
        if v > 1000:
            flags.append("implausible-over-1000mm")
        elif group in ("seal", "tablet, bas-relief", "tablet, incised", "tablet, copper", "tag or sealing") and axis != "thickness":
            if v < 3:
                flags.append("implausible-under-3mm")
            elif v > 150:
                flags.append("implausible-over-150mm")
    return flags


def website_class(lip, web, lip_other, web_other):
    """Compare one axis of Lipi (mm) and the website export."""
    if lip is None and web is None:
        return "both-missing"
    if lip is None or lip == 0:
        return "lipi-missing" if web else "both-missing"
    if web is None or web == 0:
        return "website-zero"
    d = abs(lip - web)
    if d <= EXACT:
        return "equal"
    if d <= ROUNDED:
        return "rounded"
    if d <= APPROX:
        return "approximate"
    if lip_other and web_other and abs(lip - web_other) <= APPROX and abs(lip_other - web) <= APPROX:
        return "swapped"
    if abs(lip - 25.4 * web) <= APPROX:
        return "inch-valued"
    if digit_slip(fmt1(lip), fmt1(web)):
        return "different (digit slip)"
    return "different"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")

    sys.path.insert(0, str(INV))
    import coverage as inv  # noqa: E402  (the inventory's grouping rules, read-only)

    faces = [json.loads(l) for l in FACES.open(encoding="utf-8") if l.strip()]
    website = [json.loads(l) for l in WEBSITE.open(encoding="utf-8") if l.strip()]
    lip_by_fam = collections.OrderedDict()
    for f in faces:
        lip_by_fam.setdefault(f["object_family_id"], []).append(f)

    # Mayig: confirm that no size field exists
    mayig_keys = collections.Counter()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                mayig_keys[k] += 1
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    mayig_files = sorted(glob.glob(str(MAYIG / "**/*.json"), recursive=True))
    for fp in mayig_files:
        walk(json.load(open(fp, encoding="utf-8")))

    sql_decl = re.findall(r"^\s*(WIDTH|HEIGHT|THICKNESS)\s+(\w+)", WEBSITE_SQL.read_text(encoding="utf-8", errors="replace"), re.M)

    # website join: SEALID = family id when the CISI keys agree or both are empty
    web_by_fam = {}
    web_join = collections.Counter()
    lip_by_cisi = collections.defaultdict(list)
    for fam, recs in lip_by_fam.items():
        k = (recs[0]["metadata"].get("cisi") or "").strip()
        if k and k not in ("-", "--"):
            lip_by_cisi[k].append(fam)
    for w in website:
        md = w["metadata"]
        sid = str(md["SEALID"])
        wc = (md.get("CISI") or "").strip()
        lrec = lip_by_fam.get(sid)
        lc = (lrec[0]["metadata"].get("cisi") or "").strip() if lrec else None
        if lrec and (wc == lc or (not wc and lc in ("-", "--", ""))):
            web_by_fam[sid] = (w, "SEALID")
            web_join["sealid_with_matching_cisi_or_both_empty"] += 1
        elif wc and len(lip_by_cisi.get(wc, [])) == 1:
            web_by_fam[lip_by_cisi[wc][0]] = (w, "CISI")
            web_join["cisi_key"] += 1
        else:
            web_join["not_joined"] += 1

    def fnum(x):
        try:
            v = float(x)
        except (TypeError, ValueError):
            return None
        return v

    face_rows = []
    for f in faces:
        md = f["metadata"]
        group = inv.type_group(md.get("type"))
        recs = {ax: parse_recorded(md.get(rf)) for ax, rf, _, _ in AXES}
        for ax, rf, mf, wf in AXES:
            others = [v for ax2, r2 in recs.items() if ax2 != ax for v in r2["values"]]
            mm = parse_mm(md.get(mf))
            res, flags = classify_axis(recs[ax], mm, others)
            mm_pos = [v for v in mm["values"] if v > 0]
            flags += implausible(ax, mm_pos or (res["value_from_record_mm"] or []), group)
            face_rows.append({
                "record_id": f["record_id"], "object_family_id": f["object_family_id"],
                "cisi": (md.get("cisi") or "").strip(), "site": md.get("site"), "type": md.get("type"),
                "type_group": group, "axis": ax,
                "lipi_recorded_field": rf, "lipi_recorded_raw": recs[ax]["raw"] or "",
                "lipi_mm_field": mf, "lipi_mm_raw": md.get(mf) if md.get(mf) is not None else "",
                "mm_min": min(mm_pos) if mm_pos else None, "mm_max": max(mm_pos) if mm_pos else None,
                **res, "flags": flags,
            })

    # faces of one object: agreement
    by_obj_axis = collections.defaultdict(list)
    for r in face_rows:
        by_obj_axis[(r["object_family_id"], r["axis"])].append(r)
    obj_rows = []
    faces_differ = 0
    for (fam, ax), rows in by_obj_axis.items():
        sig = {(r["lipi_recorded_raw"].strip(), str(r["lipi_mm_raw"]).strip()) for r in rows}
        base = dict(rows[0])
        base["face_records"] = ";".join(r["record_id"] for r in rows)
        if len(sig) > 1:
            faces_differ += 1
            base["flags"] = base["flags"] + ["faces-differ"]
        obj_rows.append(base)

    # website comparison per object and axis
    web_counts = collections.Counter()
    web_axis_counts = collections.Counter()
    web_disagreements = []
    obj_index = {(r["object_family_id"], r["axis"]): r for r in obj_rows}
    for fam in lip_by_fam:
        if fam not in web_by_fam:
            for ax, *_ in AXES:
                r = obj_index[(fam, ax)]
                r["website_value"] = None
                r["website_relation"] = "no-website-record"
                r["website_join"] = None
            continue
        w, how = web_by_fam[fam]
        wmd = w["metadata"]
        wv = {ax: fnum(wmd.get(wf)) for ax, _, _, wf in AXES}
        lv = {ax: (obj_index[(fam, ax)]["mm_max"]) for ax, *_ in AXES}
        lmin = {ax: (obj_index[(fam, ax)]["mm_min"]) for ax, *_ in AXES}
        rels = {}
        for ax, *_ in AXES:
            other = "vertical" if ax == "horizontal" else "horizontal" if ax == "vertical" else None
            rels[ax] = website_class(lv[ax], wv[ax], lv.get(other) if other else None, wv.get(other) if other else None)
            if lmin[ax] is not None and lmin[ax] != lv[ax] and wv[ax] and rels[ax] not in ("equal", "rounded", "approximate"):
                # Lipi holds a range: the website may hold its lower end
                if abs(lmin[ax] - wv[ax]) <= APPROX:
                    rels[ax] = "equals Lipi range minimum"
            r = obj_index[(fam, ax)]
            r["website_value"] = wv[ax]
            r["website_relation"] = rels[ax]
            r["website_join"] = how
            r["website_decimals"] = decimals(str(wmd.get(AXES[[x[0] for x in AXES].index(ax)][3]))) if wmd.get(AXES[[x[0] for x in AXES].index(ax)][3]) is not None else None
            web_axis_counts[(ax, rels[ax])] += 1
            if rels[ax] == "swapped":
                r["flags"] = r["flags"] + ["swapped-axes-vs-website"]
        disagree = [ax for ax in rels if rels[ax] in ("swapped", "inch-valued", "different", "different (digit slip)")]
        comparable = [ax for ax in rels if rels[ax] in ("equal", "rounded", "approximate", "swapped", "inch-valued", "different", "different (digit slip)")]
        if not comparable:
            web_counts["objects_no_comparable_axis"] += 1
        elif disagree:
            web_counts["objects_disagree_on_an_axis"] += 1
            for ax in disagree:
                r = obj_index[(fam, ax)]
                conv = r["value_from_record_mm"] or []
                web_disagreements.append({"object_family_id": fam, "cisi": r["cisi"], "site": r["site"], "type": r["type"], "axis": ax,
                                          "lipi_mm": lv[ax], "website": wv[ax], "relation": rels[ax],
                                          "lipi_recorded_raw": r["lipi_recorded_raw"], "unit_of_record": r["unit_of_record"],
                                          "website_equals_conversion_of_lipi_recorded_value": bool(conv and wv[ax] and any(abs(c - wv[ax]) <= APPROX for c in conv)),
                                          "join": how})
        else:
            web_counts["objects_agree_on_all_comparable_axes"] += 1

    # inventory-style replication of the 206/2,018 comparison (sorted plain numbers, 0.6 mm)
    inv_cmp = collections.Counter()
    for fam, (w, how) in web_by_fam.items():
        if how != "SEALID" and how != "CISI":
            continue
    # ---------------- summaries ----------------
    s = {}
    unit_counts = collections.Counter()
    fit_counts = collections.Counter()
    prec_counts = collections.Counter()
    grid_counts = collections.Counter()
    grid_by_dec = collections.Counter()
    flag_counts = collections.Counter()
    cause_counts = collections.Counter()
    mm_only_prec = collections.Counter()
    for r in face_rows:
        unit_counts[(r["axis"], r["unit_of_record"] or "none")] += 1
        if r["fit"]:
            fit_counts[(r["unit_of_record"], r["fit"])] += 1
        if r["recorded_precision"]:
            prec_counts[(r["unit_of_record"], r["recorded_precision"])] += 1
        if r["unit_of_record"] == "inch" and r["recorded_decimals"] is not None:
            grid_counts[(r["recorded_decimals"], r["inch_grid"])] += 1
            grid_by_dec[r["recorded_decimals"]] += 1
        if r["unit_of_record"] == "mm (not stated)":
            mm_only_prec[r["mm_decimals"]] += 1
        for fl in r["flags"]:
            flag_counts[fl] += 1
        if r["mismatch_cause"]:
            cause_counts[r["mismatch_cause"]] += 1

    grid_observed = {}
    for dec in sorted(grid_by_dec):
        n = grid_by_dec[dec]
        run = 0
        cum = {}
        for d in GRID_DENOMS:
            run += grid_counts.get((dec, d), 0)
            cum[str(d)] = {"values": run, "share": round(run / n, 4)}
        grid_observed[str(dec)] = {"inch_values": n, "cumulative_fit": cum,
                                   "chance_cumulative_share": {str(k): v for k, v in chance_grid_share(dec).items()}}

    # mm-only values: do they sit on a sixteenth-inch grid more than chance?
    mm_only_grid = collections.Counter()
    for r in face_rows:
        if r["unit_of_record"] == "mm (not stated)" and r["mm_decimals"] == 1 and r["mm_max"]:
            inch = r["mm_max"] / 25.4
            on = abs(inch * 16 - round(inch * 16)) * 25.4 / 16 <= 0.051
            mm_only_grid["on_sixteenth_grid" if on else "off"] += 1
    n_grid = sum(mm_only_grid.values())
    expected_share = round(0.1 / (25.4 / 16), 4)  # 0.1 mm window on a 1.5875 mm grid

    s["faces"] = len(faces)
    s["objects"] = len(lip_by_fam)
    s["face_axis_values"] = len(face_rows)
    s["unit_of_record_by_axis"] = {f"{ax}|{u}": n for (ax, u), n in sorted(unit_counts.items())}
    s["unit_of_record_totals"] = dict(collections.Counter(r["unit_of_record"] or "none" for r in face_rows))
    s["fit_of_mm_value_by_unit"] = {f"{u}|{fit}": n for (u, fit), n in sorted(fit_counts.items())}
    s["recorded_precision"] = {f"{u}|{p}": n for (u, p), n in sorted(prec_counts.items(), key=lambda kv: str(kv[0]))}
    s["inch_fraction_grid"] = grid_observed
    s["mm_only_decimals"] = {str(k): v for k, v in sorted(mm_only_prec.items(), key=lambda kv: str(kv[0]))}
    s["mm_only_one_decimal_on_sixteenth_inch_grid"] = {"values": n_grid, "on_grid": mm_only_grid["on_sixteenth_grid"],
                                                       "share": round(mm_only_grid["on_sixteenth_grid"] / n_grid, 4) if n_grid else None,
                                                       "chance_share": expected_share}
    s["flags"] = dict(flag_counts.most_common())
    s["mismatch_causes"] = dict(cause_counts.most_common())
    s["faces_differ_on_axis_objects"] = faces_differ
    s["website"] = {"records": len(website), "join": dict(web_join), "sql_declarations": [list(x) for x in sql_decl],
                    "objects": dict(web_counts),
                    "axis_relations": {f"{ax}|{rel}": n for (ax, rel), n in sorted(web_axis_counts.items())}}
    s["mayig"] = {"files": len(mayig_files), "keys": dict(mayig_keys), "size_fields": [k for k in mayig_keys if re.search(r"size|width|height|thick|dim|mm", k, re.I)]}
    s["inventory_replication"] = {}
    # replicate the inventory's paired inch/mm count with its own rule
    rep = collections.Counter()
    for f in faces:
        md = f["metadata"]
        for mmf, inf in inv.INCH_FIELDS.items():
            mm, inch = inv.norm(md.get(mmf)), inv.norm(md.get(inf))
            if inv.is_number(mm) and inv.is_number(inch) and float(mm) > 0 and float(inch) > 0:
                rep["both_present"] += 1
                rep["within_0.6" if abs(float(mm) - 25.4 * float(inch)) <= 0.6 else "differs"] += 1
    s["inventory_replication"]["lipi_inch_vs_mm_fields"] = dict(rep)

    # grid tests: are millimetre-only values conversions of lost inch values, and are
    # two-decimal inch values conversions of whole millimetres?
    def on_grid(x, step, tol):
        return abs(x - round(x / step) * step) <= tol
    grid_tests = {}
    mm1 = [r["mm_max"] for r in face_rows if r["unit_of_record"] == "mm (not stated)" and r["mm_decimals"] == 1 and r["mm_max"]]
    mm0 = [r["mm_max"] for r in face_rows if r["unit_of_record"] == "mm (not stated)" and r["mm_decimals"] == 0 and r["mm_max"]]
    grid_tests["mm_only_one_decimal_on_0.1in_grid"] = {"values": len(mm1), "on_grid": sum(on_grid(x, 2.54, 0.051) for x in mm1), "chance_share": round(0.102 / 2.54, 4)}
    grid_tests["mm_only_one_decimal_on_0.01in_grid"] = {"values": len(mm1), "on_grid": sum(on_grid(x, 0.254, 0.051) for x in mm1), "chance_share": round(0.102 / 0.254, 4)}
    grid_tests["mm_only_whole_on_0.1in_grid"] = {"values": len(mm0), "on_grid": sum(on_grid(x, 2.54, 0.5) for x in mm0), "chance_share": round(1.0 / 2.54, 4)}
    inch2 = [(v, t) for r in face_rows if r["unit_of_record"] == "inch" and r["recorded_decimals"] == 2
             for v, t in zip(parse_recorded(r["lipi_recorded_raw"])["values"], parse_recorded(r["lipi_recorded_raw"])["value_texts"]) if v > 0]
    grid_tests["two_decimal_inch_equal_to_whole_mm_rounded"] = {"values": len(inch2), "on_grid": sum(on_grid(25.4 * v, 1.0, 0.127) for v, _ in inch2), "chance_share": 0.254}
    inch1 = [v for r in face_rows if r["unit_of_record"] == "inch" and r["recorded_decimals"] == 1 for v in parse_recorded(r["lipi_recorded_raw"])["values"] if v > 0]
    grid_tests["one_decimal_inch_values"] = {"values": len(inch1)}
    for k, d in grid_tests.items():
        if "on_grid" in d and d["values"]:
            d["share"] = round(d["on_grid"] / d["values"], 4)
    s["grid_tests"] = grid_tests

    # the inventory's 228 paired values that differ from the inch conversion, in this audit's classes
    inv228 = collections.Counter()
    face_axis_idx = {(r["record_id"], r["lipi_mm_field"]): r for r in face_rows}
    for f in faces:
        md = f["metadata"]
        for mmf, inf in inv.INCH_FIELDS.items():
            mm, inch = inv.norm(md.get(mmf)), inv.norm(md.get(inf))
            if inv.is_number(mm) and inv.is_number(inch) and float(mm) > 0 and float(inch) > 0 and abs(float(mm) - 25.4 * float(inch)) > 0.6:
                r = face_axis_idx[(f["record_id"], mmf)]
                inv228[f"{r['unit_of_record']}|{r['fit']}"] += 1
    s["inventory_228_in_audit_classes"] = dict(inv228.most_common())

    # the inventory's 2,018 / 206 website comparison, with the reason for each difference
    inv_web = collections.Counter()
    web_by_cisi = {}
    for w in website:
        k = (w["metadata"].get("CISI") or "").strip()
        if k:
            web_by_cisi.setdefault(k, w)
    for k, w in web_by_cisi.items():
        if k not in lip_by_cisi:
            continue
        lmd = lip_by_fam[lip_by_cisi[k][0]][0]["metadata"]
        wmd = w["metadata"]
        wd = [inv.norm(wmd.get(x)) for x in ("WIDTH", "HEIGHT", "THICKNESS")]
        ld = [inv.norm(lmd.get(x)) for x in inv.DIM_FIELDS]
        plain = lambda xs: sorted(float(x) for x in xs if inv.is_number(x) and float(x) > 0)
        ws, ls = plain(wd), plain(ld)
        if not ws or not ls:
            inv_web["one_side_missing"] += 1
            continue
        if len(ws) == len(ls) and all(abs(a - b) <= 0.6 for a, b in zip(ws, ls)):
            inv_web["agree"] += 1
            continue
        if len(ws) != len(ls):
            lrange = bool(inv.RANGE.match(ld[2]))
            wpos = [inv.is_number(x) and float(x) > 0 for x in wd]
            lpos = [inv.is_number(x) and float(x) > 0 for x in ld]
            if lrange:
                inv_web["differ: Lipi thickness is a printed range, not a plain number"] += 1
            elif wpos != lpos:
                inv_web["differ: one source has a zero where the other has a value"] += 1
            else:
                inv_web["differ: other count difference"] += 1
        else:
            inv_web["differ: values differ beyond 0.6 mm"] += 1
    s["inventory_website_comparison_reasons"] = dict(inv_web.most_common())

    # ---------------- seals in the October 12 split ----------------
    sys.path.insert(0, str(SHOT_A))
    from seal_table import seal_table  # noqa: E402
    import rank_lib as L  # noqa: E402
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    rows = [dict(f, half=split[f["object_family_id"]]["half"], component=split[f["object_family_id"]]["component"]) for f in faces]
    face_axis = {(r["record_id"], r["axis"]): r for r in face_rows}
    split_out = {"split_sha256": sha256(SPLIT), "faces_sha256": sha256(FACES)}
    detail = []
    for half in ("discovery", "confirmation"):
        table = seal_table([r for r in rows if r["half"] == half])
        for t in table:
            t["half"] = half
        pops = {
            "all_seal_families_size_ok": [t for t in table if t["size_ok"]],
            "shot_a_size_text_population_one_per_component": L.representative(L.size_text_population(table)),
        }
        for pname, pop in pops.items():
            c = collections.Counter()
            for t in pop:
                hr = face_axis[(t["record_id"], "horizontal")]
                vr = face_axis[(t["record_id"], "vertical")]
                units = {hr["unit_of_record"], vr["unit_of_record"]}
                c["seals"] += 1
                if units == {"inch"}:
                    c["both_face_dims_inch_conversions"] += 1
                    decs = {hr["recorded_decimals"], vr["recorded_decimals"]}
                    if decs <= {0, 1}:
                        c["both_rounded_to_0.1in_or_coarser"] += 1
                    if decs & {0, 1}:
                        c["any_rounded_to_0.1in_or_coarser"] += 1
                    if 2 in decs:
                        c["any_two_decimal_inch"] += 1
                    if all(x["inch_grid"] in (2, 4, 8, 16) for x in (hr, vr)):
                        c["both_on_sixteenth_inch_grid"] += 1
                elif units == {"mm (not stated)"}:
                    c["both_face_dims_mm_not_stated"] += 1
                    if {hr["mm_decimals"], vr["mm_decimals"]} == {0}:
                        c["both_whole_mm"] += 1
                elif units <= {"cm", "mm"}:
                    c["both_face_dims_metric_stated_or_inferred"] += 1
                else:
                    c["mixed_units"] += 1
                if any(x["fit"] == "mismatch" for x in (hr, vr)):
                    c["mm_value_mismatches_recorded"] += 1
                if any(x["fit"] in ("rounded", "approximate") for x in (hr, vr)):
                    c["mm_value_rounded_from_recorded"] += 1
                if any("swapped-axes-vs-website" in x["flags"] for x in (hr, vr)):
                    c["swapped_axes_vs_website"] += 1
                if any(x.get("website_relation") in ("different", "different (digit slip)", "inch-valued") for x in (obj_index[(t["family"], "horizontal")], obj_index[(t["family"], "vertical")])):
                    c["differs_from_website"] += 1
                if any(fl.startswith("implausible") for x in (hr, vr) for fl in x["flags"]):
                    c["implausible_flag"] += 1
                if any("extant" in x["flags"] for x in (hr, vr)):
                    c["extant_marker"] += 1
                if abs((t["h"] or 0) - 25.4) < 0.05 or abs((t["v"] or 0) - 25.4) < 0.05:
                    c["a_face_dimension_equal_to_25.4mm"] += 1
                if pname.startswith("shot_a"):
                    detail.append({"half": half, "family": t["family"], "cisi": t["cisi"],
                                   "h_unit": hr["unit_of_record"], "v_unit": vr["unit_of_record"],
                                   "h_recorded_decimals": hr["recorded_decimals"], "v_recorded_decimals": vr["recorded_decimals"],
                                   "h_inch_grid": hr["inch_grid"], "v_inch_grid": vr["inch_grid"],
                                   "h_precision_mm": hr["precision_mm"], "v_precision_mm": vr["precision_mm"]})
            split_out[f"{half}|{pname}"] = dict(c)

    out.mkdir(parents=True)
    obj_cols = ["object_family_id", "face_records", "cisi", "site", "type", "type_group", "axis",
                "lipi_recorded_field", "lipi_recorded_raw", "lipi_mm_field", "lipi_mm_raw", "mm_min", "mm_max",
                "unit_of_record", "unit_basis", "recorded_decimals", "recorded_precision", "inch_grid",
                "value_from_record_mm", "fit", "fit_diff_mm", "mismatch_cause", "mm_decimals", "precision_mm",
                "website_join", "website_value", "website_decimals", "website_relation", "flags"]
    with (out / "dimension-table.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=obj_cols, extrasaction="ignore")
        wr.writeheader()
        for r in obj_rows:
            r = dict(r)
            r["flags"] = ";".join(r["flags"])
            r["value_from_record_mm"] = ";".join(str(x) for x in r["value_from_record_mm"]) if r.get("value_from_record_mm") else ""
            wr.writerow(r)
    mism = [r for r in face_rows if r["fit"] == "mismatch"]
    with (out / "conversion-mismatches.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["record_id", "object_family_id", "cisi", "site", "type", "axis", "lipi_recorded_raw", "lipi_mm_raw",
                "unit_of_record", "value_from_record_mm", "fit_diff_mm", "mismatch_cause"]
        wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        wr.writeheader()
        for r in mism:
            r = dict(r)
            r["value_from_record_mm"] = ";".join(str(x) for x in r["value_from_record_mm"] or [])
            wr.writerow(r)
    with (out / "website-disagreements.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["object_family_id", "cisi", "site", "type", "axis", "lipi_mm", "website", "relation", "lipi_recorded_raw", "unit_of_record",
                "website_equals_conversion_of_lipi_recorded_value", "join"]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(web_disagreements)
    with (out / "split-seal-dimension-detail.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = list(detail[0].keys()) if detail else ["half"]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(detail)
    (out / "summary.json").write_text(json.dumps(s, indent=1), encoding="utf-8")
    (out / "split-counts.json").write_text(json.dumps(split_out, indent=1), encoding="utf-8")
    (out / "input-hashes.json").write_text(json.dumps({
        "lipi_faces": sha256(FACES), "website": sha256(WEBSITE), "website_sql": sha256(WEBSITE_SQL), "split": sha256(SPLIT),
        "seal_table.py": sha256(SHOT_A / "seal_table.py"), "rank_lib.py": sha256(SHOT_A / "rank_lib.py"),
        "inventory_coverage.py": sha256(INV / "coverage.py")}, indent=1), encoding="utf-8")
    print(json.dumps({"out": str(out.relative_to(ROOT)), "face_axis_values": len(face_rows), "mismatches": len(mism),
                      "website_disagreement_rows": len(web_disagreements)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
