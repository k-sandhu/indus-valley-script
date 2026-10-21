"""Summarize the Q-0027 plate audit (PROTOCOL section 3) into tracked tables without sign codes.

Usage: python -P experiments/2026-10-20-seal-legend-units/audit_summary.py --out experiments/2026-10-20-seal-legend-units/plate-audit
"""
import argparse
import collections
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import legend_units as U  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    work = list(csv.DictReader(open(U.AUDIT / "worklist.tsv", encoding="utf-8"), delimiter="\t"))
    audit = U.load_audit()
    faces = {r["record_id"]: r for r in U.read_jsonl(U.FACES)}
    rows = []
    for w in work:
        rid = w["record_id"]
        face = faces[rid]
        lines, why = U.lines_of(face)
        v = audit.get(rid, {})
        if not w["files"]:
            status = "no_plate_crop"
        elif not v:
            status = "not_read"
        else:
            status = "read"
        rows.append({"record_id": rid, "cisi": w["cisi"], "site": w["site"], "object_type": w["type"],
                     "direction": w["direction"], "segments": w["segments"], "signs_per_segment": w["signs_per_segment"],
                     "code_status": "eligible" if lines else why, "audit_status": status,
                     "legible": v.get("legible", ""), "groups_seen": v.get("groups_seen", ""),
                     "counts_seen_top_down": v.get("counts_seen", ""), "division_confirmed": v.get("division_confirmed", ""),
                     "first_segment_is": v.get("first_segment_is", ""), "layout": v.get("layout", ""),
                     "confidence": v.get("confidence", ""), "plate_order": U.audit_order(v) or "",
                     "note": v.get("note", "")})
    args.out.mkdir(parents=True, exist_ok=True)
    with open(args.out / "audit-table.csv", "x", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    read = [r for r in rows if r["audit_status"] == "read"]
    elig = [r for r in rows if r["code_status"] == "eligible"]
    summary = {"faces": len(rows), "with_plate_crop": sum(r["audit_status"] != "no_plate_crop" for r in rows),
               "read": len(read),
               "code_status": dict(collections.Counter(r["code_status"] for r in rows)),
               "legible": dict(collections.Counter(r["legible"] for r in read)),
               "division_confirmed": dict(collections.Counter(r["division_confirmed"] for r in read)),
               "first_segment_is": dict(collections.Counter(r["first_segment_is"] for r in read)),
               "first_segment_is_confirmed_high_medium": dict(collections.Counter(
                   r["first_segment_is"] for r in read if r["division_confirmed"] == "yes" and r["confidence"] in ("high", "medium"))),
               "layout": dict(collections.Counter(r["layout"] for r in read)),
               "confidence": dict(collections.Counter(r["confidence"] for r in read)),
               "plate_order": dict(collections.Counter(r["plate_order"] or "none" for r in read)),
               "eligible_faces": len(elig),
               "eligible_with_plate_order": sum(bool(r["plate_order"]) for r in elig),
               "eligible_division_not_confirmed": sum(r["division_confirmed"] == "no" for r in elig),
               "no_crop_by_reason": dict(collections.Counter(
                   ("CISI 3 number" if r["cisi"] != "-" else "no CISI number") for r in rows if r["audit_status"] == "no_plate_crop")),
               "verdict_files": {p.name: U.sha256(p) for p in sorted(U.AUDIT.glob("verdicts-*.tsv"))},
               "worklist_sha256": U.sha256(U.AUDIT / "worklist.tsv")}
    U.write_json(args.out / "audit-summary.json", summary)
    print(U.json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
