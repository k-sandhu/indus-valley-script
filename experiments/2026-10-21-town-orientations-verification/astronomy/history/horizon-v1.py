"""Copernicus DEM ray tracing with WGS84 geodesics and bilinear cell sampling."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from records import *
import numpy as np
import rasterio
from pyproj import Geod
from scipy.ndimage import map_coordinates
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
GEOD=Geod(ellps='WGS84')
RE=6371000/(1-.13)
ATTRIBUTION='? DLR e.V. 2010?2014 and ? Airbus Defence and Space GmbH 2014?2018 provided under COPERNICUS by the European Union and ESA'
TOWNS={'mohenjo-daro':(27.324,68.136),'harappa':(30.631,72.864),
'kalibangan':(29.473,74.130),'lothal':(22.522,72.249),'dholavira':(23.887,70.213),
'surkotada':(23.617,70.841),'banawali':(29.598,75.393),'rakhigarhi':(29.290,76.110),
'chanhu-daro':(26.174,68.323),'kanmer':(23.400,70.865),'shikarpur':(23.230,70.670)}
AZ=np.r_[np.arange(450,1351),np.arange(2250,3151)]/10

def tilename(res,lat,lon):
    return f"Copernicus_DSM_COG_{10 if res==30 else 30}_{'N' if lat>=0 else 'S'}{abs(lat):02d}_00_{'E' if lon>=0 else 'W'}{abs(lon):03d}_00_DEM"

@lru_cache()
def inventory(res):
    p=download(f'https://copernicus-dem-{res}m.s3.amazonaws.com/tileList.txt',RAW/f'tileList-{res}.txt','Copernicus DEM licence; AWS tile inventory; local-only raw reference.')
    return set(p.read_text().splitlines())

def tile(res,lat,lon):
    name=tilename(res,lat,lon)
    if name not in inventory(res): return None
    url=f'https://copernicus-dem-{res}m.s3.amazonaws.com/{name}/{name}.tif'
    return download(url,RAW/'dem'/f'{res}m'/f'{name}.tif','Copernicus DEM licence. '+ATTRIBUTION)

@lru_cache(maxsize=48)
def raster(path):
    with rasterio.open(path) as src:
        a=src.read(1)
        if np.any(a==src.nodata): raise ValueError('DEM contains nodata: '+path)
        return a,~src.transform

def sample(res,lats,lons,used):
    lats,lons=np.asarray(lats),np.asarray(lons)
    keys=np.column_stack([np.floor(lats).astype(int).ravel(),np.floor(lons).astype(int).ravel()])
    unique,inverse=np.unique(keys,axis=0,return_inverse=True)
    def fetch(key): return tile(res,int(key[0]),int(key[1]))
    with ThreadPoolExecutor(max_workers=6) as pool: paths=list(pool.map(fetch,unique))
    result=np.zeros(lats.size)
    for i,path in enumerate(paths):
        mask=inverse==i
        name=tilename(res,*unique[i]); used[f'{res}m/{name}']=sha(path) if path else 'absent-in-tileList:sea-level'
        if path is None: continue
        arr,transform=raster(str(path))
        cols,rows=transform*(lons.ravel()[mask],lats.ravel()[mask])
        result[mask]=map_coordinates(arr,[rows-.5,cols-.5],order=1,mode='nearest',prefilter=False)
    return result.reshape(lats.shape)

def build(lat,lon,out):
    out=Path(out)
    if out.exists(): raise FileExistsError(out)
    used={}
    ground=float(sample(30,np.array([lat]),np.array([lon]),used)[0])
    H=ground+1.6
    # Sea-level dip uses total observer height above sea level, not 1.6m alone.
    # A sub-sea-level observer has no real sea-level dip; this domain is rejected.
    if H<0: raise ValueError('observer below sea level: dip is undefined by protocol')
    dip=-np.arccos(RE/(RE+H))*180/np.pi
    maximum=np.full(len(AZ),dip)
    maxima_distance=np.zeros(len(AZ))
    for res,dist in [(30,np.arange(2000,20001,30)),(90,np.r_[np.arange(20000,250000,90),250000])]:
        for start in range(0,len(AZ),120):
            az=AZ[start:start+120]
            aa,dd=np.meshgrid(az,dist,indexing='ij')
            lons,lats,_=GEOD.fwd(np.full(aa.shape,lon),np.full(aa.shape,lat),aa,dd)
            z=sample(res,lats,lons,used)
            elev=np.arctan((z-H)/dd-dd/(2*RE))*180/np.pi
            ix=np.argmax(elev,axis=1); peak=elev[np.arange(len(az)),ix]
            sl=slice(start,start+len(az)); wins=peak>maximum[sl]
            maximum[sl]=np.maximum(maximum[sl],peak)
            maxima_distance[sl]=np.where(wins,dist[ix],maxima_distance[sl])
    inputs=[RAW/f'tileList-{r}.txt' for r in (30,90)]
    inputs += [RAW/'dem'/k.split('/')[0]/(k.split('/')[1]+'.tif') for k,v in used.items() if len(v)==64]
    return write_json(out,'town-horizon',dict(lat=lat,lon=lon,
        dem_surface_m=ground,observer_height_asl_m=H,eye_height_above_surface_m=1.6,
        effective_earth_radius_m=RE,sea_level_dip_deg=dip,azimuth_deg=AZ,
        apparent_altitude_deg=maximum,maximum_distance_m=maxima_distance,
        dem_tiles=used,attribution=ATTRIBUTION,interpolation='bilinear; nearest at tile cell boundary',
        sea_interpretation='Only names absent from AWS tileList are sea level; HTTP failures and nodata raise errors.',
        sampling='GLO-30: 2000..20000m every30m; GLO-90: 20000..249950m every90m plus250000m.'),
        inputs=inputs,codes=[__file__,Path(__file__).with_name('records.py')])

def profile(lat,lon,path=None):
    if path is None:
        for slug,coords in TOWNS.items():
            if (lat,lon)==coords:
                path=OUT/'horizon'/f'{slug}.json'; break
        else:
            path=OUT/'horizon'/f'coords-{lat:.8f}-{lon:.8f}.json'
    path=Path(path)
    data=json.loads(path.read_text()) if path.exists() else build(lat,lon,path)
    if abs(data['lat']-lat)>1e-10 or abs(data['lon']-lon)>1e-10: raise ValueError('horizon coordinate mismatch')
    return data

def horizon_at(data,az):
    if not (45<=az<=135 or 225<=az<=315):
        raise ValueError('azimuth outside protocol horizon coverage')
    return float(np.interp(az,data['azimuth_deg'],data['apparent_altitude_deg']))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--all',action='store_true')
    ap.add_argument('--lat',type=float); ap.add_argument('--lon',type=float); ap.add_argument('--output',type=Path)
    a=ap.parse_args()
    if a.all:
        for slug,(lat,lon) in TOWNS.items():
            p=OUT/'horizon'/f'{slug}.json'
            if p.exists(): raise FileExistsError(p)
            d=build(lat,lon,p)
            print(slug,d['dem_surface_m'],min(d['apparent_altitude_deg']),max(d['apparent_altitude_deg']),flush=True)
    else: build(a.lat,a.lon,a.output)
