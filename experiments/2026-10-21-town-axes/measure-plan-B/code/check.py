"""Draw hand picks (green) and their refined fits (red) on a crop of a rendered plan.

Usage:
  python .../code/check.py IMAGE X0 Y0 X1 Y1 SCALE OUTNAME "label:x1,y1,x2,y2[,band[,mode]]" (mode 1 = Canny edges, else ink) ...

Prints each fit (page azimuth, RMS, pixel count, shift from the pick) and writes the crop
to data/raw/2026-10-21-town-axes/plan-B/crops/OUTNAME.png.
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refine as R  # noqa: E402

Image.MAX_IMAGE_PIXELS = None


def main():
    img = sys.argv[1]
    x0, y0, x1, y1 = map(int, sys.argv[2:6])
    sc = float(sys.argv[6])
    name = sys.argv[7]
    g = R.load_gray(img)
    im = Image.open(img).convert("RGB").crop((x0, y0, x1, y1))
    im = im.resize((int(im.width * sc), int(im.height * sc)))
    d = ImageDraw.Draw(im)
    T = lambda x, y: ((x - x0) * sc, (y - y0) * sc)
    for spec in sys.argv[8:]:
        lab, nums = spec.split(":")
        v = list(map(float, nums.split(",")))
        band = v[4] if len(v) > 4 else 6.0
        mode = "edge" if len(v) > 5 and v[5] == 1 else "ink"
        r = R.fit(g, v[0], v[1], v[2], v[3], band=band, mode=mode)
        d.line([T(v[0], v[1]), T(v[2], v[3])], fill=(0, 190, 0), width=1)
        if r:
            d.line([T(*r["p1"]), T(*r["p2"])], fill=(255, 0, 0), width=2)
            sh = ((r["az_fit"] - r["az_pick"] + 90) % 180) - 90
            print("%-6s az %.3f rms %.2f n %d shift %.2f len %.0f" % (lab, r["az_fit"], r["rms"], r["n"], sh, r["length_px"]))
        else:
            print(lab, "no fit")
        mx, my = T((v[0] + v[2]) / 2, (v[1] + v[3]) / 2)
        d.text((mx + 4, my), lab, fill=(200, 0, 200))
    out = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "crops", name + ".png")
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    main()
