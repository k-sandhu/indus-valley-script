"""Acquire primary witnesses into the owned, ignored raw directory."""
import concurrent.futures
import datetime
import hashlib
import json
from pathlib import Path
import requests
import fitz
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-12-transmission-hypothesis/texts'
PLAN=[
 ('rv9-sanskrit','https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/1_sam/1_rv/rv_hn09u.htm'),
 ('rv10-sanskrit','https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/1_veda/1_sam/1_rv/rv_hn10u.htm'),
 ('rv9112-griffith','https://sacred-texts.com/hin/rigveda/rv09112.htm'),
 ('rv10071-griffith','https://sacred-texts.com/hin/rigveda/rv10071.htm'),
 ('rv10101-griffith','https://sacred-texts.com/hin/rigveda/rv10101.htm'),
 ('yasna9-avestan','https://www.avesta.org/yasna/y9.htm'),
 ('yasna-mills','https://www.avesta.org/yasna/yasna.htm'),
 ('vendidad3-avestan','https://www.avesta.org/vendidad/vd3.htm'),
 ('vendidad3-darmesteter','https://www.avesta.org/vendidad/vd3sbe.htm'),
 ('witzel-harappa-repository','https://fid4sa-repository.ub.uni-heidelberg.de/120/1/LanguagesHarappa_1998.pdf'),
 ('witzel-substrates1999-author','https://www.michaelwitzel.org/wp-content/uploads/2014/06/ejvs0501article.pdf'),
 ('greek-repo-commit','https://api.github.com/repos/PerseusDL/canonical-greekLit/commits/master'),
 ('bilara-repo-commit','https://api.github.com/repos/suttacentral/bilara-data/commits/published'),
]


def sha(data):return hashlib.sha256(data).hexdigest()


def capture(item,tag):
 ident,url=item
 row=dict(witness_id=ident,requested_url=url,retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tls_verification=True,rights='rights-unverified',redistribution='local-only')
 try:
  r=requests.get(url,timeout=30,headers={'User-Agent':'Source inspection research/1.0','Accept':'*/*'})
  data=r.content
  kind='pdf' if data.startswith(b'%PDF') else 'html' if b'<html' in data[:3000].lower() or b'<!doctype' in data[:3000].lower() else 'json' if 'json' in r.headers.get('Content-Type','') else 'bin'
  dest=RAW/f'{ident}-{tag}.{kind}'
  if dest.exists():raise FileExistsError(dest)
  dest.write_bytes(data)
  row.update(status_code=r.status_code,resolved_url=r.url,path=dest.relative_to(ROOT).as_posix(),bytes=len(data),sha256=sha(data),content_type=r.headers.get('Content-Type'),format=kind)
  if kind=='pdf':
   doc=fitz.open(stream=data,filetype='pdf')
   derivative=RAW/f'{ident}-{tag}-pages.json'
   content=json.dumps(dict(parent_path=row['path'],parent_sha256=row['sha256'],tool='PyMuPDF',version=fitz.VersionBind,pages=[dict(pdf_page_1based=i+1,text=page.get_text()) for i,page in enumerate(doc)]),ensure_ascii=False,indent=2).encode('utf8')
   row['pdf_pages']=len(doc)
  elif kind=='html':
   soup=BeautifulSoup(data,'html.parser')
   for node in soup(['script','style','nav']):node.decompose()
   content=('\n'.join(x.strip() for x in soup.get_text('\n').splitlines() if x.strip())+'\n').encode('utf8')
   derivative=RAW/f'{ident}-{tag}-text.txt'
  else:return row
  if derivative.exists():raise FileExistsError(derivative)
  derivative.write_bytes(content)
  row['derivative']=dict(path=derivative.relative_to(ROOT).as_posix(),sha256=sha(content),bytes=len(content),parent_sha256=row['sha256'])
 except Exception as exc:row['error']=type(exc).__name__+': '+str(exc)
 return row


def main():
 RAW.mkdir(parents=True,exist_ok=True)
 target=RAW/'capture-v1.json'
 if target.exists():raise FileExistsError(target)
 frozen=json.loads((HERE/'freeze-v1.json').read_text('utf8'))
 for row in frozen['files']:
  if sha((ROOT/row['path']).read_bytes())!=row['sha256']:raise ValueError('Selection/protocol changed before capture')
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda item:capture(item,'v1'),PLAN))
 target.write_text(json.dumps(dict(script_sha256=sha(Path(__file__).read_bytes()),freeze_sha256=sha((HERE/'freeze-v1.json').read_bytes()),attempts=rows),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 for row in rows:print(row['witness_id'],row.get('status_code'),row.get('format'),row.get('bytes'),row.get('error',''))


if __name__=='__main__':main()
