"""Reviewer check 2: draw an independent sample of catalogue IDs and render the PDF entries for visual comparison.

Sample frame: all IDs 1-2058 except the 60 IDs the package audited. Seeded simple random sample, plus a short
list of targeted IDs that earlier scans flagged (kept out of the error-rate calculation).
Images and per-row comparison sheets are written to the local raw directory (third-party page images).
Run from the repository root:
    python -B -X utf8 experiments/2026-10-06-weight-metrology/review/render_audit.py --n 36
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / 'experiments/2026-10-06-weight-metrology'
RAW = ROOT / 'data/raw/2026-10-06-weight-metrology'
OUT = RAW / 'review-tmp/audit-renders'
SOURCE = ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf'
START = re.compile(r'^(\d{1,4})\.?\s+(Susa|Choga|Djaffarabad|Tell|Telloh|Ancient|Jiroft|Konar|Tepe|Shahr|Mindasht|Rakhigarhi|Farmana|Kuntasi|Nageshwar|Nagwada|Shikarpur|Bagasra|Dholavira|Baluchistan|Unknown)')


def crops_for(doc, row):
    cat = row['cat']
    start_re = re.compile(r'^' + str(cat) + r'\.?\s+' + re.escape(row['site_literal'].split(' /')[0]))
    tiles = []
    first = True
    active = False
    for pn in row['source_pdf_pages']:
        page = doc[pn - 1]
        W = page.rect.width
        segs = {0: [], 1: []}
        started_here = False
        for block in page.get_text('dict')['blocks']:
            if block['type'] != 0:
                continue
            for line in block['lines']:
                txt = ''.join(s['text'] for s in line['spans'])
                if start_re.match(txt) and first:
                    active = True; first = False
                elif active and (START.match(txt) or re.match(r'[456]\.\d+(?:\.\d+)+\.', txt)) and not start_re.match(txt):
                    active = False
                if active:
                    col = 0 if line['bbox'][0] < W / 2 - 5 else 1
                    segs[col].append(fitz.Rect(line['bbox']))
        if not first or any(segs.values()):
            pass
        for col, rects in segs.items():
            if not rects:
                continue
            r = rects[0]
            for b in rects[1:]:
                r |= b
            r += (-6, -6, 6, 6)
            pix = page.get_pixmap(matrix=fitz.Matrix(3.2, 3.2), clip=r)
            im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            tiles.append(im)
    return tiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=36)
    ap.add_argument('--seed', type=int, default=20261011)
    ap.add_argument('--targeted', default='82,1201,1730,1503,1212,1400')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = json.loads((RAW / 'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    frame = json.loads((RAW / 'extraction-v3/validation-renders/sample-frame.json').read_text(encoding='utf-8'))
    audited = set(frame['sample_ids'])
    pool = [i for i in range(1, 2059) if i not in audited]
    sample = sorted(random.Random(args.seed).sample(pool, args.n))
    targeted = [int(x) for x in args.targeted.split(',') if x]
    doc = fitz.open(SOURCE)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
    manifest = {'seed': args.seed, 'n_random': args.n, 'random_ids': sample, 'targeted_ids': targeted,
                'excluded_package_ids': sorted(audited)}
    (RAW / 'review-tmp/audit-sample.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    allids = sample + [t for t in targeted if t not in sample]
    for cat in allids:
        row = rows[cat - 1]
        tiles = crops_for(doc, row)
        w = max([t.width for t in tiles] + [900])
        h = 36 + sum(t.height + 8 for t in tiles)
        sheet = Image.new('RGB', (w, h), 'white')
        d = ImageDraw.Draw(sheet)
        d.text((4, 4), f'Cat. {cat}  PDF {row["source_pdf_pages"]}  printed {row["source_printed_pages"]}', fill='black', font=font)
        y = 36
        for t in tiles:
            sheet.paste(t, (0, y)); y += t.height + 8
        sheet.save(OUT / f'cat-{cat:04}.png')
    print(json.dumps(manifest))


if __name__ == '__main__':
    main()
