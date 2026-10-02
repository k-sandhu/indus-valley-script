"""Hash the owned package after review, retaining local witness classifications."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json


def main():
    root = Path(__file__).resolve().parent
    project = Path.cwd().resolve()
    output = root / "freeze-manifest.json"
    if output.exists():
        raise FileExistsError(output)
    files = sorted(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    files.append(project / "src/six_hour/physical_acquisition.py")
    records = []
    for path in files:
        payload = path.read_bytes()
        if "sources" in path.parts:
            handling, rights = "local-only-source-witness", "rights-unverified"
        elif path.suffix.lower() == ".png":
            handling, rights = "local-only-own-render-under-current-ignore-rules", "own-work"
        else:
            handling, rights = "own-knowledge-package", "own-work"
        records.append({"path": path.relative_to(project).as_posix(), "bytes": len(payload),
                        "sha256": sha256(payload).hexdigest(), "handling": handling, "rights_status": rights})
    by_handling = Counter()
    for row in records:
        by_handling[row["handling"]] += row["bytes"]
    result = {"status": "owned-endpoints-frozen-after-review", "frozen_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "All owned prose, source code, simulations, proofs, figures and acquisition metadata. Compiled Python caches are temporary and omitted. Downloaded notices and PNG render previews remain local under current repository rules.",
              "files": records, "file_count": len(records), "total_bytes": sum(r["bytes"] for r in records),
              "bytes_by_handling": dict(by_handling),
              "endpoint_policy": "Preserve these bytes; subsequent numerical or editorial revisions use new dated/versioned outputs.",
              "main_policy_records": 360, "refinement_policy_records": 96, "pilot_policy_records": 72,
              "relative_ambiguity_witness_pairs": 28,
              "reviewed_main_and_refinement_states": 4794, "reviewed_main_and_refinement_actions": 4338}
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
