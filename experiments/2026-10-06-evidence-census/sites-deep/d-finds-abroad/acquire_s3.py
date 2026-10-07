"""Recover two original reports through the current ISAC public asset route."""
import pathlib, urllib.request, hashlib, json, os
import fitz
ROOT=pathlib.Path(__file__).resolve().parents[4]
RAW=ROOT/'data/raw/2026-10-06-evidence-census/sites-deep/d-finds-abroad'
for k in ('TMP','TEMP','MPLCONFIGDIR'): os.environ[k]=str(RAW/'tmp')
(RAW/'tmp').mkdir(exist_ok=True)
urls={'nippur1993':'https://isac-assets.s3.amazonaws.com/isac-publications/oip111.pdf?VersionId=cvnwqpeceewulu3XPV9UTzV32j9_KbUl','frankfort1933':'https://isac-assets.s3.amazonaws.com/isac-publications/oic16.pdf?VersionId=2y0wkg.GlDeKiCmzNwNCQi7wmVdYXxIS'}
records=[]
for sid,url in urls.items():
 r={'id':sid,'url':url,'date':'2026-10-07','new_route':'current ISAC landing-page download link','handling':'local-only'}
 try:
  p=RAW/(sid+'-s3.pdf')
  if not p.exists():
   with urllib.request.urlopen(url,timeout=60) as f: payload=f.read()
   if not payload.startswith(b'%PDF'): raise ValueError('Not PDF')
   p.write_bytes(payload)
  doc=fitz.open(p)
  text='\n'.join('[PDF PAGE %d]\n'%(i+1)+page.get_text() for i,page in enumerate(doc))
  txt=RAW/(sid+'-s3.txt')
  if txt.exists():
   if txt.read_text(encoding='utf-8')!=text:raise RuntimeError('Existing extraction differs; use a new witness path')
  else:txt.write_text(text,encoding='utf-8')
  r.update(status='acquired',pages=len(doc),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 except Exception as exc: r.update(status='failed',error=str(exc))
 records.append(r);print(sid,r)
manifest=RAW/'s3-acquisition.json';payload=json.dumps(records,indent=2)
if manifest.exists():
 if manifest.read_text(encoding='utf-8')!=payload:raise RuntimeError('Saved acquisition differs; use a new manifest path')
else:manifest.write_text(payload,encoding='utf-8')
