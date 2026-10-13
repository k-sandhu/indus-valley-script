"""Offline identifier recall search after the 13 October review.

Search every non-joined decision row, including impressions and uninscribed rows.
Use accession components separated by slash or semicolon as well as whole keys;
split a two-number hyphenated accession into its registration components. Other
punctuation is removed, without imposing a site or object-type filter. Source
record IDs used by web servers are locators, not archaeological identifiers.
The output contains candidates only; a printed-row image must decide a join.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
TABLE = ROOT / "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv"
FOCUSED = ROOT / "data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/focused-records.json"
RAW = ROOT / "data/raw/2026-10-13-museum-open-access"


def norm(value):
    return re.sub(r"[^a-z0-9]", "", str(value or "").casefold())


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def identifier_values(value):
    if isinstance(value, list):
        for item in value:
            yield from identifier_values(item)
    elif isinstance(value, dict):
        if "value" in value:
            yield from identifier_values(value["value"])
    elif value:
        # Number labels describe the identifier type, not part of the key.
        text = str(value).strip()
        text = re.sub(r"\s+-\s+.*(?:Number|Field No).*", "", text, flags=re.I)
        if ": " in text:
            label, tail = text.split(": ", 1)
            if re.search(r"number|field|registration|excavation|inventory", label, re.I):
                text = tail
        yield text
        yield from (s.strip() for s in re.split(r"[;/]", text) if s.strip() != text and s.strip())
        if re.fullmatch(r"\d+\s*-\s*\d+", text):
            yield from (s.strip() for s in text.split("-"))


def main():
    museum_sources = defaultdict(list)
    for record in read_json(FOCUSED):
        museum_sources[(record["institution"], record["accession"])].append(record)
    names = {"met": "Metropolitan Museum of Art", "cleveland": "Cleveland Museum of Art",
             "penn": "Penn Museum", "vam": "Victoria and Albert Museum", "bm": "British Museum"}
    for slug, museum in names.items():
        path = RAW / slug / "records-extracted.json"
        if path.exists():
            for record in read_json(path):
                if record.get("accession"):
                    museum_sources[(museum, record["accession"])].append(record)
    table_rows = read_csv(TABLE)
    table_by_family = defaultdict(list)
    for row in table_rows:
        if row["lipi_family_id"]:
            table_by_family[row["lipi_family_id"]].append(row)
    targets = set()
    for line in (ROOT / "data/normalized/lipi_observed_faces.jsonl").read_text(encoding="utf-8").splitlines():
        face = json.loads(line)
        family, metadata = face["object_family_id"], face["metadata"]
        cisi = str(metadata.get("cisi") or face.get("source_cisi") or "").strip()
        for field, value in [("excavation-idno", metadata.get("excavation-idno")),
                             ("cisi", metadata.get("cisi")), ("cisi", face.get("source_cisi"))]:
            if norm(value) and re.search(r"\d", str(value)):
                targets.add((family, cisi, "lipi:" + field, str(value).strip(), face.get("site", ""), ""))
    for row in table_rows:
        if norm(row["field_no"]):
            locator = f'{TABLE.relative_to(ROOT).as_posix()}#{row["source_row_id"]}; printed p. {row["printed_page"]}, row {row["catalogue_no"]}'
            targets.add((row["lipi_family_id"], row["cisi"], "table:field_no", row["field_no"], "", locator))
    targets = sorted(targets)
    nonjoined = [r for r in read_csv(PKG / "joins/join-table.csv") if r["joined"] != "True"]
    hits = []
    record_families = {}
    for decision in nonjoined:
        key = (decision["museum"], decision["accession"])
        identifiers = set(identifier_values(decision["accession"]))
        for record in museum_sources[key]:
            for field in ["accession", "excavation_raw", "other_numbers", "misc_number", "field_number", "registration_number", "museum_number", "excavation_number"]:
                identifiers.update(identifier_values(record.get(field)))
            for field, value in record.get("metadata", {}).items():
                if re.search(r"accession|object.?number|field.?no|excavation|registration|inventory|museum.?number|miscellaneous", field, re.I):
                    identifiers.update(identifier_values(value))
        identifiers = sorted({norm(value) for value in identifiers if norm(value)})
        families = set()
        for identifier in identifiers:
            for family, cisi, source, matched, site, locator in targets:
                if identifier not in norm(matched):
                    continue
                if family:
                    families.add(family)
                locators = [locator] if locator else [
                    f'{TABLE.relative_to(ROOT).as_posix()}#{r["source_row_id"]}; printed p. {r["printed_page"]}, row {r["catalogue_no"]}'
                    for r in table_by_family[family]]
                if not locators:
                    page = {"Mohenjo-daro": "366-370", "Harappa": "370-372", "Lothal": "372-373",
                            "Chanhu-daro": "374-375", "Banawali": "375"}.get(site)
                    locators = [f'CISI object entry {cisi}; ' + (f'CISI 1 basic-data pp. {page} if present; ' if page else '') + 'printed identifier row not yet located']
                for loc in sorted(set(locators)):
                    hits.append(dict(museum=key[0], accession=key[1], museum_identifier_normalized=identifier,
                                     family=family, cisi=cisi, match_source=source, matched_string=matched,
                                     confirmation_locator=loc))
        if families or any(h["museum"] == key[0] and h["accession"] == key[1] for h in hits):
            record_families[key] = families
    fields = ["museum", "accession", "museum_identifier_normalized", "family", "cisi", "match_source", "matched_string", "confirmation_locator"]
    with (PKG / "joins/recall-candidates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(hits)
    summary = {"date": "2026-10-13", "nonjoined_records_searched": len(nonjoined),
               "records_with_hits": len(record_families),
               "records_with_single_family_hits": sum(len(families) == 1 for families in record_families.values()),
               "records_with_multiple_family_hits": sum(len(families) > 1 for families in record_families.values()),
               "records_with_only_unassigned_table_hits": sum(not families for families in record_families.values()),
               "candidate_rows": len(hits), "joins_added_by_search": 0,
               "scope": "All non-joined decision rows; no site filter; identifiers and printed-row locators only."}
    (PKG / "joins/recall-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
