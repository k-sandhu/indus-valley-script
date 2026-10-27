import requests,pathlib,json,datetime,hashlib,fitz
r=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-pass3'); log=json.loads((r/'routes.json').read_text())
urls={'iitgn':'https://repository.iitgn.ac.in/entities/publication/8b5a98f0-16f1-4a53-b2f9-dd19c8bb4986','article-download':'https://www.academia.edu/attachments/121285940/download_file?s=profile'}
for name,url in urls.items():
 try:
  x=requests.get(url,timeout=30); (r/f'{name}.response').write_bytes(x.content); log.append(dict(id=name,url=url,final_url=x.url,status=x.status_code,bytes=len(x.content),sha256=hashlib.sha256(x.content).hexdigest(),time=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 except Exception as e: log.append(dict(id=name,url=url,error=str(e)))
(r/'routes.json').write_text(json.dumps(log,indent=2),encoding='utf8')
d=fitz.open('D:/projects/indus_valley_script/research/literature/sources/joshi_parpola_1987_cisi1.pdf')
for n in [408,409,410]:
 (r/f'cisi-pdf{n}.txt').write_text(d[n-1].get_text(),encoding='utf8');d[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(r/f'cisi-pdf{n}.png')
