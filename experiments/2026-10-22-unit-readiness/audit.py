"""Audit held metadata needed for a reusable-unit study; never score a model."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True

INPUTS = {
    "plate_audit": "experiments/2026-10-20-seal-legend-units/plate-audit/audit-table.csv",
    "plate_summary": "experiments/2026-10-20-seal-legend-units/plate-audit/audit-summary.json",
    "image_links": "experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv",
    "verified_sides": "experiments/2026-10-13-image-index-and-units/verified-sides.tsv",
    "faces": "data/normalized/lipi_observed_faces.jsonl",
    "post_catalogue": "experiments/2026-10-21-post-catalogue-finds/objects.csv",
    "exposure_log": "experiments/2026-10-21-post-catalogue-finds/exposure-log.csv",
    "exposure_retrospective": "experiments/2026-10-21-post-catalogue-finds/RETROSPECTIVE-CODEX.md",
    "readable_records": "data/raw/2026-10-12-bronze-age-comparison/normalized-v4/records.jsonl",
    "clean_lengths": "data/normalized/lipi_clean_rtl_singleline.jsonl",
    "bench_segmentation": "bench/segmentation.py",
    "rehearsal": "experiments/2026-10-12-structure-first/step5-rehearsal/rehearse_segmentation.py",
    "spent": "bench/spent.json",
    "unit_spent_proposal": "experiments/2026-10-20-seal-legend-units/spent-entry.json",
}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(path, delimiter=","):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


def json_rows(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False, sort_keys=True)
        stream.write("\n")


def write_csv(path, rows):
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def register_check(directory):
    files = [directory / "objects.jsonl", directory / "faces.jsonl"]
    if not all(path.is_file() for path in files):
        return {"status": "pending", "reason": "metadata export not available", "paths": [str(p) for p in files]}
    objects, faces = map(json_rows, files)
    errors = []
    oids = [r.get("object_id") for r in objects]
    fids = [r.get("face_id", r.get("surface_id")) for r in faces]
    if len(set(oids)) != len(oids):
        errors.append("duplicate object ids")
    if len(set(fids)) != len(fids):
        errors.append("duplicate face ids")
    if any(r.get("object_id") not in set(oids) for r in faces):
        errors.append("face parent absent")
    if any(not isinstance(i, str) or not i.startswith("LIPI:") for i in oids + fids):
        errors.append("unexpected provisional ID namespace")
    images = [image for face in faces for image in face.get("image_links", [])]
    return {
        "status": "failed" if errors else "checked",
        "errors": errors,
        "objects": len(objects), "faces": len(faces), "image_links": len(images),
        "face_exposure_statuses": dict(Counter(r.get("exposure_status", "missing") for r in faces)),
        "face_identity_statuses": dict(Counter(r.get("identity_status", "missing") for r in faces)),
        "image_side_match": dict(Counter(str(r.get("side_match", "missing")) for r in images)),
        "faces_with_conflicts": sum(bool(r.get("conflicts")) for r in faces),
        "sources": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in files],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--local-out", type=Path, required=True)
    parser.add_argument("--register-dir", type=Path)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.local_out = args.local_out.resolve()
    if args.register_dir:
        args.register_dir = args.register_dir.resolve()
    if args.out.exists() or args.local_out.exists():
        raise SystemExit("Refusing to replace an existing output file or local directory")
    paths = {k: ROOT / v for k, v in INPUTS.items()}
    plate = csv_rows(paths["plate_audit"])
    links = csv_rows(paths["image_links"])
    verified = csv_rows(paths["verified_sides"], "\t")
    faces = json_rows(paths["faces"])
    fmap = {r["record_id"]: r for r in faces}
    assert len(fmap) == len(faces), "duplicate normalized face IDs"
    assert len({r["record_id"] for r in plate}) == len(plate), "duplicate audit IDs"
    assert all(r["record_id"] in fmap for r in plate), "unjoined plate audit ID"
    assert all(r["record_id"] in fmap for r in links), "unjoined image index ID"
    args.local_out.mkdir(parents=True)
    register_summary = register_check(args.register_dir) if args.register_dir else None
    registered_faces = {}
    if register_summary and register_summary["status"] == "checked":
        registered_faces = {r.get("face_id", r.get("surface_id")): r
                            for r in json_rows(args.register_dir / "faces.jsonl")}
    byface = defaultdict(list)
    for link in links:
        byface[link["record_id"]].append(link)

    plate_queue = []
    for r in plate:
        f = fmap[r["record_id"]]
        issues = []
        if r["audit_status"] == "no_plate_crop":
            issues.append("acquire-CISI3-plate" if r["cisi"] != "-" else "resolve-primary-object-locator")
        if r["audit_status"] == "read" and r["division_confirmed"] != "yes":
            issues.append("adjudicate-physical-division")
        if r["audit_status"] == "read" and not r["plate_order"]:
            issues.append("adjudicate-spatial-order")
        if r["code_status"] != "eligible":
            issues.append("retain-damage-or-direction-qualification")
        # Every row needs independent layout adjudication and geometry before a new study.
        issues.extend(["second-independent-layout-reader", "source-image-geometry"])
        regface = registered_faces.get("LIPI:" + r["record_id"], {})
        regimages = regface.get("image_links", [])
        regconflicts = regface.get("conflicts", [])
        flagged_images = [x for x in regimages if x.get("join_status") == "needs-later-audit-review"
                          or x.get("relation") == "needs-later-audit-review"
                          or "needs-later-audit-review" in str(x.get("note", ""))]
        identity_review = bool(regconflicts or flagged_images)
        if identity_review:
            issues.insert(0, "resolve-register-image-identity-conflicts")
        plate_queue.append({
            "priority": 1 if identity_review or (r["audit_status"] == "read" and not r["plate_order"]) else 2 if r["audit_status"] == "no_plate_crop" else 3,
            "object_id": "LIPI:" + f["object_family_id"], "face_id": "LIPI:" + r["record_id"],
            "source_record_id": r["record_id"], "cisi": r["cisi"], "site": r["site"],
            "source": INPUTS["plate_audit"], "audit_status": r["audit_status"],
            "division_confirmed": r["division_confirmed"], "physical_order": r["plate_order"],
            "code_status": r["code_status"], "tasks": "|".join(issues),
            "image_files": "|".join(sorted({x["file"] for x in byface[r["record_id"]]})),
            "image_relations": "|".join(sorted({x["relation"] for x in byface[r["record_id"]]})),
            "register_present": bool(regface),
            "registered_face_identity": regface.get("identity_status", "register-unavailable"),
            "register_image_conflicts": json.dumps({"face_conflicts": regconflicts, "flagged_images": flagged_images}, ensure_ascii=False, sort_keys=True) if regface else "",
            "accepted_side_image_count": sum(x.get("side_match") is True for x in regimages) if regface else "",
            "needs_image_identity_review": identity_review if regface else "unreviewed-register-unavailable",
            "source_locators": "|".join(sorted({f'CISI {x["cisi_volume"]} PDF {x["cisi_pdf_page"]}' for x in byface[r["record_id"]] if x["cisi_pdf_page"]})),
            "exposure_status": "historically-examined-corpus", "new_confirmation_eligible": False,
        })
    plate_queue.sort(key=lambda r: (r["priority"], r["site"], r["cisi"], r["face_id"]))
    write_csv(args.local_out / "divided-face-queue.csv", plate_queue)

    families = defaultdict(list)
    for f in faces:
        families[f["object_family_id"]].append(f)
    verified_ids = {r["record_id"] for r in verified}
    multiface_queue = []
    for oid, members in families.items():
        if len(members) < 2 or all(r["record_id"] in verified_ids for r in members):
            continue
        fids = [r["record_id"] for r in members]
        flinks = [x for fid in fids for x in byface[fid]]
        multiface_queue.append({
            "priority": 2 if flinks else 3, "object_id": "LIPI:" + oid,
            "face_ids": "|".join("LIPI:" + fid for fid in fids),
            "cisi": "|".join(sorted({r["source_cisi"] for r in members})),
            "faces": len(fids), "verified_faces": sum(fid in verified_ids for fid in fids),
            "linked_files": len({x["file"] for x in flinks}),
            "task": "identify-every-face-in-primary-images" if flinks else "acquire-primary-images-and-map-every-face",
            "source": INPUTS["verified_sides"], "exposure_status": "historically-examined-corpus",
        })
    multiface_queue.sort(key=lambda r: (r["priority"], r["object_id"]))
    write_csv(args.local_out / "multiface-queue.csv", multiface_queue)

    post = csv_rows(paths["post_catalogue"])
    assert len({r["row_id"] for r in post}) == len(post), "duplicate post-catalogue row IDs"
    exposure = csv_rows(paths["exposure_log"])
    bysource = defaultdict(list)
    for item in exposure:
        bysource[item["source_id"]].append(item)
    candidates = []
    for r in post:
        if r["catalogue_status"] == "in-baseline-catalogue":
            continue
        tasks = ["source-page-exposure-review", "confirmed-physical-identity", "all-faces-and-aliases", "participant-specific-exposure-attestation"]
        if r["possible_duplicate_of"]:
            tasks.append("resolve-possible-duplicate")
        if r["inscription_status"] != "stated":
            tasks.append("verify-inscription-status")
        candidates.append({
            "priority": 2 if r["local_match"] == "absent" else 3,
            "source_row_id": r["row_id"], "site": r["site"], "primary_source_id": r["primary_publication"],
            "pdf_page": r["pdf_page"], "printed_page": r["page"], "plate_or_figure": r["plate_or_figure"],
            "catalogue_status": r["catalogue_status"], "inscription_status": r["inscription_status"],
            "identity_status": r["local_match"], "candidate_lipi_families": r["local_family_ids"],
            "possible_duplicate_of": r["possible_duplicate_of"],
            "source_exposure_log_rows": len(bysource[r["primary_publication"]]),
            "exposure_status": "unreviewed-at-object-and-participant-level",
            "new_confirmation_eligible": False, "tasks": "|".join(tasks),
        })
    candidates.sort(key=lambda r: (r["priority"], r["site"], r["source_row_id"]))
    write_csv(args.local_out / "candidate-cohort-queue.csv", candidates)

    from bench import segmentation
    # This reproduces only existing cohort membership, never predictions or scores.
    cohorts = segmentation.cohorts()
    control_counts = {name: {"texts": len(items), "internal_boundary_labels": sum(len(b) for _, b in items),
                            "complete": True, "previously_used": True} for name, items in cohorts.items()}
    raw_controls = json_rows(paths["readable_records"])
    control_pools = []
    for corpus, kind in [("sumerian", "seal"), ("sumerian", "natural_line"), ("egyptian", "glyph_sentence"), ("akkadian", "natural_line")]:
        rows = [r for r in raw_controls if r["corpus"] == corpus and r["kind"] == kind]
        valid = [r for r in rows if r.get("word_units") and all(r["word_units"])]
        control_pools.append({"corpus": corpus, "kind": kind, "source_rows": len(rows),
                              "rows_with_nonempty_word_units": len(valid),
                              "source_documents": len({r.get("document") for r in valid}),
                              "rows_with_source_word_refs": sum(bool(r.get("source_word_refs")) for r in valid),
                              "source_document_is_physical_object": "unverified; review composites and aliases"})

    spent = json.loads(paths["spent"].read_text(encoding="utf-8"))
    historical = json.loads(paths["unit_spent_proposal"].read_text(encoding="utf-8"))
    families_spent = sorted({f for r in spent["splits"].values() for f in r.get("spent_families", [])})
    histfamilies = historical["spent_families"]
    summary = {
        "schema_version": "1.0", "task": "unit-data-readiness", "synthetic": False,
        "scope": "held metadata audit; no image viewing, no new model score, no new confirmation read",
        "plate_audit": {
            "faces": len(plate), "with_crop": sum(r["audit_status"] == "read" for r in plate),
            "confirmed_divisions": sum(r["division_confirmed"] == "yes" for r in plate),
            "unclear_divisions": sum(r["division_confirmed"] == "unclear" for r in plate),
            "missing_crops": sum(r["audit_status"] == "no_plate_crop" for r in plate),
            "missing_crop_source_categories": dict(Counter("CISI3-number-per-prior-audit" if r["cisi"] != "-" else "no-CISI-number" for r in plate if r["audit_status"] == "no_plate_crop")),
            "physical_order_labels": sum(bool(r["plate_order"]) for r in plate),
            "eligible_clean_order_labels": sum(bool(r["plate_order"]) and r["code_status"] == "eligible" for r in plate),
            "imaged_without_physical_order": sum(r["audit_status"] == "read" and not r["plate_order"] for r in plate),
            "code_status": dict(Counter(r["code_status"] for r in plate)),
            "complete_word_boundary_labels": 0,
            "queued_faces": len(plate_queue),
            "registered_faces": sum(r["register_present"] for r in plate_queue),
            "register_image_identity_reviews": sum(r["needs_image_identity_review"] is True for r in plate_queue),
        },
        "image_assignment": {
            "objects": len(families), "faces": len(faces),
            "multiface_objects": sum(len(v) > 1 for v in families.values()),
            "multiface_objects_without_all_verified_sides": len(multiface_queue),
            "queued_multiface_objects_with_any_linked_image": sum(r["linked_files"] > 0 for r in multiface_queue),
            "queued_multiface_objects_without_linked_image": sum(r["linked_files"] == 0 for r in multiface_queue),
            "side_unassigned_faces_with_image": len({r["record_id"] for r in links if r["relation"] == "side-unassigned"}),
            "face_side_object_photo_faces": len({r["record_id"] for r in links if r["relation"] == "face-side" and r["kind"] == "object"}),
            "link_relations": dict(Counter(r["relation"] for r in links)),
        },
        "candidate_cohort": {
            "inventory_rows": len(post), "nonbaseline_rows": len(candidates),
            "definite_post_catalogue_rows": sum(r["catalogue_status"] == "post-catalogue" and r["inscription_status"] == "stated" for r in candidates),
            "identity_status": dict(Counter(r["identity_status"] for r in candidates)),
            "rows_with_possible_duplicate_marker": sum(bool(r["possible_duplicate_of"]) for r in candidates),
            "rows_with_source_level_exposure_log": sum(r["source_exposure_log_rows"] > 0 for r in candidates),
            "exposure_log_rows": len(exposure), "confirmed_fresh_objects": 0,
            "freshness_statement": "No candidate is certified fresh by this audit; source-level logs need object, page and participant review.",
        },
        "readable_control_cohorts": control_counts, "readable_source_pools": control_pools,
        "spending": {"shared_families": families_spent, "historical_unit_families": histfamilies,
                     "unit_families_absent_from_shared_ledger": sorted(set(histfamilies) - set(families_spent)),
                     "interpretation": "Historical use remains exposure even if a proposed ledger update was not integrated."},
        "readiness": {"held_source_audit": "complete", "historical_reproduction": "available",
                      "new_full_word_boundary_claim": "blocked-no-complete-Indus-labels",
                      "new_physical_division_test": "blocked-adjudication-identity-and-exposure",
                      "prospective_reusable_unit_test": "blocked-confirmed-fresh-cohort-and-freeze",
                      "source_block_transfer_test": "blocked-source-and-dependence-graph-review"},
        "provenance": {"inputs": [{"role": k, "path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": digest(p)} for k, p in paths.items()],
                       "code_sha256": digest(Path(__file__)), "protocol_sha256": digest(PACKAGE / "PROTOCOL.md")},
        "local_outputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in sorted(args.local_out.glob("*.csv"))],
    }
    if args.register_dir:
        summary["object_register"] = register_summary
    expected = json.loads(paths["plate_summary"].read_text(encoding="utf-8"))
    checks = {
        "plate_count_matches_saved_audit": len(plate) == expected["faces"],
        "crop_count_matches_saved_audit": summary["plate_audit"]["with_crop"] == expected["with_plate_crop"],
        "confirmed_count_matches_saved_audit": summary["plate_audit"]["confirmed_divisions"] == expected["division_confirmed"]["yes"],
        "clean_order_count_matches_saved_audit": summary["plate_audit"]["eligible_clean_order_labels"] == expected["eligible_with_plate_order"],
        "all_plate_faces_queued_once": len(plate_queue) == len(plate),
        "all_nonbaseline_rows_queued_once": len(candidates) == sum(r["catalogue_status"] != "in-baseline-catalogue" for r in post),
        "no_freshness_inferred": not any(r["new_confirmation_eligible"] for r in candidates),
        "register_not_failed": summary.get("object_register", {}).get("status") != "failed",
    }
    summary["checks"] = checks
    write_json(args.out, summary)
    print(json.dumps({"out": str(args.out), "checks": checks, "plate": summary["plate_audit"], "image_assignment": summary["image_assignment"], "candidate_cohort": summary["candidate_cohort"], "controls": control_counts}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
