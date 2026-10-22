"""Record anonymous Landsat 8/9 C2 Level-1 availability without paid buckets."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,requests
from common import read_json,write_json,record,utc
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('sites');p.add_argument('raw');p.add_argument('output');a=p.parse_args();root=Path(a.raw)/'landsat-attempt';root.mkdir(parents=True,exist_ok=False);files=[];attempts=[]
    url='https://planetarycomputer.microsoft.com/api/stac/v1/search'
    params=dict(collections='landsat-c2-l1',datetime='2018-01-01T00:00:00Z/2026-12-31T23:59:59Z',query=json.dumps({'platform':{'in':['landsat-8','landsat-9']}}),limit=1)
    try:
        r=requests.get(url,params=params,timeout=45);r.raise_for_status();path=root/'landsat-8-9-c2-l1-search.json';path.write_bytes(r.content);files.append(record(path,r.url,'rights-unverified','Microsoft Planetary Computer STAC metadata'))
        count=len(r.json().get('features',[]));attempts.append(dict(url=r.url,item_count_returned=count,outcome='No Landsat 8/9 Level-1 items' if not count else 'Items returned; further anonymous access check required'))
    except Exception as e:attempts.append(dict(url=url,failure=str(e)))
    collection=Path(a.raw)/'validation'/'service-attempts'/'planetary-computer-landsat-l1.json'
    data=read_json(collection) if collection.exists() else {}
    result=dict(schema_version=1,created_utc=utc(),files=files,attempts=attempts,collection_description=data.get('description'),collection_platforms=data.get('summaries',{}).get('platform'),collection_instruments=data.get('summaries',{}).get('instruments'),requester_pays_accessed=False,login_used=False,towns=[dict(slug=s['slug'],obtained=False,reason='No anonymously available Landsat 8/9 Collection 2 Level-1 product established. Planetary Computer Level-1 collection describes MSS on Landsat 1–5; its Level-2 collection does not supply the 15 m panchromatic band.',attempt_record='infra-v1/landsat-attempt-v1.json') for s in read_json(a.sites)['sites']])
    write_json(a.output,result);print(attempts)
if __name__=='__main__':main()
