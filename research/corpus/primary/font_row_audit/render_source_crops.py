"""Render original source pages without OCR or glyph matching."""
from pathlib import Path
import fitz
import json
import hashlib

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / 'koskenniemi_parpola1979.pdf'
DOC = fitz.open(SOURCE)
SPECS = {
    'pdf30_col0_rows3_7_8x': (29,(50,125,283,228),8),
    'pdf30_col1_rows3_7_8x': (29,(348,125,547,228),8),
    'pdf20_chart_4x': (19,(48,58,579,782),4),
    'pdf21_chart_4x': (20,(48,58,579,782),4),
    'pdf21_U_c5_bottom_12x': (20,(312,654,368,782),12),
    'pdf21_U_c6_top_12x': (20,(365,60,420,194),12),
    'pdf30_1021_U_check_20x': (29,(216,188,231,209),20),
    'pdf30_1056_fish_check_20x': (29,(478,168,488,189),20),
    'pdf21_unclear_fish_c9_12x': (20,(520,245,575,307),12),
    'pdf21_box_c3_rows14_20_12x': (20,(207,345,265,486),12),
    'pdf21_fishhat_c2_rows27_30_12x': (19,(157,602,212,691),12),
    'pdf21_U_c5_bottom_corrected_12x': (20,(300,654,353,782),12),
    'pdf21_U_c6_top_corrected_12x': (20,(350,60,403,194),12),
    'pdf21_unclear_fish_c9_corrected_12x': (20,(500,245,553,307),12),
    'pdf21_box_c3_rows14_20_corrected_12x': (20,(201,345,254,486),12),
    'pdf20_fish_c2_rows7_11_12x': (19,(156,206,210,307),12),
}
for page in (19,20):
    for label,(y0,y1) in [('top',(60,314)),('middle',(298,558)),('bottom',(542,785))]:
        SPECS[f'pdf{page+1}_chart_{label}_4x'] = (page,(48,y0,579,y1),4)
logs = []
for name,(page,rect,scale) in SPECS.items():
    file = OUT/(name+'.png')
    DOC[page].get_pixmap(matrix=fitz.Matrix(scale,scale),clip=fitz.Rect(rect)).save(file)
    logs.append({'name':file.name,'pdf_page_1based':page+1,'source_clip_pdf_points':rect,'render_scale':scale,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(OUT/'crop_manifest.json').write_text(json.dumps({
    'source_pdf':'research/corpus/primary/koskenniemi_parpola1979.pdf',
    'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'method':'Direct original-PDF rasters, unretouched, no OCR or matching',
    'crops':logs,
},indent=2),encoding='utf-8')
print(json.dumps({'rendered':len(logs)}))
