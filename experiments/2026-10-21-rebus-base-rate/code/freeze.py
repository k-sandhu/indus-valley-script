"""Write FREEZE.json: hashes of the protocol, code and inputs, recorded before the real measurements.

    python experiments/2026-10-21-rebus-base-rate/code/freeze.py
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments" / "2026-10-21-rebus-base-rate"
DER = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p):
    return str(p.relative_to(ROOT)).replace("\\", "/")


def main():
    target = PKG / "FREEZE.json"
    if target.exists():
        print("refusing to overwrite", target)
        return 1
    required = [PKG / "PROTOCOL.md", PKG / "pools-v1.json", PKG / "SOURCES.json", PKG / "selftest-v1" / "selftest.json",
                PKG / "bench-selftest-v1.json"]
    missing = [rel(p) for p in required if not p.exists()]
    if missing:
        print("missing", missing)
        return 1
    selftest = json.loads((PKG / "selftest-v1" / "selftest.json").read_text(encoding="utf-8"))
    if not selftest.get("pass"):
        print("selftest did not pass")
        return 1
    out = {
        "schema": "rebus-base-rate freeze v1",
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
        "statement": "Recorded before run_homophones.py and run_interlocks.py were run on real data.",
        "protocol": {"path": rel(PKG / "PROTOCOL.md"), "sha256": sha(PKG / "PROTOCOL.md")},
        "code": {rel(p): sha(p) for p in sorted((PKG / "code").glob("*.py"))},
        "package_inputs": {rel(p): sha(p) for p in required[1:]},
        "local_inputs": {rel(p): sha(p) for p in sorted(DER.glob("*"))},
        "selftest_pass": selftest["pass"],
    }
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"protocol_sha256": out["protocol"]["sha256"], "code_files": len(out["code"]),
                      "local_inputs": len(out["local_inputs"])}))


if __name__ == "__main__":
    sys.exit(main())
