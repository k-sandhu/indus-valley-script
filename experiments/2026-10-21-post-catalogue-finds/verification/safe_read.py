"""Limited identity display and exposure records; use isolated Python."""
import csv
import json
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8',errors='backslashreplace')

ROOT=Path.cwd()
BASE=ROOT/'experiments/2026-10-21-post-catalogue-finds'
OUT=BASE/'verification'
RAW=ROOT/'data/raw/2026-10-21-post-catalogue-finds'

def word(codes):
    return ''.join(map(chr,codes))

BLOCKED=[word(c) for c in [
    [117,110,105,99,111,114,110],[98,117,108,108],[114,104,105,110,111,99,101,114,111,115],
    [101,108,101,112,104,97,110,116],[116,105,103,101,114],[98,117,102,102,97,108,111],
    [122,101,98,117],[103,111,97,116],[97,110,116,101,108,111,112,101],
    [109,111,116,105,102],[97,110,105,109,97,108],[115,105,103,110,32,115,101,113,117,101,110,99,101],
    [114,101,97,100,115,32,97,115]]]
RESTRICTED=re.compile(r'\b(?:'+ '|'.join(map(re.escape,BLOCKED))+r')\b',re.I)
EXTRA=re.compile(r'\b(?:signs?|characters?|letters?|symbols?|depict\w*|represent\w*|design|device|scene|figural|obverse|reverse|inscription|legend|measure\w*|weigh\w*|size|length|width|height|thick\w*|diameter|pict\w*|fish|bird|snake|tree|human|figure of|standing|seated|horn\w*|face[ds]?)\b',re.I)
UNIT=re.compile(r'\b\d+(?:[.,]\d+)?\s*(?:m{2}|c[m]|kg|gms?|grams?)\b',re.I)

def clean_line(s):
    if RESTRICTED.search(s) or EXTRA.search(s) or UNIT.search(s):
        return None
    if re.search(r'\d\s*[x×X]\s*\d|\b(?:dia|ht|geometric|illegible)\b',s,re.I): return None
    s=re.sub(r'[\ue000-\uf8ff\U00010000-\U0010ffff]','[redacted]',s)
    return s

def safe_print(s, prefix=''):
    t=clean_line(s)
    if t is None:
        return
    chunks=re.findall(r'\S+',t)
    for i in range(0,len(chunks),10):
        print(prefix+' '.join(chunks[i:i+10]))

def exposure(source,page,path,purpose):
    log=OUT/'exposure-log.csv'
    exists=log.exists()
    with log.open('a',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        if not exists:
            w.writerow(['source_id','pdf_page','path','agent','access','purpose','image_viewed'])
        w.writerow([source,page,str(path.relative_to(ROOT)),'GPT-6 / Codex API','filtered identity text',purpose,'no'])

def page_path(source,page):
    roots=[RAW/('run2'+p)/'text'/source for p in 'NGDPEF']+[RAW/'run1a/text'/source]
    options=[]
    for root in roots:
        if not root.exists(): continue
        for p in sorted(root.glob('*.txt')):
            nums=re.findall(r'\d+',p.stem)
            if nums and int(nums[-1])==int(page): options.append(p)
    return options[0] if options else None

def identity_view(source,page,purpose):
    p=page_path(source,page)
    print('PAGE',source,page,'MISSING' if not p else '')
    if not p: return
    exposure(source,page,p,purpose)
    lines=p.read_text(encoding='utf-8-sig',errors='replace').splitlines()
    for i,s in enumerate(lines,1):
        # The Dholavira context tables put identity before descriptive columns.
        if source=='bisht-2015-held' and 264<=int(page)<=275:
            m=re.match(r'^\s*(\d{1,3})\.\s+(\d{1,6}|NM)\b(?:\s+(\d{1,2}[x×]\d{1,3}(?:[x×+]\d{1,3})*(?:[x×]\d+)?))?',s,re.I)
            if m: print(i,'catalogue',m[1],'registration',m[2],'grid',m[3] or 'unreadable')
            m=re.search(r'\b(Castle|Citadel|Middle Town|Midle Town|Lower Town|East|North ER)\b(?:\s+(VI(?:-\s*\?)?|[IV]+))?',s,re.I)
            if m: print(i,'area',m[1],'period',m[2] or '')
            continue
        # Emit fields of a closed identity vocabulary. Never emit descriptions.
        if re.fullmatch(r'\s*\d{1,4}\s*',s): print(i,'printed page candidate',s.strip())
        for rx,label in [
            (r'\b(?:19|20)\d{2}\s*[-–/]\s*(?:\d{2}|(?:19|20)\d{2})\b','season'),
            (r'\b(?:Fig(?:ure)?\.?|Pl(?:ate)?\.?)\s*[IVXLCDM\d]+(?:[.:-]\d+)?(?:\s*\([a-z]\))?','locator'),
            (r'\b(?:BSR|DHR|FRM|RGR|KMR|KNM|SKP)\s*[- ]?\d+\b','registration'),
            (r'\b(?:trench|square|grid|room|lot|mound|block|area|period|phase|layer)\s*[A-Z]?\s*\d+(?:[-/.]\d+)*(?:\s*[A-Z])?\b','context'),
            (r'\b(?:inscribed\s+)?(?:seals?|sealings?|tablets?|tags?|potsherds?|sherds?|rods?|tools?|pottery|terracotta|steatite|ivory|bone)\b','type or material'),
            (r'\b(?:photographs?|drawings?|transcription|inscribed|uninscribed|possibly|uncertain)\b','publication cue'),
        ]:
            for m in re.finditer(rx,s,re.I): print(i,label,m.group())
        for m in re.finditer(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:inscribed\s+)?(?:steatite\s+|terracotta\s+|square\s+)?(?:seals?|sealings?|tablets?|potsherds?|sherds?|rods?)\b',s,re.I):
            print(i,'object quantity',m.group())
        for m in re.finditer(r'\b(?:not|no|without)\s+(?:inscribed|inscription)\b',s,re.I):print(i,'status cue negative')

def main():
    mode=sys.argv[1]
    if mode=='inventory':
        for source,page in [('bisht-2015-held',275),('hrp-parpola-2019',4),('gdh-jamison-2017',9),('farmana-2006-08',385)]:
            p=page_path(source,page)
            print(source,page,str(p.relative_to(ROOT)) if p else 'MISSING')
    elif mode=='page':
        identity_view(sys.argv[2],sys.argv[3],'blind sample' if len(sys.argv)<5 else sys.argv[4])
    elif mode=='blind-pages':
        with (OUT/'blind-assignments.csv').open(encoding='utf-8',newline='') as f: assignments=list(csv.DictReader(f))
        pairs=sorted({(r['primary_publication'],int(n)) for r in assignments for n in re.findall(r'\d+',r['pdf_page'])})
        for source,page in pairs:
            if len(sys.argv)>2 and source!=sys.argv[2]: continue
            identity_view(source,page,'blind sample')
    elif mode=='omission-pages':
        with (OUT/'omission-assignments.csv').open(encoding='utf-8',newline='') as f: assignments=list(csv.DictReader(f))
        start=int(sys.argv[2]) if len(sys.argv)>2 else 0
        end=int(sys.argv[3]) if len(sys.argv)>3 else len(assignments)
        for r in assignments[start:end]:identity_view(r['source_id'],r['pdf_page'],'omission sample')
    elif mode=='docs':
        for name in sys.argv[2:]:
            p=ROOT/name
            print('DOCUMENT',name)
            txt=p.read_text(encoding='utf-8-sig',errors='replace')
            if p.name=='registry.json':
                reg=json.loads(txt)
                print('Registry loaded; top-level structure:',type(reg).__name__)
                continue
            for i,line in enumerate(txt.splitlines(),1): safe_print(line,f'{i}: ')

if __name__=='__main__':
    try: main()
    except OSError:
        try: (OUT/'WRITE-FAILURE.txt').write_text('Stopped after an input/output error.\n',encoding='utf-8')
        finally: raise SystemExit('Stopped after an input/output error.')
