"""Create a local-only review sheet of selected new anchor hypotheses."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/raw/2026-10-08-bonta-extension/source-2026-10-09/new-anchor-preview.png'
catalogue=json.loads((ROOT/'experiments/2026-10-08-bonta-extension/run-2026-10-09-v5/candidates.json').read_text(encoding='utf-8'))
rows={r['code']:r for r in catalogue['rows']}
selected=[('151','Porter or carried load','bhāra / bhārika'),('411','Barley or grain lot','yava'),
 ('450','Water supply/allotment','udaka / jala'),('600','Field or landed holding','kṣetra'),
 ('825','Cloth or textile lot','vastra / paṭa'),('142','Staff-holder or official','daṇḍin / adhikārin'),
 ('370','Seed stock or bulb produce','bīja'),('645','Joint contribution/link','saha / saṃyoga')]
im=Image.new('RGB',(1240,650),'#f4f2e9');d=ImageDraw.Draw(im)
title=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',30)
text=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
d.text((24,18),'New working anchors',font=title,fill='#21342d')
d.text((24,64),'Sanskrit comparisons and catalogue drawings · candidate meanings, 9 October 2026',font=small,fill='#59675e')
for i,(code,label,word) in enumerate(selected):
    x=24+(i%4)*300;y=110+(i//4)*255
    d.rounded_rectangle((x,y,x+284,y+235),radius=6,fill='#fffef9',outline='#dadcd0')
    d.text((x+13,y+10),'W'+code,font=text,fill='#285c48')
    glyph=Image.open(ROOT/rows[code]['font_drawing']['path']);im.paste(glyph,(x+62,y+40))
    d.text((x+13,y+170),label,font=small,fill='#21342d')
    d.text((x+13,y+197),word,font=text,fill='#285c48')
d.text((24,625),'Local Lipi font drawings; definitions checked against the retained Monier-Williams records.',font=small,fill='#59675e')
if OUT.exists():raise FileExistsError(OUT)
im.save(OUT);print(OUT)
