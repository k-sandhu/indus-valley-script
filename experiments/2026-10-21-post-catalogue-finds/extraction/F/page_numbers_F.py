"""Resolve physical running-page numbers from cropped footer OCR."""
import argparse
import concurrent.futures
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pdf',required=True,type=Path)
    p.add_argument('--records',required=True,type=Path)
    p.add_argument('--pages',default='1-641')
    a=p.parse_args()
    ns=[]
    for s in a.pages.split(','):
        if '-' in s:
            lo,hi=map(int,s.split('-')); ns.extend(range(lo,hi+1))
        else: ns.append(int(s))
    pop=Path(r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin')
    info=subprocess.run([str(pop/'pdfinfo.exe'),'-f','1','-l','641',str(a.pdf)],capture_output=True,check=True).stdout.decode('utf-8','replace')
    sizes={int(n):(float(w),float(h)) for n,w,h in re.findall(r'Page\s+(\d+)\s+size:\s+([\d.]+)\s+x\s+([\d.]+)',info)}
    def run(n):
        w,h=sizes[n]
        fd,name=tempfile.mkstemp(prefix=f'iarF-footer-{n}-',suffix='.png'); os.close(fd)
        image=Path(name)
        try:
            subprocess.run([str(pop/'pdftoppm.exe'),'-f',str(n),'-l',str(n),'-r','300','-gray','-png','-singlefile','-x','0','-y',str(int(h*300/72*.85)),'-W',str(int(w*300/72)),'-H',str(int(h*300/72*.05)+2),str(a.pdf),str(image.with_suffix(''))],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
            t=subprocess.run([r'C:\Program Files\Tesseract-OCR\tesseract.exe',str(image),'stdout','-l','eng','--psm','11'],capture_output=True,check=True,env=dict(os.environ,OMP_THREAD_LIMIT='1')).stdout.decode('utf-8','replace')
        finally: image.unlink(missing_ok=True)
        nums=[s.strip() for s in t.splitlines() if re.fullmatch(r'\s*\d{1,3}\s*',s)]
        return dict(source_id='iar-2003-04-asi',pdf_page=n,printed_page=nums[-1] if nums else '',basis='footer-ocr-300dpi',numeric_candidates='|'.join(nums))
    dest=a.records/'footer-numbers-v3-F.csv'
    rows={int(r['pdf_page']):r for r in csv.DictReader(dest.open(encoding='utf-8'))} if dest.exists() else {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(run,[n for n in ns if n not in rows]):
            rows[r['pdf_page']]=r
            with dest.open('w',encoding='utf-8',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=['source_id','pdf_page','printed_page','basis','numeric_candidates']); writer.writeheader();writer.writerows(rows[k] for k in sorted(rows))
            if len(ns)<30 or len(rows)%100==0: print(json.dumps(r),flush=True)


if __name__=='__main__': main()
