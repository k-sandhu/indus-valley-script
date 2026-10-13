"""Place CISI catalogue keys on the pages of the CISI 1 and CISI 2 scans.

Usage (from the repository root):
    python -P experiments/2026-10-13-image-index-and-units/page_index.py --out experiments/2026-10-13-image-index-and-units/run-2026-10-13/pages

Reads the page text saved by cisi_pages.py (local): tesseract output for CISI 1 PDF pages
1-431 and CISI 2 PDF pages 1-486, plus the CISI 2 text layer. For each page it finds the
running heading's catalogue range (for example 'LOTHAL 97-100') and the caption keys
followed by a side letter (for example 'L-98 A') on the plate pages. A key is placed on a page when its
caption is read there, or when its number lies inside the heading range of a page whose
captions carry the same prefix. The printed page number is the PDF page minus the
volume's modal offset between PDF page and the page numbers read on plate pages.

Outputs (identifiers and page locators only): pages.csv and key-pages.csv.
"""
import argparse
import collections
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-13-image-index-and-units/cisi-pages"

CAP = re.compile(r"(?<![A-Za-z])([A-Z][a-z]{0,3}|[A-Z]{1,2}|\?)\s?-\s?(\d{1,4})\s?(?:\(\d\)\s?)?([A-Ga-g])(?![A-Za-z])")
HEAD = re.compile(r"([A-Z][A-Z\- ]{2,}[A-Z])\s*(\d{1,4})\s*[-–—]\s*(\d{1,4})")
LONE = re.compile(r"^\s*(\d{1,3})\s*\|?\s*$", re.M)
# Plate pages: from printed page 1 to the page before the basic-data tables, whose
# headings carry the word DATA (CISI 1 PDF 401-411, CISI 2 PDF 469-482).
PLATES = {1: (37, 400), 2: (36, 468)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out = out if out.is_absolute() else ROOT / out
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    pages = []
    for vol in (1, 2):
        fp = RAW / f"cisi{vol}-pages.jsonl"
        for line in fp.open(encoding="utf-8"):
            r = json.loads(line)
            text = r["ocr"] + "\n" + r.get("text_layer", "")
            caps = collections.Counter()
            for p, n, side in CAP.findall(text):
                caps[(p, int(n))] += 1
            heads = []
            for site, n1, n2 in HEAD.findall(text):
                n1, n2 = int(n1), int(n2)
                if 0 < n1 <= n2 and n2 - n1 <= 60:
                    heads.append((site.strip(), n1, n2))
            prefixes = collections.Counter(p for (p, n) in caps.elements())
            lone = [int(x) for x in LONE.findall(r["ocr"])]
            pages.append({"volume": vol, "pdf_page": r["pdf_page"], "caps": caps, "heads": heads,
                          "dominant_prefix": prefixes.most_common(1)[0][0] if prefixes else "", "lone_numbers": lone})

    # modal offset between PDF page and printed page number per volume
    offsets = {}
    for vol in (1, 2):
        c = collections.Counter()
        for p in pages:
            if p["volume"] == vol:
                for n in p["lone_numbers"]:
                    d = p["pdf_page"] - n
                    if 0 <= d <= 60:
                        c[d] += 1
        offsets[vol] = c.most_common(1)[0][0] if c else None

    key_pages = collections.defaultdict(dict)
    for p in pages:
        lo, hi = PLATES[p["volume"]]
        if not lo <= p["pdf_page"] <= hi:
            continue
        loc = (p["volume"], p["pdf_page"])
        for (pfx, n), cnt in p["caps"].items():
            key_pages[f"{pfx}-{n}"].setdefault(loc, set()).add("caption")
        if p["dominant_prefix"]:
            for site, n1, n2 in p["heads"]:
                # accept the heading range only if a caption key on the page falls inside it
                inside = [n for (pfx, n) in p["caps"] if pfx == p["dominant_prefix"] and n1 <= n <= n2]
                if inside:
                    for n in range(n1, n2 + 1):
                        key_pages[f"{p['dominant_prefix']}-{n}"].setdefault(loc, set()).add("heading-range")

    out.mkdir(parents=True)
    with (out / "pages.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["volume", "pdf_page", "printed_page", "heading_site", "heading_range", "dominant_caption_prefix", "caption_keys_read"])
        for p in pages:
            off = offsets[p["volume"]]
            h = p["heads"][0] if p["heads"] else ("", "", "")
            w.writerow([p["volume"], p["pdf_page"], p["pdf_page"] - off if off is not None else "", h[0],
                        f"{h[1]}-{h[2]}" if h[1] != "" else "", p["dominant_prefix"], sum(p["caps"].values())])
    rows = []
    for key, locs in key_pages.items():
        # prefer pages where both the caption and the heading range place the key, then caption only
        ranked = sorted(locs.items(), key=lambda kv: (-len(kv[1]), -("caption" in kv[1]), kv[0]))
        (vol, pg), basis = ranked[0]
        rows.append({"key": key, "volume": vol, "pdf_page": pg, "printed_page": pg - offsets[vol] if offsets[vol] is not None else "",
                     "basis": "+".join(sorted(basis)), "other_pages": ";".join(f"{v}:{p}" for (v, p), _ in ranked[1:])})
    rows.sort(key=lambda r: (r["key"].split("-")[0], int(r["key"].split("-")[1])))
    with (out / "key-pages.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    summary = {"pages": len(pages), "offsets_pdf_minus_printed": offsets,
               "keys_placed": len(rows), "basis": dict(collections.Counter(r["basis"] for r in rows)),
               "keys_with_other_pages": sum(1 for r in rows if r["other_pages"])}
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
