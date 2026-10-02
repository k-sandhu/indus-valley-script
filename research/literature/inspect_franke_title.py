from pathlib import Path
import fitz
B=Path(__file__).parent
d=fitz.open(B/'sources/franke_govscan_74331.pdf');o=B/'renders/franke';o.mkdir(exist_ok=True)
for p in range(8):d[p].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(o/f'pdf{p+1:03}.png')
print(d.metadata)
