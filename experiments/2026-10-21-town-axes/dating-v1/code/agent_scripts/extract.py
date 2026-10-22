import sys, fitz, pathlib
pdf, out, pages = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
scale = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
crop = sys.argv[5] if len(sys.argv) > 5 else None
out.mkdir(parents=True, exist_ok=True)
doc = fitz.open(pdf)
sel = []
for part in pages.split(','):
    if '-' in part:
        a, b = part.split('-'); sel += list(range(int(a), int(b) + 1))
    else:
        sel.append(int(part))
for n in sel:
    imgs = doc[n - 1].get_images(full=True)
    big = max(imgs, key=lambda t: t[2] * t[3])
    pix = fitz.Pixmap(doc, big[0])
    if pix.alpha:
        pix = fitz.Pixmap(pix, 0)
    if crop:
        x0, y0, x1, y1 = [float(v) for v in crop.split(':')]
        r = fitz.IRect(int(x0 * pix.width), int(y0 * pix.height), int(x1 * pix.width), int(y1 * pix.height))
        pix2 = fitz.Pixmap(pix.colorspace, r, False)
        pix2.copy(pix, r)
        pix = pix2
    if scale != 1:
        pix = fitz.Pixmap(pix, int(pix.width * scale), int(pix.height * scale), None) if False else pix
    fn = out / ("p%03d%s.png" % (n, ("_" + crop.replace(':', '_')) if crop else ""))
    if scale != 1:
        import io
        pix.shrink(int(round(1 / scale)).bit_length() - 1) if scale < 1 else None
    pix.save(fn)
    print(fn, pix.width, pix.height)
