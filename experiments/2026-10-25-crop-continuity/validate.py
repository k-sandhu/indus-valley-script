"""Check the audit with pdfplumber and exact rational arithmetic.

This is a second extraction/calculation route by the same contributor.
It does not constitute independent scholarly reproduction.
"""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re

import pdfplumber


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = json.loads(args.summary.read_text(encoding="utf-8"))
    checks = []

    def check(name, condition, detail=None):
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    pdf_path = args.raw / "petrie-bates-2017.pdf"
    check("source_hash", hashlib.sha256(pdf_path.read_bytes()).hexdigest() in result["source_hashes"].values())
    check("author_code_hash", hashlib.sha256(Path(__file__).with_name("audit.py").read_bytes()).hexdigest() == result["code_sha256"])
    with pdfplumber.open(pdf_path) as pdf:
        # Independent layout-aware extractor: summary rows become complete text lines.
        page_text = {p: pdf.pages[p - 1].extract_text() for p in (81, 83, 85, 89, 92)}
        for row in result["cohorts"]:
            occurrence = 1 if row["site"] == "Burj" and row["phase"] == "PGW" else 0
            column = ({"Early Harappan": 0, "Mature Harappan": 1, "Late Harappan": 2}[row["phase"]]
                      if row["site"] == "Masudpur VII" else 1 if row["site"] == "Bahola" and row["phase"] == "PGW" else 0)
            for field, label in (("summer_pct", "Summer crops"), ("winter_pct", "Winter crops"),
                                 ("fruit_pct", "Tree/Orchard"), ("unknown_pct", "Unknown")):
                lines = re.findall(r"^\s*" + re.escape(label) + r"\s+(.+)$", page_text[row["pdf_page"]], re.I | re.M)
                values = re.findall(r"(\d+(?:\.\d+)?)%+", lines[occurrence])
                observed = Fraction(values[column])
                check(f"pdfplumber:{row['site']}:{row['phase']}:{field}", abs(float(observed) - row[field]) < 1e-10)

        def cell(page_number, label, column_x):
            page = pdf.pages[page_number - 1]
            matches = page.search(re.escape(label), regex=True)
            if len(matches) != 1:
                raise ValueError(f"Ambiguous source label {label}: {len(matches)} matches")
            loc = matches[0]
            text = page.crop((column_x - 1, loc["top"] - 1, column_x + 54, loc["bottom"] + 1)).extract_text() or ""
            values = re.findall(r"(\d+(?:\.\d+)?)%+", text)
            if len(values) > 1:
                raise ValueError(f"Ambiguous numeric cell: {text}")
            return Fraction(values[0]) if values else Fraction(0)

        millet = ["Echinochloa sp.", "Setaria sp.", "Panicum sp.", "SEB", "Indet. small millet"]
        cereals = millet + ["Hordeum vulgare", "Triticum sp.", "Hordeum/Triticum", "Oryza sp."]
        for record in result["denominator_checks"]:
            page, x = (85, 356) if record["site"] == "Masudpur VII" else (91, 183)
            numerator = sum((cell(page, label, x) for label in millet), Fraction())
            denominator = sum((cell(page, label, x) for label in cereals), Fraction())
            check(f"millet_sum:{record['site']}", abs(float(numerator) - record["millet_pct_of_all_reported_crop_remains"]) < 1e-10)
            check(f"cereal_sum:{record['site']}", abs(float(denominator) - record["cereal_pct_of_all_reported_crop_remains"]) < 1e-10)
            check(f"denominator_conversion:{record['site']}", abs(float(100 * numerator / denominator) - record["millet_pct_within_cereals"]) < 1e-10)

    contrast = result["descriptive_contrasts"]["Bahola_Late_Harappan_to_PGW"]
    check("Bahola_winter_difference_exact", float(Fraction("17.29") - Fraction("6.87")) == contrast["winter_change_pp"])
    check("Bahola_summer_difference_exact", float(Fraction("72.88") - Fraction("88.24")) == contrast["summer_change_pp"])
    check("nine_site_phase_rows", len(result["cohorts"]) == 9)
    check("five_distinct_sites", len({r["site"] for r in result["cohorts"]}) == 5)
    check("all_reported_crop_ranges_predate_1200_reference", all(r["younger_cal_BCE"] > 1200 for r in result["focal_reported_date_ranges"]))
    check("two_reported_crop_ranges_postdate_1900_reference", sum(r["older_cal_BCE"] < 1900 for r in result["focal_reported_date_ranges"]) == 2)
    check("no_regional_significance_claim", result["regional_inference"]["performed"] is False)
    check("focal_count_replication_left_uncomputed", result["focal_percentage_closure_only"]["count_based_replication"] is False)
    payload = {"method": "pdfplumber source-cell reread and Fraction arithmetic by the same contributor",
               "summary_sha256": hashlib.sha256(args.summary.read_bytes()).hexdigest(),
               "checks": checks, "passed": sum(c["passed"] for c in checks),
               "failed": sum(not c["passed"] for c in checks), "verification_tier": "submitted"}
    with args.out.open("x", encoding="utf-8") as out:
        json.dump(payload, out, indent=2)
        out.write("\n")
    print(json.dumps({"passed": payload["passed"], "failed": payload["failed"], "output": str(args.out)}))
    raise SystemExit(bool(payload["failed"]))


if __name__ == "__main__":
    main()
