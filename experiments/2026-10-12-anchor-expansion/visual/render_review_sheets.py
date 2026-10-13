"""Build local-only exact-font sheets for a declared visual review inventory."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-12-anchor-expansion/visual'
FONT = ROOT / 'data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf'
INPUT = HERE.parent / 'candidate-starting-pool.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = sorted(json.loads(INPUT.read_text(encoding='utf-8'))['rows'],
                  key=lambda row: int(row['code']))
    RAW.mkdir(parents=True, exist_ok=True)
    glyph_font = ImageFont.truetype(str(FONT), 77)
    label_font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 20)
    sheets = []
    for offset in range(0, len(rows), 50):
        batch = rows[offset:offset + 50]
        sheet = Image.new('RGB', (1500, 1000), 'white')
        drawing = ImageDraw.Draw(sheet)
        for index, row in enumerate(batch):
            x, y = (index % 10) * 150, (index // 10) * 200
            drawing.text((x + 8, y + 5), f"W{row['code']}", font=label_font, fill='black')
            char = chr(0xE000 + int(row['code']))
            box = drawing.textbbox((0, 0), char, font=glyph_font)
            drawing.text((x + (150 - box[2] + box[0]) / 2 - box[0],
                          y + 45 + (145 - box[3] + box[1]) / 2 - box[1]),
                         char, font=glyph_font, fill='black')
            drawing.rectangle((x, y, x + 149, y + 199), outline='#dddddd')
        target = RAW / f'exact-font-sheet-{offset // 50 + 1:02d}.png'
        if target.exists():
            raise FileExistsError(target)
        sheet.save(target)
        sheets.append({'path': target.relative_to(ROOT).as_posix(),
                       'sha256': digest(target), 'codes': [row['code'] for row in batch],
                       'seen': False})
    record = {'scope': 'Local-only exact-font witnesses; no corpus strings.',
              'encoding': 'Lipi index.vue uses U+E000 plus decimal Wells code.',
              'font_path': FONT.relative_to(ROOT).as_posix(), 'font_sha256': digest(FONT),
              'candidate_input_sha256': digest(INPUT), 'rights': 'rights-unverified; local-only',
              'sheet_geometry': [1500, 1000], 'rows': sheets}
    (HERE / 'sheet-manifest-initial.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'sheets': len(sheets), 'codes': len(rows)}))


if __name__ == '__main__':
    main()
