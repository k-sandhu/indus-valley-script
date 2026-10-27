"""Review a fixed candidate cohort using identity and access metadata only."""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-22-candidate-identity-exposure"
BASE = "experiments/2026-10-21-post-catalogue-finds/"
PATHS = {
    "queue": "data/raw/2026-10-22-unit-readiness/run-register-v2/candidate-cohort-queue.csv",
    "inventory": BASE + "objects.csv",
    "sources": BASE + "matching/source-register.csv",
    "source_variants": BASE + "matching/source-register-variants.csv",
    "decisions": BASE + "join-decisions.csv",
    "duplicates_cross": BASE + "matching/cross-part-duplicates.csv",
    "duplicates_same": BASE + "matching/same-part-duplicates.csv",
    "logs": BASE + "exposure-log.csv",
    "mechanical": BASE + "verification/exposure-mechanical.csv",
    "incidents": BASE + "verification/exposure-incidents.json",
    "incidents_v2": BASE + "verification/exposure-incidents-v2.json",
    "register": "data/raw/2026-10-22-object-register/run-v2/objects.jsonl",
    "retrospective": BASE + "RETROSPECTIVE-CODEX.md",
    "verification_retrospective": BASE + "verification/RETROSPECTIVE.md",
    "workflow_n": BASE + "extraction/N/finalize_N.py",
    "workflow_d": BASE + "extraction/D/build_D.py",
    "workflow_verification": BASE + "verification/write_notes.py",
    "workflow_page_index": BASE + "verification/audit.py",
    "workflow_content": BASE + "verification/search_and_content.py",
    "identity_rules": BASE + "matching/identity_io.py",
    "identity_tests": BASE + "matching/selftest_3.py",
    "original_verification_log": BASE + "verification/exposure-log.csv",
    "original_verification_log_v2": BASE + "verification/exposure-log-v2.csv",
}
IDENTITY_COLUMNS = ["row_id", "site", "local_site_label", "registration", "other_numbers", "primary_publication", "publication_year", "page", "pdf_page", "plate_or_figure", "other_publications", "possible_duplicate_of", "cisi_in_baseline", "local_match", "local_family_ids", "match_basis", "context_join_family", "catalogue_status", "inscription_status", "extracted_by", "reviewed_by"]
CANONICAL_STATUS = {"observed", "catalogued", "inferred", "unknown", "conflicting", "not-applicable"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1048576), b""): h.update(b)
    return h.hexdigest()


def read_csv(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_lines(path, rows):
    with Path(path).open("w", encoding="utf-8", newline="\n") as f:
        for row in rows: f.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def write_csv(path, rows):
    keys = list(rows[0]) if rows else []
    with Path(path).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader(); writer.writerows(rows)


def stable_id(prefix, value):
    return prefix + hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def normalize_registration(value):
    """Whole identifier only; numeric components and namespaces stay separate."""
    text = unicodedata.normalize("NFKC", str(value or "")).strip().upper()
    if not text or any(c in text for c in "[]?;|/()") or not re.fullmatch(r"[A-Z0-9 ._\-]+", text): return None
    parts = re.findall(r"[A-Z]+|\d+", text)
    if not parts or not any(p.isdigit() for p in parts) or len(parts) > 8: return None
    if any(p in {"FIG", "FIGURE", "PL", "PLATE", "SEE", "LOT", "CATALOGUE"} for p in parts): return None
    return tuple(str(int(p)) if p.isdigit() else p for p in parts)


def normalize_site(value):
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


def site_registration(site, value):
    """Remove only two documented site/project namespaces; retain all numbers."""
    parts = normalize_registration(value)
    if not parts: return None
    site = normalize_site(site)
    prefixes = [("DHR",)] if site == "dholavira" else [("RIHN", "INDUS", "PROJECT"), ("INDUS", "PROJECT")] if site == "kanmer" else []
    for prefix in prefixes:
        if parts[:len(prefix)] == prefix and all(p.isdigit() for p in parts[len(prefix):]) and len(parts) > len(prefix):
            return parts[len(prefix):]
    return parts


def family_ids(value):
    return sorted({"LIPI:" + x.removeprefix("LIPI:") for x in re.split(r"[|;,\s]+", str(value or "")) if re.fullmatch(r"(?:LIPI:)?\d+", x)}, key=lambda x: int(x.split(":")[1]))


def parse_pages(value):
    """Strict numerical locator parsing; prose and reversed ranges stay unknown."""
    text = str(value or "").strip()
    coordinate = "pdf" if re.match(r"(?i)^PDF\b", text) else "unspecified"
    text = re.sub(r"(?i)^PDF\s*", "", text).strip()
    if not text: return {"pages": [], "status": "missing", "coordinate": coordinate}
    if not re.fullmatch(r"\d+(?:\s*-\s*\d+)?(?:\s*[,;]\s*\d+(?:\s*-\s*\d+)?)*", text):
        return {"pages": [], "status": "unparsed", "coordinate": coordinate}
    pages = set()
    for bit in re.split(r"[,;]", text):
        nums = [int(x.strip()) for x in bit.split("-")]
        a, b = (nums[0], nums[-1])
        if a < 1 or b < a or b - a > 10000: return {"pages": [], "status": "invalid_range", "coordinate": coordinate}
        pages.update(range(a, b + 1))
    return {"pages": sorted(pages), "status": "parsed", "coordinate": coordinate}


def access_class(access):
    """Classify only the recorded access method; never inspect source passages."""
    a = access.casefold()
    if "cropped image viewed" in a:
        return "image_display", "model_display_recorded", "page_specific; crop_object_identity_unresolved"
    if "confirmed display incident" in a:
        return "possible_nonidentity_text", "model_display_recorded", "page_specific; displayed_content_extent_uncertain"
    if "conservative display incident" in a:
        return "possible_nonidentity_text", "possible_model_display_documented", "conservative_affected_page_set; displayed_content_unverified"
    if "preview included descriptive content" in a:
        return "possible_nonidentity_text", "model_display_recorded", "source_landing_page; relation_to_pdf_pages_unresolved"
    if "incidental restricted-content exposure" in a or "reader exposed" in a:
        return "possible_nonidentity_text", "model_display_recorded", "reviewed_page_set; exposed_subset_unknown"
    if any(s in a for s in ["agent-visible text preview", "diagnostic text output", "automated context-fragment exposure"]):
        return "possible_nonidentity_text", "model_display_recorded", "page_specific; displayed_content_extent_uncertain"
    if any(s in a for s in ["bytes hashed", "byte-only acquisition"]):
        return "bytes_only", "script_only_recorded", "no_content_display_recorded"
    if any(s in a for s in ["no source words emitted", "text layer read by script", "script-only", "automated identity search", "automated alias and keyword scan", "automated pdf text extraction", "automated ocr", "ocr and keyword search by script", "no human image view"]):
        return "machine_text_or_ocr" if "bytes" not in a else "bytes_only", "script_only_recorded", "no_model_display_asserted_by_this_record"
    if "bibliographic" in a or "publication landing-page" in a or "publisher bibliographic" in a:
        return "bibliographic_metadata", "metadata_display_recorded", "source_or_frontmatter_scope"
    if any(s in a for s in ["filtered identity text", "closed identity", "identity relations", "registration on immediate line", "closed-vocabulary", "filtered metadata output", "metadata filters", "restricted-vocabulary", "tables only", "filtered identity and scope review"]):
        return "identity_metadata", "metadata_display_recorded", "recorded_page_set"
    return "content_scope_unknown", "display_status_unknown", "unresolved"


def participant(agent):
    raw = agent.strip()
    run = re.search(r"(?i)\brun\s+([0-9][A-Z]?)\b", raw)
    known_cli = "gpt-6.1-sol" in raw.casefold() and bool(run)
    model = "gpt-6.1-sol" if "gpt-6.1-sol" in raw.casefold() else "GPT-6 family" if "gpt-6" in raw.casefold() else "unknown"
    return {"reported_label": raw, "model": model, "run": run[1] if run else None, "harness": "Codex CLI 0.160.1" if known_cli else "Codex API harness" if "api" in raw.casefold() else "unknown", "harness_basis": PATHS["retrospective"] if known_cli else "reported_agent_label", "individual_session_identity": "not_reconstructed", "later_participant_propagation": "unknown"}


class Audit:
    def __init__(self):
        self.input_manifest = [{"name": k, "path": p, "sha256": sha(ROOT / p), "bytes": (ROOT / p).stat().st_size} for k, p in PATHS.items()]
        self.hashes = {r["path"]: r["sha256"] for r in self.input_manifest}
        self.queue = read_csv(PATHS["queue"])
        if len(self.queue) != 358 or len({r["source_row_id"] for r in self.queue}) != 358: raise ValueError("Fixed 358-row selection changed")
        self.all_inventory = {r["row_id"]: {k: r[k] for k in IDENTITY_COLUMNS} for r in read_csv(PATHS["inventory"])}
        self.selected = {r["source_row_id"]: self.all_inventory[r["source_row_id"]] for r in self.queue}
        self.sources = {r["source_id"]: r for r in read_csv(PATHS["sources"])}
        self.decisions = {r["row_id"]: r for r in read_csv(PATHS["decisions"])}
        self.register = {}
        # The compact register has no transcription payload. Retain identity,
        # site and aliases only; no measurement or descriptive field is emitted.
        with (ROOT / PATHS["register"]).open(encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                self.register[r["object_id"]] = {"object_id": r["object_id"], "aliases": r["aliases"], "site": r["fields"]["context.site"]["value"], "registration": r["fields"]["object.excavation_identifier"]["value"]}
        self.regindex = collections.defaultdict(set)
        self.reg_evidence = collections.defaultdict(list)
        for oid, row in self.register.items():
            for alias in row["aliases"]:
                if alias["status"] != "confirmed" or not (alias["scheme"] == "export_registration_string" or alias["scheme"].endswith(":field_number")): continue
                norm = site_registration(row["site"], alias["value"])
                if norm:
                    self.regindex[(normalize_site(row["site"]), norm)].add(oid)
                    self.reg_evidence[(oid, norm)].append({"scheme": alias["scheme"], "assertion_id": alias["assertion_id"], "value": alias["value"]})
        self.events, self.event_by_source, self.reviews, self.relations = [], collections.defaultdict(list), [], []

    def add_event(self, source_id, agent, access, pages, path, record, coordinate="inferred_pdf", purpose=None, incident=False):
        parsed = parse_pages(pages)
        src = self.sources.get(source_id, {})
        local = str(src.get("local_path", ""))
        nonpdf = bool(local and not local.lower().endswith(".pdf"))
        if parsed["coordinate"] == "pdf": coordinate = "explicit_pdf_label"
        if nonpdf: coordinate = "derived_page_label; underlying_pdf_version_unverified" if parsed["pages"] else "nonpdf_source_page_mapping_unresolved"
        content, display, extent = access_class(access)
        e = {"event_id": stable_id("EXP-", [path, record, source_id, agent, access, str(pages)]), "source_id": source_id, "source_asset_sha256_declared": src.get("sha256") or None, "source_version_binding": "derived_text_or_acquisition_record_hash; underlying_pdf_version_unverified" if nonpdf else "registered_pdf_hash; bytes_not_rechecked", "source_hash_verified_this_audit": False, "source_local_path": local or None, "participant_scope": participant(agent), "access_method": access, "page_locator_raw": str(pages), "pdf_pages": parsed["pages"] if coordinate != "nonpdf_source_page_mapping_unresolved" else [], "page_parse_status": parsed["status"], "page_coordinate_basis": coordinate, "content_type": content, "display_status": display, "display_extent": extent, "object_specific_content_verified": False, "evidence": {"path": path, "record": str(record), "sha256": self.hashes.get(path) or sha(ROOT / path)}, "purpose_recorded": purpose or None, "date": "2026-10-21", "date_basis": "source_package_date; exact timestamp unknown", "statistic_family": "not_recorded", "confirmation_eligible_effect": "requires_declared_participant_and_statistic_policy"}
        self.events.append(e); self.event_by_source[source_id].append(e)

    def exposure(self):
        for i, row in enumerate(read_csv(PATHS["logs"])):
            # Original verification records name pdf_page explicitly; the
            # combined log retains this coordinate in its pages column.
            coord = "explicit_pdf_original_header" if row["log"].startswith("verification/exposure-log") else "inferred_pdf"
            self.add_event(row["source_id"], row["agent"], row["access"], row["pages"], PATHS["logs"], "row_index=" + str(i), coord, row["purpose"])
        for i, row in enumerate(read_csv(PATHS["mechanical"])):
            self.add_event(row["source_id"], row["agent"], row["access"], row["pages"], PATHS["mechanical"], "row_index=" + str(i), "explicit_pdf_mechanical_audit", row["purpose"])
        incidents = read_json(PATHS["incidents"])
        for i, row in enumerate(incidents["affected_display_set"]):
            self.add_event(row["source_id"], row.get("agent", "Codex / GPT-6 / API harness"), "conservative display incident; possible nonidentity text", str(row["pdf_page"]), PATHS["incidents"], "affected_display_set/" + str(i), "explicit_pdf_incident", incident=True)
        for i, row in enumerate(read_json(PATHS["incidents_v2"])["additional_display_set"]):
            self.add_event(row["source_id"], "Codex / GPT-6 / API harness", "confirmed display incident; possible nonidentity text", str(row["pdf_page"]), PATHS["incidents_v2"], "additional_display_set/" + str(i), "explicit_pdf_incident", incident=True)

    def duplicate_relations(self):
        pairs = {}
        for rid, row in self.selected.items():
            other = row["possible_duplicate_of"]
            if other:
                pairs[tuple(sorted([rid, other]))] = {"reported_by": "inventory_possible_duplicate", "evidence": [{"path": PATHS["inventory"], "record": "row_id=" + rid, "field": "possible_duplicate_of"}]}
        for name in ["duplicates_cross", "duplicates_same"]:
            for i, row in enumerate(read_csv(PATHS[name])):
                a, b = row["row_id_a"], row["row_id_b"]
                if a not in self.selected and b not in self.selected: continue
                pair = tuple(sorted([a, b]))
                if pair not in pairs: pairs[pair] = {"reported_by": "shared_registration_review", "evidence": []}
                pairs[pair]["evidence"].append({"path": PATHS[name], "record": "row_index=" + str(i), "field": "row_id_a,row_id_b,registration_a,registration_b"})
        for (a, b), info in sorted(pairs.items()):
            ra, rb = self.all_inventory.get(a), self.all_inventory.get(b)
            same_reg = bool(ra and rb and normalize_registration(ra["registration"]) and normalize_registration(ra["registration"]) == normalize_registration(rb["registration"]) and normalize_site(ra["site"]) == normalize_site(rb["site"]))
            if same_reg:
                # Different catalogue entries can share an excavation number.
                # Keep the relation, rather than collapse physical carriers.
                status = "shared_registration_distinct_catalogue_entries_unresolved"
                reason = "The same registration appears with different catalogue entries; its object-level uniqueness has not been established."
            else:
                status = "possible_duplicate_unresolved"
                reason = "One or both rows lack a registration and no explicit same-object cross-reference is present in the reviewed identity metadata."
            self.relations.append({"relation_id": stable_id("DUP-", [a, b]), "row_ids": [a, b], "status": status, "same_reported_registration": same_reg, "duplicate_cluster": None, "merge_authorized": False, "reason": reason, **info})

    def identity(self, row):
        inherited = family_ids(row["local_family_ids"])
        missing = [x for x in inherited if x not in self.register]
        if missing: raise ValueError("Candidate points outside register: " + str(missing))
        norm = site_registration(row["site"], row["registration"])
        sites = {normalize_site(row["site"]), normalize_site(row["local_site_label"])} - {""}
        exact = set()
        if norm:
            for site in sites: exact.update(self.regindex.get((site, norm), set()))
        inherited_strong = row["local_match"] == "matched" and row["match_basis"] in {"registration-exact", "registration-normalised", "registration-contained"}
        supported = set(inherited) & exact if inherited_strong else set()
        accepted_new = set()
        for oid in exact:
            if row["match_basis"] != "conflict" and (oid in inherited or row["local_match"] == "absent"):
                accepted_new.add(oid)
        # Whole-identifier equality can narrow an existing candidate set. It
        # never merges provisional families or overrides a recorded conflict.
        supported.update(accepted_new)
        if len(supported) == 1:
            status = "identifier_supported_provisional_family"
        elif len(supported) > 1:
            status = "identifier_supported_one_to_many_unresolved"
        elif exact:
            status = "exact_identifier_candidate_requires_conflict_review"
        elif inherited:
            status = "candidate_only"
        else:
            status = "not_linked_in_held_register"
        evidence = [{"path": PATHS["inventory"], "record": "row_id=" + row["row_id"], "fields": ["registration", "local_match", "local_family_ids", "match_basis"], "sha256": self.hashes[PATHS["inventory"]]}]
        if row["row_id"] in self.decisions:
            evidence.append({"path": PATHS["decisions"], "record": "row_id=" + row["row_id"], "sha256": self.hashes[PATHS["decisions"]]})
        for oid in sorted(exact):
            evidence.append({"path": PATHS["register"], "record": "object_id=" + oid, "sha256": self.hashes[PATHS["register"]], "matched_aliases": self.reg_evidence[(oid, norm)], "rule": "whole_registration_components_equal_with_same_site; documented_DHR_or_Kanmer_project_namespace_allowed", "namespace_rule_evidence": PATHS["identity_rules"] + ":157-199"})
        return {"identity_status": status, "supported_candidate_family_ids": sorted(supported), "inherited_candidate_family_ids": inherited, "inherited_match_basis": row["match_basis"], "inherited_match_status": row["local_match"], "exact_identifier_family_ids": sorted(exact), "new_supported_family_ids": sorted(accepted_new - set(inherited if inherited_strong else [])), "unresolved_candidate_family_ids": sorted((set(inherited) | exact) - supported), "context_only_family_ids": family_ids(row["context_join_family"]), "physical_identity_status": "provisional; no families merged", "identity_evidence": evidence}

    def match_events(self, row):
        source = self.sources.get(row["primary_publication"], {})
        digest = source.get("sha256")
        compatible = {row["primary_publication"]}
        if digest:
            compatible.update(sid for sid, s in self.sources.items() if s.get("sha256") == digest)
        pages = parse_pages(row["pdf_page"])
        printed = parse_pages(row["page"])
        matches, source_only = [], []
        for sid in sorted(compatible):
            for e in self.event_by_source.get(sid, []):
                overlap = sorted(set(pages["pages"]) & set(e["pdf_pages"]))
                if overlap:
                    matches.append({"event_id": e["event_id"], "matched_pdf_pages": overlap, "source_relation": "same_source_id" if sid == row["primary_publication"] else "same_declared_sha256", "page_mapping_basis": e["page_coordinate_basis"], "display_status": e["display_status"], "content_type": e["content_type"], "display_extent": e["display_extent"], "participant": e["participant_scope"]["reported_label"], "evidence": e["evidence"]})
                else: source_only.append(e["event_id"])
        explicit = [m for m in matches if m["page_mapping_basis"].startswith("explicit_pdf")]
        images = [m for m in matches if m["content_type"] == "image_display"]
        page_displays = [m for m in matches if m["content_type"] == "possible_nonidentity_text" and m["display_extent"].startswith("page_specific")]
        potential = [m for m in matches if m["display_status"] == "possible_model_display_documented"]
        broad = [m for m in matches if m["display_extent"] == "reviewed_page_set; exposed_subset_unknown"]
        metadata = [m for m in matches if m["display_status"] == "metadata_display_recorded"]
        scripts = [m for m in matches if m["display_status"] == "script_only_recorded"]
        if images: state = "source_page_image_display_recorded_object_scope_unresolved"
        elif page_displays: state = "source_page_text_display_recorded_object_scope_unresolved"
        elif potential: state = "source_page_possible_text_display_documented_object_scope_unresolved"
        elif broad: state = "source_review_display_recorded_exposed_subset_unresolved"
        elif metadata: state = "identity_or_bibliographic_display_recorded"
        elif scripts: state = "script_access_recorded_no_display_certification"
        else: state = "source_access_recorded_page_scope_unresolved" if source_only else "exposure_history_unknown"
        srcpath = str(source.get("local_path", ""))
        nonpdf = bool(srcpath and not srcpath.lower().endswith(".pdf"))
        mapping = "derived_page_label_event_match_underlying_pdf_version_unverified" if nonpdf and matches else "explicit_pdf_page_event_match" if explicit else "inferred_pdf_page_event_match" if matches else "source_is_nonpdf_page_map_unresolved" if nonpdf else "no_page_event_match"
        return {"reviewed_exposure_status": state, "page_mapping_status": mapping, "candidate_pdf_pages": pages, "candidate_printed_pages": printed, "printed_to_pdf_mapping": {"status": "inventory_pair_only_not_independently_verified", "pairs": list(zip(printed["pages"], pages["pages"])) if len(printed["pages"]) == len(pages["pages"]) else []}, "exposure_events": matches, "source_level_event_ids_without_page_overlap": source_only, "participant_scope": sorted({m["participant"] for m in matches}), "source_version": {"source_id": row["primary_publication"], "sha256_declared": digest or None, "registered_local_path": srcpath or None, "asset_bytes_opened_this_audit": False}, "confirmation_eligible": False, "confirmation_blockers": ["physical identity and dependence closure not certified", "future participant set and statistic-family policy not frozen", "historical displayed content cannot be certified object by object from these logs"]}

    def run(self):
        self.exposure(); self.duplicate_relations()
        for queue_row in self.queue:
            rid = queue_row["source_row_id"]; row = self.selected[rid]
            review = {"source_row_id": rid, "review_status": "metadata_review_completed", "site": row["site"], "registration": row["registration"], "other_identifiers": row["other_numbers"], "primary_source_id": row["primary_publication"], "catalogue_status": row["catalogue_status"], "inscription_status": row["inscription_status"], "duplicate_relations": [r for r in self.relations if rid in r["row_ids"]], "duplicate_cluster": None, "value_status": "catalogued", "source_locator": {"pdf_page": row["pdf_page"], "printed_page": row["page"], "plate_or_figure": row["plate_or_figure"]}, **self.identity(row), **self.match_events(row)}
            self.reviews.append(review)
        self.summary = {"fixed_selection": {"rows": len(self.queue), "path": PATHS["queue"], "sha256": self.hashes[PATHS["queue"]]}, "reviewed_rows": len(self.reviews), "identity_status": dict(collections.Counter(r["identity_status"] for r in self.reviews)), "rows_with_supported_family": sum(bool(r["supported_candidate_family_ids"]) for r in self.reviews), "rows_with_new_supported_family": sum(bool(r["new_supported_family_ids"]) for r in self.reviews), "supported_distinct_family_ids": len({o for r in self.reviews for o in r["supported_candidate_family_ids"]}), "duplicate_relations": dict(collections.Counter(r["status"] for r in self.relations)), "inherited_possible_duplicate_markers_reviewed": sum(bool(r["possible_duplicate_of"]) for r in self.selected.values()), "physical_family_merges": 0, "exposure_documentation_records": len(self.events), "event_content_type": dict(collections.Counter(e["content_type"] for e in self.events)), "reviewed_exposure_status": dict(collections.Counter(r["reviewed_exposure_status"] for r in self.reviews)), "page_mapping_status": dict(collections.Counter(r["page_mapping_status"] for r in self.reviews)), "rows_with_pdf_event_overlap": sum(bool(r["exposure_events"]) for r in self.reviews), "confirmation_eligible": 0, "new_primary_source_images_displayed": 0, "new_primary_source_passages_displayed": 0, "scope_notes": ["Event counts describe documentation records; a combined log and incident record may describe the same historical access.", "A page match connects candidate locators to recorded access; it does not establish which part of that page a participant saw.", "Sources with identical declared hashes share version-specific exposure; different versions are not assigned the same PDF pagination.", "Printed-to-PDF pairs are retained from the inventory, with no whole-volume offset extrapolated.", "All confirmation eligibility remains false; source absence and missing logs do not establish freshness."]}
        return self

    def patches(self):
        return [{"patch_id": stable_id("PATCH-", r["source_row_id"]), "source_row_id": r["source_row_id"], "supported_object_ids": r["supported_candidate_family_ids"], "candidate_object_ids": r["unresolved_candidate_family_ids"], "operation": "append_source_review_assertions; do_not_merge_families", "assertions": [{"field": field, "value": r[field], "value_status": "catalogued" if field == "participant_scope" else "inferred", "source_review_id": r["source_row_id"]} for field in ["identity_status", "reviewed_exposure_status", "page_mapping_status", "participant_scope", "confirmation_eligible", "duplicate_relations"]], "evidence": r["identity_evidence"], "exposure_event_ids": [e["event_id"] for e in r["exposure_events"]], "uncertainty": "provisional identity and incomplete participant-specific exposure history"} for r in self.reviews]

    def current_access_log(self):
        records = []
        for entry in self.input_manifest:
            name = entry["name"]
            workflow = name.startswith("workflow") or name.startswith("identity_")
            display = "selected workflow code and comments" if workflow else "selected identifier, locator, access-method or aggregate metadata"
            if name == "workflow_d": display += "; incidental object-type, material and context literals in code search output"
            records.append({"access_id": "CURRENT-" + name, "date": "2026-10-22", "timestamp_precision": "session_date; individual tool times not reconstructed", "path": entry["path"], "sha256": entry["sha256"], "access_kind": "metadata_or_workflow_read_and_hash", "displayed_content": display, "display_detail": "Exact excerpts are not copied; input bytes are identified by hash.", "primary_source_asset_opened": False, "primary_source_image_displayed": False, "primary_source_passage_displayed": False, "candidate_nonidentity_metadata_in_code_displayed": name == "workflow_d", "possibly_affected_source_ids": ["bisht2015-held", "iar-1997-98-archive"] if name == "workflow_d" else [], "participant": {"model": "GPT-6 family; exact backend identifier not exposed", "harness": "Codex desktop collaboration; exec_command", "agent": "object-register worker"}, "record_scope": "audit-session access group; repeated metadata projections and replay reads grouped by input", "confirmation_eligibility_asserted": False})
        return records


def validate(audit):
    errors = []
    if len(audit.reviews) != 358 or {r["source_row_id"] for r in audit.reviews} != set(audit.selected): errors.append("selection_closure")
    event_ids = {e["event_id"] for e in audit.events}
    if len(event_ids) != len(audit.events): errors.append("duplicate_event_id")
    for row in audit.reviews:
        if row["confirmation_eligible"]: errors.append("unsupported_freshness")
        if row["primary_source_id"] not in audit.sources: errors.append("unregistered_primary_source")
        if not set(row["supported_candidate_family_ids"]).issubset(set(row["exact_identifier_family_ids"])): errors.append("supported_link_without_full_identifier_check")
        for oid in row["supported_candidate_family_ids"] + row["unresolved_candidate_family_ids"]:
            if oid not in audit.register: errors.append("unknown_family_id")
        for event in row["exposure_events"]:
            if event["event_id"] not in event_ids: errors.append("unknown_event_id")
            if not event["matched_pdf_pages"]: errors.append("empty_page_match")
    if sum(audit.summary["identity_status"].values()) != 358 or sum(audit.summary["reviewed_exposure_status"].values()) != 358: errors.append("aggregate_reconciliation")
    if any(r["merge_authorized"] for r in audit.relations): errors.append("physical_merge_not_supported")
    for patch in audit.patches():
        if any(a["value_status"] not in CANONICAL_STATUS for a in patch["assertions"]): errors.append("noncanonical_value_status")
    return sorted(set(errors))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--summary-dir", required=True)
    args = ap.parse_args()
    out, summary = Path(args.out).resolve(), Path(args.summary_dir).resolve()
    if not out.is_relative_to(RAW.resolve()) or out == RAW.resolve(): raise ValueError("out must be a new owned local child")
    if not summary.is_relative_to(HERE) or summary == HERE: raise ValueError("summary must be a new owned child")
    if out.exists() or summary.exists(): raise ValueError("Existing output refused")
    audit = Audit().run(); errors = validate(audit)
    if errors: raise ValueError(str(errors))
    out.mkdir(parents=True); summary.mkdir(parents=True)
    write_lines(out / "candidate-reviews.jsonl", audit.reviews)
    write_lines(out / "exposure-events.jsonl", audit.events)
    write_lines(out / "duplicate-relations.jsonl", audit.relations)
    write_lines(out / "assertion-patches.jsonl", audit.patches())
    write_lines(out / "current-access-log.jsonl", audit.current_access_log())
    dispositions = [{"source_row_id": r["source_row_id"], "identity_status": r["identity_status"], "supported_candidate_family_ids": "|".join(r["supported_candidate_family_ids"]), "unresolved_candidate_family_ids": "|".join(r["unresolved_candidate_family_ids"]), "reviewed_exposure_status": r["reviewed_exposure_status"], "page_mapping_status": r["page_mapping_status"], "matched_exposure_records": len(r["exposure_events"]), "confirmation_eligible": False} for r in audit.reviews]
    write_csv(out / "reconciled-dispositions.csv", dispositions)
    write_json(summary / "summary.json", audit.summary)
    write_json(summary / "source-manifest.json", {"inputs": audit.input_manifest, "protocol_sha256": sha(HERE / "PROTOCOL.md"), "code_sha256": sha(Path(__file__)), "source_assets_opened": False, "source_version_note": "Asset hashes are inherited from the source register; exact input metadata bytes are checked here."})
    write_json(summary / "validation.json", {"status": "passed", "errors": errors, "reviewed_rows": len(audit.reviews), "output_hashes": {p.name: sha(p) for p in sorted(out.iterdir())}})
    print(json.dumps(audit.summary, ensure_ascii=True))


if __name__ == "__main__": main()
