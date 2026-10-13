"""Filter the Penn Museum collections CSV for Indus objects and read the object pages of seals.

Usage (from the repository root):
    python experiments/2026-10-13-museum-open-access/harvest_penn.py
The CSV (Penn_Museum_Collections_Data.csv, updated 2026-10-07) is CC BY 4.0 per the download
page. It lacks the 'Other Number' and 'Bibliography' fields, so the object pages of the
seal-like originals are fetched for field numbers, MFA numbers, bibliography and image URLs.
Attribution: Penn Museum Collections Data, Penn Museum, CC BY 4.0.
"""
import csv
import re
import sys
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mo_common import PKG, RAW, ROOT, fetch, write_json  # noqa: E402
from classify import classify_record  # noqa: E402

CSV_URL = "https://collections.penn.museum/collections/assets/data/Penn_Museum_Collections_Data.csv"
PAT = re.compile(r"harapp|mohenjo|moenjo|chanhu|lothal|kalibangan|dholavira|indus|rakhi ?gha?r|rojdi", re.I)
COLS = ["placeName", "siteName", "culture", "cultureArea", "period", "inscriptionMarkLanguage", "description", "title",
        "objectName", "locus"]
SEALISH = re.compile(r"seal|tablet|impression|sealing|amulet|\btag\b|token", re.I)


def page_fields(path):
    s = BeautifulSoup(Path(path).read_text(encoding="utf-8", errors="replace"), "lxml")
    lines = s.get_text("\n", strip=True).split("\n")
    out = {}
    labels = ["Object Number", "Current Location", "Culture", "Provenience", "Site Name", "Date Made", "Section",
              "Materials", "Inscription Language", "Description", "Other Number", "Iconography", "Technique",
              "Credit Line", "Period", "Locus", "Measurements", "Object Name"]
    for i, ln in enumerate(lines):
        if ln in labels and i + 1 < len(lines) and ln not in out:
            out[ln] = lines[i + 1]
    if "Bibliography" in lines:
        idx = [i for i, ln in enumerate(lines) if ln == "Bibliography"]
        if len(idx) >= 2:
            start = idx[1] + 1
            stop = next((i for i in range(start, len(lines)) if lines[i].startswith("View related objects")), len(lines))
            out["Bibliography"] = " ".join(lines[start:stop])
    imgs = sorted({img.get("src") for img in s.find_all("img") if img.get("src") and "/collections/assets/" in img.get("src")})
    out["images"] = [("https://collections.penn.museum" + u) if u.startswith("/") else u for u in imgs]
    return out


def main():
    csv_meta = fetch("penn", CSV_URL, timeout=900)
    df = pd.read_csv(ROOT / csv_meta["path"], dtype=str, low_memory=False).fillna("")
    hit = df[COLS].apply(lambda r: bool(PAT.search(" | ".join(r))), axis=1)
    sub = df[hit]
    records = []
    for _, r in sub.iterrows():
        dims = {k: r[k] for k in ("length", "width", "height", "thickness", "depth", "outsideDiameter", "weight") if r[k]}
        rec = {
            "museum": "Penn Museum", "record_id": r["Record URL"].rsplit("/", 1)[-1], "accession": r["identifier"],
            "url": r["Record URL"].split("\n")[0], "title": r["title"], "object_name": r["objectName"],
            "classification": r["curatorialSection"], "culture": r["culture"], "period": r["period"],
            "date": r["dateMade"], "date_begin": r["earlyDate"], "date_end": r["lateDate"], "material": r["material"],
            "dimensions_raw": "; ".join(f"{k} {v}" for k, v in dims.items()) + (f" ({r['measurementUnit']})" if dims else ""),
            "findspot_raw": "; ".join(x for x in (r["placeName"], r["siteName"], r["locus"]) if x),
            "credit_line": r["creditLine"], "bibliography": [], "other_numbers": [],
            "inscription_note": r["inscriptionMarkLanguage"], "description": r["description"],
            "iconography": r["iconography"], "image_urls": [],
            "image_licence": "Penn Museum images: non-profit, education or personal use with credit (not an open licence)",
            "data_licence": "CC BY 4.0 (Penn Museum Collections Data)", "is_public_domain": False,
            "raw_path": csv_meta["path"], "raw_sha256": csv_meta["sha256"],
        }
        rec.update(classify_record(rec))
        # Penn's place field names the site; the Ur sealings and other foreign finds are not Indus
        if re.search(r"Iraq|Kuwait|Bahrain|New Zealand|Ghana|France|Sri Lanka", r["placeName"]):
            rec["indus_attributed"] = False
            rec["in_scope"] = False
            rec["exclusion_reason"] = "foreign site in place field"
        sealish = bool(SEALISH.search(r["objectName"] + " " + r["inscriptionMarkLanguage"]))
        rec["seal_like"] = sealish
        if rec["indus_attributed"] and sealish:
            rec["in_scope"] = True
            rec["exclusion_reason"] = ""
            if re.search(r"plaster|cast|reproduction|latex", r["material"] + " " + r["objectName"], re.I):
                rec["originality"] = "cast-or-replica"
            if rec["originality"] == "original":
                pm = fetch("penn", rec["url"])
                if pm["status"] == 200:
                    pf = page_fields(ROOT / pm["path"])
                    rec["other_numbers"] = [x.strip() for x in pf.get("Other Number", "").split("|") if x.strip()]
                    rec["bibliography"] = [pf["Bibliography"]] if pf.get("Bibliography") else []
                    rec["image_urls"] = pf.get("images", [])
                    rec["page_raw_path"] = pm["path"]
                    rec["page_raw_sha256"] = pm["sha256"]
        records.append(rec)
    write_json(RAW / "penn" / "records-extracted.json", records)
    out = PKG / "harvest"
    out.mkdir(exist_ok=True)
    tracked = [r for r in records if r["in_scope"]]
    write_json(out / "penn-records.json", tracked)
    with open(out / "penn-queries.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["query", "csv_rows", "rows_matching", "in_scope", "csv_sha256", "retrieved_utc"])
        w.writerow([f"regex {PAT.pattern} over {','.join(COLS)}", len(df), len(sub), len(tracked), csv_meta["sha256"],
                    csv_meta["retrieved_utc"]])
    for r in tracked:
        print(r["accession"], "|", r["object_name"], "|", r["material"], "|", r["originality"], "|", r["inscription_status"],
              "|", r["other_numbers"], "|", (r["bibliography"] or [""])[0][:80])
    print(len(df), "csv rows;", len(sub), "Indus-matching;", len(tracked), "in scope")


if __name__ == "__main__":
    main()
