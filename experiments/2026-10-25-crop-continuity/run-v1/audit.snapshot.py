"""Audit published crop summaries without treating grains as independent trials.

Run from the repository root. Full source tables remain in the local raw directory.
Requires PyMuPDF for the author's accepted manuscript with its supplement.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import platform
import re

import fitz


STUDY = "CROP-CONTINUITY-2026-10-25"
PERCENT = re.compile(r"^(\d+(?:\.\d+)?)%+$")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def seasonal_block(text: str, label: str, width: int) -> list[Decimal]:
    tail = text.split(label, 1)[1]
    values = re.findall(r"(\d+(?:\.\d+)?)%+", tail)
    return [Decimal(x) for x in values[:width]]


def crop_rows(page: fitz.Page, top: float, centres: list[float], season_x: float):
    """Read numerical columns by coordinates, preserving blank cells as null."""
    groups: list[list[tuple]] = []
    for word in sorted(page.get_text("words"), key=lambda w: (w[1], w[0])):
        if word[1] < top:
            continue
        group = next((g for g in groups if abs(g[0][1] - word[1]) < 2), None)
        if group is None:
            groups.append([word])
        else:
            group.append(word)
    rows = []
    for group in sorted(groups, key=lambda g: g[0][1]):
        group.sort(key=lambda w: w[0])
        label = " ".join(w[4] for w in group if not PERCENT.fullmatch(w[4]) and w[0] < season_x)
        if label.startswith("Summer crops"):
            break
        if not any(PERCENT.fullmatch(w[4]) for w in group):
            continue
        cells = [None] * len(centres)
        for word in group:
            match = PERCENT.fullmatch(word[4])
            if match:
                column = min(range(len(centres)), key=lambda i: abs(word[0] - centres[i]))
                if cells[column] is not None:
                    raise ValueError(f"Two percentages in one cell: {label}")
                cells[column] = match.group(1)
        season = " ".join(w[4] for w in group if w[0] >= season_x)
        rows.append({"taxon_raw": label, "percent_of_crop_assemblage": cells, "season_raw": season,
                     "pdf_page": page.number + 1, "y_top": round(group[0][1], 2)})
    return rows


def total(rows: list[dict], column: int, labels: set[str]) -> Decimal:
    found = {r["taxon_raw"] for r in rows if r["taxon_raw"] in labels}
    if found != labels:
        raise ValueError(f"Required source rows missing: {labels - found}")
    # A blank proportion contributes no reported amount to this descriptive sum.
    # It remains null in the detailed extraction and is not an observed ecological absence.
    return sum((Decimal(r["percent_of_crop_assemblage"][column] or "0")
                for r in rows if r["taxon_raw"] in labels), Decimal(0))


def number(value: Decimal) -> float:
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite an existing result directory")
    args.out.mkdir(parents=True)
    source = args.raw / "petrie-bates-2017.pdf"
    doc = fitz.open(source)
    if len(doc) != 100:
        raise ValueError("Expected the 100-page accepted manuscript and supplement")

    cohorts = []
    table_specs = [
        (81, "S5", ["Dabli vas Chugta|Mature Harappan"], ""),
        (83, "S8", ["Burj|Early Harappan"], "Table S8."),
        (83, "S9", ["Burj|PGW"], "Table S9."),
        (85, "S12", ["Masudpur VII|Early Harappan", "Masudpur VII|Mature Harappan", "Masudpur VII|Late Harappan"], ""),
        (89, "S19", ["Masudpur I|Mature Harappan"], ""),
        (92, "S23", ["Bahola|Late Harappan", "Bahola|PGW"], ""),
    ]
    for page_number, table, names, marker in table_specs:
        text = doc[page_number - 1].get_text().replace("\u00a0", " ")
        if marker:
            text = text.split(marker, 1)[1]
        columns = {key: seasonal_block(text, label, len(names)) for key, label in (
            ("summer_pct", "Summer crops"), ("winter_pct", "Winter crops"),
            ("fruit_pct", "Tree/"), ("unknown_pct", "Unknown"))}
        for i, name in enumerate(names):
            site, phase = name.split("|")
            row = {"site": site, "phase": phase, "source_id": "PB2017", "table": table,
                   "pdf_page": page_number, **{k: number(v[i]) for k, v in columns.items()}}
            row["reported_category_sum_pct"] = number(sum((v[i] for v in columns.values()), Decimal(0)))
            row["closure_error_pp"] = number(sum((v[i] for v in columns.values()), Decimal(0)) - 100)
            cohorts.append(row)

    masudpur = crop_rows(doc[84], 171, [185, 267, 356], 410)
    bahola = crop_rows(doc[90], 424, [183, 268], 350)
    write_new(args.raw / "comparison-tables-extracted-v1.json", {"source_sha256": digest(source),
        "S12": masudpur, "S23_page91": bahola, "blank_rule": "null; no reported contribution when summing selected rows"})

    millet_labels = {"Echinochloa sp.", "Setaria sp.", "Panicum sp.", "SEB", "Indet. small millet"}
    cereal_labels = millet_labels | {"Hordeum vulgare", "Triticum sp.", "Hordeum/Triticum", "Oryza sp."}
    denominator_checks = []
    for site, rows, col, cited in (("Masudpur VII", masudpur, 2, 54), ("Bahola", bahola, 0, 71)):
        millet = total(rows, col, millet_labels)
        cereal = total(rows, col, cereal_labels)
        cereal_percent = millet * 100 / cereal
        denominator_checks.append({"site": site, "phase": "Late Harappan",
            "millet_pct_of_all_reported_crop_remains": number(millet),
            "cereal_pct_of_all_reported_crop_remains": number(cereal),
            "millet_pct_within_cereals": number(cereal_percent),
            "percent_quoted_in_Swaroop2026": cited,
            "nearest_integer_matches_cited": int(cereal_percent + Decimal("0.5")) == cited,
            "interpretation": "Reconstructed denominator from 2017 rounded table values; original 2026 supplementary denominator not inspected."})

    bahola_by_phase = {r["phase"]: r for r in cohorts if r["site"] == "Bahola"}
    early, late = bahola_by_phase["Late Harappan"], bahola_by_phase["PGW"]
    contrasts = {"Bahola_Late_Harappan_to_PGW": {
        "winter_change_pp": round(late["winter_pct"] - early["winter_pct"], 8),
        "summer_change_pp": round(late["summer_pct"] - early["summer_pct"], 8),
        "inference": "Descriptive phase-composition change; no sample-level uncertainty or causal attribution."}}

    dates = [("Hordeum vulgare", 2471, 2298), ("Vigna radiata", 1880, 1691), ("Oryza sativa", 1517, 1428)]
    chronology = []
    for taxon, older, younger in dates:
        row = {"taxon": taxon, "older_cal_BCE": older, "younger_cal_BCE": younger,
               "source_id": "SW2026", "locator": "PDF p. 7, Chronology of Jognakhera"}
        for boundary in (2200, 1900, 1200):
            row[f"relative_to_{boundary}_BCE"] = ("older" if younger > boundary else "younger" if older < boundary else "overlaps")
        chronology.append(row)

    summary = {
        "schema_version": "1.0", "study": STUDY, "status_class": "source-review", "verification_tier": "submitted",
        "created_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
        "source_hashes": {str(source): digest(source)}, "code_sha256": digest(Path(__file__)),
        "comparison_sites": len({x["site"] for x in cohorts}), "comparison_site_phases": len(cohorts),
        "comparison_source_lineage": "All nine phase summaries are one Land, Water and Settlement publication/data lineage.",
        "cohorts": cohorts, "denominator_checks": denominator_checks, "descriptive_contrasts": contrasts,
        "focal_sampling": {"samples_reported": 8, "trenches_reported": 1, "trench": "YA1/IV", "layers": [5, 12],
            "sieve_mm": 0.5, "reported_all_remains": 950, "reported_identified_subset": 867,
            "source_count_replication": "not computable: supplementary S1-S3 and Figure 5 numerical labels not acquired locally",
            "sample_volumes_litres": None, "layer_by_taxon_counts": None,
            "dating_note": "Three reported crop date ranges; lab IDs, dated-specimen counts and model specification remain uninspected."},
        "focal_reported_date_ranges": chronology,
        "chronology_check": {"date_ranges_wholly_after_1900_BCE": sum(x["relative_to_1900_BCE"] == "younger" for x in chronology),
            "date_ranges_reaching_1200_BCE_reference": sum(x["relative_to_1200_BCE"] != "older" for x in chronology),
            "youngest_reported_interval_precedes_1200_reference_by_years": 1428 - 1200,
            "inference": "Interval positions only. No new calibration, PGW phase assignment or probability model."},
        "focal_percentage_closure_only": {"cereals_plus_legumes_pct": 57.2 + 42.8,
            "winter_plus_summer_pct": 62.1 + 37.9, "count_based_replication": False},
        "reporting_audit": {"modern_crop_list_misread_as_ancient": ["maize", "sugarcane", "mustard", "sunflower"],
            "claim_source": "ThePrint article, Archaeobotany section", "correct_source": "SW2026 PDF p. 4, The study site and its environment",
            "video_spoken_claim_checked": False},
        "regional_inference": {"performed": False, "reason": "This pilot lacks harmonized deposit-level crop counts, independent date/context links and recovery metadata across sites."},
    }
    write_new(args.out / "summary.json", summary)
    write_new(args.out / "extraction.json", {"local_detailed_tables": "data/raw/2026-10-25-crop-continuity/comparison-tables-extracted-v1.json",
        "inspected_PDF_pages": [81, 83, 85, 88, 89, 91, 92], "raw_input_sha256": digest(source)})
    print(json.dumps({"output": str(args.out / "summary.json"), "sites": summary["comparison_sites"],
        "site_phases": len(cohorts), "denominator_checks": denominator_checks,
        "contrasts": contrasts, "chronology": summary["chronology_check"]}, indent=2))


if __name__ == "__main__":
    main()
