from pathlib import Path
import fitz
B=Path(__file__).parent
d=fitz.open(B/'sources/joshi_parpola_1987_cisi1.pdf')
o=B/'metrology/primary_numeric';o.mkdir(parents=True,exist_ok=True)
d[119].get_pixmap(matrix=fitz.Matrix(3,3)).save(o/'M331_pdf120.png')
