import fitz, sys, io
from PIL import Image, ImageDraw
src, out, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
frac = float(sys.argv[5]) if len(sys.argv) > 5 else 0.07
bottom = len(sys.argv) > 6 and sys.argv[6] == 'bottom'
d = fitz.open(src)
ims = []
for i in range(first, last+1):
    r = d[i-1].rect
    clip = fitz.Rect(0, r.height*(1-frac), r.width, r.height) if bottom else fitz.Rect(0, r.height*0.06, r.width, r.height*(0.06+frac))
    pix = d[i-1].get_pixmap(dpi=60, clip=clip)
    ims.append((i, Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')))
w = max(im.width for _, im in ims) + 80; h = sum(im.height for _, im in ims)
o = Image.new('RGB', (w, h), 'white'); dr = ImageDraw.Draw(o)
y = 0
for i, im in ims:
    o.paste(im, (80, y)); dr.text((5, y + 5), str(i), fill='red'); dr.line([(0, y), (w, y)], fill='blue'); y += im.height
o.save(out)
