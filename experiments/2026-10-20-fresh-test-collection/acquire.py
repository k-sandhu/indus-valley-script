import requests,pathlib,json,hashlib,datetime
p=pathlib.Path('data/raw/2026-10-20-fresh-test-collection'); u='https://archive.org/download/excavationsatfarmana200608vshindeetal_212_v/Excavations%20at%20Farmana%2C%202006-08%20-%20V%20Shinde%20et%20al.pdf'
r=requests.get(u,timeout=180);r.raise_for_status();(p/'farmana.pdf').write_bytes(r.content)
j={'url':u,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':len(r.content),'sha256':hashlib.sha256(r.content).hexdigest(),'rights':'rights-unverified','prior_held':'manifest says not-held; holdings filename search found no Farmana PDF'};(p/'acquisition.json').write_text(json.dumps(j,indent=2));print(j)
