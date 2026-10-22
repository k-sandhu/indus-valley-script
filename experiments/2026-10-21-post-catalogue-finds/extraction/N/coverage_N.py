"""Finish the candidate-page review and retain metadata-only coverage records."""
import collections
import csv
import json
import re
import runpy
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
OUT=M['OUT']; BASE=M['BASE']
read={(r['source_id'],r['pdf_page']) for r in M['rows'](OUT/'pages-read-N.csv')}
groups=collections.defaultdict(set)
for r in M['rows'](BASE/'acquisition/candidate-pages-1a.csv'):
    if r['site_code'] in M['SITES']:
        groups[r['source_id']].add(int(r['pdf_page']))
    elif r['site_code']=='GENERIC' and r['source_id'].startswith('iar-'):
        groups[r['source_id']].add(int(r['pdf_page']))
for r in M['rows'](OUT/'additional-candidates-N.csv'):
    groups[r['source_id']].add(int(r['pdf_page']))
# Mandatory source chapters are covered as complete text blocks.
for sid,a,b in [('rakhigarhi-nath',1,396),('farmana-2006-08',1,854),('farmana-2007-08-report',1,128),('farmana-necropolis',1,1),('rakhigarhi-inventory-held',1,189),('tarkhanewala-2009',1,284),('binjor2017-held',1,9),('puratattva-35-held',64,79),('puratattva-36-held',26,53),('puratattva-36',59,63),('puratattva-36',181,191)]:
    groups[sid].update(range(a,b+1))
results=[]; alerts=[]
for sid,ns in sorted(groups.items()):
    for n in sorted(ns):
        f=M['path_for'](sid)/f'p{n:04}.txt'
        if not f.exists():
            results.append(dict(source_id=sid,pdf_page=n,review='missing text'));continue
        t=f.read_text(encoding='utf-8')
        result='no exact object or script keyword'
        if re.search(r'\bseals?\b|\binscri\w*|\bgraffiti?\b|\bscript\b|\blegends?\b',t,re.I):result='identity and context keyword review'
        results.append(dict(source_id=sid,pdf_page=n,review=result))
        if (sid,str(n)) not in read and re.search(r'\binscribed\b|\bIndus\s+(?:sign|character|letter|script)|\bHarappan\s+(?:sign|character|letter|script)',t,re.I):
            alerts.append(dict(source_id=sid,pdf_page=n,identifiers=re.findall(r'\b(?:Reg\.?\s*(?:No\.?)?\s*|RGR[- ])\d+',t),references=re.findall(r'\b(?:Fig(?:ure)?\.?|Pl(?:ate)?\.?|PI\.)\s*[IVXLC\d]+(?:\.\d+)?',t)))
    M['log'](sid,ns,'context')
M['savecsv'](OUT/'coverage-N.csv',['source_id','pdf_page','review'],results)
(OUT/'coverage-alerts-N.json').write_text(json.dumps(alerts,indent=2),encoding='utf-8')
print(json.dumps(alerts))
