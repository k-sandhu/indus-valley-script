"""Summarize the transcription check and the join check.

    python -P experiments/2026-10-13-mackay-marshall-tables/summarize_verification.py

Reads verification/transcription-check.csv, verification/join-verification.csv and the
run's join table; writes verification/summary.json. Intervals are Wilson 95% intervals.
"""
import collections
import csv
import json
import math
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "run-2026-10-13"


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [max(0.0, round(100 * (c - a) / d, 1)), min(100.0, round(100 * (c + a) / d, 1))]


def main():
    # the join sample is reproducible from the run's join table
    joins = list(csv.DictReader((RUN / "join-table.csv").open(encoding="utf-8")))
    ex = [j for j in joins if j["disposition"] == "exact"]
    co = [j for j in joins if j["disposition"] == "confirmed"]
    rng = random.Random(20261014)
    drawn = [j["source_row_id"] for j in rng.sample(ex, 20) + rng.sample(co, 10)]

    jv = list(csv.DictReader((HERE / "verification/join-verification.csv").open(encoding="utf-8")))
    assert [r["source_row_id"] for r in jv] == drawn, "verification rows differ from the seeded draw"
    out = {"join_check": {"seed": 20261014, "population": {"exact": len(ex), "confirmed": len(co)}}}
    for s in ("exact", "confirmed"):
        rows = [r for r in jv if r["stratum"] == s]
        c = collections.Counter(r["verdict"] for r in rows)
        out["join_check"][s] = {
            "checked": len(rows), **dict(c),
            "precision_pct": round(100 * c["correct"] / len(rows), 1),
            "wilson95_pct": wilson(c["correct"], len(rows)),
            "cisi_basic_data_checked": sum(1 for r in rows if not r["cisi_basic_data"].startswith("not held")),
        }
    c = collections.Counter(r["verdict"] for r in jv)
    out["join_check"]["all"] = {"checked": len(jv), **dict(c), "precision_pct": round(100 * c["correct"] / len(jv), 1),
                                "wilson95_pct": wilson(c["correct"], len(jv)), "wrong": c.get("wrong", 0)}
    pe = out["join_check"]["exact"]["correct"] / out["join_check"]["exact"]["checked"]
    pc = out["join_check"]["confirmed"]["correct"] / out["join_check"]["confirmed"]["checked"]
    out["join_check"]["population_weighted_precision_pct"] = round(100 * (len(ex) * pe + len(co) * pc) / (len(ex) + len(co)), 1)
    out["join_check"]["unresolved_counted_as"] = "not correct"
    out["join_check"]["transcription_errors_seen_in_join_sample"] = dict(collections.Counter(r["transcription_error_found"] for r in jv if r["transcription_error_found"]))

    tc = list(csv.DictReader((HERE / "verification/transcription-check.csv").open(encoding="utf-8")))
    out["transcription_check"] = {"seed": 20261013}
    for t in ("mackay", "marshall"):
        rows = [r for r in tc if r["table"] == t]
        err = [r for r in rows if r["verdict"] == "error"]
        out["transcription_check"][t] = {
            "rows_checked": len(rows), "rows_with_error": len(err),
            "row_error_rate_pct": round(100 * len(err) / len(rows), 1),
            "wilson95_pct": wilson(len(err), len(rows)),
            "errors_by_field": dict(collections.Counter(r["field_in_error"] for r in err)),
        }
    allrows = len(tc)
    allerr = sum(1 for r in tc if r["verdict"] == "error")
    out["transcription_check"]["both"] = {"rows_checked": allrows, "rows_with_error": allerr,
                                          "row_error_rate_pct": round(100 * allerr / allrows, 1),
                                          "wilson95_pct": wilson(allerr, allrows)}
    (HERE / "verification/summary.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
