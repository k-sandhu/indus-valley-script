from pathlib import Path
import fitz,hashlib,json
BASE=Path(__file__).parent
SOURCE=BASE.parents[2]/'research/corpus/primary/koskenniemi_parpola1979.pdf'
OUT=BASE/'full_pdf21'
OUT.mkdir(exist_ok=True)
doc=fitz.open(SOURCE);manifest=[]
for col in range(10):
    stop_all=35 if col<9 else 22
    left=47+49.5*col
    for start,stop in ((0,12),(12,min(24,stop_all)),(24,stop_all)):
        if start>=stop:continue
        rect=fitz.Rect(left-3,65+20.05*start-1,left+48,65+20.05*(stop-1)+23)
        name=f'pdf21_c{col}_rows{start}_{stop-1}.png'
        doc[20].get_pixmap(matrix=fitz.Matrix(6,6),clip=rect).save(OUT/name)
        manifest.append({'pdf_page':21,'printed_page':20,'column_0based':col,'row_start':start,'row_end':stop-1,'clip_points':list(rect),'image':name})
(OUT/'source_manifest.json').write_text(json.dumps({'source':str(SOURCE.resolve()),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'audit':'Printed numeric labels only, manually read; no OCR/root reference/templates/predictions inspected. Earlier fresh20 sample remains separate.','images':manifest},indent=2),encoding='utf-8')
print(str(OUT))
