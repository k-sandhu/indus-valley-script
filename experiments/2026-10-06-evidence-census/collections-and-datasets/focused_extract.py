"""Extract portal record fields into local-only rows for inspection."""
import json, re
from bs4 import BeautifulSoup
from focused_fetch import RAW

rows=[]
for file in sorted(RAW.glob('object-*.body')):
    soup=BeautifulSoup(file.read_bytes(),'html.parser')
    fields={tr.find('th').get_text(' ',strip=True):tr.find('td').get_text(' ',strip=True) for tr in soup.select('tr') if tr.find('th') and tr.find('td')}
    identifier=file.stem.removeprefix('object-')
    log=json.loads((RAW/(file.stem+'.request.json')).read_text(encoding='utf8'))
    if log.get('http_status')!=200 or not fields:
        rows.append(dict(record_identifier=identifier,fields=fields,status='unavailable')); continue
    text=' '.join(fields.values())
    relevant=bool(re.search(r'harapp|mohenjo|chanhu|lothal|indus',text,re.I))
    inscribed=bool(re.search(r'inscri|pictogra|script|character|letter',fields.get('Brief Description',''),re.I))
    copy=bool(re.search(r'plaster|replica|reproduc|cast',fields.get('Main Material','')+' '+fields.get('Brief Description',''),re.I))
    status='confirmed_description' if relevant and inscribed and not copy else 'modern_copy' if relevant and copy else 'unconfirmed_inscription' if relevant else 'other_period_or_place'
    slots=sorted(set(re.findall(re.escape(identifier)+r'_(\d{2})',str(soup))))
    rows.append(dict(record_identifier=identifier,url=log['url'],body=log['body'],fields=fields,status=status,image_slots=slots,identifier_candidates=re.findall(r'\b(?:DK|HR|VS|SD|HP|C)[ .-]*\d+[A-Za-z]?\b',fields.get('Accession Number',''),re.I)))
(RAW/'portal-record-review.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Reviewed',len(rows))
for r in rows:
    if r['status'] in {'confirmed_description','modern_copy','unconfirmed_inscription'}:
        f=r['fields']; print(r['status'],r['record_identifier'],f.get('Accession Number'),f.get('Origin Place'),f.get('Period / Year of Work'),f.get('Brief Description','')[:160])
