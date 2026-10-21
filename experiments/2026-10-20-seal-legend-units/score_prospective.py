"""Score the frozen prospective predictions on a fresh pool of seal legends (PREDICTIONS.md).

Usage:
  python -P experiments/2026-10-20-seal-legend-units/score_prospective.py --pool cisi31 \
      --input data/raw/<date>-<package>/fresh-faces.jsonl --out experiments/<date>-<package>/prospective-cisi31.json

Input rows need record_id, object_type and direction, and the legend in one of two forms:
  lines_reading: a list of lines, each a list of Wells sign numbers in reading order, the lines in
                 the order the transcriber reads them (preferred for new transcriptions); or
  text_code_visual_ltr: the Lipi visual code, whose segments are read last to first (Q-0027).
Unreadable signs are written 000 and damaged edges [ or ]. The scorer refuses to run unless every
frozen hash matches, and it appends each read to prospective-access.jsonl before scoring.
"""
import argparse
import datetime
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402
from calibrate import Known, mcnemar_one_sided  # noqa: E402

POOLS = {"cisi31": "absent CISI 3.1 seal numbers", "post_catalogue": "post-catalogue finds (Q-1026)"}


def check_hashes():
    listed = {}
    for line in (U.PKG / "PREDICTIONS.sha256").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            h, name = line.split(None, 1)
            listed[name.strip()] = h
    for name, h in listed.items():
        path = U.ROOT / name if name.startswith("data/") else U.PKG / name
        if U.sha256(path) != h:
            raise SystemExit(f"Frozen file changed: {name}")
    return listed


def legend_lines(face):
    """Lines in reading order, or (None, reason)."""
    if not face["object_type"].startswith("SEAL"):
        return None, "not_a_seal"
    if face.get("direction") == "BUS":
        return None, "boustrophedon"
    if "lines_reading" in face:
        lines = [tuple(str(s).zfill(3) for s in line) for line in face["lines_reading"] if line]
        if not lines or any(s in ("000", "999") for line in lines for s in line):
            return None, "unknown_or_damaged_sign"
        return lines, None
    code = face["text_code_visual_ltr"]
    if "/" in code:
        lines, why = U.lines_of(face)
        if lines is None:
            return None, why
        return lines[::-1], None
    signs = [s for s in code.strip("+").replace("+", "-").split("-") if s]
    if any(ch in code for ch in "[]") or "000" in signs or "999" in signs:
        return None, "unknown_or_damaged_sign"
    if face["direction"] != "L/R":
        signs = signs[::-1]
    return [tuple(signs)], None


def binom_tail(k, n, p):
    return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True, choices=sorted(POOLS))
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit("Output exists; write each scoring run to a new path")
    listed = check_hashes()
    spec = U.json.loads((U.PKG / "predictions.json").read_text(encoding="utf-8"))
    rows = U.read_jsonl(args.input)
    event = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "pool": args.pool,
             "input": str(args.input), "input_sha256": U.sha256(args.input), "faces": len(rows),
             "predictions_sha256": listed.get("PREDICTIONS.md")}
    with open(U.PKG / "prospective-access.jsonl", "a", encoding="utf-8") as f:
        f.write(U.json.dumps(event) + "\n")

    raw = U.RAW / f"frozen-{spec['frozen_version']}"
    inv = {tuple(r["unit"]) for r in U.json.loads((raw / "inventory.json").read_text(encoding="utf-8"))["units"]}
    stock = {tuple(r["unit"]) for r in U.json.loads((raw / "closing-stock.json").read_text(encoding="utf-8"))["units"]}
    build = [tuple(s["text"]) for s in U.read_jsonl(raw / "build-segmentation.jsonl")]
    known = Known(build)
    known_set = set(build)
    th = spec["thresholds"]

    single, divided, excluded, seen = [], [], {}, set()
    for face in rows:
        lines, why = legend_lines(face)
        if lines is None:
            excluded[why] = excluded.get(why, 0) + 1
            continue
        text = tuple(s for line in lines for s in line)
        if text in seen:
            excluded["duplicate_within_pool"] = excluded.get("duplicate_within_pool", 0) + 1
            continue
        seen.add(text)
        if len(lines) == 1:
            if len(text) < 3:
                excluded["fewer_than_3_signs"] = excluded.get("fewer_than_3_signs", 0) + 1
                continue
            st = known.legend_stats(text, inv, stock)
            st.update({"record_id": face["record_id"], "identical_to_known": text in known_set})
            single.append(st)
        elif len(lines) == 2:
            a, b = lines
            main_line = a if len(a) >= len(b) else b
            if len(main_line) < 2:
                excluded["divided_main_line_under_2"] = excluded.get("divided_main_line_under_2", 0) + 1
                continue
            cut = len(a)
            vals = []
            for i in range(1, len(text)):
                if i == cut:
                    continue
                x, y = text[:i], text[i:]
                m = x if len(x) >= len(y) else y
                vals.append(len(m) >= 2 and U.closing_formula(m, stock) is not None)
            divided.append({"record_id": face["record_id"],
                            "main_line_stock_closing": U.closing_formula(main_line, stock) is not None,
                            "chance": sum(vals) / len(vals) if vals else 0.0})
        else:
            excluded["three_or_more_lines"] = excluded.get("three_or_more_lines", 0) + 1
    n = len(single)
    out = {"pool": args.pool, "description": POOLS[args.pool], "access": event, "single_line_legends": n,
           "divided_legends": len(divided), "excluded": excluded,
           "identical_to_known": sum(r["identical_to_known"] for r in single), "predictions": {}}

    def bound(pid, key, size):
        return spec["bounds"][pid][key][str(min(max(size, 1), 400))]

    if n:
        cov = sum(r["closing"] for r in single) / n
        lo, kill = bound("P1", "lower", n), bound("P1", "kill", n)
        out["predictions"]["P1"] = {"statistic": cov, "n": n, "lower_bound": lo, "kill_bound": kill,
                                    "pass": cov >= lo - 1e-12, "kill": n >= 20 and cov <= kill + 1e-12}
        b = sum(r["end_pair_known"] and not r["start_pair_known"] for r in single)
        c = sum(r["start_pair_known"] and not r["end_pair_known"] for r in single)
        p = mcnemar_one_sided(b, c)
        out["predictions"]["P2"] = {"statistic": (b - c) / n, "discordant_end": b, "discordant_start": c,
                                    "mcnemar_one_sided_p": p, "pass": b > c and p < th["P2_alpha"],
                                    "wrong_direction": b <= c}
        op = [r["opening_known"] for r in single if r["closing"] and r["opening_len"] and r["opening_len"] >= 2]
        if op:
            share, hi = sum(op) / len(op), bound("P3", "upper", len(op))
            out["predictions"]["P3"] = {"statistic": share, "n": len(op), "upper_bound": hi, "pass": share <= hi + 1e-12}
    k = len(divided)
    if k >= th["P4_min_faces"]:
        hits = sum(r["main_line_stock_closing"] for r in divided)
        p0 = sum(r["chance"] for r in divided) / k
        p = binom_tail(hits, k, p0)
        out["predictions"]["P4"] = {"statistic": hits / k, "faces": k, "chance": p0, "binomial_p": p,
                                    "pass": hits / k >= th["P4_share"] and p < th["P4_alpha"]}
    else:
        out["predictions"]["P4"] = {"faces": k, "scorable": False}
    U.write_json(args.out, out)
    print(U.json.dumps(out["predictions"], indent=1))


if __name__ == "__main__":
    main()
