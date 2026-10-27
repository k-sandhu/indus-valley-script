"""Compare all record-level output hashes from two completed builds."""
import argparse
import json
from pathlib import Path

from build_register import sha


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--first", required=True)
    p.add_argument("--second", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    first, second, out = Path(a.first), Path(a.second), Path(a.output)
    if out.exists(): raise ValueError("Existing output refused")
    names = sorted({x.name for d in [first, second] for x in d.iterdir() if x.is_file()})
    checks = [{"file": name, "first_sha256": sha(first / name) if (first / name).exists() else None, "second_sha256": sha(second / name) if (second / name).exists() else None} for name in names]
    for c in checks: c["equal"] = c["first_sha256"] is not None and c["first_sha256"] == c["second_sha256"]
    result = {"status": "passed" if all(c["equal"] for c in checks) else "failed", "files": len(checks), "checks": checks}
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "files": len(checks)}))
    if result["status"] != "passed": raise SystemExit(1)


if __name__ == "__main__": main()
