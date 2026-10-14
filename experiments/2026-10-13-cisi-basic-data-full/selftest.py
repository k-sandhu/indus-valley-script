"""Test generated readings and reproduce the frozen pilot's coverage.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/selftest.py
Creates a new codex/selftest-<timestamp>/ local fixture directory and writes
selftest.json here. No full-run pass file or image is opened.
"""
from __future__ import annotations

import datetime as dt
import json
import random
import subprocess
import sys
import traceback
from pathlib import Path

from cisi_common import (HERE, INV, LIPI, PILOT, RAW, ROOT, SHORT, SOURCE_SETS, TABLE_JOIN,
                         WEBSITE, consistent, load_json, load_jsonl, provenance, source_index,
                         table_rows, write_json, write_jsonl)
from cisi_parse import parse_line, parse_museum, parse_pass
from compare_passes import compare_block
from build_finals import prepare_block, recheck_map, write_block
from merge_volumes import merge_rows
from crosscheck import compare_excavation, crosscheck_rows, excavation_keys, fc_check
from join_full import (combined_report, coverage_report, extension_suffixes, join_rows,
                       predictions)


def require(condition):
    if not condition:
        raise AssertionError("check failed; value details remain in local fixtures")


def expect_error(callback, fragment=None):
    try:
        callback()
    except ValueError as e:
        if fragment:
            require(fragment in str(e))
        return
    raise AssertionError("expected refusal did not occur")


def main():
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    scratch = RAW / "codex" / ("selftest-" + stamp)
    scratch.mkdir(parents=True, exist_ok=False)
    raw, out = scratch / "raw", scratch / "reports"
    rng = random.Random(20261013)
    seed_num = rng.randrange(100, 700)
    number = lambda offset=0: str(seed_num * 10 + offset)
    fc = lambda offset=0: str(2000 + seed_num + offset)
    entry = lambda key, offset=0: [key, fc(offset), "DK " + number(offset), "MD " + str(seed_num + offset), "JL " + number(offset + 40)]
    specs = [{"block": "cisi1-fixture-a", "volume": "cisi1", "printed_page": 366, "pdf_page": 402, "strips": 4},
             {"block": "cisi2-fixture-b", "volume": "cisi2", "printed_page": 437, "pdf_page": 472, "strips": 3},
             {"block": "cisi2-fixture-c", "volume": "cisi2", "printed_page": 438, "pdf_page": 473, "strips": 2}]
    blocks_path = scratch / "blocks.json"
    write_json(blocks_path, specs, local=True)
    a1 = {f"M-{i}": entry(f"M-{i}", i) for i in range(1, 10)}
    a2 = {k: list(v) for k, v in a1.items()}
    a1["M-1"][2] = "DK " + number(1)[:-1] + "[1/3]"
    a2["M-1"][4] = a1["M-1"][4].replace(" ", "\t")
    a2["M-2"][1] = "[" + a1["M-2"][1] + "/" + fc(22) + "]"
    a2["M-3"][3] = "MD " + number(73)
    del a2["M-4"]
    del a1["M-5"]
    alternate_duplicate = list(a1["M-6"])
    alternate_duplicate[3] = "MD " + number(76)
    a2["M-8"][4] = "HU " + number(88)
    del a2["M-9"]
    piece1, piece2 = entry("M-7 (1)", 7), entry("(2)", 17)
    piece2[1] = ""
    b1 = {f"H-{i}": entry(f"H-{i}", 100 + i) for i in range(1, 4)}
    b2 = {k: list(v) for k, v in b1.items()}
    b2["H-1"][1] = fc(151)
    c1 = [["H-10", "", "???", "EXB", ""]]

    def pass_file(spec, p, rows):
        path = raw / p / f"{spec['block']}.{p}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        comments = [f"# {p}, CISI {spec['volume'][-1]} printed p. {spec['printed_page']} (PDF {spec['pdf_page']}), block {spec['block']}",
                    "# site: synthetic site", "# started 2026-10-13T01:00:00-04:00"]
        lines = comments + [" | ".join(cs) for cs in rows] + ["# finished 2026-10-13T01:02:00-04:00"]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    for p, rows in (("pass1", a1), ("pass2", a2)):
        expanded = []
        for key, cs in rows.items():
            if key == "M-7":
                expanded.extend([piece1, piece1, piece2])
            else:
                expanded.append(cs)
                if key == "M-6" and p == "pass1":
                    expanded.append(alternate_duplicate)
        pass_file(specs[0], p, expanded)
    for p, rows in (("pass1", b1), ("pass2", b2)):
        pass_file(specs[1], p, rows.values())
        pass_file(specs[2], p, c1)
    corrigendum = {"block": "cisi1-corrigenda", "volume": "cisi1", "kind": "corrigenda", "strips": 0}
    for p in ("pass1", "pass2"):
        path = raw / p / f"cisi1-corrigenda.{p}.txt"
        path.write_text("# text fixture\n" + "correction " + number(91 if p == "pass1" else 92) + "\n", encoding="utf-8")
        path = raw / p / f"cisi2-corrigenda.{p}.txt"
        path.write_text("# text fixture\n" + "correction " + number(94) + "\n", encoding="utf-8")

    results = []

    def test(name, callback):
        try:
            callback()
        except Exception as e:
            (scratch / (name + ".failure.txt")).write_text(traceback.format_exc(), encoding="utf-8")
            results.append({"name": name, "passed": False, "exception_type": type(e).__name__})
        else:
            results.append({"name": name, "passed": True})

    compared, counts = compare_block(specs[0], raw)
    todo = {(r["cisi"], r["column"]): r for r in compared["todo"]}
    test("one_sided_and_conflicting_duplicate_require_rows", lambda: require({("M-4", "row"), ("M-5", "row"), ("M-6", "row"), ("M-9", "row")} <= todo.keys()))
    test("overlap_deduplicated_and_pieces_combined", lambda: require(counts["duplicates"]["pass1"]["identical_overlap_rows"] == 1 and counts["duplicates"]["pass1"]["piece_lines_combined"] == 1))
    test("whitespace_only_agrees", lambda: require(("M-1", "col5") not in todo))
    test("reading_times", lambda: require(counts["reading_times"]["pass1"]["seconds"] == 120))
    test("strip_estimates_have_neighbours", lambda: require(all(r["strips"] and len(r["strips"]) <= 3 for r in compared["todo"])))
    test("missing_adjudication_refuses_block", lambda: require(prepare_block(specs[0], raw)[0] is None and bool(prepare_block(specs[0], raw)[2])))

    choices = {
        ("M-1", "col3"): ("second-pass-right", a2["M-1"][2]),
        ("M-2", "col2"): ("first-pass-right", a1["M-2"][1]),
        ("M-3", "col4"): ("undecidable", "[" + a1["M-3"][3] + "/" + a2["M-3"][3] + "]"),
        ("M-4", "row"): ("first-pass-right", " | ".join(a1["M-4"])),
        ("M-5", "row"): ("second-pass-right", " | ".join(a2["M-5"])),
        ("M-6", "row"): ("both-wrong", " | ".join(alternate_duplicate)),
        ("M-8", "col5"): ("both-wrong", "CE " + number(98)),
        ("M-9", "row"): ("second-pass-right", "absent"),
    }

    def decisions_for(spec, options):
        comparison, _ = compare_block(spec, raw)
        decisions = [{"cisi": r["cisi"], "column": r["column"], "pass1": r["pass1"], "pass2": r["pass2"],
                      "outcome": options[(r["cisi"], r["column"])][0], "final": options[(r["cisi"], r["column"])][1], "note": "synthetic fixture"}
                     for r in comparison["todo"]]
        path = raw / "adjudication" / f"{spec['block']}.adjudication.json"
        write_json(path, decisions, local=True)
        return path, decisions

    adj_path, adjs = decisions_for(specs[0], choices)
    decisions_for(specs[1], {("H-1", "col2"): ("second-pass-right", b2["H-1"][1])})
    decisions_for(specs[2], {})
    decisions_for(corrigendum, {("line-1", "row"): ("first-pass-right", "correction " + number(91))})
    rechecks = [{"cisi": "H-1", "column": "col2", "outcome": "corrected", "final": fc(181)},
                {"cisi": "H-2", "column": "col3", "outcome": "corrected", "final": "DK " + number(182)},
                {"cisi": "H-3", "column": "col3", "outcome": "ambiguous", "final": "DK [" + number(103) + "/" + number(183) + "]"}]
    write_json(raw / "recheck/recheck.json", rechecks, local=True)
    checks = recheck_map(raw / "recheck/recheck.json")
    prepared, _, missing = prepare_block(specs[0], raw, checks)
    test("complete_adjudication_builds", lambda: require(prepared is not None and not missing and len(prepared["parsed"]) == 8))
    accuracy = prepared["accuracy"]
    test("bracket_candidates_prevent_false_errors", lambda: require(accuracy["by_column"]["col3"]["first_pass_errors"] == 0 and accuracy["by_column"]["col2"]["second_pass_errors"] == 0))
    test("both_wrong_and_upper_rates", lambda: require(accuracy["by_column"]["col5"]["first_pass_errors"] == 1 and accuracy["by_column"]["col5"]["second_pass_errors"] == 1 and accuracy["by_column"]["col4"]["undecidable_first_definite"] == 1 and accuracy["by_column"]["col4"]["undecidable_second_definite"] == 1))
    test("omission_and_spurious_row_counts", lambda: require(accuracy["row_adjudication"]["first_pass_omissions"] == 1 and accuracy["row_adjudication"]["second_pass_omissions"] == 1 and accuracy["row_adjudication"]["first_pass_spurious_rows"] == 1))
    test("piece_fc_preserved", lambda: require(next(r for r in prepared["parsed"] if r["cisi"] == "M-7")["parsed"]["fc_number"] == piece1[1]))
    changed_adjs = [dict(d) for d in adjs]
    changed_adjs[0]["pass1"] = "stale synthetic reading"
    write_json(adj_path, changed_adjs, local=True)
    test("stale_adjudication_refused", lambda: expect_error(lambda: prepare_block(specs[0], raw), "stale"))
    write_json(adj_path, adjs, local=True)
    invalid_adjs = [dict(d) for d in adjs]
    next(d for d in invalid_adjs if d["outcome"] == "undecidable")["final"] = a1["M-3"][3]
    write_json(adj_path, invalid_adjs, local=True)
    test("undecidable_definite_final_refused", lambda: expect_error(lambda: prepare_block(specs[0], raw), "brackets"))
    write_json(adj_path, adjs, local=True)
    prepared_b, _, _ = prepare_block(specs[1], raw, checks)
    test("blind_decision_blocks_recheck", lambda: require(prepared_b["parsed"][0]["col2_fc"] == b2["H-1"][1] and prepared_b["accuracy"]["rechecks"]["blocked_by_blind_adjudication"] == 1))
    test("rechecks_change_agreeing_cells_only", lambda: require(prepared_b["parsed"][1]["col3_excavation"] == rechecks[1]["final"] and "[" in prepared_b["parsed"][2]["col3_excavation"] and prepared_b["accuracy"]["by_column"]["col3"]["first_pass_errors"] == 0))
    test("wildcard_and_partial_bracket_matching", lambda: require(consistent("DK [?]", "DK " + number()) and not consistent("DK [1/3]", "DK " + number())))
    multi = parse_line(" | ".join(["M-20", fc(), "DK " + number() + " (o), HR " + number(1) + " (t)", "IM A " + number(2) + ", ASI " + number(3), "HU " + number(4)]), volume="cisi1")
    test("cisi1_markers_and_multiple_numbers", lambda: require(multi["parsed"]["excavation"][0]["layer"] is None and multi["parsed"]["excavation"][0]["markers"] == ["o", "t"] and len(multi["parsed"]["excavation"][0]["numbers"]) == 2))
    multi_plain = parse_line(" | ".join(["M-22", fc(), "DK " + number() + " HR " + number(1), "EXB", ""]), volume="cisi1")
    test("multiple_unpunctuated_excavation_numbers", lambda: require(len(multi_plain["parsed"]["excavation"][0]["numbers"]) == 2))
    multi_slash = parse_line(" | ".join(["M-23", fc(), "UPM/MD-" + number() + " / HR " + number(1), "EXB", ""]), volume="cisi1")
    test("number_separator_preserves_area_slash", lambda: require(len(multi_slash["parsed"]["excavation"][0]["numbers"]) == 2 and multi_slash["parsed"]["excavation"][0]["numbers"][0]["area_code"] == "UPM/MD"))
    test("cisi1_institution_and_prefixed_number", lambda: require(multi["parsed"]["museum_number_usable"] and multi["parsed"]["museum_holdings"][0][0]["number"].startswith("A ")))
    generic = parse_line(" | ".join(["M-21", fc(), "???", "ZZX " + number(), "ZZP " + number()]), volume="cisi1")
    test("unknown_codes_parsed_and_reported", lambda: require(generic["parsed"]["unknown_museum_codes"] == ["ZZX"] and generic["parsed"]["unknown_photo_codes"] == ["ZZP"] and generic["parsed"]["museum_number_usable"]))
    acc = "50." + number()
    test("year_accession_is_volume_specific", lambda: require(parse_museum("ASI " + acc, "cisi1")[0][0]["nmp_accession"] is None and parse_museum("MD " + acc, "cisi2")[0][0]["nmp_accession"] == acc))
    merged, gaps, _ = merge_rows([("a", prepared["parsed"])], "cisi1")
    test("duplicate_merge_refused", lambda: expect_error(lambda: merge_rows([("a", merged), ("b", merged)], "cisi1"), "duplicate"))
    suffix_rows = [dict(merged[0], cisi="M-1a"), dict(merged[1], cisi="M-3b")]
    test("integer_gaps_ignore_letter_suffixes", lambda: require(merge_rows([("a", suffix_rows)], "cisi1")[1]["M"] == ["M-2"]))

    def run(script, *extra, success=True):
        cmd = [sys.executable, str(HERE / script), "--raw", str(raw), "--out", str(out), "--blocks", str(blocks_path), *extra]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        (scratch / (script + ".last-log.txt")).write_text(result.stdout + result.stderr, encoding="utf-8")
        require((result.returncode == 0) == success)

    test("compare_cli", lambda: run("compare_passes.py"))
    saved = list(adjs)
    write_json(adj_path, adjs[:-1], local=True)
    test("build_cli_preflight_refuses_missing", lambda: run("build_finals.py", success=False))
    test("preflight_writes_no_partial_finals", lambda: require(not (raw / "final").exists()))
    write_json(adj_path, saved, local=True)
    test("build_cli", lambda: run("build_finals.py"))
    synthetic_pilot = scratch / "empty-pilot.jsonl"
    write_jsonl(synthetic_pilot, [])
    test("merge_cli", lambda: run("merge_volumes.py", "--pilot", str(synthetic_pilot)))
    final_path = raw / "final" / (specs[0]["block"] + ".final.jsonl")
    frozen_bytes = final_path.read_bytes()
    final_path.write_bytes(frozen_bytes + b"\n")
    test("edited_final_hash_refused", lambda: run("merge_volumes.py", "--pilot", str(synthetic_pilot), success=False))
    final_path.write_bytes(frozen_bytes)
    finals = load_jsonl(raw / "cisi1-basic-data.jsonl") + load_jsonl(raw / "cisi2-basic-data.jsonl")
    families = []
    web = []
    for i, row in enumerate(finals, 1):
        families.append({"object_family_id": str(i), "metadata": {"cisi": row["cisi"], "type": "SEAL", "site": "Harappa" if row["cisi"].startswith("H-") else "Mohenjo-daro",
                                                                  "excavation-idno": row["col3_excavation"]}})
        if i % 2 == 0:
            web.append({"source_cisi": row["cisi"], "metadata": {"MUSEUM": row["col4_museum"].replace("MD ", "MJD ")}})
    faces_path, web_path, table_path, sets_path = (scratch / name for name in ("faces.jsonl", "website.jsonl", "table.csv", "source-sets.json"))
    write_jsonl(faces_path, families)
    write_jsonl(web_path, web)
    table_path.write_text("cisi,lipi_family_id,disposition,source,catalogue_no\nM-1,1,exact,mackay1938," + str(seed_num + 1) + "\n", encoding="utf-8")
    webset = {str(i) for i in range(1, len(finals) + 1) if i % 2 == 0}
    synthetic_sets = {"objects": len(families), "source_sets": {k: {"count": len(v), "families": sorted(v)} for k, v in
                     {"older_website": webset, "october_6_census": set(), "museum_package": set(), "cisi2_including_brackets": set(),
                      "cisi2_without_brackets_in_cell": set(), "cisi2_any_definite_number": set()}.items()}}
    write_json(sets_path, synthetic_sets, local=True)
    test("crosscheck_cli", lambda: run("crosscheck.py", "--lipi", str(faces_path), "--website", str(web_path), "--table-join", str(table_path)))
    test("join_cli", lambda: run("join_full.py", "--lipi", str(faces_path), "--website", str(web_path), "--table-join", str(table_path), "--source-sets", str(sets_path)))
    test("crosscheck_rebuild_cli_preserves_blind_precedence", lambda: run("crosscheck.py", "--rebuild", "--lipi", str(faces_path), "--website", str(web_path), "--table-join", str(table_path)))
    index = source_index(families, web)
    joined, flags, statuses = join_rows(finals, index)
    cov = coverage_report(finals, index, joined, statuses)
    test("strict_brackets_cannot_increase_coverage", lambda: require(all(cov["modes"]["without_brackets_in_cell"]["joined"]["overall"]["after"][k] <= cov["coverage_after"][k] for k in cov["coverage_after"])))
    multi_faces = families + [{"object_family_id": families[0]["object_family_id"], "metadata": {"cisi": "M-999", "type": "POT", "site": "Harappa"}}]
    test("mixed_base_family_excluded", lambda: require(join_rows(finals, source_index(multi_faces, web))[2]["ambiguous"] >= 1))
    two_families = families + [{"object_family_id": "extra", "metadata": dict(families[0]["metadata"])}]
    test("base_with_two_families_excluded", lambda: require(join_rows(finals, source_index(two_families, web))[2]["ambiguous"] >= 1))
    test("table_base_aliases_excluded", lambda: require(join_rows(finals + [dict(finals[0], cisi=finals[0]["cisi"] + "a")], index)[2]["ambiguous"] >= 2))
    predictor = parse_line(" | ".join(["H-40", fc(), "HR " + number(), "EXB", ""]), volume="cisi2")
    extension = "HR " + number() + fc()[1:]
    pi = source_index([{"object_family_id": "test", "metadata": {"cisi": "H-40", "excavation-idno": extension}}], [])
    pj, _, _ = join_rows([predictor], pi)
    prediction = predictions([predictor], pi, pj, [])
    test("harappa_extension_prediction", lambda: require(prediction["prediction_2_harappa"]["scorable_share"]["share"] == 1 and extension_suffixes(predictor, [extension]) == {fc()[1:]}))
    predictor_missing = parse_line(" | ".join(["H-40", "[??]", "HR " + number(), "EXB", ""]), volume="cisi2")
    test("harappa_unknown_fc_retains_denominator", lambda: require(predictions([predictor_missing], pi, {"test": predictor_missing}, [])["prediction_2_harappa"]["share_bounds_from_unresolved_fc"] == {"lower": 0.0, "upper": 1.0}))
    md = parse_line(" | ".join(entry("M-1000")), volume="cisi2")
    catalogue = {"cisi": "M-1000", "source": "mackay1938", "catalogue_no": str(seed_num), "disposition": "exact", "lipi_family_id": "test"}
    test("fc_arithmetic_and_unique_entry_denominator", lambda: require(fc_check(md, catalogue) == "match" and predictions([md], pi, {}, [catalogue, catalogue])["prediction_1_mohenjo_daro"]["denominator"] == 1))
    contradictory_catalogue = dict(catalogue, catalogue_no=str(seed_num + 1))
    mixed_prediction = predictions([md], pi, {}, [catalogue, contradictory_catalogue])["prediction_1_mohenjo_daro"]
    test("fc_prediction_or_and_conflicting_checks_reported", lambda: require(mixed_prediction["share"] == 1 and mixed_prediction["all_scorable_rows_share"]["share"] == 0 and mixed_prediction["counts"]["entries_with_conflicting_catalogue_checks"] == 1))
    marked = parse_line(" | ".join(["M-40", fc(), "DK " + number() + " (o)", "EXB", ""]), volume="cisi1")
    test("cisi1_marker_removed_for_excavation_comparison", lambda: require(compare_excavation(marked, "DK " + number(), excavation_keys([marked])) == "exact"))
    union = combined_report(joined, index, synthetic_sets)
    test("union_deduplicates_family_ids", lambda: require(all(v["count"] == len(set(v["families"])) for v in union["stages"].values())))
    report_paths = list(out.rglob("*.json")) + list(out.rglob("*.csv"))
    def report_shapes():
        forbidden = {"final", "col2_fc", "col3_excavation", "col4_museum", "col5_photographs", "lipi_excavation", "website_museum"}

        def inspect(value):
            if isinstance(value, dict):
                require(not forbidden & value.keys())
                for key, child in value.items():
                    if key in ("pass1", "pass2"):
                        require(not isinstance(child, str))
                    inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)

        for path in report_paths:
            if path.suffix == ".json":
                inspect(load_json(path))
            else:
                import csv
                with path.open(encoding="utf-8", newline="") as handle:
                    require(not forbidden & set(next(csv.reader(handle))))
    test("tracked_report_shapes_exclude_value_keys", report_shapes)
    repeat_path = pass_file(dict(specs[0], block="piece-repeat"), "pass1", [piece1, piece2, piece2, piece1])
    from cisi_common import read_pass
    repeat = read_pass(repeat_path)
    test("piece_overlap_after_combination_deduplicated", lambda: require(repeat["duplicates_exact"] == 2 and not repeat["variants"] and repeat["piece_lines_combined"] == 1))
    missing_pair = dict(specs[0], block="missing-pair")
    test("missing_pass_pair_reported", lambda: require(compare_block(missing_pair, raw)[0] is None))
    literal = parse_line(" | ".join(["M-41", fc(), "DK {" + number() + "}", "EXB", ""]), volume="cisi1")
    test("printed_curly_brackets_are_not_uncertainty", lambda: require(not literal["uncertain_columns"]))
    definite_wrong = parse_line(" | ".join(entry("M-1001", 1)), volume="cisi2")
    wrong_cat = dict(catalogue, cisi="M-1001")
    test("prediction_exception_is_identifier_only", lambda: require(predictions([definite_wrong], pi, {}, [wrong_cat])["prediction_1_mohenjo_daro"]["exceptions"] == ["M-1001"]))
    _, cross_counts = crosscheck_rows([definite_wrong], pi, [wrong_cat])
    test("fc_mismatch_enters_recheck", lambda: require(cross_counts["by_column"].get("col2") == 1))
    blank_md = parse_line(" | ".join(["M-1001", "", "???", "EXB", ""]), volume="cisi2")
    blank_index = source_index([{"object_family_id": "test", "metadata": {"cisi": "M-1001", "excavation-idno": "DK " + number()}}],
                              [{"source_cisi": "M-1001", "metadata": {"MUSEUM": "MJD " + number()}}])
    blank_todo, _ = crosscheck_rows([blank_md], blank_index, [wrong_cat])
    test("source_numbers_against_blank_cells_enter_recheck", lambda: require({r["column"] for r in blank_todo} == {"col2", "col3", "col4"}))
    bracket_fc = parse_line(" | ".join(["M-1001", "[" + fc(2) + "/" + fc(3) + "]", "???", "EXB", ""]), volume="cisi2")
    bf_todo, _ = crosscheck_rows([bracket_fc], pi, [wrong_cat])
    test("fc_bracket_excluding_rule_enters_recheck", lambda: require(any(r["column"] == "col2" for r in bf_todo)))
    bracket_fc["parsed"]["fc_number"] = "[" + fc() + "/" + fc(3) + "]"
    bf_todo, _ = crosscheck_rows([bracket_fc], pi, [wrong_cat])
    test("fc_bracket_including_rule_preserves_uncertainty", lambda: require(not any(r["column"] == "col2" for r in bf_todo)))

    pilot_result = {}
    pilot_inputs = provenance({"pilot": PILOT, "lipi": LIPI, "website": WEBSITE, "pilot_coverage": HERE.parent / "2026-10-13-cisi2-basic-data-pilot/coverage.json", "source_sets": SOURCE_SETS})

    def pilot_regression():
        nonlocal pilot_result
        rows = load_jsonl(PILOT)
        merged, gaps, _ = merge_rows([], "cisi2", rows)
        require(len(merged) == 327 and not gaps["M"])
        write_jsonl(scratch / "pilot-merged.jsonl", merged)
        idx = source_index(load_jsonl(LIPI), load_jsonl(WEBSITE))
        pj, pf, ps = join_rows(merged, idx)
        coverage = coverage_report(merged, idx, pj, ps)
        frozen = load_json(HERE.parent / "2026-10-13-cisi2-basic-data-pilot/coverage.json")
        for k in ("museum_number", "holding_institution", "fc_number", "excavation"):
            require(coverage["coverage_before"][k] == frozen["coverage_before"][k])
            require(coverage["coverage_after"][k] == frozen["coverage_after"][k])
        require(len(pj) == 283 and coverage["coverage_before"]["museum_number"] == 74 and coverage["coverage_after"]["museum_number"] == 276 and coverage["coverage_after"]["fc_number"] == 283 and coverage["coverage_after"]["excavation"] == 278)
        # Reparse the two final pass files through the extended parser as well.
        parsed = [r for name in ("final-p435.txt", "final-p436.txt") for r in parse_pass(PILOT.parent / name, "cisi2")]
        pj2, _, ps2 = join_rows(parsed, idx)
        coverage2 = coverage_report(parsed, idx, pj2, ps2)
        require(coverage2["coverage_before"] == coverage["coverage_before"] and coverage2["coverage_after"] == coverage["coverage_after"])
        union = combined_report(pj, idx, load_json(SOURCE_SETS))
        dated = load_json(SOURCE_SETS)
        for mode in ("including_brackets", "without_brackets_in_cell", "any_definite_number"):
            require(union["stages"]["combined_" + mode]["count"] == dated["stages"]["combined_" + mode]["count"])
        pilot_result = {"rows": len(merged), "joined_objects": len(pj), "join_status": ps,
                        "coverage_before": coverage["coverage_before"], "coverage_after": coverage["coverage_after"],
                        "extended_parser_reproduces_coverage": True,
                        "combined_museum_counts": {mode: union["stages"]["combined_" + mode]["count"] for mode in ("including_brackets", "without_brackets_in_cell", "any_definite_number")}}

    test("pilot_merge_join_and_reparse_regression", pilot_regression)
    summary = {"date": "2026-10-13", "passed": all(r["passed"] for r in results), "checks": len(results),
               "failed_checks": [r["name"] for r in results if not r["passed"]], "results": results,
               "fixture_directory": scratch.relative_to(ROOT).as_posix(), "pilot": pilot_result,
               "pilot_inputs": pilot_inputs, "scope": "Generated synthetic readings and the pilot's final files only; no active full-run pass files or images read."}
    summary["implementation"] = provenance({name: HERE / name for name in ("cisi_common.py", "cisi_parse.py", "compare_passes.py", "build_finals.py", "merge_volumes.py", "crosscheck.py", "join_full.py", "selftest.py")})
    write_json(HERE / "selftest.json", summary)
    write_json(scratch / "selftest-result.json", summary, local=True)
    print(json.dumps({k: summary[k] for k in ("passed", "checks", "failed_checks", "pilot", "fixture_directory")}, indent=2))
    if not summary["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
