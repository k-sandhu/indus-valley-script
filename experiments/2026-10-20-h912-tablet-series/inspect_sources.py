"""Make an attributed local contact sheet and preserve image pointers/hashes."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageOps, ImageDraw, ImageFont
import fitz

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RAW=ROOT/'data/raw/2026-10-20-h912-tablet-series'


def main():
 out=RAW/'inspection-v1';out.mkdir(exist_ok=False)
 names=['H-302_A.jpg','H-302_B.jpg','H-912_A.jpg','H-912_B.jpg',
        'M-494_A.jpg','M-495_A.jpg','M-928_A.jpg','H-246_A.jpg']
 sheet=Image.new('RGB',(1280,1600),'white')
 draw=ImageDraw.Draw(sheet)
 try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 except OSError:font=ImageFont.load_default()
 records=[]
 for i,name in enumerate(names):
  path=ROOT/'data/lipi/public/seal_images'/name
  x,y=(i%2)*640,(i//2)*400
  draw.text((x+12,y+8),name+' | CISI source crop',fill='black',font=font)
  with Image.open(path) as im:
   scaled=ImageOps.contain(im.convert('RGB'),(610,350))
   sheet.paste(scaled,(x+(640-scaled.width)//2,y+45+(350-scaled.height)//2))
  records.append({'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rights':'CISI photograph reproduced in Lipi; rights-unverified; kept local','transformation':'Resized to fit labelled contact sheet; no sign reconstruction.'})
 sheet.save(out/'source-contact.png')
 cisi=ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
 doc=fitz.open(cisi)
 for page in [261,157,158,253]:
  doc[page-1].get_pixmap(matrix=fitz.Matrix(1.8,1.8)).save(out/f'cisi1-pdf{page}.png')
 with (HERE/'inspection-v1.json').open('x',encoding='utf8') as f:json.dump({'selection':'All available core tablet photographs; published vessel-repetition controls; one fine-variant seal and one other appended sign control. H-1191 and H-1192 lack held CISI photographs. Vats drawings are audited in the excavation branch.','image_inputs':records,'cisi1_pdf':{'path':cisi.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(cisi.read_bytes()).hexdigest(),'pages_rendered_one_based':[261,157,158,253]},'output_local':out.relative_to(ROOT).as_posix()},f,indent=2);f.write('\n')
 print(json.dumps({'contact':str(out/'source-contact.png'),'full_pages':4,'inputs':len(records)}))


if __name__=='__main__':main()
