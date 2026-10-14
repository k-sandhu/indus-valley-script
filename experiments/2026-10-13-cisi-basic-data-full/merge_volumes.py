"""Merge final blocks by volume, adding the frozen CISI 2 pilot once.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/merge_volumes.py [--allow-partial] [--pilot <local.jsonl>]
Writes local cisi1-basic-data.jsonl, cisi2-basic-data.jsonl and merge-gaps.json;
tracked merge-summary.json holds counts by site prefix and input hashes.
"""
from __future__ import annotations

import collections
import re

from cisi_common import (PILOT, arguments, block_list, load_json, load_jsonl, main_guard,
                         provenance, sort_key, verify_inputs, write_json, write_jsonl)


def merge_rows(blocks, volume, pilot=None):
    rows, seen = [], set()
    for name, records in list(blocks) + ([("pilot", pilot)] if pilot is not None else []):
        for r in records:
            key = r["cisi"]
            if key in seen:
                raise ValueError("duplicate CISI number in " + volume + ": " + key)
            seen.add(key)
            rows.append(dict(r, volume=volume, block=r.get("block", name)))
    rows.sort(key=lambda r: sort_key(r["cisi"]))
    numbers = collections.defaultdict(set)
    for r in rows:
        m = re.fullmatch(r"([A-Za-z?]+)-(\d+)[A-Za-z]?", r["cisi"])
        if not m:
            raise ValueError("invalid merged identifier")
        numbers[m[1]].add(int(m[2]))
    gaps = {prefix: [f"{prefix}-{n}" for n in range(min(have), max(have) + 1) if n not in have]
            for prefix, have in sorted(numbers.items())}
    counts = {prefix: {"lowest": min(have), "highest": max(have), "distinct_integer_numbers": len(have),
                       "rows": sum(r["cisi"].startswith(prefix + "-") for r in rows), "missing_numbers": len(gaps[prefix])}
              for prefix, have in sorted(numbers.items())}
    return rows, gaps, counts


def main():
    ap = arguments(__doc__.splitlines()[0])
    ap.add_argument("--pilot", type=type(PILOT), default=PILOT)
    args = ap.parse_args()
    specs = [b for b in block_list(args) if b.get("kind") != "corrigenda"]
    groups, missing, paths = {v: [] for v in ("cisi1", "cisi2")}, [], {}
    for spec in specs:
        path = args.raw / "final" / f"{spec['block']}.final.jsonl"
        if not path.exists():
            missing.append(spec["block"])
            continue
        accuracy = args.out / "accuracy" / f"{spec['block']}.accuracy.json"
        if not accuracy.exists():
            raise ValueError("missing accuracy record for final: " + spec["block"])
        a = load_json(accuracy)
        verify_inputs(a["inputs"])
        if a.get("final_outputs"):
            verify_inputs(a["final_outputs"])
        rows = load_jsonl(path)
        if len(rows) != a["final_rows"]:
            raise ValueError("final row count differs from accuracy record: " + spec["block"])
        groups[spec["volume"]].append((spec["block"], rows))
        paths[spec["block"]] = path
        paths[spec["block"] + "-accuracy"] = accuracy
    if missing and not args.allow_partial:
        raise ValueError("missing final blocks: " + ", ".join(missing))
    pilot = load_jsonl(args.pilot)
    paths["pilot"] = args.pilot
    inputs = provenance(paths)
    all_rows, all_gaps, summary = {}, {}, {}
    for v in groups:
        rows, gaps, counts = merge_rows(groups[v], v, pilot if v == "cisi2" else None)
        all_rows[v], all_gaps[v] = rows, gaps
        summary[v] = {"rows": len(rows), "new_blocks": len(groups[v]), "pilot_rows": len(pilot) if v == "cisi2" else 0,
                      "by_site_prefix": counts, "missing_numbers": sum(len(g) for g in gaps.values())}
    verify_inputs(inputs)
    for v, rows in all_rows.items():
        write_jsonl(args.raw / f"{v}-basic-data.jsonl", rows)
    write_json(args.raw / "merge-gaps.json", all_gaps, local=True)
    write_json(args.out / "merge-summary.json", {"complete_for_selected_blocks": not missing,
                                                "selection_is_partial": bool(args.block) or bool(missing),
                                                "missing_blocks": missing, "volumes": summary, "inputs": inputs,
                                                "gap_rule": "Integer numbers between the lowest and highest present per site prefix, separately per volume. A letter suffix occupies its integer number."})
    print("Merged " + ", ".join(f"{v}: {len(rs)} rows" for v, rs in all_rows.items()))


if __name__ == "__main__":
    main_guard(main)
