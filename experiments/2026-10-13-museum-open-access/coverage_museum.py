"""Object-level museum-accession coverage before and after this package.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/coverage_museum.py
'Before' counts families with a MUSEUM value in the older website export (the data inventory's
definition, 5.8%) and, separately, that set joined with the census's 68 confirmed families.
'After' adds the families joined (exact or confirmed) in joins/join-table.csv.
Writes coverage/museum-coverage.json.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG))
from lipi_index import load, norm  # noqa: E402

ROOT = PKG.parents[1]


# Copied rule: experiments/2026-10-12-data-inventory/coverage.py,
# TYPE_GROUPS, norm() and type_group(). Display labels retain this package's spelling.
TYPE_GROUP_SOURCE = "experiments/2026-10-12-data-inventory/coverage.py:type_group"
TYPE_GROUPS = [("SEAL", "seal"), ("TAB:B", "tablet, bas-relief"),
               ("TAB:I", "tablet, incised"), ("TAB:C", "tablet, copper"),
               ("TAG", "tag or sealing"), ("POT", "pottery"), ("POST", "pottery")]
LABELS = {"seal": "Seals", "tablet, bas-relief": "Tablets, bas-relief",
          "tablet, incised": "Tablets, incised", "tablet, copper": "Tablets, copper",
          "tag or sealing": "Tags and sealings", "pottery": "Pottery", "other": "Other"}


def type_group(raw):
    text = re.sub(r"\s+", " ", str(raw if raw is not None else "")).strip().upper().replace("POST:", "POT:")
    for prefix, label in TYPE_GROUPS:
        if text.startswith(prefix):
            return label
    return "other"


def group(raw):
    return LABELS[type_group(raw)]


def main():
    fams = load()
    website = set()
    for line in open(ROOT / "data/normalized/indus_website_observed.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r["metadata"].get("MUSEUM"):
            website.add(norm(r["source_cisi"]))
    web_f = {f["family"] for f in fams.values() if f["cisi_norm"] & website}
    census = {x["family"] for x in json.loads((ROOT / "data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/"
                                               "confirmed-object-joins.json").read_text(encoding="utf-8"))}
    rows = list(csv.DictReader(open(PKG / "joins/join-table.csv", encoding="utf-8")))
    new = {r["family"] for r in rows if r["joined"] == "True"}
    n = len(fams)
    out = {"objects": n, "type_group_source": TYPE_GROUP_SOURCE}
    sets = {"website_export_only": web_f, "website_or_census_joins": web_f | census,
            "website_or_census_or_this_package": web_f | census | new}
    for k, s in sets.items():
        out[k] = {"objects": len(s), "percent": round(100 * len(s) / n, 2)}
    by = {}
    for k, s in sets.items():
        c = Counter(group(fams[f].get("type")) for f in s)
        tot = Counter(group(f.get("type")) for f in fams.values())
        by[k] = {g: f"{c[g]}/{tot[g]} ({100 * c[g] / tot[g]:.1f}%)" for g in sorted(tot)}
    out["by_type"] = by
    site_tot = Counter(f["site"] for f in fams.values())
    out["by_site_after"] = {s: f"{sum(1 for f in sets['website_or_census_or_this_package'] if fams[f]['site'] == s)}/{site_tot[s]}"
                            for s in ("Mohenjo-daro", "Harappa", "Lothal", "Chanhu-daro", "Banawali", "Dholavira", "Kalibangan")}
    out["families_joined_here_not_in_census"] = sorted(new - census, key=int)
    out["families_joined_here_new_to_any_museum_value"] = sorted(new - census - web_f, key=int)
    (PKG / "coverage").mkdir(exist_ok=True)
    (PKG / "coverage" / "museum-coverage.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
