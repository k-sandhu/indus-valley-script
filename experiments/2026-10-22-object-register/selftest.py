"""Synthetic mutation checks for register safety; never reads Indus payloads."""
import copy
import json
from types import SimpleNamespace

from build_register import HERE, INPUTS, missing, number, dimension_present, key, read, validate


def fixture():
    schema = read(str((HERE / "schema-v2.json").relative_to(HERE.parents[1])))
    data = {"schema_version": "2.0", "status": "Exploratory", "selection_sha256": "synthetic", "sequence_policy": "No sign sequences; transcription payloads are local-only", **{name: [] for name in schema["$defs"]}}
    fields = lambda table: {name: missing("synthetic_fixture_unknown") for name in schema["$defs"][table]["properties"]["fields"]["required"]}
    obj = {"id": "LIPI:test", "selection_key": "test", "identity_status": "source-reported", "fields": fields("objects")}
    obj["fields"]["face_count"] = {"value": 1, "assertion_ids": ["A-test"], "missing_reason": None}
    data["objects"] = [obj]
    data["contexts"] = [{"id": "CTX:test", "object_id": obj["id"], "fields": fields("contexts")}]
    data["surfaces"] = [{"id": "LIPI:test.1", "object_id": obj["id"], "fields": fields("surfaces")}]
    data["sources"] = [{"id": "synthetic", "title": "Synthetic fixture", "authors": ["Repository research contributors"], "year": 2026, "year_missing_reason": None, "venue": "Local fixture", "url": "selftest.py", "version": "1", "access_status": "constructed", "quoted_words": 0, "creator_role": "repository contributor"}]
    data["assertions"] = [{"id": "A-test", "object_id": obj["id"], "field": "face_count", "value": 1, "source_id": "synthetic", "locator": {"path": str((HERE / "selftest.py").relative_to(HERE.parents[1])).replace("\\", "/"), "record": "fixture", "field": "face_count", "page_or_url": None, "page_missing_reason": "synthetic"}, "method": "constructed_fixture", "confidence": "source-reported", "review_status": "not-expert-reviewed"}]
    return SimpleNamespace(schema=schema, data=data, stats={"lipi": {"cisi_raw_usable": 4075, "any_positive_dimension_including_ranges": 3598}}, output_objects=[{"exposure_status": "unreviewed"}], values=[])


def main():
    base = fixture()
    expected = {"base_population_changed"}
    checks = [{"name": "synthetic_fixture_has_only_expected_population_failure", "passed": set(validate(base)) == expected}]
    mutations = [
        ("duplicate_object", lambda r: r.data["objects"].append(copy.deepcopy(r.data["objects"][0])), "duplicate_id"),
        ("absent_source", lambda r: r.data["sources"].clear(), "broken_source_id"),
        ("foreign_object_assertion", lambda r: r.data["assertions"][0].update(object_id="LIPI:another"), "foreign_object_assertion"),
        ("candidate_accepted", lambda r: r.data["assertions"][0].update(confidence="candidate"), "candidate_in_accepted_cell"),
        ("unknown_exposure_promoted", lambda r: r.output_objects[0].update(exposure_status="fresh"), "unsupported_freshness_assignment"),
        ("missing_reason", lambda r: r.data["objects"][0]["fields"]["material"].update(missing_reason=None), "missing_reason"),
    ]
    for name, mutate, signature in mutations:
        reg = copy.deepcopy(base); mutate(reg)
        errors = validate(reg)
        checks.append({"name": name, "passed": any(signature in e for e in errors)})
    checks.extend([
        {"name": "zero_is_not_a_dimension", "passed": number("0") is None and not dimension_present("0")},
        {"name": "positive_range_preserved_as_coverage_without_scalar", "passed": dimension_present("5 - 9") and number("5 - 9") is None},
        {"name": "nan_rejected", "passed": number("nan") is None},
        {"name": "catalogue_normalization", "passed": key("M-001A") == key("M-1")},
        {"name": "ambiguous_catalogue_string_not_normalized", "passed": key("M-1/M-2") is None},
    ])
    result = {"status": "passed" if all(c["passed"] for c in checks) else "failed", "kind": "synthetic mutation tests", "checks": checks}
    print(json.dumps(result, indent=2))
    if result["status"] != "passed": raise SystemExit(1)


if __name__ == "__main__": main()
