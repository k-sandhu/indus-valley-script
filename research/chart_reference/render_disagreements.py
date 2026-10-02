from pathlib import Path
import json,fitz
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
out=Path(__file__).resolve().parent
mismatch=json.loads((out/'full21_disagreements_before_adjudication.json').read_text())
manual=json.loads((ROOT/'research/literature/chart_complete/full21_audit.json').read_text())
index={(r['column_0based'],r['row_0based']):r for r in manual['rows']}
page=fitz.open(ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf')[20]
for m in mismatch:
    r=index[m['col'],m['row']];path=out/f'disagreement_c{m["col"]}_r{m["row"]}.png'
    page.get_pixmap(matrix=fitz.Matrix(12,12),clip=fitz.Rect(*r['cell_clip_points'])).save(path)
for start in [0,8,16]:
    rows=mismatch[start:start+8];canvas=Image.new('RGB',(1200,185*4),'white');draw=ImageDraw.Draw(canvas)
    for i,m in enumerate(rows):
        im=Image.open(out/f'disagreement_c{m["col"]}_r{m["row"]}.png').resize((510,144))
        x=(i%2)*600;y=(i//2)*185;canvas.paste(im,(x,y+28));draw.text((x,y),f'c{m["col"]} r{m["row"]}: root{m["root"]} / independent{m["independent"]}',fill='black')
    canvas.save(out/f'disagreement_sheet_{start}.png')
