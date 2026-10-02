from pathlib import Path
import fitz,hashlib,json,random
from PIL import Image,ImageDraw
BASE=Path(__file__).parent
SOURCE=BASE.parents[2]/'research/corpus/primary/koskenniemi_parpola1979.pdf'
previous=json.loads((BASE.parent/'chart_label_audit/sampling_manifest.json').read_text())['sample']
excluded={(r['column_0based'],r['row_0based']) for r in previous if r['pdf_page']==21}
eligible=[(c,r) for c in range(10) for r in range(35) if (c<9 or r<22) and (c,r) not in excluded]
chosen=sorted(random.Random(20261013).sample(eligible,20))
OUT=BASE/'fresh_pdf21'
OUT.mkdir(exist_ok=True)
doc=fitz.open(SOURCE)
manifest=[]
for col,row in chosen:
    left=47+49.5*col;top=65+20.05*row
    rect=fitz.Rect(left-3,top-1,left+48,top+23)
    name=f'pdf21_c{col}_r{row}.png'
    doc[20].get_pixmap(matrix=fitz.Matrix(8,8),clip=rect).save(OUT/name)
    manifest.append({'pdf_page':21,'printed_page':20,'column_0based':col,'row_0based':row,'clip_points':list(rect),'image':name})
for half in range(2):
    sheet=Image.new('RGB',(1020,1250),'white');draw=ImageDraw.Draw(sheet)
    for j,m in enumerate(manifest[half*10:(half+1)*10]):
        x=(j%2)*510;y=(j//2)*250
        draw.text((x+10,y+8),f"PDF21 COLUMN {m['column_0based']} ROW {m['row_0based']}",fill='black')
        sheet.paste(Image.open(OUT/m['image']).convert('RGB'),(x+10,y+35))
    sheet.save(OUT/f'fresh_sheet_{half+1}.png')
(BASE/'fresh21_sampling_manifest.json').write_text(json.dumps({'source':str(SOURCE.resolve()),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'seed':20261013,'rng':'Python random.Random; column-major then row-major eligible enumeration; sample20 without replacement then sort','previous15_excluded':sorted(excluded),'eligible_count':len(eligible),'sample':manifest},indent=2),encoding='utf-8')
print(json.dumps(manifest,indent=2))
