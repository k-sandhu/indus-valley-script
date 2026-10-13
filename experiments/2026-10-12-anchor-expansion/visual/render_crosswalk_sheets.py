"""Pair local exact-font witnesses with earlier licensed class pointers."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-12-anchor-expansion/visual'
FONT = ROOT / 'data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = json.loads((HERE.parent / 'candidate-starting-pool.json').read_text(encoding='utf-8'))['rows']
    rows = sorted([row for row in rows if row['drawings']], key=lambda row: int(row['code']))
    label = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 19)
    glyph = ImageFont.truetype(str(FONT), 65)
    sheets = []
    for offset in range(0, len(rows), 36):
        batch = rows[offset:offset + 36]
        image = Image.new('RGB', (1500, 1080), 'white')
        draw = ImageDraw.Draw(image)
        witnesses = []
        for index, row in enumerate(batch):
            x, y = (index % 6) * 250, (index // 6) * 180
            drawing = row['drawings'][0]
            draw.text((x + 6, y + 3), f"W{row['code']} / {drawing['graphic_class']}", font=label, fill='black')
            char = chr(0xE000 + int(row['code']))
            box = draw.textbbox((0, 0), char, font=glyph)
            draw.text((x + (110 - box[2] + box[0]) / 2 - box[0],
                       y + 40 + (120 - box[3] + box[1]) / 2 - box[1]),
                      char, font=glyph, fill='black')
            source = ROOT / drawing['path']
            original = Image.open(source)
            rect = (90, 15, min(209, original.width), min(120, original.height))
            cropped = original.crop(rect)
            cropped.thumbnail((127, 120))
            image.paste(cropped, (x + 119, y + 40))
            draw.line((x + 114, y + 30, x + 114, y + 174), fill='#cccccc')
            draw.rectangle((x, y, x + 249, y + 179), outline='#999999')
            witnesses.append({'code': row['code'], 'class': drawing['graphic_class'],
                              'source': drawing['path'], 'source_sha256': sha(source),
                              'chart_rectangle': list(rect)})
        target = RAW / f'paired-crosswalk-sheet-{offset // 36 + 1:02d}.png'
        if target.exists():
            raise FileExistsError(target)
        image.save(target)
        sheets.append({'path': target.relative_to(ROOT).as_posix(), 'sha256': sha(target),
                       'seen': False, 'witnesses': witnesses})
    target = HERE / 'crosswalk-sheet-manifest-initial.json'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(json.dumps({'font_sha256': sha(FONT), 'mapped_codes': len(rows),
      'reading': 'Left: exact font code. Right: licensed earlier mapped chart class. Font pairings remain local-only.',
      'chart_license': 'CC BY 4.0; Koskenniemi and Parpola (1979), University of Helsinki edition.',
      'rows': sheets}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'mapped_codes': len(rows), 'sheets': len(sheets)}))


if __name__ == '__main__':
    main()
