"""Wrapper around tools/measure_lines.py that measures picks one line at a time.

measure_lines.measure() stops at the first line whose fit fails.  For
exploration this wrapper calls it once per line, records each failure with its
message, and writes the successful rows in the same output format.  The tool
code is imported unchanged.

Usage: python -I measure_each.py <picks.json> <render.png.json> <out.json>
"""
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
sys.dont_write_bytecode = True
import measure_lines  # noqa: E402
from common import read_json, write_json  # noqa: E402


def main():
    picks = read_json(sys.argv[1])
    sidecar = sys.argv[2]
    out = sys.argv[3]
    rows, failures, base = [], [], None
    for line in picks["lines"]:
        one = dict(picks)
        one["lines"] = [line]
        try:
            res = measure_lines.measure(one, sidecar)
            rows.extend(res["lines"])
            base = res
        except ValueError as e:
            failures.append(dict(id=line["id"], error=str(e)))
    if base is None:
        base = dict(schema_version=1, source_id=picks["source_id"], lines=[])
    base = dict(base)
    base["lines"] = rows
    base["failures"] = failures
    base["wrapper"] = "measure-B/scripts-G/measure_each.py (per-line calls of tools/measure_lines.measure)"
    write_json(out, base)
    for f in failures:
        print("FAILED", f["id"], f["error"])


if __name__ == "__main__":
    main()
