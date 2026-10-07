"""Acquire/reuse primary witnesses; downloaded text stays in the local raw directory."""
import argparse, hashlib, json, os, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
import fitz
import requests

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / 'data/raw/2026-10-06-evidence-census/sites-deep/c-north-india'
RAW.mkdir(parents=True, exist_ok=True)
for variable in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[variable] = str(RAW / 'tmp')
(RAW / 'tmp').mkdir(exist_ok=True)

def acquire(identifier, url=None, reuse=None):
    path=RAW/(identifier+'.pdf')
    rec={'id':identifier,'url':url,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'rights_status':'rights-unverified'}
    try:
        if reuse:
            shutil.copyfile(reuse,path); rec['reused_path']=str(reuse)
        elif not path.exists():
            r=requests.get(url,timeout=55);r.raise_for_status()
            if not r.content.startswith(b'%PDF'):raise ValueError('Response is not a PDF')
            path.write_bytes(r.content)
        rec.update(local_path=str(path.relative_to(ROOT)),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        doc=fitz.open(path)
        rec['page_count']=len(doc)
        pages=[{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)]
        (RAW/(identifier+'.pages.json')).write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
        rec.update(status='acquired',text_characters=sum(len(p['text']) for p in pages))
    except Exception as e:rec.update(status='failed',error=str(e))
    (RAW/(identifier+'.acquisition.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
    return rec

def ocr(identifier,pages):
    doc=fitz.open(RAW/(identifier+'.pdf')); results=[]
    for page in pages:
        img=RAW/(f'{identifier}-pdf{page:04d}.png')
        doc[page-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(img)
        out=img.with_suffix('')
        subprocess.run(['C:/Program Files/Tesseract-OCR/tesseract.exe',str(img),str(out),'--psm','3'],check=True,capture_output=True)
        results.append({'pdf_page':page,'text':out.with_suffix('.txt').read_text(encoding='utf-8'),'method':'tesseract locator; image review required'})
        # The PDF preserves the visual witness. Avoid retaining a large page PNG
        # unless a caller needs to render it separately for immediate review.
        img.unlink()
    target=RAW/(identifier+'.ocr.json')
    old=json.loads(target.read_text(encoding='utf-8')) if target.exists() else []
    merged={r['pdf_page']:r for r in old+results}
    target.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    return results

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('id');ap.add_argument('--url');ap.add_argument('--reuse');ap.add_argument('--ocr',nargs='+',type=int);ap.add_argument('--find',nargs='+');args=ap.parse_args()
    if args.ocr:
        print(json.dumps(ocr(args.id,args.ocr),ensure_ascii=True))
    elif args.find:
        p=RAW/(args.id+'.pages.json')
        hits=[x for x in json.loads(p.read_text(encoding='utf-8')) if any(t.casefold() in x['text'].casefold() for t in args.find)]
        print(json.dumps(hits,ensure_ascii=True,indent=2))
    else:print(json.dumps(acquire(args.id,args.url,args.reuse),ensure_ascii=True))
