"""Map running-page numbers, using coordinates and narrow footer OCR."""
import argparse
import concurrent.futures
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pdf',required=True,type=Path)
    p.add_argument('--records',required=True,type=Path)
    p.add_argument('--text',required=True,type=Path)
    a=p.parse_args()
    pop=Path(r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin')
    data=subprocess.run([str(pop/'pdftotext.exe'),'-bbox',str(a.pdf),'-'],capture_output=True,check=True).stdout
    doc=ET.fromstring(data)
    pgs=[x for x in doc.iter() if x.tag.endswith('page')]
    result={}; missing=[]
    for n,pg in enumerate(pgs,1):
        nums=[x.text for x in pg.iter() if x.tag.endswith('word') and x.text and re.fullmatch(r'\d{1,3}',x.text) and 710<float(x.attrib['yMin'])<790]
        if len(nums)==1:
            result[n]=dict(source_id='iar-2003-04-asi',pdf_page=n,printed_page=nums[0],basis='positioned-text-footer')
        else:
            missing.append((n,float(pg.attrib['width']),float(pg.attrib['height'])))
    def run(item):
        n,w,h=item
        fd,name=tempfile.mkstemp(prefix=f'iarF-narrow-{n}-',suffix='.png');os.close(fd);image=Path(name)
        try:
            x=15 if n%2==0 else w-90
            subprocess.run([str(pop/'pdftoppm.exe'),'-f',str(n),'-l',str(n),'-r','300','-gray','-png','-singlefile','-x',str(int(x*300/72)),'-y',str(int(725*300/72)),'-W',str(int(75*300/72)),'-H',str(int(45*300/72)),str(a.pdf),str(image.with_suffix(''))],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
            t=subprocess.run([r'C:\Program Files\Tesseract-OCR\tesseract.exe',str(image),'stdout','-l','eng','--psm','6'],capture_output=True,check=True,env=dict(os.environ,OMP_THREAD_LIMIT='1')).stdout.decode('utf-8','replace')
        finally: image.unlink(missing_ok=True)
        nums=re.findall(r'(?m)^\s*(\d{1,3})\s*$',t)
        return n,dict(source_id='iar-2003-04-asi',pdf_page=n,printed_page=nums[0] if len(nums)==1 else '',basis='narrow-footer-ocr' if len(nums)==1 else 'not-detected')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        result.update(pool.map(run,missing))
    with (a.records/'printed-pages-F.csv').open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['source_id','pdf_page','printed_page','basis']);wr.writeheader();wr.writerows(result[k] for k in sorted(result))
    mapping={k:v['printed_page'] for k,v in result.items()}
    (a.text/'printed_page_map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    cand=a.records/'candidate-pages-F.csv'
    if cand.exists():
        rows=list(csv.DictReader(cand.open(encoding='utf-8')))
        for r in rows:r['printed_page']=mapping[int(r['pdf_page'])]
        with cand.open('w',encoding='utf-8',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    print(json.dumps(dict(pages=len(result),positioned=sum(r['basis']=='positioned-text-footer' for r in result.values()),footer_ocr=sum(r['basis']=='narrow-footer-ocr' for r in result.values()),unresolved=[k for k,v in result.items() if not v['printed_page']])))


if __name__=='__main__':main()
