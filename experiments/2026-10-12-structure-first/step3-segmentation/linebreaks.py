"""Step 3a: do line breaks fall at unit boundaries?

Usage: python -X utf8 linebreaks.py --out <run_dir>

For every face with marked line breaks ('/' in the visual code) and no unknown
or damaged signs, each line is read right to left (left to right for L/R faces).
A line is "found" if it occurs as a contiguous substring of a clean single-line
text from a different object family. Control windows of the same length straddle
the break under either line order. PROTOCOL step 3, line-break evidence.
"""
import argparse
import collections
import json
import sys
from math import comb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common  # noqa: E402


def lines_of(face):
    code = face["text_code_visual_ltr"].strip("+")
    if any(ch in code for ch in "[]") or "000" in code:
        return None
    raw = [seg for seg in code.split("/")]
    lines = []
    for seg in raw:
        signs = [s for s in seg.replace("+", "-").split("-") if s]
        if not signs:
            return None
        if face["direction"] != "L/R":
            signs = signs[::-1]
        lines.append(tuple(signs))
    return lines if len(lines) >= 2 else None


def contains(ref_by_len, window, fam):
    for t, fams in ref_by_len:
        if fam in fams and len(fams) == 1:
            continue
        n = len(window)
        for i in range(len(t) - n + 1):
            if t[i:i + n] == window:
                return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    clean = common.load_clean()
    ref = [(d["text"], d["families"]) for d in clean]
    faces = common.read_jsonl(common.FACES)
    rows = []
    excluded = collections.Counter()
    for f in faces:
        if "/" not in f["text_code_visual_ltr"]:
            continue
        ls = lines_of(f)
        if ls is None:
            excluded["unknown_damaged_or_empty_line"] += 1
            continue
        if f["direction"] == "BUS":
            # Review response (finding 13): boustrophedon faces change direction by line and the
            # catalogue does not say which line runs which way; they are excluded.
            excluded["boustrophedon"] += 1
            continue
        fam = f["object_family_id"]
        line_found, straddle_found = [], []
        by_order = {"forward": [], "reverse": []}
        # Review response (finding 13): each line is counted once, including interior lines.
        for L in ls:
            if len(L) >= 2:
                line_found.append(contains(ref, L, fam))
        for k in range(len(ls) - 1):
            A, B = ls[k], ls[k + 1]
            for order, (first, second) in (("forward", (A, B)), ("reverse", (B, A))):
                joined = first + second
                cut = len(first)
                for m in {len(A), len(B)}:
                    if m < 2:
                        continue
                    for i in range(max(0, cut - m + 1), min(cut, len(joined) - m + 1)):
                        w = joined[i:i + m]
                        if i < cut < i + m:
                            hit = contains(ref, w, fam)
                            straddle_found.append(hit)
                            by_order[order].append(hit)
        if not line_found or not straddle_found:
            excluded["no_line_or_window_of_length_2plus"] += 1
            continue
        rows.append({"face": f["record_id"], "type": f["metadata"].get("type"), "lines": len(ls),
                     "line_rate": sum(line_found) / len(line_found),
                     "straddle_rate": sum(straddle_found) / len(straddle_found),
                     "line_windows": len(line_found), "straddle_windows": len(straddle_found),
                     "straddle_rate_best_order": max(sum(v) / len(v) for v in by_order.values() if v)})
    better = sum(r["line_rate"] > r["straddle_rate"] for r in rows)
    worse = sum(r["line_rate"] < r["straddle_rate"] for r in rows)
    n = better + worse
    p_two = min(1.0, 2 * sum(comb(n, k) for k in range(max(better, worse), n + 1)) / 2 ** n) if n else None
    pooled_line = sum(r["line_rate"] * r["line_windows"] for r in rows) / sum(r["line_windows"] for r in rows)
    pooled_str = sum(r["straddle_rate"] * r["straddle_windows"] for r in rows) / sum(r["straddle_windows"] for r in rows)
    # Amendment 2026-10-12: the both-orders control includes windows from the wrong line
    # order, which cannot occur in the text. The conservative comparison uses, per face,
    # the order with the higher straddle rate.
    b2 = sum(r["line_rate"] > r["straddle_rate_best_order"] for r in rows)
    w2 = sum(r["line_rate"] < r["straddle_rate_best_order"] for r in rows)
    n2 = b2 + w2
    p2 = min(1.0, 2 * sum(comb(n2, k) for k in range(max(b2, w2), n2 + 1)) / 2 ** n2) if n2 else None
    best_order = {"mean_straddle_rate_best_order": sum(r["straddle_rate_best_order"] for r in rows) / len(rows),
                  "faces_line_higher": b2, "faces_straddle_higher": w2, "ties": len(rows) - n2,
                  "sign_test_two_sided_p": p2}
    summary = {"conservative_best_order": best_order, "protocol_sha256": common.sha256(common.PROG / "PROTOCOL.md"),
               "faces_with_breaks": sum("/" in f["text_code_visual_ltr"] for f in faces),
               "faces_used": len(rows), "excluded": dict(excluded),
               "mean_line_rate": sum(r["line_rate"] for r in rows) / len(rows),
               "mean_straddle_rate": sum(r["straddle_rate"] for r in rows) / len(rows),
               "pooled_line_rate": pooled_line, "pooled_straddle_rate": pooled_str,
               "faces_line_higher": better, "faces_straddle_higher": worse, "ties": len(rows) - n,
               "sign_test_two_sided_p": p_two,
               "object_types": dict(collections.Counter(r["type"] for r in rows))}
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    common.RAW.mkdir(parents=True, exist_ok=True)
    (common.RAW / "step3-linebreak-faces.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
