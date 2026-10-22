"""Acquire the small publisher PDFs linked by three already-held plan sources."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,requests
from common import record,write_json,check_space,utc
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('output');a=ap.parse_args();root=Path(a.raw);rows=[]
    for slug,name in [('sutkagen-dor','4-2/A%20Search.pdf'),('balakot','19-2/Shell.pdf'),('allahdino','28-2/Cattle.pdf')]:
        url='https://www.penn.museum/documents/publications/expedition/'+name;row=dict(slug=slug,url=url)
        try:
            r=requests.get(url,stream=True,timeout=60);r.raise_for_status();n=int(r.headers.get('Content-Length',0));limit=30_000_000
            if n>limit:raise ValueError('PDF exceeds 30 MB')
            chunks=[];size=0
            for b in r.iter_content(65536):
                size+=len(b)
                if size>limit:raise ValueError('PDF exceeds 30 MB')
                chunks.append(b)
            payload=b''.join(chunks);p=root/'plans'/slug/'penn-publisher-pdf'/'source.pdf';check_space(p,len(payload));p.parent.mkdir(parents=True,exist_ok=False)
            with p.open('xb') as f:f.write(payload)
            row['file']=record(p,url,'rights-unverified','Penn Museum Expedition publisher PDF; no explicit reuse licence verified')
        except Exception as e:row['failure']=str(e)
        rows.append(row);print(slug,row.get('file',{}).get('bytes'),row.get('failure',''),flush=True)
    write_json(a.output,dict(created_utc=utc(),sources=rows))
if __name__=='__main__':main()
