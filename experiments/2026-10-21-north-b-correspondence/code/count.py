"""Count Kurukh and Malto initials against Tamil m- and v- across DEDR (PROTOCOL.md).

Reads the local parse written by dedr_parts.py and writes a results JSON that holds
counts, entry numbers and initial and vowel classes, and no dictionary forms.

    python -I experiments/2026-10-21-north-b-correspondence/code/count.py --out experiments/2026-10-21-north-b-correspondence/results-v1/results.json
"""

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PARSE = ROOT / "data" / "raw" / "2026-10-21-north-b-correspondence" / "derived-v1" / "dedr-parts.jsonl"
NORTH = ("Kurukh", "Malto")
CLASSES = ("m", "b", "v", "other")
EXCLUDED = "4876"


def entry_number(key):
    """'4896(a)' -> '4896'; '583A' stays a number of its own; appendix keys keep their prefix."""
    return re.sub(r"\([a-z]\)$", "", key)


def entry_sort(x):
    m = re.match(r"(a?)(\d+)(.*)", x)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else ("z", 0, x)


def nfc_initial(form):
    s = unicodedata.normalize("NFC", form)
    for ch in s:
        if unicodedata.category(ch).startswith("L"):
            base = "".join(c for c in unicodedata.normalize("NFD", ch) if c not in "́̀")
            return unicodedata.normalize("NFC", base).lower()
    return ""


def lang_forms(part, lang):
    out = []
    for ln in part["lines"]:
        if ln["lang"] == lang:
            out.extend(ln["forms"])
    return out


def summary(forms):
    """First form, first undoubted form and form-level classes of one language in one part."""
    kept = [f for f in forms if not f["borrowed"]]
    if not kept:
        return None
    first = kept[0]
    und = [f for f in kept if not f["doubt"]]
    return {
        "first": first,
        "first_undoubted": und[0] if und else None,
        "classes_any": sorted({f["initial_class"] for f in kept}),
        "classes_undoubted": sorted({f["initial_class"] for f in und}),
        "b_forms": [f for f in kept if f["initial_class"] == "b"],
        "m_forms": [f for f in kept if f["initial_class"] == "m"],
    }


def unit_table():
    return {c: 0 for c in CLASSES}


def analyse(records):
    parts_info = []
    for rec in records:
        for part in rec["parts"]:
            ta = [f for f in lang_forms(part, "Tamil") if not f["borrowed"]]
            if not ta:
                continue
            t0 = ta[0]
            t_letter = t0["initial_letter"]
            t_nfc = nfc_initial(t0["form"])
            group = t_letter if t_letter in ("m", "v") else None
            ta_initials = {f["initial_letter"] for f in ta}
            info = {
                "entry": rec["entry"], "number": entry_number(rec["entry"]), "letter": part["letter"],
                "tamil_initial": t_nfc, "group": group,
                "tamil_vowel": t0["vowel"], "tamil_nasal_next": t0["nasal_next"],
                "tamil_m_and_v": "m" in ta_initials and "v" in ta_initials,
                "north": {}, "brahui": None, "witness": {},
            }
            for lang in NORTH:
                s = summary(lang_forms(part, lang))
                if s:
                    info["north"][lang] = s
            info["brahui"] = summary(lang_forms(part, "Brahui"))
            for lang in ("Telugu", "Kannada", "Gondi"):
                s = summary(lang_forms(part, lang))
                info["witness"][lang] = s["first"]["initial_class"] if s else None
            parts_info.append(info)
    return parts_info


def tables(parts, langs, key, exclude_4876):
    """Tamil group x northern class counts at the part-language level."""
    out = {}
    for g in ("m", "v"):
        out[g] = {}
        pooled = unit_table()
        no_undoubted = 0
        for lang in langs:
            t = unit_table()
            for p in parts:
                if p["group"] != g or (exclude_4876 and p["number"] == EXCLUDED):
                    continue
                s = p["north"].get(lang) if lang in NORTH else p["brahui"]
                if not s:
                    continue
                f = s[key]
                if f is None:
                    no_undoubted += 1
                    continue
                t[f["initial_class"]] += 1
                pooled[f["initial_class"]] += 1
            out[g][lang] = t
        if len(langs) > 1:
            out[g]["pooled"] = pooled
        if key == "first_undoubted":
            out[g]["units_with_only_doubtful_forms"] = no_undoubted
    return out


def any_form_tables(parts, exclude_4876, undoubted):
    out = {}
    for g in ("m", "v"):
        out[g] = {}
        for lang in NORTH:
            t = unit_table()
            for p in parts:
                if p["group"] != g or (exclude_4876 and p["number"] == EXCLUDED):
                    continue
                s = p["north"].get(lang)
                if not s:
                    continue
                for c in (s["classes_undoubted"] if undoubted else s["classes_any"]):
                    t[c] += 1
            out[g][lang] = t
    return out


def entries_with_b(parts, group, exclude_4876, level, skip_alternation=False):
    found = set()
    for p in parts:
        if p["group"] != group or (exclude_4876 and p["number"] == EXCLUDED):
            continue
        if skip_alternation and p["tamil_m_and_v"]:
            continue
        for lang in NORTH:
            s = p["north"].get(lang)
            if not s:
                continue
            if level == "first_undoubted":
                hit = s["first_undoubted"] is not None and s["first_undoubted"]["initial_class"] == "b"
            elif level == "first":
                hit = s["first"]["initial_class"] == "b"
            else:
                hit = bool(s["b_forms"])
            if hit:
                found.add(p["number"])
    return sorted(found, key=entry_sort)


def case_list(parts, group, cls):
    """Every part of a Tamil group with a non-borrowed northern form of class cls, without forms."""
    rows = []
    for p in parts:
        if p["group"] != group:
            continue
        for lang in NORTH:
            s = p["north"].get(lang)
            if not s:
                continue
            hits = [f for f in s[{"b": "b_forms", "m": "m_forms"}[cls]]]
            if not hits:
                continue
            f = hits[0]
            rows.append({
                "entry": p["entry"], "part": p["letter"] or None, "language": lang,
                "first_form_class": s["first"]["initial_class"],
                "first_undoubted_class": s["first_undoubted"]["initial_class"] if s["first_undoubted"] else None,
                "is_first_form": s["first"] is f,
                "doubtful": f["doubt"], "bh": f.get("bh", False),
                "n_forms_of_class": len(hits),
                "tamil_vowel": p["tamil_vowel"], "tamil_nasal_next": p["tamil_nasal_next"],
                "northern_vowel": f["vowel"], "northern_nasal_next": f["nasal_next"],
                "tamil_m_and_v": p["tamil_m_and_v"],
                "telugu_first_class": p["witness"]["Telugu"], "kannada_first_class": p["witness"]["Kannada"],
                "gondi_first_class": p["witness"]["Gondi"],
            })
    return rows


def vowel_tables(parts):
    out = defaultdict(lambda: defaultdict(Counter))
    for p in parts:
        if p["group"] not in ("m", "v"):
            continue
        for lang in NORTH:
            s = p["north"].get(lang)
            if not s or s["first_undoubted"] is None:
                continue
            f = s["first_undoubted"]
            pair = f"Tamil {p['group']}- / northern {f['initial_class']}-"
            out[pair]["tamil"][f"{p['tamil_vowel']}{', nasal next' if p['tamil_nasal_next'] else ''}"] += 1
            out[pair]["northern"][f"{f['vowel']}{', nasal next' if f['nasal_next'] else ''}"] += 1
    return {k: {kk: dict(sorted(vv.items())) for kk, vv in v.items()} for k, v in sorted(out.items())}


def all_initials(parts):
    rows = defaultdict(unit_table)
    for p in parts:
        for lang in NORTH:
            s = p["north"].get(lang)
            if not s or s["first_undoubted"] is None:
                continue
            rows[p["tamil_initial"] or "?"][s["first_undoubted"]["initial_class"]] += 1
    out = {}
    for k in sorted(rows):
        r = rows[k]
        n = sum(r.values())
        out[k] = dict(r, units=n, b_share=round(r["b"] / n, 4) if n else None)
    return out


def union_check(records):
    """S7: northern classes found in a shorter print of a repeated number but not in the longest."""
    extra = []
    for rec in records:
        if rec.get("n_prints", 1) < 2:
            continue
        main = set()
        for p in analyse([rec]):
            for lang, s in p["north"].items():
                if p["group"]:
                    for c in s["classes_any"]:
                        main.add((p["group"], lang, c))
        for other in rec.get("other_prints", []):
            for p in analyse([dict(other, n_prints=1)]):
                for lang, s in p["north"].items():
                    if p["group"]:
                        for c in s["classes_any"]:
                            if (p["group"], lang, c) not in main:
                                extra.append({"entry": rec["entry"], "group": p["group"], "language": lang, "class": c})
    return extra


def run(records):
    parts = analyse(records)
    pop = [p for p in parts if p["group"] in ("m", "v") and p["north"]]
    pass_entries = entries_with_b(pop, "m", True, "first_undoubted")
    fail_any_m = entries_with_b(pop, "m", True, "any")
    v_first_b = entries_with_b(pop, "v", False, "first")
    if len(pass_entries) >= 2:
        outcome, credence = "pass", 0.30
    elif not fail_any_m and v_first_b:
        outcome, credence = "failure", 0.10
    else:
        outcome, credence = "unresolved", 0.20
    alternation = sorted({p["entry"] for p in pop if p["tamil_m_and_v"]})
    res = {
        "population": {
            "parts_with_tamil_line": len(parts),
            "parts_tamil_m": sum(1 for p in parts if p["group"] == "m"),
            "parts_tamil_v": sum(1 for p in parts if p["group"] == "v"),
            "population_parts_tamil_m": sum(1 for p in pop if p["group"] == "m"),
            "population_parts_tamil_v": sum(1 for p in pop if p["group"] == "v"),
            "population_entries_tamil_m": len({p["number"] for p in pop if p["group"] == "m"}),
            "population_entries_tamil_v": len({p["number"] for p in pop if p["group"] == "v"}),
            "units": {g: {lang: sum(1 for p in pop if p["group"] == g and lang in p["north"]) for lang in NORTH} for g in ("m", "v")},
        },
        "entry_4876": [{"part": p["letter"] or None,
                        **{lang: {"first_class": s["first"]["initial_class"], "doubtful": s["first"]["doubt"],
                                  "vowel": s["first"]["vowel"], "nasal_next": s["first"]["nasal_next"]}
                           for lang, s in p["north"].items()},
                        "tamil_initial": p["tamil_initial"], "tamil_vowel": p["tamil_vowel"], "tamil_nasal_next": p["tamil_nasal_next"]}
                       for p in parts if p["number"] == EXCLUDED],
        "primary": {
            "first_undoubted_form": {"without_4876": tables(pop, NORTH, "first_undoubted", True),
                                     "with_4876": tables(pop, NORTH, "first_undoubted", False)},
            "first_form_doubtful_allowed": {"without_4876": tables(pop, NORTH, "first", True),
                                            "with_4876": tables(pop, NORTH, "first", False)},
            "entries_with_northern_b_first_undoubted": {
                "tamil_m_without_4876": pass_entries,
                "tamil_m_with_4876": entries_with_b(pop, "m", False, "first_undoubted"),
                "tamil_v": entries_with_b(pop, "v", False, "first_undoubted"),
            },
            "entries_with_northern_b_first_form_doubtful_allowed": {
                "tamil_m_without_4876": entries_with_b(pop, "m", True, "first"),
                "tamil_v": v_first_b,
            },
        },
        "pass_rule": {
            "entries_counted_for_pass": pass_entries,
            "n_entries_counted_for_pass": len(pass_entries),
            "tamil_m_entries_with_any_northern_b_form_excluding_4876": fail_any_m,
            "tamil_v_entries_with_northern_b_first_form": len(v_first_b),
            "outcome": outcome,
            "credence_by_frozen_rule": credence,
        },
        "cases": {
            "tamil_m_northern_b": case_list(pop, "m", "b"),
            "tamil_v_northern_m": case_list(pop, "v", "m"),
        },
        "S1_every_form": {"doubtful_allowed": any_form_tables(pop, True, False),
                          "undoubted": any_form_tables(pop, True, True)},
        "S2_brahui": {"first_undoubted_form": tables([p for p in parts if p["group"] in ("m", "v") and p["brahui"]], ("Brahui",), "first_undoubted", True),
                      "entries_with_b_tamil_m": sorted({p["number"] for p in parts if p["group"] == "m" and p["brahui"] and p["brahui"]["b_forms"]}, key=entry_sort),
                      "entries_with_m_tamil_v": sorted({p["number"] for p in parts if p["group"] == "v" and p["brahui"] and p["brahui"]["m_forms"]}, key=entry_sort)},
        "S3_all_tamil_initials": all_initials([p for p in parts if p["north"]]),
        "S4_vowel_context": vowel_tables(pop),
        "S5_tamil_m_and_v": {"entries": alternation,
                             "pass_entries_without_them": entries_with_b(pop, "m", True, "first_undoubted", skip_alternation=True),
                             "tamil_v_entries_with_b_without_them": entries_with_b(pop, "v", False, "first_undoubted", skip_alternation=True)},
        "S7_union_over_prints": union_check(records),
    }
    return res


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--parse", default=str(PARSE))
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    src = Path(args.parse)
    records = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    res = run(records)
    res = {"study": "NORTH-B-CORRESPONDENCE-2026-10-21", "protocol": "experiments/2026-10-21-north-b-correspondence/PROTOCOL.md",
           "parse_sha256": hashlib.sha256(src.read_bytes()).hexdigest(), **res}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"out": str(out), "outcome": res["pass_rule"]["outcome"]}))


if __name__ == "__main__":
    sys.exit(main())
