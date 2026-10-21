"""Record parent-owned files and check their local links without opening reserves."""
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGISTRY = ROOT / "knowledge/registry/attempts/RESERVED-TEST-PROGRAM-2026-10-20.json"
OUT = HERE / "final-scope-check-v1.json"
CHANGED = HERE / "changed-paths.json"
if OUT.exists() or CHANGED.exists():
    raise SystemExit("Preserve previous records; use a new version")

link_errors = []
for path in HERE.glob("*.md"):
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = unquote(target.split("#", 1)[0].strip("<>"))
        if target and "://" not in target and not (path.parent / target).exists():
            link_errors.append({"file": path.name, "target": target})
entry = json.loads(REGISTRY.read_text(encoding="utf-8"))
evidence_errors = [p for p in entry["evidence"] if not (ROOT / p).exists()]
whole = json.loads((HERE / "repository-check-v2.json").read_text(encoding="utf-8"))
owned_names = [
    "2026-10-20-reserved-test-program", "2026-10-20-fresh-test-collection",
    "2026-10-20-khirsara-reserve", "2026-10-20-farmana-reserve-review",
    "2026-10-20-foreign-script-audit", "2026-10-20-foreign-script-blind-review",
    "2026-10-20-foreign-script-verification",
]
scoped_errors = [e for e in whole["errors"] if any(n in e for n in owned_names)]
result = {
    "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    "parent_link_errors": link_errors,
    "registry_evidence_errors": evidence_errors,
    "whole_repository_status": whole["status"],
    "whole_repository_error_count": len(whole["errors"]),
    "task_package_errors_in_repository_snapshot": scoped_errors,
    "parent_and_task_scope_pass": not (link_errors or evidence_errors or scoped_errors),
    "reserved_payload_files_opened": 0,
    "scope": "Safe parent Markdown links, registry evidence existence, and filtering of the saved whole-repository check. No raw source or reserved object content read.",
}
OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
paths = sorted(p for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
paths.append(REGISTRY)
record = {
    "scope": "Parent-owned files only; each delegated package carries its own changed-paths record.",
    "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
    "this_manifest": CHANGED.relative_to(ROOT).as_posix(),
}
CHANGED.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
