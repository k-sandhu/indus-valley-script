import requests,pathlib,json,concurrent.futures
L=pathlib.Path('data/raw/2026-10-20-khirsara-reserve')
urls={'publisher-root':'https://abisy.org.in/','publisher-index-http':'http://abisy.org.in/assets/All-pdf/Anukarmanika.pdf','nmma-2011-https':'https://nmma.nic.in/nmma/NAS1/nmma_doc/IAR/Indian%20Archaeology%20%202011%20-%202012%20%20A%20Review.pdf'}
def get(k,u):
 j={'id':k,'url':u}
 try:r=requests.get(u,timeout=20);j.update(status=r.status_code,bytes=len(r.content));(L/(k+'.response')).write_bytes(r.content)
 except Exception as e:j['error']=str(e)
 (L/(k+'.json')).write_text(json.dumps(j,indent=2));return j
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as p:
 for j in p.map(lambda kv:get(*kv),urls.items()):print(j,flush=True)
