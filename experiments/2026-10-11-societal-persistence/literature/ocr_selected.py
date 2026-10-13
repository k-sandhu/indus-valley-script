"""Local-only OCR for selected pages of the image-only Sraffa witness."""
from pathlib import Path
import hashlib
import json
import subprocess
import fitz

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'data/raw/2026-10-11-societal-persistence/literature'
PDF=RAW/'L17-sraffa1960-capture-v1.pdf'
SELECTED=[1,2,15,16,17,18]

if __name__=='__main__':
    target=RAW/'L17-sraffa1960-selected-ocr-v1.json'
    if target.exists(): raise FileExistsError(str(target))
    doc=fitz.open(PDF)
    rows=[]
    for pageno in SELECTED:
        png=RAW/f'L17-sraffa1960-pdfpage-{pageno:03d}-ocr-v1.png'
        if png.exists(): raise FileExistsError(str(png))
        doc[pageno-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(png)
        process=subprocess.run(['tesseract',str(png),'stdout','-l','eng'],capture_output=True,text=True,check=True)
        rows.append(dict(pdf_page_1based=pageno,image_path=png.relative_to(ROOT).as_posix(),image_sha256=hashlib.sha256(png.read_bytes()).hexdigest(),text=process.stdout,stderr=process.stderr))
    target.write_text(json.dumps(dict(parent_path=PDF.relative_to(ROOT).as_posix(),parent_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),engine=subprocess.run(['tesseract','--version'],capture_output=True,text=True,check=True).stdout,extraction='Tesseract OCR, not an independent edition',pages=rows),ensure_ascii=False,indent=2),encoding='utf-8')
    print(target)
