"""Align and compare all available pairs of blind readings.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/compare_passes.py [--block <id>] [--allow-partial]
Local compare/<block>.todo.json contains values. accuracy/<block>.compare.json
and compare-summary.json contain counts, identifiers and input hashes only.
"""
from __future__ import annotations

from cisi_common import (SHORT, arguments, block_list, likely_strips, main_guard,
                         provenance, read_pass, uncertain, verify_inputs, ws, write_json)


def compare_block(spec, raw):
    block = spec["block"]
    paths = {p: raw / p / f"{block}.{p}.txt" for p in ("pass1", "pass2")}
    missing = [p for p, path in paths.items() if not path.exists()]
    if missing:
        return None, {"block": block, "volume": spec["volume"], "status": "missing-pass", "missing": missing}
    inputs = provenance(paths)
    corrigenda = spec.get("kind") == "corrigenda"
    p1, p2 = (read_pass(paths[p], corrigenda) for p in ("pass1", "pass2"))
    order = p1["order"] + [k for k in p2["order"] if k not in p1["rows"]]
    todo, by_col = [], {}
    for col in (["row"] if corrigenda else SHORT):
        i = 0 if corrigenda else SHORT.index(col)
        by_col[col] = {"cells": len(order), "paired_cells": 0, "agreements": 0, "disagreements": 0,
                       "bracketed_pass1": 0, "bracketed_pass2": 0}
        for key in order:
            a, b = p1["rows"].get(key), p2["rows"].get(key)
            if a is not None:
                by_col[col]["bracketed_pass1"] += uncertain(a[i])
            if b is not None:
                by_col[col]["bracketed_pass2"] += uncertain(b[i])
            by_col[col]["paired_cells"] += a is not None and b is not None
            agrees = a is not None and b is not None and ws(a[i]) == ws(b[i])
            by_col[col]["agreements"] += agrees
            by_col[col]["disagreements"] += not agrees
    for key in order:
        a, b = p1["rows"].get(key), p2["rows"].get(key)
        row_issue = a is None or b is None or key in p1["variants"] or key in p2["variants"] or corrigenda
        if row_issue:
            if a is not None and b is not None and [ws(x) for x in a] == [ws(x) for x in b] and not (key in p1["variants"] or key in p2["variants"]):
                continue
            todo.append({"cisi": key, "column": "row", "pass1": " | ".join(a) if a is not None else "absent",
                         "pass2": " | ".join(b) if b is not None else "absent",
                         "duplicate_variants": {p: [" | ".join(cs) for cs in reading["variants"].get(key, [])]
                                                for p, reading in (("pass1", p1), ("pass2", p2))},
                         "strips": likely_strips(spec, key, (p1, p2)), "location_is_estimate": True})
        else:
            for i, col in enumerate(SHORT):
                if ws(a[i]) != ws(b[i]):
                    todo.append({"cisi": key, "column": col, "pass1": a[i], "pass2": b[i],
                                 "strips": likely_strips(spec, key, (p1, p2)), "location_is_estimate": True})
    summary = {
        "block": block, "volume": spec["volume"], "kind": "corrigenda" if corrigenda else "entries", "status": "compared",
        "inputs": inputs, "rows_union": len(order), "rows_in_both_passes": len(set(p1["rows"]) & set(p2["rows"])),
        "rows_only_pass1": len(set(p1["rows"]) - set(p2["rows"])), "rows_only_pass2": len(set(p2["rows"]) - set(p1["rows"])),
        "by_column": by_col, "todo_records": len(todo),
        "duplicates": {p: {"identical_overlap_rows": reading["duplicates_exact"],
                           "conflicting_identifiers": len(reading["variants"]),
                           "conflicting_extra_rows": sum(len(v) for v in reading["variants"].values()),
                           "piece_lines_combined": reading["piece_lines_combined"]}
                       for p, reading in (("pass1", p1), ("pass2", p2))},
        "reading_times": {"pass1": p1["reading_time"], "pass2": p2["reading_time"]},
        "denominator": "Union of aligned identifiers; omissions are separate row errors. Corrigenda use line positions and separate text-line counts.",
    }
    verify_inputs(inputs)
    return {"todo": todo, "pass1": p1, "pass2": p2, "order": order}, summary


def main():
    args = arguments(__doc__.splitlines()[0]).parse_args()
    specs = block_list(args)
    summaries = []
    for spec in specs:
        result, summary = compare_block(spec, args.raw)
        summaries.append(summary)
        if result is not None:
            write_json(args.raw / "compare" / f"{spec['block']}.todo.json", result["todo"], local=True)
            write_json(args.out / "accuracy" / f"{spec['block']}.compare.json", summary)
    missing = [s["block"] for s in summaries if s["status"] != "compared"]
    write_json(args.out / "compare-summary.json", {"selected_blocks": len(specs), "compared_blocks": len(specs) - len(missing),
                                                   "missing_blocks": missing,
                                                   "todo_records": sum(s.get("todo_records", 0) for s in summaries)})
    print(f"Compared {len(specs) - len(missing)} blocks; {sum(s.get('todo_records', 0) for s in summaries)} decisions requested.")
    if missing and not args.allow_partial:
        raise ValueError("missing pass pairs: " + ", ".join(missing) + "; use --allow-partial for an explicit interim comparison")


if __name__ == "__main__":
    main_guard(main)
