import fitz,json,csv,hashlib
from pathlib import Path
P=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-extension')
pdfs={1:Path('research/literature/sources/joshi_parpola_1987_cisi1.pdf'),2:Path('data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf')}
rows=list(csv.DictReader(open('experiments/2026-10-13-image-index-and-units/run-2026-10-13/pages/key-pages.csv',encoding='utf8')))
for r in rows:
 if r['key'] not in ['H-733','H-1001','H-102','H-160','C-40']:continue
 d=fitz.open(pdfs[int(r['volume'])]); page=d[int(r['pdf_page'])-1]; target=P/(r['key']+'-plate.png'); assert not target.exists(); page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(target)
 print(r['key'],page.rect)

# Source amendment and second surface: use a new local output directory on reproduction.
for volume,page_number,scale,name in [(1,374,1.5,"C-40-A-plate.png"),(2,175,2,"M-1188-plate.png")]:
 d=fitz.open(pdfs[volume]);target=P/name;assert not target.exists();d[page_number-1].get_pixmap(matrix=fitz.Matrix(scale,scale)).save(target)
