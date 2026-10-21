"""Acquire a bounded set of primary author texts; keep every witness local."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request
import fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT/'data/raw/2026-10-20-h912-tablet-series/sources-v1'
SOURCES = [
 ('parpola2012','Asko Parpola','Indus Civilization (1750 BCE)',2012,
  'https://tuhat.helsinki.fi/ws/portalfiles/portal/127256327/Parpola_A_2012._Indus_Civilization_1750_BCE_._Proofs_of_pp._3_18_in_Brill_s_Encyclopedia_of_Hinduism_vol._4.pdf'),
 ('parpola-fish-chapter','Asko Parpola','The ‘fish’ signs of the Indus script',1994,
  'https://sindhilanguagelibrary.com/assets/documents/pdf/647f088f1fff3.pdf'),
 ('belcher2018','William R. Belcher','Fish Symbolism and Fishing in Ancient South Asia',2018,
  'https://www.harappa.com/sites/default/files/pdf/Belcher%202018%20Fish%20Symbolism%20and%20Fish%20Remains%20in%20Ancient%20South%20Asia.pdf')
]


def main():
 RAW.mkdir(parents=True,exist_ok=False)
 records=[]
 for ident,author,title,year,url in SOURCES:
  r={'id':ident,'author':author,'title':title,'year':year,'url':url,
     'retrieved_utc':datetime.now(timezone.utc).isoformat(),'rights_status':'rights-unverified'}
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'IndusResearchSourceAudit/1.0 (public scholarly source retrieval)'})
   with urllib.request.urlopen(req,timeout=45) as response:
    data=response.read();r.update(http_status=response.status,final_url=response.url,content_type=response.headers.get('Content-Type'))
   pdf=data.startswith(b'%PDF-');path=RAW/(ident+('.pdf' if pdf else '.response'))
   with path.open('xb') as f:f.write(data)
   r.update(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),pdf=pdf)
   if pdf:
    doc=fitz.open(path);r['pages']=len(doc);r['metadata']=doc.metadata
    text='\n'.join(p.get_text() for p in doc)
    with path.with_suffix('.txt').open('x',encoding='utf8') as f:f.write(text)
    r['observed_notices']=[line.strip() for line in text.splitlines() if 'copyright' in line.lower() or '©' in line][:6]
  except Exception as exc:r['error']=str(exc)
  records.append(r)
 # Reuse the previously held Rao chapter instead of downloading it again.
 q=ROOT/'research/literature/sources/rao_2018_economics.pdf'
 if q.exists():
  doc=fitz.open(q)
  text='\n'.join(p.get_text() for p in doc)
  (RAW/'rao2018-reused.txt').write_text(text,encoding='utf8')
  records.append({'id':'rao2018-existing','author':'Rajesh P. N. Rao','title':'The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor','year':2018,'new_acquisition':False,'path':q.relative_to(ROOT).as_posix(),'bytes':q.stat().st_size,'pages':len(doc),'sha256':hashlib.sha256(q.read_bytes()).hexdigest(),'url':'https://arxiv.org/abs/1812.00049','rights_status':'rights-unverified'})
 with (HERE/'sources-v1.json').open('x',encoding='utf8') as f:json.dump({'sources':records,'handling':'PDFs, full extracted text and any renders remain local; source notes and hashes are tracked.'},f,indent=2,ensure_ascii=False);f.write('\n')
 print(json.dumps([{'id':r['id'],'pages':r.get('pages'),'error':r.get('error')} for r in records]))


if __name__=='__main__':main()
