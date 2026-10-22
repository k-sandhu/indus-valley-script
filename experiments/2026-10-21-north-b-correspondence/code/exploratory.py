"""Exploratory analyses written after the frozen count (REPORT.md, "Exploratory steps").

Reads the local parse and the frozen results and writes counts, entry numbers and
classes, without dictionary forms:

1. Every Tamil m- or v- part in which Brahui has a b- or m- first undoubted form
   that crosses the regular correspondence, with the vowel classes and the
   Kurukh and Malto classes of the same part.
2. Tamil m- parts by the Tamil vowel class (long front or other) and the class of
   the first undoubted northern form, the context P5 names.
3. Northern b- and m- reflexes by Tamil initial and by whether a nasal follows the
   Tamil vowel.

    python -I experiments/2026-10-21-north-b-correspondence/code/exploratory.py --out experiments/2026-10-21-north-b-correspondence/exploratory-v1/exploratory.json
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import count  # noqa: E402


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    src = count.PARSE
    records = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    parts = count.analyse(records)

    brahui = []
    for p in parts:
        b = p["brahui"]
        if p["group"] not in ("m", "v") or not b or b["first_undoubted"] is None:
            continue
        f = b["first_undoubted"]
        if (p["group"], f["initial_class"]) in (("m", "b"), ("v", "m")):
            brahui.append({
                "entry": p["entry"], "tamil_initial": p["group"], "brahui_class": f["initial_class"],
                "tamil_vowel": p["tamil_vowel"], "tamil_nasal_next": p["tamil_nasal_next"],
                "brahui_vowel": f["vowel"], "brahui_nasal_next": f["nasal_next"],
                "kurukh_first_undoubted_class": (p["north"]["Kurukh"]["first_undoubted"] or {}).get("initial_class") if "Kurukh" in p["north"] else None,
                "malto_first_undoubted_class": (p["north"]["Malto"]["first_undoubted"] or {}).get("initial_class") if "Malto" in p["north"] else None,
            })

    p5_context = Counter()
    nasal = Counter()
    for p in parts:
        if p["group"] not in ("m", "v"):
            continue
        for lang in count.NORTH:
            s = p["north"].get(lang)
            if not s or s["first_undoubted"] is None:
                continue
            cls = s["first_undoubted"]["initial_class"]
            if p["group"] == "m" and p["number"] != count.EXCLUDED:
                ctx = "Tamil long front vowel" if p["tamil_vowel"] == "long front" else "other Tamil vowel"
                p5_context[f"{ctx} / northern {cls}"] += 1
            nasal[f"Tamil {p['group']}- {'with' if p['tamil_nasal_next'] else 'without'} nasal next / northern {cls}"] += 1

    res = {
        "study": "NORTH-B-CORRESPONDENCE-2026-10-21",
        "status": "exploratory, computed after results-v1",
        "parse_sha256": count.hashlib.sha256(src.read_bytes()).hexdigest(),
        "brahui_crossing_cases": brahui,
        "tamil_m_by_vowel_context_without_4876": dict(sorted(p5_context.items())),
        "by_nasal_context_with_4876": dict(sorted(nasal.items())),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
