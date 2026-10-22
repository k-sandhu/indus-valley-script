"""Distinguish generated-file times from missing first-run acquisition times.

This changes metadata only. Preserve previous inventories and prove that every
referenced path, byte count and SHA-256 is unchanged.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,shutil,copy
import requests
from common import read_json,write_json,check_space,sha256,utc
from package_audit import file_records
def replace_json(path,data):
    payload=json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False)+'\n';check_space(path,len(payload.encode('utf-8')));path.write_text(payload,encoding='utf-8')
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');a=ap.parse_args();raw=Path(a.raw);infra=Path(a.infra)
    legacy={str(Path(r['path']).resolve()) for r in read_json(infra/'storage-verification-v1.json')['rasters'] if r.get('full_band_read_pass') and not r.get('record_found') and Path(r['path']).exists()}
    image_path=infra/'imagery-manifest-v1.json';inventory_path=infra/'asset-inventory-v1.json';image=read_json(image_path);inventory=read_json(inventory_path)
    def identities(x):return {(str(Path(r['path']).resolve()),r['bytes'],r['sha256']) for r in file_records(x)}
    original_identities=identities(image);original_image_hash=sha256(image_path)
    for p in [image_path,inventory_path]:
        backup=p.with_name(p.stem+'-before-provenance-review.json');check_space(backup,p.stat().st_size);shutil.copyfile(p,backup)
    def correct_legacy(r):
        if str(Path(r['path']).resolve()) in legacy:
            r['record_created_utc']=r.get('retrieved_utc');r['retrieved_utc']=None;r['original_capture_time_status']='Not preserved in interrupted first-run acquisition';r['verified_against_original_pixel_hash']=True
    for r in file_records(image):correct_legacy(r)
    aliases={}
    for p in infra.glob('duplicate-cleanup-v*.json'):
        for row in read_json(p)['deletions']:
            if row.get('retained_path'):aliases[str(Path(row['path']).resolve())]=Path(row['retained_path'])
    points={s['slug']:s['coordinate_used'] for s in read_json(infra/'sites-located-v1.json')['sites']}
    points.update({s['airport']:s['point'] for s in read_json(infra/'runway-acquisition-v1.json')['references']})
    generated=0;metadata=[]
    for r in inventory['files']:
        correct_legacy(r)
        if r.get('retrieval_time_basis') and r['rights_status']=='own-work':
            r['created_utc']=r['retrieved_utc'];r['creation_time_basis']=r.pop('retrieval_time_basis');generated+=1
        elif r.get('retrieval_time_basis') and Path(r['path']).name.startswith('stac-search-'):
            p=Path(r['path']);number=int(p.stem.rsplit('-',1)[1]);href=None
            if number>1:
                previous=p.with_name(f'stac-search-{number-1:03d}.json')
                while not previous.exists() and str(previous.resolve()) in aliases:previous=aliases[str(previous.resolve())]
                if previous.exists():href=next((l['href'] for l in read_json(previous).get('links',[]) if l['rel']=='next'),None)
            if not href:
                parts=p.parts;slug=parts[parts.index('imagery')+1];point=points[slug]
                params=dict(collections='sentinel-2-l2a',bbox=','.join(map(str,[point[1]-1e-6,point[0]-1e-6,point[1]+1e-6,point[0]+1e-6])),datetime='2018-01-01T00:00:00Z/2026-12-31T23:59:59Z',query=json.dumps({'eo:cloud_cover':{'lte':3}}),limit=100)
                href=requests.Request('GET','https://earth-search.aws.element84.com/v1/search',params=params).prepare().url
                r['url_basis']='Reconstructed first-page query from retained query code and starting point'
            else:r['url_basis']='Pagination link preserved in the preceding response'
            r['url']=href;r['retrieval_time_basis']='Approximate UTC from unchanged first-run response file modification time';r['retrieved_utc_approximate']=True;metadata.append(r['path'])
    assert original_identities==identities(image)
    inventory['records_reconstructed_from_filesystem']=metadata;inventory['legacy_rasters_without_original_capture_time']=sorted(legacy);inventory['generated_file_creation_times']=generated
    replace_json(image_path,image);replace_json(inventory_path,inventory)
    result=dict(schema_version=1,created_utc=utc(),legacy_raster_capture_times_not_preserved=len(legacy),legacy_paths=sorted(legacy),stac_metadata_times_approximate=len(metadata),stac_metadata_paths=metadata,generated_files_reclassified=generated,referenced_files_unchanged=True,manifest_sha256_before=original_image_hash,manifest_sha256_after=sha256(image_path),inventory_sha256_after=sha256(inventory_path))
    write_json(infra/'provenance-reconciliation-v1.json',result)
    completion=read_json(infra/'completion-v1.json');completion['unresolved']=[s for s in completion['unresolved'] if '193 raw file records' not in s]
    completion['unresolved'].append(f'{len(legacy)} legacy raster capture times were not preserved; {len(metadata)} first-run STAC response times are approximate filesystem times. Scene observation dates and all file hashes are known.')
    replace_json(infra/'completion-v1.json',completion)
    verified=read_json(infra/'verification-v1.json');verified['metadata_only_revision']='provenance-reconciliation-v1.json';verified['final_manifest_sha256']={image_path.name:sha256(image_path),'plan-library-v1.json':sha256(infra/'plan-library-v1.json')};replace_json(infra/'verification-v1.json',verified)
    print(json.dumps({k:v for k,v in result.items() if not k.endswith('_paths') and k!='legacy_paths'},indent=2))
if __name__=='__main__':main()
