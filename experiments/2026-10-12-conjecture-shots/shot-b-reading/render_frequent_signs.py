"""Render the signs with at least ten discovery tokens from the local Lipi font.

Local-only visual witness: writes PNG sheets under data/raw/.../shot-b-reading/glyphs/.
Each cell is labelled with the code and its discovery token count. Codes are rendered at
U+E000 + decimal code, as in the structure-first glyph sheets.
"""
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common_b import DISC, RAW, ROOT

TTF = ROOT / "data/raw/2026-10-12-structure-first/glyph-sheets/lipi-font-local.ttf"
if not TTF.exists():
    TTF = ROOT / "data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf"
OUT = RAW / "glyphs"
OUT.mkdir(parents=True, exist_ok=True)

rows = list(csv.DictReader(open(DISC / "sign_profile.tsv", encoding="utf-8"), delimiter="\t"))
signs = [(r["code"], int(r["tokens"])) for r in rows if int(r["tokens"]) >= 10]
glyph = ImageFont.truetype(str(TTF), 70)
label = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
cols, nrow, cw, ch = 8, 4, 150, 140
per = cols * nrow
for start in range(0, len(signs), per):
    batch = signs[start:start + per]
    sheet = Image.new("RGB", (cols * cw, nrow * ch), "white")
    d = ImageDraw.Draw(sheet)
    for k, (c, n) in enumerate(batch):
        x, y = (k % cols) * cw, (k // cols) * ch
        ch_ = chr(0xE000 + int(c))
        box = d.textbbox((0, 0), ch_, font=glyph)
        gw, gh = box[2] - box[0], box[3] - box[1]
        d.text((x + (cw - gw) / 2 - box[0], y + 26 + (ch - 30 - gh) / 2 - box[1]), ch_, font=glyph, fill="black")
        d.text((x + 5, y + 3), f"{c} n={n}", font=label, fill="#b00000")
        d.rectangle((x, y, x + cw - 1, y + ch - 1), outline="#d0d0d0")
    sheet.save(OUT / f"frequent-{start // per + 1:02d}.png")
print(len(signs), "signs rendered to", OUT)
