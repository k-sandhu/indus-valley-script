"""Extract the largest embedded image of a PDF page at native resolution.

Usage: python .../code/extract_image.py PDF PAGEINDEX NAME
Writes data/raw/2026-10-21-town-axes/plan-B/renders/NAME_p<idx>_native.png and prints its
pixel size, SHA-256, the image's placement box on the page (points) and whether the image
is placed rotated or flipped (from its transform matrix).
"""
import hashlib, os, sys
import fitz
pdf, idx, name = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = fitz.open(pdf)
p = d[idx]
infos = p.get_image_info(xrefs=True)
best = max(infos, key=lambda x: x["width"] * x["height"])
pix = fitz.Pixmap(d, best["xref"])
if pix.n - pix.alpha >= 4:
    pix = fitz.Pixmap(fitz.csRGB, pix)
out = os.path.join("data", "raw", "2026-10-21-town-axes", "plan-B", "renders", f"{name}_p{idx:04d}_native.png")
pix.save(out)
h = hashlib.sha256(open(out, "rb").read()).hexdigest()
print(out, pix.width, pix.height, h, "bbox", [round(v, 1) for v in best["bbox"]], "transform", [round(v, 3) for v in best["transform"]])
