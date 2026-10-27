import urllib.request,json,hashlib,datetime,pathlib
root=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-harappa-context-pass2')
urls={
'kenoyer2009-old.pdf':'https://www.harappa.com/sites/default/files/pdf/Kenoyer2009%20Indus%20Seals_0.pdf',
'kenoyer2009.pdf':'https://www.harappa.com/sites/default/files/pdf/Kenoyer2009%20Indus%20Seals.pdf',
'kenoyer1999.pdf':'https://www.harappa.com/sites/default/files/pdf/Kenoyer1999_Harappa%20New%20Discoveries%20on%20its%20origins%20and%20growt.pdf',
'large-unicorn.html':'https://www.harappa.com/slide/large-unicorn-seal',
'chapter-page.html':'https://www.harappa.com/content/indus-seals-overview-iconography-and-style-0'}
records=[]
for name,url in urls.items():
 r={'name':name,'url':url,'acquired_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rights_status':'rights-unverified','handling':'local-only'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as f: data=f.read();r['status']=f.status
  (root/name).write_bytes(data);r.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),physical_path=str(root/name),logical_path='data/raw/2026-10-24-harappa-context-pass2/'+name)
 except Exception as e:r['error']=str(e)
 records.append(r)
(root/'acquisition.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
