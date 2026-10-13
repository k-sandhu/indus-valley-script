"""Verify ledger reconstruction, overwrite guards and owned documentary references."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PACKAGE = Path("experiments/2026-10-11-societal-persistence/evidence")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    checks = []

    def record(name, passed, detail):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})

    fresh = args.output_dir / "rebuilt"
    rebuilt = subprocess.run([sys.executable, "-X", "utf8", str(PACKAGE / "build_ledger.py"), str(fresh)], capture_output=True, text=True)
    record("builder-completes", rebuilt.returncode == 0, rebuilt.stdout.strip())
    names = ["sources.json", "observations.json", "acquisition-index.json"]
    for name in names:
        record(f"byte-identical-{name}", (PACKAGE / name).read_bytes() == (fresh / name).read_bytes(), "Deterministic reconstruction from preserved local witnesses")
    before = {name: digest(PACKAGE / name) for name in names}
    blocked = subprocess.run([sys.executable, "-X", "utf8", str(PACKAGE / "build_ledger.py"), str(PACKAGE)], capture_output=True, text=True)
    record("builder-overwrite-guard", blocked.returncode != 0 and "Refusing to overwrite" in blocked.stderr, "Existing documentary endpoint rejected")
    record("builder-guard-preserves-ledgers", before == {name: digest(PACKAGE / name) for name in names}, "Frozen bytes unchanged after rejection")
    run_files = sorted((PACKAGE / "run-v2").glob("*.json"))
    before_run = {p.name: digest(p) for p in run_files}
    blocked_run = subprocess.run([sys.executable, "-X", "utf8", str(PACKAGE / "audit.py"), str(PACKAGE / "run-v2")], capture_output=True, text=True)
    record("auditor-overwrite-guard", blocked_run.returncode != 0 and "FileExistsError" in blocked_run.stderr, "Existing frozen run directory rejected")
    record("auditor-guard-preserves-run", before_run == {p.name: digest(p) for p in run_files}, "Frozen audit bytes unchanged after rejection")
    old_hashes = json.loads((PACKAGE / "run-v1/input-hashes.json").read_text(encoding="utf-8"))
    record("original-audit-code-preserved", digest(PACKAGE / "audit-v1.py") == old_hashes[(PACKAGE / "audit.py").as_posix()], "Saved v1 code exactly matches the input hash recorded in failed initial run")
    observations = json.loads((PACKAGE / "observations.json").read_text(encoding="utf-8"))["observations"]
    known = {o["observation_id"] for o in observations}
    links = []
    for p in sorted(PACKAGE.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        unknown = set(re.findall(r"\bE\d{2}\b", text)) - known
        record(f"observation-refs-{p.name}", not unknown, sorted(unknown))
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            candidate = (p.parent / target.split("#", 1)[0]).resolve()
            links.append({"file": p.as_posix(), "target": target, "exists": candidate.exists()})
    record("owned-markdown-local-links", all(r["exists"] for r in links), {"checked": len(links), "missing": [r for r in links if not r["exists"]]})
    schecks = json.loads((PACKAGE / "source-checks.json").read_text(encoding="utf-8"))["final_audit"]
    summary = json.loads((PACKAGE / "run-v2/summary.json").read_text(encoding="utf-8"))
    record("manual-summary-agrees", all(schecks[k] == summary[k] for k in ["checks", "passed", "failed", "included_primary_works", "observations", "acquisition_attempts"]), "Manual source controls join the final audit")
    result = {"scope": "package reconstruction and integrity; no archaeological model fit",
              "checks": len(checks), "passed": sum(c["passed"] for c in checks),
              "failed": [c["check"] for c in checks if not c["passed"]], "local_links": len(links), "details": checks}
    (args.output_dir / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (args.output_dir / "local-links.json").write_text(json.dumps(links, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ["checks", "passed", "failed", "local_links"]}))
    if result["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
