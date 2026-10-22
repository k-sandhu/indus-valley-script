import fitz, sys
src, out, page, dpi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
clip = None
if len(sys.argv) > 5:
    x0,y0,x1,y1 = map(float, sys.argv[5].split(','))
    r = fitz.open(src)[page-1].rect
    clip = fitz.Rect(r.width*x0, r.height*y0, r.width*x1, r.height*y1)
d = fitz.open(src)
d[page-1].get_pixmap(dpi=dpi, clip=clip).save(out)
