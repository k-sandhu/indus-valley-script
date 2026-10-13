"""Render labelled contact sheets of every Wells code in the local Lipi font.

The sheets are local-only visual witnesses for base/modifier coding. Codes are
rendered at U+E000 + decimal code, following data/lipi/src/pages/index.vue.

Usage: python -X utf8 render_sheets.py
"""
import collections
import hashlib
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT = ROOT / "data/lipi/src/assets/fonts/indus-font.woff2"
OUT = ROOT / "data/raw/2026-10-12-structure-first/glyph-sheets"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"
CLEAN = ROOT / "data/normalized/lipi_clean_rtl_singleline.jsonl"
PRESERVED_TTF = ROOT / "data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf"


def counts():
    allc = collections.Counter()
    for line in FACES.open(encoding="utf-8"):
        r = json.loads(line)
        allc.update(s for s in r["signs_reading_rtl"] if s not in ("000",))
    seen = set()
    clean = collections.Counter()
    for line in CLEAN.open(encoding="utf-8"):
        r = json.loads(line)
        if not r["clean_rtl_singleline"] or r["has_unknown_sign"]:
            continue
        t = tuple(r["signs_reading_rtl"])
        if t in seen:
            continue
        seen.add(t)
        clean.update(t)
    return allc, clean


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        f = TTFont(FONT)
        f.flavor = None
        ttf = OUT / "lipi-font-local.ttf"
        f.save(ttf)
    except ImportError:
        # This interpreter lacks the WOFF2 Brotli decoder; reuse the 9 October
        # decompression of the same font file, recorded with its hash below.
        ttf = PRESERVED_TTF
        f = TTFont(ttf)
    cmap = f.getBestCmap()
    glyph = ImageFont.truetype(str(ttf), 78)
    label = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 17)
    allc, clean = counts()
    codes = sorted(cp - 0xE000 for cp in cmap if 0xE000 <= cp < 0xE000 + 1000)
    attested = set(allc)
    rows = []
    cols, nrow, cw, ch = 8, 6, 170, 165
    per = cols * nrow
    for start in range(0, len(codes), per):
        batch = codes[start:start + per]
        sheet = Image.new("RGB", (cols * cw, nrow * ch), "white")
        d = ImageDraw.Draw(sheet)
        for k, c in enumerate(batch):
            x, y = (k % cols) * cw, (k // cols) * ch
            box = d.textbbox((0, 0), chr(0xE000 + c), font=glyph)
            gw, gh = box[2] - box[0], box[3] - box[1]
            d.text((x + (cw - gw) / 2 - box[0], y + 28 + (ch - 34 - gh) / 2 - box[1]), chr(0xE000 + c),
                   font=glyph, fill="black")
            tag = f"{c:03d} {clean.get(f'{c:03d}', 0)}/{allc.get(f'{c:03d}', 0)}"
            d.text((x + 6, y + 4), tag, font=label, fill="#b00000" if f"{c:03d}" in attested else "#888888")
            d.rectangle((x, y, x + cw - 1, y + ch - 1), outline="#d0d0d0")
        name = f"sheet-{start // per + 1:02d}-{batch[0]:03d}-{batch[-1]:03d}.png"
        sheet.save(OUT / name)
        rows.append({"sheet": name, "codes": [f"{c:03d}" for c in batch]})
    meta = {
        "font": FONT.relative_to(ROOT).as_posix(),
        "font_sha256": hashlib.sha256(FONT.read_bytes()).hexdigest(),
        "rendered_ttf": ttf.relative_to(ROOT).as_posix(),
        "rendered_ttf_sha256": hashlib.sha256(ttf.read_bytes()).hexdigest(),
        "label_format": "code clean_unique_text_tokens/all_face_tokens",
        "font_codes": len(codes),
        "attested_codes_all_faces": len(attested),
        "sheets": rows,
    }
    (OUT / "index.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("font_codes", "attested_codes_all_faces")}), len(rows), "sheets")


if __name__ == "__main__":
    main()
