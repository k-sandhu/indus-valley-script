"""Reconcile held windows, recover offline composites and freeze current hashes."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,copy,re,shutil
import numpy as np
import rasterio
from common import read_json,write_json,record,sha256,utc
from acquire import BANDS,DESCS,RIGHTS,STAC,save_tif,item_epsg,tile
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('raw');ap.add_argument('infra');ap.add_argument('--output',default='imagery-manifest-v1.json');a=ap.parse_args()
    root=Path(a.raw);infra=Path(a.infra);sites=read_json(infra/'sites-located-v1.json')['sites']
    landsat={s['slug']:s for s in read_json(infra/'landsat-attempt-v1.json').get('towns',[])}
    items={};known={}
    def recs(v):
        if isinstance(v,dict):
            if all(k in v for k in ['path','bytes','sha256']):known[str(Path(v['path']).resolve())]=v
            for x in v.values():recs(x)
        elif isinstance(v,list):
            for x in v:recs(x)
    if (infra/'imagery-manifest-v1.json').exists():recs(read_json(infra/'imagery-manifest-v1.json'))
    for p in root.rglob('acquisition-result.json'):
        try:recs(read_json(p))
        except ValueError:pass
    needed={p.name.removesuffix('-window.tif') for p in root.rglob('*-window.tif')}
    for p in list((root/'imagery').rglob('stac-search-*.json'))+list((root/'validation'/'runway-imagery').rglob('stac-search-*.json')):
        try:
            for it in read_json(p).get('features',[]):
                if it['id'] in needed:items[it['id']]=it
        except ValueError:pass
    def current(p,url,**kw):
        old=known.get(str(p.resolve()),{})
        r=record(p,url,'explicit-license',RIGHTS,**kw)
        if old:r['retrieved_utc']=old['retrieved_utc'];r['acquisition_sha256']=old['sha256']
        return r
    def reconcile(slug,parent,point):
        scenes=[];unpaired=[]
        for p in sorted(parent.rglob('*-window.tif')):
            ident=p.name.removesuffix('-window.tif');mask=p.with_name(ident+'-scl.tif');it=items.get(ident)
            if not mask.exists() or not it:
                unpaired.append(dict(file=current(p,STAC),reason='No surviving SCL mask' if not mask.exists() else 'STAC item not recovered'));continue
            with rasterio.open(mask) as ds:scl=ds.read(1)
            if np.isin(scl,[0,1,3,8,9,10,11]).any():raise ValueError('Invalid SCL '+str(mask))
            with rasterio.open(p) as ds:
                arr=ds.read();epsg=ds.crs.to_epsg();bounds=list(ds.bounds);tr=ds.transform
                # DN zero is rejected before scaling during acquisition. A zero
                # surface reflectance after scale/offset can be a valid value;
                # SCL, full reads and recorded hashes establish validity here.
                if not np.isfinite(arr).all():raise ValueError('Invalid spectral window '+str(p))
            props=it['properties'];assets=[]
            for key in BANDS:
                asset=it['assets'][key];meta=asset.get('raster:bands',[{}])[0]
                assets.append(dict(band=key,url=asset['href'],native_resolution_m=20 if key in ['swir16','swir22'] else 10,resampling='bilinear to 10 m' if key in ['swir16','swir22'] else 'fractional window on aligned 10 m grid',scale=meta.get('scale',.0001),offset=meta.get('offset',0)))
            url=next(x['href'] for x in it['links'] if x['rel']=='self')
            scenes.append(dict(item_id=ident,self_link=url,datetime=props['datetime'],cloud_cover=props.get('eo:cloud_cover'),tile=tile(it),epsg=epsg,window_bounds=bounds,file=current(p,url,assets=assets,transformation='COG range window; surface reflectance; B11/B12 bilinear 20 m to 10 m'),scl=current(mask,it['assets']['scl']['href'],transformation='SCL nearest neighbour to 10 m'),scl_invalid_pixel_count=0))
        # A scene is retained once. Duplicate reads have a separate cleanup ledger.
        dedup={}
        for s in scenes:dedup[s['item_id']]=s
        scenes=list(dedup.values());composites=sorted(parent.rglob('median-composite.tif'),key=lambda p:p.stat().st_mtime_ns);comp=None;used=[]
        if composites:
            p=composites[-1];old=known.get(str(p.resolve()),{});parents=old.get('parents',[])
            selected=[s for s in scenes if known.get(str(Path(s['file']['path']).resolve()),{}).get('sha256') in parents or s['file']['sha256'] in parents]
            if not selected:raise ValueError('Cannot recover composite membership '+str(p))
            used=[s['item_id'] for s in selected]
            with rasterio.open(p) as ds:actual=ds.read()
            arrays=[]
            for s in selected:
                with rasterio.open(s['file']['path']) as ds:arrays.append(ds.read())
            median=np.median(np.stack(arrays),axis=0);expected=np.concatenate([median,median[:4].mean(axis=0)[None]])
            if not np.array_equal(actual,expected):raise ValueError('Composite differs from scene median '+str(p))
            comp=current(p,STAC,transformation='Median per band; brightness mean of B02 B03 B04 B08',parents=[s['file']['sha256'] for s in selected],pixel_median_verified=True)
        elif scenes:
            # Recover only held, masked scenes; no network requests are made.
            selected=scenes[:5] if slug.islower() else scenes[:16]
            grids={(s['epsg'],tuple(s['window_bounds'])) for s in selected}
            if len(grids)!=1:raise ValueError('Inconsistent grids '+slug)
            arrays=[]
            for s in selected:
                with rasterio.open(s['file']['path']) as ds:arrays.append(ds.read());tr=ds.transform
            median=np.median(np.stack(arrays),axis=0);median=np.concatenate([median,median[:4].mean(axis=0)[None]])
            d=parent/'offline-recovery-v1';d.mkdir(exist_ok=False);p=d/'median-composite.tif'
            save_tif(p,median,selected[0]['epsg'],tr,DESCS+['brightness'])
            used=[s['item_id'] for s in selected]
            comp=current(p,STAC,transformation='Offline recovery from verified held scenes; median per band; brightness mean of first four bands',parents=[s['file']['sha256'] for s in selected],pixel_median_verified=True)
        for s in scenes:s['used_in_composite']=s['item_id'] in used
        archived=[current(p,STAC,transformation='Retained earlier composite; superseded by current composite',parents=known.get(str(p.resolve()),{}).get('parents',[]),used_in_current_composite=False) for p in composites[:-1]]
        result=dict(slug=slug,point=point,scenes=scenes,composite=comp,archived_composites=archived,composite_scene_ids=used,scene_count_in_composite=len(used),unpaired_files=unpaired,mosaic=False,landsat=dict(obtained=False,attempt_record=(infra/'landsat-attempt-v1.json').as_posix()),status='available' if comp else 'missing-space',missing_reason=None if comp else 'No held complete masked scene; imagery acquisition requires 1.5 GB free')
        if scenes:result.update(epsg=scenes[0]['epsg'],tile=scenes[0]['tile'],window_bounds=scenes[0]['window_bounds'],window_metres=[5000,5000],resolution_m=10)
        print(slug,len(scenes),len(used),flush=True);return result
    towns=[reconcile(s['slug'],root/'imagery'/s['slug'],s['coordinate_used']) for s in sites]
    runway=[]
    for ref in read_json(infra/'runway-acquisition-v1.json')['references']:
        runway.append(reconcile(ref['airport'],root/'validation'/'runway-imagery'/'imagery'/ref['airport'],ref['point']))
    write_json(infra/a.output,dict(schema_version=1,created_utc=utc(),task='town-orientation-infrastructure',selection='October-April scenes, 2018-2026, cloud cover at most 3%; one MGRS tile per location; existing nine-scene composites retained, resumed acquisitions use up to five',towns=towns,runways=runway,rights_status='explicit-license',rights_notice=RIGHTS,free_bytes=shutil.disk_usage(root).free,missing_imagery_acquisition_order=[s['slug'] for s in towns if not s['composite']]))
if __name__=='__main__':main()
