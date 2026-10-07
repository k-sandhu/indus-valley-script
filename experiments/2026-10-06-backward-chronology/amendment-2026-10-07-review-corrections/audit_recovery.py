"""Audit acquired signatures and query witnesses without repeating network calls."""
import argparse, hashlib, json
from pathlib import Path
from build_corrections import ROOT, OWN, RAW, read, write
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Use a fresh output file.')
    acquisitions=read(RAW/'acquisition-01.json')+[read(RAW/'petrie2012-pdf.acquisition.json'),read(RAW/'coningham1996.acquisition.json')]
    for x in acquisitions:
        p=ROOT/x['local_witness'];x['hash_verified']=hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
        assert x['hash_verified']
        x['pdf_signature']=p.read_bytes().startswith(b'%PDF-')
        x['usable_pdf']=x['http_status']==200 and x['pdf_signature']
    queries=[]
    for p in sorted(RAW.glob('web-*.json')):
        data=read(p);queries.append(dict(witness=p.relative_to(ROOT).as_posix(),request=data['request'],sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    write(out,dict(status='Verified computation',query_batches=len(queries),query_witnesses=queries,download_attempts=len(acquisitions),http_failures=sum(x['http_status']!=200 for x in acquisitions),acquisitions=acquisitions,
        unresolved_targets=['Jarrige and Santoni 1979 primary chronology','Magee and Petrie 2010 recalibration chapter','Exact catalogue concordance for Kenoyer Fig. 3','Allchin/Coningham 1995 original chapter','Coningham et al. 1996 full paper'],
        failed_search_note='Queries recovered bibliographic/review/summary records for these targets, without their required primary date or specimen joins. Individual requests and tool errors remain in the raw response witnesses. The 1996 filename ends in .pdf but contains HTTP 403 HTML.'))
    print(json.dumps(dict(query_batches=len(queries),download_attempts=len(acquisitions),http_failures=sum(x['http_status']!=200 for x in acquisitions))))
if __name__=='__main__':main()
