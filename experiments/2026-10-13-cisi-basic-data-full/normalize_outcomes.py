"""Make each adjudication's outcome label agree with its decided reading under the bracket rule.

Usage (from the repository root):
  python experiments/2026-10-13-cisi-basic-data-full/normalize_outcomes.py [block-prefix]

The protocol counts a reading as wrong only when it is definite and differs from the decided
reading, or when its bracketed candidates exclude it. Adjudicators sometimes labelled a cell
`both-wrong` when one reader had bracketed the decided reading without choosing it; under the rule
that reader was not wrong. This script recomputes the label from `pass1`, `pass2` and `final` for
every decided (not undecidable) record: first-pass-right, second-pass-right, both-consistent (both
readings allow the decided one) or both-wrong. The adjudicator's label is kept as
`outcome_as_written`. The originals are copied once to assembled/adjudication-original/ before the
first change. Error rates are computed from the readings, not from these labels, so they do not
change; only the outcome counts do.
"""
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cisi_common import cells, consistent  # noqa: E402

ADJ = HERE.parents[1] / "data/raw/2026-10-13-cisi-basic-data-full/assembled/adjudication"
ORIG = ADJ.parent / "adjudication-original"


def allows(column, reading, truth):
    if column == "row" and reading != "absent" and truth != "absent" and " | " in truth:
        return all(consistent(a, b) for a, b in zip(cells(reading), cells(truth)))
    if column == "row" and ("absent" in (reading, truth)):
        return reading == truth
    return consistent(reading, truth)


def main():
    ORIG.mkdir(exist_ok=True)
    changed = {}
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    for f in sorted(ADJ.glob(prefix + "*.adjudication.json")):
        if not (ORIG / f.name).exists():
            shutil.copy2(f, ORIG / f.name)
        records = json.loads(f.read_text(encoding="utf-8"))
        n = 0
        for r in records:
            if r.get("outcome") == "undecidable":
                continue
            if "[" in r["final"]:
                # a cell the adjudicator settled only in part keeps brackets, so it is undecidable
                r.setdefault("outcome_as_written", r["outcome"])
                r["outcome"] = "undecidable"
                n += 1
                continue
            r1 = allows(r["column"], r["pass1"], r["final"])
            r2 = allows(r["column"], r["pass2"], r["final"])
            label = ("both-consistent" if r1 and r2 else "first-pass-right" if r1
                     else "second-pass-right" if r2 else "both-wrong")
            if label != r["outcome"]:
                r.setdefault("outcome_as_written", r["outcome"])
                r["outcome"] = label
                n += 1
        if n:
            f.write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            changed[f.name] = n
    print(json.dumps(changed, indent=1))


if __name__ == "__main__":
    main()
