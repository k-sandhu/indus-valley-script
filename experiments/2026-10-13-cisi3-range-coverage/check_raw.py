"""Independent check of count_ranges.py from the raw Lipi CSV.

Reads the export's own inscriptions.csv rather than the normalized faces, takes the
object family from the part of `id` before the dot, splits `cisi` on its first hyphen,
and uses CISI 1 and 2 end numbers typed from the printed ranges. It then compares the
present numbers, families and faces with a run of count_ranges.py.

Usage: python -P experiments/2026-10-13-cisi3-range-coverage/check_raw.py --run <tracked run dir> --local <local run dir>
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "lipi" / "src" / "assets" / "data" / "inscriptions.csv"
RAW_SHA256 = "c36d0c26becb00b12b509cb2f5a35ffab1b5332e2e438cda308a272f77dba62c"
# Highest CISI 1 or 2 number per prefix: M-1659 and H-1019 (CISI 2), K-122 and C-50 (CISI 1), Ns-10 (CISI 2), Rjd-1 (CISI 1).
END = {"M": 1659, "H": 1019, "K": 122, "C": 50, "Ns": 10, "Rjd": 1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--local", required=True)
    args = ap.parse_args()
    run, local_run = Path(args.run), Path(args.local)
    digest = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if digest != RAW_SHA256:
        sys.exit(f"{RAW} has SHA256 {digest}, expected {RAW_SHA256}")

    mine = {p: {} for p in END}
    with RAW.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            prefix, _, rest = row["cisi"].strip().partition("-")
            digits = ""
            for ch in rest:
                if not ch.isdigit():
                    break
                digits += ch
            if prefix not in END or not digits or int(digits) <= END[prefix]:
                continue
            cell = mine[prefix].setdefault(int(digits), [set(), 0, set()])
            cell[0].add(row["id"].split(".")[0])
            cell[1] += 1
            head = row["type"].split(":")[0]
            cell[2].add("pottery" if head == "POT" else "seal-tablet" if head in ("SEAL", "TAB", "TAG") else "other")

    theirs = {p: {} for p in END}
    their_context = {}
    with (local_run / "number-slots.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["present"] == "1":
                theirs[row["prefix"]][int(row["number"])] = [set(row["object_family_ids"].split(";")),
                                                             int(row["faces"]), set(row["classes"].split(";"))]
            else:
                their_context[(row["prefix"], int(row["number"]))] = row["absent_context"]

    # Context of each absent slot, walking outward to the nearest present numbers.
    my_context = {}
    for p in END:
        present = sorted(mine[p])
        for n in range(END[p] + 1, present[-1] + 1):
            if n in mine[p]:
                continue
            near = set()
            for m in range(n - 1, END[p], -1):
                if m in mine[p]:
                    near |= mine[p][m][2]
                    break
            for m in range(n + 1, present[-1] + 1):
                if m in mine[p]:
                    near |= mine[p][m][2]
                    break
            my_context[(p, n)] = near.pop() if len(near) == 1 else "mixed"
    with (run / "range-coverage.csv").open(encoding="utf-8", newline="") as fh:
        reported = {row["prefix"]: row for row in csv.DictReader(fh)}

    result = {"raw_input": {str(RAW.relative_to(ROOT)).replace("\\", "/"): digest},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "run": str(run).replace("\\", "/"), "local_run": str(local_run).replace("\\", "/"), "prefixes": {}}
    ok = True
    for p in END:
        top = max(mine[p])
        slots = top - END[p]
        same = (mine[p] == theirs[p] and int(reported[p]["slots"]) == slots
                and int(reported[p]["numbers_present"]) == len(mine[p]))
        ok &= same
        contexts = {}
        for (q, _), c in my_context.items():
            if q == p:
                contexts[c] = contexts.get(c, 0) + 1
        result["prefixes"][p] = {"slots": slots, "numbers_present": len(mine[p]),
                                 "faces": sum(c[1] for c in mine[p].values()), "absent_context": contexts,
                                 "agrees_with_run": same}
    result["absent_context_agrees"] = my_context == their_context
    ok &= result["absent_context_agrees"]
    result["all_agree"] = ok
    (run / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["prefixes"], indent=1), "\nall_agree:", ok)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
