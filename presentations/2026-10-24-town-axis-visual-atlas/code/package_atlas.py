"""Assemble a bookmarked PDF and local-only archive after figure review."""
from pathlib import Path
import hashlib
import json
import sys
import textwrap
import zipfile
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

PACKAGE=Path(__file__).resolve().parents[1]
LOCAL=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-axis-visual-atlas')
RUN=sys.argv[1] if len(sys.argv)>1 else 'run-v4'
OUT=LOCAL/RUN
manifest=json.loads((OUT/'figures.json').read_text(encoding='utf-8'))
figs=manifest['figures']
assert len(figs)==32

def archive_and_record(suffix=''):
    final=OUT/'town-axis-visual-atlas-2026-10-24.pdf'
    archive=OUT/f'town-axis-graphics-2026-10-24{suffix}.zip'
    if archive.exists():raise FileExistsError(archive)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for folder in ['png','svg','pdf','thumbs']:
            for f in sorted((OUT/folder).iterdir()):z.write(f,str(f.relative_to(OUT)))
        for f in [final,OUT/'figures.json',OUT/'SOURCE-NOTES.md',OUT/'selected-figures.jpg']:
            z.write(f,f.name)
        for f in sorted((PACKAGE/'code').glob('*')):
            if f.is_file():z.write(f,'code/'+f.name)
    # Verify after closing the writer, when its central directory is complete.
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    delivery={'figure_count':32,'atlas_pages':35,'current_run':RUN,'mixed_rights_local_only':True,
     'files':[{'physical_path':str(p),'logical_path':f'data/raw/2026-10-24-town-axis-visual-atlas/{RUN}/{p.name}',
              'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [final,archive,OUT/'selected-figures.jpg']],
     'new_sources':0,'new_archaeological_measurements':0,'coverage_changes':0,
     'package_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (PACKAGE/f'delivery-{RUN}.json').write_text(json.dumps(delivery,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(delivery,indent=2))

if '--recover' in sys.argv:
    # The earlier files passed reopening checks. Preserve them and repack the
    # corrected recipe under a new archive name.
    archive_and_record(sys.argv[3] if len(sys.argv)>3 else '-v2')
    raise SystemExit(0)
BG,INK,MUTED,TEAL='#F7F4ED','#182C30','#59686A','#207D80'
pdfmetrics.registerFont(TTFont('ArialLocal','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialLocalBold','C:/Windows/Fonts/arialbd.ttf'))

def line(c,x,y,text,size=16,bold=False,color=INK):
    c.setFont('ArialLocalBold' if bold else 'ArialLocal',size)
    c.setFillColor(color);c.drawString(x,y,text)

def page(c):
    c.setFillColor(BG);c.rect(0,0,1152,720,stroke=0,fill=1)

def wrap(c,text,x,y,width=140,size=14,color=INK):
    for value in textwrap.wrap(text,width):
        line(c,x,y,value,size,color=color);y-=size*1.45
    return y

front=OUT/'build/front-matter.pdf'
c=canvas.Canvas(str(front),pagesize=(1152,720))
page(c)
line(c,65,630,'Town axes',60,True)
line(c,68,567,'A visual atlas',35,True)
line(c,68,517,'32 source-linked figures for Q-1032',22,color=TEAL)
line(c,68,470,'24 October 2026',17,color=MUTED)
for i,number in enumerate([8,14,23]):
    f=figs[number-1];c.drawImage(str(OUT/'thumbs'/f"{f['slug']}.jpg"),65+i*354,218,width=330,height=206,preserveAspectRatio=True,anchor='c')
wrap(c,'Coverage, architectural axes, source images, building phases and modern horizons. The final figure gives the named-wall survey that could decide the reading.',68,167,width=132,size=17)
wrap(c,'Local-only atlas. Source plates and imagery retain their existing rights. Each figure preserves its source route and the uncertainty that affects its use.',68,91,width=150,size=12,color=MUTED)
wrap(c,'produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.',68,42,width=180,size=9,color=MUTED)
c.showPage()
for section in range(2):
    page(c);line(c,65,645,'Figure catalogue',31,True)
    line(c,67,600,'Figures '+str(section*16+1)+'-'+str((section+1)*16),17,color=MUTED)
    for i,row in enumerate(figs[section*16:(section+1)*16]):
        y=556-i*28
        line(c,68,y,f"{row['number']:02d}",15,True,color=TEAL)
        line(c,115,y,row['title'].replace('’',"'"),15)
        line(c,1025,y,str(row['number']+3),14,color=MUTED)
    line(c,68,60,'The PDF bookmarks open each full-size figure. PNG, SVG and individual PDF versions accompany the atlas.',12,color=MUTED)
    c.showPage()
c.save()

final=OUT/'town-axis-visual-atlas-2026-10-24.pdf'
if final.exists():raise FileExistsError(final)
writer=PdfWriter();writer.append(str(front))
for row in figs:writer.append(str(OUT/'pdf'/f"{row['slug']}.pdf"))
writer.add_outline_item('Cover',0)
writer.add_outline_item('Figure catalogue',1)
for row in figs:writer.add_outline_item(f"{row['number']:02d} {row['title']}",row['number']+2)
writer.add_metadata({'/Title':'Town axes: a visual atlas','/Author':'The Indus research project, with GPT-6 through Codex desktop','/Subject':'Q-1032 source-backed observations and deciding survey','/Keywords':'town axes, north references, Surkotada, Mohenjo-daro, Lothal, horizon, uncertainty'})
with final.open('wb') as f:writer.write(f)
assert len(PdfReader(final).pages)==35

# A compact preview uses existing figures without changing their evidence.
selected=[1,8,14,15,18,21,23,31,32]
preview=Image.new('RGB',(2400,1660),BG)
draw=ImageDraw.Draw(preview)
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',34)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
draw.text((45,30),'Town-axis visual atlas: selected figures',fill=INK,font=font)
for idx,num in enumerate(selected):
    row=figs[num-1];im=Image.open(OUT/'png'/f"{row['slug']}.png").convert('RGB')
    im.thumbnail((770,470),Image.Resampling.LANCZOS)
    x=(idx%3)*800+(800-im.width)//2;y=105+(idx//3)*510
    preview.paste(im,(x,y));draw.text(((idx%3)*800+34,y+475),f"{num:02d}  {row['group']}",fill=MUTED,font=small)
preview.save(OUT/'selected-figures.jpg',quality=92)

notes=['# Source and use notes','',
 'This local-only bundle contains 32 PNG figures, 32 SVG figures, 32 individual PDFs and a 35-page bookmarked atlas.',
 'Source imagery and scanned plans retain their own terms. They are not covered by the project\'s CC0 dedication.',
 'Copernicus: produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved.',
 'Esri imagery: Esri, Vantor, Earthstar Geographics and the GIS User Community. Archived release 8432 has no established exposure date.',
 'Own project prose and aggregate plots follow CC0. Project code follows the Unlicense. The whole bundle has mixed rights and remains local-only.',
 'The source register is experiments/2026-10-24-q1032-town-axis-register/run-v5/. No new archaeological measurements or source acquisitions enter through this atlas.',
 'The endpoint sensitivity curve is a calculation with fixed three-pixel endpoint uncertainty. It is not an empirical calibration.',
 'The two 20-town horizon comparisons retain all 30 usable profiles, including different observer points at a town. Four excluded horizon records remain in the register.',
 '', '## Figure sources','']
for row in figs:
    notes.extend([f"### {row['number']:02d}. {row['title']}",'',row['caption'],'',row['source'],'','Records: '+', '.join(row['source_records']), '','Rights: '+row['rights_status']+'. Handling: local-only.',''])
(OUT/'SOURCE-NOTES.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')

archive_and_record()
