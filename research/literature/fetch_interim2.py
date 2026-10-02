from pathlib import Path
import json,requests,fitz,hashlib,datetime
B=Path(__file__).parent;u='https://ignca.gov.in/Asi_data/77275.pdf'
r=requests.get(u,timeout=45);print(r.status_code,len(r.content),r.headers.get('Content-Type'))
r.raise_for_status();p=B/'sources/jansen_urban1987_interim2_govscan_77275.pdf';p.write_bytes(r.content)
d=fitz.open(p)
(B/'sources/jansen_urban1987_interim2_govscan_77275.txt').write_text('\n'.join(f'[PDFPAGE{i+1}]\n'+x.get_text() for i,x in enumerate(d)),encoding='utf-8')
o=B/'metrology/primary_numeric/interim2';o.mkdir(exist_ok=True)
for n in [1,5,6,7,8,9,10,108,110,112,114,116,118,120]:
 if n<=len(d):d[n-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(o/f'pdf{n:03}.png')
q=B/'source_retrieval_log.json';a=json.loads(q.read_text(encoding='utf-8'))
a.append({'id':'jansen_urban1987_interim2','url':u,'source_type':'Official government-hosted primary volume scan','requested_identity':'InterimReportsVol2, includes Vidale1987pp105–111','retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_status':r.status_code,'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest(),'pages':len(d),'local_file':str(p),'identity_verified':'Pending original title inspection; metadata alone not sufficient.'})
q.write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
print(len(d),hashlib.sha256(r.content).hexdigest())
