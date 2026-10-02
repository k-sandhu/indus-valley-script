"""Check contributor manifests and the claims used in the shared account."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import py_compile
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
checks = []


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(name, value):
    checks.append({"name": name, "passed": bool(value)})


for relative, field in [("regional-west/endpoint-manifest.json", "files"),
                        ("harappa-short-records/artifact-manifest.json", "artifacts")]:
    obj = read(HERE / relative)
    for item in obj[field]:
        path = ROOT / item["path"]
        check(f"{relative}: {path.name}: bytes", path.stat().st_size == item["bytes"])
        check(f"{relative}: {path.name}: hash", hashlib.sha256(path.read_bytes()).hexdigest()
              == item["sha256"])

novelty = read(HERE / "novelty/evidence-check.json")
check("novelty numeric checks", novelty["numeric_assertions_passed"])
check("novelty linked evidence", novelty["all_local_links_exist"])
regional = read(HERE / "regional-west/validation.json")
check("regional verification", regional["status"] == "pass" and
      len(regional["checks"]) == 7 and all(r["result"] == "pass" for r in regional["checks"]))
census = read(HERE / "regional-west/marked-weight-census-v2.json")
indus = read(HERE / "regional-west/indus-weight-audit.json")
check("regional endpoints available", bool(census) and bool(indus))
harappa = read(HERE / "harappa-short-records/main-v2/results.json")
check("Harappa population", harappa["objects"] == 22 and harappa["faces"] == 66)
check("Harappa module classes", harappa["exact_unordered_module_set_class_sizes"] == [20, 1, 1])
hr = read(HERE / "harappa-short-records/review-v1/checks.json")
check("Harappa scalar review", hr["passed"] == hr["checks"] == 241 and not hr["failures"])
south = read(HERE / "south-india/verification.json")
check("South source/results checks", south["status"] == "pass" and south["checks_total"] == 576)
sr = HERE / "south-india/independent-review.json"
check("South independent review available", sr.is_file())
if sr.is_file():
    audit = read(sr)
    check("South independent checks", audit["counts"]["checks"] ==
          audit["counts"]["passed"] == 317 and audit["counts"]["failed"] == 0)
    check("South independent property rows", audit["counts"]["membership_forms_compared"] == 194)
lothal = read(HERE / "lothal-contact/results.json")
lv = read(HERE / "lothal-contact/verification.json")
check("Lothal image checks", lv["all_passed"] and lv["check_count"] == 234)
check("Lothal resolved contact", lothal["G01"]["diagnostic_curvature_or_edge_objects"] == ["L-206"])
check("Lothal combined ranges", lothal["G02"]["reader_envelope_visible_zone_intervals"] ==
      {"L-161": [2, 4], "L-162": [3, 5], "L-163": [3, 5], "L-168": [2, 3]})
check("Lothal coverage scope", not lothal["G02"]["zone_comparability_established"] and
      lothal["G02"]["whole_object_totals_observed"] == 0)

preservation = read(HERE / "baseline-preservation.json")
baseline_bytes = subprocess.check_output(["git", "show", preservation["baseline_commit"] +
                                          ":knowledge/experiments/registry.json"], cwd=ROOT)
old = json.loads(baseline_bytes)
registry = read(ROOT / "knowledge/experiments/registry.json")
check("102 prior registry entries preserved", len(old["experiments"]) == 102 and
      registry["experiments"][:102] == old["experiments"])
check("107 registry entries", len(registry["experiments"]) == 107)
check("new entry values match declared additions", registry["experiments"][102:] ==
      read(HERE / "registry-additions.json"))
with tempfile.TemporaryDirectory(prefix="indus-connections-syntax-") as temp:
    for number, path in enumerate(sorted(HERE.rglob("*.py"))):
        if "__pycache__" in path.parts:
            continue
        try:
            py_compile.compile(str(path), cfile=str(Path(temp) / f"{number}.pyc"), doraise=True)
            check(f"syntax: {path.relative_to(HERE)}", True)
        except py_compile.PyCompileError:
            check(f"syntax: {path.relative_to(HERE)}", False)
result = {"created_utc": datetime.now(timezone.utc).isoformat(),
          "status": "pass" if all(r["passed"] for r in checks) else "fail",
          "checks_total": len(checks), "failures": [r for r in checks if not r["passed"]],
          "scope": "Preservation of contributor outputs, shared numerical claims and prior registry entries, plus Python syntax",
          "checks": checks}
(HERE / "integration-verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k != "checks"}))
raise SystemExit(0 if result["status"] == "pass" else 1)
