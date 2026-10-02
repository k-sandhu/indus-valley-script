"""Render original primary pages for the vessel/metrology audit; no OCR inference."""
from pathlib import Path
import fitz

BASE = Path(__file__).resolve().parent
OUT = BASE / 'renders' / 'metrology'
OUT.mkdir(exist_ok=True)

jobs = [
    ('vats_1940_govscan_9842.pdf', [4, 58, 59, 80]),
    ('vats_1940_govscan_18220.pdf', [4, 6, 10, 12, 14, 16, 80]),
]
for name, pages in jobs:
    doc = fitz.open(BASE / 'sources' / name)
    for page in pages:
        doc[page - 1].get_pixmap(matrix=fitz.Matrix(2, 2)).save(
            OUT / f'{Path(name).stem}_pdf{page}.png')
doc = fitz.open(BASE / 'sources' / 'joshi_parpola_1987_cisi1.pdf')
page = doc[407]
r = page.rect
page.get_pixmap(matrix=fitz.Matrix(5,5), clip=fitz.Rect(r.width*.045,r.height*.645,r.width*.48,r.height*.71)).save(OUT / 'cisi1_p372_H370372_data.png')
