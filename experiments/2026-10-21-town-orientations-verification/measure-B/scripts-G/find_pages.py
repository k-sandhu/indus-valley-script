"""Find pages that mention given names in a pages.json or PDF, without showing orientation text.

Lines matching orientation wording or degree figures are never printed; the
page is flagged instead.  For each hit page we print the count of hits and up
to three short context lines that contain 'fig', 'pl', 'plan' or the name.

Usage: python -I find_pages.py <pages.json|file.pdf> name [name ...]
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ORIENT = re.compile(r"orient|\d\s*[°º]|\d\s*deg|\bdegree|north|south|east|west|cardinal|true\s+n|magnetic", re.I)


def pages_of(path):
    p = Path(path)
    if p.suffix.lower() == ".json":
        for row in json.loads(p.read_text(encoding="utf-8")):
            yield row["pdf_page"], row.get("text", "")
    else:
        import fitz
        with fitz.open(path) as d:
            for i, pg in enumerate(d):
                yield i + 1, pg.get_text()


def main():
    path, names = sys.argv[1], sys.argv[2:]
    pat = re.compile("|".join(re.escape(n) for n in names), re.I)
    for n, text in pages_of(path):
        hits = len(pat.findall(text))
        if not hits:
            continue
        flagged = False
        ctx = []
        for line in text.splitlines():
            if ORIENT.search(line):
                flagged = True
                continue
            if (pat.search(line) or re.search(r"\bfig|\bpl\.|\bplan\b", line, re.I)) and len(ctx) < 3:
                ctx.append(line.strip()[:110])
        print(f"PDF {n}: {hits} hits{' [orientation-like lines withheld]' if flagged else ''}")
        for c in ctx:
            print("     ", c)


if __name__ == "__main__":
    main()
