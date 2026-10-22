"""Verify held rasters and scans, then losslessly recompress one TIFF at a time.

Run with the infrastructure venv and -I. Historical acquisition JSON is immutable;
the audit preserves original records and records replacement hashes separately.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import argparse, hashlib, shutil
import numpy as np
import rasterio
from common import read_json, write_json, sha256, utc

RESERVE = 250_000_000

def records(value):
    if isinstance(value, dict):
        if all(k in value for k in ('path', 'bytes', 'sha256')):
            yield value
        for v in value.values(): yield from records(v)
    elif isinstance(value, list):
        for v in value: yield from records(v)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw',required=True);ap.add_argument('--infra',required=True)
    a=ap.parse_args();root=Path(a.raw).resolve();infra=Path(a.infra)
    known={}
    for p in list(infra.glob('*.json'))+list(root.rglob('acquisition-result.json')):
        try:
            for r in records(read_json(p)): known.setdefault(str(Path(r['path']).resolve()).lower(),[]).append(r)
        except (ValueError,OSError): pass
    if (infra/'storage-verification-v1.json').exists():
        out=read_json(infra/'storage-verification-v1.json')
    else:
        out=dict(schema_version=1,created_utc=utc(),initial_free_bytes=shutil.disk_usage(root).free,rasters=[],scans=[],deletions=[],recompression=[])
    rasters=sorted(set((root/'imagery').rglob('*.tif'))|set((root/'validation'/'runway-imagery').rglob('*.tif')))
    # Complete the full read audit before changing any surviving raster.
    for p in ([] if out['rasters'] else rasters):
        old=known.get(str(p).lower(),[]);row=dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha256(p))
        try:
            with rasterio.open(p) as ds:
                bands=[ds.read(b) for b in ds.indexes]
                arr=np.stack(bands)
                expected=1 if p.name.endswith('-scl.tif') else 7 if p.name=='median-composite.tif' else 6
                if arr.shape!=(expected,500,500): raise ValueError(f'array shape {arr.shape}, expected {(expected,500,500)}')
                if not np.isfinite(arr).all(): raise ValueError('non-finite pixels')
                if any(r['bytes']!=row['bytes'] for r in old): raise ValueError('byte count differs from acquisition record')
                if any(r['sha256']!=row['sha256'] for r in old): raise ValueError('hash differs from acquisition record')
                row.update(shape=list(arr.shape),dtype=str(arr.dtype),pixel_sha256=hashlib.sha256(arr.tobytes()).hexdigest(),epsg=ds.crs.to_epsg(),transform=list(ds.transform),descriptions=list(ds.descriptions),record_found=bool(old),full_band_read_pass=True)
        except Exception as e:
            row.update(full_band_read_pass=False,failure=str(e))
            assert p.is_relative_to(root)
            out['deletions'].append(dict(path=p.as_posix(),bytes=p.stat().st_size,reason='Corrupt or truncated raster: '+str(e)))
            p.unlink()
        out['rasters'].append(row)
    # Hash every held source scan, including files not yet indexed as plans.
    for p in ([] if out['scans'] else sorted((root/'plans').rglob('*'))):
        if p.is_file():
            row=dict(path=p.as_posix(),bytes=p.stat().st_size,sha256=sha256(p))
            old=known.get(str(p).lower(),[])
            row['record_found']=bool(old);row['matches_records']=all(r['bytes']==row['bytes'] and r['sha256']==row['sha256'] for r in old)
            out['scans'].append(row)
    if not (infra/'storage-verification-v1.json').exists():write_json(infra/'storage-verification-v1.json',out)
    changes=[]
    for row in out['rasters']:
        if not row['full_band_read_pass']:continue
        p=Path(row['path']);tmp=p.with_suffix('.recompress.tmp.tif')
        if not p.exists():continue  # Separately recorded duplicate cleanup.
        with rasterio.open(p) as src:
            arr=src.read();profile=src.profile.copy();tags=src.tags();descriptions=src.descriptions
            assert hashlib.sha256(arr.tobytes()).hexdigest()==row['pixel_sha256'],p
            if src.compression.name=='deflate' and src.tags(ns='IMAGE_STRUCTURE').get('PREDICTOR')=='2':
                changes.append(dict(path=p.as_posix(),old_bytes=row['bytes'],new_bytes=p.stat().st_size,old_sha256=row['sha256'],new_sha256=sha256(p),pixel_sha256=row['pixel_sha256'],all_bands_identical=True,compression='DEFLATE',predictor=2,recovered_after_reserve_stop=True))
                continue
            bandtags=[src.tags(b) for b in src.indexes];scales=src.scales;offsets=src.offsets
            # Check the conservative uncompressed output bound before each write.
            bound=arr.nbytes+1_000_000;free=shutil.disk_usage(root).free
            if free-bound<RESERVE:raise OSError(f'Recompression needs {bound} bytes above reserve; free={free}')
            profile.update(compress='deflate',predictor=2,tiled=True,blockxsize=256,blockysize=256)
            with rasterio.open(tmp,'w',**profile) as dst:
                dst.write(arr);dst.update_tags(**tags);dst.descriptions=descriptions;dst.scales=scales;dst.offsets=offsets
                for b,t in enumerate(bandtags,1):dst.update_tags(b,**t)
        with rasterio.open(tmp) as dst:
            assert np.array_equal(arr,dst.read()),p
            assert dst.crs.to_epsg()==row['epsg'] and list(dst.transform)==row['transform']
        new=dict(path=p.as_posix(),old_bytes=row['bytes'],new_bytes=tmp.stat().st_size,old_sha256=row['sha256'],new_sha256=sha256(tmp),pixel_sha256=row['pixel_sha256'],all_bands_identical=True,compression='DEFLATE',predictor=2,free_before_bytes=free)
        # A small append-only journal survives a reserve stop or interruption.
        with (infra/'recompression-journal-v1.jsonl').open('a',encoding='utf-8') as journal:
            journal.write(__import__('json').dumps(new)+'\n')
        tmp.replace(p);changes.append(new)
        print('recompressed',p.parent.parent.name,p.name,new['old_bytes'],new['new_bytes'],flush=True)
    write_json(infra/'recompression-v1.json',dict(schema_version=1,created_utc=utc(),files=changes,final_free_bytes=shutil.disk_usage(root).free))
    print('deleted',out['deletions']);print('free',shutil.disk_usage(root).free)
if __name__=='__main__':main()
