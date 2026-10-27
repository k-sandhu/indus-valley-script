"""Independently check the register's base population against held source IDs.

This check uses no builder helpers and does not evaluate inscription readings.
Only aggregate results and source hashes are written to the report.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def records(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--register-dir", type=Path, required=True)
    parser.add_argument("--source", type=Path,
                        default=Path("data/normalized/lipi_observed_faces.jsonl"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Choose a new output; existing evidence is preserved")
    source = records(args.source)
    object_path = args.register_dir / "objects.jsonl"
    face_path = args.register_dir / "faces.jsonl"
    objects = records(object_path)
    faces = records(face_path)
    expected = defaultdict(set)
    for row in source:
        expected["LIPI:" + str(row["object_family_id"])].add(
            "LIPI:" + str(row["record_id"]))
    object_ids = Counter(row["object_id"] for row in objects)
    face_ids = Counter(row["face_id"] for row in faces)
    expected_faces = {face for values in expected.values() for face in values}
    observed_membership = defaultdict(set)
    for row in faces:
        observed_membership[row["object_id"]].add(row["face_id"])
    checks = {
        "object_ids_match_source_families": set(object_ids) == set(expected),
        "face_ids_match_source_records": set(face_ids) == expected_faces,
        "object_ids_unique": all(n == 1 for n in object_ids.values()),
        "face_ids_unique": all(n == 1 for n in face_ids.values()),
        "source_record_ids_unique": len(source) == len(expected_faces),
        "face_parent_links_match_source": dict(observed_membership) == dict(expected),
        "object_face_lists_match_source": all(
            set(row["face_ids"]) == expected[row["object_id"]]
            and len(row["face_ids"]) == len(set(row["face_ids"]))
            for row in objects),
        "all_base_identities_provisional": all(
            row.get("physical_identity_status") == "provisional" for row in objects),
        "objects_require_exposure_review": all(
            row.get("exposure_status") == "unreviewed" for row in objects),
        "faces_require_exposure_review": all(
            row.get("exposure_status") == "unreviewed" for row in faces),
        "face_evidence_has_source_hash": all(
            isinstance(row.get("source_sha256"), str)
            and len(row["source_sha256"]) == 64
            and row.get("source_id") for row in faces),
    }
    forbidden = {"signs_visual_ltr", "signs_reading_rtl", "text_code_visual_ltr"}
    checks["compact_interface_omits_transcription_fields"] = all(
        not forbidden.intersection(row) for row in objects + faces)
    statuses = {"observed", "catalogued", "inferred", "unknown",
                "conflicting", "not-applicable"}
    checks["object_fields_use_canonical_value_status"] = all(
        field.get("value_status") in statuses
        for row in objects for field in row.get("fields", {}).values())
    checks["unknown_object_fields_have_missing_reason"] = all(
        field.get("missing_reason")
        for row in objects for field in row.get("fields", {}).values()
        if field.get("value_status") == "unknown")
    assertion_path = args.register_dir / "assertion-values.jsonl"
    assertion_statuses = Counter()
    with assertion_path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                assertion_statuses[json.loads(line).get("value_status")] += 1
    checks["assertions_use_canonical_value_status"] = set(assertion_statuses) <= statuses
    report = {
        "schema_version": "1.0", "status": "pass" if all(checks.values()) else "fail",
        "scope": "Independent ID and relationship accounting; source joins and archaeological identity require their own review.",
        "counts": {"source_faces": len(source), "source_provisional_objects": len(expected),
                   "exported_objects": len(objects), "exported_faces": len(faces)},
        "checks": checks,
        "assertion_value_status_counts": assertion_statuses,
        "provenance": {str(path).replace("\\", "/"): digest(path)
                       for path in (args.source, object_path, face_path, assertion_path,
                                    Path(__file__))},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": report["status"], "counts": report["counts"],
                      "failed_checks": [name for name, passed in checks.items() if not passed]}))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
