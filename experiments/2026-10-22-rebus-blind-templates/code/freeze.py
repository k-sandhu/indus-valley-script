"""Record the SHA-256 of the protocol, predictions, identifications, template list, code and inputs.

Run after build_templates.py and before run_templates.py; refuses to overwrite FREEZE.json.

    python experiments/2026-10-22-rebus-blind-templates/code/freeze.py
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = HERE.parents[2]
BASE = ROOT / "experiments" / "2026-10-21-rebus-base-rate" / "code"
DER = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "derived-v1"
SANGAM = ROOT / "data" / "raw" / "2026-10-21-rebus-base-rate" / "sources-v1" / "sangam"


def h(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def main():
    out = PKG / "FREEZE.json"
    if out.exists():
        print("refusing to overwrite", out)
        return 1
    files = [PKG / "PROTOCOL.md", PKG / "PREDICTIONS.json", PKG / "identifications-v1.json", PKG / "templates-v1.json",
             PKG / "discovery-v1" / "pairs.json", PKG / "confirmation-v1" / "pairs.json", PKG / "round.json"]
    files += sorted(HERE.glob("*.py"))
    files += [BASE / "rebus.py", BASE / "run_interlocks.py", BASE / "parse_tamil_lex.py"]
    inputs = [DER / "tamil-lex-entries.jsonl", DER / "dedr-entries.jsonl"] + sorted(SANGAM.glob("pmuni*.html"))
    res = {"schema_version": "1.0", "task": "rebus-blind-templates/freeze",
           "created_utc": datetime.now(timezone.utc).isoformat(),
           "note": "Written after the confirmation pair read and the template build, before any Tamil compound was looked up for a template.",
           "files": {rel(p): h(p) for p in files},
           "inputs": {rel(p): h(p) for p in inputs}}
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("PROTOCOL", res["files"][rel(PKG / "PROTOCOL.md")])
    print("TEMPLATES", res["files"][rel(PKG / "templates-v1.json")])
    return 0


if __name__ == "__main__":
    sys.exit(main())
