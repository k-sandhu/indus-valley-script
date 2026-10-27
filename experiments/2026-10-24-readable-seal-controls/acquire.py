import requests,pathlib,json,hashlib,datetime,fitz
root=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-readable-seal-controls'); pkg=pathlib.Path('experiments/2026-10-24-readable-seal-controls')
sources=[('urkesh-2002','https://urkesh.org/attach/Buccellati%202002%20Taram%20Agade%20Daughter%20of%20Naram%20Sin.pdf'),('urkesh-2005','https://urkesh.org/EL-MZ/Buccellati_and_Kelly-Buccellati_2005_Urkesh_as_Hurrian_Religious_Center_-_SMEA_47.pdf'),('ete-revised','https://library.cict.in/uploads/files/books/30.pdf'),('tnarch','https://www.tnarch.gov.in/tamil-brahmi-script'),('a14-239','https://urkesh.org/MZ/A/A14/D/I/0239.HTM'),('urkesh-1998','https://urkesh.org/attach/Buccellati_and_Kelly-Buccellati_1998_The_Courtiers_of_the_Queen_of_Urkesh_-_Subartu_42%20pp.%20195-216.pdf')]
if (pkg/'source-manifest.json').exists(): raise SystemExit('Frozen acquisition exists. Use a new dated acquisition directory and manifest for a rerun.')
manifest=[]
for sid,url in sources:
    entry=dict(source_id=sid,url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rights_status='rights-unverified',handling='local-only')
    try:
        r=requests.get(url,timeout=45); r.raise_for_status(); ext='pdf' if r.content[:4]==b'%PDF' else 'html'; p=root/(sid+'.'+ext); p.write_bytes(r.content)
        entry.update(status='acquired',bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest(),physical_path=str(p),logical_path='data/raw/2026-10-24-readable-seal-controls/'+p.name)
        if ext=='pdf':
            doc=fitz.open(p); entry['pages']=len(doc); (root/(sid+'.pages.json')).write_text(json.dumps([{'pdf_page':i+1,'text':p.get_text()} for i,p in enumerate(doc)],ensure_ascii=False),encoding='utf8')
    except Exception as e: entry.update(status='failed',error=str(e))
    manifest.append(entry); (pkg/'source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8'); print(sid,entry['status'],entry.get('bytes'))
