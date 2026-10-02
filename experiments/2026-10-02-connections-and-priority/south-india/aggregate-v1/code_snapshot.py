"""Check aggregate catalogue joins without redistributing specimen data."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).parent
RAW = ROOT / "data/raw/2026-10-02-connections-and-priority/south-india/portal-v1"


def read(name):
    return json.loads((RAW / name).read_text(encoding="utf-8"))


def margin(row, key):
    return sum(x["value"] for x in row["records"].get(key, []))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    dest = HERE / args.run
    dest.mkdir(exist_ok=False)
    families = [read(f"sign-{i}.json")["data"] for i in range(1, 43)]
    rows = [(kind, row) for f in families for kind, values in
            [("Base", [f["base"]]), ("Variant", f["variants"]), ("Composite", f["composites"])]
            for row in values]
    types = Counter(kind for kind, _ in rows)
    occurrences = Counter()
    discrepancies = []
    for kind, row in rows:
        n = margin(row, "site")
        occurrences[kind] += n
        for field in ["hab", "material", "depth"]:
            if margin(row, field) != n:
                discrepancies.append({"sign": row["sign"], "field": field,
                                      "site_sum": n, "field_sum": margin(row, field)})
    sites = read("sites.json")["data"]
    site_type = Counter()
    site_rows = Counter()
    for site in sites:
        for row in site["records"]["sign"]:
            site_type[row["type"]] += row["value"]
            site_rows[(str(row["key"]), site["site"])] += row["value"]
    family_rows = Counter()
    for _, row in rows:
        for r in row["records"].get("site", []):
            family_rows[(str(row["sign"]), r["key"])] += r["value"]
    unmatched = [{"sign": key[0], "site": key[1],
                  "sites_route": site_rows[key], "family_route": family_rows[key]}
                 for key in sorted(site_rows.keys() | family_rows.keys())
                 if site_rows[key] != family_rows[key]]
    # Counts describe visible repeated lines under the authors' graphic classes.
    # They supply no archaeological value or unit for any mark.
    counts = {"39": (1, "vertical"), "39.1": (1, "horizontal"),
              "39.2": (2, "vertical"), "39.3": (2, "horizontal"),
              "39.4": (3, "vertical"), "39.5": (3, "horizontal"),
              "39.6": (4, "vertical"), "39.7": (4, "horizontal"),
              "39.8": (5, "vertical"), "39.9": (6, "vertical"),
              "39.10": (6, "horizontal"), "39.11": (7, "vertical"),
              "39.12": (8, "vertical"), "39.13": (9, "vertical"),
              "39.14": (9, "tilted-horizontal"), "39.15": (16, "vertical")}
    stroke_rows = [(row, counts[row["sign"]]) for kind, row in rows
                   if kind != "Composite" and row["sign"] in counts]
    stroke_frequency = Counter()
    orientation = Counter()
    for row, (count, axis) in stroke_rows:
        n = margin(row, "site")
        stroke_frequency[count] += n
        orientation[axis] += n
    result = {
        "input_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(RAW.glob("*.json"))},
        "question": "Which public data connections and numeric observation fields are available?",
        "family_count": len(families), "catalogue_form_counts": dict(types),
        "family_route_occurrences": dict(occurrences),
        "family_route_occurrence_total": sum(occurrences.values()),
        "site_route_sites": len(sites),
        "site_route_occurrence_total": sum(s["occurence"] for s in sites),
        "site_route_type_totals": dict(site_type),
        "within_form_margin_discrepancies": discrepancies,
        "cross_route_cells_differing": unmatched,
        "api_family_totals_all_sum": sum(f["totals"]["all"] for f in families),
        "api_family_totals_definition_check": {
            "base_equals_occurrences_in_all_families": all(
                f["totals"]["base"] == margin(f["base"], "site") for f in families),
            "variants_equals_number_of_forms_in_all_families": all(
                f["totals"]["variants"] == len(f["variants"]) for f in families),
            "composites_equals_number_of_forms_in_all_families": all(
                f["totals"]["composites"] == len(f["composites"]) for f in families),
        },
        "stroke_family": {
            "description_source": "Rajan and Sivanantham 2026 volI printed387–388, PDF426–427",
            "photograph_source": "volI Plate5.136, printed684, PDF723",
            "plain_stroke_form_count": len(stroke_rows),
            "plain_stroke_occurrences": sum(stroke_frequency.values()),
            "stroke_count_frequency": dict(sorted(stroke_frequency.items())),
            "orientation_frequency": dict(orientation),
            "family_base_and_variants_occurrences": sum(margin(r, "site") for k, r in rows
                if k != "Composite" and (r["sign"] == "39" or r["sign"].startswith("39."))),
        },
        "observed_schema": {
            "family_rows": "sign key with separate site, habitation, ware and depth margins",
            "specimen_registration_in_family_records": False,
            "capacity_or_measured_mass_in_family_records": False,
            "measured_contents_count_in_family_records": False,
            "calendar_age_or_dating_sample_key_in_family_records": False,
            "indus_route": "authors' visual-parallel table; separate sign namespace",
        },
        "scope": "Frozen deployed portal snapshot, not the full printed excavation inventory",
    }
    (dest / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (dest / "code_snapshot.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k: result[k] for k in ["catalogue_form_counts", "family_route_occurrences",
          "family_route_occurrence_total", "site_route_sites", "site_route_occurrence_total",
          "api_family_totals_definition_check", "stroke_family"]}))
    print("Margin discrepancies", len(discrepancies), "cross-route cells", len(unmatched))


if __name__ == "__main__":
    main()
