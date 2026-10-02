"""Original chart label-only source audit, columns5-9; no OCR/templates read."""
from pathlib import Path
import fitz, hashlib, json
BASE=Path(__file__).parent
SOURCE=BASE.parents[2]/'research/corpus/primary/koskenniemi_parpola1979.pdf'
OUT=BASE/'full_pdf20_columns5_9'
OUT.mkdir(exist_ok=True)
doc=fitz.open(SOURCE)
manifest=[]
for col in range(5,10):
    left=62+49.5*col
    for start,stop in ((0,12),(12,24),(24,35)):
        rect=fitz.Rect(left-3,65+20.05*start-1,left+48,65+20.05*(stop-1)+23)
        name=f'pdf20_c{col}_rows{start}_{stop-1}.png'
        doc[19].get_pixmap(matrix=fitz.Matrix(6,6),clip=rect).save(OUT/name)
        manifest.append({'pdf_page':20,'column_0based':col,'row_start':start,'row_end':stop-1,'clip_points':list(rect),'image':name})
(OUT/'source_manifest.json').write_text(json.dumps({'source':str(SOURCE.resolve()),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'audit':'Printed numeric labels only; no glyph verification; no OCR, matching or root labels inspected.','images':manifest},indent=2),encoding='utf-8')
print(str(OUT))
