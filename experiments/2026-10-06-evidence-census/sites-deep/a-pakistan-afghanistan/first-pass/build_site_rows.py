"""Assemble site, source, search, and comparison tables from the three research slices."""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


OUT = Path(__file__).resolve().parent
ROOT = next(p for p in OUT.parents if (p / "knowledge" / "INDEX.md").exists())
COVERAGE_PATH = ROOT / "experiments/2026-10-06-research-program/local-site-coverage.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def refs(value, source_map, search_map):
    if isinstance(value, list):
        return [refs(v, source_map, search_map) for v in value]
    if isinstance(value, dict):
        updated = {}
        for key, item in value.items():
            if key == "source_id" and isinstance(item, str):
                updated[key] = source_map.get(item, item)
            elif key == "source_ids" and isinstance(item, list):
                updated[key] = [source_map.get(v, v) for v in item]
            elif key == "search_ids" and isinstance(item, list):
                updated[key] = [search_map.get(v, v) for v in item]
            else:
                updated[key] = refs(item, source_map, search_map)
        return updated
    return value


parts = [
    ("ML", "part-major-lower.json", "part-major-lower-sources.json", "part-major-lower-searches.json"),
    ("WU", "part-west-upper.json", "part-west-upper-sources.json", "part-west-upper-searches.json"),
    ("AL", "part-afghan-local.json", "part-afghan-local-sources.json", "part-afghan-local-searches.json"),
]

rows = []
sources = []
searches = []
additional_sites = []
for prefix, row_name, source_name, search_name in parts:
    part_rows = load_json(OUT / row_name)
    part_sources = load_json(OUT / source_name)
    part_searches = load_json(OUT / search_name)
    source_map = {item["id"]: f"{prefix}-{item['id']}" for item in part_sources}
    search_map = {item["id"]: f"{prefix}-{item['id']}" for item in part_searches}
    rows.extend(refs(part_rows.get("sites", []), source_map, search_map) if isinstance(part_rows, dict) else refs(part_rows, source_map, search_map))
    if isinstance(part_rows, dict):
        additional_sites.extend(refs(part_rows.get("additional_same_region_sites", []), source_map, search_map))
    sources.extend({**item, "id": source_map[item["id"]], "research_slice": prefix} for item in part_sources)
    searches.extend({**item, "id": search_map[item["id"]], "research_slice": prefix} for item in part_searches)

integration_sources = load_json(OUT / "integration-sources.json")["sources"]
integration_searches = load_json(OUT / "integration-searches.json")["searches"]
sources.extend(integration_sources)
searches.extend(integration_searches)

for source in sources:
    access = str(source.get("access", source.get("mode", "")))
    if "opened" not in source:
        lowered = access.casefold()
        source["opened"] = not any(token in lowered for token in ("snippet only", "search snippet only", "result excerpt", "not opened")) and any(token in lowered for token in ("opened", "open full", "page opened", "pdf opened", "inspected"))
    source.setdefault("access_status", "opened" if source["opened"] else "snippet or bibliographic lead")
    if not source.get("authors") or not source.get("year") or not source.get("venue"):
        original = str(source.get("title", ""))
        match = re.match(r"^(.*?)\.\s*[“\"](.+?)[”\"]\.?\s*(.*)$", original)
        if match:
            author, exact_title, tail = match.groups()
            source.setdefault("citation_as_recorded", original)
            source["title"] = exact_title
            source.setdefault("authors", author)
            year_match = re.search(r"\b(18|19|20)\d{2}\b", tail)
            if year_match:
                source.setdefault("year", int(year_match.group(0)))
                source.setdefault("venue", tail[:year_match.start()].strip(" ,.;"))
                source.setdefault("citation_details", tail[year_match.start():].strip())
            elif tail:
                source.setdefault("venue", tail.strip(" ,.;"))
        else:
            year_match = re.search(r"\b(18|19|20)\d{2}\b", original)
            if year_match and not source.get("year"):
                source["year"] = int(year_match.group(0))
    source.setdefault("authors", None)
    source.setdefault("year", None)
    source.setdefault("venue", None)

coverage = load_json(COVERAGE_PATH)["sites"]
local_by_key = {norm(item["site"]): item for item in coverage}
aliases = {
    "balakot": "bala-kot",
    "rehmandheri": "rahmanderi",
    "rahmandheri": "rahmanderi",
    "nindowari": "nindowaridamb",
    "lakhanjodaro": "lakhanjodaro",
    "kotdiji": "kotdiji",
}
for row in rows:
    key = norm(row["canonical_name"])
    key = norm(aliases.get(key, row["canonical_name"]))
    local = local_by_key.get(key)
    if local is None:
        row_aliases = {key, *(norm(a) for a in row.get("alternative_spellings", []))}
        local = next((item for item in coverage if norm(item["site"]) in row_aliases), None)
    row["local_corpus"] = local
    if local:
        row["local_coverage_judgment"] = (
            f"Local snapshot contains {local['faces']} face rows, {local['object_families']} object families, "
            f"{local['distinct_cisi_ids']} distinct CISI IDs and prefixes {local['cisi_prefixes']} "
            f"(highest recorded numbers {local['max_cisi_number_by_prefix']}). The highest ID is a coverage indicator, "
            "not a completeness proof; these local rows are not independent physical-object counts."
        )
    else:
        row["local_coverage_judgment"] = "No matching site label occurs in the pinned local coverage snapshot; local presence is not evidence that no published material exists."
    row.setdefault("alternative_spellings", [])
    row.setdefault("province", None)
    row.setdefault("coordinates", None)
    row.setdefault("excavation_campaigns", [])
    row.setdefault("publications", [])
    row.setdefault("cisi", None)
    row.setdefault("mahadevan_1977_count", None)
    row.setdefault("icit_count", None)
    row.setdefault("reported_object_counts", [])
    row.setdefault("publication_metadata", None)
    row.setdefault("post_cisi_finds", [])
    row.setdefault("present_holding", None)
    row.setdefault("digital_availability", None)
    row.setdefault("open_problems", [])
    row.setdefault("source_ids", [])
    row.setdefault("search_ids", [])
    row.setdefault("status", "Exploratory")
    if isinstance(row.get("reported_object_counts"), list):
        row["reported_object_counts"] = [
            item for item in row["reported_object_counts"]
            if not (isinstance(item, dict) and ("local face" in str(item.get("unit", "")).casefold() or "LOCAL-COVERAGE" in str(item.get("source_id", ""))))
        ]

excluded_local_sites = {
    "Kalibangan": ("India", ["PRIOR-SITE-REGISTER"], "The prior broad site register assigns Kalibangan to India."),
    "Karanpura": ("India", ["KARANPURA-IITGN", "INDIA-PARLIAMENT-2015"], "Institutional and government records locate the site in Rajasthan, India."),
    "Baror": ("India", ["INDIA-PARLIAMENT-2015"], "Rajya Sabha proceedings locate Baror in Sriganganagar District, Rajasthan, India."),
    "Tarkhanewala-dera": ("India", ["INDIA-PARLIAMENT-2015"], "Rajya Sabha proceedings locate Tarkhanwala Dhera in Ganganagar District, Rajasthan, India."),
    "Tigrana": ("India", ["TIGRANA-HARYANA-GOV", "TIGRANA-CURRENT-SCIENCE"], "Haryana government and scholarly records locate Tigrana in Bhiwani District, India."),
}
exclusions = []
kept_rows = []
for row in rows:
    excluded = excluded_local_sites.get(row["canonical_name"])
    if excluded:
        country, source_ids, reason = excluded
        local = local_by_key.get(norm(row["canonical_name"]))
        exclusions.append({"canonical_name": row["canonical_name"], "country": country, "local_corpus": local, "reason": reason, "source_ids": source_ids, "search_ids": row.get("search_ids", [])})
    elif row.get("country") not in {"Pakistan", "Afghanistan"} and row.get("canonical_name") != "Rajanpur":
        exclusions.append({"canonical_name": row["canonical_name"], "country": row.get("country"), "local_corpus": row.get("local_corpus"), "reason": "Outside Pakistan–Afghanistan scope according to the site-row location evidence.", "source_ids": row.get("source_ids", []), "search_ids": row.get("search_ids", [])})
    else:
        kept_rows.append(row)
rows = kept_rows
for name, (country, source_ids, reason) in excluded_local_sites.items():
    if not any(item["canonical_name"] == name for item in exclusions):
        local = local_by_key.get(norm(name))
        exclusions.append({"canonical_name": name, "country": country, "local_corpus": local, "reason": reason, "source_ids": source_ids, "search_ids": []})

all_source_ids = {item["id"] for item in sources}
source_aliases = {"CII": "AL-CII", "CAT": "AL-CAT"}
for item in additional_sites:
    item["source_ids"] = [source_aliases.get(value, value) for value in item.get("source_ids", [])]
    item["source_ids"] = [value for value in item["source_ids"] if value in all_source_ids]
for item in exclusions:
    item["source_ids"] = [value for value in item.get("source_ids", []) if value in all_source_ids]

count_categories = {
    "seals": ("seal",),
    "sealings": ("sealing", "impression"),
    "tablets": ("tablet",),
    "inscribed_pottery_and_graffiti": ("pottery", "sherd", "graffiti", "pottery mark"),
    "metal": ("metal", "copper", "bronze"),
    "other_inscribed_objects": ("other", "misc", "ring", "bangle", "rod", "bead", "unidentified"),
}
for row in rows:
    assessed = {}
    evidence = row.get("reported_object_counts")
    claims = []
    if isinstance(evidence, list):
        claims = [item for item in evidence if isinstance(item, dict)]
    elif isinstance(evidence, dict):
        claims = [item for item in evidence.get("reported_values", []) if isinstance(item, dict)]
    for category, keywords in count_categories.items():
        matched = []
        for claim in claims:
            text = " ".join(str(claim.get(key, "")) for key in ("unit", "report", "value", "claim", "count_basis_and_date")).casefold()
            explicit_class = str(claim.get("class", "")).casefold()
            if any(word in text or word in explicit_class for word in keywords):
                matched.append({
                    "count": claim.get("count"),
                    "unit_or_basis": claim.get("unit", claim.get("count_basis_and_date", "source narrative")),
                    "date": claim.get("date"),
                    "source_location": claim.get("location"),
                    "source_ids": claim.get("source_ids", [claim.get("source_id")] if claim.get("source_id") else row.get("source_ids", [])),
                    "claim": claim.get("report", claim.get("value", claim.get("claim"))),
                    "inscription_status": "not established as inscribed" if "not said to be inscribed" in text or "not necessarily accepted" in text else "source's inscription relation retained as stated",
                })
        if not matched and isinstance(evidence, dict):
            by_class = evidence.get("by_class", {})
            class_alias = {"inscribed_pottery_and_graffiti": "inscribed_pottery_or_graffiti", "metal": "metal_or_other"}.get(category, category)
            description = by_class.get(class_alias)
            if description:
                matched.append({"count": None, "unit_or_basis": description, "date": None, "source_location": None, "source_ids": row.get("source_ids", []), "claim": None})
        if not matched:
            matched.append({
                "count": None,
                "unit_or_basis": "No class-specific published count located in this pass.",
                "date": None,
                "source_location": None,
                "source_ids": row.get("source_ids", []),
                "search_ids": row.get("search_ids", []),
            })
        assessed[category] = matched
    row["reported_counts_by_class"] = assessed

rows.sort(key=lambda row: row["canonical_name"].casefold())
all_search_ids = {item["id"] for item in searches}
for row in rows:
    row["source_ids"] = sorted(set(row["source_ids"]) & all_source_ids)
    row["search_ids"] = sorted(set(row["search_ids"]) & all_search_ids)

numeric_count_records = []
count_comparisons = []
for row in rows:
    counts = row.get("reported_object_counts") or []
    if isinstance(counts, list):
        for item in counts:
            if isinstance(item, dict) and isinstance(item.get("count"), (int, float)):
                numeric_count_records.append({"site": row["canonical_name"], **item})
    local = row.get("local_corpus")
    count_comparisons.append({
        "site": row["canonical_name"],
        "published_numeric_counts": [item for item in counts if isinstance(item, dict) and isinstance(item.get("count"), (int, float))] if isinstance(counts, list) else [],
        "published_claims_without_machine_numeric_count": counts if not isinstance(counts, list) or not any(isinstance(item, dict) and isinstance(item.get("count"), (int, float)) for item in counts) else [],
        "local_faces": local.get("faces") if local else None,
        "local_object_families": local.get("object_families") if local else None,
        "local_distinct_cisi_ids": local.get("distinct_cisi_ids") if local else None,
        "local_id_prefixes_and_maxima": {"prefixes": local.get("cisi_prefixes"), "maxima": local.get("max_cisi_number_by_prefix")} if local else None,
        "comparison_note": "Source counts and local face/family/ID rows are retained separately until units and object identities can be joined.",
    })

local_totals = Counter()
for row in rows:
    local = row.get("local_corpus")
    if local:
        for key in ("faces", "object_families", "distinct_cisi_ids"):
            local_totals[key] += int(local.get(key, 0))

# Bibliography-level classification for the report. These titles/series are
# identified in the row bibliographies as site-level final or comprehensive
# excavation publications; this does not imply full-text inspection.
final_publication_sites = [
    "Allahdino", "Amri", "Balakot", "Chanhu-daro", "Harappa", "Kot Diji",
    "Mehrgarh", "Mohenjo-daro", "Mundigak", "Nausharo", "Nindowari",
    "Pirak", "Rehman Dheri", "Shortughai",
]

aggregate = {
    "as_of": "2026-10-07",
    "status": "Exploratory",
    "scope": "Pakistan and Afghanistan; user-named sites plus Pakistan local-corpus labels in Lower Indus, Upper Indus and Inter-Riverine. India-side local labels are recorded separately.",
    "sites": len(rows),
    "sites_with_any_identified_publication": sum(bool(row.get("publications")) for row in rows),
    "sites_with_final_or_comprehensive_excavation_publication_identified": [
        name for name in final_publication_sites
        if any(row["canonical_name"] == name for row in rows)
    ],
    "final_publication_classification_note": "Bibliography-level identification from row records; not all volumes were inspected in full.",
    "sites_with_post_cisi_notes": sum(bool(row.get("post_cisi_finds")) for row in rows),
    "queries": len(searches),
    "source_records": len(sources),
    "local_coverage_sites": sum(bool(row.get("local_corpus")) for row in rows),
    "local_totals": dict(local_totals),
    "published_numeric_count_records": numeric_count_records,
    "sites_with_at_least_one_numeric_source_count": sum(bool(item["published_numeric_counts"]) for item in count_comparisons),
    "count_comparability_note": "Numeric source values are listed by site and retain their source unit. The list is not summed: physical objects, texts, impressions, faces and sign-bearing sherds use different denominators and publications overlap.",
    "additional_same_region_sites": additional_sites,
    "scope_exclusions": exclusions,
    "output_files": ["site-rows.json", "site-rows.csv", "sources.json", "searches.json", "aggregate.json", "scope-exclusions.json", "site-count-comparison.json"],
}

(OUT / "site-rows.json").write_text(json.dumps({"as_of": aggregate["as_of"], "status": "Exploratory", "sites": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "sources.json").write_text(json.dumps({"as_of": aggregate["as_of"], "sources": sources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "searches.json").write_text(json.dumps({"as_of": aggregate["as_of"], "searches": searches}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "aggregate.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "scope-exclusions.json").write_text(json.dumps({"as_of": aggregate["as_of"], "exclusions": exclusions, "additional_same_region_sites": additional_sites}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(OUT / "site-count-comparison.json").write_text(json.dumps({"as_of": aggregate["as_of"], "comparison_note": aggregate["count_comparability_note"], "sites": count_comparisons}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

columns = [
    "canonical_name", "alternative_spellings", "country", "province", "coordinates", "excavation_campaigns",
    "publications", "cisi", "mahadevan_1977_count", "icit_count", "reported_object_counts", "local_corpus",
    "local_coverage_judgment", "publication_metadata", "post_cisi_finds", "present_holding",
    "digital_availability", "open_problems", "reported_counts_by_class", "source_ids", "search_ids", "status",
]
with (OUT / "site-rows.csv").open("w", newline="", encoding="utf-8-sig") as stream:
    writer = csv.DictWriter(stream, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(row.get(key), ensure_ascii=False) if isinstance(row.get(key), (dict, list)) else row.get(key) for key in columns})

print(f"Wrote {len(rows)} site rows, {len(sources)} source records, {len(searches)} searches.")
