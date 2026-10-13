"""Acquire native Sentinel and DEM windows with exact georeferencing records."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from concurrent.futures import ThreadPoolExecutor
import argparse,hashlib,json,math,time
import numpy as np
import requests,rasterio
from rasterio.windows import from_bounds,Window
from rasterio.warp import transform_bounds
from pyproj import Transformer
from shapely.geometry import shape,box

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent
API='https://earth-search.aws.element84.com/v1'
ENV=dict(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',CPL_VSIL_CURL_ALLOWED_EXTENSIONS='.tif',GDAL_HTTP_TIMEOUT=90,GDAL_HTTP_MAX_RETRY=3,GDAL_HTTP_RETRY_DELAY=2,GDAL_CACHEMAX=128)
BANDS=['blue','green','red','nir','swir16','swir22','scl']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def savejson(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def relative(path):return path.resolve().relative_to(ROOT).as_posix()

def stac_search(collection,bbox,interval):
    payload=dict(collections=[collection],bbox=bbox,datetime=interval,limit=200,query={'eo:cloud_cover':{'lte':10}})
    r=requests.post(API+'/search',json=payload,timeout=90);r.raise_for_status()
    return r.json(),payload

def read_window(url,bbox,path,band):
    if path.exists():raise FileExistsError(path)
    error=None
    for attempt in range(3):
        try:
            with rasterio.Env(**ENV),rasterio.open(url) as src:
                native_bounds=transform_bounds('EPSG:4326',src.crs,*bbox,densify_pts=21)
                fractional=from_bounds(*native_bounds,transform=src.transform)
                x0=max(0,math.floor(fractional.col_off));y0=max(0,math.floor(fractional.row_off))
                x1=min(src.width,math.ceil(fractional.col_off+fractional.width));y1=min(src.height,math.ceil(fractional.row_off+fractional.height))
                if x1<=x0 or y1<=y0:raise ValueError('Empty native overlap')
                window=Window(x0,y0,x1-x0,y1-y0)
                data=src.read(1,window=window)
                profile=src.profile.copy();profile.update(width=data.shape[1],height=data.shape[0],count=1,transform=src.window_transform(window),compress='deflate',tiled=True,blockxsize=256,blockysize=256)
                with rasterio.open(path,'w',**profile) as dst:dst.write(data,1)
                return dict(band=band,url=url,local_path=relative(path),bytes=path.stat().st_size,sha256=sha(path),native_crs=str(src.crs),native_pixel=list(src.res),native_transform=list(src.window_transform(window))[:6],native_window=[x0,y0,x1-x0,y1-y0],shape=list(data.shape),nodata=src.nodata,parent_asset_shape=[src.height,src.width],acquisition='Unsigned HTTP-range COG window, written with native DN and georeferencing; full remote checksum not independently verified')
        except Exception as exc:
            error=str(exc)
            if path.exists():raise
            time.sleep(1)
    raise RuntimeError(error)

def main():
    p=argparse.ArgumentParser();p.add_argument('--blocks',type=Path,default=BASE/'blocks-v1.json');p.add_argument('--output',type=Path,required=True);p.add_argument('--only',nargs='*')
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True)
    config=json.loads(a.blocks.read_text(encoding='utf-8'))
    records=[];failures=[]
    for b in config['blocks']:
        if a.only and b['id'] not in a.only:continue
        directory=a.output/b['id'];directory.mkdir()
        toxy=Transformer.from_crs(4326,b['native_epsg'],always_xy=True);tolon=Transformer.from_crs(b['native_epsg'],4326,always_xy=True)
        cx,cy=toxy.transform(*b['center_lonlat']);left=math.floor((cx-b['width_m']/2)/10)*10;bottom=math.floor((cy-b['height_m']/2)/10)*10
        bounds_m=[left,bottom,left+b['width_m'],bottom+b['height_m']]
        bbox=list(transform_bounds(b['native_epsg'],4326,*bounds_m,densify_pts=21))
        br=dict(**b,bbox_lonlat=bbox,bounds_native_m=bounds_m,width_pixels=b['width_m']//10,height_pixels=b['height_m']//10,scenes=[],dem_tiles=[])
        print(json.dumps(dict(stage='block',id=b['id'],bbox=bbox)),flush=True)
        used=set()
        for date in config['requested_dates']:
            center=datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
            start=(center-timedelta(days=45)).isoformat().replace('+00:00','Z');end=min(center+timedelta(days=45),datetime(2026,10,12,23,59,tzinfo=timezone.utc)).isoformat().replace('+00:00','Z')
            data,payload=stac_search(config['sentinel_collection'],bbox,start+'/'+end)
            savejson(directory/f'query-{date}.json',dict(request=payload,response=data))
            target_polygon=box(*bbox)
            candidates=[x for x in data['features'] if shape(x['geometry']).covers(target_polygon) and x['id'] not in used]
            candidates.sort(key=lambda x:(abs((datetime.fromisoformat(x['properties']['datetime'].replace('Z','+00:00'))-center).total_seconds()),x['properties'].get('eo:cloud_cover',100)))
            if not candidates:
                failures.append(dict(block=b['id'],requested_date=date,reason='No single low-cloud tile covers the whole block'));continue
            item=candidates[0];used.add(item['id']);scene_dir=directory/item['id'];scene_dir.mkdir();savejson(scene_dir/'item.json',item)
            print(json.dumps(dict(stage='scene',block=b['id'],id=item['id'],requested_date=date,actual_date=item['properties']['datetime'])),flush=True)
            def acquire(band):
                asset=item['assets'][band]
                result=read_window(asset['href'],bbox,scene_dir/f'{band}.tif',band)
                result.update(raster_bands=asset.get('raster:bands'),native_gsd=asset.get('gsd'),source_file_checksum=asset.get('file:checksum'))
                return result
            with ThreadPoolExecutor(max_workers=3) as executor:band_records=list(executor.map(acquire,BANDS))
            scene=dict(id=item['id'],requested_date=date,datetime=item['properties']['datetime'],tile_cloud_cover=item['properties'].get('eo:cloud_cover'),item_path=relative(scene_dir/'item.json'),item_sha256=sha(scene_dir/'item.json'),properties=item['properties'],bands=band_records)
            br['scenes'].append(scene)
            savejson(directory/'partial.json',br)
            print(json.dumps(dict(stage='scene_done',block=b['id'],id=item['id'],bands=len(band_records))),flush=True)
        # Every touched integer-degree DEM tile is recorded; overlapping edges
        # are mosaicked later on the analysis grid, without pretending 10m data.
        w,s,e,n=bbox
        for lat in range(math.floor(s),math.floor(n)+1):
            for lon in range(math.floor(w),math.floor(e)+1):
                name=f'Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM'
                url=f'https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/{name}/{name}.tif'
                clipped=[max(w,lon),max(s,lat),min(e,lon+1),min(n,lat+1)]
                if clipped[2]<=clipped[0] or clipped[3]<=clipped[1]:continue
                print(json.dumps(dict(stage='dem',block=b['id'],tile=name)),flush=True)
                record=read_window(url,clipped,directory/(name+'.tif'),'dem')
                record.update(tile_id=name,collection='cop-dem-glo-30',vertical_datum='EGM2008',surface='DSM: includes surface objects',requested_clip_lonlat=clipped)
                br['dem_tiles'].append(record)
        savejson(directory/'manifest.json',br);records.append(br)
    manifest=dict(acquired_utc=datetime.now(timezone.utc).isoformat(),config_path=relative(a.blocks),config_sha256=sha(a.blocks),code_path=relative(Path(__file__)),code_sha256=sha(Path(__file__)),blocks=records,failures=failures,rights='Raw sources local-only pending recorded dataset licenses; no signed URLs or credentials used',selection='Dates chosen before candidate inspection; single-tile complete coverage and <=10% catalogue cloud filter, per-pixel QA performed during analysis')
    savejson(a.output/'manifest.json',manifest)
    print(json.dumps(dict(stage='complete',blocks=len(records),scenes=sum(len(x['scenes']) for x in records),failures=failures)),flush=True)

if __name__=='__main__':main()
