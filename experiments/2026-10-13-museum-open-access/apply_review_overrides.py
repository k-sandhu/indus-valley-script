"""Apply the dated review ledger to saved harvest flags without fetching records.

An override accepts its recorded old value or its new value, so replay is
idempotent. Any unexpected value or ambiguous accession stops the run before
any file is written. Source witnesses and the pre-review snapshot stay intact.
"""
import json
from pathlib import Path

PKG = Path(__file__).resolve().parent
HARVEST = PKG / "harvest"


def main():
    ledger = json.loads((HARVEST / "review-overrides.json").read_text(encoding="utf-8"))
    documents = {p: json.loads(p.read_text(encoding="utf-8"))
                 for p in sorted(HARVEST.glob("*-records.json"))}
    index = {}
    for path, document in documents.items():
        rows = document["records"] if isinstance(document, dict) else document
        for row in rows:
            index.setdefault((row["museum"], row["accession"]), []).append((path, row))
    changed = set()
    for override in ledger:
        key = (override["museum"], override["accession"])
        matches = index.get(key, [])
        if len(matches) != 1:
            raise ValueError(f"Expected one record for {key}, found {len(matches)}")
        path, row = matches[0]
        field = override["field"]
        current = row.get(field)
        if current not in (override["old_value"], override["new_value"]):
            raise ValueError(f"Unexpected {field} for {key}: {current!r}")
        if current != override["new_value"]:
            row[field] = override["new_value"]
            changed.add(path)
    for path in sorted(changed):
        path.write_text(json.dumps(documents[path], indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"overrides": len(ledger), "files_changed": [p.name for p in sorted(changed)]}))


if __name__ == "__main__":
    main()
