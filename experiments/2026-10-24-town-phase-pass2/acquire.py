import requests, pathlib, hashlib, datetime,json,fitz
root=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-phase-pass2')
u='https://whc.unesco.org/document/184543'
r=requests.get(u,timeout=180); p=root/'dholavira-management.pdf';p.write_bytes(r.content)
m={'id':'unesco-management','title':'Dholavira: a Harappan City, Site Management Plan, Volume II','url':u,'final_url':r.url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest(),'physical_path':str(p),'logical_path':'data/raw/2026-10-24-town-phase-pass2/'+p.name,'rights':'rights-unverified; local-only','status':r.status_code}
(root/'acquisition.json').write_text(json.dumps(m,indent=2))
d=fitz.open(p); print('pages',len(d))
hits=[]
for i,page in enumerate(d):
 t=page.get_text()
 if any(k in t.lower() for k in ['conservation works undertaken','castle','restor','total station']):
  hits.append({'index':i,'terms':[k for k in ['conservation works undertaken','castle','restor','total station'] if k in t.lower()]})
(root/'management-hits.json').write_text(json.dumps(hits,indent=2)); print(hits[:40])
