"""Reproducibility and completeness check for share H; writes nothing.

For each town record it (1) reruns tools/measure_lines.measure on every picks
file named in the record against the render sidecar stored in the lines file
and compares bearings, theta and sigma line by line; (2) reruns
tools/systems.town_result on the town input and compares every system value
and the main system per source with the record; (3) checks that every line has
a source locator and a positive error, and every plan source a north class,
north evidence and a survey-year field.
Usage: verify.py <towns-dir> <town-inputs-dir> slug [slug ...]
"""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS))
import json
import warnings
warnings.filterwarnings("ignore")
from common import read_json
from measure_lines import measure
from systems import town_result


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main():
    towns, inputs = Path(sys.argv[1]), Path(sys.argv[2])
    ok_all = True
    for slug in sys.argv[3:]:
        rec = read_json(towns / f"{slug}.json")
        inp = read_json(inputs / f"{slug}-input-v1.json")
        problems = []
        # (1) lines reproduce from picks
        files = {}
        for line in rec["lines"]:
            files.setdefault((line["picks_file"], line["lines_file"]), []).append(line)
        for (pk, lf), lines in files.items():
            old = read_json(lf)
            new = measure(read_json(pk), old["render_sidecar"])
            byid = {l["id"]: l for l in new["lines"]}
            for line in lines:
                n = byid.get(line["id"])
                if n is None:
                    problems.append(f"{line['id']}: missing on rerun")
                    continue
                for k in ("bearing_deg", "theta_deg", "sigma_deg", "length_m"):
                    if not close(n[k], line[k]):
                        problems.append(f"{line['id']}: {k} {line[k]} -> {n[k]}")
        # (2) systems reproduce from input
        res = town_result(inp)
        if res["main_system_by_source"] != rec["main_system_by_source"]:
            problems.append("main systems differ")
        key = lambda s: (s["source_id"], s["id"])
        recs = {key(s): s for s in rec["systems"]}
        for s in res["systems"]:
            r = recs.get(key(s))
            if r is None:
                problems.append(f"system {key(s)} missing")
                continue
            for k in ("n", "total_length_m", "theta_deg", "se_deg", "conditions_pass"):
                if (isinstance(s[k], float) and not close(s[k], r[k])) or (not isinstance(s[k], float) and s[k] != r[k]):
                    problems.append(f"system {key(s)} {k} {r[k]} -> {s[k]}")
        # (3) completeness
        for line in rec["lines"]:
            if not line.get("source_locator"):
                problems.append(f"{line['id']}: no source locator")
            if not (line.get("sigma_deg", 0) > 0):
                problems.append(f"{line['id']}: no positive sigma")
        used = {l["source_id"] for l in rec["lines"]}
        for src in rec["sources"]:
            if src.get("kind") == "plan" and src["id"] in used:
                for k in ("north_class", "north_evidence", "survey_year"):
                    if k not in src:
                        problems.append(f"source {src['id']}: no {k}")
                if src.get("north_class") not in ("true", "magnetic", "grid", "unspecified"):
                    problems.append(f"source {src['id']}: bad north class")
        if not rec["lines"] and not rec.get("unmeasurable_reason"):
            problems.append("no lines and no unmeasurable reason")
        status = "OK" if not problems else "PROBLEMS"
        ok_all &= not problems
        print(f"{slug}: {status} ({len(rec['lines'])} lines, {len(rec['systems'])} systems)")
        for p in problems:
            print("   ", p)
    print("ALL OK" if ok_all else "SOME PROBLEMS")


if __name__ == "__main__":
    main()
