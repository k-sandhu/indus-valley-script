#!/usr/bin/env python3
"""Measure per-field metadata coverage of the local Indus corpus derivatives.

Reads local-only inputs (Lipi observed faces, the older website export, Mayig
faces and the Lipi image index) and writes aggregate counts only. No output
contains inscription text, sign sequences or record-level rows.

Usage (from the repository root):
    python -I experiments/2026-10-12-data-inventory/coverage.py --out experiments/2026-10-12-data-inventory/run-2026-10-12
The output directory must not exist.
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

INPUTS = {
    "lipi_faces": "data/normalized/lipi_observed_faces.jsonl",
    "website": "data/normalized/indus_website_observed.jsonl",
    "mayig": "data/normalized/mayig_faces.jsonl",
    "image_index": "data/lipi/src/assets/data/seal_id_and_image_mapping.json",
    "lipi_raw_csv": "data/lipi/src/assets/data/inscriptions.csv",
}
IMAGE_DIR = "data/lipi/public/seal_images"

# Hashes recorded in knowledge/provenance/SOURCES.md.
EXPECTED_SHA256 = {
    "lipi_faces": "1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db",
    "mayig": "033b8e40d4fdfa1f4a2c51390c8fd5f95eae35c6c835b47776c969ab947a19b7",
    "lipi_raw_csv": "c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c",
}

PLACEHOLDERS = {"", "-", "--", "- -", "?", "??", "unknown"}
DIM_FIELDS = ["horizontal(mm)", "vertical(mm)", "thickness(mm)"]
INCH_FIELDS = {"horizontal(mm)": "h", "vertical(mm)": "v", "thickness(mm)": "th"}

# Field -> group used in the target-record table.
FIELDS = [
    ("cisi", "identity"),
    ("excavation-idno", "identity"),
    ("region", "context"),
    ("site", "context"),
    ("area-section", "context"),
    ("block-house", "context"),
    ("room-grid", "context"),
    ("depth", "context"),
    ("time", "chronology"),
    ("period", "chronology"),
    ("phase", "chronology"),
    ("type", "physical"),
    ("material", "physical"),
    ("color", "physical"),
    ("shape", "physical"),
    ("cross-section", "physical"),
    ("boss", "physical"),
    ("preservation", "physical"),
    ("condition", "physical"),
    ("complete", "physical"),
    ("sides", "physical"),
    ("horizontal(mm)", "dimensions"),
    ("vertical(mm)", "dimensions"),
    ("thickness(mm)", "dimensions"),
    ("symbol", "iconography"),
    ("cult", "iconography"),
    ("dir.", "layout"),
]
DERIVED = [
    ("spatial_any", "context", "any of area-section, block-house, room-grid"),
    ("chronology_any", "chronology", "any of time, period, phase"),
    ("dimensions_any", "dimensions", "at least one positive millimetre dimension"),
    ("dimensions_all3", "dimensions", "all three millimetre dimensions positive"),
    ("image_local_lipi", "images", "raw CISI key in the Lipi image index with an existing file"),
    ("museum_older_export", "custody", "non-empty MUSEUM value for the same raw CISI key in the older website export"),
    ("calendar_date", "chronology", "no local field carries a calendar date or dated sample"),
]

TYPE_GROUPS = [
    ("SEAL", "seal"),
    ("TAB:B", "tablet, bas-relief"),
    ("TAB:I", "tablet, incised"),
    ("TAB:C", "tablet, copper"),
    ("TAG", "tag or sealing"),
    ("POT", "pottery"),
    ("POST", "pottery"),
]
MAIN_SITES = ["Harappa", "Mohenjo-daro", "Dholavira", "Kalibangan", "Lothal", "Chanhu-daro"]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(value) -> str:
    return re.sub(r"\s+", " ", str(value if value is not None else "")).strip()


def is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


RANGE = re.compile(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$")
SITE_ALIASES = {"chanhujo-daro": "chanhu-daro"}


def dim_max(text: str):
    """Positive number, or the maximum of a printed range such as '5 - 9'."""
    if is_number(text):
        return float(text)
    m = RANGE.match(text)
    if m:
        return max(float(m.group(1)), float(m.group(2)))
    return None


def usable(field: str, raw) -> bool:
    text = norm(raw)
    if text.lower() in PLACEHOLDERS:
        return False
    if field in DIM_FIELDS or field in ("h", "v", "th"):
        value = dim_max(text)
        return value is not None and value > 0
    return True


def type_group(raw: str) -> str:
    text = norm(raw).upper().replace("POST:", "POT:")
    for prefix, group in TYPE_GROUPS:
        if text.startswith(prefix):
            return group
    return "other"


def site_group(site: str) -> str:
    return site if site in MAIN_SITES else "other sites"


def pct(num: int, den: int):
    return round(100.0 * num / den, 2) if den else None


def load_jsonl(path: pathlib.Path):
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def image_sides(files):
    """Distinct side tokens parsed from file names such as KEY_A_50_.jpg."""
    sides = set()
    for name in files:
        stem = name.rsplit(".", 1)[0]
        parts = stem.split("_")
        if len(parts) > 1 and parts[1]:
            token = parts[1]
            if token in ("imp", "ma", "aa"):
                token = "_".join(parts[1:3])
            sides.add(token)
    return sides


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="new output directory")
    args = ap.parse_args()
    out = (ROOT / args.out).resolve() if not pathlib.Path(args.out).is_absolute() else pathlib.Path(args.out)
    if out.exists():
        sys.exit(f"refusing to overwrite existing output {out}")

    paths = {k: ROOT / v for k, v in INPUTS.items()}
    for k, p in paths.items():
        if not p.exists():
            sys.exit(f"missing local input {k}: {p}")
    input_hashes = {}
    for k, p in paths.items():
        digest = sha256(p)
        input_hashes[k] = {
            "path": INPUTS[k],
            "bytes": p.stat().st_size,
            "sha256": digest,
            "expected_sha256": EXPECTED_SHA256.get(k),
            "matches_recorded": (digest == EXPECTED_SHA256[k]) if k in EXPECTED_SHA256 else None,
        }

    faces = load_jsonl(paths["lipi_faces"])
    website = load_jsonl(paths["website"])
    mayig = load_jsonl(paths["mayig"])
    image_index = json.loads(paths["image_index"].read_text(encoding="utf-8"))
    image_dir = ROOT / IMAGE_DIR
    image_files = {p.name for p in image_dir.iterdir() if p.is_file()} if image_dir.exists() else set()

    # ---------------- images ----------------
    indexed_existing = {}
    for key, files in image_index.items():
        present = [f for f in files if f in image_files]
        if present:
            indexed_existing[key] = present
    indexed_names = {f for files in image_index.values() for f in files}
    unlabelled_vol = sum(1 for f in image_files if f.startswith("vol") or f.startswith("z_fix"))
    images_summary = {
        "image_files_in_directory": len(image_files),
        "index_keys": len(image_index),
        "index_file_references": sum(len(v) for v in image_index.values()),
        "index_keys_with_existing_file": len(indexed_existing),
        "files_not_in_index": len(image_files - indexed_names),
        "files_named_by_volume_page_without_catalogue_key": unlabelled_vol,
        "scope": "Lipi repository image crops named by CISI key and side; rights follow the CISI photographs and remain unresolved.",
    }

    # ---------------- museum values from older export ----------------
    museum_by_cisi = {}
    website_by_cisi = {}
    for r in website:
        key = norm(r.get("source_cisi"))
        if not key:
            continue
        website_by_cisi.setdefault(key, []).append(r)
        m = norm((r.get("metadata") or {}).get("MUSEUM"))
        if m and m.lower() not in PLACEHOLDERS:
            museum_by_cisi.setdefault(key, set()).add(m)

    # ---------------- face-level coverage ----------------
    field_names = [f for f, _ in FIELDS]
    placeholder_counts = {f: collections.Counter() for f in field_names + ["h", "v", "th"]}
    families = collections.OrderedDict()
    for r in faces:
        fam = r["object_family_id"]
        families.setdefault(fam, []).append(r)

    def face_values(r):
        md = r["metadata"]
        vals = {}
        for f in field_names:
            raw = md.get(f)
            ok = usable(f, raw)
            vals[f] = norm(raw) if ok else None
            if not ok:
                placeholder_counts[f][norm(raw)] += 1
        for f in ("h", "v", "th"):
            if not usable(f, md.get(f)):
                placeholder_counts[f][norm(md.get(f))] += 1
        vals["spatial_any"] = next((vals[f] for f in ("area-section", "block-house", "room-grid") if vals[f]), None)
        vals["chronology_any"] = next((vals[f] for f in ("time", "period", "phase") if vals[f]), None)
        dims = [vals[f] for f in DIM_FIELDS]
        vals["dimensions_any"] = "yes" if any(dims) else None
        vals["dimensions_all3"] = "yes" if all(dims) else None
        key = norm(md.get("cisi"))
        vals["image_local_lipi"] = "yes" if key in indexed_existing else None
        vals["museum_older_export"] = "; ".join(sorted(museum_by_cisi[key])) if key in museum_by_cisi else None
        vals["calendar_date"] = None
        return vals

    all_fields = field_names + [d for d, _, _ in DERIVED]
    face_vals = {r["record_id"]: face_values(r) for r in faces}

    def group_counts(records_by_group, unit):
        rows = []
        for group, recs in records_by_group.items():
            den = len(recs)
            for f in all_fields:
                present = sum(1 for v in recs if v.get(f))
                rows.append({"unit": unit, "group": group, "denominator": den, "field": f,
                             "usable": present, "percent": pct(present, den)})
        return rows

    # object-level values
    obj_vals = {}
    conflicts = collections.Counter()
    conflict_examples_by_field = collections.Counter()
    obj_type = {}
    obj_site = {}
    for fam, recs in families.items():
        merged = {}
        for f in all_fields:
            distinct = {face_vals[r["record_id"]][f].lower() for r in recs if face_vals[r["record_id"]][f]}
            merged[f] = "yes" if distinct else None
            if f in field_names and len(distinct) > 1:
                conflicts[f] += 1
        obj_vals[fam] = merged
        groups = {type_group(r["metadata"].get("type")) for r in recs}
        obj_type[fam] = groups.pop() if len(groups) == 1 else "mixed"
        sites = {norm(r["metadata"].get("site")) for r in recs}
        obj_site[fam] = sites.pop() if len(sites) == 1 else "mixed"

    face_by_type = collections.defaultdict(list)
    face_by_site = collections.defaultdict(list)
    face_by_site_full = collections.defaultdict(list)
    for r in faces:
        v = face_vals[r["record_id"]]
        face_by_type[type_group(r["metadata"].get("type"))].append(v)
        s = norm(r["metadata"].get("site"))
        face_by_site[site_group(s)].append(v)
        face_by_site_full[s].append(v)
    obj_by_type = collections.defaultdict(list)
    obj_by_site = collections.defaultdict(list)
    obj_by_site_full = collections.defaultdict(list)
    for fam, v in obj_vals.items():
        obj_by_type[obj_type[fam]].append(v)
        obj_by_site[site_group(obj_site[fam])].append(v)
        obj_by_site_full[obj_site[fam]].append(v)

    overall = group_counts({"all": list(face_vals.values())}, "face") + group_counts({"all": list(obj_vals.values())}, "object")
    by_type = group_counts(dict(sorted(face_by_type.items())), "face") + group_counts(dict(sorted(obj_by_type.items())), "object")
    by_site = group_counts(dict(sorted(face_by_site.items())), "face") + group_counts(dict(sorted(obj_by_site.items())), "object")
    by_site_full = group_counts(dict(sorted(face_by_site_full.items())), "face") + group_counts(dict(sorted(obj_by_site_full.items())), "object")

    # ---------------- per-object side imaging (approximate) ----------------
    sides_ok = 0
    sides_known = 0
    for fam, recs in families.items():
        md = recs[0]["metadata"]
        key = norm(md.get("cisi"))
        try:
            n_sides = int(norm(md.get("sides")))
        except ValueError:
            continue
        sides_known += 1
        if key in indexed_existing and len(image_sides(indexed_existing[key])) >= n_sides:
            sides_ok += 1
    images_summary["objects_with_side_count"] = sides_known
    images_summary["objects_with_image_side_tokens_at_least_side_count"] = sides_ok
    images_summary["side_count_rule"] = "Distinct side tokens parsed from indexed file names compared with the export's sides field; approximate, ignores whether a side is inscribed."

    # ---------------- dimension unit check ----------------
    unit_check = collections.Counter()
    for r in faces:
        md = r["metadata"]
        for mm_field, in_field in INCH_FIELDS.items():
            mm = norm(md.get(mm_field))
            inch = norm(md.get(in_field))
            if is_number(mm) and is_number(inch) and float(mm) > 0 and float(inch) > 0:
                diff = abs(float(mm) - 25.4 * float(inch))
                unit_check["both_present"] += 1
                unit_check["mm_equals_inch_x_25.4_within_0.6mm" if diff <= 0.6 else "mm_differs_from_inch_conversion"] += 1
            elif usable(mm_field, mm):
                unit_check["mm_only"] += 1
            elif usable(in_field, inch):
                unit_check["inch_only"] += 1

    # ---------------- placeholder table ----------------
    placeholder_rows = []
    for f, counter in placeholder_counts.items():
        for token, n in counter.most_common():
            placeholder_rows.append({"field": f, "placeholder_or_empty": token if token else "(empty)", "faces": n})

    # flagged values
    hyphen_led_idno = sum(1 for r in faces if norm(r["metadata"].get("excavation-idno")).startswith("-") and usable("excavation-idno", r["metadata"].get("excavation-idno")))
    surface_depth = sum(1 for r in faces if norm(r["metadata"].get("depth")).lower().startswith("surface"))
    numeric_all3_faces = sum(1 for r in faces if all(is_number(norm(r["metadata"].get(f))) and float(norm(r["metadata"].get(f))) > 0 for f in DIM_FIELDS))
    numeric_any_faces = sum(1 for r in faces if any(is_number(norm(r["metadata"].get(f))) and float(norm(r["metadata"].get(f))) > 0 for f in DIM_FIELDS))
    range_dims = {f: sum(1 for r in faces if RANGE.match(norm(r["metadata"].get(f)))) for f in DIM_FIELDS}
    none_symbol = sum(1 for r in faces if norm(r["metadata"].get("symbol")) == "None")
    none_cult = sum(1 for r in faces if norm(r["metadata"].get("cult")) == "None")
    depth_units = collections.Counter()
    for r in faces:
        d = norm(r["metadata"].get("depth"))
        if usable("depth", d):
            depth_units["ft" if re.search(r"\bft\b", d) else "m" if re.search(r"\bm\b", d) else "other"] += 1

    # ---------------- cross-source checks ----------------
    lipi_by_cisi = collections.defaultdict(list)
    for r in faces:
        key = norm(r["metadata"].get("cisi"))
        if usable("cisi", key):
            lipi_by_cisi[key].append(r)

    site_cmp = collections.Counter()
    material_cmp = collections.Counter()
    dim_cmp = collections.Counter()
    website_keys = [k for k in website_by_cisi if k]
    for key in website_keys:
        if key not in lipi_by_cisi:
            site_cmp["website_key_absent_from_lipi"] += 1
            continue
        w = website_by_cisi[key][0]
        lrecs = lipi_by_cisi[key]
        lsites = {norm(r["metadata"].get("site")).lower() for r in lrecs}
        wsite = norm(w.get("site")).lower()
        site_cmp["agree" if wsite in lsites else "differ_raw_spelling"] += 1
        if wsite not in lsites:
            alias = SITE_ALIASES.get(wsite, wsite)
            site_cmp["agree_after_recorded_alias" if alias in lsites else "differ_after_alias"] += 1
        lmats = {norm(r["metadata"].get("material")).lower() for r in lrecs if usable("material", r["metadata"].get("material"))}
        wmat = norm(w.get("material")).lower()
        if not lmats or wmat in PLACEHOLDERS or wmat == "none":
            material_cmp["one_side_missing"] += 1
        else:
            material_cmp["agree" if wmat in lmats else "differ"] += 1
        wmd = w.get("metadata") or {}
        wdims = [norm(wmd.get(k)) for k in ("WIDTH", "HEIGHT", "THICKNESS")]
        ldims = [norm(lrecs[0]["metadata"].get(k)) for k in DIM_FIELDS]
        def plain(xs):
            return sorted(float(x) for x in xs if is_number(x) and float(x) > 0)
        wset, lset = plain(wdims), plain(ldims)
        if not wset or not lset:
            dim_cmp["one_side_missing"] += 1
        else:
            if len(wset) == len(lset) and all(abs(a - b) <= 0.6 for a, b in zip(wset, lset)):
                dim_cmp["agree_same_values_mm"] += 1
            elif len(wset) == len(lset) and all(abs(a * 25.4 - b) <= 0.6 for a, b in zip(wset, lset)):
                dim_cmp["agree_after_inch_conversion"] += 1
            else:
                dim_cmp["differ"] += 1

    mayig_cmp = collections.Counter()
    for m in mayig:
        fam = norm(m.get("object_family_id"))
        if fam in lipi_by_cisi:
            lsites = {norm(r["metadata"].get("site")).lower() for r in lipi_by_cisi[fam]}
            mayig_cmp["site_agree" if norm(m.get("site")).lower() in lsites else "site_differ"] += 1
        else:
            mayig_cmp["mayig_key_absent_from_lipi"] += 1

    cross_source = {
        "lipi_vs_older_website_export": {
            "website_records_with_cisi_key": sum(len(v) for v in website_by_cisi.values()),
            "distinct_website_cisi_keys": len(website_keys),
            "site": dict(site_cmp),
            "material": dict(material_cmp),
            "dimensions": dict(dim_cmp),
            "site_alias_rule": "Raw lower-case comparison, then the recorded spelling alias Chanhujo-daro = Chanhu-daro.",
            "dimension_rule": "Compare sorted positive plain numbers; agreement within 0.6 mm either directly or after multiplying the older export's values by 25.4.",
            "older_export_museum_values": {
                "records_with_museum_value": sum(1 for r in website if norm((r.get("metadata") or {}).get("MUSEUM")) and norm((r.get("metadata") or {}).get("MUSEUM")).lower() not in PLACEHOLDERS),
                "records": len(website),
            },
        },
        "lipi_vs_mayig": {"mayig_faces": len(mayig), **dict(mayig_cmp)},
        "lipi_inch_vs_mm_fields": dict(unit_check),
        "scope": "Internal consistency among derivatives that share upstream sources; agreement does not verify a value against the object.",
    }

    conflicts_out = {
        "rule": "An object conflicts on a field when its faces carry two or more distinct usable values after case and whitespace normalization.",
        "objects": len(families),
        "multi_face_objects": sum(1 for recs in families.values() if len(recs) > 1),
        "objects_with_conflict_by_field": {f: conflicts.get(f, 0) for f in field_names},
        "objects_with_mixed_type_group": sum(1 for v in obj_type.values() if v == "mixed"),
        "objects_with_mixed_site": sum(1 for v in obj_site.values() if v == "mixed"),
    }

    def get(rows, unit, group, field):
        for row in rows:
            if row["unit"] == unit and row["group"] == group and row["field"] == field:
                return row
        return None

    summary = {
        "date": "2026-10-12",
        "status": "Verified computation on pinned local derivatives; Exploratory inventory",
        "faces": len(faces),
        "objects": len(families),
        "multi_face_objects": conflicts_out["multi_face_objects"],
        "object_type_counts": {k: len(v) for k, v in sorted(obj_by_type.items())},
        "face_type_counts": {k: len(v) for k, v in sorted(face_by_type.items())},
        "object_site_counts_main": {k: len(v) for k, v in sorted(obj_by_site.items())},
        "sites": len(obj_by_site_full),
        "headline_object_coverage_percent": {f: get(overall, "object", "all", f)["percent"] for f in all_fields},
        "headline_face_coverage_percent": {f: get(overall, "face", "all", f)["percent"] for f in all_fields},
        "headline_object_coverage_count": {f: get(overall, "object", "all", f)["usable"] for f in all_fields},
        "flags": {
            "excavation_idno_hyphen_led_usable_strings": hyphen_led_idno,
            "depth_surface_finds": surface_depth,
            "depth_unit_counts_usable": dict(depth_units),
            "dimension_range_strings_counted_usable": range_dims,
            "faces_with_all_three_dimensions_plain_numbers_only": numeric_all3_faces,
            "faces_with_any_dimension_plain_numbers_only": numeric_any_faces,
            "symbol_asserted_none_faces": none_symbol,
            "cult_asserted_none_faces": none_cult,
        },
        "images": images_summary,
        "derived_field_definitions": {d: desc for d, _, desc in DERIVED},
        "field_groups": {f: g for f, g in FIELDS} | {d: g for d, g, _ in DERIVED},
        "placeholder_tokens": sorted(PLACEHOLDERS) + ["0 and non-positive numbers in dimension fields"],
    }

    compact_fields = ["cisi", "excavation-idno", "spatial_any", "depth", "chronology_any", "material",
                      "shape", "dimensions_any", "dimensions_all3", "symbol", "image_local_lipi", "museum_older_export"]
    compact = []
    for label, rows_src, unit, group in (
        [("all objects", overall, "object", "all")]
        + [(g, by_type, "object", g) for g in sorted(obj_by_type)]
        + [(g, by_site, "object", g) for g in MAIN_SITES + ["other sites"] if g in obj_by_site]
    ):
        row = {"group": label, "objects": get(rows_src, unit, group, "cisi")["denominator"]}
        for f in compact_fields:
            row[f] = get(rows_src, unit, group, f)["percent"]
        compact.append(row)

    out.mkdir(parents=True)

    def write_csv(name, rows, fields):
        with (out / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    cols = ["unit", "group", "denominator", "field", "usable", "percent"]
    write_csv("field-coverage-overall.csv", overall, cols)
    write_csv("field-coverage-by-type.csv", by_type, cols)
    write_csv("field-coverage-by-site.csv", by_site, cols)
    write_csv("field-coverage-by-site-all.csv", by_site_full, cols)
    write_csv("compact-object-table.csv", compact, ["group", "objects"] + compact_fields)
    write_csv("placeholders.csv", placeholder_rows, ["field", "placeholder_or_empty", "faces"])
    (out / "conflicts.json").write_text(json.dumps(conflicts_out, indent=2), encoding="utf-8")
    (out / "cross-source.json").write_text(json.dumps(cross_source, indent=2), encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "input-hashes.json").write_text(json.dumps(input_hashes, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out.relative_to(ROOT)), "faces": len(faces), "objects": len(families),
                      "inputs_match_recorded": {k: v["matches_recorded"] for k, v in input_hashes.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
