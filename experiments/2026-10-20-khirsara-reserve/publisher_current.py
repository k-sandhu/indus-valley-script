import requests,pathlib,re,json,hashlib,concurrent.futures
L=pathlib.Path('data/raw/2026-10-20-khirsara-reserve')
for k,u in [('publisher-current-index','https://abisy.org.in/assetss/All-pdf/Anukarmanika.pdf'),('publisher-old-editions','https://abisy.org.in/php/old-editions.php')]:
 r=requests.get(u,timeout=30);r.raise_for_status();(L/(k+('.pdf' if r.content.startswith(b'%PDF') else '.html'))).write_bytes(r.content);print(k,len(r.content),hashlib.sha256(r.content).hexdigest(),flush=True)
 if 'editions' in k:print(json.dumps(re.findall(r'href=[\x22\x27]([^\x22\x27]+)[\x22\x27]',r.text),ensure_ascii=True))
