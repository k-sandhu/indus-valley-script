"""List excavation, museum and FC discrepancies for a page recheck.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/crosscheck.py [--rebuild]
--rebuild runs build_finals.py and merge_volumes.py first, applying recheck/recheck.json
only where blind adjudication has no decision. Writes local recheck/todo.json and
tracked crosscheck-summary.json. Source comparisons never themselves change cells.
"""
from __future__ import annotations

import collections
import itertools
import re
import subprocess
import sys

from cisi_common import (INV, LIPI, TABLE_JOIN, WEBSITE, HERE, arguments, base_key, join_status,
                         load_jsonl, load_merged, main_guard, provenance, records, source_index,
                         table_rows, uncertain, verify_inputs, write_json, consistent)

WEBSITE_CODE_MAP = {"MJD": "MD", "MM": "MM", "LHR": "L", "NMK": "NMP", "NMP": "NMP", "HM": "HM", "HRP": "HM"}


def squash(text):
    return re.sub(r"[\s\-/.,\[\]]", "", text or "").upper()


def expand(text):
    options = []
    for part in re.split(r"(\[[^\]]*\])", text or ""):
        if part.startswith("["):
            if "?" in part:
                return set()
            options.append(part[1:-1].split("/"))
        else:
            options.append([part])
    size = 1
    for option in options:
        size *= len(option)
    if size > 10000:
        return set()
    return {"".join(p) for p in itertools.product(*options)}


def fc_tails(fc, allow_uncertain=False):
    if not fc or (uncertain(fc) and not allow_uncertain):
        return {""}
    tails = set()
    for reading in expand(fc):
        if not reading.isdigit() or reading.startswith("0"):
            tails.add("")
        else:
            rest = reading[1:]
            if rest:
                tails |= {rest, str(int(rest)) if int(rest) else ""}
    return tails or {""}


def excavation_printed(row):
    """Use separately printed numbers; remove only CISI 1's provenance markers."""
    values = []
    for e in row["parsed"]["excavation"]:
        if e["status"] != "printed":
            continue
        for n in e.get("numbers") or [{"printed": e["printed"]}]:
            values.append(re.sub(r"\s*\([ot]\)", "", n["printed"]).strip())
    return values


def strip_area(text):
    return re.sub(r"^[A-Z]+", "", text)


def excavation_keys(rows):
    return {r["cisi"]: {squash(p) + t for p in excavation_printed(r) if not uncertain(p)
                         for t in fc_tails(r["parsed"].get("fc_number"), True)} for r in rows}


def compare_excavation(row, lipi_value, all_keys):
    printed = excavation_printed(row)
    if not printed or not lipi_value:
        return None
    if any(uncertain(p) for p in printed):
        return "cisi-cell-uncertain"
    lv, fc = squash(lipi_value), row["parsed"].get("fc_number")
    tails = fc_tails(fc)
    for p in printed:
        pv = squash(p)
        if lv == pv:
            return "exact"
        if any(lv == pv + t for t in tails if t):
            return "lipi-adds-fc-tail"
        if any(strip_area(lv) == strip_area(pv) + t for t in tails):
            return "area-prefix-differs"
    if not re.search(r"[A-Z]", lv) or not re.search(r"\d{2}", strip_area(lv)):
        return "lipi-incomplete"
    for other, keys in all_keys.items():
        if other != row["cisi"] and lv in keys:
            return "matches-another-entry"
    if uncertain(fc):
        return "cisi-fc-uncertain"
    for p in printed:
        pv = squash(p)
        if lv.startswith(pv) and lv != pv:
            return "same-number-tail-differs"
        if any(t and lv.endswith(t) for t in tails):
            return "number-differs-tail-agrees"
    return "different"


def website_pairs(value):
    return [(WEBSITE_CODE_MAP.get(code, code), num.replace(".", ""))
            for code, num in re.findall(r"\b([A-Z]{2,4})\s*([\d.]+[a-z]?)", value or "")]


def cisi_pairs(row):
    out = []
    for piece in row["parsed"]["museum_holdings"]:
        for h in piece:
            if h.get("number"):
                out.append((h.get("code"), re.sub(r"^(P|LU)-", "", h["number"]).replace(".", "").replace(" ", "")))
            if h.get("nmp_accession"):
                out.append(("NMP", h["nmp_accession"].replace(".", "")))
    return out


def compare_museum(row, values):
    if not values or not row["parsed"]["museum_number_usable"]:
        return None
    wp, cp = {p for v in values for p in website_pairs(v)}, set(cisi_pairs(row))
    if wp & cp:
        return "agree"
    if any(uncertain(n) for _, n in cp):
        return "cisi-cell-uncertain"
    if {n for _, n in wp} & {n for _, n in cp}:
        return "same-number-different-code"
    return "different"


def joined_catalogues(table):
    out = collections.defaultdict(list)
    for r in table:
        if r.get("disposition") in ("exact", "confirmed") and r.get("source") in ("mackay1938", "marshall1931"):
            out[base_key(r["cisi"])].append(r)
    return out


def fc_check(row, catalogue):
    fc = row["parsed"].get("fc_number")
    if uncertain(fc):
        return "fc-uncertain"
    if not re.fullmatch(r"\d{4}", fc or ""):
        return "fc-missing-or-nonnumeric"
    num = catalogue.get("catalogue_no", "").strip()
    if not re.fullmatch(r"\d+", num):
        return "catalogue-nonnumeric"
    offset = {"mackay1938": 2000, "marshall1931": 1000}[catalogue["source"]]
    return "match" if int(fc) == offset + int(num) else "differ"


def crosscheck_rows(rows, index, table):
    all_keys, catalogues = excavation_keys(rows), joined_catalogues(table)
    todo, counts = {}, collections.Counter()
    dispositions = collections.Counter()

    def add(row, col, kind, other):
        key = (row["cisi"], col)
        if key not in todo:
            todo[key] = {"cisi": row["cisi"], "column": col, "final": row[{"col2": "col2_fc", "col3": "col3_excavation", "col4": "col4_museum"}[col]],
                         "blind_decided": col in row.get("blind_adjudicated_columns", []) or row.get("block") == "pilot",
                         "reasons": []}
        todo[key]["reasons"].append({"kind": kind, **other})
        counts[kind] += 1

    for row in rows:
        status, fams = join_status(row, index)
        dispositions[status] += 1
        if status == "one-family":
            fs = index["families"][fams[0]]
            exc = sorted({INV.norm(f["metadata"].get("excavation-idno")) for f in fs if INV.usable("excavation-idno", f["metadata"].get("excavation-idno"))})
            for lv in exc:
                kind = compare_excavation(row, lv, all_keys)
                if kind is None:
                    kind = "cisi-number-not-printed"
                if kind and kind not in ("exact", "lipi-adds-fc-tail", "area-prefix-differs"):
                    add(row, "col3", "excavation-" + kind, {"lipi_family": fams[0], "lipi_excavation": lv})
            keys = {INV.norm(f["metadata"].get("cisi")) for f in fs}
            museum = sorted({v for k in keys for v in index["museum"].get(k, ())})
            kind = compare_museum(row, museum)
            if kind is None and museum:
                kind = "cisi-number-not-printed"
            if kind and kind != "agree":
                add(row, "col4", "museum-" + kind, {"website_museum": museum, "lipi_family": fams[0]})
        if row["cisi"].startswith("M-"):
            for catalogue in catalogues.get(base_key(row["cisi"]), ()):
                kind = fc_check(row, catalogue)
                counts["fc-table-" + kind] += 1
                bracket_excludes = False
                if kind == "fc-uncertain" and re.fullmatch(r"\d+", catalogue.get("catalogue_no", "")):
                    expected = {"mackay1938": 2000, "marshall1931": 1000}[catalogue["source"]] + int(catalogue["catalogue_no"])
                    bracket_excludes = not consistent(row["parsed"].get("fc_number"), str(expected))
                if kind in ("differ", "fc-missing-or-nonnumeric") or bracket_excludes:
                    reason = "fc-rule-bracket-excludes" if bracket_excludes else "fc-rule-differs"
                    add(row, "col2", reason, {"source": catalogue["source"], "catalogue_no": catalogue["catalogue_no"],
                                                         "lipi_family": catalogue["lipi_family_id"]})
    return list(todo.values()), {"rows": len(rows), "join_status": dict(dispositions), "comparison_counts": dict(counts),
                                 "recheck_cells": len(todo), "recheck_rows": len({key[0] for key in todo}),
                                 "by_column": dict(collections.Counter(key[1] for key in todo)),
                                 "protected_cells": sum(t["blind_decided"] for t in todo.values()),
                                 "count_rule": "Recheck cells are unique CISI/column pairs. Comparison counts count each source comparison, including distinct face values and catalogue rows."}


def main():
    ap = arguments(__doc__.splitlines()[0])
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--lipi", type=type(LIPI), default=LIPI)
    ap.add_argument("--website", type=type(WEBSITE), default=WEBSITE)
    ap.add_argument("--table-join", type=type(TABLE_JOIN), default=TABLE_JOIN)
    args = ap.parse_args()
    if args.rebuild:
        shared = ["--raw", str(args.raw), "--out", str(args.out), "--blocks", str(args.blocks)]
        for block in args.block:
            shared += ["--block", block]
        if args.allow_partial:
            shared += ["--allow-partial"]
        for script in ("build_finals.py", "merge_volumes.py"):
            subprocess.run([sys.executable, str(HERE / script), *shared], check=True)
    paths = {"lipi": args.lipi, "website": args.website, "table_join": args.table_join,
             **{v: args.raw / f"{v}-basic-data.jsonl" for v in ("cisi1", "cisi2")}}
    inputs = provenance(paths)
    rows = load_merged(args.raw, require_both=not args.allow_partial)
    index = source_index(load_jsonl(args.lipi), load_jsonl(args.website))
    todo, summary = crosscheck_rows(rows, index, table_rows(args.table_join))
    recheck = args.raw / "recheck/recheck.json"
    if recheck.exists():
        from build_finals import recheck_map
        current = recheck_map(recheck)
        summary["recorded_rechecks"] = dict(collections.Counter(r["outcome"] for r in current.values()))
        inputs.update(provenance({"recheck": recheck}))
    summary["inputs"] = inputs
    verify_inputs(inputs)
    write_json(args.raw / "recheck/todo.json", todo, local=True)
    write_json(args.out / "crosscheck-summary.json", summary)
    print(f"Listed {summary['recheck_cells']} cells on {summary['recheck_rows']} rows for page recheck.")


if __name__ == "__main__":
    main_guard(main)
