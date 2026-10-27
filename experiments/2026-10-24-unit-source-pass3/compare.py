import urllib.request,pathlib,fitz,json,hashlib,re,datetime
p=pathlib.Path('D:/projects/indus_valley_script/data/raw/2026-10-24-unit-source-pass3');url='https://www.harappa.com/sites/default/files/pdf/Kenoyer-Meadow-2010-HARP.pdf'
r={'label':'harp-linked','url':url,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
try:
 b=urllib.request.urlopen(url,timeout=40).read(30000001);f=p/'harp-linked.pdf';f.write_bytes(b);r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),physical_path=str(f),logical_path='data/raw/2026-10-24-unit-source-pass3/'+f.name)
 d=fitz.open(f); old=fitz.open('research/corpus/primary/kenoyer_meadow2010_inscribed_objects.pdf');a=[x.get_text() for x in d];o=[x.get_text() for x in old];(p/'new-chapter-text.json').write_text(json.dumps(a),encoding='utf8');(p/'held-chapter-text.json').write_text(json.dumps(o),encoding='utf8');norm=lambda t:re.sub(r'\W','',t).lower()
 comparisons=[{'new_page':i+3,'held_page':i+1,'equal_normalized_text':norm(a[i+2])==norm(t)} for i,t in enumerate(o)];(p/'edition-comparison-v1.json').write_text(json.dumps({'new_pages':len(d),'held_pages':len(old),'comparisons':comparisons,'search_stems':{s:[i+1 for i,t in enumerate(a) if s in t] for s in ['9406','2229','9438','8303','8381','48.03','57.04','49.05','50.08','40.04']},'bibliography_pages':[i+1 for i,t in enumerate(a) if 'Bibliography' in t]}),encoding='utf8');print(r);print(comparisons);print(a[-1][-4500:])
except Exception as e:r['error']=str(e);print(r)
(p/'linked-acquisition-v1.json').write_text(json.dumps(r,indent=2),encoding='utf8')
