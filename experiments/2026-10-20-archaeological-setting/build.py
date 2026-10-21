"""Build a complete, source-qualified Harappa object disposition."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / "data/raw/2026-10-20-archaeological-setting"
CORPUS = ROOT / "data/normalized/lipi_observed_faces.jsonl"
PRIOR = ROOT / "experiments/2026-10-02-six-hour/harappa-object-frame/annotated/target-ledger.csv"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--local-out", required=True)
    args = parser.parse_args()
    out, local = ROOT / args.out, ROOT / args.local_out
    if out.exists() or local.exists():
        raise FileExistsError("Use new output directories")
    observations = json.loads((OWN / "source-observations.json").read_text(encoding="utf-8"))
    targets = [f"H-{i}" for i in [*range(1719, 1726), *range(1727, 1767)]]
    faces = [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()]
    by_target: dict[str, list[dict]] = defaultdict(list)
    for face in faces:
        if face["source_cisi"] in targets:
            by_target[face["source_cisi"]].append(face)
    prior = {r["target_id"]: r for r in csv.DictReader(PRIOR.open(encoding="utf-8"))}
    assert len(targets) == 47 and len(set(targets)) == 47
    assert all(prior[t]["source_image_status"] == "not-yet-coded" for t in targets)
    caption = {row["target"]: row for row in observations["caption_rows"] if row["target"]}
    rows, local_rows = [], []
    for target in targets:
        fs = by_target[target]
        families = sorted({f["object_family_id"] for f in fs})
        assert len(families) <= 1
        n = int(target.split("-")[1])
        if n <= 1724:
            group = observations["group_assertions"][0]
        elif n == 1725:
            group = observations["group_assertions"][1]
        else:
            group = observations["group_assertions"][2]
        cap = caption.get(target)
        row = {
            "target": target,
            "export_status": "present" if fs else "absent",
            "export_faces": len(fs),
            "source_operation": group["operation"],
            "operation_source": "KM2010-P7",
            "operation_basis": "published-description",
            "firing": group.get("firing", "vessel fired after stamping"),
            "source_image_status": "identified-primary-drawing" if cap else "no-identified-primary-view",
            "individual_caption": cap["id"] if cap else "",
            "source_registration": cap.get("registration", "") if cap else "",
            "source_unit": cap["excavation_unit"] if cap else "",
            "source_item": cap["item"] if cap else "",
            "deposition": cap["deposition"] if cap else (group["deposition"] or "not reported in inspected passage"),
            "deposition_basis": "individual published caption" if cap else (
                "explicit object-range description" if group["deposition"] else "unknown"),
            "join_basis": cap["join_rule"] if cap else "explicit CISI number or range in KM2010-P7",
            "contents_observed": False,
            "reverse_attachment_view": False,
        }
        raw_ids = sorted({f["metadata"]["excavation-idno"] for f in fs})
        if cap:
            if target == "H-1745":
                matches = [f for f in faces if "H95-2407" in f["metadata"]["excavation-idno"]]
            else:
                matches = [f for f in faces if re.search(r"H95-4450-0*31(?:\D|$)", f["metadata"]["excavation-idno"])]
            assert {f["object_family_id"] for f in matches} == set(families)
        row["disposition_reason"] = (
            "matched caption and visible vessel fragment" if cap else
            "source group supplies operation; individual plate/registration not recovered in bounded search")
        rows.append(row)
        local_rows.append({**row, "families": families, "raw_excavation_ids": raw_ids,
                           "object_types": sorted({f["object_type"] for f in fs})})
    unmatched = [r for r in observations["caption_rows"] if not r["target"]]
    unmatched_checks = []
    for cap in unmatched:
        unit, item = cap["excavation_unit"], cap["item"]
        pattern = re.compile(re.escape(unit) + r"\D*0*" + re.escape(str(int(item))) + r"(?:\D|$)")
        found = [f for f in faces if pattern.search(f["metadata"]["excavation-idno"])]
        assert not found, (cap["id"], found)
        unmatched_checks.append({"observation": cap["id"], "matches": 0})
    types = Counter(r["source_operation"] for r in rows)
    changes = {
        "targets": 47,
        "export_objects_present": sum(r["export_status"] == "present" for r in rows),
        "export_objects_absent": sum(r["export_status"] == "absent" for r in rows),
        "export_faces_present": sum(r["export_faces"] for r in rows),
        "explicit_operation_source": {"before": 0, "after": len(rows), "scope": "this bounded ARCH-01 target ledger; no global corpus coverage claim"},
        "identified_primary_view": {"before": 0, "after": len(caption)},
        "individual_source_locus_and_lot_item": {"before": 0, "after": len(caption)},
        "source_registration_restored": ["H-1734"],
        "group_secondary_deposition_assertion": 6,
        "individual_secondary_deposition_assertion": len(caption),
        "objects_with_contents_evidence": 0,
        "objects_with_reverse_attachment_view": 0,
        "operations": dict(types),
        "unjoined_caption_objects": len(unmatched),
        "unjoined_registered_photographed_objects": 1,
        "additional_unregistered_sealing_photograph_objects": 3,
        "export_type_conflicts": ["H-1741: KM2010 named vessel-stamp range versus export TAG"],
        "calendar_dates": {"direct_object_dates_added": 0, "vessel_typology_interval_attributed_to_source": 40},
        "independent_group_feasibility": {
            "sealing_upper_bound_before_alias_text_closure": 7,
            "vessel_upper_bound_before_alias_text_closure": 40,
            "required_per_class": 10,
            "eligible_for_classifier": False,
            "reason": "sealing class cannot reach ten groups even before grouping; no direct contents labels or registered seal-to-vessel pairs"},
    }
    sources = []
    for inspection in observations["primary_inspections"]:
        for key in ["source_path", "render_path"]:
            path = ROOT / inspection[key]
            sources.append({"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "bytes": path.stat().st_size})
    for name in ["acquisition.json", "image-acquisition.json", "image-acquisition-v2.json"]:
        manifest = json.loads((OWN / name).read_text(encoding="utf-8"))
        for rec in manifest["records"]:
            if "path" in rec:
                path = ROOT / rec["path"]
                assert sha(path) == rec["sha256"]
                sources.append({"path": rec["path"], "sha256": rec["sha256"], "bytes": path.stat().st_size})
    out.mkdir(parents=True)
    local.mkdir(parents=True)
    with (out / "target-dispositions.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (local / "object-joins.json").write_text(json.dumps(local_rows, indent=2) + "\n", encoding="utf-8")
    (out / "unmatched-caption-checks.json").write_text(json.dumps(unmatched_checks, indent=2) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")
    provenance = {
        "python": platform.python_version(),
        "corpus": {"path": CORPUS.relative_to(ROOT).as_posix(), "sha256": sha(CORPUS)},
        "prior_frame": {"path": PRIOR.relative_to(ROOT).as_posix(), "sha256": sha(PRIOR)},
        "protocol_sha256": sha(OWN / "PROTOCOL.md"),
        "code_sha256": sha(Path(__file__)),
        "annotations_sha256": sha(OWN / "source-observations.json"),
        "sources": sources,
        "local_object_joins_sha256": sha(local / "object-joins.json"),
        "freshness": "source and identity audit; no fresh inscription statistic evaluated",
    }
    (out / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(changes, indent=2))


if __name__ == "__main__":
    main()
