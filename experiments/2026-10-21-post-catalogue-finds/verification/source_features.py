"""Display only closed identity fields for the seeded assignments."""
import csv
import json
import random
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from safe_read import BASE, OUT, ROOT, page_path, exposure
sys.stdout.reconfigure(encoding='utf-8')

def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def features():
    for r in readcsv(OUT/'blind-assignments.csv'):
        print(r['row_id'], r['site'], r['primary_publication'],r['pdf_page'],r['registration_or_position'])
        for num in re.findall(r'\d+',r['pdf_page']):
            p=page_path(r['primary_publication'],num)
            if not p: print('MISSING');continue
            s=p.read_text(encoding='utf-8-sig',errors='replace')
            lines=s.splitlines()
            foot=[l.strip() for l in lines[-12:] if re.fullmatch(r'\s*\d{1,4}\s*',l)]
            print('footer',foot)
            reg=r['registration_or_position']
            if not reg.startswith('position:'):
                pattern=r'(?<!\d)'+r'[\s-]*'.join(map(re.escape,re.findall(r'[A-Za-z]+|\d+',reg)))+r'(?!\d)'
                hits=[i for i,l in enumerate(lines) if re.search(pattern,l,re.I)]
                print('registration lines',[i+1 for i in hits])
                for i in hits:
                    line=lines[i]
                    if r['primary_publication']=='bisht-2015-held' and 264<=int(num)<=275:
                        tokens=line.split()
                        # Table's registration and grid field precede other columns.
                        j=next((j for j,t in enumerate(tokens) if re.fullmatch(pattern,t,re.I)),None)
                        if j is not None and j+1<len(tokens):
                            grid=tokens[j+1]
                            if re.fullmatch(r'\d{1,2}(?:[xX×+]\d{1,3})+',grid):print('grid',grid)
                    for l in lines[max(0,i-1):i+4]:
                        for m in re.finditer(r'\b(?:Middle Town|Midle Town|Lower Town|Castle|Citadel)\b',l,re.I):print('area',m.group())
                        for m in re.finditer(r'\b(?:inscribed|uninscribed|possibly|uncertain|photograph|drawing|sealing|seal|tablet|potsherd|rod)\b',l,re.I):print('cue',m.group())
                    for m in re.finditer(r'\b(?:[IV]+)\b',line):print('period',m.group())
            else:
                ids=list(dict.fromkeys(re.findall(r'\b(?:H|M|Dlv|Rgr|C|K)-\d+[A-Za-z]?\b',s)))
                if ids:print('distinct catalogue ids in source order',ids)
            locs=list(dict.fromkeys(m.group() for m in re.finditer(r'\b(?:Fig(?:ure)?\.?|Pl(?:ate)?\.?)\s*[IVXLCDM\d]+(?:[.:-]\d+)?',s,re.I)))
            print('locators',locs)

def scope():
    targets=readcsv(OUT/('blind-assignments.csv' if sys.argv[2]=='blind' else 'omission-assignments.csv'))
    for r in targets:
        source=r.get('primary_publication',r.get('source_id'))
        for n in re.findall(r'\d+',r['pdf_page']):
            p=page_path(source,n)
            if not p:continue
            s=p.read_text(encoding='utf-8-sig',errors='replace')
            print('PAGE',r.get('row_id',''),source,n)
            sites=[]
            seed=readcsv(BASE/'selection/sites-seed.csv')
            for x in seed:
                for v in [x.get('site',''),*re.split('[;|]',x.get('aliases',''))]:
                    if len(v)>3 and re.search(r'\b'+re.escape(v)+r'\b',s,re.I):sites.append(v)
            print('site mentions',list(dict.fromkeys(sites)))
            for m in re.finditer(r'\b(?:stone|slab|board|pottery|sealings?|seals?|tablets?|rods?|potsherds?|sherds?|tag|tool|ivory|bone)\b',s,re.I):
                a=s.rfind('\n\n',0,m.start())+2
                b=s.find('\n\n',m.end())
                snippet=s[a:b if b>=0 else len(s)]
                status=bool(re.search(r'\b(?:inscribed|inscription|Indus\s+script|Harappan\s+(?:sign|character|letter))',snippet,re.I))
                loc=[z.group().replace('\n',' ') for z in re.finditer(r'\b(?:fig(?:ure)?\.?|pl(?:ate)?\.?)\s*(?:\d+(?:\.\d+)?|[IVXLCDM]+)\b',snippet,re.I)]
                print('line',s[:m.start()].count('\n')+1,'object/material',m.group(),'scope wording',status,'locators',loc)


def omission():
    pop={}
    for p in sorted((BASE/'extraction').glob('*/pages-read-*.csv')):
        for r in readcsv(p):
            if r['purpose'].strip()=='candidate':
                key=(r['source_id'],r['pdf_page'])
                pop.setdefault(key,set()).add(p.parent.name)
    rng=random.Random(20261022)
    sample=rng.sample(sorted(pop),min(40,len(pop)))
    candidates={}
    for p in [BASE/'acquisition/candidate-pages-1a.csv',*sorted((BASE/'extraction').glob('*/candidate-pages-*.csv'))]:
        for r in readcsv(p):
            candidates.setdefault((r['source_id'],r['pdf_page']),set()).update(filter(None,re.split(r'[;|]',r.get('site_code','') or r.get('sites',''))))
    out=[]
    for source,page in sample:
        out.append(dict(source_id=source,pdf_page=page,parts=';'.join(sorted(pop[source,page])),candidate_sites=';'.join(sorted(candidates.get((source,page),set())))))
    with (OUT/'omission-assignments.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    (OUT/'omission-sampling.json').write_text(json.dumps({'seed':20261022,'population_unique_pages':len(pop),'sample':len(sample),'population_rule':'Unique source and PDF-page pairs with exact purpose candidate; sorted before sampling.','part_memberships':{p:sum(p in v for v in pop.values()) for p in 'NGDPEF'}},indent=2)+'\n',encoding='utf-8')
    for r in out:print(json.dumps(r))

if sys.argv[1]=='features':features()
elif sys.argv[1]=='scope':scope()
else:omission()
