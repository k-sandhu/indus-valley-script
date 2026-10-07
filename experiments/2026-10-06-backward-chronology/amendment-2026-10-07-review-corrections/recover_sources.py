"""Optional bounded recovery of three observed source URLs into a fresh local raw run."""
import argparse, hashlib, json, os, urllib.request, urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'data/raw/2026-10-06-backward-chronology/amendment-2026-10-07-review-corrections'
URLS={
 'petrie2012':'https://ijas.usb.ac.ir/article_1054_7880d0eba8951d2e17e4a19a17a8c13f.pdf',
 'magee2010-preview':'https://api.pageplace.de/preview/DT0400.9780857718013_A23726039/preview-9780857718013_A23726039.pdf',
 'coningham1996':'https://www.discoveringbuddha.org/wp-content/uploads/2025/02/1996-Passage-to-India-Anuradhapura-and-the-Early-Use-of-the-Brahmi-Script-team-of-4-1996.pdf'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(RAW)
    if out.exists():ap.error('Use a fresh raw directory.')
    out.mkdir(parents=True);tmp=out/'tmp';tmp.mkdir()
    for k in ['TMP','TEMP','MPLCONFIGDIR']:os.environ[k]=str(tmp)
    results=[]
    for sid,url in URLS.items():
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Indus research source verification'})
            try:response=urllib.request.urlopen(req,timeout=30)
            except urllib.error.HTTPError as e:response=e
            with response as r:
                status=r.status;data=r.read(25*1024*1024+1)
            if len(data)>25*1024*1024:raise ValueError('25 MB limit exceeded')
            valid=status==200 and data.startswith(b'%PDF-')
            path=out/(sid+('.pdf'if valid else '.response'))
            path.write_bytes(data)
            results.append(dict(id=sid,url=url,http_status=status,is_pdf=valid,bytes=len(data),local_witness=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(data).hexdigest(),outcome='acquired PDF'if valid else'failed PDF recovery'))
        except Exception as e:results.append(dict(id=sid,url=url,outcome='failed',error=str(e)))
    (out/'acquisition.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([dict(id=x['id'],outcome=x['outcome'])for x in results]))
if __name__=='__main__':main()
