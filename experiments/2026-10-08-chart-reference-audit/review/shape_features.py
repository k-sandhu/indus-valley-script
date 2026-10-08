"""Per-digit pixel check of the reviewer's 63 independently read cells.

For every digit of the class number and code of each cell in review/independent-readings.json this script records the
best template matches (templates built from the other cells' digits that were clear by eye, so a cell never
contributes to its own templates), the width of the top stroke as a fraction of the digit width and the fill of the
top-left corner. A flat-topped 5 in this typeface has a top stroke 85-96% of the digit width and a filled corner; a 6
has a rounded top (about 40-60%) and an empty corner. It also draws review/disputed-digits.png.

Run from the repository root:  python experiments/2026-10-08-chart-reference-audit/review/shape_features.py
Output: experiments/2026-10-08-chart-reference-audit/review/shape-features-63-cells.json
"""
import json
import os
import sys
from collections import defaultdict

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixel_check as pc

PK = 'experiments/2026-10-08-chart-reference-audit/'
man = json.load(open(pc.MANIFEST, encoding='utf-8'))
geo = {c['cell']: c['clip_pdf_points'] for c in man['cells']}
rd = json.load(open(PK + 'review/independent-readings.json', encoding='utf-8'))
bits_of = lambda cell: pc.page_bits(int(cell[1:3]))


def crop(img):
    r = np.where(img.any(axis=1))[0]
    c = np.where(img.any(axis=0))[0]
    return img[r.min():r.max() + 1, c.min():c.max() + 1]


def top_features(img):
    im = crop(img)
    H, W = im.shape
    top = im[:max(3, H // 12)]
    cols = np.where(top.any(axis=0))[0]
    top_w = (cols.max() - cols.min() + 1) / W
    corner = im[:max(2, int(.12 * H)), :max(2, int(.20 * W))].mean()
    return round(float(top_w), 2), round(float(corner), 2)


records = []
for c in rd['cells']:
    dl = pc.cell_digits(bits_of(c['cell']), geo[c['cell']])
    for li, (line, txt) in enumerate(((dl[0], str(c['class_number'])), (dl[1], str(c['code'])))):
        if len(line) != len(txt):
            records.append(dict(cell=c['cell'], line='class' if li == 0 else 'code', segmentation_mismatch=True, expected=txt, found=len(line)))
            continue
        for k, (d, ch) in enumerate(zip(line, txt)):
            records.append(dict(cell=c['cell'], line='class' if li == 0 else 'code', index=k, final_label=ch, thin=bool(d['w'] / d['h'] < 0.45),
                                img=d['img'], a=None if d['w'] / d['h'] < 0.45 else pc.norm(d['img']),
                                eye_unchanged=not c['changed_after_pixel_check'], confidence=c['confidence']))

# templates from digits of cells read with high or medium-high confidence and unchanged by the pixel check, leaving the target cell out
lib = defaultdict(lambda: defaultdict(list))
for r in records:
    if 'a' in r and r['a'] is not None and r['eye_unchanged'] and r['confidence'] in ('high', 'medium-high'):
        lib[r['cell']][r['final_label']].append(r['a'])
cells = sorted({r['cell'] for r in records})
out, disagree = [], []
for r in records:
    if r.get('segmentation_mismatch'):
        out.append(r)
        continue
    if r['thin']:
        out.append(dict(cell=r['cell'], line=r['line'], index=r['index'], final_label=r['final_label'], thin_stroke=True, template_label='1', agree=r['final_label'] == '1'))
        continue
    pools = defaultdict(list)
    for cell, d in lib.items():
        if cell != r['cell']:
            for ch, arrs in d.items():
                pools[ch].extend(arrs)
    scores = {ch: pc.corr(r['a'], np.mean(v, axis=0)) for ch, v in pools.items() if v}
    order = sorted(scores, key=lambda k: -scores[k])
    tw, cf = top_features(r['img'])
    rec = dict(cell=r['cell'], line=r['line'], index=r['index'], final_label=r['final_label'], template_label=order[0],
               top3=[(k, round(scores[k], 3)) for k in order[:3]], top_stroke_width_fraction=tw, top_left_corner_fill=cf, agree=order[0] == r['final_label'])
    out.append(rec)
    if not rec['agree']:
        disagree.append(rec)
n = sum(1 for x in out if 'agree' in x)
summary = dict(digits=n, agree=sum(1 for x in out if x.get('agree')), disagree=len(disagree), segmentation_mismatches=sum(1 for x in out if x.get('segmentation_mismatch')))
fives = [x for x in out if x.get('final_label') == '5' and 'top_stroke_width_fraction' in x and x['top3'][0][1] > 0.8]
sixes = [x for x in out if x.get('final_label') == '6' and 'top_stroke_width_fraction' in x and x['top3'][0][1] > 0.85]
summary['clear_5_top_stroke_range'] = [min(x['top_stroke_width_fraction'] for x in fives), max(x['top_stroke_width_fraction'] for x in fives), len(fives)]
summary['clear_6_top_stroke_range'] = [min(x['top_stroke_width_fraction'] for x in sixes), max(x['top_stroke_width_fraction'] for x in sixes), len(sixes)]
json.dump(dict(status='Exploratory reviewer pixel check', summary=summary, disagreements=disagree, digits=out), open(PK + 'review/shape-features-63-cells.json', 'w'), indent=1)
print(json.dumps(summary))
for d in disagree:
    print(d['cell'], d['line'], d['index'], 'final', d['final_label'], 'template', d['top3'])

# figure of disputed digits beside clear examples
want = [('p20_c4_r13', 'code', 1, 'p20_c4_r13 code d2'), ('p21_c1_r19', 'code', 1, 'p21_c1_r19 code d2 (350)'), ('p20_c8_r19', 'code', 1, 'clear 5 (455)'),
        ('p21_c3_r5', 'code', 2, 'clear 6 (396)'), ('p21_c6_r1', 'code', 2, 'p21_c6_r1 code d3'), ('p20_c4_r21', 'code', 1, 'clear 8 (486)'),
        ('p20_c3_r33', 'class', 1, 'p20_c3_r33 class d2'), ('p20_c3_r32', 'class', 1, 'p20_c3_r32 class d2')]
tiles = []
for cell, line, idx, label in want:
    dl = pc.cell_digits(bits_of(cell), geo[cell])
    img = dl[0 if line == 'class' else 1][idx]['img']
    t = Image.new('L', (34, 46), 255)
    a = np.where(img, 0, 255).astype(np.uint8)
    t.paste(Image.fromarray(a), ((34 - a.shape[1]) // 2, (46 - a.shape[0]) // 2))
    t = t.resize((34 * 5, 46 * 5), Image.NEAREST).convert('RGB')
    ImageDraw.Draw(t).text((3, 3), label, fill=(200, 0, 0))
    tiles.append(t)
tw_, th_ = tiles[0].size
fig = Image.new('RGB', (len(tiles) * (tw_ + 6), th_), (255, 255, 255))
for i, t in enumerate(tiles):
    fig.paste(t, (i * (tw_ + 6), 0))
fig.save(PK + 'review/disputed-digits.png')
