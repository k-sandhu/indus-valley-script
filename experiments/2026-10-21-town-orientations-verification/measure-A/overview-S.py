"""Fresh PDF contact sheet for locating plans; never a coordinate-picking surface."""
import sys,json,hashlib,shutil
from pathlib import Path
import fitz
from PIL import Image,ImageDraw
source,output=map(Path,sys.argv[1:3]);pages=[int(p) for p in sys.argv[3:]]
if output.exists():raise FileExistsError(output)
if shutil.disk_usage('C:/').free<1073741824:raise RuntimeError('Below 1 GiB free')
if 'jansen_urban1987_interim2' in source.name:raise RuntimeError('Use explicit page render for restricted report')
canvas=Image.new('RGB',(960,500*((len(pages)+2)//3)),'white');draw=ImageDraw.Draw(canvas)
with fitz.open(source) as doc:
    for j,p in enumerate(pages):
        pg=doc[p-1]; pix=pg.get_pixmap(matrix=fitz.Matrix(0.6,0.6),alpha=False)
        im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
        im.thumbnail((315,465))
        x=(j%3)*320;y=(j//3)*500
        canvas.paste(im,(x,y+25));draw.text((x+5,y+5),f'PDF {p} - overview only',fill='blue')
canvas.save(output)
with Path(str(output)+'.json').open('x',encoding='utf-8') as f:json.dump(dict(source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pages=pages,role='plan locator only; no picks'),f,indent=2)
