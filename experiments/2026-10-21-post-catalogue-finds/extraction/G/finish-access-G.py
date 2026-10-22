"""Repair access metadata after the interruption and remove completed OCR rasters."""
import argparse,csv,json,re,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);p.add_argument('raw',type=Path);a=p.parse_args()
for name,key in [('kanmer-entry-fields-G.json','context'),('kanmer-catalogue-fields-G.json','contexts')]:
    q=a.out/name;rows=json.loads(q.read_text(encoding='utf-8'))
    for r in rows:r[key]=[{'identity_context':v} if isinstance(v,str) else v for v in r[key]]
    q.write_text(json.dumps(rows,indent=2),encoding='utf-8')
removed=[]
for q in (a.raw/'ocr').rglob('*.png'):
    if not q.resolve().is_relative_to(a.raw.resolve()):raise RuntimeError('path boundary')
    text=a.raw/'text'/q.parent.name/(q.stem+'.txt')
    if text.exists():q.unlink();removed.append(str(q.relative_to(a.raw)))
errors=[];empty=[];counts={}
for d in sorted((a.raw/'text').iterdir()):
    files=sorted(d.glob('p*.txt'));counts[d.name]=len(files)
    for q in files:
        if not q.stat().st_size:empty.append(str(q.relative_to(a.raw)))
for q in a.out.iterdir():
    if q.suffix=='.json':
        try:json.loads(q.read_text(encoding='utf-8-sig'))
        except Exception:errors.append(q.name)
    if q.suffix=='.csv':
        with q.open(encoding='utf-8-sig',newline='') as f:rs=list(csv.reader(f))
        if not rs or any(len(r)!=len(rs[0]) for r in rs):errors.append(q.name)
result={'passed':not errors,'format_errors':errors,'zero_text_pages':empty,'zero_text_page_status':'OCR attempted; no text recovered; none used as an object locator','removed_remaining_ocr_images':removed,'page_files_by_source':counts,'free_bytes':shutil.disk_usage(a.root).free}
(a.out/'resume-check-G.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'format_errors':errors,'zero_text_pages':empty,'remaining_images':len(list((a.raw/'ocr').rglob('*.png')))}))
