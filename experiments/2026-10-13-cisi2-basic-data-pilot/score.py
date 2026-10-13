"""Cell-level agreement between the first and second passes, and the adjudicated error rates.

Usage (from the repository root):
  python experiments/2026-10-13-cisi2-basic-data-pilot/score.py disagreements
      writes data/raw/2026-10-13-cisi2-basic-data-pilot/adjudication-todo.json (local, with values)
  python experiments/2026-10-13-cisi2-basic-data-pilot/score.py score
      reads the local adjudication.json and writes accuracy.json here (counts only)
  Add --full to either command to compare the first pass with the full second reading of
  Amendment 1 (pass2b/pass2b.txt; adjudication-full-todo.json, adjudication-full.json,
  accuracy-full.json).

Comparison rule (PROTOCOL.md): cells are compared after collapsing whitespace. A secondary
measure, added after the first comparison was seen, also ignores punctuation (. , ; :) and
compares only letters, digits and brackets. An uncertain-marked first-pass cell counts as
an error only if none of its bracketed candidates gives the adjudicated reading. Cells the
scan cannot decide are excluded from the error count; the upper error bound adds those in
which the first pass gave a definite (unbracketed) reading.
"""
import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOCAL = ROOT / "data/raw/2026-10-13-cisi2-basic-data-pilot"
COLS = ["col1", "col2_fc", "col3_excavation", "col4_museum", "col5_photographs"]


def read_txt(path):
    rows = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cells = [c.strip() for c in line.split(" | ")]
        if len(cells) != 5:
            raise ValueError("bad line in %s: %r" % (path, line))
        cisi = re.match(r"^([A-Za-z?]+-\d+[a-z]?)", cells[0]).group(1)
        rows[cisi] = dict(zip(COLS, cells))
    return rows


def ws(text):
    return re.sub(r"\s+", " ", text).strip()


def alnum(text):
    return re.sub(r"[^0-9A-Za-z\[\]/?]", "", text)


def expansions(text):
    """All readings allowed by bracket notation: [a/b] gives a or b; [?] and [??] match any."""
    parts = re.split(r"(\[[^\]]*\])", text)
    options = []
    for p in parts:
        if p.startswith("[") and p.endswith("]"):
            inner = p[1:-1]
            options.append(None if "?" in inner else inner.split("/"))
        else:
            options.append([p])
    if any(o is None for o in options):
        pattern = "".join(".*" if o is None else "(?:%s)" % "|".join(re.escape(x) for x in o) for o in options)
        return ("regex", pattern)
    return ("set", {"".join(c) for c in itertools.product(*options)})


def consistent(first, truth):
    kind, val = expansions(ws(first))
    t = ws(truth)
    if kind == "regex":
        return re.fullmatch(val, t) is not None
    return t in val


def main():
    mode = sys.argv[1]
    full = "--full" in sys.argv[2:]
    sample = json.loads((HERE / "sample.json").read_text(encoding="utf-8"))
    p1 = {}
    for f in ("pass1-p435.txt", "pass1-p436.txt"):
        p1.update(read_txt(LOCAL / f))
    if full:
        # Amendment 1: the full second reading of all rows.
        p2 = read_txt(LOCAL / "pass2b" / "pass2b.txt")
        cisis = list(p1)
        todo_name, adj_name, out_name = "adjudication-full-todo.json", "adjudication-full.json", "accuracy-full.json"
    else:
        p2 = read_txt(LOCAL / "pass2" / "pass2.txt")
        cisis = [s["cisi"] for s in sample["sample"]]
        todo_name, adj_name, out_name = "adjudication-todo.json", "adjudication.json", "accuracy.json"
    missing = [c for c in cisis if c not in p2]
    if mode == "disagreements":
        todo = []
        for c in cisis:
            for col in COLS:
                a, b = p1[c][col], p2.get(c, {}).get(col, "")
                if ws(a) != ws(b):
                    todo.append({"cisi": c, "column": col, "pass1": a, "pass2": b,
                                 "alnum_equal": alnum(a) == alnum(b)})
        (LOCAL / todo_name).write_text(json.dumps(todo, indent=1, ensure_ascii=False), encoding="utf-8")
        print(len(todo), "disagreements;", "missing in pass 2:", missing)
        return
    adj = {(a["cisi"], a["column"]): a for a in json.loads((LOCAL / adj_name).read_text(encoding="utf-8"))}
    by_col = {}
    for col in COLS:
        n = agree_ws = agree_alnum = err1 = err2 = undecided = unc1 = undec_p1_definite = 0
        for c in cisis:
            if c not in p2:
                continue
            n += 1
            a, b = p1[c][col], p2[c][col]
            unc1 += "[" in a
            if ws(a) == ws(b):
                agree_ws += 1
                agree_alnum += 1
                continue
            agree_alnum += alnum(a) == alnum(b)
            d = adj[(c, col)]
            if d["outcome"] == "undecidable":
                undecided += 1
                # the first pass gave a definite reading that the scan cannot confirm
                undec_p1_definite += "[" not in a
                continue
            truth = d["adjudicated"]
            if not consistent(a, truth):
                err1 += 1
            if not consistent(b, truth):
                err2 += 1
        by_col[col] = {
            "cells": n,
            "agree_whitespace_normalized": agree_ws,
            "agreement_percent": round(100 * agree_ws / n, 1) if n else None,
            "agree_ignoring_punctuation": agree_alnum,
            "agreement_ignoring_punctuation_percent": round(100 * agree_alnum / n, 1) if n else None,
            "disagreements": n - agree_ws,
            "first_pass_errors_after_adjudication": err1,
            "first_pass_error_percent": round(100 * err1 / n, 1) if n else None,
            "second_pass_errors_after_adjudication": err2,
            "undecidable_from_scan": undecided,
            "first_pass_cells_marked_uncertain": unc1,
            "undecidable_where_first_pass_was_definite": undec_p1_definite,
            "first_pass_error_percent_upper": round(100 * (err1 + undec_p1_definite) / n, 1) if n else None,
        }
    tot = {k: sum(v[k] for v in by_col.values()) for k in
           ("cells", "agree_whitespace_normalized", "agree_ignoring_punctuation", "disagreements",
            "first_pass_errors_after_adjudication", "second_pass_errors_after_adjudication", "undecidable_from_scan",
            "undecidable_where_first_pass_was_definite")}
    tot["first_pass_error_percent_upper"] = round(100 * (tot["first_pass_errors_after_adjudication"]
                                                         + tot["undecidable_where_first_pass_was_definite"]) / tot["cells"], 1)
    tot["agreement_percent"] = round(100 * tot["agree_whitespace_normalized"] / tot["cells"], 1)
    tot["first_pass_error_percent"] = round(100 * tot["first_pass_errors_after_adjudication"] / tot["cells"], 1)
    rows_with_error = sorted({k[0] for k, v in adj.items() if v["outcome"] in ("second-pass-right", "both-wrong")})
    out = {"sample_rows": len(cisis), "rows_read_in_pass2": len(cisis) - len(missing), "missing_in_pass2": missing,
           "by_column": by_col, "total": tot,
           "rows_with_a_first_pass_error": len([r for r in rows_with_error
                                                 if any(not consistent(p1[r][c], adj[(r, c)]["adjudicated"])
                                                        for c in COLS if (r, c) in adj and adj[(r, c)]["outcome"] != "undecidable")]),
           "adjudication_outcomes": {o: sum(1 for v in adj.values() if v["outcome"] == o)
                                     for o in ("first-pass-right", "second-pass-right", "both-wrong", "undecidable")},
           "frozen_first_pass_sha256": sample["frozen_first_pass_sha256"]}
    (HERE / out_name).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
