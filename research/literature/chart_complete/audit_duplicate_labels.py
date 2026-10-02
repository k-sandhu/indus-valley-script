"""Source-only reinspection of flagged numeric-label duplicate groups."""
from pathlib import Path
import json,fitz
from PIL import Image,ImageDraw
B=Path(__file__).parent
cells=[(20,2,1),(21,5,9),(20,4,1),(21,7,5),(20,4,13),(21,1,19),(20,4,21),(20,7,24),(20,7,25),(21,8,33),(20,8,5),(21,8,2),(20,9,19),(21,4,7),(20,9,33),(21,8,16)]
src=B.parents[2]/'research/corpus/primary/koskenniemi_parpola1979.pdf'
d=fitz.open(src);o=B/'duplicate_labels';o.mkdir(exist_ok=True)
for p,c,r in cells:
 x=(62 if p==20 else 47)+49.5*c;y=65+20.05*r
 d[p-1].get_pixmap(matrix=fitz.Matrix(12,12),clip=fitz.Rect(x-3,y-1,x+22,y+23)).save(o/f'pdf{p}_c{c}_r{r}.png')
for start in [0,8]:
 sheet=Image.new('RGB',(1200,650),'white');draw=ImageDraw.Draw(sheet)
 for q,(p,c,r) in enumerate(cells[start:start+8]):
  x=300*(q%4);y=325*(q//4)
  draw.text((x+8,y+3),f'Original PDF{p} c{c} r{r}',fill='black')
  sheet.paste(Image.open(o/f'pdf{p}_c{c}_r{r}.png'),(x,y+25))
 sheet.save(o/f'original_sheet_{start}.png')
(o/'manifest.json').write_text(json.dumps({'source':str(src.resolve()),'method':'Original numeric labels only. Coordinates selected because parent flagged duplicate best codes; no uniqueness constraint or proposed expected value is used to adjudicate.','cells':cells},indent=2),encoding='utf-8')
print(o)
