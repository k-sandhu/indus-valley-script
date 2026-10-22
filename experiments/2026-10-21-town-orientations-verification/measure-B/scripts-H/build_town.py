"""Assemble a town input file for tools/systems.py from a spec and measure_lines results.

The spec gives the slug, located point, sources, notes and, for each lines
result, its file, a source locator and an optional mapping from line id to the
system label used at the grouping stage (picks carry provisional labels).
Every refinement field of every line is retained; source_id, source_locator,
lines_file and picks_file are added.
Usage: build_town.py <spec.json> <town-input.json>
"""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path


def main():
    spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    if out.exists():
        raise FileExistsError(out)
    lines = []
    for block in spec.get("line_results", []):
        res = json.loads(Path(block["lines_file"]).read_text(encoding="utf-8"))
        relabel = block.get("system_map", {})
        drop = set(block.get("exclude", []))
        for line in res["lines"]:
            if line["id"] in drop:
                continue
            row = dict(line)
            row["source_id"] = res["source_id"]
            row["source_locator"] = block["source_locator"]
            row["lines_file"] = block["lines_file"]
            row["picks_file"] = block["picks_file"]
            if line["id"] in relabel:
                row["system_in_picks"] = line["system"]
                row["system"] = relabel[line["id"]]
            lines.append(row)
    town = {
        "schema_version": 1,
        "slug": spec["slug"],
        "measurer": "B",
        "located_point": spec["located_point"],
        "sources": spec["sources"],
        "lines": lines,
        "registrations": spec.get("registrations", []),
        "notes": spec.get("notes", ""),
        "unmeasurable_reason": spec.get("unmeasurable_reason"),
    }
    for k in ("imagery_status", "plan_search", "stated_orientation_encounters"):
        if k in spec:
            town[k] = spec[k]
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(town, indent=2, ensure_ascii=False) + "\n")
    print(out, len(lines), "lines")


if __name__ == "__main__":
    main()
