"""Validate the join decisions and write the join table, the Q-1019 table and the coverage summary.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/build_joins.py
Inputs (local-only): data/normalized/lipi_observed_faces.jsonl, the Lipi image index, the older
website export, this package's raw harvests and the census's saved records. Outputs (tracked):
joins/join-table.csv, joins/q1019-decisions.csv, coverage/summary.json. The tracked tables hold
identifiers, our classes, locators and field-presence flags; values from records under
restrictive terms are not copied.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG / "joins"))
from candidates import search  # noqa: E402
from decisions import D  # noqa: E402
from lipi_index import load, norm, usable  # noqa: E402

ROOT = PKG.parents[1]
RAW = ROOT / "data/raw/2026-10-13-museum-open-access"
CENSUS = ROOT / "data/raw/2026-10-06-evidence-census"
FOCUSED = CENSUS / "collections-and-datasets/focused-pass-2026-10-07/focused-records.json"
CONFIRMED = CENSUS / "synthesis/main-2026-10-07-v6/confirmed-object-joins.json"
UNRESOLVED = CENSUS / "synthesis/main-2026-10-07-v6/candidate-object-joins.json"
WEBSITE = ROOT / "data/normalized/indus_website_observed.jsonl"

LICENCE = {
    "Metropolitan Museum of Art": ("CC0", "CC0"),
    "Cleveland Museum of Art": ("CC0", "CC0"),
    "Penn Museum": ("CC BY 4.0", "non-commercial (Penn image terms)"),
    "Victoria and Albert Museum": ("V&A API terms, non-commercial, 4-week storage limit", "V&A terms, non-commercial"),
    "British Museum": ("not open (BM terms)", "CC BY-NC-SA 4.0 only where marked"),
    "National Museum, New Delhi": ("rights reserved (Museums of India portal)", "rights reserved"),
    "Indian Museum, Kolkata": ("rights reserved (Museums of India portal)", "rights reserved"),
    "Louvre": ("Licence Ouverte / Etalab 2.0 (record text)", "restricted (Louvre CGU art. 4.1.1.2)"),
}
OPEN_IMAGE = {"Metropolitan Museum of Art", "Cleveland Museum of Art"}
FINER = re.compile(r"\b(block|house|room|trench|locus|level|street|lane|mound|site no|area|grid|sq\.?|depth)\b", re.I)


def museum_values():
    """(institution, accession) -> dict with dims, findspot, image flag; from local raw files."""
    out = {}
    for r in json.loads(FOCUSED.read_text(encoding="utf-8")):
        out[(r["institution"], r["accession"])] = {"dims": r.get("dimensions") or "", "findspot": r.get("site") or "",
                                                    "images": bool(r.get("image_slots")), "desc": r.get("description") or ""}
    for museum, name in (("met", "Metropolitan Museum of Art"), ("cleveland", "Cleveland Museum of Art"),
                         ("penn", "Penn Museum"), ("vam", "Victoria and Albert Museum")):
        p = RAW / museum / "records-extracted.json"
        if not p.exists():
            continue
        for r in json.loads(p.read_text(encoding="utf-8")):
            if not r.get("accession"):
                continue
            prev = out.get((name, r["accession"]), {})
            out[(name, r["accession"])] = {
                "dims": r.get("dimensions_raw") or prev.get("dims") or "",
                "findspot": r.get("findspot_raw") or prev.get("findspot") or "",
                "images": bool(r.get("image_urls")) or prev.get("images", False),
                "desc": r.get("description") or "",
                "open_image_urls": len(r.get("image_urls") or []) if name in OPEN_IMAGE and r.get("is_public_domain") else 0,
            }
    bm = RAW / "bm" / "records-extracted.json"
    if bm.exists():
        for r in json.loads(bm.read_text(encoding="utf-8")):
            out.setdefault(("British Museum", r["accession"]), {"dims": "", "findspot": r.get("findspot_label") or "",
                                                                 "images": False, "desc": ""})
    return out


def n_dims(s):
    """Number of measured axes in a museum dimension string (a fraction such as 1 1/16 counts once)."""
    s = str(s or "")
    paren = re.findall(r"\(([^()]*\d[^()]*(?:cm|mm)[^()]*)\)", s)
    if paren:
        s = paren[0]
    s = re.sub(r"\(Of the (seal|impression)\)", "", s, flags=re.I)
    vals = re.findall(r"\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?", s)
    return min(len(vals), 3)


def main():
    fams = load()
    website = {}
    with open(WEBSITE, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r["metadata"].get("MUSEUM"):
                website[norm(r["source_cisi"])] = r["metadata"]["MUSEUM"]
    census_conf = {x["key"]: x["family"] for x in json.loads(CONFIRMED.read_text(encoding="utf-8"))}
    census_open = {f'{x["institution"]}|{x["accession"]}': x["query_disposition"]
                   for x in json.loads(UNRESOLVED.read_text(encoding="utf-8"))}
    census_fams = set(census_conf.values())
    values = museum_values()
    rows, problems = [], []
    for d in D:
        key = f'{d["museum"]}|{d["accession"]}'
        row = dict(d)
        fam = fams.get(d["family"]) if d["family"] else None
        if d["family"] and not fam:
            problems.append(f"{key}: family {d['family']} not found")
        if fam and d["cisi"] and d["cisi"] not in fam["cisi"]:
            problems.append(f"{key}: CISI {d['cisi']} not on family {d['family']}")
        if d["cisi"] and not fam:
            hit = [f["family"] for f in fams.values() if d["cisi"] in f["cisi"]]
            row["cisi_in_local_corpus"] = bool(hit)
        if d["spec"]:
            site, typ, motif, w, h, s, tol, stol = d["spec"].split("|")
            res = search(site, typ, motif, float(w), float(h), int(s), float(tol), int(stol), fams=fams)
            row["candidate_count"] = len(res)
            row["candidates_spec"] = ";".join(r["family"] for r in res[:25]) + (";..." if len(res) > 25 else "")
        else:
            row["candidate_count"] = len([c for c in d["cands"].split(";") if c]) if d["cands"] else ""
            row["candidates_spec"] = ""
        row["q1019"] = key in census_open
        row["census_disposition"] = census_open.get(key, "confirmed" if key in census_conf else "not in census")
        if key in census_conf and census_conf[key] != d["family"]:
            problems.append(f"{key}: census family {census_conf[key]} differs from {d['family']}")
        row["data_licence"], row["image_licence"] = LICENCE.get(d["museum"], ("", ""))
        v = values.get((d["museum"], d["accession"]), {})
        row["museum_dims_values"] = n_dims(v.get("dims"))
        row["museum_findspot_finer"] = bool(FINER.search(v.get("findspot", "")))
        row["museum_open_image_urls"] = v.get("open_image_urls", 0)
        joined = d["cls"] in ("exact", "confirmed")
        row["joined"] = joined
        row["new_join"] = joined and key not in census_conf
        if fam:
            dims = [usable(fam.get(k)) for k in ("h_mm", "v_mm", "t_mm")]
            row["lipi_dims_any"], row["lipi_dims_all"] = any(dims), all(dims)
            row["lipi_spatial_unit"] = any(usable(fam.get(k)) for k in ("area-section", "block-house", "room-grid"))
            row["lipi_museum_value"] = any(website.get(c) for c in fam["cisi_norm"])
            row["lipi_local_image"] = bool(fam["images"])
            row["family_in_census_joins"] = d["family"] in census_fams
        if joined and fam:
            row["gain_accession"] = not row["lipi_museum_value"] and not row["family_in_census_joins"]
            lipi_axes = sum(dims)
            row["lipi_dims_axes"] = lipi_axes
            row["gain_dims_any"] = lipi_axes == 0 and row["museum_dims_values"] >= 1
            row["gain_dims_more_axes"] = row["museum_dims_values"] > lipi_axes
            row["gain_open_image"] = row["museum_open_image_urls"] > 0
            row["gain_findspot"] = (not row["lipi_spatial_unit"]) and row["museum_findspot_finer"]
        rows.append(row)
    if problems:
        print("VALIDATION PROBLEMS:\n  " + "\n  ".join(problems))
    cols = ["museum", "accession", "source", "q1019", "census_disposition", "cls", "method", "family", "cisi", "joined",
            "new_join", "candidate_count", "cands", "candidates_spec", "spec", "addition", "evidence", "conflicts",
            "data_licence", "image_licence", "museum_dims_values", "museum_findspot_finer", "museum_open_image_urls",
            "lipi_dims_any", "lipi_dims_all", "lipi_spatial_unit", "lipi_museum_value", "lipi_local_image",
            "family_in_census_joins", "gain_accession", "gain_dims_any", "gain_open_image",
            "gain_findspot", "cisi_in_local_corpus", "lipi_dims_axes", "gain_dims_more_axes"]
    (PKG / "joins").mkdir(exist_ok=True)
    with open(PKG / "joins" / "join-table.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    q = [r for r in rows if r["q1019"]]
    with open(PKG / "joins" / "q1019-decisions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["museum", "accession", "census_disposition", "cls", "method", "family", "cisi",
                                           "candidate_count", "cands", "addition", "evidence", "conflicts"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(q)
    missing_q = sorted(set(census_open) - {f'{r["museum"]}|{r["accession"]}' for r in rows})

    def tally(rs):
        return dict(Counter(r["cls"] for r in rs))

    joined = [r for r in rows if r["joined"]]
    new = [r for r in joined if r["new_join"]]
    new_fams = {r["family"] for r in new}
    summary = {
        "package": "experiments/2026-10-13-museum-open-access",
        "records_decided": len(rows),
        "classes_all": tally(rows),
        "by_museum": {m: tally([r for r in rows if r["museum"] == m]) for m in sorted({r["museum"] for r in rows})},
        "q1019": {"records": len(q), "census_records_not_decided": missing_q, "classes": tally(q),
                  "by_census_disposition": {k: tally([r for r in q if r["census_disposition"] == k])
                                            for k in sorted({r["census_disposition"] for r in q})},
                  "new_confirmed_or_exact": sum(r["joined"] for r in q),
                  "candidate_additions": sum(bool(r["addition"]) for r in q)},
        "joins": {"exact_or_confirmed_records": len(joined), "new_vs_census": len(new),
                  "reproduced_census_joins": len(joined) - len(new),
                  "new_families": len(new_fams),
                  "census_lower_bound_before": 68,
                  "census_lower_bound_after": 68 + sum(r["joined"] for r in q),
                  "new_joins_outside_census_records": len([r for r in new if not r["q1019"]])},
        "coverage_gains_new_joins": {
            "families_gaining_museum_accession": len({r["family"] for r in new if r.get("gain_accession")}),
            "families_gaining_any_dimension": len({r["family"] for r in new if r.get("gain_dims_any")}),
            "families_where_museum_gives_more_axes_than_lipi": len({r["family"] for r in new if r.get("gain_dims_more_axes")}),
            "families_gaining_open_licence_image_url": len({r["family"] for r in new if r.get("gain_open_image")}),
            "families_gaining_finer_findspot": len({r["family"] for r in new if r.get("gain_findspot")}),
        },
        "candidate_additions": [f'{r["museum"]}|{r["accession"]}' for r in rows if r["addition"]],
        "ambiguous_single_candidate": [f'{r["museum"]}|{r["accession"]}' for r in rows
                                       if r["cls"] == "ambiguous" and str(r["candidate_count"]) == "1"
                                       or (r["cls"] == "ambiguous" and r["cands"] and len(r["cands"].split(";")) == 1)],
        "validation_problems": problems,
    }
    (PKG / "coverage").mkdir(exist_ok=True)
    (PKG / "coverage" / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
