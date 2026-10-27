import urllib.request, json, hashlib, datetime, pathlib, fitz, re
p=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-pass3')
urls=[('harappa-page','https://www.harappa.com/content/inscribed-objects-harappa-excavations-1987-2007'),('harp-old','https://old.harappa.com/indus/Kenoyer-Meadow-2010-HARP.pdf'),('helka31','https://www.finna.fi/Record/oy.9910978483906252'),('helka32','https://kansalliskirjasto.finna.fi/kansalliskirjastofikka/Record/helka.9934146360306253')]
rows=[]
for label,url in urls:
 r={'label':label,'url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rights':'unresolved; local-only'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as h:
   b=h.read(30000001); r.update(status=h.status,resolved_url=h.url)
  f=p/(label+('.pdf' if b.startswith(b'%PDF') else '.html')); f.write_bytes(b);r.update(physical_path=str(f),logical_path='data/raw/2026-10-24-unit-source-pass3/'+f.name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  if b.startswith(b'%PDF'):
   d=fitz.open(f); texts=[x.get_text() for x in d];(p/(label+'-text.json')).write_text(json.dumps(texts),encoding='utf8');r['pages']=len(d)
 except Exception as e:r['error']=str(e)
 rows.append(r)
(p/'acquisition-v1.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps(rows,indent=2))
