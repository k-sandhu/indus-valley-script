"""Check corrected package bookkeeping and saved-field claims; run no old analysis."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def load(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def pointer(obj, path):
    for part in path.strip("/").split("/"):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def main():
    inv = load(PACKAGE / "inventory.json")
    src = load(PACKAGE / "sources.json")
    candidates = {c["id"]: c for c in inv["candidates"]}
    outcomes = []

    def check(name, passed, details=None):
        outcomes.append(dict(check=name, passed=bool(passed), details=details))

    coverage = subprocess.run([sys.executable, str(PACKAGE / "audit_coverage.py")], cwd=ROOT, capture_output=True, text=True)
    check("registry_coverage", coverage.returncode == 0, coverage.stdout.strip() or coverage.stderr.strip())
    for c in candidates.values():
        for path in c["evidence"]:
            check("evidence_exists:" + c["id"] + ":" + path, (ROOT / path.split("#")[0]).exists())
        for field in c["evidence_fields"]:
            if "#/" in field:
                path, key = field.split("#", 1)
                try:
                    pointer(load(ROOT / path), key)
                    check("field_exists:" + field, True)
                except (KeyError, IndexError, TypeError, ValueError, OSError) as exc:
                    check("field_exists:" + field, False, str(exc))
        check("original_statuses:" + c["id"], set(c["registry_ids"]) == set(c["original_registry_statuses"]))
    for claim in inv["correction_claim_checks"]:
        observed = pointer(load(ROOT / claim["source_path"]), claim["source_pointer"])
        if claim["transform"] == "length":
            observed = len(observed)
        elif claim["transform"] == "percent_round_2":
            observed = round(observed * 100, 2)
        stated = candidates[claim["candidate_id"]]["numbers"][claim["inventory_key"]]
        check("saved_value:" + claim["candidate_id"] + ":" + claim["inventory_key"], observed == stated == claim["expected"], dict(source=observed, inventory=stated))
    held = candidates["PUBLIC-INDEX-COVERAGE"]
    check("rank6_held", held["rank"] == 6 and held["numbers"] == {} and held["priority_position"] is None and held["evidence"] == ["experiments/2026-10-06-evidence-census/"])
    source_ids = {s["id"] for s in src["sources"]}
    for c in candidates.values():
        check("source_ids:" + c["id"], set(c["novelty"]["sources"] + c["venue_sources"]) <= source_ids)
    for name in ["inventory.json", "sources.json", "README.md", "REPORT.md", "RETROSPECTIVE.md", "PROTOCOL.md", "registry-entry.json"]:
        data = (PACKAGE / name).read_bytes()
        decoded = data.decode("utf-8")
        check("utf8_no_bom:" + name, not data.startswith(b"\xef\xbb\xbf") and "\ufffd" not in decoded)
    check("priority_order", len(inv["recommended_priority_order"]) == 25 and len(set(inv["recommended_priority_order"])) == 25 and "PUBLIC-INDEX-COVERAGE" not in inv["recommended_priority_order"])
    check("first_pass_snapshot", all((PACKAGE / "first-pass" / n).exists() for n in ["inventory.json", "sources.json", "README.md", "REPORT.md", "RETROSPECTIVE.md", "PROTOCOL.md", "registry-entry.json", "audit_coverage.py", "REVIEW.md"]))
    checks = load(ROOT / "experiments/2026-10-02-dataset-landscape/main-v1/local-input-audit.json")
    check("landscape_saved_checks_passed", checks["all_checks_passed"] and len(checks["checks"]) == 39)
    gate = load(ROOT / "experiments/2026-10-02-six-hour/khipu-control/conservation-check/main-v1/aggregate.json")["rows"]
    for index, expected in [(71, [1, 2, 0, 197]), (79, [1, 0, 0, 199]), (87, [133, 9, 58, 0]), (95, [190, 1, 9, 0])]:
        row = gate[index]
        actual = [row.get(k, 0) for k in ["correct_relative", "wrong_relative", "abstained_ambiguity", "rejected_support"]]
        check("saved_gate_row:" + str(index), actual == expected, actual)
    result = dict(scope="Package bookkeeping and saved fields; no prior analysis rerun or source authentication", candidate_count=len(candidates), saved_claim_count=len(inv["correction_claim_checks"]), check_count=len(outcomes), all_checks_passed=all(c["passed"] for c in outcomes), checks=outcomes)
    (PACKAGE / "correction-checks.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["candidate_count", "saved_claim_count", "check_count", "all_checks_passed"]}))
    for check_result in outcomes:
        if not check_result["passed"]:
            print(json.dumps(check_result, ensure_ascii=False))
    return 0 if result["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
