"""Contact sheet of selected PDF pages (file:page,page,...) for finding plans.
Usage: python .../code/sheet.py OUTNAME FILE:IDX,IDX ... [--size 330] [--cols 6]"""
import os, sys
import fitz
from PIL import Image, ImageDraw
args = sys.argv[1:]
size, cols = 330, 6
if "--size" in args:
    k = args.index("--size"); size = int(args[k + 1]); del args[k:k + 2]
if "--cols" in args:
    k = args.index("--cols"); cols = int(args[k + 1]); del args[k:k + 2]
name = args[0]
tiles = []
for spec in args[1:]:
    f, idxs = spec.rsplit(":", 1)
    d = fitz.open(f)
    for i in [int(x) for x in idxs.split(",") if x]:
        if i >= d.page_count:
            continue
        pix = d[i].get_pixmap(dpi=40)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        im.thumbnail((size, size))
        c = Image.new("RGB", (size + 10, size + 22), "white")
        c.paste(im, (5, 18))
        ImageDraw.Draw(c).text((5, 2), "%s %d" % (os.path.basename(f)[:18], i), fill="red")
        tiles.append(c)
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (size + 10), rows * (size + 22)), "white")
for k, t in enumerate(tiles):
    sheet.paste(t, ((k % cols) * (size + 10), (k // cols) * (size + 22)))
out = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "crops", name + ".png")
sheet.save(out)
print(out, sheet.size)
