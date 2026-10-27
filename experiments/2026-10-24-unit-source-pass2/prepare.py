from pathlib import Path
import fitz,json,csv,hashlib,datetime,urllib.request,urllib.error
P=Path('experiments/2026-10-24-unit-source-pass2'); R=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-pass2')
def dump(p,x): p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
routes=json.load(open('data/raw/2026-10-24-unit-source-extension/run-v2/missing-face-routes.json'))
targets=[x for x in routes if x['route'] in ['HARP-object-and-figure','Dholavira-excavation-number']]
dump(R/'frozen-targets-v1.json',targets)
rows=list(csv.DictReader(open('data/lipi/src/assets/data/inscriptions.csv',encoding='utf-8-sig')))
dump(R/'target-export-metadata-v1.json',[x for x in rows if 'LIPI:'+x['id'] in {t['face_id'] for t in targets}])
source=Path('data/raw/2026-10-11-societal-persistence/evidence/acquisition-v5/bisht2015-preliminary-original.pdf');d=fitz.open(source)
for n in [266,297]:
 p=d[n-1];(R/f'bisht-pdf{n}.txt').write_text(p.get_text(),encoding='utf-8');p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(R/f'bisht-pdf{n}.png')
urls=[('publisher','https://acadsci.fi/en/publications/the-corpus-of-indus-seals-and-inscriptions-3-2-humaniora-383-has-been-published/'),('cisi31-institution','https://researchportal.helsinki.fi/en/publications/corpus-of-indus-seals-and-inscriptions-volume-3-new-material-untr/'),('cisi32-store','https://www.tiedekirja.fi/english/corpus-of-indus-seals-and-inscriptions-3-2.html?___from_store=default'),('harappa-bat','https://www.harappa.com/slide/pottery-bat-inscriptions'),('harappa-potters','https://www.harappa.com/slide/pottery-sherds-potters-marks'),('harappa-2000-index','https://www.harappa.com/slideshows/harappa-2000-2001'),('harappa-1995-index','https://www.harappa.com/slideshows/harappa-excavations1995-2000')]
log=[]
for label,u in urls:
 rec={'label':label,'url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rights':'rights-unverified; local-only'}
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25) as f:
   b=f.read();out=R/(label+'.html');out.write_bytes(b);rec.update(status=f.status,resolved_url=f.url,physical_path=str(out),logical_path='data/raw/2026-10-24-unit-source-pass2/'+out.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e: rec.update(error_type=type(e).__name__,error=str(e))
 log.append(rec)
dump(R/'access-log-v1.json',log)
print([(x['label'],x.get('status',x.get('error'))) for x in log])
