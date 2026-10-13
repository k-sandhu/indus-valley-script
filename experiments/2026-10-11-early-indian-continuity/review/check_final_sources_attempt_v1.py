"""Check the final review's source identities, local disposition and prose repairs.

These are payload/locator checks following manual source reading. They cannot
authenticate a scholarly interpretation or recover an unobserved ancient event.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import fitz

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
ROOT = PACKAGE.parents[1]
CHECKS = []


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name, condition, **detail):
    CHECKS.append(dict(id=name, passed=bool(condition), **detail))


def main():
    output = HERE / "final-source-checks-v1.json"
    if output.exists():
        raise FileExistsError(output)
    memory = json.loads((PACKAGE / "memory/sources.json").read_text(encoding="utf-8"))
    for source in memory["sources"]:
        path = ROOT / source["witness_path"]
        check("memory-witness-" + source["id"], path.exists() and digest(path) == source["sha256"],
              path=source["witness_path"])
        check("memory-local-disposition-" + source["id"], source["disposition"] == "local-only")
    by_id = {s["id"]: s for s in memory["sources"]}
    check("allon-publication-identity", by_id["A22"]["publication_year"] == 2022
          and by_id["A22"]["title"] == "Early Buddhist Texts: Their Composition and Transmission"
          and "09499" in by_id["A22"]["doi"])
    check("witzel-1997-excerpt-depth", "Indexed" in by_id["W97"]["inspection_scope"]
          and "full" in by_id["W97"]["inspection_scope"].lower()
          and "blocked" in by_id["W97"]["inspection_scope"].lower())
    check("dave-2019-abstract-depth", "abstract" in by_id["D19"]["inspection_scope"].lower())
    institutions = json.loads((PACKAGE / "institutions/sources.json").read_text(encoding="utf-8"))
    I = {s["id"]: s for s in institutions}
    check("witzel-1995-transport-exception-disclosed", "disabled TLS" in I["S05"]["inspected_scope"]
          and "disabled TLS" in I["S06"]["inspected_scope"])
    check("witzel-1995-proof-pagination", "113" in I["S06"]["inspected_scope"] and "197" in I["S06"]["inspected_scope"])
    proof = fitz.open(ROOT / I["S06"]["witnesses"][0]["path"])
    proof_text = proof[112].get_text()
    check("witzel-primary-addition-list", "4.57.4-8" in proof_text
          and "later" in proof_text and "additions" in proof_text)
    rice = fitz.open(ROOT / I["S01"]["witnesses"][0]["path"])
    table_text = rice[13].get_text()
    check("rice-primary-PGW-exclusion", "four PGW" in table_text and "excluded" in table_text
          and "remaining six" in table_text)
    for name in ["run-v1/audit.json", "run-v2/audit.json", "audit.py", "audit-v2.py", "AMENDMENT-eligibility.md"]:
        check("institution-original-and-corrected-" + name, (PACKAGE / "institutions" / name).exists())
    memory_report = (PACKAGE / "memory/REPORT.md").read_text(encoding="utf-8")
    check("memory-other-discourse-witness-limit", "Gāndhārī variant" in memory_report
          and "received Pali wording" in memory_report and "DN27" in memory_report)
    check("memory-erasure-scope", "non-identification after stipulated erasure" in memory_report
          and "sophisticated stories arise automatically" in memory_report)
    check("memory-type-gate-scope", "zero propagated composition bounds" in memory_report
          and "explicit restrictive rule" in memory_report)
    coordinator = (PACKAGE / "coordinator/CONTROL-AND-MODEL.md").read_text(encoding="utf-8")
    check("coordinator-feedback-variants", "multiple workable variants" in coordinator
          and "reference procedure" in coordinator)
    check("coordinator-real-performance-target", "fire production" in coordinator and "Gandharva" in coordinator)
    check("coordinator-meaning-assessment-attributed", "their philological judgment" in coordinator
          and "circulated orally" in coordinator)
    check("coordinator-model-no-complexity-generation", "does not generate literary sophistication" in coordinator)
    report = (PACKAGE / "institutions/REPORT.md").read_text(encoding="utf-8")
    check("institution-intermediate-candidate-repair", "source-reported" in report.lower()
          and "candidate" in report.lower() and "Sanauli" in report)
    check("institution-core-removal-bounded", "in this inspected set" in report
          and "composed late" in report)
    check("institution-domestication-bounds-scope", "rounded published percentages" in report
          and "Immature bases retain" in report and "Removing either" in report)
    tracked = subprocess.run(["git", "ls-files", "--", "data/raw/2026-10-11-early-indian-continuity"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
    check("raw-witnesses-untracked", not tracked.strip())
    result = dict(scope="Final source identity, selected manually read locators, raw disposition and reporting repair presence",
                  checker_sha256=digest(Path(__file__)), checks=CHECKS,
                  passed=sum(x["passed"] for x in CHECKS), failed=sum(not x["passed"] for x in CHECKS))
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "failed": result["failed"]}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
