"""Reading aid: trace the two outer outlines of a wall drawn as a band of outlined bricks.

From an approximate centreline (x0 y0 x1 y1, render pixels) it samples
perpendicular profiles every 4 px, takes on each side the outermost dark pixel
of the band (dark < threshold, stopping at a light gap longer than `gap`),
fits a straight line by total least squares with one 2-sigma rejection pass
and prints the page bearing, RMS and the projected end points. These end
points seed edge picks; the recorded fit is always made by tools/measure_lines.py.
Usage: outline.py <render.png> name x0 y0 x1 y1 [name x0 y0 x1 y1 ...] [--reach 40] [--gap 6] [--threshold 150]
"""
import sys
sys.dont_write_bytecode = True
import argparse
import numpy as np
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument("render")
    p.add_argument("items", nargs="+")
    p.add_argument("--reach", type=int, default=40)
    p.add_argument("--gap", type=int, default=6)
    p.add_argument("--threshold", type=int, default=150)
    a = p.parse_args()
    im = np.asarray(Image.open(a.render).convert("L")).astype(float)
    it = a.items
    for k in range(0, len(it), 5):
        name = it[k]
        x0, y0, x1, y1 = map(float, it[k + 1:k + 5])
        s, e = np.array([x0, y0]), np.array([x1, y1])
        L = np.linalg.norm(e - s)
        d = (e - s) / L
        n = np.array([-d[1], d[0]])
        for side in (1, -1):
            pts = []
            for t in np.arange(8, L - 8, 4):
                c = s + d * t
                prof = []
                for r in range(a.reach):
                    q = c + n * r * side
                    xi, yi = int(round(q[0])), int(round(q[1]))
                    if 0 <= yi < im.shape[0] and 0 <= xi < im.shape[1]:
                        prof.append(im[yi, xi])
                    else:
                        prof.append(255)
                dark = np.nonzero(np.array(prof) < a.threshold)[0]
                if len(dark) == 0:
                    continue
                last = dark[0]
                for i in dark[1:]:
                    if i - last > a.gap:
                        break
                    last = i
                pts.append(c + n * side * last)
            if len(pts) < 5:
                print(name, side, "too few points")
                continue
            P = np.array(pts)
            for _ in range(2):
                cen = P.mean(0)
                v = np.linalg.svd(P - cen)[2][0]
                res = (P - cen) @ np.array([-v[1], v[0]])
                keep = np.abs(res) <= 2 * res.std() + 0.5
                P = P[keep]
            cen = P.mean(0)
            v = np.linalg.svd(P - cen)[2][0]
            res = (P - cen) @ np.array([-v[1], v[0]])
            ang = np.degrees(np.arctan2(v[0], -v[1])) % 180
            p0 = cen + v * ((s - cen) @ v)
            p1 = cen + v * ((e - cen) @ v)
            print(f"{name} side {side:+d}: page bearing {ang:.2f} rms {res.std():.2f} n {len(P)} ends [[{p0[0]:.1f},{p0[1]:.1f}],[{p1[0]:.1f},{p1[1]:.1f}]]")


if __name__ == "__main__":
    main()
