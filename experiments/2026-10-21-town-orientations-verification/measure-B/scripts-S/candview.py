"""Draw wall candidates (from wallcands.py) over a crop of the render, enlarged, for review.
Usage: candview.py <render.png> <cands.json> <out.png> x0 y0 x1 y1 [--zoom 2] [--only c00,c01]"""
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw
p = argparse.ArgumentParser(); p.add_argument('png'); p.add_argument('cands'); p.add_argument('out')
p.add_argument('box', type=int, nargs=4); p.add_argument('--zoom', type=int, default=2); p.add_argument('--only')
a = p.parse_args()
if Path(a.out).exists(): raise SystemExit('exists')
x0, y0, x1, y1 = a.box; z = a.zoom
im = Image.open(a.png).convert('RGB').crop((x0, y0, x1, y1)); im = im.resize((im.width * z, im.height * z), Image.Resampling.NEAREST)
d = ImageDraw.Draw(im)
only = set(a.only.split(',')) if a.only else None
for c in json.loads(Path(a.cands).read_text(encoding='utf-8'))['candidates']:
    if only and c['cand'] not in only: continue
    q0 = ((c['p0'][0] - x0 + .5) * z, (c['p0'][1] - y0 + .5) * z); q1 = ((c['p1'][0] - x0 + .5) * z, (c['p1'][1] - y0 + .5) * z)
    if not (-50 < q0[0] < im.width + 50 and -50 < q0[1] < im.height + 50): continue
    d.line([q0, q1], fill=(255, 0, 0), width=1)
    d.text(((q0[0] + q1[0]) / 2 + 4, (q0[1] + q1[1]) / 2 - 6), c['cand'], fill=(0, 0, 255), stroke_width=2, stroke_fill='white')
im.save(a.out); print(a.out)
