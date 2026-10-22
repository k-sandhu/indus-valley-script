"""Acquire named archive reports, reference services and optional Landsat metadata."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,requests,concurrent.futures
from urllib.parse import quote
from common import write_json,record,utc
from acquire import download

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('raw');p.add_argument('output');a=p.parse_args();root=Path(a.raw);files=[];attempts=[]
    jobs=[('surkotada','masi87excavationsatsurkotadaandkutchjagatpatijoshi_841_t'),('lothal','masi78lothalaharappanporttownraos.r.part1_312_a'),('rakhigarhi','excavationsatrakhigarhi19972000amarendranath_457_Z'),('farmana','excavationsatfarmana200608vshindeetal_212_v')]
    def archive(job):
        slug,item=job;out=[]
        try:
            d=root/'plans'/slug/item;d.mkdir(parents=True,exist_ok=True);url='https://archive.org/metadata/'+item;r=requests.get(url,timeout=40);r.raise_for_status();path=d/'metadata.json';path.write_bytes(r.content);out.append(record(path,url,'rights-unverified','Internet Archive uploader metadata; does not settle report rights'))
            data=r.json();pdfs=[f for f in data.get('files',[]) if f['name'].lower().endswith('.pdf') and f.get('format') in ['Text PDF','Image Container PDF','Additional Text PDF']]
            if not pdfs:pdfs=[f for f in data.get('files',[]) if f['name'].lower().endswith('.pdf')]
            pdfs.sort(key=lambda f:('text' not in f['name'].lower(),int(f.get('size',10**12))))
            if not pdfs:raise ValueError('No anonymous PDF listed')
            file=pdfs[0];u='https://archive.org/download/'+item+'/'+quote(file['name']);out.append(download(u,d/'source.pdf','rights-unverified','Archive.org scan; copyright of source report not verified'))
            return dict(slug=slug,item=item,files=out)
        except Exception as e:return dict(slug=slug,item=item,files=out,failure=str(e))
    with concurrent.futures.ThreadPoolExecutor(4) as pool:archives=list(pool.map(archive,jobs))
    for item in archives:files.extend(item['files']);print(item['slug'],item.get('failure','acquired'),flush=True)
    # Independently computed official IGRF outputs, avoiding any archaeological location.
    for lat,lon,year in [(0,0,2025),(45,-75,1900),(-33,151,2030)]:
        url='https://geomag.bgs.ac.uk/web_service/GMModels/igrf/14/'
        try:
            r=requests.get(url,params=dict(latitude=lat,longitude=lon,altitude=0,date=f'{year}-01-01',format='json'),timeout=60);r.raise_for_status();d=root/'igrf'/'official-tests';d.mkdir(parents=True,exist_ok=True);path=d/f'{lat}-{lon}-{year}.json';path.write_bytes(r.content);files.append(record(path,r.url,'rights-unverified','BGS IGRF-14 official calculator output; API result'))
        except Exception as e:attempts.append(dict(url=url,case=[lat,lon,year],failure=str(e)))
    for ident in ['VAAH','VABJ','VAKE','VIBT','VIHR']:
        url='https://aim-india.aai.aero/eaip/eaip-v2-06-2026/eAIP/IN-AD%202.1'+ident+'-en-GB.html'
        try:files.append(download(url,root/'validation'/'official-aip'/f'{ident}.html','rights-unverified','Airports Authority of India eAIP; rights unverified'))
        except Exception as e:attempts.append(dict(url=url,failure=str(e),retrieved_utc=utc()))
    for url,name in [('https://caapakistan.com.pk/AIS/AIS.aspx','pakistan-ais.html'),('https://planetarycomputer.microsoft.com/api/stac/v1/collections/landsat-c2-l1','planetary-computer-landsat-l1.json')]:
        try:files.append(download(url,root/'validation'/'service-attempts'/name,'rights-unverified','Public service response; rights unverified'))
        except Exception as e:attempts.append(dict(url=url,failure=str(e),retrieved_utc=utc()))
    write_json(a.output,dict(files=files,archives=archives,attempts=attempts))
if __name__=='__main__':main()
