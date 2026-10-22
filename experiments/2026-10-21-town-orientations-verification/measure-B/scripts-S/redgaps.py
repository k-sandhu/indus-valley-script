"""Report non-red gaps (streets) inside red-filled excavation areas along rows or columns of a colour plan render.
Usage: redgaps.py <png> row|col <lo> <hi> <start> <stop> <step> [--diff 40] [--min 2]"""
import argparse
import numpy as np
from PIL import Image
p = argparse.ArgumentParser()
p.add_argument('png'); p.add_argument('mode', choices=['row', 'col'])
p.add_argument('lo', type=int); p.add_argument('hi', type=int)
p.add_argument('start', type=int); p.add_argument('stop', type=int); p.add_argument('step', type=int)
p.add_argument('--diff', type=float, default=40); p.add_argument('--min', type=int, default=2)
a = p.parse_args()
im = np.asarray(Image.open(a.png).convert('RGB'), float)
red = (im[..., 0] - im[..., 1]) > a.diff
for i in range(a.start, a.stop + 1, a.step):
    v = red[i, a.lo:a.hi] if a.mode == 'row' else red[a.lo:a.hi, i]
    idx = np.where(v)[0]
    if not len(idx):
        print(a.mode, i, 'none'); continue
    gaps = []; s = None
    for k in range(idx.min(), idx.max() + 1):
        if not v[k]:
            if s is None: s = k
        elif s is not None:
            if k - s >= a.min: gaps.append((s + a.lo, k - 1 + a.lo))
            s = None
    print(a.mode, i, (int(idx.min() + a.lo), int(idx.max() + a.lo)), gaps)
