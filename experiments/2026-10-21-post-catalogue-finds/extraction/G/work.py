"""Local extraction utilities. Run with Python isolated mode and explicit roots."""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

P = argparse.ArgumentParser()
P.add_argument('mode')
P.add_argument('root', type=Path)
P.add_argument('out', type=Path)
P.add_argument('raw', type=Path)
P.add_argument('args', nargs='*')
A = P.parse_args()
A.out.mkdir(parents=True, exist_ok=True)
A.raw.mkdir(parents=True, exist_ok=True)
BASE = A.root / 'experiments/2026-10-21-post-catalogue-finds'
RAW = A.root / 'data/raw/2026-10-21-post-catalogue-finds'
def csvread(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
REG = csvread(BASE / 'acquisition/source-register-1a.csv')
REG += csvread(BASE / 'acquisition-web/source-candidates-1b.csv')
SOURCES = {r['source_id']: r for r in REG}
SITES = {r['site_code']: r for r in csvread(BASE / 'selection/sites-seed.csv')}
CODES = 'KHR KNM SKP GDH NGW PDR BTD KNT JKR KBD NVN SKT DSL RJD LTL DMB JNK PBM PTH NGS KNW RNG PRB'.split()
ALIASES = {c: [SITES.get(c,{}).get('site',c)] + SITES.get(c,{}).get('aliases','').split('|') for c in CODES}
ALIASES.update({'JNK':['Juna Khatiya','Juna Khatiya','Khatiya'], 'PBM':['Pabumath'], 'PTH':['Pithad'], 'NGS':['Nageshwar'], 'KNW':['Kanewal'], 'RNG':['Rangpur'], 'PRB':['Prabhas Patan','Somnath']})
ALIASES.update({'UMT':['Umta'], 'SYT':['Siyot'], 'STM':['Shaktari','Moti Pipli']})
ALIASES['GDH'] = ['Bagasra','Gola Dhoro']
ALIASES['DSL'] = ['Desalpar','Desalpur']
ALIASES['RJD'] = ['Rojdi','Rodji']
KEY = re.compile(r'seal|tablet|inscri|script|sign|character|letter|legend|graffit', re.I)
BAD = [''.join(map(chr, v)) for v in [
 [117,110,105,99,111,114,110], [98,117,108,108], [114,104,105,110,111,99,101,114,111,115],
 [101,108,101,112,104,97,110,116], [116,105,103,101,114], [98,117,102,102,97,108,111],
 [122,101,98,117], [103,111,97,116], [97,110,116,101,108,111,112,101],
 [109,111,116,105,102], [97,110,105,109,97,108],
 [115,105,103,110,32,115,101,113,117,101,110,99,101], [114,101,97,100,115,32,97,115]]]
BANNED = re.compile(r'\b(?:' + '|'.join(map(re.escape, BAD)) + r')\b|\b\d+(?:\.\d+)?\s*(?:m{2}|c[m])\b', re.I)
NUM = r'(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|single|several|many|multiple|few)'
def safe(t):
    t = re.sub(r'\n\s*\n', '\n', t)
    t = re.sub(r'(?im)^.*(?:Vats.?\s*(?:sign|\d)|Marshall.?s?\s*(?:sign|[IVXLCDM]+\b)|[\u0900-\u097f]).*$', '[content omitted]', t)
    t = re.sub(r'(?im)^.*(?:inscription|characters?|signs?|symbols?)\b.*$', lambda m: re.sub(r'(?i)(?:inscription|characters?|signs?|symbols?)\b.*','[content omitted]',m[0]),t)
    t = re.sub(r'(?i)\b(?:'+ '|'.join(map(re.escape,BAD)) +r')\b[^\n.!?]*', '[content omitted]', t)
    t = re.sub(r'(?i)\b'+NUM+r'(?:\s*[-–]\s*'+NUM+r')?\s*[- ]?(?:Indus\s+|Harappan\s+)?(?:signs?|characters?|letters?|lines?|symbols?|strokes?)\b', '[content omitted]', t)
    t = re.sub(r'(?i)(?:right\s*[-–]?\s*to\s*[-–]?\s*left|left\s*[-–]?\s*to\s*[-–]?\s*right|clockwise|counterclockwise|dextrorse|sinistrorse)', '[content omitted]', t)
    t = re.sub(r'(?i)\b(?:readings?|reads?|transliterat\w*|depict\w*|represent\w*|portray\w*|engraved with|incised with|bearing the figure|in the form of|legend consists|signs? consist)[^\n.!?]*', '[content omitted]', t)
    t = re.sub(r'(?i)\b(?:fish|crocodile|horse|camel|snake|deer|bird|human|pipal|peepal|swastika|cross|humped|horned|ibex|ram|ewe|tortoise|scorpion|hare|rabbit|palm|tree|taurus|caprid|bovid)\b[^\n.!?]*', '[content omitted]', t)
    t = re.sub(r'(?i)\b(?:length|breadth|width|height|thickness|diameter|weight|weighing|measures?|measuring|dimensions?)\b[^\n;.!?]*', '[measurement omitted]', t)
    t = BANNED.sub('[omitted]', t)
    return t
def pages(s):
    d = A.raw / 'text' / s
    if not d.exists(): d = RAW / 'run1a/text' / s
    return sorted(d.glob('p*.txt'))
def pagepath(s,n):
    return next((p for p in pages(s) if int(re.search(r'\d+',p.stem)[0]) == int(n)), None)
def log(s,n,purpose='candidate'):
    p = A.out / 'pages-read-G.csv'
    old = csvread(p) if p.exists() else []
    if not any(r['source_id']==s and r['pdf_page']==str(n) and r['purpose']==purpose for r in old):
        with p.open('a',encoding='utf-8',newline='') as f:
            w=csv.writer(f)
            if not old: w.writerow(['source_id','pdf_page','purpose','image_viewed'])
            w.writerow([s,n,purpose,'no'])
def contents(p): return p.read_text(encoding='utf-8',errors='replace')
if A.mode == 'inventory':
    for s in A.args:
        r = SOURCES.get(s,{})
        print(s, 'year='+str(r.get('year',r.get('year_or_volume',''))), 'pages='+str(len(pages(s))), 'path='+str(r.get('local_path','')))
elif A.mode == 'extract':
    records=[]
    for s in A.args:
        p = next((RAW/'run1b/sources'/s).glob('*.pdf'),None)
        if p is None: p = next((RAW/'run1a/sources'/s).glob('*.pdf'),None)
        if p is None:
            print(s,'missing'); continue
        d = A.raw/'text'/s
        d.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(['pdftotext','-layout','-enc','UTF-8',str(p),'-'],capture_output=True,check=True)
        texts=result.stdout.decode('utf-8',errors='replace').split('\f')
        if not texts[-1].strip():texts.pop()
        blank=[]
        for n,t in enumerate(texts,1):
            (d/f'p{n:04d}.txt').write_text(t,encoding='utf-8')
            if len(re.findall('[A-Za-z]',t))<30:blank.append(n)
        records.append({'source_id':s,'pdf_pages':len(texts),'sparse_pages':blank,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'pdftotext -layout'})
        print(s,len(texts),'sparse',','.join(map(str,blank)),flush=True)
    (A.out/'text-extraction-G.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
elif A.mode == 'scan':
    found=csvread(A.out/'scan-G.csv') if (A.out/'scan-G.csv').exists() else []
    for s in A.args:
        hits=[]
        for p in pages(s):
            t=contents(p)
            codes=[c for c,aliases in ALIASES.items() if any(a and re.search(r'\b'+re.escape(a)+r'\b',t,re.I) for a in aliases)]
            if codes and KEY.search(t):
                n=int(re.search(r'\d+',p.stem)[0]); hits.append((n,','.join(codes)))
                record={'source_id':s,'pdf_page':n,'site_codes':';'.join(codes)}
                if not any(str(r['source_id'])==s and str(r['pdf_page'])==str(n) for r in found):found.append(record)
        print(s, ' '.join(f'{n}:{c}' for n,c in hits))
    with (A.out/'scan-G.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['source_id','pdf_page','site_codes']);w.writeheader();w.writerows(found)
elif A.mode == 'read':
    s=A.args[0]
    nums=[]
    for a in A.args[1:]:
        if '-' in a:
            x,y=map(int,a.split('-')); nums.extend(range(x,y+1))
        else:nums.append(int(a))
    for n in nums:
        p=pagepath(s,n)
        print('\nSOURCE',s,'PDF',n)
        if p is None: print('PAGE MISSING');continue
        log(s,n)
        print(safe(contents(p)))
elif A.mode == 'locate':
    for s in A.args:
        print('\nSOURCE',s)
        for p in pages(s):
            t=contents(p)
            if re.search(r'\b(?:seals?|sealings?|inscribed|graffiti|script material)\b',t,re.I):
                n=int(re.search(r'\d+',p.stem)[0])
                lines=t.splitlines()
                matches=[safe(l.strip()) for l in lines if re.search(r'\b(?:seals?|sealings?|inscribed|graffiti|script material)\b',l,re.I)]
                print(n, ' | '.join(matches)[:500])
elif A.mode == 'excerpt':
    for s in A.args:
        print('\nSOURCE',s)
        for p in pages(s):
            t=contents(p)
            if not KEY.search(t): continue
            n=int(re.search(r'\d+',p.stem)[0]);log(s,n)
            lines=t.splitlines()
            keep=set()
            for i,l in enumerate(lines):
                if re.search(r'\b(?:seals?|sealings?|tablets?|inscri\w*|graffiti|script|Harappan signs?)\b',l,re.I):
                    keep.update(range(max(0,i-2), min(len(lines),i+4)))
            print('PDF',n)
            print(safe('\n'.join(lines[i] for i in sorted(keep))))
elif A.mode == 'ocr':
    from concurrent.futures import ThreadPoolExecutor
    s=A.args[0]
    p=next((RAW/'run1b/sources'/s).glob('*.pdf'),None)
    if p is None:p=next((RAW/'run1a/sources'/s).glob('*.pdf'),None)
    nums=[]
    for v in A.args[1:]:
        if '-' in v:
            x,y=map(int,v.split('-'));nums.extend(range(x,y+1))
        else:nums.append(int(v))
    d=A.raw/'text'/s;d.mkdir(parents=True,exist_ok=True)
    def ocr(n):
        target=A.raw/'ocr'/s/f'p{n:04d}'
        target.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['pdftoppm','-f',str(n),'-l',str(n),'-singlefile','-r','160','-png',str(p),str(target)],capture_output=True,check=True)
        r=subprocess.run(['tesseract',str(target)+'.png','stdout','-l','eng'],capture_output=True,check=True)
        (d/f'p{n:04d}.txt').write_text(r.stdout.decode('utf-8',errors='replace'),encoding='utf-8')
        Path(str(target)+'.png').unlink(missing_ok=True)
        return n
    with ThreadPoolExecutor(max_workers=3) as pool:
        for n in pool.map(ocr,nums): print(s,n,'OCR complete',flush=True)
elif A.mode == 'iar':
    for d in sorted((RAW/'run1a/text').glob('iar-*'))+sorted((A.raw/'text').glob('iar-*')):
        hits=[]
        for p in sorted(d.glob('p*.txt')):
            t=contents(p)
            if re.search(r'\b(?:GUJARAT|MAHARASHTRA)\b',t):
                n=int(re.search(r'\d+',p.stem)[0]); hits.append(n)
        print(d.name,','.join(map(str,hits)))
elif A.mode == 'html':
    from html.parser import HTMLParser
    class Text(HTMLParser):
        def __init__(self): super().__init__();self.parts=[];self.skip=0
        def handle_starttag(self,tag,attrs):
            if tag in ('script','style'): self.skip+=1
        def handle_endtag(self,tag):
            if tag in ('script','style'):self.skip=max(0,self.skip-1)
            if tag in ('p','div','li','tr','h1','h2','h3'):self.parts.append('\n')
        def handle_data(self,data):
            if not self.skip:self.parts.append(data)
    for s in A.args:
        p=next((RAW/'run1b/sources'/s).glob('*.html'),None)
        parser=Text();parser.feed(contents(p))
        t=' '.join(parser.parts)
        d=A.raw/'text'/s;d.mkdir(parents=True,exist_ok=True)
        (d/'p0001.txt').write_text(t,encoding='utf-8')
        print(s,'HTML text extracted')
elif A.mode == 'meta':
    for s in A.args:
        print(s,json.dumps({k:v for k,v in SOURCES[s].items() if k in ('title','authors','authors_or_editors','year','year_or_volume','venue','local_path','notes')},ensure_ascii=False))
elif A.mode == 'identity':
    for s in A.args:
        print('\nSOURCE',s)
        for p in pages(s):
            n=int(re.search(r'\d+',p.stem)[0]);t=contents(p)
            chunks=[]
            for l in t.splitlines():
                l=l.strip()
                if re.search(r'\bBSR\s*\d+|\b(?:Trench|Layer|Season)\b|\b(?:Figure|Fig\.)\s*\d+',l,re.I):
                    if re.search(r'\b(?:measurement|maximum|minimum|square|carv|engrav|inscript|character|boss|style|color|colour)\b',l,re.I):continue
                    if BANNED.search(l):continue
                    chunks.append(safe(l))
            if chunks:
                log(s,n);print(n,' | '.join(chunks))
elif A.mode == 'frames':
    for s in sorted(k for k in SOURCES if k.startswith('kanmer-frame-')):
        r=SOURCES[s]
        print(s,r.get('local_path',''))
        for p in pages(s):
            t=contents(p)
            if re.search(r'\b(?:seal|sealing|tablet|script material|K[A-Z]?\s*[-/]?\s*\d{3,})',t,re.I):
                log(s,1)
                nums=re.findall(r'\b(?:K[A-Z]?[ -]?\d{2,}(?:[-/]\d+)*|\d{2,}[-/]\d{2,}(?:[-/]\d+)*)\b',t)
                print('ids',','.join(dict.fromkeys(nums))[:700])
elif A.mode == 'kanmer':
    root=A.root/'experiments/2026-10-02-six-hour/kanmer-physical-use'
    pairs=[('kanmer-frame-55','acquisition-remaining-chapter-pages'),('kanmer-frame-22','acquisition-chapter-render'),('kanmer-frame-7','acquisition-chapter-extra')]
    for s,folder in pairs:
        d=A.raw/'text'/s;d.mkdir(parents=True,exist_ok=True)
        for p in (root/'local-witness'/folder).glob('*-text.txt'):
            m=re.search(r'chapter8-page(\d+)',p.name)
            if not m:continue
            n=int(m[1]);(d/f'p{n:04d}.txt').write_text(contents(p),encoding='utf-8')
        print(s,len(pages(s)))
elif A.mode == 'hits':
    c=A.args[0]
    candidates=csvread(BASE/'acquisition/candidate-pages-1a.csv')
    ps={(r['source_id'],int(r['pdf_page'])) for r in candidates if r['site_code']==c}
    for s,n in sorted(ps):
        if s in ('bisht-2015-held','nuhato-2018-held','rakhigarhi-nath','farmana-2006-08','farmana-2007-08-report'):continue
        p=pagepath(s,n)
        if not p:continue
        t=contents(p);log(s,n)
        if not any(re.search(re.escape(a),t,re.I) for a in ALIASES[c]):continue
        snippets=[]
        for m in re.finditer(r'\b(?:seal(?:s|ing|ings)?|tablet[s]?|inscri\w*|graffiti)\b',t,re.I):
            a=max(0,m.start()-85);b=min(len(t),m.end()+190)
            chunk=re.sub(r'\s+',' ',t[a:b])
            snippets.append(safe(chunk))
        if snippets:print(s,n,' | '.join(snippets)[:1800])
elif A.mode == 'fields':
    for s in A.args:
        print('\nSOURCE',s)
        for p in pages(s):
            t=re.sub(r'\s+',' ',contents(p)); n=int(re.search(r'\d+',p.stem)[0]);log(s,n)
            matches=[]
            patterns=[r'\b\d{2}-\d{3,}\b',r'\b(?:No\.?|Number|Reg\.?|Registration)\s*[:.]?\s*\d+[A-Z]?(?:[-/]\d+)*',r'\b(?:Tr\.|Trench)\s*[A-Z]+\s*\d+(?:\s*[/,]\s*[A-Z0-9]+)*',r'\b(?:Layer|Qua\.|Period|KMR)\s*[A-Z0-9]+(?:\s*[A-Z])?',r'\b(?:[Ff]ig(?:ure)?\.?|Plate)\s*\d+(?:\.\d+)?',r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:terracotta\s+|steatite\s+|clay\s+|inscribed\s+|Harappan\s+)*(?:seals?|sealings?|tablets?|potsherds?)\b']
            for pat in patterns: matches+=re.findall(pat,t)
            if matches:print(n,' | '.join(matches))
elif A.mode == 'schema':
    for arg in A.args:
        value=json.loads(contents(A.root/arg))
        print(arg)
        if isinstance(value,dict):
            print('keys',list(value))
            for k,v in value.items():
                if isinstance(v,list):print(k,'items',len(v),'schema',list(v[0]) if v and isinstance(v[0],dict) else '')
        elif isinstance(value,list):print('items',len(value),'schema',list(value[0]) if value and isinstance(value[0],dict) else '')
elif A.mode == 'kanmer-entries':
    entries=[]
    pairs=[('kanmer-frame-55',1),('kanmer-frame-7',2),('kanmer-frame-7',3),('kanmer-frame-22',4),('kanmer-frame-22',5),('kanmer-frame-22',6)]+[('kanmer-frame-55',n) for n in range(7,14)]
    for s,n in pairs:
        p=pagepath(s,n)
        if p is None:continue
        t=re.sub(r'\s+',' ',contents(p));log(s,n)
        blocks=re.split(r'(?<![\d.])(\d{1,2})\.\s*(?=[A-Z])',t)
        print('\nPAGE',n,s)
        for i in range(1,len(blocks),2):
            num=blocks[i];b=blocks[i+1]
            if int(num)>24:continue
            opening=re.split(r'(?i)\b(?:sign|graffiti|inscript|depict|engraved|bearing|incised|with|which|showing|has|is|of the|measures)|\(',b)[0][:140]
            opening=';'.join(re.findall(r'(?i)\b(?:steatite|terracotta|clay|Red Ware|Red slip ware|Black slipped ware|body sherd|rim sherd|jar|seal|sealing|tablet|potsherd)\b',opening))
            if BANNED.search(opening):opening='[description omitted]'
            ids=re.findall(r'\bNo\.?\s*\d+(?:[-/]\d+)*',b)
            ctx=re.findall(r'\([^)]*(?:Tr\.|Trench|Layer|Qua\.)[^)]*\)',b)
            types=[x for x in ('seal','sealing','sherd','pot','tablet') if re.search(r'\b'+x+r'\w*',b,re.I)]
            scope=bool(re.search(r'(?:Indus|Harappan)\s+(?:sign|character|letter|script)|(?:sign|character|letter|script).{0,30}(?:Indus|Harappan)',b,re.I))
            ref=bool(re.search('Parpola|Mahadevan|Vats',b,re.I))
            qual=bool(re.search(r'\b(?:similar|resemble|may|perhaps|possibly|probabl)\w*',b,re.I))
            entries.append({'source_id':s,'page':n,'entry':num,'opening':opening,'ids':ids,'context':ctx,'types':types,'explicit_scope':scope,'list_reference':ref,'qualification':qual})
            print(num,opening,'; ids=',','.join(ids),'; context=',','.join(ctx),'; classes=',','.join(types),'; scope/ref/qualified=',scope,ref,qual)
    for record in entries:record['context']=[{'identity_context':x} for x in record['context']]
    (A.out/'kanmer-entry-fields-G.json').write_text(json.dumps(entries,indent=2),encoding='utf-8')
elif A.mode == 'query':
    s,pattern=A.args[:2]
    for p in pages(s):
        t=re.sub(r'\s+',' ',contents(p));n=int(re.search(r'\d+',p.stem)[0])
        for m in re.finditer(pattern,t,re.I):
            log(s,n);print(n,safe(t[max(0,m.start()-100):m.end()+240]))
elif A.mode == 'resume-check':
    import shutil
    print('free_bytes',shutil.disk_usage(A.root).free)
    errors=[];removed=0
    for p in (A.raw/'ocr').rglob('*.png'):
        if not p.resolve().is_relative_to(A.raw.resolve()):raise RuntimeError('path boundary')
        txt=A.raw/'text'/p.parent.name/(p.stem+'.txt')
        if txt.exists():
            p.unlink();removed+=1
    for p in A.out.iterdir():
        if p.suffix=='.json':
            try:json.loads(contents(p))
            except Exception:errors.append(p.name)
        elif p.suffix=='.csv':
            with p.open(encoding='utf-8-sig',newline='') as f:
                rows=list(csv.reader(f));size=len(rows[0]) if rows else 0
                if not rows or any(len(r)!=size for r in rows):errors.append(p.name)
    for p in (A.raw/'text').rglob('*.txt'):
        if p.stat().st_size==0:errors.append(str(p.relative_to(A.raw)))
    result={'errors':errors,'removed_ocr_images':removed,'free_bytes':shutil.disk_usage(A.root).free}
    (A.out/'resume-check-G.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))
elif A.mode == 'names':
    pattern=A.args[0]
    for s in A.args[1:]:
        hits=[]
        for p in pages(s):
            if re.search(pattern,contents(p),re.I):hits.append(int(re.search(r'\d+',p.stem)[0]))
        print(s,','.join(map(str,hits)))
elif A.mode == 'region':
    states='ANDHRA PRADESH|ARUNACHAL PRADESH|ASSAM|BIHAR|CHHATTISGARH|GOA|GUJARAT|HARYANA|HIMACHAL PRADESH|JAMMU AND KASHMIR|JHARKHAND|KARNATAKA|KERALA|MADHYA PRADESH|MAHARASHTRA|MANIPUR|MEGHALAYA|MIZORAM|NAGALAND|ORISSA|ODISHA|PUNJAB|RAJASTHAN|SIKKIM|TAMIL NADU|TRIPURA|UTTAR PRADESH|UTTARAKHAND|WEST BENGAL'
    for s in A.args:
        state='';hits=[]
        for p in pages(s):
            t=contents(p);n=int(re.search(r'\d+',p.stem)[0])
            headers=list(re.finditer(r'(?m)^\s*('+states+r')\s*$',t))
            segments=[];start=0
            for m in headers:
                segments.append((state,t[start:m.start()]));state=m[1];start=m.end()
            segments.append((state,t[start:]))
            for st,seg in segments:
                if st not in ('GUJARAT','MAHARASHTRA'):continue
                log(s,n)
                if not re.search(r'seal|tablet|inscri|script|graffit',seg,re.I):continue
                names=[c for c,aliases in ALIASES.items() if any(a and re.search(re.escape(a),seg,re.I) for a in aliases)]
                heads=re.findall(r'(?im)\b(?:EXCAVATION[S]?|EXPLORATION[S]?)\s+(?:AT|IN)\s+([^\n.]{3,90})',seg)
                counts=re.findall(r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty[ -]eight)\s+(?:(?:inscribed|Harappan|Indus|terracotta|steatite|clay)\s+)*(?:seals?|sealings?|tablets?|potsherds?)\b',seg,re.I)
                print(s,n,st,','.join(names),'heads=',safe(';'.join(heads)),'counts=',','.join(counts),'scope=',bool(re.search('Harappan|Indus',seg,re.I)))
elif A.mode == 'tailheads':
    for s in A.args:
        print('SOURCE',s)
        for p in pages(s):
            n=int(re.search(r'\d+',p.stem)[0])
            lines=[l.strip() for l in contents(p).splitlines() if l.strip()]
            heads=[l for l in lines[:4]+lines[-3:] if re.fullmatch(r'[A-Za-z :,.‐–\-\d()]+',l) and not re.search(r'seal|script|character|sign|weight|length',l,re.I)]
            print(n,' | '.join(heads))
elif A.mode == 'kanmer-catalogue':
    pairs=[('kanmer-frame-55',1),('kanmer-frame-7',2),('kanmer-frame-7',3),('kanmer-frame-22',4),('kanmer-frame-22',5),('kanmer-frame-22',6)]+[('kanmer-frame-55',n) for n in range(7,11)]
    records=[]
    for s,n in pairs:
        t=re.sub(r'\s+',' ',contents(pagepath(s,n)));log(s,n)
        ms=list(re.finditer(r'\bNos?\.?\s*(\d{2}\s*[-/]\s*\d+|\d{3,})',t))
        for j,m in enumerate(ms):
            b=t[max(0,m.start()-180): ms[j+1].start() if j+1<len(ms) else len(t)]
            after=t[m.end():ms[j+1].start() if j+1<len(ms) else len(t)]
            ctx=re.findall(r'\([^)]*(?:Tr\.|T r\.|Trench)[^)]*\)',b)
            reg=re.sub(r'\s+','',m[1])
            # Only named classification and context fields are emitted.
            near=t[max(0,m.start()-160):m.start()]
            obj='seal' if re.search(r'steatite seal|faience|button seal',near,re.I) else 'pottery'
            mats=re.findall(r'\b(?:steatite|terracotta|clay|shell|faience|Red ware|Red Ware|Red slip ware|Black slipped ware)\b',b,re.I)
            record={'source_id':s,'pdf_page':n,'registration':reg,'contexts':ctx,'class':obj,'materials':list(dict.fromkeys(mats)),'explicit_scope':bool(re.search(r'(?:Indus|Harappan)\s+(?:sign|character|letter|script)|(?:sign|character|letter|script).{0,30}(?:Indus|Harappan)',b,re.I)),'list_reference':bool(re.search('Parpola|Mahadevan|Vats',b,re.I)),'qualification':bool(re.search(r'\b(?:similar|resemble|may|perhaps|possibly|probabl)\w*',b,re.I))}
            records.append(record);print(json.dumps(record,ensure_ascii=False))
    for record in records:record['contexts']=[{'identity_context':x} for x in record['contexts']]
    (A.out/'kanmer-catalogue-fields-G.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
elif A.mode == 'facts':
    s=A.args[0]
    for arg in A.args[1:]:
        n=int(arg);t=re.sub(r'\s+',' ',contents(pagepath(s,n)));log(s,n)
        print(s,n)
        for m in re.finditer(r'\bseal(?:ing)?\b',t,re.I):
            b=t[max(0,m.start()-55):m.end()+250]
            print(json.dumps({'object':m[0],'material':re.findall(r'\b(?:clay|terracotta|steatite|shell|copper|faience)\b',b,re.I),'script_term':bool(re.search(r'\b(?:inscri\w*|script|signs?|characters?|letters?|legends?)\b',b,re.I)),'script_qualified':bool(re.search(r'\b(?:unclear|possibly|maybe|resembl\w*)\b',b,re.I)),'Indus_or_Harappan':bool(re.search(r'\b(?:Indus|Harappan)\b',b,re.I)),'numbers':re.findall(r'\b(?:Trench|Tr\.|Layer|Period|Phase)\s*[A-Z0-9-]+',b,re.I)},ensure_ascii=False))
elif A.mode == 'imprints':
    for s in A.args:
        found=[]
        for pp in pages(s)[:10]:
            t=re.sub(r'\s+',' ',contents(pp));n=int(re.search(r'\d+',pp.stem)[0]);log(s,n,'context')
            for m in re.finditer(r'(?i)(?:published|publication|printed|copyright|©).{0,55}?\b((?:19|20)\d{2})\b',t):found.append((n,m[1]))
        rs=[r for r in REG if r['source_id']==s]
        print(s,'register-years',[r.get('year',r.get('year_or_volume','')) for r in rs],'imprints',found)
elif A.mode == 'extra-scan':
    found=[]
    ids=sorted({p.name for p in (RAW/'run1a/text').iterdir() if p.is_dir() and re.match('iar-|man-environment-|puratattva-',p.name)}|{p.name for p in (A.raw/'text').iterdir() if p.is_dir() and re.match('iar-|man-environment-|puratattva-',p.name)})
    for s in ids:
        for p in pages(s):
            t=contents(p)
            codes=[c for c in A.args if any(re.search(r'\b'+re.escape(a)+r'\b',t,re.I) for a in ALIASES[c])]
            if codes and KEY.search(t):
                n=int(re.search(r'\d+',p.stem)[0]);log(s,n)
                found.append({'source_id':s,'pdf_page':n,'site_codes':';'.join(codes)})
                print(s,n,','.join(codes),flush=True)
    with (A.out/'extra-candidates-G.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['source_id','pdf_page','site_codes']);w.writeheader();w.writerows(found)
