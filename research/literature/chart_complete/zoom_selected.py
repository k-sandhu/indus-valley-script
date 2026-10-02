from pathlib import Path
import fitz
B=Path(__file__).parent
d=fitz.open(B.parents[2]/'research/corpus/primary/koskenniemi_parpola1979.pdf')
for c,r in [(6,8),(6,9),(6,20),(6,28)]:
    x=47+49.5*c;y=65+20.05*r
    d[20].get_pixmap(matrix=fitz.Matrix(12,12),clip=fitz.Rect(x-3,y-1,x+22,y+23)).save(B/'full_pdf21'/f'c{c}_r{r}_label_zoom.png')
