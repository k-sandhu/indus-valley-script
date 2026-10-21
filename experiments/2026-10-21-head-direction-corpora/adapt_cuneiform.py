"""Map run B's cuneiform records onto the record form checked by validate_records.py.

Usage: python -I experiments/2026-10-21-head-direction-corpora/adapt_cuneiform.py --records <jsonl> --out <new jsonl>

Three differences of form, none of content (AMENDMENT-4.md):
  1. a record without words keeps one empty line (`lines: [[]]`), as SCHEMA.md asks for basis `none`;
  2. run B's `site_unknown_reason` is copied to `site_reason`;
  3. a word with no sign units (a lacuna such as `[...]`, only in damaged records) is removed with its
     members, tags, tag sources, glosses, part-of-speech code and line position, and counted in
     `adapter_removed_lacuna_words`.
Readings, units, sites and completeness are not changed. Standard library only.
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hd_common import read_jsonl, write_jsonl  # noqa: E402

PER_WORD = ("words", "members", "tags", "tag_source", "gloss", "gold", "word_units", "line_of_word", "source_word_refs")


def adapt(record):
    r = dict(record)
    if r.get("site") is None and r.get("site_unknown_reason") and not r.get("site_reason"):
        r["site_reason"] = r["site_unknown_reason"]
    units = r.get("word_units") or []
    empty = [i for i, w in enumerate(units) if not w]
    if empty:
        keep = [i for i in range(len(units)) if i not in set(empty)]
        for field in PER_WORD:
            value = r.get(field)
            if isinstance(value, list) and len(value) == len(units):
                r[field] = [value[i] for i in keep]
        lines, w = [], 0
        for line in record.get("lines") or []:
            kept = []
            for word in line:
                if w not in empty:
                    kept.append(word)
                w += 1
            if kept:
                lines.append(kept)
        r["lines"] = lines
        r["adapter_removed_lacuna_words"] = len(empty)
        # line indices are renumbered after empty lines disappear
        index, line_of_word = 0, []
        for k, line in enumerate(r["lines"]):
            line_of_word.extend([k] * len(line))
        r["line_of_word"] = line_of_word
    if not r.get("lines"):
        r["lines"] = [[]]
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    if args.out.exists():
        sys.exit("refusing existing output")
    rows = [adapt(r) for r in read_jsonl(args.records)]
    write_jsonl(args.out, rows)
    print(json.dumps({"records": len(rows), "lacuna_words_removed": sum(r.get("adapter_removed_lacuna_words", 0) for r in rows),
                      "site_reason_copied": sum(1 for r in rows if r.get("site") is None and r.get("site_reason"))}))


if __name__ == "__main__":
    main()
