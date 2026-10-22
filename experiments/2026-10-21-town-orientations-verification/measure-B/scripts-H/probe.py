"""Reading aid: list dark runs along rows or columns of a plan render.

For each requested row (or column) prints the centres and widths of runs of
pixels darker than the threshold inside the given span. Used to place picks on
dashed or hand-drawn lines; the line fit itself is done by tools/measure_lines.py.
Usage: probe.py <render.png> rows y1 y2 ... --span x0 x1 [--threshold 128]
       probe.py <render.png> cols x1 x2 ... --span y0 y1
"""
import sys
sys.dont_write_bytecode = True
import argparse
import numpy as np
from PIL import Image


def runs(v, thr, off):
    dark = v < thr
    out = []
    i = 0
    while i < len(dark):
        if dark[i]:
            j = i
            while j + 1 < len(dark) and dark[j + 1]:
                j += 1
            out.append(f"{off + (i + j) / 2:.1f}({j - i + 1})")
            i = j + 1
        else:
            i += 1
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("render")
    p.add_argument("mode", choices=["rows", "cols"])
    p.add_argument("idx", type=int, nargs="+")
    p.add_argument("--span", type=int, nargs=2, required=True)
    p.add_argument("--threshold", type=int, default=128)
    a = p.parse_args()
    im = np.asarray(Image.open(a.render).convert("L")).astype(int)
    s0, s1 = a.span
    for k in a.idx:
        v = im[k, s0:s1] if a.mode == "rows" else im[s0:s1, k]
        print(f"{a.mode[:-1]} {k}: " + " ".join(runs(v, a.threshold, s0)))


if __name__ == "__main__":
    main()
