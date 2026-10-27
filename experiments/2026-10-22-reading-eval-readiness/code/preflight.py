"""Fail-closed manifest check before requesting a prospective shots read.

This validates declarations and pinned files. Independent review must establish
their truth; passing this check does not replace the shared shots loader.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

FREEDOMS = ("coverage", "alternatives", "empty_emissions", "deletion_budget",
            "alphabet_projection", "lexical_resources", "sense_and_attestation",
            "morphology", "direction_and_segmentation", "template_selection",
            "training", "tuning_budget")
REQUIRED = ("participant_id", "role", "family", "comparison_group", "claim", "sign_namespace", "mapping", "inputs",
            "construction_record", "freedom", "predictions", "controls",
            "calibration", "source_review", "cohort", "scorer", "freeze")
UNKNOWN = {"unknown", "unreviewed", "unresolved", "pending", "tbd", "todo"}


def unresolved(value, path="manifest"):
    errors = []
    if value is None:
        errors.append(f"{path}: null is unresolved")
    elif isinstance(value, float) and not math.isfinite(value):
        errors.append(f"{path}: nonfinite value")
    elif isinstance(value, str) and (not value.strip() or value.strip().casefold() in UNKNOWN):
        errors.append(f"{path}: empty or unresolved text")
    elif isinstance(value, dict):
        if not value:
            errors.append(f"{path}: empty object is unresolved")
        for key, item in value.items():
            errors.extend(unresolved(item, f"{path}.{key}"))
    elif isinstance(value, list):
        if not value:
            errors.append(f"{path}: empty list is unresolved")
        for index, item in enumerate(value):
            errors.extend(unresolved(item, f"{path}[{index}]"))
    return errors


def validate(manifest, root):
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]
    errors.extend(unresolved(manifest))

    def fields(record, required, label):
        if not isinstance(record, dict):
            errors.append(f"{label}: must be an object")
            return {}
        for key in required:
            if key not in record:
                errors.append(f"{label}.{key}: missing")
        return record

    def pinned(records, label):
        if not isinstance(records, list) or not records:
            errors.append(f"{label}: nonempty artifact list required")
            return
        for index, record in enumerate(records):
            item = fields(record, ("path", "sha256"), f"{label}[{index}]")
            path, expected = item.get("path"), item.get("sha256")
            if not isinstance(path, str) or not isinstance(expected, str):
                continue
            if not re.fullmatch("[0-9a-f]{64}", expected):
                errors.append(f"{label}[{index}]: invalid SHA256")
                continue
            target = (root / path).resolve()
            if not target.is_relative_to(root.resolve()):
                errors.append(f"{label}[{index}]: artifact must be inside declared root")
            elif not target.is_file():
                errors.append(f"{label}[{index}]: artifact missing")
            elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                errors.append(f"{label}[{index}]: artifact hash changed")

    fields(manifest, REQUIRED, "manifest")
    for key in ("participant_id", "role", "family", "comparison_group"):
        if not isinstance(manifest.get(key), str):
            errors.append(f"{key}: a string is required")
    if not isinstance(manifest.get("role"), str) or manifest["role"] not in {"proposal", "positive_control", "negative_control"}:
        errors.append("role: expected proposal, positive_control or negative_control")
    family = manifest.get("family")
    expected_task = {"phonetic_key": "key-calibration", "meaning_map": "meaning-map"}.get(family) if isinstance(family, str) else None
    if expected_task is None:
        errors.append("family: no reviewed shared scorer available for this family")
    pinned(manifest.get("inputs"), "inputs")
    claim = fields(manifest.get("claim"), ("title", "edition", "locator", "statement", "sources"), "claim")
    pinned(claim.get("sources"), "claim.sources")
    namespace = fields(manifest.get("sign_namespace"), ("name", "version", "crosswalk"), "sign_namespace")
    pinned(namespace.get("crosswalk"), "sign_namespace.crosswalk")
    pinned(manifest.get("mapping"), "mapping")
    pinned(manifest.get("construction_record"), "construction_record")
    fields(manifest.get("freedom"), FREEDOMS, "freedom")
    controls = fields(manifest.get("controls"), ("known_correct", "wrong"), "controls")
    for key in ("known_correct", "wrong"):
        if not isinstance(controls.get(key), list) or not controls[key]:
            errors.append(f"controls.{key}: nonempty participant list required")
        elif not all(isinstance(value, str) for value in controls[key]):
            errors.append(f"controls.{key}: participant IDs must be strings")
        elif len(controls[key]) != len(set(controls[key])):
            errors.append(f"controls.{key}: duplicate participant IDs")
    if all(isinstance(controls.get(key), list) and all(isinstance(value, str) for value in controls[key])
           for key in ("known_correct", "wrong")):
        if set(controls["known_correct"]) & set(controls["wrong"]):
            errors.append("controls: known-correct and wrong IDs must be distinct")
    for key in ("calibration", "source_review"):
        item = fields(manifest.get(key), ("status", "evidence"), key)
        if item.get("status") != "accepted":
            errors.append(f"{key}: independent accepted review required")
        pinned(item.get("evidence"), f"{key}.evidence")
    cohort = fields(manifest.get("cohort"), ("exposure_status", "identity_review",
                                            "exposure_review", "independent_units"), "cohort")
    if cohort.get("exposure_status") != "reviewed-unexamined":
        errors.append("cohort: exposure must be reviewed-unexamined")
    for key in ("identity_review", "exposure_review"):
        pinned(cohort.get(key), f"cohort.{key}")
    units = cohort.get("independent_units")
    if not isinstance(units, int) or isinstance(units, bool) or units < 1:
        errors.append("cohort.independent_units: positive integer required")
    scorer = fields(manifest.get("scorer"), ("task", "artifacts"), "scorer")
    if scorer.get("task") != expected_task:
        errors.append("scorer: task does not match family")
    pinned(scorer.get("artifacts"), "scorer.artifacts")
    predictions = manifest.get("predictions")
    if not isinstance(predictions, list) or not predictions:
        errors.append("predictions: nonempty list required")
    else:
        for index, prediction in enumerate(predictions):
            item = fields(prediction, ("id", "statistic_family", "null", "pass_rule",
                                       "min_units", "missingness_rule"), f"predictions[{index}]")
            minimum = item.get("min_units")
            if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1:
                errors.append(f"predictions[{index}].min_units: positive integer required")
            elif isinstance(units, int) and units < minimum:
                errors.append(f"predictions[{index}]: insufficient independent units")
    freeze = fields(manifest.get("freeze"), ("registered_participants", "frozen_participants",
                                             "confirmation_reads", "joint_credence_rule",
                                             "artifacts"), "freeze")
    registered = freeze.get("registered_participants")
    frozen = freeze.get("frozen_participants")
    if not isinstance(registered, list) or not registered or not all(isinstance(x, str) for x in registered):
        errors.append("freeze: registered participant IDs required")
    elif len(registered) != len(set(registered)):
        errors.append("freeze: duplicate registered participant IDs")
    elif not isinstance(frozen, list) or not all(isinstance(x, str) for x in frozen) or set(registered) != set(frozen):
        errors.append("freeze: every registered participant must be frozen")
    elif len(frozen) != len(set(frozen)):
        errors.append("freeze: duplicate frozen participant IDs")
    elif manifest.get("participant_id") not in registered:
        errors.append("freeze: current participant is not registered")
    else:
        for key in ("known_correct", "wrong"):
            values = controls.get(key)
            if isinstance(values, list) and any(value not in registered for value in values):
                errors.append(f"controls.{key}: unregistered control")
    if type(freeze.get("confirmation_reads")) is not int or freeze["confirmation_reads"] != 0:
        errors.append("freeze: this prospective gate requires zero prior confirmation reads")
    pinned(freeze.get("artifacts"), "freeze.artifacts")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    errors = validate(data, args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        json.dump({"task": "reading-eval-readiness/preflight", "pass": not errors,
                   "errors": errors, "scope": "Declaration and artifact integrity; review truth remains external"}, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"pass": not errors, "errors": len(errors)}))
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
