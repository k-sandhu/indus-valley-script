"""Locate additional northern site aliases without emitting page payloads."""
import csv
import json
import re
import runpy
from pathlib import Path
M=runpy.run_path(str(Path(__file__).with_name('extract_N.py')))
ALIASES={'MSD':r'Masudpur','MTL':r'Mitathal','HUL':r'\bHulas\b','DHL':r'Dhalewan','ALG':r'Alamgirpur','CHG':r'Chandigarh','LHR':r'Lohari\s+Ragho','BAL':r'\bBalu\b','GRW':r'Girawad','MDI':r'\bManda\b','BRs':r'\bBrass\b','DNK':r'Donder\s+Khera'}
data=[]; accesses=[]
for directory in sorted((M['RAW']/'run1a/text').iterdir()):
    if not directory.is_dir():continue
    files=sorted(directory.glob('p*.txt'))
    accesses.append(dict(source_id=directory.name,agent=M['AGENT'],access='automated alias and keyword scan',pages=f'1-{len(files)}',purpose='locate northern entries'))
    for f in files:
        t=f.read_text(encoding='utf-8')
        if not M['KEY'].search(t):continue
        for code,pat in ALIASES.items():
            if re.search(pat,t,re.I):data.append(dict(source_id=directory.name,pdf_page=int(f.stem[1:]),site_code=code))
M['savecsv'](M['OUT']/'additional-candidates-N.csv',['source_id','pdf_page','site_code'],data)
M['savecsv'](M['OUT']/'scan-access-N.csv',['source_id','agent','access','pages','purpose'],accesses)
groups={}
for r in data:
    if r['site_code']=='CHG':continue
    groups.setdefault(r['site_code'],{}).setdefault(r['source_id'],[]).append(r['pdf_page'])
print(json.dumps(groups))
