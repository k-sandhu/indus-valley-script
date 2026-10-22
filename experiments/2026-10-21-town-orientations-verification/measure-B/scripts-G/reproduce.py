"""Reproduce measurer B share G town records from picks.

For every town config given, this script
  1. re-measures every lines file from its picks file and the render sidecar
     recorded in it (per-line calls of tools/measure_lines.measure),
  2. compares bearings, deviations, errors and lengths with the stored lines
     file,
  3. rebuilds the town input in memory with the same rules as build_town.py and
     runs tools/systems.town_result on it,
  4. compares systems and main systems with the stored town record,
and checks that every line has a source locator and an error and every plan
source a north class, evidence and an arrow result.  It writes one JSON report.

Usage: python -I reproduce.py <report.json> <town-config.json> <town-record.json> [...pairs]
"""
import json
import math
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import measure_lines  # noqa: E402
import systems  # noqa: E402
from common import read_json, write_json, utc  # noqa: E402

KEYS = ["bearing_deg", "theta_deg", "sigma_deg", "length_m"]


def remeasure(lines_path):
    stored = read_json(lines_path)
    picks_path = lines_path.replace("-lines.json", "-picks.json")
    picks = read_json(picks_path)
    sidecar = stored.get("render_sidecar")
    rows, fails = [], []
    for line in picks["lines"]:
        one = dict(picks)
        one["lines"] = [line]
        try:
            rows.extend(measure_lines.measure(one, sidecar)["lines"])
        except ValueError as e:
            fails.append(line["id"])
    old = {r["id"]: r for r in stored["lines"]}
    new = {r["id"]: r for r in rows}
    maxdiff = 0.0
    mismatched = []
    for i, r in old.items():
        if i not in new:
            mismatched.append(i)
            continue
        for k in KEYS:
            d = abs(float(r[k]) - float(new[i][k]))
            maxdiff = max(maxdiff, d)
            if d > 1e-9:
                mismatched.append(f"{i}:{k}")
    return dict(lines_file=lines_path, picks_file=picks_path, sidecar=sidecar, stored_lines=len(old),
                remeasured_lines=len(new), failed_in_rerun=fails, max_abs_difference=maxdiff,
                mismatches=mismatched), new


def rebuild(cfg, remeasured):
    lines = []
    for lf in cfg.get("line_files", []):
        excl = set(lf.get("exclude", []))
        for i, r in remeasured[lf["path"]].items():
            if i in excl:
                continue
            row = dict(r)
            row["source_id"] = lf["source_id"]
            if i in lf.get("systems", {}):
                row["system"] = lf["systems"][i]
            row["source_locator"] = lf["locator"]
            lines.append(row)
    town = dict(slug=cfg["slug"], lines=lines, unmeasurable_reason=cfg.get("unmeasurable_reason"))
    return systems.town_result(town)


def main():
    out = sys.argv[1]
    pairs = sys.argv[2:]
    report = dict(schema_version=1, created_utc=utc(), towns=[])
    for cfg_path, rec_path in zip(pairs[::2], pairs[1::2]):
        cfg = read_json(cfg_path)
        rec = read_json(rec_path)
        entry = dict(config=cfg_path, record=rec_path, slug=cfg["slug"], line_files=[])
        remeasured = {}
        for lf in cfg.get("line_files", []):
            res, new = remeasure(lf["path"])
            entry["line_files"].append(res)
            remeasured[lf["path"]] = new
        rebuilt = rebuild(cfg, remeasured)
        old_sys = {(s["source_id"], s["id"]): s for s in rec["systems"]}
        new_sys = {(s["source_id"], s["id"]): s for s in rebuilt["systems"]}
        sysdiff = []
        for k, s in old_sys.items():
            t = new_sys.get(k)
            if t is None:
                sysdiff.append(f"missing {k}")
                continue
            for f in ["n", "total_length_m", "theta_deg", "se_deg", "conditions_pass"]:
                a, b = s[f], t[f]
                if isinstance(a, float) and not math.isclose(a, b, rel_tol=0, abs_tol=1e-9):
                    sysdiff.append(f"{k} {f} {a} {b}")
                elif not isinstance(a, float) and a != b:
                    sysdiff.append(f"{k} {f} {a} {b}")
        entry["systems_reproduced"] = not sysdiff and set(old_sys) == set(new_sys)
        entry["system_differences"] = sysdiff
        entry["main_reproduced"] = rec["main_system_by_source"] == rebuilt["main_system_by_source"]
        # completeness checks on the stored record
        missing = []
        for r in rec["lines"]:
            if not r.get("source_locator"):
                missing.append(f"{r['id']}: no locator")
            if r.get("sigma_deg") is None or not (r["sigma_deg"] > 0):
                missing.append(f"{r['id']}: no error")
        for s in rec["sources"]:
            if s["kind"] == "plan":
                if s.get("north_class") not in ["true", "magnetic", "grid", "unspecified"]:
                    missing.append(f"{s['id']}: north class")
                if not s.get("north_evidence"):
                    missing.append(f"{s['id']}: north evidence")
                if not s.get("arrow_result"):
                    missing.append(f"{s['id']}: arrow result")
                if "survey_year" not in s:
                    missing.append(f"{s['id']}: survey year field")
        if not rec["lines"] and not rec.get("unmeasurable_reason"):
            missing.append("no lines and no unmeasurable reason")
        entry["completeness_problems"] = missing
        report["towns"].append(entry)
        print(cfg["slug"], "lines ok" if all(not l["mismatches"] and not l["failed_in_rerun"] for l in entry["line_files"]) else "LINE MISMATCH",
              "systems ok" if entry["systems_reproduced"] and entry["main_reproduced"] else "SYSTEM MISMATCH",
              "complete" if not missing else missing)
    write_json(out, report)


if __name__ == "__main__":
    main()
