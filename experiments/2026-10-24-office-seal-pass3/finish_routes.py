import pathlib,requests,json,hashlib,datetime,fitz
r=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-office-seal-pass3');log=json.loads((r/'routes.json').read_text())
u='https://www.academia.edu/attachments/54250579/download_file?s=profile'; x=requests.get(u,timeout=30);(r/'poster-download.response').write_bytes(x.content);log.append(dict(id='poster-download',url=u,final_url=x.url,status=x.status_code,bytes=len(x.content),sha256=hashlib.sha256(x.content).hexdigest(),time=datetime.datetime.now(datetime.timezone.utc).isoformat()));(r/'routes.json').write_text(json.dumps(log,indent=2),encoding='utf8')
d=fitz.open('D:/projects/indus_valley_script/data/raw/2026-10-21-town-axes/dating/lothal/rao1985lothal-part2.pdf')
for n in [68,69,70,71]: d[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(r/f'rao-pdf{n}.png')
