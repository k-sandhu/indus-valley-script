"""Independent count replay and focused checks for this package only."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unicodedata
import unittest

ROOT = Path(__file__).resolve().parents[3]
PKG = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("output exists; select a new path")
    summary = read(PKG / "run-v1/input-audit.json")
    details = read(ROOT / summary["local_detail"]["path"])
    sources = read(PKG / "run-v1/source-manifest.json")
    integrity = []
    for item in sources["inputs_and_code"] + sources["sangam_files"] + [summary["local_detail"]]:
        integrity.append({"path": item["path"], "matches": sha(ROOT / item["path"]) == item["sha256"]})
    tokens = []
    for item in sources["sangam_files"]:
        text = re.sub(r"<[^>]+>", " ", (ROOT / item["path"]).read_text(encoding="utf-8", errors="replace"))
        tokens.extend(unicodedata.normalize("NFC", token) for token in re.findall(r"[஀-௿]+", text))
    exact_matches = 0
    prefix_matches = 0
    for item in details["words"]:
        old = item["historical"]
        if old["entry"]:
            head = unicodedata.normalize("NFC", old["entry"]["head"].strip())
            exact_matches += tokens.count(head) == item["same_historical_form_exact_count"]
            prefix_matches += sum(token.startswith(old["prefix"]) for token in tokens) == old["count"]
    stream = io.StringIO()
    tests = unittest.defaultTestLoader.discover(str(PKG / "code"), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(tests)
    bench = {name: read(PKG / f"{name}-synthetic-v1.json")["pass"]
             for name in ("key", "meaning", "shots")}
    checks = {"source_hashes": all(item["matches"] for item in integrity),
              "token_denominator": len(tokens) == summary["historical_token_count"],
              "independent_exact_counts": exact_matches == len(details["words"]),
              "independent_prefix_counts": prefix_matches == len(details["words"]),
              "focused_tests": result.wasSuccessful(),
              "bench_smoke_tests": all(bench.values())}
    payload = {"schema_version": "1.0", "task": "reading-eval-readiness/verification",
               "verification_tier": "submitted", "pass": all(checks.values()), "checks": checks,
               "tests_run": result.testsRun, "test_output": stream.getvalue(),
               "independent_word_counts_checked": exact_matches,
               "independent_token_denominator": len(tokens), "source_hashes": integrity,
               "bench_pass": bench, "new_real_confirmation_access": False,
               "scope": "Author verification of source integrity, diagnostic counts and generated fixtures; no independent linguistic adjudication",
               "code_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in sorted((PKG / "code").glob("*.py"))}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output:
        json.dump(payload, output, indent=2)
        output.write("\n")
    print(json.dumps({"pass": payload["pass"], "checks": checks, "tests_run": result.testsRun}))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
