"""Rerun site transfer after retaining all physical aliases of unique strings.

Separate outputs preserve completed earlier assays rather than silently changing
their saved results. Deterministic representative metadata remains a sensitivity.
"""
import argparse
import json
from pathlib import Path
import time

from conditional_structure import digest, group_records, load_records
from nested_conditional import leave_site_out


def main(args):
    start = time.monotonic()
    collapse = json.loads(Path(args.collapse).read_text(encoding="utf-8"))["mapping"] if args.collapse else None
    rows, exclusions = load_records(args.input, args.min_length, not args.all_records, False, collapse)
    groups = group_records(rows)
    for group, indices in enumerate(groups):
        for index in indices:
            rows[index]["analysis_group"] = group
    result = {
        "design": "Site transfer excluding every transitive physical-artifact/identical-string component touching the held-out site",
        "parameters": vars(args),
        "input_sha256": digest(args.input),
        "runner_sha256": digest(__file__),
        "model_source_sha256": digest(Path(__file__).with_name("nested_conditional.py")),
        "loader_source_sha256": digest(Path(__file__).with_name("conditional_structure.py")),
        "records": len(rows), "groups": len(groups),
        "group_sizes": sorted([len(g) for g in groups], reverse=True),
        "exclusions": exclusions,
        "leave_site_out": leave_site_out(rows, seed=args.seed),
        "elapsed_seconds": time.monotonic() - start,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"stage": "complete_alias_safe_transfer", "output": str(output), "records": len(rows), "groups": len(groups), "site_gains": [{"site": r["heldout_site"], "gain": r["gain_bits_per_noninitial_sign"], "n": r["test_records"]} for r in result["leave_site_out"]]}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-length", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261001)
    parser.add_argument("--collapse")
    parser.add_argument("--all-records", action="store_true")
    main(parser.parse_args())
