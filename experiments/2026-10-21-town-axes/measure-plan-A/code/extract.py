"""Extract embedded images from a PDF page at native resolution.

usage: python extract.py PDF INDEX OUTDIR [xref ...]
Writes OUTDIR/<pdfbase>_p<index>_x<xref>.png and prints its size, SHA-256 and the
placement matrix on the page, so a rotation of the placed image can be checked.
"""
import sys, os, fitz, hashlib
pdf, idx, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
want = set(int(x) for x in sys.argv[4:])
os.makedirs(out, exist_ok=True)
d = fitz.open(pdf)
pg = d[idx]
base = os.path.splitext(os.path.basename(pdf))[0]
for im in pg.get_images(full=True):
    xref = im[0]
    if want and xref not in want:
        continue
    pix = fitz.Pixmap(d, xref)
    if pix.n - pix.alpha >= 4:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    fn = os.path.join(out, f"{base}_p{idx}_x{xref}.png")
    pix.save(fn)
    try:
        info = pg.get_image_info(xrefs=True)
        tr = [i["transform"] for i in info if i.get("xref") == xref]
    except Exception:
        tr = []
    print(fn, pix.width, pix.height, hashlib.sha256(open(fn, 'rb').read()).hexdigest(), tr)
