"""Working aid: draw the dark line work of a plan render over an imagery render.

The plan is placed with a similarity given by a plan anchor pixel, the UTM point
it should fall on, metres per plan pixel and the page bearing of north on the plan
(degrees clockwise from page-up). This is a visual identification aid only; it
does not measure anything and is not a registration.

Usage: overlay.py <plan.png> <render.png> <out.png> --anchor-plan x y --anchor-utm E N
       --mpp m --north-page-bearing deg [--threshold 100] [--plan-region x0 y0 x1 y1]
"""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument("plan")
    p.add_argument("render")
    p.add_argument("out")
    p.add_argument("--anchor-plan", type=float, nargs=2, required=True)
    p.add_argument("--anchor-utm", type=float, nargs=2, required=True)
    p.add_argument("--mpp", type=float, required=True)
    p.add_argument("--north-page-bearing", type=float, required=True)
    p.add_argument("--threshold", type=int, default=100)
    p.add_argument("--plan-region", type=int, nargs=4)
    p.add_argument("--color", type=int, nargs=3, default=[255, 0, 0])
    a = p.parse_args()
    if Path(a.out).exists():
        raise FileExistsError(a.out)
    side = json.loads(Path(a.render + ".json").read_text(encoding="utf-8"))
    inv = np.linalg.inv(np.asarray(side["pixel_to_utm"], float))
    plan = np.asarray(Image.open(a.plan).convert("L"))
    ys, xs = np.nonzero(plan < a.threshold)
    if a.plan_region:
        x0, y0, x1, y1 = a.plan_region
        keep = (xs >= x0) & (xs < x1) & (ys >= y0) & (ys < y1)
        xs, ys = xs[keep], ys[keep]
    dx = xs - a.anchor_plan[0]
    dy = ys - a.anchor_plan[1]
    r = np.hypot(dx, dy) * a.mpp
    beta = np.degrees(np.arctan2(dx, -dy)) - a.north_page_bearing
    e = a.anchor_utm[0] + r * np.sin(np.radians(beta))
    n = a.anchor_utm[1] + r * np.cos(np.radians(beta))
    px = inv @ np.vstack([e, n, np.ones_like(e)])
    img = np.asarray(Image.open(a.render).convert("RGB")).copy()
    cx = np.round(px[0]).astype(int)
    cy = np.round(px[1]).astype(int)
    ok = (cx >= 0) & (cx < img.shape[1]) & (cy >= 0) & (cy < img.shape[0])
    img[cy[ok], cx[ok]] = a.color
    Image.fromarray(img).save(a.out)
    print(a.out, int(ok.sum()), "plan pixels drawn")


if __name__ == "__main__":
    main()
