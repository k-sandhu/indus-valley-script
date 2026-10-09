"""Draw the reviewer's seeded sample of readings and render figure sheets into the local raw directory.

Sheets (page crops of the third-party PDF beside Table 18 crops) stay under data/raw/.../reviewer-pdf-tmp/sheets.
From the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/sample_readings.py
"""
import collections, json, random
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
W = RAW / 'pdf-2026-10-09-v1'
TMP = RAW / 'reviewer-pdf-tmp'
(TMP / 'sheets').mkdir(parents=True, exist_ok=True)
inv = {r['reading_id']: r for r in json.loads((W / 'reading-inventory-v4.json').read_text(encoding='utf-8'))}
sel = {r['reading_id']: r for r in json.loads((W / 'lexical-selection-v2.json').read_text(encoding='utf-8'))['readings']}
att = [r for r in inv.values() if r['is_reading_attempt']]
cap = [r for r in att if r['reading_id'] in sel and sel[r['reading_id']]['basis'].startswith('explicit caption')]
other_sel = [r for r in att if r['reading_id'] in sel and not sel[r['reading_id']]['basis'].startswith('explicit caption')]
unsel = [r for r in att if r['reading_id'] not in sel]
rng = random.Random(20261009 + 7)
sample = rng.sample(cap, 16) + rng.sample(other_sel, 4) + rng.sample(unsel, 8)
sample.append(rng.choice([r for r in att if r['source_kind'].startswith('Table 21')]))
sample.append(rng.choice([r for r in att if r['unclear_or_unattested_flag']]))
ids = [r['reading_id'] for r in sample]
(TMP / 'sample-ids.json').write_text(json.dumps(ids), encoding='utf-8')

cat = {r['sign_id']: r for r in json.loads((W / 'sign-catalogue-v2.json').read_text(encoding='utf-8'))}
doc = fitz.open(RAW / 'papers/A_Partial_Decipherment_of_the_Indus_Vall.pdf')
font = ImageFont.load_default()


def sheet(rid):
    r = inv[rid]
    pg = doc[r['source_page'] - 1]
    gl = r['primary_glyphs']
    if gl:
        y0 = min(g['bbox'][1] for g in gl); y1 = max(g['bbox'][3] for g in gl)
    else:
        y0, y1 = r['primary_bbox'][1], r['primary_bbox'][3]
    y0 = min(y0, r['primary_bbox'][1])
    clip = fitz.Rect(40, max(0, y0 - 10), pg.rect.width - 30, min(pg.rect.height, y1 + 75))
    pix = pg.get_pixmap(matrix=fitz.Matrix(2.6, 2.6), clip=clip)
    img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    crops = []
    for s in r['sign_sequence_visual_ltr']:
        if s in cat and cat[s].get('crop_path'):
            c = Image.open(ROOT / cat[s]['crop_path']).convert('RGB'); c.thumbnail((70, 70)); crops.append((s, c))
    out = Image.new('RGB', (max(img.width, 60 + 80 * len(crops)), img.height + (100 if crops else 20) + 22), 'white')
    d = ImageDraw.Draw(out)
    d.text((4, 2), f"{rid} p{r['source_page']} {r['primary_label']} seq={r['sign_sequence_visual_ltr']} reading={r['proposed_reading']}", fill='red', font=font)
    out.paste(img, (0, 16))
    for k, (s, c) in enumerate(crops):
        out.paste(c, (4 + 80 * k, img.height + 20)); d.text((4 + 80 * k, img.height + 92), f"{s} {cat[s].get('label', '')}", fill='blue', font=font)
    return out


for i in range(0, len(ids), 3):
    ims = [sheet(x) for x in ids[i:i + 3]]
    S = Image.new('RGB', (max(im.width for im in ims), sum(im.height for im in ims) + 10 * len(ims)), 'white')
    y = 0
    for im in ims:
        S.paste(im, (0, y)); y += im.height + 10
    S.save(TMP / 'sheets' / f'sheet-{i // 3 + 1:02d}.png')
print(len(ids), ids)
