import sys
sys.dont_write_bytecode=True
from pathlib import Path
import fitz,subprocess,json,re,shutil
sys.stdout.reconfigure(encoding='utf-8')
source=Path(sys.argv[1]);raw=Path(sys.argv[2]);textdir=Path(sys.argv[3]);start=int(sys.argv[4]);end=int(sys.argv[5])
raw.mkdir(parents=True,exist_ok=True);textdir.mkdir(parents=True,exist_ok=True)
doc=fitz.open(source)
for n in range(start,min(end,len(doc))+1):
 if shutil.disk_usage(raw).free<1_000_000_000:raise RuntimeError('Less than 1 GB free')
 out=raw/f'ocr-page-{n:03d}-v1.png';txt=textdir/f'ocr-page-{n:03d}-v1.txt'
 if out.exists() or txt.exists():raise FileExistsError(out)
 pix=doc[n-1].get_pixmap(dpi=140,alpha=False);pix.save(out)
 proc=subprocess.run([r'C:\Program Files\Tesseract-OCR\tesseract.exe',str(out),'stdout','--psm','3'],capture_output=True,text=True,encoding='utf-8')
 with txt.open('x',encoding='utf-8') as f:f.write(proc.stdout)
 lines=proc.stdout.splitlines();hits=[s for s in lines if re.search(r'bhirrana|mitathal|contents|plan|fig\.|new light',s,re.I) and not re.search(r'orient|degree|\d\s*°',s,re.I)]
 print(json.dumps(dict(pdf_page=n,hits=hits,orientation_text_captured=bool(re.search(r'orient|\d\s*°',proc.stdout,re.I))),ensure_ascii=False),flush=True)
