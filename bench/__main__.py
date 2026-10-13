"""Run manual benchmark tasks from the repository root."""
import argparse
import json
from pathlib import Path
import sys

from .common import strict_json, write_json


def parser():
    ap = argparse.ArgumentParser(prog="python -m bench")
    sub = ap.add_subparsers(dest="task", required=True)
    from . import key_calibration, meaning_map, shots, restoration, segmentation, selftest
    for name, module in (("key-calibration", key_calibration), ("meaning-map", meaning_map),
                         ("shots", shots), ("restoration", restoration),
                         ("segmentation", segmentation), ("selftest", selftest)):
        p = sub.add_parser(name, description=module.__doc__)
        p.add_argument("--out", type=Path, help="New aggregate JSON path; existing files are refused")
        module.configure(p)
        p.set_defaults(run=module.run)
    return ap


def main():
    ap = parser()
    args = ap.parse_args()
    if args.out and args.out.exists():
        ap.error("Output exists; choose a new path")
    try:
        result = strict_json(args.run(args))
        if args.out:
            write_json(args.out, result)
        print(json.dumps(result, indent=2, allow_nan=False))
        if args.task == "selftest" and not result["pass"]:
            return 1
        return 0
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError, KeyError, AssertionError) as error:
        print(json.dumps({"schema_version": "1.0", "task": args.task, "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
