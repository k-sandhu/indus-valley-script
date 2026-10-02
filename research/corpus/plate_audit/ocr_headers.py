from pathlib import Path
import fitz, subprocess, json, concurrent.futures
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
pdf=fitz.open(ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf')
jobs=[]
for n in range(37,125):
    p=pdf[n-1]
    clip=fitz.Rect(0,0,p.rect.width,p.rect.height*.08)
    dest=OUT/f'header_{n}.png'
    p.get_pixmap(matrix=fitz.Matrix(2,2),clip=clip).save(dest)
    jobs.append((n,dest))
def run(job):
    n,p=job
    res=subprocess.run(['C:/Program Files/Tesseract-OCR/tesseract.exe',str(p),'stdout','--psm','6'],capture_output=True,text=True,encoding='utf-8',errors='replace')
    return {'pdf_page':n,'header_ocr':res.stdout.strip()}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
    rows=list(ex.map(run,jobs))
(OUT/'page_headers.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows: print(r['pdf_page'],r['header_ocr'].replace('\n',' | '))
