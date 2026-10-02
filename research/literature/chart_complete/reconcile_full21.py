from pathlib import Path
import shutil,json,fitz
from PIL import Image,ImageDraw
B=Path(__file__).parent
for ext in ['json','csv']:
    src=B/f'full21_audit.{ext}';dst=B/f'full21_audit_before_adjudication.{ext}'
    if not dst.exists():shutil.copyfile(src,dst)
cells=[(0,1),(0,10),(0,14),(0,18),(0,29),(2,34),(3,2),(3,4),(4,6),(5,34),
       (6,11),(6,12),(6,13),(6,14),(6,15),(6,16),(6,17),(6,9),(7,6),(8,33),(8,5),(9,5)]
d=fitz.open(B.parents[2]/'research/corpus/primary/koskenniemi_parpola1979.pdf')
o=B/'full21_reconciliation';o.mkdir(exist_ok=True)
for c,r in cells:
    x=47+49.5*c;y=65+20.05*r
    d[20].get_pixmap(matrix=fitz.Matrix(12,12),clip=fitz.Rect(x-3,y-1,x+22,y+23)).save(o/f'c{c}_r{r}.png')
for start in range(0,len(cells),8):
    sheet=Image.new('RGB',(1200,650),'white');draw=ImageDraw.Draw(sheet)
    for j,(c,r) in enumerate(cells[start:start+8]):
        x=300*(j%4);y=325*(j//4)
        draw.text((x+10,y+3),f'Original PDF21 c{c} r{r}',fill='black')
        sheet.paste(Image.open(o/f'c{c}_r{r}.png'),(x,y+25))
    sheet.save(o/f'original_sheet_{start}.png')
(o/'manifest.json').write_text(json.dumps({'source':'Original1979 PDF21, printed20','cells':cells,'method':'Original12x labels only; no reference values rendered. Post-comparison source adjudication; earlier independent337 preserved.'},indent=2),encoding='utf-8')
