import fitz, sys
src, out, first, last, dpi, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
d = fitz.open(src)
pixs = [d[i-1].get_pixmap(dpi=dpi) for i in range(first, last+1)]
w = max(p.width for p in pixs); h = max(p.height for p in pixs)
rows = (len(pixs)+cols-1)//cols
o = fitz.Pixmap(fitz.csRGB, fitz.IRect(0,0,w*cols,h*rows), False)
o.clear_with(255)
for k,p in enumerate(pixs):
    if p.n != 3 or p.alpha: p = fitz.Pixmap(fitz.csRGB, p, 0) if p.alpha else fitz.Pixmap(fitz.csRGB, p)
    p.set_origin((k%cols)*w, (k//cols)*h)
    o.copy(p, p.irect)
o.save(out)
