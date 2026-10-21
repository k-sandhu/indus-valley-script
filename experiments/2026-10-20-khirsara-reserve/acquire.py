import requests,re,pathlib,json,hashlib,datetime,concurrent.futures
L=pathlib.Path('data/raw/2026-10-20-khirsara-reserve');u='https://nmma.nic.in/nmma/archReview.do';r=requests.get(u,timeout=30);(L/'nmma-index.html').write_bytes(r.content)
links=re.findall(r'href\s*=\s*[\x22\x27]([^\x22\x27]+)[\x22\x27]',r.text)
print([x for x in links if any(s in x for s in ['2010','2011','2012','2013'])],flush=True)
urls={'iar2010-11':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202010%20-%202011%20%20A%20Review.pdf','iar2011-12':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202011%20-%202012%20%20A%20Review.pdf'}
for x in links:
 if '2012' in x and '2013' in x:urls['iar2012-13']=requests.compat.urljoin(u,x)
def get(k,u):
 j={'id':k,'url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rights':'rights-unverified'}
 try:
  z=requests.get(u,timeout=100);z.raise_for_status();assert z.content.startswith(b'%PDF');(L/(k+'.pdf')).write_bytes(z.content);j.update(status='acquired',bytes=len(z.content),sha256=hashlib.sha256(z.content).hexdigest())
 except Exception as e:j.update(status='failed',error=str(e))
 (L/(k+'-acquisition.json')).write_text(json.dumps(j,indent=2));return j
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for j in pool.map(lambda kv:get(*kv),urls.items()):print(j,flush=True)
p=pathlib.Path('data/normalized/lipi_observed_faces.jsonl');rs=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines()];out=[{'id':x['record_id'],'family':x['object_family_id'],'cisi':x['source_cisi'],'meta':{k:x['metadata'].get(k) for k in ['excavation-idno','area-section','room-grid','horizontal(mm)','vertical(mm)','thickness(mm)','type']}} for x in rs if 'khirs' in x['site'].lower()];(L/'corpus-identities.json').write_text(json.dumps(out,indent=2));print(out)
