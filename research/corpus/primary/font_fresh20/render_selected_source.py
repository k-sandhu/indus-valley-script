"""Preselect and render fresh original rows; performs no recognition."""
from pathlib import Path
import random
import json
import hashlib
from datetime import datetime, timezone
import fitz

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent/'koskenniemi_parpola1979.pdf'
OUT.mkdir(parents=True,exist_ok=True)
SELECTION = sorted(random.Random(20261015).sample([(c,r) for c in range(2) for r in range(8,35)],20))
doc=fitz.open(SOURCE)
rows=[]
for col,row in SELECTION:
    x0,x1=(64,285) if col==0 else (342,548)
    y0=67+20.0*row
    rect=(x0,y0-12,x1,y0+27)
    f=OUT/f'pdf30_c{col}_r{row:02d}_8x.png'
    doc[29].get_pixmap(matrix=fitz.Matrix(8,8),clip=fitz.Rect(rect)).save(f)
    rows.append({'col_0based':col,'row_0based':row,'crop':f.name,'clip_pdf_points':rect,'render_scale':8,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(OUT/'source_selection_manifest.json').write_text(json.dumps({
    'source_pdf':'research/corpus/primary/koskenniemi_parpola1979.pdf',
    'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'pdf_page_1based':30,'printed_page':29,
    'random_seed':20261015,'selection_rule':'sorted(random.Random(seed).sample([(col,row) for col in range(2) for row in range(8,35)],20))',
    'created_utc':datetime.now(timezone.utc).isoformat(),
    'method':'Direct source-PDF crops, no OCR/template recognition/prediction files consulted. Conservative39-point bands retain neighbouring-row context; only the explicitly labelled selected row is annotated. Extended upper margin avoids clipping taller glyphs and cumulative row-grid drift.',
    'rows':rows,
},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selection':SELECTION}))
