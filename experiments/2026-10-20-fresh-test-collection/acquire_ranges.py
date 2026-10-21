import concurrent.futures,requests,pathlib,time
p=pathlib.Path('data/raw/2026-10-20-fresh-test-collection');u='https://ia800806.us.archive.org/3/items/excavationsatfarmana200608vshindeetal_212_v/Excavations%20at%20Farmana%2C%202006-08%20-%20V%20Shinde%20et%20al.pdf';size=107158489;chunk=4000000
def get(i):
 a=i*chunk;b=min(size-1,a+chunk-1);r=requests.get(u,headers={'Range':f'bytes={a}-{b}'},timeout=60);r.raise_for_status();assert len(r.content)==b-a+1;(p/f'part-{i:02d}').write_bytes(r.content);return i
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
 for i in pool.map(get,range((size+chunk-1)//chunk)): print(i,flush=True)
(p/'farmana-chunked.pdf').write_bytes(b''.join((p/f'part-{i:02d}').read_bytes() for i in range((size+chunk-1)//chunk)))
