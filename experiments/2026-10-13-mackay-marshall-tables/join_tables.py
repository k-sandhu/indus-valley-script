#!/usr/bin/env python3
"""Join the Mackay 1938 and Marshall 1931 seal-table rows to Lipi object families.

Usage (from the repository root):
    python -P experiments/2026-10-13-mackay-marshall-tables/join_tables.py \
        --out experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13 \
        --local data/raw/2026-10-13-mackay-marshall-tables/run-2026-10-13

Inputs (local-only): the epachayan clone at the pinned commit and
data/normalized/lipi_observed_faces.jsonl. The rules are those of PROTOCOL.md with its
amendments. The tracked output directory receives identifiers, table values (CC BY 4.0,
Koshy 2026), dispositions, agreement judgements and counts; Lipi field values appear only
in the local directory. Neither output directory may already exist.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CLONE = ROOT / "data/raw/2026-10-13-mackay-marshall-tables/epachayan-indus-script"
MACKAY_CSV = CLONE / "outputs/mackay_seal_table.csv"
MARSHALL_CSV = CLONE / "outputs/marshall_seal_table_transcribed.csv"
LIPI = ROOT / "data/normalized/lipi_observed_faces.jsonl"
ADJUDICATION = pathlib.Path(__file__).resolve().parent / "verification/contradiction-adjudication.csv"
EXPECTED = {
    "mackay": "0d2499b2079d05fd",  # prefix of sha256 of the committed blob
    "marshall": "5a339a7884d34cc9",
    "lipi": "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db",
}

# Usable-value rule of the 12 October data inventory (experiments/2026-10-12-data-inventory/coverage.py).
PLACEHOLDERS = {"", "-", "--", "- -", "?", "??", "unknown"}
RANGE = re.compile(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$")

# Marshall area -> prefixes under which the Lipi export writes the same registration
# (Amendment 1: observed on serial+plate-number matches during development).
MARSHALL_ALIASES = {
    "HR": ["HR"], "VS": ["VS"], "SD": ["SD"], "L": ["L"], "BJ": ["BJ"], "DM": ["DM"], "MUS": ["MUS"],
    "DK": ["DK", "DKA", "DKB", "DKC", "DKD", "DKE", "DKF"],
    "C": ["DKC", "C"], "E": ["DKE", "E"], "B": ["DKB", "B"], "A": ["DKA", "A"], "F": ["DKF", "F"],
    "D": ["D", "DKD"],
}
MATERIAL_CLASS = {
    "steatite": "steatite",
    "faience": "faience", "paste": "faience", "v. paste": "faience",
    "clay": "fired clay", "terracotta": "fired clay", "pottery": "fired clay", "ceramic": "fired clay", "stoneware": "fired clay",
    "copper": "metal", "silver": "metal", "gold": "metal", "metal": "metal",
    "ivory": "ivory, bone or shell", "bone": "ivory, bone or shell", "shell": "ivory, bone or shell",
    "calcite": "other stone", "marble": "other stone", "limestone": "other stone", "agate": "other stone",
    "stone": "other stone", "soft stone": "other stone", "gypsum": "other stone",
}
SQUARE_TYPES = {"B", "C"}
RECT_TYPES = {"D", "F"}
SIZE_AGREE = 0.06
SIZE_CONTRADICT = 0.15
LEVEL_AGREE = 0.2


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(v) -> str:
    return re.sub(r"\s+", " ", str(v if v is not None else "")).strip()


def usable(v) -> bool:
    return clean(v).lower() not in PLACEHOLDERS


def num(v):
    t = clean(v)
    try:
        x = float(t)
    except ValueError:
        m = RANGE.match(t)
        x = max(float(m.group(1)), float(m.group(2))) if m else None
    return x if x is not None and x > 0 else None


def key(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def edit1(a: str, b: str) -> bool:
    """True if a and b differ by one substitution, insertion, deletion or adjacent transposition."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        diff = [i for i in range(la) if a[i] != b[i]]
        if len(diff) == 1:
            return True
        return len(diff) == 2 and diff[1] == diff[0] + 1 and a[diff[0]] == b[diff[1]] and a[diff[1]] == b[diff[0]]
    if la > lb:
        a, b = b, a
    return any(a == b[:i] + b[i + 1:] for i in range(len(b)))


# ---------------------------------------------------------------- table rows

def parse_dims(text: str):
    """'1.05x1.05x0.32' -> ([1.05, 1.05], 0.32); '?' parts -> None; 'Dm. 0.75' -> diameter."""
    t = clean(text)
    if not t:
        return [], None, False
    if t.lower().startswith("dm."):
        d = num(t[3:])
        return ([d] if d else []), None, True
    if "thick" in t:
        return [], num(t.split()[0]), False
    parts = [p.strip() for p in t.split("x")]
    vals = [num(p) if p not in ("?", "") else None for p in parts]
    face = [v for v in vals[:2] if v]
    thick = vals[2] if len(vals) > 2 else None
    return face, thick, False


def load_tables():
    rows = []
    for r in csv.DictReader(MACKAY_CSV.open(encoding="utf-8")):
        face, thick, _ = parse_dims(r["dims_in"])
        mat = clean(r["material"])
        lvl = clean(r["level_ft"])
        rows.append({
            "source": "mackay1938",
            "row_id": f"mackay1938:{r['no']}",
            "cat_no": r["no"],
            "type": clean(r["type"]),
            "size_as_printed": clean(r["dims_in"]),
            "face_in": face,
            "thick_in": thick,
            "material": mat,
            "material_usable": bool(mat) and "ditto after" not in mat.lower(),
            "block": clean(r["block"]), "house": clean(r["house"]), "room": clean(r["room"]), "street": clean(r["street"]),
            "area": clean(r["area"]),
            "level": lvl,
            "level_value": (0.0 if lvl == "surface" else (float(lvl) if re.fullmatch(r"[+-]?\d+(\.\d+)?", lvl) else None)),
            "level_reference": "SD bench mark (2.2 ft above the DK datum)" if r["area"] == "SD" else "DK datum",
            "field_no": clean(r["field_no"]),
            "field_key": key(r["field_no"]),
            "field_prefixes": [re.match(r"[A-Z]+", key(r["field_no"])).group()] if r["field_no"] else [],
            "field_digits": re.sub(r"^[A-Z]+", "", key(r["field_no"])),
            "printed_page": int(r["pdf_page"]) + 324,
        })
    for r in csv.DictReader(MARSHALL_CSV.open(encoding="utf-8")):
        face, thick, diam = parse_dims(r["size_in"])
        mat = clean(r["material"])
        area, serial = clean(r["area"]), clean(r["serial"])
        lf = clean(r["level_ft"])
        if lf == "surface":
            lv = 0.0
        else:
            try:
                lv = float(r["depth_ft"]) if clean(r["depth_ft"]) else None
            except ValueError:
                lv = None
        rows.append({
            "source": "marshall1931",
            "row_id": f"marshall1931:{r['plate_no']}",
            "cat_no": r["plate_no"],
            "type": clean(r["type"]),
            "size_as_printed": clean(r["size_in"]),
            "face_in": face,
            "thick_in": thick,
            "material": mat,
            "material_usable": bool(mat),
            "block": "", "house": "", "room": "", "street": "",
            "area": area,
            "level": (f"{lf} ft {clean(r['level_in'])} in" if lf and lf not in ("surface",) and re.fullmatch(r"\d+", lf) else lf),
            "level_value": lv,
            "level_reference": "below the modern surface",
            "field_no": f"{area} {serial}".strip() if serial else "",
            "field_key": key(area + serial) if serial else "",
            "field_prefixes": MARSHALL_ALIASES.get(area, [key(area)]) if serial else [],
            "field_digits": key(serial),
            "printed_page": int(re.match(r"p(\d+)", r["source_page"]).group(1)),
        })
    return rows


# ---------------------------------------------------------------- Lipi objects

def load_lipi():
    fams = collections.OrderedDict()
    for line in LIPI.open(encoding="utf-8"):
        r = json.loads(line)
        fams.setdefault(r["object_family_id"], []).append(r)
    objs = {}
    for fid, faces in fams.items():
        # object-level value: the first usable value over the family's faces (the inventory's rule)
        md = dict(faces[0]["metadata"])
        for f in faces[1:]:
            for k, v in f["metadata"].items():
                if not usable(md.get(k)) or (k in ("h", "v", "th", "horizontal(mm)", "vertical(mm)", "thickness(mm)") and not num(md.get(k))):
                    if usable(v) and (k not in ("h", "v", "th", "horizontal(mm)", "vertical(mm)", "thickness(mm)") or num(v)):
                        md[k] = v
        idno = clean(md.get("excavation-idno"))
        prefix, kind, head, listed = parse_idno(idno) if usable(idno) else ("", "other", "", [])
        h = num(md.get("h")) or (num(md.get("horizontal(mm)")) / 25.4 if num(md.get("horizontal(mm)")) else None)
        v = num(md.get("v")) or (num(md.get("vertical(mm)")) / 25.4 if num(md.get("vertical(mm)")) else None)
        th = num(md.get("th")) or (num(md.get("thickness(mm)")) / 25.4 if num(md.get("thickness(mm)")) else None)
        depth = clean(md.get("depth"))
        dm = re.match(r"^([+-]?\d+(?:[.:]\d+)?)\s*ft$", depth)
        objs[fid] = {
            "fid": fid,
            "cisi": clean(faces[0].get("source_cisi")),
            "site": clean(md.get("site")),
            "type": clean(md.get("type")),
            "idno": idno,
            "idno_prefix": prefix,
            "idno_kind": kind,
            "idno_head": head,
            "idno_listed": listed,
            "material": clean(md.get("material")),
            "area": clean(md.get("area-section")),
            "block_house": clean(md.get("block-house")),
            "room_grid": clean(md.get("room-grid")),
            "depth": depth,
            "depth_value": float(dm.group(1).replace(":", ".")) if dm else None,
            "face_in": [x for x in (h, v) if x],
            "thick_in": th,
            "md": md,
        }
    return objs


# ---------------------------------------------------------------- comparisons

def type_compare(row, obj):
    """'agree', 'disagree', 'contradict' or 'n/a'. Lipi SEAL:S square, SEAL:R rectangular,
    SEAL:C circular, SEAL:CY cylinder, SEAL unspecified (not compared). Protocol: a contradiction is a square seal (table
    type B or C) against a cylinder, tablet or sealing."""
    lt = obj["type"].upper()
    tt = re.sub(r"[^A-Z]", "", row["type"].upper())
    if not tt or not lt or lt == "-" or lt == "SEAL":
        return "n/a"
    if tt in SQUARE_TYPES and (lt == "SEAL:CY" or lt.startswith("TAB") or lt.startswith("TAG")):
        return "contradict"
    expected = {"B": "SEAL:S", "C": "SEAL:S", "D": "SEAL:R", "F": "SEAL:R", "A": "SEAL:CY"}.get(tt)
    if expected is None:
        return "n/a"
    return "agree" if lt == expected else "disagree"


def mat_class(text: str):
    t = clean(text).lower()
    t = re.sub(r"\s*\(.*\)$", "", t)
    return MATERIAL_CLASS.get(t)


def material_compare(row, obj):
    if not row["material_usable"] or not usable(obj["material"]):
        return "n/a"
    a, b = mat_class(row["material"]), mat_class(obj["material"])
    if a is None or b is None:
        return "n/a"
    if a == b:
        return "agree"
    if {a, b} == {"steatite", "other stone"}:
        return "disagree"
    return "contradict"


def size_compare(row, obj):
    t, l = sorted(row["face_in"]), sorted(obj["face_in"])
    if not t or not l:
        return "n/a"
    if len(t) == 2 and len(l) == 2:
        d = [abs(t[0] - l[0]), abs(t[1] - l[1])]
        if max(d) <= SIZE_AGREE:
            return "agree"
        return "contradict" if d[1] > SIZE_CONTRADICT else "disagree"
    short, other = (t, l) if len(t) <= len(l) else (l, t)
    best = min(abs(x - y) for x in short for y in other)
    if best <= SIZE_AGREE:
        return "agree"
    return "contradict" if best > SIZE_CONTRADICT else "disagree"


def thickness_compare(row, obj):
    if row["thick_in"] is None or obj["thick_in"] is None:
        return "n/a"
    return "agree" if abs(row["thick_in"] - obj["thick_in"]) <= SIZE_AGREE else "disagree"


ROMAN = re.compile(r"^(\d+A?)([IVXL]+)?-?$")


def findspot_compare(row, obj):
    if row["source"] != "mackay1938" or not row["block"]:
        return "n/a"
    m = ROMAN.match(obj["block_house"].replace(" ", ""))
    if not m:
        return "n/a"
    checks = [row["block"].upper() == m.group(1).upper()]
    if row["house"] and m.group(2):
        checks.append(row["house"].upper() == m.group(2).upper())
    rm = re.match(r"^(\d+)", obj["room_grid"])
    if row["room"] and rm:
        checks.append(row["room"] == rm.group(1))
    return "agree" if all(checks) else "disagree"


def level_compare(row, obj):
    if row["level_value"] is None or obj["depth_value"] is None:
        return "n/a"
    if row["source"] == "mackay1938":
        return "agree" if abs(row["level_value"] - obj["depth_value"]) <= LEVEL_AGREE else "disagree"
    return "agree" if abs(abs(row["level_value"]) - abs(obj["depth_value"])) <= LEVEL_AGREE else "disagree"


COMPARATORS = {
    "type": type_compare, "material": material_compare, "size": size_compare,
    "thickness": thickness_compare, "findspot": findspot_compare, "level": level_compare,
}


def compare(row, obj):
    res = {k: f(row, obj) for k, f in COMPARATORS.items()}
    agree = sum(1 for k in ("type", "material", "size", "findspot", "level") if res[k] == "agree")
    contradict = [k for k, v in res.items() if v == "contradict"]
    return res, agree, contradict


# ---------------------------------------------------------------- candidates

def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def parse_idno(idno: str):
    """Split a Lipi excavation-idno into (prefix, kind, head, listed numbers).

    kind 'list': '<digits>[+/<n>]...' where head is the field number, possibly followed
    without a separator by the first catalogue number; 'plate': '<field><ROMAN>:<n>';
    'other': anything else (no key).
    """
    s = clean(idno).upper().replace("[", "").replace("]", "")
    m = re.match(r"^([A-Z][A-Z.\- ]*?)\s*(\d.*)$", s)
    if not m:
        return "", "other", "", []
    prefix = re.sub(r"[^A-Z]", "", m.group(1))
    body = m.group(2).replace(" ", "")
    pm = re.fullmatch(r"(\d+[A-Z]?)([IVXLC]+):(\d+[A-Z]?)", body)
    if pm:
        return prefix, "plate", pm.group(1), [pm.group(3)]
    lm = re.fullmatch(r"(\d+(?:[A-Z]\d*)?)((?:[+/]\d+[A-Z]?)*)", body)
    if lm:
        return prefix, "list", lm.group(1), re.findall(r"[+/](\d+[A-Z]?)", lm.group(2))
    return prefix, "other", "", []


def cat_variants(row):
    no = key(row["cat_no"])
    out = {no}
    m = re.fullmatch(r"(\d+)([A-Z]?)", no)
    if m:
        out.add(m.group(1).zfill(3) + m.group(2))
    return out


def strong_basis(row, obj):
    """Basis string if the Lipi registration carries this row's field number (and, if
    present, its catalogue number), else None."""
    if not row["field_key"] or obj["idno_prefix"] not in row["field_prefixes"]:
        return None
    kind, head, listed = obj["idno_kind"], obj["idno_head"], obj["idno_listed"]
    F, N = row["field_digits"], cat_variants(row)
    if kind == "plate":
        return "field+plate-reference" if head == F and set(listed) & N else None
    if kind != "list":
        return None
    if head == F and not listed:
        return "field-number"
    if head.startswith(F) and len(head) > len(F):
        first = head[len(F):]
        numbers = {first, *listed}
        if first in N:
            return "field+catalogue-number" if not listed else "field+catalogue-numbers (listed)"
        if listed and N & set(listed):
            return "field+catalogue-numbers (listed)"
    return None


def weak_basis(row, obj):
    """Variant keys (Amendment 2): the field number differs by one or two edits with the
    catalogue number exact; the catalogue number differs by one edit with the field number
    exact; or the registration is the field number followed by a single letter."""
    if not row["field_key"] or obj["idno_prefix"] not in row["field_prefixes"] or obj["idno_kind"] != "list":
        return None
    head, F, N = obj["idno_head"], row["field_digits"], cat_variants(row)
    for n in N:
        if head.endswith(n) and len(head) > len(n) and 0 < levenshtein(head[: -len(n)], F) <= 2:
            return "variant-field-number"
    if head.startswith(F) and len(head) > len(F):
        tail = head[len(F):]
        if any(edit1(tail, n) for n in N):
            return "variant-catalogue-number"
    if not obj["idno_listed"] and re.fullmatch(re.escape(F) + r"[A-Z]", head):
        return "field-number with letter suffix"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--local", required=True)
    a = ap.parse_args()
    out, local = ROOT / a.out, ROOT / a.local
    for d in (out, local):
        if d.exists():
            sys.exit(f"refusing to overwrite {d}")

    hashes = {"mackay": sha256(MACKAY_CSV), "marshall": sha256(MARSHALL_CSV), "lipi": sha256(LIPI)}
    for k, v in EXPECTED.items():
        if not hashes[k].startswith(v):
            sys.exit(f"input hash mismatch for {k}: {hashes[k]}")

    rows = load_tables()
    objs = load_lipi()
    md_objs = {f: o for f, o in objs.items() if o["site"] == "Mohenjo-daro"}

    adjud = {}
    if ADJUDICATION.exists():
        for d in csv.DictReader(ADJUDICATION.open(encoding="utf-8")):
            adjud[(d["source_row_id"], d["lipi_family_id"])] = d

    # strong keys first, over all sites (off-site hits are counted, not joined)
    cand = collections.defaultdict(list)  # row_id -> [(fid, basis)]
    offsite = collections.Counter()
    for r in rows:
        for f, o in objs.items():
            b = strong_basis(r, o)
            if b:
                if f in md_objs:
                    cand[r["row_id"]].append((f, b))
                else:
                    offsite[r["source"]] += 1
    strong_fams = {f for c in cand.values() for f, _ in c}
    # weak keys only for rows without a strong candidate and families without a strong row
    for r in rows:
        if cand[r["row_id"]]:
            continue
        for f, o in md_objs.items():
            if f in strong_fams:
                continue
            b = weak_basis(r, o)
            if b:
                cand[r["row_id"]].append((f, b))

    fam_rows = collections.defaultdict(set)
    for rid, c in cand.items():
        for f, _ in c:
            fam_rows[f].add(rid)
    row_by_id = {r["row_id"]: r for r in rows}

    def listed_duplicate(f):
        """All rows claiming family f share one field number and are named in its registration."""
        rs = [row_by_id[x] for x in fam_rows[f]]
        if len(rs) < 2 or len({x["field_key"] for x in rs}) != 1:
            return False
        return all(b.startswith("field+catalogue-number") for x in rs for ff, b in cand[x["row_id"]] if ff == f)

    dispositions = []
    joins = []
    for r in rows:
        c = cand[r["row_id"]]
        comps = {f: compare(r, md_objs[f]) for f, _ in c}
        accepted, rejected, pending = [], [], []
        for f, b in c:
            if not comps[f][2]:
                accepted.append((f, b, ""))
                continue
            d = adjud.get((r["row_id"], f))
            if d and d["decision"] == "accept":
                accepted.append((f, b, "contradiction adjudicated against the printed table"))
            elif d and d["decision"] == "reject":
                rejected.append((f, b))
            else:
                pending.append((f, b))
        disp, reason, chosen = None, "", None
        if not c:
            if not r["field_key"]:
                disp, reason = "unmatched", "no field number printed in the table row"
            else:
                same = [x for x in rows if x is not r and x["field_key"] == r["field_key"] and x["source"] == r["source"]]
                same_joined = [x["row_id"] for x in same if cand[x["row_id"]]]
                if same_joined:
                    disp, reason = "unmatched", "shares its field number with " + ", ".join(same_joined) + ", which is joined; the Lipi registration does not name this row's catalogue number (printed duplicate listing or misprinted field number)"
                else:
                    disp, reason = "unmatched", "field number not found in any form in the Lipi excavation-idno field"
        elif len(accepted) == 1 and not pending and (len(fam_rows[accepted[0][0]]) == 1 or listed_duplicate(accepted[0][0])):
            f, b, note = accepted[0]
            strong = b.startswith("field+") or b == "field-number"
            if strong and not note:
                disp, chosen = "exact", (f, b)
                reason = "single registration match; no confirming attribute contradicts"
                if len(fam_rows[f]) > 1:
                    reason += "; the registration lists this row with " + ", ".join(sorted(fam_rows[f] - {r['row_id']})) + " (printed duplicate listing of one object)"
            elif comps[f][1] >= 2 or note:
                disp, chosen = "confirmed", (f, b)
                bits = [f"{b} key"] if not strong else [f"{b} key"]
                if note:
                    bits.append(note + " (see verification/contradiction-adjudication.csv)")
                if rejected:
                    bits.append(f"{len(rejected)} other candidate(s) rejected after adjudication")
                bits.append(f"{comps[f][1]} confirming attributes agree")
                reason = "; ".join(bits)
            else:
                disp, reason = "ambiguous", f"weak key ({b}) with only {comps[f][1]} agreeing attribute(s)"
        else:
            disp = "ambiguous"
            bits = []
            if len(c) > 1:
                bits.append(f"{len(c)} candidate families")
            shared = [f for f, _ in c if len(fam_rows[f]) > 1 and not listed_duplicate(f)]
            if shared:
                bits.append("candidate family also claimed by " + ", ".join(sorted(x for f in shared for x in fam_rows[f] if x != r["row_id"])))
            if pending:
                bits.append("contradicted, not adjudicated: " + ", ".join(f"{f} ({'/'.join(comps[f][2])})" for f, _ in pending))
            if rejected and not accepted:
                bits.append("all candidates rejected after adjudication")
            reason = "; ".join(bits)
            if rejected and not accepted and not pending:
                disp = "unmatched"
        dispositions.append({
            "source_row_id": r["row_id"], "source": r["source"], "catalogue_no": r["cat_no"],
            "field_no": r["field_no"], "disposition": disp,
            "lipi_family_id": chosen[0] if chosen else "",
            "cisi": md_objs[chosen[0]]["cisi"] if chosen else "",
            "basis": chosen[1] if chosen else "",
            "candidates": "; ".join(f"{f}={md_objs[f]['cisi']} [{b}]" for f, b in c),
            "reason": reason,
        })
        if chosen:
            joins.append((r, md_objs[chosen[0]], chosen[1], disp, comps[chosen[0]]))

    # ---------------------------------------------------------------- outputs
    out.mkdir(parents=True)
    local.mkdir(parents=True)

    def write_csv(path, data, fields):
        with path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            for d in data:
                w.writerow({k: d.get(k, "") for k in fields})

    write_csv(out / "row-dispositions.csv", dispositions,
              ["source_row_id", "source", "catalogue_no", "field_no", "disposition", "lipi_family_id", "cisi", "basis", "candidates", "reason"])

    join_rows, local_rows = [], []
    for r, o, basis, disp, (res, nagree, contra) in joins:
        locus = ", ".join(x for x in [
            f"Block {r['block']}" if r["block"] else "", f"House {r['house']}" if r["house"] else "",
            f"Room {r['room']}" if r["room"] else "", r["street"]] if x)
        join_rows.append({
            "lipi_family_id": o["fid"], "cisi": o["cisi"], "disposition": disp, "basis": basis,
            "source": r["source"], "source_row_id": r["row_id"], "catalogue_no": r["cat_no"],
            "printed_page": r["printed_page"],
            "field_no": r["field_no"], "seal_type": r["type"],
            "size_in_as_printed": r["size_as_printed"], "size_unit": "inch",
            "material": r["material"],
            "area": r["area"], "locus": locus,
            "level_ft": r["level"], "level_reference": r["level_reference"],
            "type_check": res["type"], "material_check": res["material"], "size_check": res["size"],
            "thickness_check": res["thickness"], "findspot_check": res["findspot"], "level_check": res["level"],
        })
        local_rows.append({
            "lipi_family_id": o["fid"], "cisi": o["cisi"], "source_row_id": r["row_id"], "basis": basis, "disposition": disp,
            "lipi_idno": o["idno"], "table_field_no": r["field_no"], "table_no": r["cat_no"],
            "lipi_type": o["type"], "table_type": r["type"],
            "lipi_material": o["material"], "table_material": r["material"],
            "lipi_face_in": " x ".join(f"{x:.2f}" for x in o["face_in"]), "lipi_th_in": o["thick_in"] or "",
            "table_size": r["size_as_printed"],
            "lipi_area": o["area"], "lipi_block_house": o["block_house"], "lipi_room": o["room_grid"],
            "table_locus": f"{r['block']}|{r['house']}|{r['room']}|{r['street']}",
            "lipi_depth": o["depth"], "table_level": r["level"],
            **{f"{k}_check": v for k, v in res.items()},
        })
    jfields = list(join_rows[0].keys()) if join_rows else []
    write_csv(out / "join-table.csv", join_rows, jfields)
    write_csv(local / "join-detail-with-lipi-values.csv", local_rows, list(local_rows[0].keys()) if local_rows else [])

    # candidate detail for ambiguous rows (local, includes Lipi values)
    amb = []
    for d in dispositions:
        if d["disposition"] != "ambiguous":
            continue
        r = row_by_id[d["source_row_id"]]
        for f, b in cand[r["row_id"]]:
            o = md_objs[f]
            res, nag, contra = compare(r, o)
            amb.append({"source_row_id": r["row_id"], "lipi_family_id": f, "cisi": o["cisi"], "basis": b,
                        "lipi_idno": o["idno"], "table_field_no": r["field_no"], "agree": nag, "contradict": "/".join(contra),
                        **{f"{k}_check": v for k, v in res.items()}})
    write_csv(local / "ambiguous-candidates.csv", amb, list(amb[0].keys()) if amb else ["source_row_id"])

    # ---------------------------------------------------------------- coverage
    joined_by_fam = collections.defaultdict(list)
    for r, o, basis, disp, _ in joins:
        joined_by_fam[o["fid"]].append(r)
    groups = {
        "Mohenjo-daro seals": [f for f, o in md_objs.items() if o["type"].upper().startswith("SEAL")],
        "Mohenjo-daro, all objects": list(md_objs.keys()),
        "Seals, all sites": [f for f, o in objs.items() if o["type"].upper().startswith("SEAL")],
        "All objects": list(objs.keys()),
    }

    def before(o, field):
        md = o["md"]
        if field == "size_any":
            return any(num(md.get(k)) for k in ("horizontal(mm)", "vertical(mm)", "thickness(mm)"))
        if field == "size_face_both":
            return bool(num(md.get("horizontal(mm)")) and num(md.get("vertical(mm)")))
        if field == "size_all3":
            return all(num(md.get(k)) for k in ("horizontal(mm)", "vertical(mm)", "thickness(mm)"))
        if field == "size_inch_field":
            return any(num(md.get(k)) for k in ("h", "v", "th"))
        if field == "material":
            return usable(md.get("material"))
        if field == "area":
            return usable(md.get("area-section"))
        if field == "spatial_any":
            return any(usable(md.get(k)) for k in ("area-section", "block-house", "room-grid"))
        if field == "findspot_fine":
            return usable(md.get("block-house")) or usable(md.get("room-grid"))
        if field == "level":
            return usable(md.get("depth"))
        if field == "registration_raw":
            return usable(md.get("excavation-idno"))
        if field == "registration_separated":
            return False
        if field in ("publication_reference", "level_with_datum", "size_with_source"):
            return False
        raise KeyError(field)

    def from_row(r, field):
        if field == "size_any":
            return bool(r["face_in"] or r["thick_in"])
        if field == "size_face_both":
            return len(r["face_in"]) == 2
        if field == "size_all3":
            return len(r["face_in"]) == 2 and r["thick_in"] is not None
        if field == "size_inch_field":
            return bool(r["face_in"] or r["thick_in"])
        if field == "material":
            return r["material_usable"]
        if field == "area":
            return bool(r["area"])
        if field == "spatial_any":
            return bool(r["area"] or r["block"] or r["house"] or r["room"] or r["street"])
        if field == "findspot_fine":
            return bool(r["block"] or r["house"] or r["room"] or r["street"])
        if field == "level":
            return r["level_value"] is not None
        if field in ("registration_raw", "registration_separated"):
            return bool(r["field_no"])
        if field == "publication_reference":
            return True
        if field == "level_with_datum":
            return r["level_value"] is not None
        if field == "size_with_source":
            return bool(r["face_in"] or r["thick_in"])
        raise KeyError(field)

    FIELDS = ["size_any", "size_face_both", "size_all3", "size_inch_field", "material", "area", "spatial_any", "findspot_fine",
              "level", "level_with_datum", "size_with_source", "registration_raw", "registration_separated", "publication_reference"]
    cov = []
    for g, fids in groups.items():
        n = len(fids)
        for field in FIELDS:
            b = sum(1 for f in fids if before(objs[f], field))
            aft = sum(1 for f in fids if before(objs[f], field) or any(from_row(x, field) for x in joined_by_fam.get(f, [])))
            joined_with = sum(1 for f in fids if any(from_row(x, field) for x in joined_by_fam.get(f, [])))
            cov.append({"group": g, "objects": n, "field": field, "before": b, "before_pct": round(100 * b / n, 2),
                        "after": aft, "after_pct": round(100 * aft / n, 2), "gained": aft - b,
                        "joined_objects_with_table_value": joined_with})
    write_csv(out / "coverage.csv", cov, list(cov[0].keys()))

    # disagreements among joined objects (both sides have a value)
    dis = collections.OrderedDict()
    for k in COMPARATORS:
        cnt = collections.Counter(res[k] for _, _, _, _, (res, _, _) in joins)
        dis[k] = {"agree": cnt["agree"], "disagree": cnt["disagree"], "contradict": cnt["contradict"],
                  "not_comparable": cnt["n/a"]}
    by_source = collections.OrderedDict()
    for src in ("mackay1938", "marshall1931"):
        sel = [j for j in joins if j[0]["source"] == src]
        by_source[src] = {k: dict(collections.Counter(res[k] for _, _, _, _, (res, _, _) in sel)) for k in COMPARATORS}
    # object-level: an object disagrees on a field if any of its joined rows does
    obj_dis = collections.OrderedDict()
    by_obj = collections.defaultdict(list)
    for r, o, b, dsp, (res, _, _) in joins:
        by_obj[o["fid"]].append((r, b, res))
    for k in COMPARATORS:
        vals = [[res[k] for _, _, res in v] for v in by_obj.values()]
        obj_dis[k] = {
            "objects_compared": sum(1 for v in vals if any(x != "n/a" for x in v)),
            "objects_disagreeing": sum(1 for v in vals if any(x in ("disagree", "contradict") for x in v)),
        }
    obj_dis["field_number"] = {
        "objects_compared": len(by_obj),
        "objects_disagreeing": sum(1 for v in by_obj.values() if any(b == "variant-field-number" for _, b, _ in v)),
    }
    obj_dis["catalogue_number"] = {
        "objects_compared": len(by_obj),
        "objects_disagreeing": sum(1 for v in by_obj.values() if any(b == "variant-catalogue-number" for _, b, _ in v)),
    }
    mohenjo_seal = {f for f, o in md_objs.items() if o["type"].upper().startswith("SEAL")}
    obj_dis_seal = {k: sum(1 for f, v in by_obj.items() if f in mohenjo_seal and any(res[k] in ("disagree", "contradict") for _, _, res in v)) for k in COMPARATORS}

    # registration disagreement: joined through a variant key
    reg_dis = collections.Counter(b for _, _, b, _, _ in joins)

    disp_counts = collections.OrderedDict()
    for src in ("mackay1938", "marshall1931"):
        disp_counts[src] = dict(collections.Counter(d["disposition"] for d in dispositions if d["source"] == src))
        disp_counts[src]["rows"] = sum(1 for d in dispositions if d["source"] == src)
        disp_counts[src]["unmatched_reasons"] = dict(collections.Counter(d["reason"] for d in dispositions if d["source"] == src and d["disposition"] == "unmatched"))
    basis_counts = {src: dict(collections.Counter(d["basis"] for d in dispositions if d["source"] == src and d["basis"])) for src in ("mackay1938", "marshall1931")}
    fams_joined = collections.Counter(o["type"].split(":")[0] for o in {o["fid"]: o for _, o, _, _, _ in joins}.values())

    summary = {
        "run": out.name,
        "inputs": {"mackay_table_sha256": hashes["mackay"], "marshall_table_sha256": hashes["marshall"],
                   "lipi_faces_sha256": hashes["lipi"], "epachayan_commit": "5c14a01f44296a01256a34e7e5e5e9fd82d9a67f"},
        "rows": {"mackay1938": sum(1 for r in rows if r["source"] == "mackay1938"),
                 "marshall1931": sum(1 for r in rows if r["source"] == "marshall1931")},
        "dispositions": disp_counts,
        "join_basis": basis_counts,
        "joined_rows": len(joins),
        "joined_objects": len({o["fid"] for _, o, _, _, _ in joins}),
        "joined_objects_by_type_prefix": dict(fams_joined),
        "families_claimed_by_more_than_one_row": sum(1 for f, s in fam_rows.items() if len(s) > 1),
        "strong_key_hits_outside_mohenjo_daro": dict(offsite),
        "attribute_comparison_joined": dis,
        "attribute_comparison_by_source": by_source,
        "objects_disagreeing_by_field": obj_dis,
        "mohenjo_daro_seals_disagreeing_by_field": obj_dis_seal,
        "joins_through_variant_registration": {k: v for k, v in reg_dis.items() if k.startswith("variant")},
        "tolerances": {"size_agree_in": SIZE_AGREE, "size_contradict_in": SIZE_CONTRADICT, "level_agree_ft": LEVEL_AGREE},
        "marshall_area_aliases": MARSHALL_ALIASES,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("dispositions", "join_basis", "joined_objects", "attribute_comparison_joined")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
