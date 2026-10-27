"""Capture manual repository/prose checks in an owned, versioned endpoint."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--integrity", action="store_true")
    args = parser.parse_args()
    out = HERE / args.out
    if out.exists():
        raise SystemExit(f"Refusing to overwrite {out}")
    commands = [
        [sys.executable, "tools/review_prose.py", "--path", HERE.relative_to(ROOT).as_posix(), "--no-write"],
        [sys.executable, "tools/kb.py", "check"],
    ]
    if args.integrity:
        commands.append([sys.executable, "tools/verify_knowledge_repo.py", "--output", (HERE / "repository-integrity-v1.json").relative_to(ROOT).as_posix()])
    results = []
    for command in commands:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        results.append(dict(command=command, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        print(json.dumps(dict(command=command[1], returncode=proc.returncode)))
    result = dict(schema_version="1.0", created_at=datetime.now(timezone.utc).isoformat(), results=results,
                  interpretation="Prose flags require review. Repository-wide failures must be attributed by path; no unrelated files are repaired by this contribution.")
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
