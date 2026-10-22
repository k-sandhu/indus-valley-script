"""Dark runs (blurred image) along columns or rows, to locate textured wall bands.
Usage: bluruns.py <png> row|col <lo> <hi> <idx...> [--thr 170] [--blur 3] [--min 6]"""
import argparse
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
p = argparse.ArgumentParser(); p.add_argument('png'); p.add_argument('mode'); p.add_argument('lo', type=int); p.add_argument('hi', type=int)
p.add_argument('idx', type=int, nargs='+'); p.add_argument('--thr', type=float, default=170); p.add_argument('--blur', type=float, default=3); p.add_argument('--min', type=int, default=6)
a = p.parse_args()
g = ndi.gaussian_filter(np.asarray(Image.open(a.png).convert('L'), float), a.blur)
for i in a.idx:
    v = g[i, a.lo:a.hi] if a.mode == 'row' else g[a.lo:a.hi, i]
    m = v < a.thr; runs = []; s = None
    for k, b in enumerate(m):
        if b and s is None: s = k
        if not b and s is not None:
            if k - s >= a.min: runs.append((s + a.lo, k - 1 + a.lo))
            s = None
    if s is not None and len(m) - s >= a.min: runs.append((s + a.lo, len(m) - 1 + a.lo))
    print(a.mode, i, runs)
