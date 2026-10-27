import requests,pathlib,fitz,json,hashlib,datetime
root=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-phase-pass2')
u='https://www.cambridge.org/core/services/aop-cambridge-core/content/view/D702BB5DE8A77C1D8EE58DF4D8B1E8DA/S0033822200036894a.pdf/tata-institute-radiocarbon-date-list-i.pdf'
r=requests.get(u,timeout=90);p=root/'tata1963.pdf';p.write_bytes(r.content)
m={'id':'tata1963','title':'Tata Institute Radiocarbon Date List I','authors':'S. Kusumgar, D. Lal and R. P. Sarna','year':1963,'url':u,'final_url':r.url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest(),'physical_path':str(p),'logical_path':'data/raw/2026-10-24-town-phase-pass2/'+p.name,'rights':'Copyright The American Journal of Science; rights-unverified; local-only','status':r.status_code}
(root/'lab-acquisition.json').write_text(json.dumps(m,indent=2))
d=fitz.open(p);print('pages',len(d));ids=[0,3,4];out='\n'.join('INDEX '+str(i)+'\n'+d[i].get_text() for i in ids);(root/'selected-lab.txt').write_text(out,encoding='utf8'); print(out.encode('ascii','replace').decode())
for i in [4]:d[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(root/f'lab-{i}.png'))
for i in [21]:
 e=fitz.open(root/'dholavira-management.pdf');e[i].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(str(root/f'management-{i}.png'))
