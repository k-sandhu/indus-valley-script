"""crop.py pdf pageno(1-based) dpi x0 y0 x1 y1 (fractions) out.png"""
import sys, fitz, numpy as np
pdf, pg, dpi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
x0, y0, x1, y1 = map(float, sys.argv[4:8])
out = sys.argv[8]
doc = fitz.open(pdf)
pix = doc[pg - 1].get_pixmap(dpi=dpi)
a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
h, w = a.shape[:2]
c = a[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w), :3].copy()
p2 = fitz.Pixmap(fitz.csRGB, c.shape[1], c.shape[0], c.tobytes(), False)
p2.save(out)
print(c.shape)
