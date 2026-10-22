"""Display omission-page identity labels, quantities and structural cues only."""
import csv
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit import BASE,OUT,ROOT,csvrows,page_index,save
from safe_read import RESTRICTED,EXTRA
idx=page_index();obj=csvrows(BASE/'objects.csv')
out=[]
for a in csvrows(OUT/'omission-assignments.csv'):
    key=(a['source_id'],int(a['pdf_page']));p=idx[key][0]
    s=p.read_text(encoding='utf-8-sig',errors='replace');flat=re.sub(r'\s+',' ',s)
    r=dict(a)
    r['internal_ids']=list(dict.fromkeys(re.findall(r'\b(?:S-\d+|[HM]-\d+|DHR[- ]\d+|NT\d+/T\d+/\d+)\b',s)))
    r['locators']=list(dict.fromkeys(re.findall(r'\b(?:Fig(?:ure)?\.?|Pl(?:ate)?\.?)\s*(?:\d+(?:\.\d+)?|[IVXLCDM]+)\b',flat,re.I)))
    r['object_quantities']=list(dict.fromkeys(re.findall(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+(?:(?:inscribed|Harappan|Indus|steatite|terracotta|square|circular)\s+){0,4}(?:seals?|sealings?|tablets?|potsherds?|sherds?|rods?)\b',flat,re.I)))
    r['object_type_mentions']=list(dict.fromkeys(re.findall(r'\b(?:seals?|sealings?|tablets?|potsherds?|sherds?|rods?)\b',s,re.I)))
    r['explicit_status_word_present']=bool(re.search(r'\b(?:inscribed|inscription|Indus\s+script|Harappan\s+(?:sign|character|letter))',flat,re.I))
    r['headings']=[]
    for l in s.splitlines():
        m=re.search(r'\b(?:EXCAVATIONS?|EXPLORATIONS?)\s+(?:AT|IN)\s+([A-Z][A-Z ,().-]{2,60})',l)
        if m and not RESTRICTED.search(m[1]):r['headings'].append(m[1])
    r['same_source_rows']=[x['row_id'] for x in obj if x['primary_publication']==a['source_id']]
    r['primary_page_rows']=[x['row_id'] for x in obj if x['primary_publication']==a['source_id'] and a['pdf_page'] in re.findall(r'\d+',x['pdf_page'])]
    r['text_has_recoverable_identity_words']=bool(re.search(r'\b(?:excavations?|seals?|sealings?|tablets?|pottery|references|bibliography|contents)\b',s,re.I))
    out.append(r)
    print(json.dumps(r))
save('omission-page-evidence.json',{'pages':out,'scope':'Closed identity vocabulary and page structure only. Source descriptions are not reproduced.'})
