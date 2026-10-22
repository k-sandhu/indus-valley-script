"""Inspect a new published coordinate without replacing initial renders."""
import sys,shutil,json
from pathlib import Path
sys.dont_write_bytecode=True
pkg=Path.cwd()/'experiments/2026-10-21-town-orientations-verification'
sys.path.insert(0,str(pkg/'tools'))
from render_image import render
from PIL import Image,ImageDraw
slug,tag,lat,lon=sys.argv[1:]
snap=json.loads((pkg/'measure-A/picks'/slug/'source-index-G-v1.json').read_text())
raw=Path.cwd()/'data/raw/2026-10-21-town-orientations-verification/measure-A'/slug
sheet=Image.new('RGB',(1600,850),'white');d=ImageDraw.Draw(sheet)
for j,(size,layer,edge) in enumerate((size,layer,edge) for size in (2000,800) for layer,edge in [('RGB',False),('NIR',False),('brightness',False),('brightness',True)]):
    if shutil.disk_usage(raw).free<1_000_000_000:raise RuntimeError('less than1GB free')
    name=f'{tag}-{size}-{layer}{"-edge" if edge else ""}.png'
    render(snap['imagery']['composite']['path'],str(raw/name),[float(lat),float(lon)],size,layer,4 if size==2000 else 10,250 if size==2000 else 100,edge)
    im=Image.open(raw/name);im.thumbnail((400,400));x=(j%4)*400;y=(j//4)*425
    sheet.paste(im,(x,y+25));d.text((x+3,y+5),name,fill='black')
out=raw/f'{tag}-overview.jpg'
if out.exists():raise FileExistsError(out)
sheet.save(out,quality=90)
print(out)
