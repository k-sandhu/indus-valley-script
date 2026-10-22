"""Spot-check recorded radiocarbon ages against the text of their local sources.

For every radiocarbon entry in dating-v1/towns/*.json whose source has a local
PDF, text or HTML file, look for the laboratory number in the text extraction and
report whether the printed age appears within a window after it. The check is
lenient about OCR (spaces inside numbers, the plus-minus sign read as other
characters) and reports three states: `ok` (number and age found together),
`lab-only` (lab number found, age not found nearby) and `absent` (lab number not
found, often because the text layer is missing or the source is a scan we read
by eye). It never edits the town files.

Usage: python -P code/check_rc_against_text.py [town-slug ...]
"""
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOWNS = HERE.parent / "towns"


def text_for(path):
    p = ROOT / path
    cands = []
    if p.suffix.lower() == ".pdf":
        cands = [p.with_suffix(".txt"), p.with_name(p.stem + "_djvu.txt")]
    elif p.suffix.lower() in (".txt", ".html", ".htm"):
        cands = [p]
    for c in cands:
        if c.exists():
            return c.read_text(encoding="utf-8", errors="replace")
    return None


def norm(s):
    return re.sub(r"[\s,]", "", s)


def main():
    slugs = sys.argv[1:]
    files = [TOWNS / f"{s}.json" for s in slugs] if slugs else sorted(TOWNS.glob("*.json"))
    tally = {}
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        texts = {}
        for s in d["sources"]:
            loc = s.get("url_or_path") or ""
            for tok in re.findall(r"(?<![\w/.:-])(?:data|research|experiments)/[^\s;()|,]+", loc):
                tok = tok.rstrip(".")
                if (ROOT / tok).exists():
                    t = text_for(tok)
                    if t:
                        texts.setdefault(s["id"], []).append(t)
        for p in d["parts"]:
            for r in p.get("radiocarbon") or []:
                src, lab, age = r.get("source"), str(r.get("lab_no") or ""), r.get("age_bp_printed")
                state = "no-text"
                for t in texts.get(src, []):
                    flat = norm(t)
                    labn = norm(lab)
                    idx = [m.start() for m in re.finditer(re.escape(labn), flat)] if labn else []
                    if not idx:
                        state = "absent" if state == "no-text" else state
                        continue
                    state = "lab-only" if state != "ok" else state
                    if age is not None and any(str(age) in flat[i:i + 400] or str(age) in flat[max(0, i - 200):i] for i in idx):
                        state = "ok"
                        break
                tally[state] = tally.get(state, 0) + 1
                if state != "ok":
                    print(f"{f.stem:14s} {src:28s} {lab:18s} {age!s:>6} {state}")
    print("summary:", tally)


if __name__ == "__main__":
    main()
