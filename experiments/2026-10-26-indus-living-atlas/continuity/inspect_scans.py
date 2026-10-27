"""Make local OCR and page images for bounded source inspection."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import fitz

RAW = Path('D:/projects/indus_valley_script/data/raw/2026-10-26-indus-living-atlas/continuity')
FILES = {
    'KM2004': RAW / 'kenoyer-meadow2004.pdf',
    'M1943': Path('research/literature/sources/mackay_1943_chandaro.pdf'),
}

def page_ocr(task):
    sid, pno = task
    image = RAW / f'{sid}-p{pno:03}.png'
    output = RAW / f'{sid}-p{pno:03}-ocr.txt'
    if output.exists():
        raise FileExistsError(output)
    with fitz.open(FILES[sid]) as doc:
        doc[pno-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(image)
    run = subprocess.run(['C:/Program Files/Tesseract-OCR/tesseract.exe', str(image), 'stdout', '-l', 'eng'],
                         capture_output=True, check=True)
    output.write_bytes(run.stdout)
    return {'source_id': sid, 'pdf_page': pno, 'text': output.read_text(encoding='utf-8')}

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    jobs = [('KM2004', p) for p in range(1,16)] + [('M1943', p) for p in range(5,21)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(page_ocr, jobs))
    for row in rows:
        if row['source_id'] == 'M1943' or row['pdf_page'] in [1,2,3,4,5,6]:
            print(row['source_id'], 'PDF', row['pdf_page'], row['text'][:2600])
    manifest = [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in RAW.glob('*-ocr.txt')]
    out = RAW / 'ocr-manifest-v1.json'
    if out.exists():
        raise FileExistsError(out)
    out.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
