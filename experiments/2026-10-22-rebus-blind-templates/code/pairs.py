"""Count ordered pairs of identified signs in one half of the split, through bench.shots.

A pair is two signs adjacent in reading order on a single-line face; a gapped pair has
exactly one sign between them. Counts are distinct split components (aliases and
identical texts joined), so a text copied on many objects counts once.

    python experiments/2026-10-22-rebus-blind-templates/code/pairs.py SPEC.json HALF OUT.json [--shot NAME]
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from bench import shots  # noqa: E402
from bench.common import sha256  # noqa: E402

SPLIT = HERE.parent / "round.json"


def count(rows, code_to_ident):
    adj, gap = defaultdict(set), defaultdict(set)
    faces = 0
    for r in rows:
        if not r.get("single_line"):
            continue
        faces += 1
        seq = [code_to_ident.get(c) for c in r["signs_reading_rtl"]]
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if a and b and a != b:
                adj[(a, b)].add(r["component"])
        for i in range(len(seq) - 2):
            a, x, b = seq[i], seq[i + 1], seq[i + 2]
            if a and b and a != b and x is None and r["signs_reading_rtl"][i + 1].isdigit() and r["signs_reading_rtl"][i + 1] != "000":
                gap[(a, b)].add(r["component"])
    fmt = lambda d: sorted(([a, b, len(v)] for (a, b), v in d.items()), key=lambda x: (-x[2], x[0], x[1]))  # noqa: E731
    return faces, fmt(adj), fmt(gap)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("half", choices=["discovery", "confirmation"])
    ap.add_argument("out")
    ap.add_argument("--shot")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        print("refusing to overwrite", out)
        return 1
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    code_to_ident = {c: k for k, v in spec["identifications"].items() for c in v["codes"]}
    rows, event = shots.load_half(SPLIT, a.half, a.shot)
    faces, adj, gap = count(rows, code_to_ident)
    res = {"schema_version": "1.0", "task": "rebus-blind-templates/pairs", "synthetic": False,
           "created_utc": datetime.now(timezone.utc).isoformat(), "half": a.half, "access_event": event,
           "provenance": {"spec": {"path": Path(a.spec).resolve().relative_to(ROOT).as_posix(), "sha256": sha256(a.spec)},
                          "split": {"path": SPLIT.relative_to(ROOT).as_posix()},
                          "code": {"path": Path(__file__).resolve().relative_to(ROOT).as_posix(), "sha256": sha256(__file__)}},
           "single_line_faces": faces,
           "adjacent_pairs": [{"first": x, "second": y, "components": n} for x, y, n in adj],
           "gapped_pairs": [{"first": x, "second": y, "components": n} for x, y, n in gap]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for th in (1, 2, 3):
        print(a.half, "adjacent pairs with >=", th, "components:", sum(1 for p in adj if p[2] >= th),
              "| gapped:", sum(1 for p in gap if p[2] >= th))
    return 0


if __name__ == "__main__":
    sys.exit(main())
