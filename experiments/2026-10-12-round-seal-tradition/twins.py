"""Part 3b: do West Asian texts begin with the "twins" sign (Wells 091) more often than South Asian texts?

Implements PROTOCOL.md Part 3b and the amendment. Inputs (local): Reader 1's records and Reader 2's
blinded readings with the blind key. Output (tracked): run-2026-10-12/twins-summary.json and
transcription-checks.csv (counts per object, no sign codes).
Usage: python twins.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter

from scipy.stats import fisher_exact

import paths

C = paths.import_ffcore()
RUN = paths.HERE / "run-2026-10-12"
CHECKS = paths.RAW / "checks"
TWINS = "two human figures side by side"


def reading_end(face: dict) -> str:
    """Impression end holding the reading-initial sign, per the protocol's direction rule."""
    d = face["direction"]
    if d == "L/R":
        return "left"
    return "right"  # R/L, single-sign NR and blank directions (Lipi parses blanks right to left)


def main():
    faces = {f["record_id"]: f for f in C.load_faces()}
    audit = json.loads((paths.HERE / "prefreeze-audit.json").read_text(encoding="utf-8"))
    wa = audit["west_asia_known_start_record_ids"]
    r1 = json.loads((CHECKS / "reader1.json").read_text(encoding="utf-8"))
    r2_items = json.loads((CHECKS / "reader2.json").read_text(encoding="utf-8"))
    key = json.loads((paths.RAW / "witness" / "blind-key-twins.json").read_text(encoding="utf-8"))
    r2 = {key[f"item{int(it['item']):02d}.png"]: it for it in r2_items}

    rows, wa_rows = [], []
    for rid in wa:
        face = faces[rid]["face"]
        rec = r1["records"].get(rid)
        lipi_091 = faces[rid]["text"]["lines"][0][0] == "091"
        r1_twins = bool(rec and rec.get("reader1_initial") and rec["reader1_initial"].startswith(TWINS))
        end = reading_end(face)
        r2_cat = None
        if rid in r2:
            r2_cat = r2[rid]["right_end_category" if end == "right" else "left_end_category"]
        r2_twins = r2_cat == TWINS
        status = rec["status"] if rec else "no witness"
        wa_rows.append({"record_id": rid, "site": face["site"], "type": face["object_type"],
                        "direction": face["direction"], "reading_end": end, "witness": bool(rec and rec["witnesses"]),
                        "lipi_initial_091": lipi_091, "reader1_twins": r1_twins, "reader2_category": r2_cat,
                        "confirmed_091": r1_twins and r2_twins, "status": status})

    k_conf = sum(r["confirmed_091"] for r in wa_rows)
    k_lipi = sum(r["lipi_initial_091"] for r in wa_rows)
    standard = [r for r in wa_rows if r["status"] not in ("pseudo-inscription", "fill")]
    k_std = sum(r["confirmed_091"] for r in standard)

    sa_checked = r1["south_asian_initial_check"]["checked"]
    sa_total = audit["south_asia_unique_full_texts"]
    sa_img = sum(1 for v in sa_checked.values() if v == TWINS)
    sa_lipi = len(audit["south_asia_initial_091_record_ids"])
    sa_no_image_091 = [r for r in audit["south_asia_initial_091_record_ids"] if r not in sa_checked]
    sa_lipi_plus = sa_img + len(sa_no_image_091)

    def fisher(k, n, ks, ns):
        _, p = fisher_exact([[k, n - k], [ks, ns - ks]], alternative="greater")
        return {"west_asia": [k, n], "south_asia": [ks, ns], "p_one_sided": float(p)}

    sa_r2 = {rid: (r2[rid]["right_end_category"] if reading_end(faces[rid]["face"]) == "right"
                   else r2[rid]["left_end_category"]) for rid in sa_checked if rid in r2}
    agreement = Counter()
    for rid in list(r2):
        if rid in wa:
            r1t = next(r["reader1_twins"] for r in wa_rows if r["record_id"] == rid)
            r2t = next(r["reader2_category"] for r in wa_rows if r["record_id"] == rid) == TWINS
        else:
            r1t = sa_checked.get(rid) == TWINS
            r2t = sa_r2.get(rid) == TWINS
        agreement[f"R1 {'twins' if r1t else 'not'} / R2 {'twins' if r2t else 'not'}"] += 1

    out = {
        "primary": fisher(k_conf, len(wa_rows), sa_img, sa_total),
        "primary_rule": "confirmed = both readers see two human figures side by side at the reading-initial end; "
                        "South Asian count = Reader 1 identifications among the 15 imaged texts of the 34 checked",
        "sensitivity_unconfirmed_lipi_readings_included": fisher(
            sum(r["confirmed_091"] or (r["lipi_initial_091"] and not r["witness"]) or
                (r["lipi_initial_091"] and r["reader1_twins"]) for r in wa_rows),
            len(wa_rows), sa_lipi_plus, sa_total),
        "lipi_091_initial_west_asia": k_lipi,
        "sensitivity_without_pseudo_or_fill": fisher(k_std, len(standard), sa_img, sa_total),
        "west_asia_rows": wa_rows,
        "south_asia": {"unique_complete_texts": sa_total, "lipi_091_initial": sa_lipi,
                       "imaged_and_checked": len(sa_checked), "reader1_twins_initial": sa_img,
                       "lipi_091_initial_without_image": sa_no_image_091,
                       "reader2_categories": sa_r2},
        "reader_agreement_all_28_items": dict(agreement),
        "parpola_1994a_via_laursen": "four Near Eastern and three Indus Valley texts begin with the twins sign",
    }
    out["decision_pattern_holds_with_image_checks"] = out["primary"]["p_one_sided"] < 0.05
    RUN.mkdir(exist_ok=True)
    (RUN / "twins-summary.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")

    # per-object transcription-check table without sign codes
    table = []
    for rid, rec in sorted(r1["records"].items(), key=lambda kv: C.natural_key(kv[0])):
        oc = Counter(p["outcome"] for p in rec["positions"])
        table.append({"record_id": rid, "site": faces[rid]["face"]["site"],
                      "type": faces[rid]["face"]["object_type"], "group": faces[rid]["group"],
                      "witnesses": ";".join(rec["witnesses"]), "lipi_positions": len(rec["positions"]),
                      "agree": oc["agree"], "agree_uncertain": oc["agree_uncertain"], "uncertain": oc["uncertain"],
                      "differ": oc["differ"], "not_shown": oc["not_shown"],
                      "extra_inserted": sum(1 for e in rec["extras"] if e["code"] is not None),
                      "extra_not_inserted": sum(1 for e in rec["extras"] if e["code"] is None),
                      "lipi_order_vs_witness": rec["lipi_order_vs_witness"], "status": rec["status"],
                      "reader1_initial": re.sub(r"\s*\([^)]*\d[^)]*\)", "", rec.get("reader1_initial") or ""),
                      "reader2_initial": (r2[rid]["right_end_category" if reading_end(faces[rid]["face"]) == "right"
                                             else "left_end_category"] if rid in r2 else ""),
                      "note": rec.get("note", "")})
    with (paths.HERE / "transcription-checks.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    print(json.dumps({k: out[k] for k in ("primary", "sensitivity_unconfirmed_lipi_readings_included",
                                          "sensitivity_without_pseudo_or_fill", "reader_agreement_all_28_items")},
                     indent=1))


if __name__ == "__main__":
    main()
