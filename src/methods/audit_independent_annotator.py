"""Read-only source/unit audit of root's independent-annotator sensitivity."""
from collections import Counter
import json
from pathlib import Path
import sys

from conditional_structure import digest, load_records

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import independent_annotator as ia


unique, _ = load_records("data/normalized/lipi_clean_rtl_singleline.jsonl", unique=True)
allrows, _ = load_records("data/normalized/lipi_clean_rtl_singleline.jsonl")
raw = [json.loads(line) for line in Path("data/normalized/mayig_faces.jsonl").read_text(encoding="utf-8").splitlines()]
mapping = json.loads(Path("data/normalized/mayig_wells_class_crosswalk.json").read_text(encoding="utf-8"))["by_mayig_class"]
tests = []
for row in raw:
    if not (row["clear_transcription"] and row["line_count"] == 1 and row["length"] >= 3):
        continue
    sets = [{w.removeprefix("W").zfill(3) for w in mapping.get(p, {}).get("wells_candidates", [])} for p in row["signs_reading_rtl"]]
    if all(sets):
        tests.append(dict(row, sets=sets))
broad = [json.loads(line) for line in Path("data/normalized/lipi_observed_faces.jsonl").read_text(encoding="utf-8").splitlines()]
broad = [dict(row, artifact=str(row["object_family_id"]), seq=tuple(row["signs_reading_rtl"])) for row in broad]
complete_only, complete_only_removal = ia.conservative_training(unique, allrows, tests)
broader, broader_removal = ia.conservative_training(unique, broad, tests)
result_path = Path("results/independent_annotator/candidate_event_test.json")
published = json.loads(result_path.read_text(encoding="utf-8"))
ids = {row["record_id"] for row in published["records"]}
scored = [row for row in raw if row["record_id"] in ids]
family_counts = Counter(row["object_family_id"] for row in scored)
result = {
    "scope": "Read-only adversarial source/unit review; no root edits and no semantic claims.",
    "source_sha256": digest(__file__), "root_source_sha256": digest("src/independent_annotator.py"),
    "root_result_sha256": digest(result_path), "mapped_eligible_tests": len(tests),
    "complete_only_identity_exclusion": complete_only_removal,
    "broader_observational_identity_exclusion": broader_removal,
    "complete_only_train_texts": len(complete_only), "broader_train_texts": len(broader),
    "identical_retained_record_ids": {r["record_id"] for r in complete_only} == {r["record_id"] for r in broader},
    "saved_result_matches_current_source": published["source_sha256"] == digest("src/independent_annotator.py"),
    "scored_faces": len(scored), "scored_physical_source_objects": len(family_counts),
    "multiple_scored_faces_per_object": {key: count for key, count in family_counts.items() if count > 1},
    "observed_generic_object_types": dict(Counter(row["object_type"] for row in scored)),
    "recorded_model_stratum": published.get("main_test_metadata_assumption", ["Mohenjo-daro", "SEAL:S"]),
    "main_candidate_event_result": published["all_clear_weighting"],
    "unspecified_subtype_sensitivity": published.get("unspecified_seal_subtype_sensitivity"),
    "fully_supported_candidate_sensitivity": published.get("all_fine_candidates_training_supported_sensitivity"),
    "math_review": "The forward filter sums allowed fine-code events and propagates their normalized posterior through each row-normalized PMB transition. It is correct for this time-varying Markov model; candidate events may overlap and therefore do not define a normalized P-label alphabet.",
    "qualifications": [
        "All current scored faces come from distinct source objects. The updated bootstrap also groups physical artifact aliases and identical P strings, protecting future multi-face reuse.",
        "The updated implementation uses the full observational source register; this leaves the present eligible training IDs identical to the complete-only identity rule.",
        "Generic seal metadata does not independently certify the SEAL:S subtype. The updated source declares that assumption and adds an unspecified-subtype sensitivity.",
        "Unsupported candidates are removed from scoring, so the estimand concerns training-supported candidate events. The fully supported subset is a useful sensitivity, not a complete-corpus validation.",
        "Model selection uses fine-code training likelihood, rather than independently observed coarse-event likelihood; keep the baseline's stated selection scope precise.",
        "The coarse schema and source photographs derive from shared historical catalogues. This is independent annotation, not independent archaeological evidence or decoded semantics.",
    ],
}
target = Path("research/methods/independent_annotator_audit.json")
target.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({k: value for k, value in result.items() if k not in {"qualifications", "math_review"}}, indent=2))
