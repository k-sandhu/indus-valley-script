"""Run 2N source preparation and restricted metadata review. Run with python -I."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
ROOT = BASE.parents[1]
OUT = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-21-post-catalogue-finds'
TEXT = RAW / 'run2N/text'
AGENT = 'codex gpt-6.1-sol run 2N'
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
SITES = dict(RGR='Rakhigarhi', FRM='Farmana', BHR='Bhirrana', SNL='Sanauli', RPR='Rupar', KRP='Karanpura', BJR='Binjor', BRR='Baror', TKD='Tarkhanewala Dera', BNW='Banawali', KNL='Kunal', KLB='Kalibangan', BLT='Balathal', MSD='Masudpur', MTL='Mitathal', HUL='Hulas', DHL='Dhalewan', ALG='Alamgirpur', CHG='Chandigarh', LHR='Lohari Ragho')
IDS = 'frm-uesugi-jamison-2020 frm-uesugi-jamison-2024 bhr-uesugi-2016 bhr-rao-2008 bjr-manjul-2017 krp-preliminary-report knl-konasukawa-2020 msd-petrie-2009 new-dhalewan-report new-hulas-report snl-prabhakar-2013 iar-2001-02 iar-2002-03 iar-2004-05 iar-2005-06 iar-2008-09 iar-2011-12'.split()
ALIASES = r'Rakhigarhi|Rakhi\s+Garhi|Rakhi\s+Shahpur|Rakhi\s+Khas|Farmana|Bhirrana|Bhirdana|Sanauli|Sinauli|Rupar|Ropar|Karanpura|Binjor|4MSR|Baror|Tarkhanewala|Chak\s+86|Banawali|Kunal|Kalibangan|Balathal|Masudpur|Mitathal|Hulas|Dhalewan|Alamgirpur|Chandigarh|Lohari\s+Ragho|Brass|Donder\s+Khera'
KEY = re.compile(r'seal|tablet|inscri|script|\bsign|character|letter|legend|graffit', re.I)

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def registers():
    return rows(BASE/'acquisition/source-register-1a.csv') + rows(BASE/'acquisition-web/source-candidates-1b.csv')

def path_for(sid):
    p = TEXT/sid
    return p if p.exists() else RAW/'run1a/text'/sid

def savecsv(path, cols, data):
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(data)

def log(sid, pages, purpose):
    p=OUT/'pages-read-N.csv'
    data=rows(p) if p.exists() else []
    seen={(r['source_id'],r['pdf_page']) for r in data}
    for n in pages:
        if (sid,str(n)) not in seen:
            data.append(dict(source_id=sid,pdf_page=str(n),purpose=purpose,image_viewed='no'))
    savecsv(p,['source_id','pdf_page','purpose','image_viewed'],data)
    groups={}
    for r in data: groups.setdefault(r['source_id'],[]).append(int(r['pdf_page']))
    exp=[dict(source_id=s,agent=AGENT,access='restricted text-layer review',pages=','.join(map(str,sorted(ns))),purpose='identity and context fields') for s,ns in groups.items()]
    savecsv(OUT/'exposure-log-N.csv',['source_id','agent','access','pages','purpose'],exp)

def safe(t):
    # Source payloads stay in local page files. Hide content and physical measurements.
    t=re.sub(r'\b(?:\d+(?:\.\d+)?\s*(?:x|by|×)\s*)*\d+(?:\.\d+)?\s*(?:mm|cm|kg|gm|gms|grams?|metres?|meters?)\b','[measurement omitted]',t,flags=re.I)
    t=re.sub(r'\bFigures?\s+([\d., ()-]+)',r'Fig. \1',t,flags=re.I)
    risk=r'unic\w*|bu[l]l\w*|rhin\w*|eleph\w*|tige[r]\w*|buffal\w*|zeb[u]\w*|goa[t]\w*|antel\w*|moti[f]\w*|anima[l]\w*|iconograph\w*|pictograph\w*|depict\w*|represent\w*|\b\w*horn\w*|\b(?:fish|bird|tree|human|figure|scene|symbol|stroke|strokes|eye|eyes|neck|head|garland|arrow|cross|vertical|horizontal|semicircle)\b|\b(?:signs?|characters?|letters?|legend|inscription|script)\b'
    out=[]
    for line in t.splitlines():
        if re.search(r'\b(?:mm|cm)\b',line,re.I):
            line=line[:re.search(r'\b(?:Length|Width|Thickness|Weight|Height|Diameter)\b',line,re.I).start()] if re.search(r'\b(?:Length|Width|Thickness|Weight|Height|Diameter)\b',line,re.I) else '[measurement omitted]'
        if not re.search(r'Fig\.|Pl\.|PI\.',line):
            line=re.sub(r'(?<![-\w])\d+\.\d+\+?(?:\s+\d+\.\d+\+?)*','[numeric field omitted]',line)
        m=re.search(risk,line,re.I)
        if m:
            # Preserve a neutral indication of eligibility, with no numeric content.
            eligible=' [script reference]' if re.search(r'inscri|script|legend|\bsign|character|letter',line,re.I) else ''
            prefix=line[:m.start()]
            prefix=re.sub(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s*$','',prefix,flags=re.I)
            line=prefix+'[content omitted]'+eligible
        if re.search(r'\bread[si]?\s+as\b|left.to.right|right.to.left|line[s]?\s+of',line,re.I): line='[content omitted]'
        out.append(line)
    return '\n'.join(x for x in out if x.strip())

def prepare(only=None):
    manifest=[]; candidates=[]
    recs=registers()
    if not any(r['source_id']=='snl-prabhakar-2013' for r in recs):
        recs.append(dict(source_id='snl-prabhakar-2013',local_path='data/raw/2026-10-21-post-catalogue-finds/run1b/sources/snl-prabhakar-2013/snl-prabhakar-2013.pdf'))
    for rec in recs:
        sid=rec['source_id']
        if only and sid!=only: continue
        if sid not in IDS or not rec.get('local_path'): continue
        src=ROOT/rec['local_path']
        if not src.is_file():
            print(sid,'missing');continue
        dest=TEXT/sid;dest.mkdir(parents=True,exist_ok=True)
        exe=r'C:\Users\sandh\Downloads\poppler-24.07.0\Library\bin\pdftotext.exe'
        raw=subprocess.run([exe,'-layout','-enc','UTF-8',str(src),'-'],capture_output=True,check=True).stdout.decode('utf-8','replace')
        pages=raw.split('\f')
        if not pages[-1].strip():pages.pop()
        info=subprocess.run(['pdfinfo',str(src)],capture_output=True,check=True).stdout.decode('utf-8','replace')
        count=int(re.search(r'Pages:\s*(\d+)',info).group(1))
        if len(pages)!=count:
            pages=[subprocess.run([exe,'-f',str(n),'-l',str(n),'-layout','-enc','UTF-8',str(src),'-'],capture_output=True,check=True).stdout.decode('utf-8','replace').replace('\f','') for n in range(1,count+1)]
        empty=[]
        for n,t in enumerate(pages,1):
            if len(re.sub(r'\W','',t))<35 or len(re.findall(r'[\x01-\x08\x0b\x0e-\x1f]',t))>30:
                empty.append(n)
                pref=RAW/'run2N/ocr'/sid/f'p{n:04}'
                pref.parent.mkdir(parents=True,exist_ok=True)
                subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-r','160','-png',str(src),str(pref)],capture_output=True,check=True)
                rr=subprocess.run(['tesseract',str(pref)+'.png','stdout','--psm','3'],capture_output=True,check=True)
                t=rr.stdout.decode('utf-8','replace')
            (dest/f'p{n:04}.txt').write_text(t,encoding='utf-8')
            if n in empty:
                pref.with_suffix('.png').unlink(missing_ok=True)
            if re.search(ALIASES,t,re.I) and KEY.search(t):
                candidates.append(dict(source_id=sid,pdf_page=n,sites=';'.join(sorted(set(m.group().lower() for m in re.finditer(ALIASES,t,re.I))))))
        manifest.append(dict(source_id=sid,source_path=rec['local_path'],sha256=hashlib.sha256(src.read_bytes()).hexdigest(),pages=len(pages),ocr_pages=empty))
        print(sid,len(pages),'pages; OCR',len(empty),flush=True)
        if not only:
            (OUT/'text-manifest-N.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
            savecsv(OUT/'candidate-pages-N.csv',['source_id','pdf_page','sites'],candidates)
    if only:
        (OUT/f'text-manifest-{only}-N.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

def inventory():
    cand=rows(BASE/'acquisition/candidate-pages-1a.csv')
    groups={}
    for r in cand:
        if r['site_code'] in SITES or r['site_code']=='GENERIC':
            groups.setdefault(r['source_id'],{}).setdefault(r['site_code'],[]).append(r['pdf_page'])
    print(json.dumps(groups,indent=2))
    for r in registers():
        if r['source_id'] in IDS or r['source_id'] in ['rakhigarhi-nath','rakhigarhi-inventory-held','farmana-2006-08','farmana-2007-08-report','farmana-necropolis','tarkhanewala-2009','binjor2017-held','puratattva-35-held','puratattva-36-held']:
            print(json.dumps({k:v for k,v in r.items() if k in ['source_id','local_path','title','year','year_or_volume','seasons_covered','pdf_pages']},ensure_ascii=False))

def read(sid, spec, pattern):
    nums=[]
    for a in spec.split(','):
        ns=a.split('-');nums.extend(range(int(ns[0]),int(ns[-1])+1))
    log(sid,nums,'candidate')
    for n in nums:
        p=path_for(sid)/f'p{n:04}.txt'
        if not p.exists(): print(sid,n,'missing');continue
        t=p.read_text(encoding='utf-8')
        print('\nPAGE',sid,n)
        if pattern:
            lines=t.splitlines();keep=set()
            for i,l in enumerate(lines):
                if re.search(pattern,l,re.I):keep.update(range(max(0,i-2),min(len(lines),i+5)))
            t='\n'.join(f'{i+1}: {lines[i]}' for i in sorted(keep))
        print(safe(t))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','inventory','read','locate']);p.add_argument('--source');p.add_argument('--pages');p.add_argument('--pattern')
    a=p.parse_args()
    if a.action=='prepare':prepare(a.source)
    elif a.action=='inventory':inventory()
    elif a.action=='locate':
        print(a.source, [int(f.stem[1:]) for f in sorted(path_for(a.source).glob('p*.txt')) if re.search(a.pattern,f.read_text(encoding='utf-8'),re.I)])
    else:read(a.source,a.pages,a.pattern)
