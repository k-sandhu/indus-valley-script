"""Record a coordinate conflict encountered while indexing the held plans.

Only coordinate lines are extracted; no archaeological direction is sought.
The additional excavation report is bounded to 30 MB before any file write.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,io,re
import requests,pymupdf
from common import record,write_json,check_space,read_json,GEOD,utc
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args();root=Path(a.raw);infra=Path(a.infra)
    url='https://old.harappa.com/goladhoro/Excavations-at-Shikarpur-2007.pdf'
    response=requests.get(url,stream=True,timeout=60);response.raise_for_status()
    size=int(response.headers.get('Content-Length',0));limit=30_000_000
    if size>limit:raise ValueError('Plan source exceeds 30 MB')
    chunks=[];total=0
    for chunk in response.iter_content(65536):
        total+=len(chunk)
        if total>limit:raise ValueError('Plan source exceeds 30 MB')
        chunks.append(chunk)
    payload=b''.join(chunks);p=root/'plans/shikarpur/report2007-source/source.pdf';check_space(p,len(payload));p.parent.mkdir(parents=True,exist_ok=False);p.write_bytes(payload)
    f=record(p,url,'rights-unverified','Public excavation report on harappa.com; no reuse licence verified')
    observations=[]
    with pymupdf.open(p) as d:
        for n,pg in enumerate(d,1):
            text=pg.get_text();lines=text.splitlines()
            for j,line in enumerate(lines):
                if 'Gola Dhoro (Bagasara)' in line:
                    observations.append(dict(source=f['path'],pdf_page=n,coordinate_text=' '.join(lines[j:j+3])))
    site=next(s for s in read_json(infra/'sites-located-v1.json')['sites'] if s['slug']=='gola-dhoro')
    published_old=[23+2/60+12/3600,70+31/60+13.86/3600]
    published_new=[23+2/60+12/3600,70+37/60+11/3600]
    def distance(q):return GEOD.inv(site['coordinate_used'][1],site['coordinate_used'][0],q[1],q[0])[2]
    write_json(infra/'coordinate-source-review-resume-v1.json',dict(schema_version=1,created_utc=utc(),source=f,observations=observations,slug='gola-dhoro',coordinate_used=site['coordinate_used'],earlier_excavation_report_coordinate=published_old,earlier_coordinate_distance_m=distance(published_old),held_2025_article_coordinate=published_new,held_2025_source=(root/'plans/shikarpur/deshpande2025/source.pdf').as_posix(),held_2025_pdf_page=4,held_2025_coordinate_distance_m=distance(published_new),decision='Retain existing starting point, consistent with the earlier excavator coordinate; flag conflicting published longitudes for the measurers. No site bearing was measured.'))
    print('source bytes',len(payload),'coordinate observations',observations)
if __name__=='__main__':main()
