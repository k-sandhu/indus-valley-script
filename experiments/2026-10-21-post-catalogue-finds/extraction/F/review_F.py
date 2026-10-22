"""Sweep recovered text and display a restricted metadata review."""
import argparse
import csv
import json
from pathlib import Path
import re
import unicodedata


SID = 'iar-2003-04-asi'
KEYS = ['seal','sealing','tablet','inscri','script','sign','character','letter','legend','graffit','tag','impression']


def norm(s):
    return re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKD',s).lower())


def write(path, rows, fields):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)


def safe(s):
    # Preserve object identities while suppressing descriptive clauses.
    stop = r'\b(?:depict\w*|represent\w*|bearing|bears?|carr(?:y|ies|ying)|portray\w*|showing|showed|engraved|incised|incision|inscrib\w*|with\s+(?:a|an|the|[a-z]+)\s+(?:design|figure)|legend|measur\w*|weigh\w*|length|breadth|width|height|diameter)\b'
    s=re.sub(stop+r'[^.;\n]*','[description omitted]',s,flags=re.I)
    names = ['756e69636f726e','62756c6c','7268696e6f6365726f73','656c657068616e74','7469676572','62756666616c6f','7a656275','676f6174','616e74656c6f7065','6d6f746966','616e696d616c']
    bad = '|'.join(bytes.fromhex(x).decode() for x in names)
    s=re.sub(r'[^.;\n]*\b(?:'+bad+r'|pictograph\w*|pictorial|horn\w*|figure\s+of|fish|deer|human|standing|seated|facing|geometric|swastika|trident|arrow|ladder|star|cross|conch|leaf|pip[a,p]l|tree|circle|dotted|pentagon|hexagon|triangle|rectangle)\b[^.;\n]*','[description omitted]',s,flags=re.I)
    s=re.sub(r'[^.;\n]*\b(?:\w+[ -]+){0,2}(?:signs?|characters?|letters?|lines?)\b[^.;\n]*','[script detail omitted]',s,flags=re.I)
    s=re.sub(r'\b\d+(?:\.\d+)?\s*(?:mm|cm|kg|gm|grams?|g)\b','[measurement omitted]',s,flags=re.I)
    s=re.sub(r'\b(?:left|right|upward|downward|vertical|horizontal)\w*[^.;\n]*','[description omitted]',s,flags=re.I)
    return s


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode', choices=['sweep','read','front','index','facts'])
    p.add_argument('--text',required=True,type=Path)
    p.add_argument('--records',required=True,type=Path)
    p.add_argument('--seed',required=True,type=Path)
    p.add_argument('--pages',default='')
    a=p.parse_args()
    pages={int(x.stem[1:]):x.read_text(encoding='utf-8') for x in a.text.glob('p[0-9][0-9][0-9][0-9].txt')}
    if a.mode=='front':
        for n in range(1,min(18,len(pages))+1):
            t=pages[n]
            # Bibliographic tokens only.
            print(json.dumps(dict(pdf_page=n,years=re.findall(r'\b(?:19|20)\d{2}(?:\s*[-–]\s*\d{2,4})?',t),title=bool(re.search('INDIAN.*ARCHAEOLOGY',t,re.I|re.S)),review=bool(re.search('REVIEW',t,re.I)),publication_years=re.findall(r'(?:Copyright|copyright|Published|published|©)[^\n]{0,50}',t))))
        return
    sites={r['site_code']:[r['site']]+r['aliases'].split('|') for r in csv.DictReader(a.seed.open(encoding='utf-8'))}
    added={'MSD':'Masudpur','MTL':'Mitathal','HUL':'Hulas','DHL':'Dhalewan','ALG':'Alamgirpur','CHG':'Chandigarh','LHR':'Lohari Ragho','BLT':'Balathal','JNK':'Juna Khatiya','PBM':'Pabumath','PTH':'Pithad','NGS':'Nageshwar','KNW':'Kanewal','RNG':'Rangpur','PRB':'Prabhas Patan'}
    sites.update({k:[v] for k,v in added.items()})
    pats={k:re.compile(r'(?<![a-z])'+r'[\s\-\u00ad]*'.join(k)+r'[a-z]*',re.I) for k in KEYS}
    def hits(t):
        hs={}
        for c,terms in sites.items():
            num=0
            for term in terms:
                if not term: continue
                q=r'(?<![a-z0-9])'+r'[\s\-\u00ad\u2010-\u2014]*'.join(re.escape(x) for x in norm(term))+r'(?![a-z0-9])'
                num+=len(re.findall(q,t,re.I))
            if num: hs[c]=num
        kws={k:len(q.findall(t)) for k,q in pats.items() if q.search(t)}
        return hs,kws,'harappan' in norm(t) and bool(kws)
    pmap={}
    for n,t in pages.items():
        lines=[x.strip() for x in t.splitlines() if x.strip()]
        candidates=[x for x in lines[-3:]+lines[:3] if re.fullmatch(r'\d{1,3}|[ivxlcdm]{1,8}',x,re.I)]
        value=next((x for x in candidates if x.isdigit() and int(x)<650),'')
        if not value and candidates: value=candidates[0]
        pmap[n]=value
    authoritative=a.text/'printed_page_map.json'
    if authoritative.exists():
        pmap={int(k):v for k,v in json.loads(authoritative.read_text(encoding='utf-8')).items()}
    if a.mode=='sweep':
        rows=[]; direct={}; leads=[]; heading=''
        for n,t in sorted(pages.items()):
            hs,kws,generic=hits(t)
            lines=t.splitlines()
            for i,line in enumerate(lines):
                if re.search(r'\b(?:EXCAVATION|EXPLORATION)\s+(?:AT|IN)\b',line,re.I):
                    span=' '.join(lines[i:i+3])
                    m=re.search(r'\b(?:EXCAVATION|EXPLORATION)\s+(?:AT|IN)\s+(.+?DISTRICT\s+[^.;:—–]+)',span,re.I)
                    if m: heading=m[1][:150]
            if generic and any(k in kws for k in ('seal','inscri','script')):
                section=next((code for lo,hi,code in [(29,37,'JKR'),(38,44,'GDH'),(48,62,'BHR'),(211,218,'TKD'),(231,249,'BRR')] if lo<=n<=hi),'front-matter' if n<5 else 'unassigned')
                leads.append(dict(pdf_page=n,section_code=section))
            if kws and (hs or generic):
                direct[n]=list(hs) or ['GENERIC']
                for c in direct[n]:
                    rows.append(dict(source_id=SID,pdf_page=n,printed_page=pmap[n],site_code=c,generic_harappan_hit=int(generic),n_site_terms=hs.get(c,0),n_keywords=sum(kws.values()),keyword_classes='|'.join(kws),context_only=0))
        context=set()
        for n,codes in direct.items():
            for m in (n-1,n+1):
                if m not in pages: continue
                for c in codes:
                    if c not in direct.get(m,[]) and (m,c) not in context:
                        context.add((m,c)); rows.append(dict(source_id=SID,pdf_page=m,printed_page=pmap[m],site_code=c,generic_harappan_hit=0,n_site_terms=0,n_keywords=0,keyword_classes='',context_only=1))
        fields='source_id,pdf_page,printed_page,site_code,generic_harappan_hit,n_site_terms,n_keywords,keyword_classes,context_only'.split(',')
        write(a.records/'candidate-pages-F.csv',sorted(rows,key=lambda r:(r['pdf_page'],r['site_code'])),fields)
        if not authoritative.exists():
            write(a.records/'printed-pages-F.csv',[dict(source_id=SID,pdf_page=n,printed_page=pmap[n],basis='footer-or-header-text' if pmap[n] else 'not-detected') for n in sorted(pages)],['source_id','pdf_page','printed_page','basis'])
        (a.records/'sweep-summary-F.json').write_text(json.dumps(dict(pages=len(pages),direct_pages=len(direct),review_pages=len({r['pdf_page'] for r in rows}),new_heading_leads=leads),indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(pages=len(pages),direct_pages=len(direct),review_pages=len({r['pdf_page'] for r in rows}))))
    elif a.mode=='index':
        for n,t in sorted(pages.items()):
            hs,kws,generic=hits(t)
            if hs or generic:
                print(json.dumps(dict(pdf_page=n,printed_page=pmap[n],sites=list(hs),keywords=list(kws),generic=generic)))
    elif a.mode in ('read','facts'):
        ns=set()
        for term in a.pages.split(','):
            if '-' in term:
                lo,hi=map(int,term.split('-')); ns.update(range(lo,hi+1))
            elif term: ns.add(int(term))
        log=a.records/'pages-read-F.csv'
        existing=list(csv.DictReader(log.open(encoding='utf-8'))) if log.exists() else []
        done={int(r['pdf_page']) for r in existing}
        for n in sorted(ns):
            if n not in pages: continue
            if n not in done: existing.append(dict(source_id=SID,pdf_page=n,purpose='candidate',image_viewed='no'))
            t=pages[n]
            print(f'PDF {n}; printed {pmap[n]}')
            # Metadata slots prevent graphic clauses reaching the preview.
            flat=re.sub(r'\s+',' ',t)
            for para in re.split(r'\n\s*\n',t):
                if not re.search(r'\b(?:seals?|sealings?|tablets?|inscri\w*|graffit\w*|celts?|tags?|legend\w*)\b',para,re.I): continue
                q=re.sub(r'\s+',' ',para)
                objects=re.findall(r'\b(?:seals?|sealings?|tablets?|celts?|sherds?|potsherds?|vessels?|tags?|pottery|knives|knife|bangles?)\b',q,re.I)
                counts=re.findall(r'\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|several|few|many|solitary|single)\s+(?:(?:Harappan|terracotta|steatite|copper|inscribed|square|broken|clay|large|small)\s+){0,4}(?:seals?|sealings?|tablets?|celts?|potsherds?|sherds?|tags?)\b',q,re.I)
                locs=re.findall(r'\b(?:Trench(?:es)?\s+[A-Z][A-Za-z0-9 ,&-]{0,45}|[Pp]hase\s*[-–]?[IVX0-9Il]+|[Pp]eriod\s*[-–]?[IVX0-9Il]+|[Pp]l(?:ate)?\s*\.?\s*[0-9]+[a-z]?(?:\s*[-–]\s*[0-9]+[a-z]?)?|[Ff]ig(?:s|ure)?\.?\s*\d+(?:\s*[-–]\s*\d+)?)',q)
                # Return only closed-vocabulary features and short locators.
                print(json.dumps(dict(object_terms=objects,object_counts=counts,locators=locs,materials=sorted(set(re.findall(r'\b(?:steatite|terracotta|copper|clay|faience|ivory|bone|shell|stone)\b',q,re.I))),script_attribution=bool(re.search(r'Harappan|Indus',q,re.I)),inscription_reference=bool(re.search(r'inscri|script|sign|character|letter|legend',q,re.I)),qualified_status=bool(re.search(r'possibl|resembl|probably',q,re.I))),ensure_ascii=True))
            for line in t.splitlines():
                if re.search(r'\b(?:EXCAVATION|EXPLORATION)\s+(?:AT|IN)\b',line,re.I):
                    print('heading: '+safe(line.strip()))
        write(log,sorted(existing,key=lambda r:int(r['pdf_page'])),['source_id','pdf_page','purpose','image_viewed'])


if __name__=='__main__': main()
