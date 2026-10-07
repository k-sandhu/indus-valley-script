"""Verify saved witnesses, owned links and aggregate checks for this dated audit."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[2]
RUN = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(RUN) or output.exists():
        raise ValueError("Use a new result path in this run")
    checks = []
    for path in RUN.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
            checks.append({"type": "json", "path": path.relative_to(ROOT).as_posix(), "passed": True})
        except Exception as error:
            checks.append({"type": "json", "path": str(path), "passed": False, "error": str(error)})
    for path in RUN.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "#")):
                continue
            resolved = path.parent / target.split("#", 1)[0]
            checks.append({"type": "local-link", "document": path.name,
                           "target": target, "passed": resolved.exists()})
    raw = ROOT / "data/raw/2026-10-02-dataset-landscape"
    for manifest_path in raw.glob("*/acquisition.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for asset in manifest["assets"]:
            path = ROOT / asset.get("path", "not-acquired")
            valid = asset.get("status") == 200 and path.is_file()
            if valid:
                data = path.read_bytes()
                valid = len(data) == asset["bytes"] and sha256(data).hexdigest() == asset["sha256"]
            checks.append({"type": "witness-hash", "url": asset["url"] if "url" in asset else asset["requested_url"],
                           "passed": valid})
    audit = json.loads((RUN / "main-v1/local-input-audit.json").read_text(encoding="utf-8"))
    checks.append({"type": "historical-aggregate-replay", "count": len(audit["checks"]),
                   "passed": audit["all_checks_passed"]})
    for source in audit["sources"]:
        for key in ("input", "historical_summary"):
            record = source[key]
            data = (ROOT / record["path"]).read_bytes()
            checks.append({"type": "local-input-pin", "path": record["path"],
                           "passed": len(data) == record["bytes"] and sha256(data).hexdigest() == record["sha256"]})
    landscape = json.loads((RUN / "landscape.json").read_text(encoding="utf-8"))
    identifiers = [r["id"] for r in landscape["sources"]]
    checks.append({"type": "source-identifiers", "count": len(identifiers),
                   "passed": len(identifiers) == len(set(identifiers))})
    registry = json.loads((ROOT / "knowledge/experiments/registry.json").read_text(encoding="utf-8"))
    entry = json.loads((RUN / "registry-entry.json").read_text(encoding="utf-8"))
    checks.append({"type": "registry-entry", "passed": entry in registry["experiments"]})
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "checks": checks,
              "all_checks_passed": all(c["passed"] for c in checks),
              "scope": "File integrity, saved access responses, links and existing aggregate replay; not expert archaeological validation."}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"checks": len(checks), "all_checks_passed": result["all_checks_passed"],
                      "failures": [c for c in checks if not c["passed"]]}, indent=2))
    if not result["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
