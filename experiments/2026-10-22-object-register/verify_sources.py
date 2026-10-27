"""Check copied raw values and uncertainty handling against the held inputs."""
import argparse
import collections
import json
from pathlib import Path

from build_register import ROOT, INPUTS, read, sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    run, out = Path(args.run), Path(args.output)
    if out.exists(): raise ValueError("Existing verification output refused")
    cache = {source: read(INPUTS[source]) for source in ["lipi", "website", "images", "cisi1", "cisi2", "excavation", "museums"]}
    by_record = {}
    for source in ["lipi", "website"]:
        by_record[source] = {str(r["record_id"]): r for r in cache[source]}
    for source in ["cisi1", "cisi2"]:
        by_record[source] = {r["cisi"]: r for r in cache[source]}
    by_record["excavation"] = {r["source_row_id"]: r for r in cache["excavation"]}
    reg = json.loads((run / "register-v2.json").read_text(encoding="utf-8"))
    objects = {r["id"]: r for r in reg["objects"]}
    all_accepted = {aid for table in ["objects", "contexts", "surfaces"] for row in reg[table] for cell in row["fields"].values() for aid in cell["assertion_ids"]}
    assertions = {a["id"]: a for a in reg["assertions"]}
    checked, skipped, errors, uncertainty = collections.Counter(), collections.Counter(), [], collections.Counter()
    values = [json.loads(line) for line in (run / "assertion-values.jsonl").read_text(encoding="utf-8").splitlines()]
    for value in values:
        source = value["source_id"]
        if source in {"cisi1", "cisi2"} and value.get("uncertainty") in {"bracketed", "unresolved-reader-disagreement"}:
            uncertainty[source] += 1
            if value["assertion_id"] in all_accepted: errors.append("uncertain_CISI_in_accepted_fields:" + value["assertion_id"])
        if value.get("uncertainty") == "implausible" and value["assertion_id"] in all_accepted: errors.append("implausible_measurement_in_accepted_fields")
        if source not in cache: skipped["inherited_or_other_source"] += 1; continue
        loc = value["locator"]
        if loc["path"] != INPUTS[source]: skipped["source_decision_file"] += 1; continue
        key, _, selector = loc["record"].partition("=")
        if key == "row_index": row = cache[source][int(selector)]
        elif source in by_record and key in {"record_id", "cisi", "source_row_id"}: row = by_record[source].get(selector)
        else: skipped["derived_family_or_other_locator"] += 1; continue
        if row is None: errors.append("record_missing:" + loc["record"]); continue
        field = loc["field"]
        if "," in field or ";" in field: skipped["composite_field_derivation"] += 1; continue
        expected = row
        if field.startswith("metadata."):
            expected = row.get("metadata", {}).get(field[len("metadata."):])
        else:
            for part in field.split("."):
                if not isinstance(expected, dict) or part not in expected:
                    expected = None; break
                expected = expected[part]
        if expected is None and field not in row and not field.startswith("metadata."):
            skipped["computed_or_nonnative_field"] += 1; continue
        if value["field"] == "image_pointer": skipped["generated_image_identifier"] += 1; continue
        if value["raw_value"] != expected: errors.append("raw_value_differs:" + str(value["assertion_id"]))
        checked[source] += 1
    hashes = {source: sha(ROOT / INPUTS[source]) for source in cache}
    for value in values:
        if value["source_id"] in hashes and value["locator"]["path"] == INPUTS[value["source_id"]] and value["source_sha256"] != hashes[value["source_id"]]: errors.append("source_hash_mismatch")
    result = {"status": "passed" if not errors else "failed", "direct_raw_values_checked": dict(checked), "checked_total": sum(checked.values()), "skipped_with_scope_reason": dict(skipped), "uncertain_CISI_assertions_withheld_from_accepted_fields": dict(uncertainty), "errors": sorted(set(errors))}
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
