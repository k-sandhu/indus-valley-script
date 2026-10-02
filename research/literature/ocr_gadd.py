"""OCR the primary scan acquired by root; text is a locator, images are evidence."""
from pathlib import Path
import concurrent.futures, hashlib, json, subprocess
import fitz

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'root_primary'/'gadd1932.pdf'
OUT=ROOT/'sources'/'gadd1932'
OUT.mkdir(exist_ok=True)
doc=fitz.open(SOURCE)
paths=[]
for i in range(9,len(doc)):
    path=OUT/f'pdf_{i+1:02d}.png'
    if not path.exists():
        doc[i].get_pixmap(matrix=fitz.Matrix(2,2)).save(path)
    paths.append(path)
def ocr(path):
    target=path.with_suffix('')
    if not path.with_suffix('.txt').exists():
        subprocess.run([r'C:\Program Files\Tesseract-OCR\tesseract.exe',str(path),str(target),'--psm','3'],check=True,capture_output=True)
    return path.with_suffix('.txt').read_text(encoding='utf-8')
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    texts=list(pool.map(ocr,paths))
(ROOT/'sources'/'gadd1932_ocr.txt').write_text('\n'.join(f'[PDF PAGE {i+10}]\n'+t for i,t in enumerate(texts)),encoding='utf-8')
(OUT/'manifest.json').write_text(json.dumps({'source':str(SOURCE),'source_url':'https://ignca.gov.in/Asi_data/33779.pdf','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'note':'OCR is not glyph transcription. Printed3-6=PDF10-13;PlateI14;printed7-10=PDF16-19;PlateII20;printed11-14=PDF22-25;PlateIII26;printed15-22=PDF28-35.','pages':len(doc),'render_dpi':144,'ocr_tool':'Tesseract','rendered_pdf_pages':list(range(10,len(doc)+1))},indent=2),encoding='utf-8')
print('OCR completed',len(paths),'pages',sum(len(t) for t in texts),'characters')
