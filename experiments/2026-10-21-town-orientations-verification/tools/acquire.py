"""Acquire anonymous open imagery and record exact query and asset provenance.

Run with python -I. No code or modules are loaded from downloaded directories.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,collections,concurrent.futures,json,math,time,shutil
from datetime import datetime,timezone
import requests
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import reproject,Resampling
from rasterio.windows import from_bounds,Window
from pyproj import Transformer
from common import utc,write_json,read_json,record,check_space
from http_ranges import RangeReader

STAC="https://earth-search.aws.element84.com/v1"
RIGHTS="Copernicus Sentinel data terms; Contains modified Copernicus Sentinel data 2018–2026"
BANDS=["blue","green","red","nir","swir16","swir22"]
DESCS=["B02","B03","B04","B08","B11","B12"]

def download(url,path,status="rights-unverified",notice="No explicit licence observed",**kw):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise FileExistsError(p)
    r=requests.get(url,timeout=90);r.raise_for_status()
    if 'plans' in p.parts and len(r.content)>30_000_000:raise ValueError('Additional plan source exceeds 30 MB')
    check_space(p,len(r.content))
    with p.open("xb") as f:f.write(r.content)
    return record(p,url,status,notice,**kw)

def query(point, directory):
    """Save all STAC search pages before choosing dates; reject warm-season items."""
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    payload=dict(collections=["sentinel-2-l2a"],intersects=dict(type="Point",coordinates=[point[1],point[0]]),datetime="2018-01-01T00:00:00Z/2026-12-31T23:59:59Z",query={"eo:cloud_cover":{"lte":3}},limit=100)
    pages=[];items=[];url=STAC+"/search";method="GET";body=payload
    while url:
        if shutil.disk_usage(directory).free<1_200_000_000:raise OSError('Imagery metadata download stopped below 1.2 GB free')
        params=None
        if not pages:
            params=dict(collections='sentinel-2-l2a',bbox=','.join(map(str,[point[1]-1e-6,point[0]-1e-6,point[1]+1e-6,point[0]+1e-6])),datetime=payload['datetime'],query=json.dumps(payload['query']),limit=100)
        for attempt in range(4):
            r=requests.request(method,url,params=params,json=body if method=="POST" else None,headers={'User-Agent':'IndusResearchInfrastructure/1.0'},timeout=90)
            if r.status_code not in [429,500,502,503,504]:break
            time.sleep(2**attempt)
        r.raise_for_status();data=r.json()
        p=directory/f"stac-search-{len(pages)+1:03d}.json";check_space(p,len(r.content));p.write_bytes(r.content)
        pages.append(record(p,r.url,"explicit-license","STAC metadata; Copernicus Sentinel data terms",request_body=body))
        items.extend(f for f in data.get("features",[]) if int(f["properties"]["datetime"][5:7]) in [10,11,12,1,2,3,4])
        link=next((l for l in data.get("links",[]) if l["rel"]=="next"),None)
        url=link["href"] if link else None;method=link.get("method","GET") if link else "GET";body=link.get("body") if link else None
    return items,pages

def item_epsg(item):
    p=item["properties"]
    return p.get("proj:epsg") or int(p.get("proj:code","EPSG:32643").split(":")[-1])

def tile(item):
    p=item["properties"]
    return p.get("s2:mgrs_tile") or p.get("mgrs:utm_zone","").__str__()+p.get("mgrs:latitude_band","")+p.get("mgrs:grid_square","") or item["id"].split("_")[1]

def target(point,epsg,size=5000,res=10):
    x,y=Transformer.from_crs(4326,epsg,always_xy=True).transform(point[1],point[0])
    left=math.floor((x-size/2)/res)*res;top=math.ceil((y+size/2)/res)*res
    n=int(size/res)
    return from_origin(left,top,res,res),(left,top-size,left+size,top),(n,n)

def read_asset(asset,epsg,transform,shape,nearest=False):
    url=asset["href"]
    if not url.startswith("https://"):raise ValueError("Only anonymous HTTPS COG assets allowed")
    # GDAL uses Range GET against the COG. Disable directory enumeration and AWS credentials.
    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".tif",GDAL_HTTP_MAX_RETRY=2,GDAL_HTTP_RETRY_DELAY=1,GDAL_HTTP_TIMEOUT=60,AWS_NO_SIGN_REQUEST="YES"):
        with rasterio.open(url,opener=RangeReader,sharing=False) as ds:
            bounds=rasterio.transform.array_bounds(*shape,transform)
            if ds.crs.to_epsg()!=epsg:raise ValueError("asset projection differs from selected tile")
            if not (ds.bounds.left<=bounds[0] and ds.bounds.bottom<=bounds[1] and ds.bounds.right>=bounds[2] and ds.bounds.top>=bounds[3]):
                raise ValueError("tile does not contain complete window")
            w=from_bounds(*bounds,ds.transform)
            # All assets share the selected UTM CRS. Fractional native windows
            # give the exact target extent and preserve the 20 m sampling phase.
            out=ds.read(1,window=w,out_shape=shape,resampling=Resampling.nearest if nearest else Resampling.bilinear,out_dtype='float32')
            if not np.isfinite(out).all():raise ValueError('non-finite COG samples')
            return out

def save_tif(path,a,epsg,transform,descs):
    if Path(path).exists():raise FileExistsError(path)
    if shutil.disk_usage(Path(path).parent).free-a.nbytes-1_000_000<250_000_000:raise OSError('Write would breach 250 MB reserve')
    with rasterio.open(path,"w",driver="GTiff",height=a.shape[1],width=a.shape[2],count=len(a),dtype="float32",crs=f"EPSG:{epsg}",transform=transform,nodata=0,compress="deflate",predictor=2,tiled=True,blockxsize=256,blockysize=256) as ds:
        ds.write(a.astype("float32"));ds.descriptions=tuple(descs)
        ds.update_tags(attribution=RIGHTS,resampled_bands="B11 and B12: native 20 m, bilinear to 10 m",values="surface reflectance, STAC scale and offset applied")
    with rasterio.open(path) as ds:
        if ds.count!=len(a) or not np.array_equal(ds.read(),a.astype('float32')):raise IOError('GeoTIFF verification after write failed')

def date_order(items):
    # Round-robin years and months; selection never inspects archaeological features.
    groups=collections.defaultdict(list)
    for it in items:groups[int(it["properties"]["datetime"][:4])].append(it)
    for y in groups:groups[y].sort(key=lambda it:(it["properties"].get("eo:cloud_cover",99),it["properties"]["datetime"]))
    used_months=collections.Counter();ordered=[]
    while any(groups.values()):
        for y in sorted(groups):
            if groups[y]:
                it=min(groups[y],key=lambda it:(used_months[it["properties"]["datetime"][5:7]],it["properties"].get("eo:cloud_cover",99)))
                groups[y].remove(it);ordered.append(it);used_months[it["properties"]["datetime"][5:7]]+=1
    return ordered

def imagery(site,raw,max_scenes=9,seed=None,cached_items=None):
    if shutil.disk_usage(raw).free<1_500_000_000:raise OSError('Imagery download requires 1.5 GB free')
    slug=site["slug"];point=site["coordinate_used"]
    parent=Path(raw)/"imagery"/slug
    # Failed acquisition attempts remain available under their original names.
    n=2
    while (parent/f'acquisition-v{n}').exists():n+=1
    dest=parent/f'acquisition-v{n}';dest.mkdir(parents=True,exist_ok=False)
    result=dict(slug=slug,point=point,scenes=[],rejected=[],files=[],composite=None,landsat={"obtained":False},mosaic=False)
    if point is None:result["failure"]="No located coordinate";return result
    try:
        if cached_items:
            items=cached_items;pages=[];result['metadata_source']='Held STAC responses; no new metadata request'
        else:items,pages=query(point,dest/"metadata")
        result["files"].extend(pages);result["candidate_count"]=len(items)
        groups=collections.defaultdict(list)
        for it in items:groups[(tile(it),item_epsg(it))].append(it)
        selected=None
        for key,g in sorted(groups.items(),key=lambda kv:-len(kv[1])):
            if seed and key[0]!=seed['tile']:continue
            epsg=key[1];tr,bounds,shape=target(point,epsg)
            try:
                if not seed:read_asset(g[0]["assets"]["scl"],epsg,tr,shape,True)
                selected=(key,g,tr,bounds,shape);break
            except Exception as e:result["rejected"].append(dict(tile=key[0],reason=str(e)))
        if selected is None:raise ValueError("No single tile window available; mosaic required but unavailable")
        (tile_id,epsg),items,tr,bounds,shape=selected
        result.update(tile=tile_id,epsg=epsg,window_bounds=list(bounds),window_metres=[5000,5000],resolution_m=10)
        arrays=[]
        seen=set()
        if seed:
            for scene in seed['scenes']:
                if not scene.get('used_in_composite',True):continue
                with rasterio.open(scene['file']['path']) as ds:
                    if ds.transform!=tr or ds.crs.to_epsg()!=epsg:raise ValueError('Seed grid differs')
                    arrays.append(ds.read())
                result['scenes'].append(scene);seen.add(scene['datetime'][:10])
        for it in date_order(items):
            if shutil.disk_usage(raw).free<1_200_000_000:raise OSError('Imagery download stopped below 1.2 GB free')
            if len(arrays)>=max_scenes:break
            day=it["properties"]["datetime"][:10]
            if day in seen:continue
            seen.add(day)
            try:
                scl=read_asset(it["assets"]["scl"],epsg,tr,shape,True)
                # SCL 0 missing; 1 defective; 3 shadow; 8/9 clouds; 10 cirrus; 11 snow.
                invalid=np.isin(scl,[0,1,3,8,9,10,11])
                if invalid.any():raise ValueError(f"SCL rejects {invalid.sum()} of {invalid.size} pixels")
                bands=[];assets=[]
                for key in BANDS:
                    asset=it["assets"][key];a=read_asset(asset,epsg,tr,shape)
                    if (a==0).any():raise ValueError(f"no-data in {key}")
                    meta=asset.get("raster:bands",[{}])[0];scale=meta.get("scale",.0001);offset=meta.get("offset",0)
                    bands.append(a*scale+offset);assets.append(dict(band=key,url=asset["href"],native_resolution_m=20 if key in ["swir16","swir22"] else 10,resampling="bilinear" if key in ["swir16","swir22"] else "aligned native grid",scale=scale,offset=offset))
                a=np.stack(bands);p=dest/(it["id"]+"-window.tif");save_tif(p,a,epsg,tr,DESCS)
                file=record(p,next(l["href"] for l in it["links"] if l["rel"]=="self"),"explicit-license",RIGHTS,transformation="HTTP range read; crop; reflectance scaling; B11/B12 bilinear 20 to 10 m",assets=assets)
                mask=dest/(it["id"]+"-scl.tif");save_tif(mask,scl[None],epsg,tr,["SCL"])
                maskrec=record(mask,it["assets"]["scl"]["href"],"explicit-license",RIGHTS,transformation="SCL nearest-neighbour 20 to 10 m")
                scene=dict(item_id=it["id"],self_link=file["url"],datetime=it["properties"]["datetime"],cloud_cover=it["properties"].get("eo:cloud_cover"),tile=tile_id,epsg=epsg,file=file,scl=maskrec)
                result["scenes"].append(scene);arrays.append(a)
                print(slug,len(arrays),day,flush=True)
            except Exception as e:result["rejected"].append(dict(item_id=it["id"],reason=str(e)))
        if not arrays:raise ValueError("No scene passed window mask")
        median=np.median(np.stack(arrays),axis=0);median=np.concatenate([median,median[:4].mean(axis=0)[None]])
        p=dest/"median-composite.tif";save_tif(p,median,epsg,tr,DESCS+["brightness"])
        result["composite"]=record(p,STAC,"explicit-license",RIGHTS,transformation="Per-pixel median of six reflectance bands; brightness is mean B02 B03 B04 B08",parents=[s["file"]["sha256"] for s in result["scenes"]])
    except Exception as e:result["failure"]=str(e)
    write_json(dest/"acquisition-result.json",result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("sites");p.add_argument("raw");p.add_argument("output");p.add_argument("--max-scenes",type=int,default=9);p.add_argument("--workers",type=int,default=4);a=p.parse_args()
    sites=read_json(a.sites)["sites"]
    def run(site):
        old=sorted((Path(a.raw)/"imagery"/site["slug"]).glob('acquisition-v*/acquisition-result.json'))
        good=[read_json(p) for p in old if read_json(p).get('composite')]
        try:return good[-1] if good else imagery(site,a.raw,a.max_scenes)
        except Exception as e:return dict(slug=site['slug'],point=site['coordinate_used'],scenes=[],files=[],composite=None,landsat={'obtained':False},failure=str(e))
    with concurrent.futures.ThreadPoolExecutor(a.workers) as pool:results=list(pool.map(run,sites))
    write_json(a.output,dict(schema_version=1,task="town-orientation-infrastructure",created_utc=utc(),selection="Up to nine clear windows, round-robin years and months, one MGRS tile",towns=results))
if __name__=="__main__":main()
