"""Exploratory literal-prefix check; emit aggregates without third-party rows."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
PREFIXES = ["H97-3433", "7617-01", "H2001-5082", "2920-02"]

def main():
    results = []
    for name in ["lipi_observed_faces.jsonl", "mayig_faces.jsonl"]:
        path = ROOT / "data/normalized" / name
        data = path.read_bytes()
        lines = data.decode("utf-8").splitlines()
        results.append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "record_lines": len(lines),
            "literal_identifier_record_counts": {
                value: sum(value.lower() in line.lower() for line in lines)
                for value in PREFIXES
            },
        })
    output = {
        "status": "exploratory post-search literal check",
        "method": "Case-insensitive substring in each face-record line; not normalized object matching",
        "limitation": "Prefixes can identify representations; full suffixes, aliases and unique-object joins remain unchecked",
        "inputs": results,
    }
    destination = Path(__file__).with_name("identifier-check.json")
    if destination.exists():
        previous = json.loads(destination.read_text(encoding="utf-8"))
        if previous != output:
            raise ValueError("Preserve the prior output and use a new dated result")
    else:
        destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output))

if __name__ == "__main__":
    main()
