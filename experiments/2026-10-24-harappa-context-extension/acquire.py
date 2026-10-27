import urllib.request,pathlib,hashlib,json,datetime,fitz
raw=pathlib.Path(r'D:/projects/indus_valley_script/data/raw/2026-10-24-harappa-context-extension')
u='https://www.harappa.com/sites/default/files/pdf/Kenoyer2009%20Indus%20Seals_0.pdf'
p=raw/'kenoyer2009-indus-seals.pdf'
r=urllib.request.urlopen(u); b=r.read(); p.write_bytes(b)
m={'url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'physical_path':str(p),'logical_path':'data/raw/2026-10-24-harappa-context-extension/'+p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'rights':'unverified; local only','http_status':r.status}
(raw/'acquisition.json').write_text(json.dumps(m,indent=2))
d=fitz.open(p)
for i,pg in enumerate(d):
 t=pg.get_text()
 if '4064' in t:
  (raw/f'kenoyer2009-p{i+1}.txt').write_text(t,encoding='utf8')
  print('PDF PAGE',i+1,t)
