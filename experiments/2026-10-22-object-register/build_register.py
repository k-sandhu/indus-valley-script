"""Build the complete provisional family register without transcription payloads.

All record-level output stays in a new local data/raw directory.  Only the
aggregate reports selected by --summary-dir may enter the tracked package.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-22-object-register"
PILOT = ROOT / "experiments/2026-10-07-object-ledger"
sys.path.insert(0, str(PILOT))
from revision_builder import split_excavation
from validate_v2 import measurement_errors

INPUTS = {
    "lipi": "data/normalized/lipi_observed_faces.jsonl",
    "website": "data/normalized/indus_website_observed.jsonl",
    "mayig": "data/normalized/mayig_faces.jsonl",
    "images": "experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv",
    "cisi1": "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi1-basic-data.jsonl",
    "cisi2": "data/raw/2026-10-13-cisi-basic-data-full/assembled/cisi2-basic-data.jsonl",
    "cisi_flags": "experiments/2026-10-13-cisi-basic-data-full/object-flags.csv",
    "excavation": "experiments/2026-10-13-mackay-marshall-tables/run-2026-10-13/join-table.csv",
    "museums": "experiments/2026-10-13-museum-open-access/joins/join-table.csv",
    "pilot_original": "experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/corrected-original/ledger-without-transcription-payloads-or-images.json",
    "pilot_hash": "experiments/2026-10-07-object-ledger/revision-2026-10-07-v4/hash-ordered/ledger-without-transcription-payloads-or-images.json",
    "plate_audit": "experiments/2026-10-20-seal-legend-units/plate-audit/audit-table.csv",
    "inventory": "experiments/2026-10-12-data-inventory/run-2026-10-12/summary.json",
}
PLACEHOLDERS = {"", "-", "--", "- -", "?", "??", "???", "unknown"}
SAFE_METADATA = ["cisi", "region", "site", "area-section", "block-house", "room-grid", "depth", "time", "period", "phase", "type", "material", "color", "shape", "cross-section", "boss", "preservation", "condition", "complete", "sides", "horizontal(mm)", "vertical(mm)", "thickness(mm)", "symbol", "cult", "dir.", "h", "v", "th", "excavation-idno"]
REPEATED_FIELDS = {"measurement", "catalogue_identifier", "export_family_identifier", "museum_accession", "bibliographic_locator", "image_pointer", "rights_pointer", "face_count", "length_bin", "damage", "field_identifier"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for b in iter(lambda: handle.read(1048576), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    import csv
    p = ROOT / path
    with p.open(encoding="utf-8-sig", newline="") as handle:
        if p.suffix == ".csv":
            return list(csv.DictReader(handle))
        if p.suffix == ".jsonl":
            return [json.loads(line) for line in handle if line.strip()]
        return json.load(handle)


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lines(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def usable(value):
    return value is not None and str(value).strip().casefold() not in PLACEHOLDERS


def key(value):
    match = re.fullmatch(r"\s*([A-Za-z?]+)[-. ]*0*(\d+)(?:[A-Ca-c])?(?:\s*(?:bis|ter|quater))?\s*", str(value or ""))
    return f"{match[1].casefold()}-{int(match[2])}" if match else None


def number(value):
    try:
        n = float(value)
        return n if math.isfinite(n) and n > 0 else None
    except (ValueError, TypeError):
        return None


def dimension_present(value):
    if number(value) is not None:
        return True
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*", str(value or ""))
    return bool(m and max(float(m[1]), float(m[2])) > 0)


def missing(reason="not_recorded_in_integrated_sources"):
    return {"value": None, "assertion_ids": [], "missing_reason": reason}


class Register:
    def __init__(self):
        self.schema = read(str((HERE / "schema-v2.json").relative_to(ROOT)))
        self.inputs = {name: read(path) for name, path in INPUTS.items()}
        self.manifest = [{"source_id": name, "path": path, "sha256": sha(ROOT / path), "bytes": (ROOT / path).stat().st_size, "handling": "local-only source-derived records; aggregates may be tracked"} for name, path in INPUTS.items()]
        self.hashes = {r["path"]: r["sha256"] for r in self.manifest}
        self.data = {"schema_version": "2.0", "status": "Exploratory", "selection_sha256": sha(HERE / "PROTOCOL.md"), "sequence_policy": "No sign sequences; transcription payloads are local-only"}
        self.data.update({table: [] for table in self.schema["$defs"]})
        self.objects, self.contexts, self.faces = {}, {}, {}
        self.values, self.queue = [], []
        self.stats = {}
        self.by_key = collections.defaultdict(set)
        self.by_raw_key = collections.defaultdict(set)
        self.assertions = {}
        self.source_names = set()
        self.source_lookup = {}
        self.used_hashes = {}
        self.disagreements = []
        self.disagreement_index = collections.defaultdict(list)
        for p in sorted((ROOT / "data/raw/2026-10-13-cisi-basic-data-full/assembled/adjudication").glob("*.adjudication.json")):
            relative = p.relative_to(ROOT).as_posix()
            for i, row in enumerate(read(relative)):
                record = {"source_path": relative, "source_sha256": self.source_hash(relative), "row_index": i, "block": p.name.removesuffix(".adjudication.json"), **row}
                self.disagreements.append(record)
                self.disagreement_index[(record["block"], row["cisi"])].append(record)
        self.pilot_aliases = collections.defaultdict(list)
        self.known_post_index = {"H-603", "M-663", "M-1187", "M-1202"}

    def source(self, source_id, title=None, authors=None, year=None, url=None):
        if source_id in self.source_names:
            return
        self.source_names.add(source_id)
        row = {"id": source_id, "title": title or source_id, "authors": authors or ["Repository research contributors"], "year": year, "year_missing_reason": None if year else "source_year_retained_in_linked_manifest", "venue": "Held source or attributed project derivative", "url": url or INPUTS.get(source_id, "knowledge/provenance/SOURCES.md"), "version": self.hashes.get(INPUTS.get(source_id, ""), "inherited_source_record"), "access_status": "local_metadata_read; primary_not_reopened", "quoted_words": 0, "creator_role": "repository contributor"}
        self.data["sources"].append(row)
        self.source_lookup[source_id] = row

    def source_hash(self, path):
        if path not in self.hashes:
            self.hashes[path] = sha(ROOT / path)
            self.used_hashes[path] = self.hashes[path]
        return self.hashes[path]

    def fields(self, table):
        return {name: missing() for name in self.schema["$defs"][table]["properties"]["fields"]["required"]}

    def add(self, oid, field, value, source, path, record, original_field=None, raw=None, target=None, confidence="source-reported", method="source_field_extraction", page=None, join_status="source-family", status=None):
        if value is None:
            return None
        self.source(source)
        aid = f"A-{len(self.data['assertions']) + 1:07d}"
        loc = {"path": path, "record": str(record), "field": original_field or field, "page_or_url": str(page) if page else None, "page_missing_reason": None if page else "source_page_not_present_in_reused_record"}
        row = {"id": aid, "object_id": oid, "field": field, "value": value, "source_id": source, "locator": loc, "method": method, "confidence": confidence, "review_status": "not-expert-reviewed"}
        self.data["assertions"].append(row)
        self.assertions[aid] = row
        uncertainty = status if status in {"implausible", "unresolved-reader-disagreement"} else "bracketed" if (isinstance(raw if raw is not None else value, str) and "[" in (raw if raw is not None else value)) or status == "uncertain" else "candidate_identity" if confidence == "candidate" else None
        vstatus = "inferred" if confidence == "derived" else "catalogued"
        self.values.append({"assertion_id": aid, "object_id": oid, "field": field, "raw_value": value if raw is None else raw, "normalized_value": value, "value_status": vstatus, "uncertainty": uncertainty, "source_id": source, "source_sha256": self.source_hash(path), "locator": loc, "join_status": join_status})
        if target is not None and field in target and confidence != "candidate":
            target[field]["assertion_ids"].append(aid)
            if target[field]["value"] is None:
                target[field]["value"] = value
                target[field]["missing_reason"] = None
        return aid

    def alias(self, oid, scheme, value, aid, uncertain=False):
        if not aid:
            return
        self.data["identifiers"].append({"id": f"ID-{len(self.data['identifiers']) + 1:06d}", "object_id": oid, "scheme": scheme, "value": str(value), "status": "candidate" if uncertain else "confirmed", "assertion_id": aid, "edition": missing("source_edition_is_recorded_by_assertion_source")})

    def measurement(self, oid, dim, value, source, path, record, raw, original_field, method="reported_numeric_mm"):
        if value is None:
            return
        v = {"dimension": dim, "value": value, "unit": "mm"}
        implausible = value > 1000
        aid = self.add(oid, "measurement", v, source, path, record, original_field, raw=raw, target=None if implausible else self.objects[oid]["fields"], method=method, status="implausible" if implausible else "present")
        if implausible:
            self.queue.append({"source_id": source, "external_id": str(record), "object_id": oid, "field": original_field, "value": value, "unit": "mm", "reason": "reported_dimension_exceeds_pilot_1000mm_plausibility_bound; retained_without_acceptance"})
        self.data["measurements"].append({"id": f"MEAS-{len(self.data['measurements']) + 1:06d}", "object_id": oid, **v, "method": missing("physical_measurement_method_not_reported"), "assertion_id": aid})

    def relation(self, oid, source, external, path, record, status="confirmed", method="inherited_join"):
        aid = self.add(oid, "source_identity_link", external, source, path, record, method=method, confidence="candidate" if status == "candidate" else "identifier-supported", join_status=status)
        self.data["relationships"].append({"id": f"REL-{len(self.data['relationships']) + 1:06d}", "object_id": oid, "source_id": source, "external_record": external, "relation": "same_reported_object" if status == "confirmed" else "possible_same_object", "status": status, "method": method, "assertion_id": aid})

    def base(self):
        self.source("lipi", "Lipi observational export", ["yajnadevam"], url="https://github.com/yajnadevam/lipi/tree/fc8813a52e183d19c441631dc26c33a4dccbea39")
        families = collections.defaultdict(list)
        for face in self.inputs["lipi"]:
            families[str(face["object_family_id"])].append(face)
        for family, faces in sorted(families.items(), key=lambda x: int(x[0])):
            oid = "LIPI:" + family
            obj = {"id": oid, "selection_key": family, "identity_status": "source-reported", "fields": self.fields("objects")}
            ctx = {"id": "CTX:" + family, "object_id": oid, "fields": self.fields("contexts")}
            self.objects[oid], self.contexts[oid] = obj, ctx
            self.data["objects"].append(obj)
            self.data["contexts"].append(ctx)
            self.add(oid, "face_count", len(faces), "lipi", INPUTS["lipi"], "object_family_id=" + family, target=obj["fields"], method="count_source_rows")
            self.add(oid, "export_family_identifier", family, "lipi", INPUTS["lipi"], "object_family_id=" + family)
            for face in faces:
                rec, m = str(face["record_id"]), face["metadata"]
                fid = "LIPI:" + rec
                skey = key(face["source_cisi"])
                if skey:
                    self.by_key[skey].add(oid)
                self.by_raw_key[str(face["source_cisi"]).strip()].add(oid)
                f = {"face_id": fid, "object_id": oid, "source_record_id": rec, "source_cisi_raw": face["source_cisi"], "catalogue_key": skey, "source_id": "lipi", "source_sha256": self.hashes[INPUTS["lipi"]], "physical_identity_status": "provisional", "identity_status": "provisional-export-family", "image_links": [], "conflicts": [], "exposure_status": "unreviewed"}
                self.faces[rec] = f
                sf = self.fields("surfaces")
                for field, value in [("label", rec), ("orientation", face.get("direction")), ("arrangement", "single_line" if face["single_line"] else "multiple_or_unresolved_lines")]:
                    if usable(value):
                        self.add(oid, field, value, "lipi", INPUTS["lipi"], "record_id=" + rec, target=sf)
                sf["alignment"] = missing("source_row_retained; physical_side_and_cross_source_alignment_unreviewed")
                self.data["surfaces"].append({"id": fid, "object_id": oid, "fields": sf})
                mappings = {"type": ("object_type", obj["fields"]), "material": ("material", obj["fields"]), "cisi": ("catalogue_identifier", obj["fields"]), "site": ("site", ctx["fields"]), "region": ("region", ctx["fields"]), "area-section": ("area", ctx["fields"]), "room-grid": ("room_grid", ctx["fields"]), "time": ("period_label", ctx["fields"]), "phase": ("stratum_phase", ctx["fields"]), "period": ("stratum_phase", ctx["fields"])}
                for original in SAFE_METADATA:
                    raw = m.get(original)
                    field, target = mappings.get(original, ("metadata." + original, None))
                    is_dimension = original in {"horizontal(mm)", "vertical(mm)", "thickness(mm)"}
                    if usable(raw) and (not is_dimension or dimension_present(raw)):
                        aid = self.add(oid, field, str(raw).strip(), "lipi", INPUTS["lipi"], "record_id=" + rec, "metadata." + original, raw=raw, target=target)
                        if original == "cisi":
                            self.alias(oid, "Lipi_reported_CISI", str(raw).strip(), aid)
                    else:
                        self.values.append({"assertion_id": None, "object_id": oid, "field": field, "raw_value": raw, "normalized_value": None, "value_status": "unknown", "missing_reason": "placeholder_or_absent_source_value", "source_id": "lipi", "source_sha256": self.hashes[INPUTS["lipi"]], "locator": {"path": INPUTS["lipi"], "record": "record_id=" + rec, "field": "metadata." + original}, "join_status": "source-family"})
                raw = m.get("excavation-idno")
                if usable(raw):
                    self.add(oid, "export_excavation_identifier", raw, "lipi", INPUTS["lipi"], "record_id=" + rec, "metadata.excavation-idno", target=obj["fields"])
                    registration, citation, lot = split_excavation(raw)
                    for field, value, target in [("excavation_identifier", registration, obj["fields"]), ("bibliographic_locator", citation, obj["fields"]), ("lot_identifier", lot, ctx["fields"])]:
                        if value:
                            aid = self.add(oid, field, value, "lipi", INPUTS["lipi"], "record_id=" + rec, "metadata.excavation-idno", raw=raw, target=target, confidence="derived", method="pilot_v2_split_registration_citation_and_lot")
                            if field == "excavation_identifier":
                                self.alias(oid, "export_registration_string", value, aid)
                for dim, original in [("horizontal", "horizontal(mm)"), ("vertical", "vertical(mm)"), ("thickness", "thickness(mm)")]:
                    self.measurement(oid, dim, number(m.get(original)), "lipi", INPUTS["lipi"], "record_id=" + rec, m.get(original), "metadata." + original)
        self.stats["lipi"] = {"rows": len(self.faces), "families": len(self.objects), "cisi_raw_usable": sum(any(usable(f["source_cisi"]) for f in fs) for fs in families.values()), "any_positive_dimension_including_ranges": sum(any(dimension_present(f["metadata"].get(k)) for f in fs for k in ["horizontal(mm)", "vertical(mm)", "thickness(mm)"]) for fs in families.values())}

    def cisi(self):
        flags = {(r["volume"], r["cisi"]): r for r in self.inputs["cisi_flags"]}
        for source in ("cisi1", "cisi2"):
            joined, n = set(), 0
            for i, row in enumerate(self.inputs[source]):
                flag = flags.get((source, row["cisi"]))
                if not flag or flag["join"] != "one-family":
                    self.queue.append({"source_id": source, "source_path": INPUTS[source], "row_index": i, "external_id": row["cisi"], "reason": "catalogue_cross_reference" if not flag else flag["join"], "candidate_families": flag.get("lipi_family", "") if flag else ""})
                    continue
                oid = "LIPI:" + flag["lipi_family"]
                if oid not in self.objects:
                    raise ValueError("CISI join refers to an absent family")
                joined.add(oid); n += 1
                rec = "cisi=" + row["cisi"]
                page = f"{source}; printed {row['printed_page']}; PDF {row['pdf_page']}"
                adjudications = self.disagreement_index.get((row.get("block"), row["cisi"]), [])
                unresolved = {a["column"] for a in adjudications if a.get("auto") or a.get("outcome") in {"undecidable", "absent"}}
                identity_disputed = False
                for a in adjudications:
                    if a["column"] != "col1" or not (a.get("auto") or a.get("outcome") == "undecidable"): continue
                    ids = [re.search(r"([A-Za-z?]+)[-. ]*0*(\d+)", str(a.get(k, ""))) for k in ["pass1", "pass2"]]
                    if not all(ids) or (ids[0][1].casefold(), int(ids[0][2])) != (ids[1][1].casefold(), int(ids[1][2])): identity_disputed = True
                self.relation(oid, source, row["cisi"], INPUTS[source], rec, status="candidate" if identity_disputed else "confirmed", method="inherited_unique_CISI_family_join; reader_identity_dispute_retained" if identity_disputed else "inherited_unique_CISI_family_join")
                self.add(oid, "cisi_adjudication_metadata", {k: row.get(k) for k in ["block", "uncertain_columns", "blind_adjudicated_columns", "rechecked_columns"]} | {"unresolved_columns_from_decision_files": sorted(unresolved), "identity_disputed": identity_disputed}, source, INPUTS[source], rec, "block,uncertain_columns,blind_adjudicated_columns,rechecked_columns", page=page, method="retained_assembly_metadata_with_decision_file_audit")
                for a in adjudications:
                    self.add(oid, "cisi_reader_disagreement." + a["column"], {k: a.get(k) for k in ["pass1", "pass2", "final", "outcome", "note", "auto"]}, source, a["source_path"], "row_index=" + str(a["row_index"]), "pass1,pass2,final,outcome,note,auto", page=page, status="unresolved-reader-disagreement" if a["column"] in unresolved else None, join_status="candidate-identity" if identity_disputed else "inherited-one-family")
                p, fields = row["parsed"], self.objects[oid]["fields"]
                specifications = [("fc_number", "col2_fc", bool(p["fc_number"]), None), ("excavation_identifier", "col3_excavation", p["excavation_usable"], fields), ("museum_accession", "col4_museum", p["museum_number_usable"], fields), ("holding", "col4_museum", p["institution_usable"], fields)]
                for field, original, present, target in specifications:
                    if not present:
                        continue
                    raw = row[original]
                    value = p["holding_institutions"] if field == "holding" else raw
                    short = original.split("_")[0]
                    disputed = identity_disputed or short in unresolved or original in row["uncertain_columns"] or "[" in raw
                    aid = self.add(oid, field, value, source, INPUTS[source], rec, original, raw=raw, target=None if disputed else target, page=page, join_status="candidate-identity" if identity_disputed else "inherited-one-family", status="unresolved-reader-disagreement" if short in unresolved else "uncertain" if disputed else "present")
                    if field in {"fc_number", "museum_accession"}:
                        self.alias(oid, source + ":" + field, value, aid, disputed)
                # Preserve each printed column including every bracketed candidate.
                for original in ["col1", "col2_fc", "col3_excavation", "col4_museum", "col5_photographs"]:
                    if usable(row[original]):
                        self.add(oid, "cisi_raw." + original, row[original], source, INPUTS[source], rec, original, page=page, join_status="inherited-one-family")
            self.stats[source] = {"rows": len(self.inputs[source]), "joined_rows": n, "families": len(joined)}
        self.stats["cisi_reader_decisions"] = {"rows": len(self.disagreements), "automatically_merged": sum(bool(r.get("auto")) for r in self.disagreements), "undecidable": sum(r.get("outcome") == "undecidable" for r in self.disagreements), "accepted_cell_policy": "Exclude automatic merges, undecidable cells, bracketed cells and disputed identities; retain original candidates and merged assertions."}

    def external(self):
        for source in ("website", "mayig"):
            joined, n = set(), 0
            for i, row in enumerate(self.inputs[source]):
                external = row.get("source_cisi") if source == "website" else row["object_family_id"]
                candidates = self.by_raw_key.get(str(external).strip(), set()) if source == "website" else self.by_key.get(key(external), set())
                if len(candidates) != 1:
                    self.queue.append({"source_id": source, "row_index": i, "external_id": str(external), "reason": "no_unique_catalogue_join", "candidate_families": sorted(candidates)})
                    continue
                oid = next(iter(candidates)); joined.add(oid); n += 1
                rec = "record_id=" + str(row["record_id"])
                self.relation(oid, source, str(row["record_id"]), INPUTS[source], rec, method="exact_catalogue_string" if source == "website" else "unique_catalogue_base; surface_alignment_unreviewed")
                if source == "website":
                    m, fields = row["metadata"], self.objects[oid]["fields"]
                    for field, original in [("museum_accession", "MUSEUM"), ("material", "MATERIAL")]:
                        if usable(m.get(original)):
                            aid = self.add(oid, field, m[original], source, INPUTS[source], rec, "metadata." + original, target=fields, join_status="unique-exact-catalogue")
                            if field == "museum_accession": self.alias(oid, "website:MUSEUM", m[original], aid)
                    # Website numeric sizes have unresolved unit lineage; retain raw only.
                    for original in ["WIDTH", "HEIGHT", "THICKNESS"]:
                        if number(m.get(original)):
                            self.add(oid, "website_raw." + original, m[original], source, INPUTS[source], rec, "metadata." + original, method="unit_not_assumed")
            self.stats[source] = {"rows": len(self.inputs[source]), "joined_rows": n, "families": len(joined)}

    def excavation(self):
        joined = set()
        for i, row in enumerate(self.inputs["excavation"]):
            oid = "LIPI:" + row["lipi_family_id"]
            if oid not in self.objects:
                raise ValueError("excavation join refers to absent family")
            joined.add(oid); source = "excavation"
            fields, ctx = self.objects[oid]["fields"], self.contexts[oid]["fields"]
            rec = "source_row_id=" + row["source_row_id"]
            self.relation(oid, source, row["source_row_id"], INPUTS[source], rec, method="inherited_" + row["disposition"] + ":" + row["basis"])
            for field, original, target in [("field_identifier", "field_no", fields), ("material", "material", fields), ("area", "area", ctx), ("room_grid", "locus", ctx), ("excavation_level_ft", "level_ft", None), ("excavation_level_datum", "level_reference", None), ("excavation_type_raw", "seal_type", None), ("excavation_size_inches_raw", "size_in_as_printed", None)]:
                if usable(row[original]):
                    aid = self.add(oid, field, row[original], source, INPUTS[source], rec, original, target=target, page=f"{row['source']} printed {row['printed_page']}", join_status="inherited-" + row["disposition"])
                    if field == "field_identifier": self.alias(oid, row["source"] + ":field_number", row[original], aid)
            self.add(oid, "bibliographic_locator", row["source"] + ":" + row["catalogue_no"], source, INPUTS[source], rec, "source,catalogue_no", target=fields, page="printed " + row["printed_page"])
            # Printed units and source axes remain visible in the method and raw value.
            size = row["size_in_as_printed"].replace(" ", "")
            parts = re.split(r"[xX×]", size)
            if len(parts) in (2, 3) and all(number(p) for p in parts):
                for dim, n in zip(["dimension_1", "dimension_2", "dimension_3"], parts):
                    self.measurement(oid, dim, round(float(n) * 25.4, 8), source, INPUTS[source], rec, row["size_in_as_printed"], "size_in_as_printed", "printed_inches_times_25.4; unlabelled_axes")
        self.stats["excavation"] = {"rows": len(self.inputs["excavation"]), "families": len(joined), "print_corrections_applied": False}

    def museums(self):
        joined = set(); n = 0
        for i, row in enumerate(self.inputs["museums"]):
            oid = "LIPI:" + row["family"]
            if row["joined"] != "True" or oid not in self.objects:
                self.queue.append({"source_id": "museums", "row_index": i, "external_id": row["museum"] + "|" + row["accession"], "reason": row["cls"], "candidate_families": row["candidates_spec"]})
                continue
            joined.add(oid); n += 1
            rec = "row_index=" + str(i)
            self.relation(oid, "museums", row["museum"] + "|" + row["accession"], INPUTS["museums"], rec, method="inherited_" + row["method"])
            for field, original in [("museum_accession", "accession"), ("holding", "museum")]:
                aid = self.add(oid, field, row[original], "museums", INPUTS["museums"], rec, original, target=self.objects[oid]["fields"], join_status="inherited-" + row["cls"])
                if field == "museum_accession": self.alias(oid, row["museum"] + ":accession", row[original], aid)
            if row["conflicts"]:
                self.add(oid, "museum_join_conflict", row["conflicts"], "museums", INPUTS["museums"], rec, "conflicts")
        self.stats["museums"] = {"rows": len(self.inputs["museums"]), "joined_rows": n, "families": len(joined), "fields": ["accession", "holding", "join_conflicts"], "full_harvest_payload_imported": False}

    def images(self):
        objects = set(); links = 0; image_rows = {}
        for i, row in enumerate(self.inputs["images"]):
            rec = row["record_id"]
            if rec not in self.faces:
                raise ValueError("image link refers to absent face")
            face = self.faces[rec]; oid = face["object_id"]
            if oid != "LIPI:" + row["object_family_id"]:
                raise ValueError("image face/family disagreement")
            path = "data/lipi/public/seal_images/" + row["file"]
            if not (ROOT / path).is_file():
                self.queue.append({"source_id": "images", "row_index": i, "external_id": row["file"], "reason": "indexed_image_missing_locally"})
                continue
            objects.add(oid); links += 1
            note = row["flags"]
            post_audit = row["cisi"] in self.known_post_index
            if post_audit:
                note += "; later_plate_audit_requires_link_review"
            link = {"path": path, "sha256": row["sha256"], "kind": row["kind"], "side_match": row["relation"] == "face-side" and not post_audit, "relation": row["relation"], "note": note, "source_path": INPUTS["images"], "source_record": "row_index=" + str(i), "source_id": "images", "source_sha256": self.hashes[INPUTS["images"]], "join_status": "needs-later-audit-review" if post_audit else "inherited-face-index"}
            face["image_links"].append(link)
            if post_audit and "later_plate_audit_requires_link_review" not in face["conflicts"]:
                face["conflicts"].append("later_plate_audit_requires_link_review")
            ikey = (oid, path)
            if ikey not in image_rows:
                iid = f"IMG-{len(image_rows) + 1:06d}"; rid = "RIGHTS:" + iid
                image_rows[ikey] = iid
                self.source("images")
                self.data["rights"].append({"id": rid, "source_id": "images", "asset_ref": iid, "status": "rights-unverified", "license": missing("CISI_image_reuse_not_cleared"), "scope": "CISI image crop", "disposition": "local-only", "notice_locator": "knowledge/provenance/REDISTRIBUTION.md"})
                self.data["images"].append({"id": iid, "object_id": oid, "source_id": "images", "rights_id": rid, "url": path, "locator": INPUTS["images"] + "#row_index=" + str(i), "kind": row["kind"], "inspection_status": "inherited_image_index; see_face_sidecar_for_alignment", "surface_alignment": missing("individual_face_relation_retained_in_faces_sidecar")})
                self.add(oid, "image_pointer", iid, "images", INPUTS["images"], "row_index=" + str(i), "file", target=self.objects[oid]["fields"])
        self.stats["images"] = {"rows": len(self.inputs["images"]), "face_links": links, "families": len(objects), "object_image_pairs": len(image_rows), "later_audit_object_keys_quarantined_from_side_match": sorted(self.known_post_index)}

    def pilots(self):
        # Transfer metadata assertions with their original provenance. Alternate
        # transcriptions and image alignments require a separate face concordance.
        seen = set(); joined = set(); imported = 0; catalogue_only = set()
        allowed = set(self.fields("objects")) | set(self.fields("contexts")) | {"measurement", "identifier_edition"}
        allowed -= {"image_pointer", "rights_pointer", "face_count", "length_bin", "damage"}
        for name in ("pilot_original", "pilot_hash"):
            pilot = self.inputs[name]
            mapping = {}
            for obj in pilot["objects"]:
                aliases = {str(a["value"]) for a in pilot["assertions"] if a["object_id"] == obj["id"] and a["field"] == "export_family_identifier"}
                if len(aliases) == 1 and "LIPI:" + next(iter(aliases)) in self.objects:
                    oid = "LIPI:" + next(iter(aliases)); mapping[obj["id"]] = oid; joined.add(oid)
                    self.pilot_aliases[oid].append({"source_id": name, "id": obj["id"], "selection_key": obj["selection_key"]})
                else:
                    catalogue_only.add(obj["selection_key"])
                    self.queue.append({"source_id": name, "external_id": obj["selection_key"], "reason": "pilot_catalogue_only_object_not_in_Lipi_base"})
            for source in pilot["sources"]:
                sid = "pilot:" + source["id"]
                if sid not in self.source_names:
                    self.source_names.add(sid)
                    self.data["sources"].append(dict(source, id=sid))
            for a in pilot["assertions"]:
                if a["object_id"] not in mapping or a["field"] not in allowed:
                    continue
                oid = mapping[a["object_id"]]; loc = a["locator"]
                fingerprint = (oid, a["field"], json.dumps(a["value"], sort_keys=True), a["source_id"], json.dumps(loc, sort_keys=True))
                if fingerprint in seen: continue
                seen.add(fingerprint)
                target = self.objects[oid]["fields"] if a["field"] in self.objects[oid]["fields"] else self.contexts[oid]["fields"]
                self.add(oid, a["field"], a["value"], "pilot:" + a["source_id"], loc["path"], loc["record"], loc["field"], target=target, confidence=a["confidence"], method="inherited_pilot_v2: " + a["method"], page=loc["page_or_url"], join_status="pilot-export-family")
                imported += 1
        self.stats["pilot_enrichment"] = {"families": len(joined), "assertions": imported, "catalogue_only_keys_queued": len(catalogue_only), "images_and_alternate_transcriptions_imported": False}

    def finish(self):
        output_objects, missing_values = [], []
        aliases = collections.defaultdict(list)
        for row in self.data["identifiers"]:
            aliases[row["object_id"]].append({"scheme": row["scheme"], "value": row["value"], "status": row["status"], "assertion_id": row["assertion_id"]})
        faces_by_object = collections.defaultdict(list)
        for row in self.faces.values(): faces_by_object[row["object_id"]].append(row["face_id"])
        conflict_count = 0
        for oid, obj in self.objects.items():
            states, conflicts = {}, []
            for scope, fields in [("object", obj["fields"]), ("context", self.contexts[oid]["fields"])]:
                for name, cell in fields.items():
                    vals = {json.dumps(self.assertions[aid]["value"], sort_keys=True, ensure_ascii=False) for aid in cell["assertion_ids"]}
                    value_status = "unknown" if cell["value"] is None else "catalogued"
                    uncertainty = "bracketed" if isinstance(cell["value"], str) and "[" in cell["value"] else None
                    if cell["assertion_ids"] and all(self.assertions[a]["confidence"] == "derived" for a in cell["assertion_ids"]): value_status = "inferred"
                    if len(vals) > 1 and name not in REPEATED_FIELDS:
                        value_status = "conflicting"; conflicts.append(scope + "." + name)
                    states[scope + "." + name] = {"value": cell["value"], "value_status": value_status, "uncertainty": uncertainty, "assertion_ids": cell["assertion_ids"], "missing_reason": cell["missing_reason"]}
                    if cell["value"] is None:
                        missing_values.append({"object_id": oid, "scope": scope, "field": name, "value_status": "unknown", "missing_reason": cell["missing_reason"]})
            conflict_count += bool(conflicts)
            output_objects.append({"object_id": oid, "source_family_id": obj["selection_key"], "physical_identity_status": "provisional", "face_ids": faces_by_object[oid], "aliases": aliases[oid], "pilot_aliases": self.pilot_aliases[oid], "fields": states, "conflicts": conflicts, "exposure_status": "unreviewed", "source_id": "lipi", "source_sha256": self.hashes[INPUTS["lipi"]], "dependency_group_status": "not_constructed"})
        self.output_objects = output_objects
        self.missing_values = missing_values
        for row in self.queue:
            if row["source_id"] in INPUTS:
                path = INPUTS[row["source_id"]]
                row.setdefault("source_path", path)
                row.setdefault("source_sha256", self.hashes[path])
            row.setdefault("join_status", "unresolved")
        self.coverage = {"population": {"provisional_objects": len(self.objects), "exported_faces": len(self.faces), "adjudicated_physical_objects": 0}, "baseline": self.stats["lipi"], "adapters": self.stats, "tables": {k: len(v) for k, v in self.data.items() if isinstance(v, list)}, "objects_with_unreconciled_field_variants": conflict_count, "field_coverage": {scope + "." + name: sum(obj["fields"][scope + "." + name]["value_status"] != "unknown" for obj in output_objects) for scope, table in [("object", "objects"), ("context", "contexts")] for name in self.fields(table)}, "exposure": {"unreviewed": len(self.objects), "eligible_fresh": 0}, "unresolved_join_queue_rows": len(self.queue), "deferred_adapters": ["Full museum harvest payloads beyond inherited pilot enrichment", "CISI photographic references linked to specific plates", "Physical face alignment for Mayig and pilot alternate transcriptions", "Helsinki occurrence concordance", "Post-catalogue objects and catalogue-only pilot objects as separate physical population", "Later plate corrections resolved image by image", "Reviewed exposure and dependency-group history"], "counting_notes": ["A family is provisional; aliases never merge families.", "Multiple source spellings count as unreconciled variants, not established errors.", "CISI accession coverage includes bracketed candidates; raw cells are retained.", "Lipi dimension baseline includes positive printed ranges; register numeric measurements retain only exact positive scalars.", "Older website numeric dimensions are retained raw because source units were not audited here."]}

    def build(self):
        for fn in (self.base, self.cisi, self.external, self.excavation, self.museums, self.images, self.pilots, self.finish):
            fn()
        return self


def validate(reg):
    import jsonschema
    errors = [e.json_path + ": " + e.message for e in jsonschema.Draft202012Validator(reg.schema).iter_errors(reg.data)]
    data = reg.data
    maps = {k: {r["id"]: r for r in rows} for k, rows in data.items() if isinstance(rows, list)}
    all_ids = []
    for table, rows in data.items():
        if isinstance(rows, list):
            ids = [r["id"] for r in rows]; all_ids += ids
            if len(ids) != len(set(ids)): errors.append(table + ":duplicate_id")
    if len(all_ids) != len(set(all_ids)): errors.append("id_reused_across_tables")
    contexts = collections.Counter(r["object_id"] for r in data["contexts"])
    if set(contexts) != set(maps["objects"]) or any(n != 1 for n in contexts.values()): errors.append("context_object_closure")
    face_counts = collections.Counter(r["object_id"] for r in data["surfaces"])
    for oid, o in maps["objects"].items():
        if o["fields"]["face_count"]["value"] != face_counts[oid]: errors.append("face_count:" + oid)
    def inspect(value, owner=None):
        if isinstance(value, dict):
            if set(value) == {"value", "assertion_ids", "missing_reason"}:
                if value["value"] is None and not value["missing_reason"]: errors.append("missing_reason")
                source_values = []
                for aid in value["assertion_ids"]:
                    a = maps["assertions"].get(aid)
                    if not a: errors.append("broken_assertion:" + aid); continue
                    if owner and a["object_id"] != owner: errors.append("foreign_object_assertion:" + aid)
                    if a["confidence"] == "candidate": errors.append("candidate_in_accepted_cell:" + aid)
                    source_values.append(a["value"])
                if value["value"] is not None and value["value"] not in source_values: errors.append("chosen_value_without_assertion")
            for v in value.values(): inspect(v, owner)
        elif isinstance(value, list):
            for v in value: inspect(v, owner)
    for table, rows in data.items():
        if not isinstance(rows, list): continue
        for row in rows:
            owner = row.get("object_id") or (row["id"] if table == "objects" else None)
            inspect(row, owner)
            for field, target in [("object_id", "objects"), ("source_id", "sources"), ("assertion_id", "assertions"), ("rights_id", "rights")]:
                if field in row and row[field] not in maps[target]: errors.append("broken_" + field + ":" + row["id"])
            if table == "assertions" and not (ROOT / row["locator"]["path"]).is_file(): errors.append("missing_source_path:" + row["id"])
            if table == "measurements":
                measurement_issues = measurement_errors({k: row[k] for k in ["dimension", "value", "unit"]}, row["id"])
                # Preserve an outlier as catalogued while withholding acceptance.
                errors += [e for e in measurement_issues if "plausibility bound" not in e]
                if any("plausibility bound" in e for e in measurement_issues) and not any(v["assertion_id"] == row["assertion_id"] and v.get("uncertainty") == "implausible" for v in reg.values):
                    errors.append("unquarantined_implausible_measurement:" + row["id"])
    if len(maps["objects"]) != 4695 or len(maps["surfaces"]) != 5680: errors.append("base_population_changed")
    if reg.stats["lipi"]["cisi_raw_usable"] != 4075: errors.append("CISI_baseline_changed")
    if reg.stats["lipi"]["any_positive_dimension_including_ranges"] != 3598: errors.append("dimension_baseline_changed")
    if any(o["exposure_status"] != "unreviewed" for o in reg.output_objects): errors.append("unsupported_freshness_assignment")
    canonical = {"observed", "catalogued", "inferred", "unknown", "conflicting", "not-applicable"}
    if any(v.get("value_status") not in canonical for v in reg.values): errors.append("noncanonical_value_status")
    for obj in reg.output_objects:
        if any(f["value_status"] not in canonical for f in obj.get("fields", {}).values()): errors.append("noncanonical_compact_field_status")
    return sorted(set(errors))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary-dir", required=True)
    args = parser.parse_args()
    out, summary = Path(args.out).resolve(), Path(args.summary_dir).resolve()
    if not out.is_relative_to(RAW.resolve()) or out == RAW.resolve(): raise ValueError("out must be a new child of the owned local data directory")
    if not summary.is_relative_to(HERE) or summary == HERE: raise ValueError("summary-dir must be a new child of the owned experiment")
    if out.exists() or summary.exists(): raise ValueError("existing output refused")
    reg = Register().build()
    errors = validate(reg)
    if errors: raise ValueError(json.dumps(errors, ensure_ascii=True))
    out.mkdir(parents=True); summary.mkdir(parents=True)
    dump(out / "register-v2.json", reg.data)
    lines(out / "objects.jsonl", reg.output_objects)
    lines(out / "faces.jsonl", reg.faces.values())
    lines(out / "assertion-values.jsonl", reg.values)
    lines(out / "missing-values.jsonl", reg.missing_values)
    lines(out / "join-queue.jsonl", reg.queue)
    lines(out / "cisi-reader-decisions.jsonl", reg.disagreements)
    dump(summary / "coverage.json", reg.coverage)
    dump(summary / "source-manifest.json", {"inputs": reg.manifest, "inherited_assertion_sources": [{"path": p, "sha256": h} for p, h in sorted(reg.used_hashes.items())], "schema_sha256": sha(HERE / "schema-v2.json"), "protocol_sha256": sha(HERE / "PROTOCOL.md"), "code_sha256": sha(Path(__file__)), "input_lineage": "Exact bytes of held inputs. Primary-source and acquisition details remain in cited source packages."})
    dump(summary / "validation.json", {"status": "verified-computation", "schema": "unchanged pilot v2", "errors": errors, "objects": len(reg.objects), "faces": len(reg.faces), "schema_and_reference_checks": "passed", "original_pilot_validator_scope": "Pilot cardinality fixed at 200; unchanged schema plus adapted closure/reference checks used here.", "output_hashes": {p.name: sha(p) for p in sorted(out.iterdir())}, "output_local_dir": str(out.relative_to(ROOT)).replace("\\", "/")})
    print(json.dumps({"status": "passed", "objects": len(reg.objects), "faces": len(reg.faces), "assertions": len(reg.data["assertions"]), "out": str(out), "summary": str(summary)}))


if __name__ == "__main__":
    main()
