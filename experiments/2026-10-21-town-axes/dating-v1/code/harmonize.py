"""Coordinating pass that applies the shared conventions of METHOD.md to every town file.

The town files were written by eight regional research agents. This pass makes
three kinds of change, each recorded in the entry it touches, and prints a log:

1. sha256 fields that carry several hashes or annotations keep the first hash;
   the rest of the text is appended to url_or_path as "other files' SHA-256: ...".
2. A determination whose source does not print the half-life is copied into the
   5568-year fields only when the laboratory reports conventional ages by
   convention (Stuiver and Polach 1977): AMS and radiometric laboratories such as
   Beta Analytic, Groningen, Gliwice, Paleo Labo, Oxford and Arizona, and a
   Pennsylvania (P-) reprint whose printed value equals the value in the
   Pennsylvania date list, which states the 5568-year half-life.
3. Birbal Sahni Institute (BS-) ages whose source states neither the half-life nor
   the Stuiver and Polach convention keep empty 5568-year fields: the BS date
   lists of 1978-1982 use 5570 years, but Sarkar et al. 2016 state 5730 years for
   the BSIP Bhirrana series, so the half-life of an unstated BSIP age is unknown.

Run once: python -P code/harmonize.py [--dry-run]
"""
import json
import pathlib
import re
import sys

TOWNS = pathlib.Path(__file__).resolve().parent.parent / "towns"
CONVENTIONAL = ("Beta", "GrN", "GdA", "PLD", "OxA", "AA-", "IAAA", "UGAMS", "Wk", "KIA", "Poz", "SUERC", "MAMS", "LTL")
NOTE_CONV = ("Coordinating pass: the source does not print the half-life; the laboratory reports conventional "
             "radiocarbon ages (Stuiver and Polach 1977), so the printed age is copied to the 5568-year fields.")
NOTE_PENN = ("Coordinating pass: the source does not print the half-life; the printed value equals the one in the "
             "Pennsylvania date list, which uses 5568 years, so it is copied to the 5568-year fields.")
NOTE_BS = ("Coordinating pass: the source states neither the half-life nor the Stuiver and Polach convention, and "
           "BSIP practice varied (5570 years in the BS date lists of 1978-1982, 5730 years for the Bhirrana series in "
           "Sarkar et al. 2016), so the 5568-year fields are left empty.")


def add_note(r, text):
    r["note"] = (r.get("note", "").rstrip() + " " + text).strip() if r.get("note") else text


def main(dry):
    log = []
    penn = {}
    for f in TOWNS.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for p in d["parts"]:
            for r in p.get("radiocarbon") or []:
                if str(r.get("source", "")).startswith("rc-penn") and r.get("half_life_printed") == 5568:
                    penn[str(r["lab_no"]).strip()] = (r["age_bp_printed"], r["sigma_printed"])
    for f in sorted(TOWNS.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        changed = False
        for s in d["sources"]:
            v = s.get("sha256")
            if v and not re.fullmatch(r"[0-9a-f]{64}", v):
                m = re.search(r"[0-9a-f]{64}", v)
                if m:
                    rest = (v[:m.start()] + v[m.end():]).strip(" ;,")
                    s["sha256"] = m.group(0)
                    if rest:
                        s["url_or_path"] = (s.get("url_or_path") or "") + f" [other files' SHA-256 and labels: {rest}]"
                    log.append(f"{d['town']}: {s['id']} sha256 normalised")
                    changed = True
        for p in d["parts"]:
            for r in p.get("radiocarbon") or []:
                lab = str(r.get("lab_no") or "").strip()
                hl, a, sg = r.get("half_life_printed"), r.get("age_bp_printed"), r.get("sigma_printed")
                if hl is not None or a is None:
                    continue
                if lab.startswith(CONVENTIONAL) and r.get("age_bp_5568") is None:
                    r["age_bp_5568"], r["sigma_5568"] = a, sg
                    add_note(r, NOTE_CONV)
                    log.append(f"{d['town']}: {lab} ({r['source']}) copied as conventional age")
                    changed = True
                elif lab.startswith("P-") and r.get("age_bp_5568") is None and penn.get(lab) == (a, sg):
                    r["age_bp_5568"], r["sigma_5568"] = a, sg
                    add_note(r, NOTE_PENN)
                    log.append(f"{d['town']}: {lab} ({r['source']}) copied from matching Penn value")
                    changed = True
                elif lab.startswith("BS-") and r.get("age_bp_5568") is not None:
                    note = r.get("note") or ""
                    if "Stuiver and Polach" in note:
                        continue
                    r["age_bp_5568"], r["sigma_5568"] = None, None
                    add_note(r, NOTE_BS)
                    log.append(f"{d['town']}: {lab} ({r['source']}) 5568 fields emptied")
                    changed = True
        if changed and not dry:
            f.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(log) or "no changes")


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
