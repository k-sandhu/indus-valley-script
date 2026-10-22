"""List local families at the listed sites that no row of objects.csv names.

Identity fields only. Sites whose baseline is a CISI 3 volume, and sites whose families are all
CISI-numbered, are summarised by count, because their unnamed families are catalogued objects.
Writes local-unnamed.csv in the package directory.
Usage: python -I unnamed_families.py <repo root>
"""
import csv, json, pathlib, sys
from collections import defaultdict

root = pathlib.Path(sys.argv[1])
pkg = root / "experiments/2026-10-21-post-catalogue-finds"
rows = list(csv.DictReader(open(pkg / "objects.csv", encoding="utf-8")))
named = {f for r in rows for f in r["local_family_ids"].split("|") if f}
seed = {r["site_code"]: r for r in csv.DictReader(open(pkg / "selection/sites-seed.csv", encoding="utf-8"))}
labels = {"Desalpar": "Desalpur", "Tarkhanewala Dera": "Tarkhanewala-dera", "Gola Dhoro (Bagasra)": "Gola Dhoro (Bagasra)", "Nuhato": "Nuhato"}
site_labels = {}
for r in rows:
    site_labels.setdefault(r["site_code"], {labels.get(r["site"], r["site"])})
site_labels.setdefault("NHT", set()).add("Gharo Bhiro")
keep = ["excavation-idno", "area-section", "block-house", "depth", "period", "material", "type"]
fams = defaultdict(dict)
with open(root / "data/normalized/lipi_observed_faces.jsonl", encoding="utf-8") as fh:
    for line in fh:
        d = json.loads(line)
        for code, labs in site_labels.items():
            if d["site"] in labs:
                m = d["metadata"]
                fams[code].setdefault(d["object_family_id"], {"site": d["site"], "cisi": d["source_cisi"], **{k: m.get(k) for k in keep}})
out, summary = [], []
for code, fs in sorted(fams.items()):
    baseline = next((r["baseline_volume"] for r in rows if r["site_code"] == code), "")
    unnamed = {fid: f for fid, f in fs.items() if fid not in named}
    no_cisi = {fid: f for fid, f in unnamed.items() if f["cisi"] in ("-", "", None)}
    summary.append((code, len(fs), len(unnamed), len(no_cisi)))
    if baseline.startswith("CISI 3"):
        continue
    for fid, f in sorted(no_cisi.items(), key=lambda x: int(x[0])):
        reg = f["excavation-idno"] if f["excavation-idno"] not in ("-", "", None) else ""
        out.append({"site_code": code, "site": f["site"], "object_family_id": fid, "type": f["type"], "material": f["material"] if f["material"] not in ("-", None) else "",
                    "excavation_idno": reg, "area_or_block": " / ".join(x for x in (f["area-section"], f["block-house"]) if x and x not in ("--", "-")),
                    "note": "post-catalogue object in the corpus that no row names: the list misses it, or its publication is outside the sources read"})
with open(pkg / "local-unnamed.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for s in summary:
    print(s)
print("rows written:", len(out))
