"""Check saved counts and hashes without rerunning the audit or a real model."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("unit_readiness_audit", PACKAGE / "audit.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    saved = json.loads((PACKAGE / "readiness-v1.json").read_text(encoding="utf-8"))
    checks = {}
    for source in saved["provenance"]["inputs"]:
        checks["source:" + source["role"]] = audit.digest(ROOT / source["path"]) == source["sha256"]
    checks["original_audit_code_preserved"] = audit.digest(PACKAGE / "audit-v1.py") == saved["provenance"]["code_sha256"]
    checks["protocol_unchanged"] = audit.digest(PACKAGE / "PROTOCOL.md") == saved["provenance"]["protocol_sha256"]
    counts = {}
    forbidden = {"signs", "signs_visual_ltr", "signs_reading_rtl", "text_code_visual_ltr", "words", "units"}
    for output in saved["local_outputs"]:
        path = ROOT / output["path"]
        checks["queue_hash:" + path.name] = audit.digest(path) == output["sha256"]
        with path.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        counts[path.name] = len(rows)
        checks["queue_has_no_text_payload:" + path.name] = not (set(rows[0]) & forbidden)
        key = "face_id" if path.name.startswith("divided") else "object_id" if path.name.startswith("multiface") else "source_row_id"
        checks["queue_ids_unique:" + path.name] = len({r[key] for r in rows}) == len(rows)
    checks["queue_counts"] = counts == {"divided-face-queue.csv": 118, "multiface-queue.csv": 881, "candidate-cohort-queue.csv": 358}
    checks["complete_and_partial_synthetic_semantics"] = json.loads((PACKAGE / "segmentation-synthetic.json").read_text(encoding="utf-8"))["pass"]
    checks["synthetic_freeze_and_spending_guards"] = json.loads((PACKAGE / "shots-synthetic.json").read_text(encoding="utf-8"))["pass"]
    # Generated metadata exercises consumer failures before the real register arrives.
    with tempfile.TemporaryDirectory(prefix="unit-readiness-") as tmp:
        folder = Path(tmp)
        objects = folder / "objects.jsonl"
        faces = folder / "faces.jsonl"
        # register_check records paths relative to ROOT, so replace its reporting root only here.
        oldroot = audit.ROOT
        audit.ROOT = folder
        try:
            objects.write_text(json.dumps({"object_id": "LIPI:1"}) + "\n", encoding="utf-8")
            faces.write_text(json.dumps({"face_id": "LIPI:1.1", "object_id": "LIPI:1"}) + "\n", encoding="utf-8")
            checks["register_accepts_valid_parent"] = audit.register_check(folder)["status"] == "checked"
            objects.write_text(objects.read_text(encoding="utf-8") * 2, encoding="utf-8")
            checks["register_rejects_duplicate_object"] = "duplicate object ids" in audit.register_check(folder)["errors"]
            objects.write_text(json.dumps({"object_id": "LIPI:2"}) + "\n", encoding="utf-8")
            checks["register_rejects_missing_parent"] = "face parent absent" in audit.register_check(folder)["errors"]
            faces.write_text(json.dumps({"face_id": "other:1", "object_id": "LIPI:2"}) + "\n", encoding="utf-8")
            checks["register_rejects_wrong_namespace"] = "unexpected provisional ID namespace" in audit.register_check(folder)["errors"]
        finally:
            audit.ROOT = oldroot
    result = {"schema_version": "1.0", "checks": checks, "pass": all(checks.values()),
              "queue_counts": counts, "scope": "author verification of saved artifacts and generated malformed-register inputs; no independent archaeological review"}
    audit.write_json(args.out, result)
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
