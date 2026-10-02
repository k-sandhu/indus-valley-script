from pathlib import Path
import concurrent.futures, fitz, subprocess

BASE=Path(__file__).resolve().parent
src=BASE/'sources/vidale_stoneware_primary.pdf'
out=BASE/'renders/stoneware'
out.mkdir(exist_ok=True)
tesseract=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def one(i):
    doc=fitz.open(src)
    image=out/f'pdf{i+1:02}.png'
    doc[i].get_pixmap(matrix=fitz.Matrix(2.5,2.5)).save(image)
    r=subprocess.run([tesseract,str(image),'stdout','--psm','3'],capture_output=True,text=True,encoding='utf-8',errors='replace')
    (out/f'pdf{i+1:02}.txt').write_text(r.stdout,encoding='utf-8')
    print(f'PDF{i+1}: {len(r.stdout)} characters',flush=True)
    return i,r.stdout
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(one,range(len(fitz.open(src)))))
(BASE/'sources/vidale_stoneware_ocr.txt').write_text('\n'.join(f'[PDF {i+1}]\n{t}' for i,t in sorted(results)),encoding='utf-8')
