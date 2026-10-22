"""Top up Kanmer and Shikarpur, then optional towns in order, subject to space."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,shutil
from common import read_json,write_json,utc
from acquire import imagery
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args();raw=Path(a.raw);infra=Path(a.infra)
    manifest=read_json(infra/'imagery-manifest-v1.json');sites=read_json(infra/'sites-located-v1.json')['sites'];held={x['slug']:x for x in manifest['towns']}
    order=['kanmer','shikarpur']+[s['slug'] for s in sites[11:]];results=[]
    for slug in order:
        old=held[slug]
        if old['scene_count_in_composite']>=5:continue
        free=shutil.disk_usage(raw).free
        if free<1_500_000_000:
            results.append(dict(slug=slug,status='skipped-space',checked_utc=utc(),free_bytes=free,reason='Imagery download requires at least 1.5 GB free'));continue
        cached={}
        for p in (raw/'imagery'/slug).rglob('stac-search-*.json'):
            try:
                for item in read_json(p).get('features',[]):
                    prop=item['properties']
                    if int(prop['datetime'][5:7]) in [10,11,12,1,2,3,4] and prop.get('eo:cloud_cover',99)<=3:cached[item['id']]=item
            except ValueError:pass
        site=next(s for s in sites if s['slug']==slug)
        try:
            result=imagery(site,raw,5,seed=old if old['scenes'] else None,cached_items=list(cached.values()))
            results.append(result)
        except Exception as e:results.append(dict(slug=slug,failure=str(e),free_bytes=shutil.disk_usage(raw).free))
        print('finished',slug,'free',shutil.disk_usage(raw).free,flush=True)
    write_json(infra/'imagery-acquisition-resume-v1.json',dict(schema_version=1,created_utc=utc(),towns=results,free_bytes=shutil.disk_usage(raw).free))
if __name__=='__main__':main()
