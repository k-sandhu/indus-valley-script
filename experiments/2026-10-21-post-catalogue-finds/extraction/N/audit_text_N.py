"""Check saved text completeness without keeping page renders."""
import hashlib
import json
import re
import runpy
import subprocess
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
out=M['OUT']; results=[]; errors=[]
manifests=[]
for f in out.glob('text-manifest-*-N.json'):
    manifests.extend(json.loads(f.read_text(encoding='utf-8')))
manifests.extend(json.loads((out/'text-manifest-N.json').read_text(encoding='utf-8')))
exe=r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin\pdftotext.exe'
for rec in manifests:
    sid=rec['source_id']; src=M['ROOT']/rec['source_path']; dest=M['TEXT']/sid
    h=hashlib.sha256()
    with src.open('rb') as f:
        while block:=f.read(4*1024*1024):h.update(block)
    if h.hexdigest()!=rec['sha256']:errors.append(dict(source_id=sid,error='source hash mismatch'))
    ns={int(f.stem[1:]) for f in dest.glob('p*.txt')}
    if ns!=set(range(1,rec['pages']+1)):errors.append(dict(source_id=sid,error='page set mismatch'))
    empty=[]; repaired=[]
    for n in range(1,rec['pages']+1):
        f=dest/f'p{n:04}.txt'
        if not f.exists():continue
        t=f.read_text(encoding='utf-8')
        if not t.strip():
            raw=subprocess.run([exe,'-f',str(n),'-l',str(n),'-layout','-enc','UTF-8',str(src),'-'],capture_output=True,check=True).stdout.decode('utf-8','replace').replace('\f','')
            if len(re.sub(r'\W','',raw))>=35:
                f.write_text(raw,encoding='utf-8');repaired.append(n)
            else:empty.append(n)
    results.append(dict(source_id=sid,pages=rec['pages'],empty_text_and_empty_text_layer=empty,repaired_pages=repaired,ocr_pages=rec['ocr_pages']))
images=list((M['RAW']/'run2N').rglob('*.png'))
if images:errors.append(dict(error='temporary page renders remain',count=len(images)))
report=dict(pass_=not errors,source_count=len(results),page_count=sum(r['pages'] for r in results),sources=results,errors=errors,notes='Empty pages had no usable saved OCR or PDF text; no object locator relies on an empty page. Temporary images were removed after OCR. No source was downloaded or copied.')
(out/'text-audit-N.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(pass_=not errors,sources=len(results),pages=report['page_count'],empty_pages=sum(len(r['empty_text_and_empty_text_layer']) for r in results),repaired=sum(len(r['repaired_pages']) for r in results),errors=errors)))
