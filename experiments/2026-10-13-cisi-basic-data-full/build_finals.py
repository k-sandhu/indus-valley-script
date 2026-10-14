"""Apply complete blind adjudications, then permitted non-blind rechecks.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/build_finals.py [--block <id>] [--allow-partial]
Writes local final/<block>.final.txt, .final.jsonl, .changes.json and
.parse-report.json; tracked accuracy/<block>.accuracy.json and accuracy-summary.json.
All selected blocks are validated before any final is written.
"""
from __future__ import annotations

import collections

from cisi_common import (OUTCOMES, RECHECK_OUTCOMES, SHORT, arguments, block_list, cells,
                         column, consistent, identity, main_guard, provenance, records,
                         uncertain, verify_inputs, ws, write_json, write_jsonl, local_path)
from cisi_parse import parse_line, parser_report
from compare_passes import compare_block


def rates(value):
    n = value["cells"]
    for label, count in (("agreement", value["agreements"]),
                         ("first_pass_error", value["first_pass_errors"]),
                         ("second_pass_error", value["second_pass_errors"]),
                         ("first_pass_error_upper", value["first_pass_errors"] + value["undecidable_first_definite"]),
                         ("second_pass_error_upper", value["second_pass_errors"] + value["undecidable_second_definite"])):
        value[label + "_rate"] = count / n if n else None
        value[label + "_percent"] = round(100 * count / n, 3) if n else None
    return value


def empty_score():
    return {"cells": 0, "agreements": 0, "disagreements": 0, "first_pass_errors": 0, "second_pass_errors": 0,
            "undecidable_first_definite": 0, "undecidable_second_definite": 0,
            "missing_first": 0, "missing_second": 0, "outcomes": dict.fromkeys(OUTCOMES, 0)}


def aggregate(scores):
    out = empty_score()
    for score in scores:
        for k in out:
            if k == "outcomes":
                for outcome in OUTCOMES:
                    out[k][outcome] += score[k][outcome]
            else:
                out[k] += score[k]
    return rates(out)


def validate_decision(d, todo, corrigenda=False):
    if not all(k in d for k in ("cisi", "column", "pass1", "pass2", "outcome", "final")):
        raise ValueError("incomplete adjudication record")
    if d.get("outcome") not in OUTCOMES or not isinstance(d.get("final"), str):
        raise ValueError("invalid adjudication outcome or final for " + todo["cisi"] + ":" + todo["column"])
    for p in ("pass1", "pass2"):
        if ws(d.get(p)) != ws(todo[p]):
            raise ValueError("stale adjudication reading for " + todo["cisi"] + ":" + todo["column"])
    truth = d["final"]
    if d["outcome"] == "undecidable":
        if not uncertain(truth):
            raise ValueError("undecidable final must contain brackets: " + todo["cisi"] + ":" + todo["column"])
    else:
        if uncertain(truth):
            raise ValueError("decided final must be definite: " + todo["cisi"] + ":" + todo["column"])
        if todo["column"] == "row" and not corrigenda:
            def allows(reading):
                if reading == "absent" or truth == "absent":
                    return reading == truth
                return all(consistent(a, b) for a, b in zip(cells(reading), cells(truth)))
        else:
            allows = lambda reading: consistent(reading, truth)
        right1, right2 = allows(todo["pass1"]), allows(todo["pass2"])
        outcome = d["outcome"]
        if (outcome == "first-pass-right" and not right1) or (outcome == "second-pass-right" and not right2) or (outcome == "both-wrong" and (right1 or right2)) or (outcome == "both-consistent" and not (right1 and right2)):
            raise ValueError("outcome contradicts final: " + todo["cisi"] + ":" + todo["column"])
    if todo["column"] == "row" and truth != "absent" and not corrigenda and identity(cells(truth)[0]) != todo["cisi"]:
        raise ValueError("row decision changes identity; remove and add through separate row decisions: " + todo["cisi"])
    if todo["column"] == "col1" and identity(truth) != todo["cisi"]:
        raise ValueError("cell decision changes identity; use separate row decisions: " + todo["cisi"])


def recheck_map(path):
    out = {}
    if not path.exists():
        return out
    for r in records(path):
        if r.get("outcome") not in RECHECK_OUTCOMES or not isinstance(r.get("final"), str):
            raise ValueError("invalid recheck record")
        col = column(r.get("column"))
        if col == "row":
            raise ValueError("rechecks may change cells, not row presence")
        key = (r["cisi"], col)
        if key in out:
            raise ValueError("duplicate recheck decision: " + ":".join(key))
        if r["outcome"] == "ambiguous" and not uncertain(r["final"]):
            raise ValueError("ambiguous recheck needs brackets: " + ":".join(key))
        if r["outcome"] != "ambiguous" and uncertain(r["final"]):
            raise ValueError("definite recheck outcome has brackets: " + ":".join(key))
        if col == "col1" and identity(r["final"]) != r["cisi"]:
            raise ValueError("recheck cannot change row identity")
        out[key] = r
    return out


def prepare_block(spec, raw, rechecks=None):
    compared, summary = compare_block(spec, raw)
    if compared is None:
        return None, summary, [spec["block"] + ":missing-pass"]
    rechecks = rechecks or {}
    todo = {(t["cisi"], t["column"]): t for t in compared["todo"]}
    adj_path = raw / "adjudication" / f"{spec['block']}.adjudication.json"
    decisions = {}
    adj_inputs = provenance({"adjudication": adj_path})
    if adj_path.exists():
        for d in records(adj_path):
            key = (d["cisi"], column(d["column"]))
            if key in decisions:
                raise ValueError("duplicate adjudication: " + ":".join(key))
            if key not in todo:
                raise ValueError("adjudication has no current disagreement: " + ":".join(key))
            validate_decision(d, todo[key], spec.get("kind") == "corrigenda")
            decisions[key] = d
    missing = [spec["block"] + ":" + ":".join(k) for k in todo if k not in decisions]
    if missing:
        return None, summary, missing
    summary["inputs"].update(adj_inputs)
    recheck_path = raw / "recheck/recheck.json"
    summary["inputs"].update(provenance({"recheck": recheck_path}))
    p1, p2 = compared["pass1"], compared["pass2"]
    corrigenda = spec.get("kind") == "corrigenda"
    score_cols = ["row"] if corrigenda else SHORT
    scores = {col: empty_score() for col in score_cols}
    final_rows, parsed, changes = [], [], []
    row_stats = {"decisions": dict.fromkeys(OUTCOMES, 0), "first_pass_omissions": 0, "second_pass_omissions": 0,
                 "first_pass_spurious_rows": 0, "second_pass_spurious_rows": 0, "absent_after_adjudication": 0}
    rc = collections.Counter()
    for key in compared["order"]:
        a, b = p1["rows"].get(key), p2["rows"].get(key)
        rd = decisions.get((key, "row"))
        chosen = list(a if a is not None else b)
        if rd:
            row_stats["decisions"][rd["outcome"]] += 1
            absent = rd["final"] == "absent"
            if rd["outcome"] != "undecidable":
                row_stats["first_pass_omissions"] += a is None and not absent
                row_stats["second_pass_omissions"] += b is None and not absent
                row_stats["first_pass_spurious_rows"] += a is not None and absent
                row_stats["second_pass_spurious_rows"] += b is not None and absent
            if absent:
                row_stats["absent_after_adjudication"] += 1
                chosen = None
            else:
                chosen = [rd["final"]] if corrigenda else cells(rd["final"])
        for i, col in enumerate(score_cols):
            s = scores[col]
            av, bv = a[i] if a is not None else None, b[i] if b is not None else None
            s["cells"] += 1
            agrees = av is not None and bv is not None and ws(av) == ws(bv)
            s["agreements"] += agrees
            s["disagreements"] += not agrees
            s["missing_first"] += av is None
            s["missing_second"] += bv is None
            decision = decisions.get((key, col)) if not rd else rd
            if decision:
                # Whole-row decisions protect every cell; spurious presence is counted above.
                truth = (chosen[i] if chosen is not None else None) if rd else decision["final"]
                s["outcomes"][decision["outcome"]] += 1
                if decision["outcome"] == "undecidable":
                    s["undecidable_first_definite"] += av is not None and not uncertain(av)
                    s["undecidable_second_definite"] += bv is not None and not uncertain(bv)
                elif truth is not None:
                    s["first_pass_errors"] += av is not None and not consistent(av, truth)
                    s["second_pass_errors"] += bv is not None and not consistent(bv, truth)
                if not rd:
                    chosen[i] = decision["final"]
            if chosen is not None and not corrigenda and (key, col) in rechecks:
                r = rechecks[(key, col)]
                if decision:
                    rc["blocked_by_blind_adjudication"] += 1
                else:
                    if r["outcome"] in ("confirmed", "source-defect") and ws(r["final"]) != ws(chosen[i]):
                        raise ValueError("confirm/source-defect recheck changes cell: " + key + ":" + col)
                    if "pass1" in r and ws(r["pass1"]) != ws(chosen[i]):
                        raise ValueError("stale recheck reading: " + key + ":" + col)
                    chosen[i] = r["final"]
                    rc[r["outcome"]] += 1
            new = chosen[i] if chosen is not None else None
            if av != new:
                changes.append({"cisi": key, "column": col, "pass1": av, "final": new,
                                "reason": "blind-" + decision["outcome"] if decision else "recheck-" + rechecks[(key, col)]["outcome"]})
        if chosen is not None:
            final_rows.append((key, chosen))
            if not corrigenda:
                row = parse_line(" | ".join(chosen), p1["page"] or spec.get("printed_page"), p1["pdf"] or spec.get("pdf_page"),
                                 spec["volume"], p1["sites"].get(key) or p2["sites"].get(key))
                row["block"] = spec["block"]
                row["blind_adjudicated_columns"] = SHORT if rd else [col for col in SHORT if (key, col) in decisions]
                row["rechecked_columns"] = [col for col in SHORT if (key, col) in rechecks and not rd and (key, col) not in decisions]
                parsed.append(row)
    accuracy = {**summary, "status": "final", "by_column": {c: rates(s) for c, s in scores.items()},
                "total": aggregate(scores.values()), "final_rows": len(final_rows), "row_adjudication": row_stats,
                "rechecks": dict(rc), "parser_review_rows": len(parser_report(parsed)),
                "parser_counts": {field + "_rows": sum(bool(r["parsed"].get(field)) for r in parsed)
                                  for field in ("unknown_museum_codes", "unknown_photo_codes", "unparsed_museum_fragments")},
                "accuracy_stage": "Blind comparison and adjudication, before non-blind rechecks.",
                "outcome_count_rule": "A whole-row decision is counted once in row_adjudication and in each affected column; duplicate review can also adjudicate agreeing canonical cells."}
    verify_inputs(accuracy["inputs"])
    return {"rows": final_rows, "parsed": parsed, "changes": changes, "pass1": p1, "pass2": p2, "accuracy": accuracy}, summary, []


def write_block(spec, result, raw, out):
    path = local_path(raw / "final" / f"{spec['block']}.final.txt")
    lines = [f"# final, {spec['volume']}, block {spec['block']}, p. {spec.get('printed_page', result['pass1']['page'])} (PDF {spec.get('pdf_page', result['pass1']['pdf'])})"]
    lines.extend("# source-pass1 " + line.lstrip("# ") for line in result["pass1"]["comments"] if not line.lower().startswith("# site:"))
    site = None
    for key, cs in result["rows"]:
        row_site = result["pass1"]["sites"].get(key) or result["pass2"]["sites"].get(key)
        if row_site and row_site != site:
            lines.append("# site: " + row_site)
            site = row_site
        lines.append(" | ".join(cs))
        lines.extend(dict.fromkeys(result["pass1"]["row_comments"].get(key, []) + result["pass2"]["row_comments"].get(key, [])))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if spec.get("kind") != "corrigenda":
        write_jsonl(path.with_suffix(".jsonl"), result["parsed"])
        write_json(path.with_name(spec["block"] + ".parse-report.json"), parser_report(result["parsed"]), local=True)
    write_json(path.with_name(spec["block"] + ".changes.json"), result["changes"], local=True)
    result["accuracy"]["final_outputs"] = provenance({"text": path, **({"jsonl": path.with_suffix(".jsonl")} if spec.get("kind") != "corrigenda" else {})})
    write_json(out / "accuracy" / f"{spec['block']}.accuracy.json", result["accuracy"])


def accuracy_summary(results, missing):
    by_volume = {}
    for volume in ("cisi1", "cisi2"):
        matching = [r["accuracy"] for r in results if r["accuracy"]["volume"] == volume and r["accuracy"]["kind"] == "entries"]
        cols = {col: aggregate(a["by_column"][col] for a in matching) for col in SHORT}
        by_volume[volume] = {"blocks": len(matching), "by_column": cols, "total": aggregate(cols.values()),
                             "row_adjudication": {k: sum(a["row_adjudication"][k] for a in matching)
                                                  for k in ("first_pass_omissions", "second_pass_omissions", "first_pass_spurious_rows", "second_pass_spurious_rows")}}
    return {"complete_for_selected_blocks": not missing, "missing_adjudications_or_passes": missing,
            "volumes": by_volume, "pilot": "Pilot accuracy remains in its frozen package; these rates cover new blocks only.",
            "corrigenda": [r["accuracy"] for r in results if r["accuracy"]["kind"] == "corrigenda"]}


def main():
    args = arguments(__doc__.splitlines()[0]).parse_args()
    specs, prepared, missing = block_list(args), [], []
    recheck_inputs = provenance({"recheck": args.raw / "recheck/recheck.json"})
    checks = recheck_map(args.raw / "recheck/recheck.json")
    for spec in specs:
        result, _, gaps = prepare_block(spec, args.raw, checks)
        missing.extend(gaps)
        if result:
            prepared.append((spec, result))
    if missing and not args.allow_partial:
        raise ValueError("unresolved disagreements or missing passes:\n" + "\n".join(missing))
    for spec, result in prepared:
        verify_inputs(result["accuracy"]["inputs"])
    verify_inputs(recheck_inputs)
    for spec, result in prepared:
        write_block(spec, result, args.raw, args.out)
    report = accuracy_summary([r for _, r in prepared], missing)
    report["selection_is_partial"] = bool(args.block) or bool(missing)
    selected = {(key, col) for _, r in prepared for key, _ in r["rows"] for col in SHORT}
    report["recheck_records_outside_selected_final_rows"] = len(set(checks) - selected)
    write_json(args.out / "accuracy-summary.json", report)
    print(f"Built {len(prepared)} blocks; {len(missing)} unresolved locators.")


if __name__ == "__main__":
    main_guard(main)
