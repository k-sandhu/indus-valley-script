"""Inventory cards and 13–27 October attempts using the repository's parser.

Run from any directory with Python 3.13. Only inventory.json is written.
Missing package fields are inferred from evidence paths and marked explicitly.
"""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import kb  # Standard-library repository parser; no generated files are built.


def package_for(fields):
    if fields.get("package"):
        return fields["package"], "package"
    for value in fields.get("evidence", []):
        match = re.match(r"(experiments/2026-\d\d-\d\d-[^/]+)", value)
        if match:
            return match[1], "evidence"
    return None, None


def build():
    items = kb.index_items()
    model = (ROOT / "knowledge/WORKING-MODEL.md").read_text(encoding="utf-8-sig")
    baseline_path=PACKAGE/'baseline/WORKING-MODEL.md'
    baseline=baseline_path.read_text(encoding='utf-8-sig') if baseline_path.exists() else model
    findings, conjectures, attempts = [], [], []
    for item in items:
        fields = item["fields"]
        if item["kind"] == "finding":
            findings.append({key: fields.get(key) for key in
                             ("id", "title", "area", "status_class", "date", "registry_ids")}
                            | {"path": item["path"]})
        elif item["kind"] == "conjecture":
            conjectures.append({key: fields.get(key) for key in ("id", "title", "status", "credence")}
                               | {"path": item["path"], "linked_from_working_model":
                                  bool(re.search(r"\]\(conjectures/" + re.escape(Path(item["path"]).name)
                                                 + r"(?:#[^)]*)?\)", model)),
                                  "linked_before_this_pass": bool(re.search(r"\]\(conjectures/"+re.escape(Path(item["path"]).name)+r"(?:#[^)]*)?\)",baseline))})
    for item in items:
        if item["kind"] != "attempt":
            continue
        fields = item["fields"]
        package, origin = package_for(fields)
        match = re.search(r"2026-10-\d{2}", str(fields.get("date", "")) + " "
                          + str(package or "") + " " + item["id"])
        if not match or not date(2026, 10, 13) <= date.fromisoformat(match[0]) <= date(2026, 10, 27):
            continue
        cited_by = [f["id"] for f in findings if item["id"] in f["registry_ids"]]
        attempts.append({key: fields.get(key) for key in
                         ("id", "status_class", "verification_tier", "outcome")}
                        | {"date": match[0], "package": package, "package_origin": origin,
                           "outcome": fields.get("outcome", ""),
                           "cited_by_finding": bool(cited_by), "cited_by": cited_by,
                           "record": item["path"]})
    return {"schema_version": 1, "scope": "Cards and attempts dated 2026-10-13 through 2026-10-27; outcomes copied verbatim, missing tiers retained as null.",
            "counts": {"findings": len(findings), "conjectures": len(conjectures), "attempts": len(attempts)},
            "findings": findings, "conjectures": conjectures, "attempts": attempts}


if __name__ == "__main__":
    result = build()
    (PACKAGE / "inventory.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"]))
