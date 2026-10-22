"""Print dark-ink runs along rows (or columns) of a rendered plan PNG, to locate wall faces.

Usage: runs.py <png> row|col <from> <to> <index...> [--thr 110]
  row: for each y in index list, runs of dark pixels with x in [from, to]
  col: for each x in index list, runs of dark pixels with y in [from, to]
"""
import argparse
import numpy as np
from PIL import Image

p = argparse.ArgumentParser()
p.add_argument('png'); p.add_argument('mode', choices=['row', 'col'])
p.add_argument('lo', type=int); p.add_argument('hi', type=int)
p.add_argument('idx', type=int, nargs='+')
p.add_argument('--thr', type=float, default=110)
a = p.parse_args()
im = np.asarray(Image.open(a.png).convert('L'), float)
for i in a.idx:
    v = im[i, a.lo:a.hi] if a.mode == 'row' else im[a.lo:a.hi, i]
    d = np.where(v < a.thr)[0] + a.lo
    runs = []
    if len(d):
        s = q = d[0]
        for x in d[1:]:
            if x != q + 1:
                runs.append((int(s), int(q))); s = x
            q = x
        runs.append((int(s), int(q)))
    print(a.mode, i, [r for r in runs if r[1] - r[0] >= 1])
