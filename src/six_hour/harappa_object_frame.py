"""Build a source-defined object frame and preserve bounded acquisition records."""
from __future__ import annotations

import argparse
import copy
import csv
from collections import defaultdict, Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/2026-10-02-six-hour/harappa-object-frame"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cisi_base(s: str) -> str | None:
    m = re.fullmatch(r"([A-Za-z]+)-?(\d+)(?:[A-Za-z])?", s.strip())
    return f"{m.group(1).upper()}-{int(m.group(2))}" if m else None


def build_frame(output: Path) -> None:
    source = ROOT / "data/normalized/lipi_observed_faces.jsonl"
    indexed = defaultdict(list)
    rows = [json.loads(s) for s in source.read_text(encoding="utf-8").splitlines() if s.strip()]
    for row in rows:
        base = cisi_base(row["source_cisi"])
        if base:
            indexed[base].append(row)
    groups = {"copied_tablets": range(2218, 2240), "sealings_and_stopper": range(1719, 1726),
              "stamped_vessels": range(1727, 1767), "rectangular_seals": range(1704, 1716)}
    frame, hints = [], []
    for group, numbers in groups.items():
        for n in numbers:
            target = f"H-{n}"
            matches = indexed.get(target, [])
            families = sorted({row["object_family_id"] for row in matches}, key=int)
            frame.append({"target_id": target, "group": group, "export_family_ids": families,
                          "export_face_ids": [r["record_id"] for r in matches], "export_face_count": len(matches),
                          "export_join_status": "absent" if not matches else "unique-family" if len(families) == 1 else "ambiguous-family",
                          "primary_registration": None, "primary_excavation_unit": None, "primary_item": None,
                          "primary_museum_accession": None, "primary_source_links": [], "source_image_status": "not-yet-coded"})
            for row in matches:
                hints.append({"target_id": target, "record_id": row["record_id"], "metadata": row["metadata"]})
    assert len(frame) == 81 and len({r["target_id"] for r in frame}) == 81
    assert Counter(r["group"] for r in frame) == {"copied_tablets": 22, "sealings_and_stopper": 7, "stamped_vessels": 40, "rectangular_seals": 12}
    payload = {"created_utc": now(), "protocol": "experiments/2026-10-02-six-hour/harappa-object-frame/PROTOCOL.md",
               "code_sha256": sha(Path(__file__)), "input": {"path": source.relative_to(ROOT).as_posix(), "sha256": sha(source)},
               "frame_size": len(frame), "join_statuses": dict(Counter(r["export_join_status"] for r in frame)), "objects": frame,
               "provenance": "Target IDs follow the published groups; export links are computed joins, with source assertions added in a separate endpoint."}
    write_json(output / "frame.json", payload)
    shutil.copyfile(Path(__file__), output / "code_snapshot.py")
    write_json(BASE / "local-witness/export-hints.json", {"source_sha256": sha(source), "rights_status": "derivative metadata local-only", "rows": hints})
    print(json.dumps({"output": str(output), "frame_size": len(frame), "join_statuses": payload["join_statuses"]}, indent=2))


def acquire(url: str, source_id: str, extension: str) -> None:
    import requests
    if not re.fullmatch(r"[a-z0-9_-]+", source_id):
        raise ValueError("source_id must be a plain lowercase identifier")
    target = BASE / "local-witness" / f"{source_id}.{extension.lstrip('.')}"
    record_path = BASE / "acquisition" / f"{source_id}.json"
    if target.exists() or record_path.exists():
        raise FileExistsError(source_id)
    record = {"source_id": source_id, "url": url, "requested_utc": now(), "access_method": "ordinary HTTPS request",
              "rights_status": "rights-unverified; local-only witness"}
    try:
        response = requests.get(url, timeout=50)
        record.update({"final_url": response.url, "http_status": response.status_code, "bytes": len(response.content),
                       "content_type": response.headers.get("content-type")})
        if response.status_code == 200:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(response.content)
            record.update({"local_path": target.relative_to(ROOT).as_posix(), "sha256": sha(target)})
            if response.content.startswith(b"%PDF"):
                import fitz
                record["format_verified"] = "PDF"
                record["pages"] = len(fitz.open(target))
            elif extension.lower() in {"jpg", "jpeg", "png", "gif", "webp"}:
                from PIL import Image
                with Image.open(target) as im:
                    record.update({"format_verified": im.format, "dimensions": list(im.size)})
            else:
                record["format_verified"] = "HTML or text; identity requires inspection"
    except Exception as exc:
        record.update({"error_type": type(exc).__name__, "error": str(exc)})
    record["completed_utc"] = now()
    write_json(record_path, record)
    print(json.dumps(record, indent=2))


def render(source: Path, pages: list[int], source_id: str, dpi: int = 180) -> None:
    binary = shutil.which("pdftoppm")
    if not binary:
        raise FileNotFoundError("pdftoppm not found; use the bundled Poppler binary")
    out = BASE / "local-witness" / "renders"
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for page in pages:
        prefix = out / f"{source_id}-pdf{page}"
        target = Path(str(prefix) + ".png")
        if target.exists():
            raise FileExistsError(target)
        subprocess.run([binary, "-f", str(page), "-l", str(page), "-r", str(dpi), "-singlefile", "-png", str(source), str(prefix)], check=True, capture_output=True)
        from PIL import Image
        with Image.open(target) as im:
            size = list(im.size)
        records.append({"pdf_page_one_based": page, "path": target.relative_to(ROOT).as_posix(), "sha256": sha(target), "dimensions": size})
    write_json(BASE / "acquisition" / f"{source_id}-renders.json", {"source_path": source.relative_to(ROOT).as_posix(), "source_sha256": sha(source),
               "rendered_utc": now(), "renderer": "Poppler pdftoppm", "dpi": dpi, "pages": records})
    print(json.dumps(records, indent=2))


def parse_registration(value: str) -> dict:
    match = re.fullmatch(r"(H\d{2,4}-\d+)/(\d+)-(\d+)", value)
    if not match:
        raise ValueError(f"Unrecognized source registration: {value}")
    return {"literal": value, "registration": match[1], "excavation_unit": match[2], "item": match[3]}


def annotation_endpoint(output: Path) -> None:
    """Join preserved descriptive observations to the complete object frame.

    Sign sequences are never read here. Caption registrations match only the
    derivative identifier field, and the join operates at physical-object level.
    """
    if output.exists():
        raise FileExistsError(output)
    source = ROOT / "data/normalized/lipi_observed_faces.jsonl"
    source_rows = [json.loads(s) for s in source.read_text(encoding="utf-8").splitlines() if s.strip()]
    reg_index = defaultdict(list)
    for row in source_rows:
        found = re.search(r"\b(H\d{2,4}-\d+)", row["metadata"].get("excavation-idno", ""))
        if found:
            reg_index[found[1]].append(row)

    def join(registration: str) -> dict:
        matches = reg_index.get(registration, [])
        targets = sorted({cisi_base(r["source_cisi"]) for r in matches if cisi_base(r["source_cisi"])})
        families = sorted({r["object_family_id"] for r in matches}, key=int)
        return {"registration": registration, "target_candidates": targets, "export_family_ids": families,
                "export_face_ids": [r["record_id"] for r in matches],
                "status": "unique-object" if len(targets) == len(families) == 1 else "absent" if not matches else "ambiguous-object",
                "basis": "exact primary-caption registration matched to derivative export identifier"}

    read = lambda name: json.loads((BASE / name).read_text(encoding="utf-8"))
    initial = read("initial/frame.json")
    first = read("figure4-first-observations.json")
    revision = read("figure4-native-reinspection.json")
    caption = read("figure4-caption-ledger.json")
    additional = read("additional-observations.json")
    beas = read("beas-observations.json")
    frame = copy.deepcopy(initial["objects"])
    frame_index = {r["target_id"]: r for r in frame}
    observations = {r["specimen"]: copy.deepcopy(r) for r in first["tablets"]}
    for change in revision["changes"]:
        row = observations[change["specimen"]]
        assert row[change["field"]] == change["first_value"]
        row[change["field"]] = change["revised_value"]
    stroke_counts = {(r["specimen"], r["side"]): r["separate_upright_strokes"] for r in revision["stroke_count_observations"]}
    crop_index = {r["specimen"]: r for r in read("figure4-native-crop-manifest.json")["crops"]}
    physical_objects, face_observations, registrations = [], [], []

    def add_to_frame(target: str, registration: dict, source_id: str, coordinate: dict, observation_id: str) -> None:
        if target not in frame_index:
            return
        item = frame_index[target]
        assert item["primary_registration"] is None
        item.update({"primary_registration": registration["registration"], "primary_excavation_unit": registration["excavation_unit"],
                     "primary_item": registration["item"], "primary_identifier_literal": registration["literal"],
                     "primary_source_links": [{"source_id": source_id, "coordinate": coordinate}],
                     "source_image_status": "inspected-drawing", "observation_id": observation_id,
                     "primary_identifier_basis": "published-caption", "face_alignment_to_export": "unassigned; object-level join only"})

    for item in caption["registrations"]:
        specimen = item["specimen"]
        registration = parse_registration(item["literal"])
        link = join(registration["registration"])
        assert link["status"] == "unique-object"
        target = link["target_candidates"][0]
        observation_id = f"MK2000-F4-{specimen}"
        coordinate = {"pdf_page_one_based": 15, "printed_page": 334, "figure": "4", "specimen": specimen}
        registrations.append({"observation_id": observation_id, "source_id": "meadow-kenoyer2000", "source_registration": registration,
                              "caption_coordinate": caption["caption_coordinate"], "join": link, "in_target_frame": target in frame_index})
        add_to_frame(target, registration, "meadow-kenoyer2000", coordinate, observation_id)
        common = {"observation_id": observation_id, "target_id": target, "in_target_frame": target in frame_index,
                  "source_id": "meadow-kenoyer2000", "source_coordinate": coordinate, "registration": registration,
                  "witness_type": "drawing", "source_crop": {"path": crop_index[specimen]["path"], "sha256": crop_index[specimen]["sha256"]},
                  "museum_accession": None, "physical_dimensions_mm": None,
                  "missing_identifiers": "museum accession absent from this caption", "export_join": link}
        if specimen == 1:
            seal = first["comparison_seal"]
            common.update({"type": "seal", "material": {"value": "steatite", "basis": "published-caption"},
                           "phase": {"value": "contemporary or nearly contemporary with the late-3B tablet group", "basis": "published-description ceramic comparison", "coordinate": {"pdf_page_one_based": 17, "printed_page": 336}},
                           "physical_action": {"value": "engraved seal used to make impressions", "basis": "published classification and inferred physical operation"},
                           "attachment": {"value": seal["attachment"], "basis": "visible-in-source-figure"},
                           "motif": {"visible": seal["motif"], "published_name": "unicorn", "published_basis": "published-description"},
                           "displayed_inscribed_faces": 1})
            face_observations.append({"observation_id": observation_id, "target_id": target, "side": "face", "basis": "visible-in-source-figure",
                                      "source_coordinate": coordinate, "layout": seal["sign_layout"], "broad_graphic_unit_count": None,
                                      "separate_upright_stroke_count": None, "polarity": seal["polarity"]})
        else:
            observed = observations[specimen]
            group = item["published_manufacturing_group"]
            association = "clump" if registration["excavation_unit"] == "8040" else "near-clump" if specimen in {9, 16} else "scattered"
            common.update({"type": "incised tablet", "material": {"value": "fired steatite", "basis": "published-caption and description"},
                           "phase": {"value": "late Period 3B", "basis": "published-description; wall and dump sequence before Period 3C", "coordinate": {"pdf_page_one_based": 14, "printed_page": 333}},
                           "physical_action": {"value": "three faces separately incised before firing", "basis": "published-description"},
                           "cross_section": {"value": "triangular", "basis": "visible-in-source-figure"},
                           "attachment": {"value": first["common_tablet_observations"]["visible_attachment_feature"], "basis": "visible-in-source-figure"},
                           "published_engraver_group": {"value": group, "basis": "authors' microscopic mould examination; interpretation", "coordinate": {"pdf_page_one_based": 16, "printed_page": 335}},
                           "deposition_association": {"value": association, "basis": "published-description, Figure 2 and caption unit/item join"},
                           "displayed_inscribed_faces": 3, "preservation_note": observed.get("preservation_note"),
                           "prior_inspected": specimen == 18})
            for side in ["top", "middle", "bottom"]:
                form = "C" if side == "top" else observed[f"{side}_form"]
                position = "left" if side == "top" else observed[f"{side}_position"]
                count = stroke_counts.get((specimen, side))
                face_observations.append({"observation_id": observation_id, "target_id": target, "side": side,
                                          "source_coordinate": {**coordinate, "display_side": side}, "basis": "visible-in-source-figure",
                                          "layout": "complex form beside short upright strokes" if form is not None else "dense hatching; grouping unresolved",
                                          "descriptive_form": form, "form_display_position": position,
                                          "broad_graphic_unit_count": 2 if form is not None else None,
                                          "separate_upright_stroke_count": count,
                                          "count_status": "counted in native pixels" if count is not None else "unassigned; published three-or-four-stroke description kept separate",
                                          "polarity": "source drawing of an incised tablet; mirror relation unreported",
                                          "catalogue_face_alignment": None})
        physical_objects.append(common)

    for item in additional["observations"]:
        registration = parse_registration(item["registration_literal"])
        link = join(registration["registration"])
        assert link["status"] == "unique-object" and link["target_candidates"] == [item["join_target"]]
        observation_id = f"{item['source_id']}-F4-{item['source_coordinate']['specimen']}"
        registrations.append({"observation_id": observation_id, "source_id": item["source_id"], "source_registration": registration,
                              "caption_coordinate": item["source_coordinate"], "join": link, "in_target_frame": True})
        add_to_frame(item["join_target"], registration, item["source_id"], item["source_coordinate"], observation_id)
        visible, published = item["visible_fields"], item["published_fields"]
        physical_objects.append({"observation_id": observation_id, "target_id": item["join_target"], "in_target_frame": True,
                                 "source_id": item["source_id"], "source_coordinate": item["source_coordinate"], "registration": registration,
                                 "type": "seal", "material": {"value": published["material"], "basis": item["published_fields_basis"]},
                                 "phase": {"value": published["period_literal"], "basis": item["dating_basis"]},
                                 "findspot": {"value": published["findspot"], "basis": item["published_fields_basis"]},
                                 "find_context": published.get("context_literal"), "physical_action": item["physical_action"],
                                 "witness_type": visible["witness_type"], "displayed_inscribed_faces": 1,
                                 "attachment": {"value": visible["attachment"], "basis": "visible-in-source-figure"},
                                 "cross_section": {"value": visible["cross_section"], "basis": "visible-in-source-figure"},
                                 "source_scale": visible["source_scale"], "physical_dimensions_mm": None, "museum_accession": None,
                                 "export_join": link})
        face_observations.append({"observation_id": observation_id, "target_id": item["join_target"], "side": "face", "basis": "visible-in-source-figure",
                                  "source_coordinate": item["source_coordinate"], "layout": visible["graphic_layout"],
                                  "broad_graphic_unit_count": visible["broad_graphic_unit_count"], "separate_upright_stroke_count": None,
                                  "polarity": visible["polarity"]})

    for fragment in beas["fragments"]:
        observation_id = fragment["witness_id"]
        coordinate = {"figure": "12", "region": fragment["source_image_region"]}
        physical_objects.append({"observation_id": observation_id, "target_id": None, "in_target_frame": False, "source_id": "beas-mapping-project",
                                 "source_coordinate": coordinate, "type": "stamped vessel fragment", "witness_type": "photograph",
                                 "material": {"value": "ceramic", "basis": "published-description and visible photograph"},
                                 "physical_action": beas["physical_action"], "phase": {"value": None, "basis": beas["dating_basis"]},
                                 "registration": None, "museum_accession": None, "physical_dimensions_mm": None,
                                 "displayed_inscribed_faces": 1, "findspot": {"value": beas["published_group_fields"]["site_literal"], "basis": "published-description"},
                                 "visible_fields": fragment, "visible_fields_basis": "visible-in-source-figure", "source_scale": beas["dimensions"]["source_scale"]})
        face_observations.append({"observation_id": observation_id, "target_id": None, "side": "exterior fragment surface", "source_coordinate": coordinate,
                                  "basis": "visible-in-source-figure", "layout": fragment["internal_graphics"], "broad_graphic_unit_count": None,
                                  "separate_upright_stroke_count": None, "polarity": fragment["polarity"], "stamp_boundary": fragment["stamp_boundary"]})

    tablets = [r for r in physical_objects if r["type"] == "incised tablet"]
    assert len(tablets) == 22 and len(registrations) == 25
    assert len(physical_objects) == 29 and len(face_observations) == 73
    assert sum(r["in_target_frame"] for r in physical_objects) == 24
    assert sum(r["primary_registration"] is not None for r in frame) == 24
    assert {r["target_id"] for r in frame if r["primary_registration"] is not None and r["group"] == "copied_tablets"} == {f"H-{n}" for n in range(2218, 2240)}
    assert Counter(r["registration"]["excavation_unit"] for r in tablets)["8040"] == 16
    table_summary = []
    for group in [1, 2, 3]:
        subset = [r for r in tablets if r["published_engraver_group"]["value"] == group]
        specimen_ids = {r["source_coordinate"]["specimen"] for r in subset}
        f = [r for r in face_observations if r.get("source_coordinate", {}).get("specimen") in specimen_ids and r["source_coordinate"].get("figure") == "4" and r.get("descriptive_form") is not None]
        # The source ID is implicit in descriptive_form, which exists only for these tablets.
        table_summary.append({"published_group": group, "objects": len(subset), "deposition_associations": dict(Counter(r["deposition_association"]["value"] for r in subset)),
                              "middle_forms": dict(Counter(observations[n]["middle_form"] for n in specimen_ids)),
                              "readable_angle_positions": dict(Counter(r["form_display_position"] for r in f if r["descriptive_form"] == "A")),
                              "readable_diamond_positions": dict(Counter(r["form_display_position"] for r in f if r["descriptive_form"] == "D")),
                              "unresolved_lower_faces": sum(observations[n][side+"_form"] is None for n in specimen_ids for side in ["middle", "bottom"])})

    target_faces = [r for r in face_observations if r["target_id"] in frame_index]
    summary = {"target_frame": 81, "initial_export_joined_objects": 72, "initial_export_absent_objects": 9,
               "primary_image_objects_in_frame": 24, "primary_image_objects_by_group": dict(Counter(frame_index[r["target_id"]]["group"] for r in physical_objects if r["in_target_frame"])),
               "target_objects_without_image_observation": [r["target_id"] for r in frame if r["primary_registration"] is None],
               "primary_registration_joins": 25, "unresolved_registration_joins": 0, "source_objects_visible": 29,
               "source_objects_outside_frame_visible": 5, "reported_object_without_image": beas["unresolved_case"],
               "source_faces_visible": 73, "source_faces_in_target_frame": len(target_faces),
               "tablet_faces": 66, "tablet_lower_face_form_unresolved": sum(r[side+"_form"] is None for r in observations.values() for side in ["middle", "bottom"]),
               "tablet_faces_with_direct_stroke_count": len(stroke_counts), "tablet_source_unit_counts": dict(Counter(r["registration"]["excavation_unit"] for r in tablets)),
               "tablet_group_summary": table_summary, "direct_numeric_dimensions": 0, "reported_museum_accessions": 0,
               "witness_types": dict(Counter(r["witness_type"] for r in physical_objects)),
               "phase_labels_in_frame": dict(Counter(r["phase"]["value"] for r in physical_objects if r["in_target_frame"])),
               "display_convention": "top/middle/bottom and left/right are positions in a published drawing; no exported A/B/C face alignment is assigned"}
    paths = [BASE / n for n in ["PROTOCOL.md", "FIRST-IMAGE-BLOCK.md", "ADDITIONAL-IMAGE-BLOCK.md", "initial/frame.json", "figure4-first-observations.json",
                              "figure4-native-reinspection.json", "figure4-caption-ledger.json", "additional-observations.json", "beas-observations.json",
                              "figure4-native-crop-manifest.json", "source-access-log.json"]]
    paths += [source, ROOT / "research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf", BASE / "local-witness/kenoyer-meadow2005-harappa.pdf",
              BASE / "local-witness/meadow-kenoyer2001-part3.html", BASE / "local-witness/meadow-kenoyer2001-figure4.gif", BASE / "local-witness/beas-figure12.jpg"]
    payload = {"created_utc": now(), "code_sha256": sha(Path(__file__)), "inputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in paths],
               "target_ledger": frame, "registration_ledger": registrations, "physical_objects": physical_objects, "face_observations": face_observations,
               "reported_missing_image_object": beas["unresolved_case"], "summary": summary}
    write_json(output / "results.json", payload)
    shutil.copyfile(Path(__file__), output / "code_snapshot.py")
    with (output / "target-ledger.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["target_id", "group", "export_join_status", "export_face_count", "primary_registration", "primary_excavation_unit", "primary_item", "primary_museum_accession", "source_image_status", "observation_id"]
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(frame)
    with (output / "physical-faces.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["observation_id", "target_id", "side", "basis", "layout", "descriptive_form", "form_display_position", "broad_graphic_unit_count", "separate_upright_stroke_count", "polarity"]
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore"); writer.writeheader(); writer.writerows(face_observations)
    print(json.dumps(summary, indent=2))


def display_summary(source: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(output)
    payload = json.loads(source.read_text(encoding="utf-8"))
    objects = {r["observation_id"]: r for r in payload["physical_objects"] if r["type"] == "incised tablet"}
    faces = defaultdict(dict)
    for face in payload["face_observations"]:
        if face["observation_id"] in objects:
            faces[face["observation_id"]][face["side"]] = face
    patterns, missing = defaultdict(list), []
    for object_id, sides in faces.items():
        obj = objects[object_id]
        middle, bottom = sides["middle"], sides["bottom"]
        support = {"observation_id": object_id, "target_id": obj["target_id"], "registration": obj["registration"]["literal"],
                   "published_group": obj["published_engraver_group"]["value"], "deposition_association": obj["deposition_association"]["value"]}
        if None in [middle["descriptive_form"], middle["form_display_position"], bottom["descriptive_form"], bottom["form_display_position"]]:
            missing.append(support)
            continue
        assert {middle["descriptive_form"], bottom["descriptive_form"]} == {"A", "D"}
        key = (middle["descriptive_form"], middle["form_display_position"], bottom["form_display_position"])
        patterns[key].append(support)
    result_patterns = [{"middle_form": k[0], "middle_position": k[1], "bottom_position": k[2], "count": len(v), "source_objects": v} for k, v in sorted(patterns.items())]
    counted_faces = [r for r in payload["face_observations"] if r["observation_id"] in objects and r["separate_upright_stroke_count"] is not None]
    result = {"created_utc": now(), "code_sha256": sha(Path(__file__)), "input_path": source.relative_to(ROOT).as_posix(), "input_sha256": sha(source),
              "protocol_path": (BASE / "DISPLAY-SUMMARY.md").relative_to(ROOT).as_posix(),
              "possible_classes_under_declared_coding": 8, "observed_classes": len(result_patterns), "resolved_object_pairs": sum(r["count"] for r in result_patterns),
              "unresolved_object_pairs": len(missing), "patterns": result_patterns, "missing_pairs": missing,
              "directly_counted_faces": counted_faces, "stroke_total_histogram": dict(Counter(r["separate_upright_stroke_count"] for r in counted_faces)),
              "scope": "Descriptive post-annotation summary of published display arrangements; physical turn order and exported face alignment remain unassigned."}
    assert result["resolved_object_pairs"] + result["unresolved_object_pairs"] == 22
    assert len(counted_faces) == 7
    write_json(output / "results.json", result)
    shutil.copyfile(Path(__file__), output / "code_snapshot.py")
    print(json.dumps({k: result[k] for k in ["possible_classes_under_declared_coding", "observed_classes", "resolved_object_pairs", "unresolved_object_pairs", "stroke_total_histogram"]}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    frame = sub.add_parser("frame")
    frame.add_argument("--output", type=Path, default=BASE / "initial")
    fetch = sub.add_parser("acquire")
    fetch.add_argument("--url", required=True)
    fetch.add_argument("--source-id", required=True)
    fetch.add_argument("--extension", required=True)
    draw = sub.add_parser("render")
    draw.add_argument("--source", type=Path, required=True)
    draw.add_argument("--source-id", required=True)
    draw.add_argument("--pages", type=int, nargs="+", required=True)
    draw.add_argument("--dpi", type=int, default=180)
    annotate = sub.add_parser("annotate")
    annotate.add_argument("--output", type=Path, default=BASE / "annotated")
    summary = sub.add_parser("display-summary")
    summary.add_argument("--input", type=Path, default=BASE / "annotated/results.json")
    summary.add_argument("--output", type=Path, default=BASE / "display-summary")
    args = parser.parse_args()
    if args.command == "frame":
        build_frame(args.output)
    elif args.command == "acquire":
        acquire(args.url, args.source_id, args.extension)
    elif args.command == "render":
        render(args.source.resolve(), args.pages, args.source_id, args.dpi)
    elif args.command == "annotate":
        annotation_endpoint(args.output)
    elif args.command == "display-summary":
        display_summary(args.input, args.output)


if __name__ == "__main__":
    main()
