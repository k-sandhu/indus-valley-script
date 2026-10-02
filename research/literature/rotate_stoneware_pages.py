from pathlib import Path
import fitz
B=Path(__file__).parent
d=fitz.open(B/'sources/vidale_stoneware_primary.pdf')
o=B/'renders/stoneware';o.mkdir(parents=True,exist_ok=True)
for p in [0,3,8,11,14]:
    d[p].get_pixmap(matrix=fitz.Matrix(2.5,2.5).prerotate(270)).save(o/f'pdf{p+1:02}_rotation270.png')
