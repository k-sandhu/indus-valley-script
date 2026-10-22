"""Write FREEZE.json: hashes of the protocol, code and inputs, recorded before the real run.

    python experiments/2026-10-22-rebus-winslow/code/freeze.py

The reused code of REBUS-BASE-RATE-2026-10-21 must carry the hashes under which
that study's results-v2 were computed (rebus.py as repaired in its Amendment 1,
run_interlocks.py and parse_tamil_lex.py as frozen).
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments" / "2026-10-22-rebus-winslow"
BASE = ROOT / "experiments" / "2026-10-21-rebus-base-rate"
RAW = ROOT / "data" / "raw" / "2026-10-22-rebus-winslow"
BASE_RAW = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate"
REUSED = {
    "rebus.py": "bfa65175b3383b8cad04d05f0078cfa7abcfbc673b0728f92a138f47c787ed42",
    "run_interlocks.py": "284fa53f152b5997465d21d94f51cd7de452f949d3c088ec3158dccc7c213d46",
    "parse_tamil_lex.py": "e2fb108f1bd3b82f6fe3dd2404a7ee3f780a0c3728afedd3059287ac1b9a6e27",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return str(Path(p).relative_to(ROOT)).replace("\\", "/")


def main():
    target = PKG / "FREEZE.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    required = [PKG / "PROTOCOL.md", PKG / "SOURCES.json", PKG / "parser-validation-v1.json",
                PKG / "selftest-v1" / "selftest.json", PKG / "selftest-base-v1" / "selftest.json",
                PKG / "bench-selftest-v1.json"]
    missing = [rel(p) for p in required if not p.exists()]
    if missing:
        print("missing", missing)
        return 1
    for p in (PKG / "selftest-v1" / "selftest.json", PKG / "selftest-base-v1" / "selftest.json"):
        if not json.loads(p.read_text(encoding="utf-8")).get("pass"):
            print("selftest did not pass:", rel(p))
            return 1
    bad = [n for n, d in REUSED.items() if sha(BASE / "code" / n) != d]
    if bad:
        print("reused code differs from the 2026-10-21 results-v2 hashes:", bad)
        return 1
    inputs = [RAW / "derived-v1" / "winslow-entries.jsonl", BASE_RAW / "derived-v1" / "dedr-entries.jsonl",
              BASE / "pools-v1.json"] + sorted((BASE_RAW / "sources-v1" / "sangam").glob("pmuni*.html"))
    out = {
        "schema": "rebus-winslow freeze v1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "statement": "Recorded before run_winslow.py was run on the Winslow compound table.",
        "protocol": {"path": rel(PKG / "PROTOCOL.md"), "sha256": sha(PKG / "PROTOCOL.md")},
        "code": {rel(p): sha(p) for p in sorted((PKG / "code").glob("*.py"))},
        "reused_code": {rel(BASE / "code" / n): sha(BASE / "code" / n) for n in REUSED},
        "package_inputs": {rel(p): sha(p) for p in required[1:]},
        "inputs": {rel(p): sha(p) for p in inputs},
    }
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"protocol_sha256": out["protocol"]["sha256"], "code_files": len(out["code"]),
                      "inputs": len(out["inputs"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
