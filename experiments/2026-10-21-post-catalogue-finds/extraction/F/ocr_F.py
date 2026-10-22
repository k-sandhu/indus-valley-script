"""Recover page text with a recorded basis and short-lived greyscale renders."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--pdf', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--records', required=True, type=Path)
    p.add_argument('--workers', type=int, default=3)
    a = p.parse_args()
    digest = hashlib.file_digest(a.pdf.open('rb'), 'sha256').hexdigest()
    assert digest == 'c5a89e9bf41225b77e4b678749deecfd66c4fc64f1742beb1ccdc31c44dbdb8a'
    a.out.mkdir(parents=True, exist_ok=True)
    a.records.mkdir(parents=True, exist_ok=True)
    poppler = Path(r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin')
    tess = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    info = subprocess.run([str(poppler/'pdfinfo.exe'), str(a.pdf)], capture_output=True, check=True).stdout.decode('utf-8', 'replace')
    count = int(re.search(r'Pages:\s+(\d+)', info)[1])
    assert count == 641
    layer = subprocess.run([str(poppler/'pdftotext.exe'), '-layout', str(a.pdf), '-'], capture_output=True, check=True).stdout.decode('utf-8', 'replace').split('\f')
    assert len(layer) >= count
    basis_file = a.records/'page-basis-v2-F.csv'
    prior = {}
    if basis_file.exists():
        prior = {int(r['pdf_page']): r for r in csv.DictReader(basis_file.open(encoding='utf-8'))}
    fields = ['source_id','pdf_page','basis','layer_words','layer_latin_share','text_sha256','elapsed_seconds']
    def run(n):
        dest = a.out/f'p{n:04}.txt'
        if n in prior and dest.exists():
            return prior[n]
        start = time.monotonic()
        text = layer[n-1]
        words = re.findall(r'\b[^\W\d_]+\b', text)
        latin = sum(bool(re.fullmatch('[A-Za-z]+', w)) for w in words)/max(1,len(words))
        basis = 'pdf-text-layer'
        if len(words) < 80 or latin < .85:
            basis = 'tesseract-eng-300dpi-grey'
            fd, name = tempfile.mkstemp(prefix=f'iarF-{n:04}-', suffix='.pgm')
            os.close(fd)
            image = Path(name)
            prefix = str(image.with_suffix(''))
            try:
                subprocess.run([str(poppler/'pdftoppm.exe'), '-f',str(n),'-l',str(n),'-r','300','-gray','-singlefile',str(a.pdf),prefix], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
                env = dict(os.environ, OMP_THREAD_LIMIT='1')
                text = subprocess.run([tess,str(image),'stdout','-l','eng','--psm','3'],capture_output=True,check=True,env=env).stdout.decode('utf-8','replace')
            finally:
                image.unlink(missing_ok=True)
        dest.write_text(text, encoding='utf-8')
        return dict(source_id='iar-2003-04-asi',pdf_page=n,basis=basis,layer_words=len(words),layer_latin_share=round(latin,5),text_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),elapsed_seconds=round(time.monotonic()-start,2))
    provenance = dict(source_id='iar-2003-04-asi',sha256=digest,pdf_pages=count,render_dpi=300,render_colour='grey',language='eng',latin_threshold=.85,word_threshold=80,workers=a.workers,text_utility=str(poppler/'pdftotext.exe'),rights='rights-unverified; raw text local only',tesseract=subprocess.run([tess,'--version'],capture_output=True).stdout.decode().splitlines()[0])
    (a.records/'ocr-provenance-F.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    done = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        for row in pool.map(run, range(1,count+1)):
            done[int(row['pdf_page'])] = row
            with basis_file.open('w',newline='',encoding='utf-8') as f:
                w = csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(done[k] for k in sorted(done))
            if len(done)%20==0 or len(done)<=3 or len(done)==count:
                print(json.dumps(dict(completed=len(done),total=count,basis=row['basis'],seconds=row['elapsed_seconds'])),flush=True)


if __name__ == '__main__':
    main()
