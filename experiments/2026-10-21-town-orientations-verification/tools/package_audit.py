"""Audit manifest hashes, raster readability, owned files and local source coverage."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,json,collections
import numpy as np
import rasterio
from common import read_json,write_json,sha256,record,utc

def file_records(value):
    if isinstance(value,dict):
        if 'sha256' in value and 'path' in value:yield value
        for x in value.values():yield from file_records(x)
    elif isinstance(value,list):
        for x in value:yield from file_records(x)

def audit(manifests):
    checked={};failures=[];rasters=[]
    for manifest in manifests:
        for r in file_records(read_json(manifest)):
            key=(r['path'],r['sha256'])
            if key in checked:continue
            p=Path(r['path'])
            if not p.exists():failures.append(dict(path=r['path'],failure='missing'));continue
            got=sha256(p);ok=got==r['sha256'] and p.stat().st_size==r['bytes'];checked[key]=ok
            if not ok:failures.append(dict(path=r['path'],failure='hash or byte count mismatch',computed_sha256=got))
            if p.suffix.lower()=='.tif':
                try:
                    with rasterio.open(p) as ds:
                        a=ds.read();finite=bool(np.isfinite(a).all());counts=[int(np.sum(b==0)) for b in a]
                        result=dict(path=p.as_posix(),shape=list(a.shape),epsg=ds.crs.to_epsg() if ds.crs else None,finite=finite,zero_pixels_by_band=counts,readable=True)
                        if not finite or not ds.crs or not ds.transform.a:failures.append(dict(path=p.as_posix(),failure='invalid raster data or coordinates'))
                        result['zero_value_policy']='Zero scaled reflectance can be valid; no-data rejection uses raw DN and SCL during acquisition.'
                    rasters.append(result)
                except Exception as e:rasters.append(dict(path=p.as_posix(),readable=False,failure=str(e)));failures.append(dict(path=p.as_posix(),failure='raster unreadable: '+str(e)))
    return dict(schema_version=1,created_utc=utc(),manifests=list(manifests),checked_records=len(checked),hashes_match=all(checked.values()) and not any(r['failure'] in ['missing','hash or byte count mismatch'] for r in failures),rasters=rasters,failures=failures,overall_pass=not failures)

def inventory(raw,manifests):
    known={}
    for path in manifests:
        try:
            for r in file_records(read_json(path)):known[str(Path(r['path']).resolve()).lower()]=r
        except (ValueError,OSError):pass
    records=[]
    for p in sorted(Path(raw).rglob('*')):
        if not p.is_file():continue
        old=known.get(str(p.resolve()).lower())
        if old:records.append(old);continue
        # Files lacking a download record remain explicitly unresolved. They
        # cannot silently acquire a project licence merely by being local.
        name=p.as_posix();own=any('/'+part+'/' in name for part in ['plan-search','synthetic-development-1','synthetic-development-2','synthetic-final-v1','runways']) or p.suffix=='.json' and p.name=='acquisition-result.json'
        records.append(record(p,'local-generated' if own else 'unresolved; see parent acquisition records','own-work' if own else 'rights-unverified','Project working derivative; CC0 1.0' if own else 'Acquisition record unresolved; source rights retained',coverage_status='generated' if own else 'requires source reconciliation',retrieved_utc=__import__('datetime').datetime.fromtimestamp(p.stat().st_mtime,__import__('datetime').timezone.utc).isoformat()))
    return dict(schema_version=1,created_utc=utc(),file_count=len(records),logical_bytes=sum(r['bytes'] for r in records),files=records)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifests',nargs='+',required=True);p.add_argument('--output',required=True);p.add_argument('--inventory-raw');a=p.parse_args()
    result=inventory(a.inventory_raw,a.manifests) if a.inventory_raw else audit(a.manifests);write_json(a.output,result)
    print({k:v for k,v in result.items() if k not in ['rasters','files']})
if __name__=='__main__':main()
