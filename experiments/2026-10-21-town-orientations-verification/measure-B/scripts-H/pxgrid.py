"""Copy a render with a labelled PNG-pixel grid, optionally cropped and enlarged.

The labels give pixel coordinates of the ORIGINAL render (integer = pixel centre),
so picks read from this copy go straight into a picks file for that render.
Usage: pxgrid.py <render.png> <out.png> [--region x0 y0 x1 y1] [--zoom k] [--step s]
"""
import sys
sys.dont_write_bytecode = True
import argparse
from pathlib import Path
from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("render")
    p.add_argument("out")
    p.add_argument("--region", type=int, nargs=4)
    p.add_argument("--zoom", type=int, default=1)
    p.add_argument("--step", type=int, default=50)
    p.add_argument("--color", default="magenta")
    a = p.parse_args()
    if Path(a.out).exists():
        raise FileExistsError(a.out)
    im = Image.open(a.render).convert("RGB")
    x0, y0, x1, y1 = a.region or (0, 0, im.width, im.height)
    crop = im.crop((x0, y0, x1, y1))
    k = a.zoom
    crop = crop.resize((crop.width * k, crop.height * k), Image.Resampling.NEAREST)
    d = ImageDraw.Draw(crop)
    # Pixel centre c in the original render lies at (c - x0 + 0.5) * k - 0.5 in the copy.
    first_x = ((x0 + a.step - 1) // a.step) * a.step
    for x in range(first_x, x1, a.step):
        q = (x - x0 + 0.5) * k - 0.5
        d.line([(q, 0), (q, crop.height)], fill=a.color, width=1)
        d.text((q + 2, 2), str(x), fill=a.color, stroke_width=1, stroke_fill="black")
        d.text((q + 2, crop.height - 14), str(x), fill=a.color, stroke_width=1, stroke_fill="black")
    first_y = ((y0 + a.step - 1) // a.step) * a.step
    for y in range(first_y, y1, a.step):
        q = (y - y0 + 0.5) * k - 0.5
        d.line([(0, q), (crop.width, q)], fill=a.color, width=1)
        d.text((2, q + 2), str(y), fill=a.color, stroke_width=1, stroke_fill="black")
        d.text((crop.width - 34, q + 2), str(y), fill=a.color, stroke_width=1, stroke_fill="black")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    crop.save(a.out)
    print(a.out, crop.size)


if __name__ == "__main__":
    main()
