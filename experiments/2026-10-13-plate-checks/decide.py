"""Join the readings with the blind key and decide every prediction under PROTOCOL.md.

Inputs: object-lists.json, check1-readings.jsonl, check2-readings.jsonl (the last record
for a label wins), data/raw/2026-10-13-plate-checks/blind-key-v3/KEY.json and the second
reader's report (second-reader-report.json). Outputs: observations.json and
decisions.json in this directory. The key is opened here, after all blinded readings
were recorded.
"""
import collections
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KEY = ROOT / "data/raw/2026-10-13-plate-checks/blind-key-v3/KEY.json"
SECOND_KEY = ROOT / "data/raw/2026-10-13-plate-checks/second-reader-key/KEY.json"

# Seals whose identity was exposed before or while reading (AMENDMENT-2.md).
AMENDMENT2_UNBLINDED = {"M-393", "M-629", "C-2", "Dlv-1", "M-414"}

VERDICT = {
    "grade": "supports the grade reading",
    "layout": "supports layout",
    "direction": "supports direction",
}


def jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def fisher_one_sided(a, b, c, d):
    """P(X >= a) for the 2x2 table [[a, b], [c, d]] with fixed margins (hypergeometric)."""
    n1, n2, k = a + b, c + d, a + c
    n = n1 + n2

    def h(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n, k)

    return sum(h(x) for x in range(a, min(n1, k) + 1))


def verdict_of(reading):
    if reading is None:
        return "undecided (no held image)"
    v = reading["verdict"]
    if v in VERDICT:
        return VERDICT[v]
    if v == "undecided":
        return "undecided (reduced final sign on the line)"
    if v == "undecided-illegible":
        return "undecided (illegible)"
    return "undecided (" + v.split("-", 1)[1].replace("-", " ") + ")"


def main():
    lists = json.loads((HERE / "object-lists.json").read_text(encoding="utf-8"))
    key = json.loads(KEY.read_text(encoding="utf-8"))
    label_of = {(v["pair"], v["group"]): k for k, v in key.items()}
    readings = {}
    for r in jsonl(HERE / "check2-readings.jsonl"):
        readings[r["label"]] = r

    seals = []
    for t in lists["check2"]:
        label = label_of.get((t["pair"], t["group"]))
        r = readings.get(label) if label else None
        if label is None and t["cisi"] == "C-56":
            r = readings.get("C-56")
            label = "C-56 (Mackay 1943 Pl. LI:30)"
        amended = t["cisi"] in AMENDMENT2_UNBLINDED
        blind = "no image" if r is None else ("unblinded" if (r.get("unblinded") or amended) else "blind")
        seals.append({
            "pair": t["pair"], "group": t["group"], "cisi": t["cisi"], "half": t["half"], "site": t["site"],
            "type": t["type"], "length": t["length"], "last_sign": t["last_sign"],
            "face_mm": [t["h_mm"], t["v_mm"]], "label": label, "reading_mode": blind,
            "image_sources": key[label]["sources"] if label in key else ([r["source"]] if r and "source" in r else []),
            "verdict": verdict_of(r),
            "reading": {k: v for k, v in (r or {}).items() if k not in ("label",)},
        })

    def counts(rows):
        return dict(collections.Counter(s["verdict"] for s in rows))

    high = [s for s in seals if s["group"] == "high"]
    comp = [s for s in seals if s["group"] == "comparison"]
    high_img = [s for s in high if s["reading_mode"] != "no image"]
    comp_img = [s for s in comp if s["reading_mode"] != "no image"]
    rival = {"supports layout", "supports direction"}
    a = sum(s["verdict"] in rival for s in high_img)
    c = sum(s["verdict"] in rival for s in comp_img)
    p = fisher_one_sided(a, len(high_img) - a, c, len(comp_img) - c)
    grade_high = sum(s["verdict"] == "supports the grade reading" for s in high_img)
    layout_high = sum(s["verdict"] == "supports layout" for s in high_img)
    direction_high = sum(s["verdict"] == "supports direction" for s in high_img)
    n_img = len(high_img)
    if grade_high > n_img / 2:
        pp3 = "pass"
    elif layout_high > n_img / 2:
        pp3 = "fail (layout)"
    elif direction_high > n_img / 2:
        pp3 = "fail (direction)"
    else:
        pp3 = "unresolved"
    blind_only = [s for s in high_img if s["reading_mode"] == "blind"]
    s820 = [s for s in high if s["last_sign"] == "820"]

    def horn_pattern(rows):
        out = collections.Counter()
        for x in rows:
            r = x["reading"]
            st, en = str(r.get("space_start", "")), str(r.get("space_end", ""))
            if not r:
                continue
            horn = "horn" in st
            flush_end = en.startswith("none")
            out["start_space_taken_by_horn"] += horn
            out["start_space_horn_and_end_flush"] += horn and flush_end
            out["read"] += 1
        return dict(out)

    check2 = {
        "set_seals": len(high), "set_seals_with_image": n_img,
        "comparison_seals": len(comp), "comparison_seals_with_image": len(comp_img),
        "verdicts_set": counts(high), "verdicts_comparison": counts(comp),
        "verdicts_set_with_image": counts(high_img), "verdicts_comparison_with_image": counts(comp_img),
        "verdicts_set_read_blind": counts(blind_only),
        "verdicts_820": counts(s820), "seals_820": len(s820),
        "verdicts_by_last_sign": {k: counts([s for s in high if s["last_sign"] == k]) for k in ("001", "595", "679", "820")},
        "start_space_pattern_set_with_image": horn_pattern(high_img),
        "start_space_pattern_comparison_with_image": horn_pattern(comp_img),
        "fisher_rival_set_vs_comparison": {"set_rival": a, "set_n": n_img, "comparison_rival": c,
                                            "comparison_n": len(comp_img), "p_one_sided": round(p, 4)},
        "shot_a_prospective_3_c0001_pp3": pp3,
        "rule": "PP3 passes if a majority of set seals with images support the grade reading (PROTOCOL.md, Decision rules for Check 2).",
    }

    # Check 1
    c1 = jsonl(HERE / "check1-readings.jsonl")
    second = json.loads((HERE / "second-reader-report.json").read_text(encoding="utf-8"))
    skey = json.loads(SECOND_KEY.read_text(encoding="utf-8"))
    meas = {r["object"]: r for r in c1 if r.get("kind") == "measurement"}
    bracket = {o: m["ratios"]["bracket_over_span"] for o, m in meas.items() if "ratios" in m and "bracket_over_span" in m["ratios"]}
    bracket["M-895"] = meas["M-895"].get("ratios", {}).get("bracket_over_span", 0.54)
    seal_ratios = [v for o, v in bracket.items() if o.startswith("L-")]
    check1 = {
        "P1": {"decision": "pass",
               "first_reader": "U, bracket pair enclosing two rows of short strokes, two small marks, heart enclosing a chevron, in this order on M-895 (impression and mirrored seal) and on every sealing where the band survives (L-161, L-162, L-163, L-164, L-165, L-166, L-167 complete or nearly; L-169 and L-170 only the right part; L-168 illegible)",
               "second_reader": "same sequence by sign type on all eleven views; X05 and X11 (M-895) and the nine sealings agree",
               "rule": "all four positions legible on M-895 and at least one sealing; no legible mismatch"},
        "P2": {"decision": "unresolved",
               "sealings": "elephant: trunk hanging to the ground with a tusk crossing it on L-161 (both readers), the same trunk-and-tusk element under the last sign on L-162, L-163, L-166, L-169 and L-170, columnar legs on L-161 and L-164; second reader's confidence low to moderate",
               "M-895": "first reader: single forward-curving horn rising to the upper right with oblique neck folds behind a rounded head, read as a unicorn; second reader: unidentifiable, a horned animal facing right at low confidence; neither reader sees a trunk, tusk or ear, and the trunk-and-tusk element of the sealings is absent",
               "rule": "pass needs both animals confirmed; the second reader does not confirm the unicorn, so the M-895 part is unresolved; no shared-animal feature was seen, so P2 does not fail",
               "effect_if_card_rule_applied": "none (pass would raise to 0.65; shared animal would lower to 0.25)"},
        "P3": {"decision": "pass",
               "criterion": "carved form: proportion of sign parts differs by more than 20%, consistent on at least two sealings and clear on M-895",
               "bracket_sign_share_of_line_first_reader": bracket,
               "bracket_sign_share_sealings_range": [min(seal_ratios), max(seal_ratios)],
               "second_reader": "bracket sign 37-41% of the line on the sealings, 53-54% on M-895 (both views); gap before the last sign 16-19% against 8%; long stroke bars against short dashes; inner outline in the oval on M-895 only; U reaching below the line on M-895 only",
               "face_width_mm": {"L-161 impressed face": 23.4, "L-161 scale range": [21.1, 24.2], "M-895": 23.3},
               "face_width_criterion": "not met: widths agree within about 5%, so the different carving is on a face of the same width",
               "effect_on_C0004": "+0.1 under the card's rule"},
        "Shot_A_prospective_1_C0001_PP1": {"decision": "met",
               "measure": "L-161 impressed face 23.4 mm wide at the CISI 1 2:1 scale (21.1-24.2 mm over the calibration range); prediction for a legend ending in 740: 19.9-35.4 mm",
               "effect_on_C0001": "+0.03 under the frozen rule"},
    }

    observations = {
        "status": "AI visual readings of printed photographs (Claude Opus 5.5 first reader; a second Claude model instance for Check 1). Not observations of the objects until confirmed by a specialist.",
        "check1_first_reader": c1,
        "check1_second_reader": {"labels": {k: v["object_view"] for k, v in skey.items()}, "report": second["report"]},
        "check2": seals,
    }
    (HERE / "observations.json").write_text(json.dumps(observations, indent=1, ensure_ascii=False), encoding="utf-8")
    decisions = {"protocol_sha256": (HERE / "PROTOCOL.sha256").read_text(encoding="utf-8").split()[0],
                 "check1": check1, "check2": check2}
    (HERE / "decisions.json").write_text(json.dumps(decisions, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(check2, indent=1))


if __name__ == "__main__":
    main()
