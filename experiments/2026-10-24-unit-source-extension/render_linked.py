import csv,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
P=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension'); rows=list(csv.DictReader(open('experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv',encoding='utf8'))); names=sorted({r['file'] for r in rows if r['object_family_id'] in ['1057','1156','1168','1201','121']}); im=Image.new('RGB',(1000,250*((len(names)+3)//4)),'white'); d=ImageDraw.Draw(im)
for i,n in enumerate(names):
 a=Image.open(Path('data/lipi/public/seal_images')/n).convert('RGB');a.thumbnail((240,210));x=(i%4)*250;y=(i//4)*250;im.paste(a,(x,y+30));d.text((x,y),n,fill='black')
im.save(P/'linked-images.png');(P/'displayed-files.json').write_text(json.dumps(names,indent=2),encoding='utf8');print(len(names))
