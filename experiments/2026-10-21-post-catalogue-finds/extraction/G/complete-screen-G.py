"""Finish the bounded local keyword screen and record page access without excerpts."""
import argparse,csv,json,re,sys
from pathlib import Path
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);p.add_argument('raw',type=Path);a=p.parse_args()
root=a.root/'data/raw/2026-10-21-post-catalogue-finds'
old=list(csv.DictReader((a.out/'pages-read-G.csv').open(encoding='utf-8',newline='')))
seen={(r['source_id'],r['pdf_page'],r['purpose']) for r in old}
ids={d.name for d in (root/'run1a/text').iterdir() if d.is_dir() and re.match(r'iar-|man-environment-|puratattva-',d.name)}
ids.update(d.name for d in (a.raw/'text').iterdir() if d.is_dir())
ids.update('surkotada-1990 kanmer-ch6 kanmer-ch8-held shikarpur-2009-held khirsara-2017-held nagwada-2018-held juna-khatiya-2021-held'.split())
dho=[];summary=[]
for s in sorted(ids):
    dirs=[root/'run1a/text'/s,a.raw/'text'/s]
    pages={p.name:p for d in dirs if d.exists() for p in d.glob('p*.txt')}
    for name,pp in sorted(pages.items()):
        n=str(int(re.search(r'\d+',pp.stem)[0]));t=pp.read_text(encoding='utf-8',errors='replace')
        key=(s,n,'context')
        if not any(r['source_id']==s and r['pdf_page']==n for r in old):
            old.append(dict(source_id=s,pdf_page=n,purpose='context',image_viewed='no'))
        if re.search(r'\bDholavira\b',t,re.I):dho.append(dict(source_id=s,pdf_page=n,purpose='keyword screen or shared context; excluded from object extraction'))
    summary.append(dict(source_id=s,pages_screened=len(pages)))
with (a.out/'pages-read-G.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['source_id','pdf_page','purpose','image_viewed']);w.writeheader();w.writerows(sorted(old,key=lambda r:(r['source_id'],int(r['pdf_page']),r['purpose'])))
with (a.out/'dholavira-pages-noted-G.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['source_id','pdf_page','purpose']);w.writeheader();w.writerows(dho)
(a.out/'screen-summary-G.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'sources_screened':len(summary),'pages_screened':sum(r['pages_screened'] for r in summary),'Dholavira_context_pages':len(dho)}))
