"""Join merged volumes to Lipi families; report coverage, source unions and predictions.

Command from repository root:
  python experiments/2026-10-13-cisi-basic-data-full/join_full.py [--allow-partial]
Reads both merged tables (CISI 2 already contains the pilot). Writes tracked
coverage.json, object-flags.csv, combined-coverage.json and predictions.json.
"""
from __future__ import annotations

import collections
import csv
import re
from itertools import combinations

from cisi_common import (INV, LIPI, SOURCE_SETS, TABLE_JOIN, WEBSITE, arguments, base_key,
                         family_sort, join_status, load_json, load_jsonl, load_merged, main_guard,
                         provenance, sort_key, source_index, table_rows, uncertain, verify_inputs, write_json)
from crosscheck import (excavation_printed, fc_check, joined_catalogues, squash, strip_area)

FIELDS = ["museum_number", "holding_institution", "fc_number", "excavation"]
MODES = ["including_brackets", "without_brackets_in_cell"]
FIELD_COL = {"museum_number": "col4_museum", "holding_institution": "col4_museum",
             "fc_number": "col2_fc", "excavation": "col3_excavation"}


def supplies(row, strict=False):
    p = row["parsed"]
    result = {"museum_number": bool(p["museum_number_usable"]), "holding_institution": bool(p["institution_usable"]),
              "fc_number": bool(p["fc_number"]), "excavation": bool(p["excavation_usable"])}
    return {k: bool(v and (not strict or not uncertain(row[FIELD_COL[k]]))) for k, v in result.items()}


def museum_numbers(text):
    """Use the dated verifier's token rule for the museum source-set union."""
    return re.findall(r"(?<![A-Za-z0-9])(?:[A-Z]+-)?(?:\[[^\]]+\]|\d)[\d.\[\]/?]*(?:\s*\[[A-Z/]+\]|[A-Za-z]+)?", text)


def baseline(family, index, strict=False):
    fs = index["families"][family]
    values = {v for f in fs for v in index["museum"].get(INV.norm(f["metadata"].get("cisi")), ())}
    museum = any(not strict or not uncertain(v) for v in values)
    excavation = any(INV.usable("excavation-idno", f["metadata"].get("excavation-idno")) and
                     (not strict or not uncertain(INV.norm(f["metadata"].get("excavation-idno")))) for f in fs)
    return {"museum_number": museum, "holding_institution": museum, "fc_number": False, "excavation": excavation}


def family_groups(index):
    types, sites = {}, {}
    for fam, fs in index["families"].items():
        tg = {INV.type_group(f["metadata"].get("type")) for f in fs}
        sg = {INV.norm(f["metadata"].get("site")) for f in fs}
        types[fam] = next(iter(tg)) if len(tg) == 1 else "mixed"
        sites[fam] = INV.site_group(next(iter(sg)) if len(sg) == 1 else "mixed")
    return types, sites


def coverage_group(families, before, supplied):
    n = len(families)
    b = {k: sum(before[f][k] for f in families) for k in FIELDS}
    c = {k: sum(supplied.get(f, {}).get(k, False) for f in families) for k in FIELDS}
    a = {k: sum(before[f][k] or supplied.get(f, {}).get(k, False) for f in families) for k in FIELDS}
    return {"objects": n, "before": b, "after": a, "gain": {k: a[k] - b[k] for k in FIELDS}, "cisi_supplies": c,
            "before_percent": {k: round(100 * b[k] / n, 3) if n else None for k in FIELDS},
            "after_percent": {k: round(100 * a[k] / n, 3) if n else None for k in FIELDS}}


def grouped(families, before, supplied, types, sites):
    return {"overall": coverage_group(families, before, supplied),
            "by_type": {t: coverage_group({f for f in families if types[f] == t}, before, supplied) for t in sorted({types[f] for f in families})},
            "by_site": {s: coverage_group({f for f in families if sites[f] == s}, before, supplied) for s in sorted({sites[f] for f in families})}}


def join_rows(rows, index):
    preliminary = [(r, *join_status(r, index)) for r in rows]
    family_rows = collections.Counter(fams[0] for _, status, fams in preliminary if status == "one-family")
    flags, joined, statuses = [], {}, collections.Counter()
    for row, status, fams in preliminary:
        if status == "one-family" and family_rows[fams[0]] > 1:
            status = "ambiguous"
        statuses[status] += 1
        flag = {"cisi": row["cisi"], "volume": row.get("volume", "cisi2"), "lipi_family": ";".join(fams), "join": status,
                "uncertain_columns": ";".join(row["uncertain_columns"]),
                **{"supplies_" + k: int(v) for k, v in supplies(row).items()},
                **{"supplies_unbracketed_" + k: int(v) for k, v in supplies(row, True).items()}}
        if status == "one-family":
            family = fams[0]
            joined[family] = row
            flag["lipi_faces"] = len(index["families"][family])
            flag.update({"before_" + k: int(v) for k, v in baseline(family, index).items()})
            flag.update({"before_unbracketed_" + k: int(v) for k, v in baseline(family, index, True).items()})
        flags.append(flag)
    return joined, flags, dict(statuses)


def coverage_report(rows, index, joined, statuses):
    all_fams, types_sites = set(index["families"]), family_groups(index)
    types, sites = types_sites
    modes = {}
    for mode in MODES:
        strict = mode == MODES[1]
        before = {f: baseline(f, index, strict) for f in all_fams}
        supplied = {f: supplies(r, strict) for f, r in joined.items()}
        modes[mode] = {
            "corpus": grouped(all_fams, before, supplied, types, sites),
            "joined": grouped(set(joined), before, supplied, types, sites),
            "by_volume": {v: grouped({f for f, r in joined.items() if r.get("volume", "cisi2") == v}, before, supplied, types, sites)
                          for v in ("cisi1", "cisi2")},
        }
    overall = modes[MODES[0]]["joined"]["overall"]
    return {"rows": len(rows), "joined_objects": len(joined), "join_status": statuses,
            "coverage_before": overall["before"], "coverage_after": overall["after"], "coverage_gain": overall["gain"],
            "modes": modes,
            "rules": {
                "join": "CISI prefix and integer base number; one Lipi family per number and one table row per family. Multiple face bases or multiple table rows for a family are ambiguous and excluded.",
                "population": "Corpus counts include all Lipi families. Joined and volume counts include unique joined families. Families with no table row remain in corpus denominators and their baseline fields remain covered.",
                "before": "Inventory usable Lipi excavation-idno and older-export MUSEUM on an identical raw CISI key; museum and institution follow the pilot baseline. FC absent in baseline.",
                "after": "Baseline or parser-supplied field. Unknown institution codes are retained without an invented expansion; parser review is required.",
                "brackets": "including_brackets counts usable uncertain cells; without_brackets_in_cell excludes any supplied cell containing a square bracket. Each mode filters baseline cells in the same way.",
                "groups": "Inventory type_group and site_group; mixed face types form a mixed group, mixed face sites fall in other sites, as in the inventory.",
            }}


def set_record(value, denominator):
    return {"count": len(value), "percent": round(100 * len(value) / denominator, 3) if denominator else None,
            "families": sorted(value, key=family_sort)}


def combined_report(joined, index, source_sets):
    den = len(index["families"])
    existing = {k: {str(f) for f in v["families"]} for k, v in source_sets["source_sets"].items()}
    if source_sets.get("objects") != den:
        raise ValueError("source-set universe differs from Lipi family universe")
    for key, value in existing.items():
        if not value <= index["families"].keys() or source_sets["source_sets"][key]["count"] != len(value):
            raise ValueError("invalid museum source set: " + key)
    base = existing["older_website"] | existing["october_6_census"] | existing["museum_package"]
    new_sets = {}
    for volume in ("cisi1", "cisi2", "both_volumes"):
        members = {f: r for f, r in joined.items() if volume == "both_volumes" or r.get("volume", "cisi2") == volume}
        all_numbers = {f for f, r in members.items() if museum_numbers(r["col4_museum"])}
        definite_cells = {f for f in all_numbers if not uncertain(members[f]["col4_museum"])}
        definite_numbers = {f for f in all_numbers if any(not uncertain(n) for n in museum_numbers(members[f]["col4_museum"]))}
        for label, value in (("including_brackets", all_numbers), ("without_brackets_in_cell", definite_cells), ("any_definite_number", definite_numbers)):
            new_sets[volume + "_" + label] = value
    stages = {"website_census_and_museum": base}
    for mode in ("including_brackets", "without_brackets_in_cell", "any_definite_number"):
        # Retain the dated pilot sets even if this invocation uses a subset of tables.
        pilot = existing["cisi2_" + mode]
        full = new_sets["both_volumes_" + mode]
        stages["combined_" + mode] = base | pilot | full
        stages["new_after_dated_packages_" + mode] = full - base - pilot
    sets = {**{"dated_" + k: v for k, v in existing.items()}, **new_sets}
    return {"objects": den, "source_sets": {k: set_record(v, den) for k, v in sets.items()},
            "stages": {k: set_record(v, den) for k, v in stages.items()},
            "pairwise_overlaps": {a + " & " + b: len(sets[a] & sets[b]) for a, b in combinations(sets, 2)},
            "rules": {"number": "Dated verifier museum_numbers token rule, separately for any token, wholly unbracketed cell and any unbracketed token.",
                      "union": "Older website, census and museum package sets from combined-coverage-post-fix.json, plus its pilot set and new unique family joins. Families are counted once."}}


def extension_suffixes(row, lipi_values):
    """Return suffixes from strict extensions of a printed numeric identifier."""
    printed = [strip_area(squash(p)) for p in excavation_printed(row) if not uncertain(p)]
    printed = [p for p in printed if p.isdigit()]
    suffixes = set()
    for lv in lipi_values:
        normalized = strip_area(squash(lv))
        if not normalized.isdigit() or uncertain(lv):
            continue
        matches = [p for p in printed if normalized.startswith(p) and len(normalized) > len(p)]
        if matches:
            longest = max(matches, key=len)
            suffixes.add(normalized[len(longest):])
    return suffixes


def share(count, denominator):
    return {"numerator": count, "denominator": denominator, "share": count / denominator if denominator else None,
            "percent": round(100 * count / denominator, 3) if denominator else None}


def predictions(rows, index, joined, table):
    catalogues = joined_catalogues(table)
    counts1, exceptions, eligible = collections.Counter(), [], []
    for row in rows:
        key = base_key(row["cisi"])
        if not key.startswith("M-") or 621 <= int(key.split("-")[1]) <= 947:
            continue
        counts1["outside_pilot_mohenjo_daro_entries"] += 1
        cats = catalogues.get(key, [])
        if not cats:
            counts1["no_catalogue_join"] += 1
            continue
        counts1["entries_with_catalogue_join"] += 1
        outcomes = [fc_check(row, c) for c in cats]
        scorable = [o for o in outcomes if o in ("match", "differ")]
        if not scorable:
            counts1["unscorable_entries"] += 1
            for o in set(outcomes) - {"match", "differ"}:
                counts1[o] += 1
            continue
        eligible.append(row["cisi"])
        counts1["eligible_entries"] += 1
        counts1["eligible_catalogue_rows"] += len(scorable)
        counts1["excluded_catalogue_rows_on_eligible_entries"] += len(outcomes) - len(scorable)
        counts1["matching_catalogue_rows"] += scorable.count("match")
        counts1["entries_with_all_scorable_rows_matching"] += all(o == "match" for o in scorable)
        counts1["entries_with_conflicting_catalogue_checks"] += "match" in scorable and "differ" in scorable
        if "match" in scorable:
            counts1["matching_entries"] += 1
        else:
            exceptions.append(row["cisi"])
    n, den = counts1["matching_entries"], counts1["eligible_entries"]
    p1 = {"counts": dict(counts1), **share(n, den), "exceptions": sorted(exceptions, key=sort_key),
          "threshold_met": n / den >= .95 if den else None, "kill_condition_met": n / den < .9 if den else None,
          "exception_explanation": "Coordinator must review the page and record crossed-record or correction evidence for each exception; these causes are not inferred from a mismatch.",
          "all_scorable_rows_share": share(counts1["entries_with_all_scorable_rows_matching"], den),
          "unit": "Unique CISI entry outside M-621 to M-947; exact or confirmed Mackay/Marshall joins; four numeric unbracketed FC digits and at least one numeric catalogue number. An entry satisfies the stated OR rule if at least one joined row satisfies its arithmetic rule. Conflicting checks and the stricter all-rows share are reported separately."}
    counts2, failures, unresolved = collections.Counter(), [], []
    for fam, row in joined.items():
        if not row["cisi"].startswith("H-"):
            continue
        counts2["joined_harappa_entries"] += 1
        if uncertain(row["col3_excavation"]):
            counts2["bracketed_printed_excavation_excluded"] += 1
            continue
        fs = index["families"][fam]
        lipi = {INV.norm(f["metadata"].get("excavation-idno")) for f in fs if INV.usable("excavation-idno", f["metadata"].get("excavation-idno"))}
        suffixes = extension_suffixes(row, lipi)
        if not suffixes:
            counts2["no_definite_numeric_extension"] += 1
            continue
        counts2["extension_entries"] += 1
        fc = row["parsed"].get("fc_number")
        if uncertain(fc) or not re.fullmatch(r"\d{4}", fc or ""):
            counts2["unresolved_fc"] += 1
            unresolved.append(row["cisi"])
            continue
        counts2["scorable_extension_entries"] += 1
        expected = fc[1:]
        # Leading zeros in the tail are optional, matching the pilot's suffix rule.
        ok = all(int(s) == int(expected) for s in suffixes)
        counts2["matching_entries"] += ok
        counts2["multiple_distinct_extensions"] += len(suffixes) > 1
        if not ok:
            failures.append(row["cisi"])
    n, den, unknown = counts2["matching_entries"], counts2["extension_entries"], counts2["unresolved_fc"]
    lower, upper = (n / den, (n + unknown) / den) if den else (None, None)
    p2 = {"counts": dict(counts2), "observed_matches_over_all_extensions": share(n, den),
          "scorable_share": share(n, counts2["scorable_extension_entries"]),
          "share_bounds_from_unresolved_fc": {"lower": lower, "upper": upper},
          "threshold_met": (True if lower >= .8 else False if upper < .8 else None) if den else None,
          "kill_condition_met": (True if upper < .5 else False if lower >= .5 else None) if den else None,
          "exceptions": sorted(failures, key=sort_key), "unresolved": sorted(unresolved, key=sort_key),
          "normalization": "Remove whitespace, hyphens, slashes, dots and commas, uppercase, remove leading area letters, and remove printed (o)/(t) markers. Require the remaining identifiers to be digits. A strict extension starts with a printed numeric identifier and has one or more appended digits. With multiple printed numbers use the longest prefix. All distinct extensions across family faces must match. Compare appended digits to the FC digits after removing the first digit, as integers to allow leading-zero padding. Bracketed excavation cells cannot define an extension; uncertain or missing FC leaves that extension unresolved in the full denominator."}
    return {"prediction_1_mohenjo_daro": p1, "prediction_2_harappa": p2,
            "stage": "Final merged table after permitted rechecks; the blind error rates remain separate."}


def write_flags(path, flags):
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = ["cisi", "volume", "lipi_family", "join"] + sorted({k for f in flags for k in f} - {"cisi", "volume", "lipi_family", "join"})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols)
        writer.writeheader()
        writer.writerows(flags)


def main():
    ap = arguments(__doc__.splitlines()[0])
    for name, default in (("lipi", LIPI), ("website", WEBSITE), ("table-join", TABLE_JOIN), ("source-sets", SOURCE_SETS)):
        ap.add_argument("--" + name, type=type(default), default=default)
    args = ap.parse_args()
    inputs = provenance({"lipi": args.lipi, "website": args.website, "table_join": args.table_join, "source_sets": args.source_sets,
                         **{v: args.raw / f"{v}-basic-data.jsonl" for v in ("cisi1", "cisi2")}})
    rows = load_merged(args.raw, require_both=not args.allow_partial)
    index = source_index(load_jsonl(args.lipi), load_jsonl(args.website))
    joined, flags, statuses = join_rows(rows, index)
    coverage = coverage_report(rows, index, joined, statuses)
    coverage["inputs"] = inputs
    coverage["lipi_faces_hash_matches_inventory"] = inputs["lipi"]["sha256"] == INV.EXPECTED_SHA256["lipi_faces"]
    union = combined_report(joined, index, load_json(args.source_sets))
    prediction = predictions(rows, index, joined, table_rows(args.table_join))
    union["inputs"] = prediction["inputs"] = inputs
    verify_inputs(inputs)
    write_json(args.out / "coverage.json", coverage)
    write_flags(args.out / "object-flags.csv", flags)
    write_json(args.out / "combined-coverage.json", union)
    write_json(args.out / "predictions.json", prediction)
    print(f"Joined {len(joined)} of {len(rows)} entries; museum numbers {coverage['coverage_before']['museum_number']} to {coverage['coverage_after']['museum_number']}.")


if __name__ == "__main__":
    main_guard(main)
