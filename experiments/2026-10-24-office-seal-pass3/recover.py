import pathlib,fitz,json,hashlib,datetime,requests
r=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-pass3')
p=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf')
d=fitz.open(p)
for n in range(68,77):
 t=d[n-1].get_text(); (r/f'rao-pdf{n}.txt').write_text(t,encoding='utf8'); print(n,t[:120] if n<72 else t[:700])
for n in [72,73,74,75,76]: d[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(r/f'rao-pdf{n}.png')
urls={'harappa':'https://www.harappa.com/content/were-cretulae-clay-sealings-indus-port-town-lothal-part-administrative-archive-contextual','posters':'https://unibo.academia.edu/DennysFrenez/Posters'}
log=[]
for name,url in urls.items():
 try:
  x=requests.get(url,timeout=30); (r/f'{name}.html').write_bytes(x.content); log.append(dict(id=name,url=url,status=x.status_code,bytes=len(x.content),sha256=hashlib.sha256(x.content).hexdigest(),time=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 except Exception as e: log.append(dict(id=name,url=url,error=str(e)))
(r/'routes.json').write_text(json.dumps(log,indent=2),encoding='utf8')
