"""Check source hashes, bounded populations and record locators for this module."""
from pathlib import Path
import collections
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    checks = []

    def check(label, passed):
        checks.append({"check": label, "pass": bool(passed)})

    sources = load(HERE / "sources.json")["source_records"]
    ids = {s["source_id"] for s in sources}
    check("source ids unique", len(ids) == len(sources))
    for source in sources:
        p = ROOT / source["logical_path"]
        check("source SHA-256 " + source["source_id"], sha(p) == source["sha256"])
        check("resolved source path " + source["source_id"], p.resolve() == Path(source["physical_path"]))
    observations = load(HERE / "observations.json")["observations"]
    check("43 unique assertion ids", len(observations) == len({o["id"] for o in observations}) == 43)
    required = {"id", "town", "phase", "feature", "assertion", "source_id", "locator", "evidence_status", "dating_basis", "uncertainty", "missing_reason"}
    for observation in observations:
        check(observation["id"] + " fields and source", required <= observation.keys() and observation["source_id"] in ids and bool(observation["locator"]) and bool(observation["uncertainty"]))
    for result in load(HERE / "prior-results.json")["results"]:
        p = ROOT / result["exact_output"]
        data = load(p)
        check("prior result hash " + result["id"], sha(p) == result["sha256"])
        for pointer, expected in result["values"].items():
            value = data
            for part in pointer.strip("/").split("/"):
                value = value[int(part)] if isinstance(value, list) else value[part]
            check("prior exact value " + result["id"] + " " + pointer, value == expected)
    summary = load(HERE / "context-table-summary.json")
    detail = Path(summary["detailed_physical_path"])
    table = load(detail)["rows"]
    check("table source and detailed payload pinned", sha(detail) == summary["detailed_sha256"] and summary["source_sha256"] == sources[0]["sha256"])
    check("complete table serials 1..225", [r["table_serial"] for r in table] == list(range(1, 226)))
    check("raw stage counts reproduce", dict(collections.Counter(r["stage_as_printed"] or "[blank]" for r in table)) == summary["stage_raw_counts"])
    check("139 explicit yes rows", sum(r["inscription_as_printed"] in ("Yes", "Yes,") for r in table) == 139)
    check("earliest assigned row is uninscribed", table[36]["accession"] == "13204" and table[36]["stage_as_printed"] == "III A" and table[36]["inscription_as_printed"] == "Nil")
    check("qualified last stage preserved across page boundary", table[-1]["stage_as_printed"] == "VI- ? Mispla ced")
    for asset in load(HERE / "local-assets.json")["assets"]:
        p = Path(asset["physical_path"])
        check("local asset hash " + p.name, sha(p) == asset["sha256"] and p.drive.lower() == "d:" and p.stat().st_size == asset["bytes"])
    check("bench spending ledger unchanged", sha(ROOT / "bench/spent.json") == load(HERE / "prior-results.json")["bench_spent_sha256"])
    result = {"status": "pass" if all(c["pass"] for c in checks) else "fail", "verification_tier": "submitted-author-check", "checks": len(checks), "failures": [c for c in checks if not c["pass"]], "source_records": len(sources), "assertions": len(observations), "table_rows": len(table), "new_objects": 0, "confirmation_access": False, "limitation": "Hash, pointer, population and bookkeeping checks; no independent archaeological review."}
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
