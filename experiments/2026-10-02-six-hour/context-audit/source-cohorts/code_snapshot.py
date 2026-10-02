"""Audit archaeological field availability without copying corpus sequences.

Run manually from the project root. Inputs stay local; outputs contain aggregates,
source hashes and a small reproducible audit of the counting rules.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "experiments/2026-10-02-six-hour/context-audit/main"
UNKNOWN = {"unknown", "unk", "n/a", "na", "?", "??", "null", "not known"}
DIMENSIONS = {"horizontal(mm)", "vertical(mm)", "thickness(mm)"}
MOTIFS = {"symbol", "cult"}
CONTEXT = ["site", "region", "cisi", "area-section", "block-house", "room-grid",
           "excavation-idno", "time", "period", "phase", "depth", "material",
           "symbol", "cult", "type", "shape", "h", "v", "th", *sorted(DIMENSIONS)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def cleaned(value: object) -> str:
    return " ".join(str(value if value is not None else "").strip().split())


def numeric(value: object) -> float | None:
    s = cleaned(value)
    if not re.fullmatch(r"[+\-]?\d+(?:\.\d+)?", s):
        return None
    return float(s)


def status(field: str, value: object) -> str:
    s = cleaned(value)
    if not s or not s.strip("- \t") or s.casefold() in UNKNOWN:
        return "missing"
    if field in DIMENSIONS:
        n = numeric(s)
        return "positive_numeric" if n is not None and n > 0 else "zero_or_negative" if n is not None else "reported_unparsed"
    if field in MOTIFS and s.casefold() == "none":
        return "catalogued_absence"
    return "reported"


def available(field: str, value: object) -> bool:
    return status(field, value) in {"reported", "positive_numeric", "catalogued_absence"}


def field_value(row: dict, field: str) -> str:
    return row["metadata"].get(field, "")


def entropy(counts: Counter) -> float:
    n = sum(counts.values())
    return -sum(c / n * math.log2(c / n) for c in counts.values()) if n else 0.0


def field_audit(rows: list[dict], groups: dict[str, list[dict]], field: str) -> dict:
    statuses = Counter(status(field, field_value(r, field)) for r in rows)
    literal = Counter(field_value(r, field) for r in rows)
    missing_literals = {k: v for k, v in sorted(literal.items()) if not available(field, k)}
    family_any = family_all = family_variation = 0
    values_per_family = Counter()
    family_statuses = Counter()
    for members in groups.values():
        vals = {cleaned(field_value(r, field)) for r in members if available(field, field_value(r, field))}
        family_any += bool(vals)
        family_all += all(available(field, field_value(r, field)) for r in members)
        family_variation += len(vals) > 1
        values_per_family[len(vals)] += 1
        if not vals:
            family_statuses["no_value"] += 1
        elif len(vals) > 1:
            family_statuses["several_values"] += 1
        else:
            family_statuses["one_value"] += 1
    return {
        "row_statuses": dict(statuses), "reported_rows": sum(available(field, field_value(r, field)) for r in rows),
        "literal_unique_values": len(literal), "informative_unique_values": sum(available(field, s) for s in literal),
        "most_common_literals": literal.most_common(12), "missing_or_unusable_literals": missing_literals,
        "families_any_value": family_any, "families_every_face_has_value": family_all,
        "families_distinct_face_values": family_variation, "family_value_counts": dict(values_per_family),
        "family_statuses": dict(family_statuses),
    }


def joint(rows: list[dict], groups: dict[str, list[dict]], predicate) -> dict:
    passing = sum(predicate(r) for r in rows)
    return {"rows": passing, "families_any_face": sum(any(predicate(r) for r in members) for members in groups.values()),
            "families_every_face": sum(all(predicate(r) for r in members) for members in groups.values())}


def all_fields(row: dict, fields: list[str]) -> bool:
    return all(available(f, field_value(row, f)) for f in fields)


def any_date(row: dict) -> bool:
    return any(available(f, field_value(row, f)) for f in ["time", "period", "phase"])


def field_by_strata(rows: list[dict], strata_fields: list[str], target: str) -> list[dict]:
    strata = defaultdict(list)
    for r in rows:
        if all_fields(r, strata_fields):
            strata[tuple(cleaned(field_value(r, f)) for f in strata_fields)].append(r)
    out = []
    for key, members in sorted(strata.items()):
        by_family = defaultdict(set)
        for r in members:
            if available(target, field_value(r, target)):
                by_family[r["object_family_id"]].add(cleaned(field_value(r, target)))
        # Ambiguous family values are retained but excluded from single-label counts.
        c = Counter(next(iter(v)) for v in by_family.values() if len(v) == 1)
        out.append({"stratum": dict(zip(strata_fields, key)), "rows": len(members),
                    "families": len({r["object_family_id"] for r in members}), "families_with_target": len(by_family),
                    "families_one_target": sum(len(v) == 1 for v in by_family.values()),
                    "families_several_targets": sum(len(v) > 1 for v in by_family.values()),
                    "target_family_counts": dict(c), "target_entropy_bits": entropy(c),
                    "largest_target_fraction": max(c.values()) / sum(c.values()) if c else None,
                    "labels_with_at_least_10_families": sum(n >= 10 for n in c.values())})
    return out


class DSU:
    def __init__(self, n: int):
        self.p = list(range(n))

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[b] = a


def components(rows: list[dict]) -> dict:
    d = DSU(len(rows))
    seen_family, seen_seq = {}, {}
    for i, r in enumerate(rows):
        fam, seq = r["object_family_id"], tuple(r["signs_reading_rtl"])
        for key, seen in [(fam, seen_family), (seq, seen_seq)]:
            if key in seen:
                d.union(i, seen[key])
            else:
                seen[key] = i
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        groups[d.find(i)].append(r)
    cross = {}
    for f in ["site", "type", "material", "time", "period", "phase", "symbol", "area-section"]:
        label_counts = []
        mixed_rows = mixed_families = 0
        for members in groups.values():
            labels = {cleaned(field_value(r, f)) for r in members if available(f, field_value(r, f))}
            label_counts.append(len(labels))
            if len(labels) > 1:
                mixed_rows += len(members)
                mixed_families += len({r["object_family_id"] for r in members})
        cross[f] = {"component_label_count_histogram": dict(Counter(label_counts)),
                    "mixed_components": sum(n > 1 for n in label_counts), "rows_in_mixed_components": mixed_rows,
                    "family_memberships_in_mixed_components": mixed_families}
    return {"rows": len(rows), "families": len(seen_family), "unique_whole_sequences": len(seen_seq),
            "components": len(groups), "max_component_rows": max(map(len, groups.values()), default=0),
            "component_size_histogram": dict(Counter(map(len, groups.values()))), "cross_labels": cross}


def simple_cisi(s: str) -> str | None:
    m = re.fullmatch(r"([A-Za-z]+)-?(\d+)(?:[A-Za-z])?", cleaned(s))
    return f"{m.group(1).upper()}-{int(m.group(2))}" if m else None


def identifier_audit(rows: list[dict], groups: dict[str, list[dict]]) -> dict:
    cisi = defaultdict(set)
    excavation = defaultdict(set)
    excavation_nondigit = Counter()
    for r in rows:
        base = simple_cisi(field_value(r, "cisi"))
        if base:
            cisi[base].add(r["object_family_id"])
        val = cleaned(field_value(r, "excavation-idno"))
        if available("excavation-idno", val):
            if not re.search(r"\d", val):
                excavation_nondigit[val] += 1
            excavation[(cleaned(field_value(r, "site")), val)].add(r["object_family_id"])
    return {"rows_simple_cisi": sum(simple_cisi(field_value(r, "cisi")) is not None for r in rows),
            "families_simple_cisi": sum(any(simple_cisi(field_value(r, "cisi")) for r in rs) for rs in groups.values()),
            "simple_cisi_bases": len(cisi), "bases_assigned_to_multiple_families": sum(len(v) > 1 for v in cisi.values()),
            "excavation_labels_site_namespaced": len(excavation),
            "excavation_labels_shared_across_families": sum(len(v) > 1 for v in excavation.values()),
            "shared_excavation_family_count_histogram": dict(Counter(len(v) for v in excavation.values() if len(v) > 1)),
            "reported_excavation_labels_without_digits": dict(excavation_nondigit),
            "excavation_rows_containing_digit": sum(available("excavation-idno", field_value(r, "excavation-idno")) and bool(re.search(r"\d", field_value(r, "excavation-idno"))) for r in rows)}


def dimensions_audit(rows: list[dict]) -> dict:
    result = {}
    for raw, converted in [("h", "horizontal(mm)"), ("v", "vertical(mm)"), ("th", "thickness(mm)")]:
        categories = Counter()
        scale_counts = Counter()
        for r in rows:
            a, b = numeric(field_value(r, raw)), numeric(field_value(r, converted))
            if a is not None and a > 0 and b is not None and b > 0:
                categories["both_positive"] += 1
                ratio = b / a
                if abs(ratio - 25.4) <= 0.11 / a:
                    scale_counts["approximately_25.4"] += 1
                elif abs(ratio - 10) <= 0.11 / a:
                    scale_counts["approximately_10"] += 1
                elif abs(ratio - 1) <= 0.11 / a:
                    scale_counts["approximately_1"] += 1
                else:
                    scale_counts["other_ratio"] += 1
            elif b is not None and b > 0:
                categories["positive_mm_without_positive_raw_numeric"] += 1
            elif a is not None and a > 0:
                categories["positive_raw_numeric_without_positive_mm"] += 1
            else:
                categories["neither_positive_numeric"] += 1
        result[converted] = {"paired_categories": dict(categories), "raw_to_mm_ratio_groups": dict(scale_counts),
                              "ratio_tolerance": "absolute 0.11 mm after multiplying raw by candidate scale"}
    depth_units = Counter()
    numerical_depth = 0
    for r in rows:
        s = cleaned(field_value(r, "depth"))
        if available("depth", s):
            numerical_depth += bool(re.search(r"\d", s))
            if re.search(r"\bft\b", s, re.I):
                depth_units["ft"] += 1
            elif re.search(r"\bm\b", s, re.I):
                depth_units["m"] += 1
            elif re.search(r"\bcm\b", s, re.I):
                depth_units["cm"] += 1
            else:
                depth_units["other_or_no_unit"] += 1
    result["depth"] = {"reported_containing_digit": numerical_depth, "reported_unit_counts": dict(depth_units),
                         "datum_status": "not established by export string"}
    return result


def mayig_audit(mayig: list[dict], lipi: list[dict]) -> dict:
    sources = defaultdict(list)
    for r in lipi:
        base = simple_cisi(r["source_cisi"])
        if base:
            sources[base].append(r)
    joins = Counter()
    matched = []
    desc_symbol = defaultdict(Counter)
    for r in mayig:
        candidates = sources.get(simple_cisi(r["object_family_id"]), [])
        families = {x["object_family_id"] for x in candidates}
        joins["no_family" if not families else "one_family" if len(families) == 1 else "several_families"] += 1
        if len(families) == 1:
            matched.extend(candidates)
            symbols = {cleaned(field_value(x, "symbol")) for x in candidates if available("symbol", field_value(x, "symbol"))}
            for symbol in symbols:
                desc_symbol[r["description"]][symbol] += 1
    matched_unique = {r["record_id"]: r for r in matched}
    return {"rows": len(mayig), "families": len({r["object_family_id"] for r in mayig}),
            "keys": sorted(set().union(*(r.keys() for r in mayig))),
            "site_counts": dict(Counter(r["site"] for r in mayig)), "object_type_counts": dict(Counter(r["object_type"] for r in mayig)),
            "description_counts": dict(Counter(r["description"] for r in mayig)), "cisi_family_joins": dict(joins),
            "unique_matched_lipi_faces": len(matched_unique),
            "matched_lipi_field_coverage": {f: sum(available(f, field_value(r, f)) for r in matched_unique.values()) for f in CONTEXT},
            "description_to_lipi_symbol_family_counts": {k: dict(v) for k, v in desc_symbol.items()},
            "field_basis": {"site": "derived from CISI prefix", "object_type": "normalizer parses annotator description",
                            "description": "upstream annotator label", "graphemes_and_line_count": "upstream graphic annotations"}}


def check_rules() -> dict:
    cases = [("depth", "- -", "missing"), ("material", "--", "missing"), ("site", "Unknown", "missing"),
             ("symbol", "None", "catalogued_absence"), ("cult", "?", "missing"),
             ("horizontal(mm)", "0", "zero_or_negative"), ("horizontal(mm)", "25.4", "positive_numeric"),
             ("horizontal(mm)", "25?", "reported_unparsed"), ("depth", "-0.0 m", "reported"),
             ("room-grid", "-Am40/1", "reported")]
    for field, value, expected in cases:
        assert status(field, value) == expected, (field, value, expected, status(field, value))
    tiny = [{"object_family_id": "a", "signs_reading_rtl": ["1", "2", "3"], "metadata": {"site": "x"}},
            {"object_family_id": "a", "signs_reading_rtl": ["4", "5", "6"], "metadata": {"site": "x"}},
            {"object_family_id": "b", "signs_reading_rtl": ["4", "5", "6"], "metadata": {"site": "y"}}]
    c = components(tiny)
    assert c["components"] == 1 and c["cross_labels"]["site"]["mixed_components"] == 1
    return {"placeholder_cases_passed": len(cases), "transitive_component_case_passed": True}


def source_cohorts(output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite endpoint: {output}")
    source = ROOT / "data/normalized/lipi_observed_faces.jsonl"
    rows = read_jsonl(source)
    indexed = defaultdict(list)
    for row in rows:
        base = simple_cisi(row["source_cisi"])
        if base:
            indexed[base].append(row)
    cohorts = {"incised_tablet_copies": range(2218, 2240), "sealings_and_stopper": range(1719, 1726),
               "stamped_vessels": range(1727, 1767), "targeted_source_cautions": [1537, 1539]}
    result = {}
    for name, ids in cohorts.items():
        ids = list(ids)
        matched = []
        joins = []
        for n in ids:
            base = f"H-{n}"
            faces = indexed.get(base, [])
            families = {r["object_family_id"] for r in faces}
            matched.extend(faces)
            joins.append({"cisi_base": base, "family_count": len(families), "faces": len(faces),
                          "any_clean_rtl_singleline_face": any(r["clean_rtl_singleline"] for r in faces),
                          "any_primary_eligible_face": any(r["clean_rtl_singleline"] and r["length"] >= 3 for r in faces)})
        per_stage = {
            "all_matched": lambda r: True,
            "complete_observed": lambda r: r["complete_observed"],
            "complete_rtl": lambda r: r["complete_observed"] and r["direction"] == "R/L",
            "clean_rtl_singleline": lambda r: r["clean_rtl_singleline"],
            "primary_length_at_least3": lambda r: r["clean_rtl_singleline"] and r["length"] >= 3,
        }
        result[name] = {
            "published_bases": len(ids), "matched_bases": sum(j["faces"] > 0 for j in joins),
            "matched_families": len({r["object_family_id"] for r in matched}), "matched_faces": len(matched), "joins": joins,
            "stages": {label: {"faces": sum(test(r) for r in matched),
                               "families": len({r["object_family_id"] for r in matched if test(r)})} for label, test in per_stage.items()},
            "face_length_counts": dict(Counter(r["length"] for r in matched)),
            "directions": dict(Counter(r["direction"] for r in matched)),
            "unknown_sign_faces": sum(r["has_unknown_sign"] for r in matched),
            "incomplete_faces": sum(not r["complete_observed"] for r in matched),
            "multiline_faces": sum(not r["single_line"] for r in matched),
            "blank_space_faces": sum(r["has_blank_space"] for r in matched),
        }
        assert sum(result[name]["face_length_counts"].values()) == len(matched)
        assert sum(result[name]["directions"].values()) == len(matched)
        assert len(ids) == len(joins)
    payload = {"created_utc": datetime.now(timezone.utc).isoformat(), "protocol": "experiments/2026-10-02-six-hour/context-audit/SOURCE-COHORT-PROTOCOL.md",
               "design_status": "post-availability-audit descriptive source cohort extension", "code_sha256": sha(Path(__file__)),
               "input": {"path": source.relative_to(ROOT).as_posix(), "sha256": sha(source)},
               "source": {"url": "https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf",
                          "printed_page": "l", "pdf_page_one_based": 9, "witness_pages": 17,
                          "retrieval_record": "experiments/2026-10-02-six-hour/context-audit/source-retrieval.json"},
               "cohorts": result}
    output.mkdir(parents=True)
    shutil.copyfile(Path(__file__), output / "code_snapshot.py")
    (output / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {f: v[f] for f in ["published_bases", "matched_bases", "matched_faces", "stages"]} for k, v in result.items()}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--source-cohorts", action="store_true", help="run the separately specified source cohort extension")
    args = parser.parse_args()
    if args.source_cohorts:
        source_cohorts(args.output)
        return
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite endpoint: {args.output}")
    inputs = {name: ROOT / "data/normalized" / name for name in ["lipi_observed_faces.jsonl", "lipi_clean_rtl_singleline.jsonl",
              "mayig_faces.jsonl", "lipi_summary.json", "mayig_summary.json"]}
    rows = read_jsonl(inputs["lipi_observed_faces.jsonl"])
    clean = read_jsonl(inputs["lipi_clean_rtl_singleline.jsonl"])
    mayig = read_jsonl(inputs["mayig_faces.jsonl"])
    groups = defaultdict(list)
    for r in rows:
        groups[r["object_family_id"]].append(r)
    assert len(rows) == 5680 and len(groups) == 4695 and len(clean) == 2930 and len(mayig) == 179
    assert len({r["record_id"] for r in rows}) == len(rows)
    checks = check_rules()
    fields = {f: field_audit(rows, groups, f) for f in CONTEXT}
    for f, a in fields.items():
        assert sum(a["row_statuses"].values()) == len(rows)
        assert sum(a["family_statuses"].values()) == len(groups)
    definitions = {
        "site_type_material": lambda r: all_fields(r, ["site", "type", "material"]),
        "site_excavation_area": lambda r: all_fields(r, ["site", "excavation-idno", "area-section"]),
        "site_area_depth_any_chronology": lambda r: all_fields(r, ["site", "area-section", "depth"]) and any_date(r),
        "site_room_depth_any_chronology": lambda r: all_fields(r, ["site", "room-grid", "depth"]) and any_date(r),
        "site_type_material_any_chronology": lambda r: all_fields(r, ["site", "type", "material"]) and any_date(r),
        "site_positive_two_dimensions_motif_reported": lambda r: all_fields(r, ["site", "horizontal(mm)", "vertical(mm)", "symbol"]),
        "site_positive_three_dimensions": lambda r: all_fields(r, ["site", "horizontal(mm)", "vertical(mm)", "thickness(mm)"]),
        "site_area_excavation_depth_room_any_chronology": lambda r: all_fields(r, ["site", "area-section", "excavation-idno", "depth", "room-grid"]) and any_date(r),
    }
    site_coverage = {}
    for site in sorted({r["site"] for r in rows}):
        members = [r for r in rows if r["site"] == site]
        site_coverage[site] = {"rows": len(members), "families": len({r["object_family_id"] for r in members}),
                               "reported_rows": {f: sum(available(f, field_value(r, f)) for r in members) for f in CONTEXT},
                               "joint_rows": {name: sum(test(r) for r in members) for name, test in definitions.items()}}
    result = {
        "protocol": "experiments/2026-10-02-six-hour/context-audit/PROTOCOL.md", "created_utc": datetime.now(timezone.utc).isoformat(),
        "code_sha256": sha(Path(__file__)), "inputs": {name: {"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p), "bytes": p.stat().st_size} for name, p in inputs.items()},
        "source_pins": {name: json.loads(inputs[name + "_summary.json"].read_text())["commit"] for name in ["lipi", "mayig"]},
        "counts": {"rows": len(rows), "families": len(groups), "clean_rtl_singleline_rows": len(clean), "eligible_length3_rows": sum(r["length"] >= 3 for r in clean)},
        "checks": checks, "field_availability": fields, "joint_availability": {name: joint(rows, groups, test) for name, test in definitions.items()},
        "site_coverage": site_coverage,
        "strata": {"material_by_site": field_by_strata(rows, ["site"], "material"), "type_by_site": field_by_strata(rows, ["site"], "type"),
                   "period_by_site_type": field_by_strata(rows, ["site", "type"], "period"),
                   "time_by_site_type": field_by_strata(rows, ["site", "type"], "time"),
                   "symbol_by_site_type": field_by_strata(rows, ["site", "type"], "symbol")},
        "component_audit": components([r for r in clean if r["length"] >= 3]),
        "identifier_audit": identifier_audit(rows, groups), "dimension_depth_audit": dimensions_audit(rows), "mayig": mayig_audit(mayig, rows),
        "evidence_basis": {"table_fields": "derivative catalogue values; source pins recorded",
                           "existing_primary_audit": "25 selected Mohenjo-daro objects, graphics/layout rather than general metadata verification",
                           "primary_context_followup": "recorded separately in source-assertions.json"},
        "availability_rule": {"unknown_labels": sorted(UNKNOWN), "hyphens_whitespace": "missing", "motif_none": "catalogued absence",
                              "millimetre_dimensions": "strictly positive numeric", "depth_zero": "reported value; datum unresolved"},
    }
    args.output.mkdir(parents=True)
    shutil.copyfile(Path(__file__), args.output / "code_snapshot.py")
    (args.output / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "counts": result["counts"], "joint_availability": result["joint_availability"], "components": result["component_audit"]["components"]}, indent=2))


if __name__ == "__main__":
    main()
