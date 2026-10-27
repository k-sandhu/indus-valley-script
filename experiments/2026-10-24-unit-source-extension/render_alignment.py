import json,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension'); rows=[json.loads(x) for x in open('data/normalized/lipi_observed_faces.jsonl',encoding='utf8')]; rows=[x for x in rows if x['object_family_id'] in ['1057','1156','1168','1201','121']]; im=Image.new('RGB',(1100,len(rows)*90),'white');d=ImageDraw.Draw(im); font=ImageFont.truetype('data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf',42)
for i,r in enumerate(rows):
 d.text((5,i*90),r['record_id']+' '+r['source_cisi'],fill='black');
 for j,c in enumerate(re.findall(r'\d{3}',r['text_code_visual_ltr'])):d.text((180+j*75,i*90),chr(0xE000+int(c)),font=font,fill='black')
im.save(p/'alignment.png')
