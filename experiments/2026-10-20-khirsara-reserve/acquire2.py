import requests,pathlib,json,concurrent.futures,hashlib,datetime
L=pathlib.Path('data/raw/2026-10-20-khirsara-reserve')
urls={'publisher-index':'https://abisy.org.in/assets/All-pdf/Anukarmanika.pdf','iar2010-11':'http://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202010%20-%202011%20%20A%20Review.pdf','iar2011-12':'https://asi.nic.in/wp-content/uploads/2015/12/INDIAN%20ARCHAEOLOGY-A%20Review%202011-12%20submitted%20to%20DG,ASI.pdf','iar2012-13':'http://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202012%20-%202013%20%20A%20Review.pdf'}
def get(k,u):
 j={'id':k,'url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rights':'rights-unverified'}
 try:
  r=requests.get(u,timeout=35);j['http_status']=r.status_code;r.raise_for_status();assert r.content.startswith(b'%PDF'),r.headers.get('content-type');(L/(k+'.pdf')).write_bytes(r.content);j.update(status='acquired',bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest())
 except Exception as e:j.update(status='failed',error=str(e))
 (L/(k+'-attempt2.json')).write_text(json.dumps(j,indent=2));return j
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 for j in pool.map(lambda kv:get(*kv),urls.items()):print(j,flush=True)
p=pathlib.Path('data/normalized/lipi_observed_faces.jsonl');rs=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines()];out=[{'id':x['record_id'],'family':x['object_family_id'],'cisi':x['source_cisi'],'meta':{k:x['metadata'].get(k) for k in ['excavation-idno','area-section','room-grid','horizontal(mm)','vertical(mm)','thickness(mm)','type']}} for x in rs if 'khirs' in x['site'].lower()];(L/'corpus-identities.json').write_text(json.dumps(out,indent=2));print(out)
