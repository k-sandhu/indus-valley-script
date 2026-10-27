"""Run the preserved horizon sampler at two corrected locations."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT/'experiments/2026-10-24-q1032-town-axis-register'
OLD = ROOT/'experiments/2026-10-21-town-axes'
sys.path.insert(0,str(OLD))
import horizon
import requests

RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-q1032-town-axis-register/dem')

def fetch(res,lat,lon,log):
    name=horizon.tile_name(res,lat,lon)
    url=f'{horizon.SOURCES[res][0]}/{name}/{name}.tif'
    p=RAW/f'GLO-{res}'/(name+'.tif'); p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        content=p.read_bytes(); status=200; retrieved='reused this run cache'
    else:
        r=requests.get(url,timeout=60); status=r.status_code
        if status!=404:r.raise_for_status()
        content=r.content if status==200 else None
        retrieved=datetime.now(timezone.utc).isoformat()
        if status==200:
            with p.open('xb') as f:f.write(content)
    row=dict(url=url,status=status,retrieved_utc=retrieved,physical_path=str(p),
             logical_path='data/raw/2026-10-24-q1032-town-axis-register/dem/'+str(p.relative_to(RAW)).replace('\\','/'),
             handling='local-only',rights_status='source-specific Copernicus DEM licence')
    if status==200:
        row.update(bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
    elif res==30:
        raise RuntimeError('Missing GLO-30 tile; do not treat incomplete land coverage as sea: '+url)
    log.append(row)
    print(f'tile GLO-{res} {lat} {lon}: {status}',flush=True)
    return content

def main():
    dest=PACKAGE/'horizon-repair-v1/horizons.json'
    if dest.exists():raise SystemExit('Output exists; preserve it.')
    horizon.fetch_tile=fetch
    log=[]; results=[]
    a,b=horizon.Dem(30,log),horizon.Dem(90,log)
    for town,lat,lon in [('surkotada',23.6113,70.9174),('farmana',29.040,76.306)]:
        h0,alt,dist,elev=horizon.profile(lat,lon,a,b)
        west=horizon.AZIMUTHS>=180
        results.append(dict(town=town,lat=lat,lon=lon,observer_elevation_m=float(h0),
            coordinate_basis='corrected location in plan-registration REPORT.md; Farmana is approximate',
            max_altitude_west_deg=float(alt[west].max()),max_altitude_east_deg=float(alt[~west].max()),
            altitude_at_270_deg=float(alt[horizon.AZIMUTHS==270][0]),altitude_at_90_deg=float(alt[horizon.AZIMUTHS==90][0]),
            profile=[dict(az=float(z),alt_deg=float(v),distance_km=float(d/1000),terrain_m=float(e)) for z,v,d,e in zip(horizon.AZIMUTHS,alt,dist,elev)]))
        print('completed '+town,flush=True)
    value=dict(schema_version='1.0',task='corrected-location-horizons',synthetic=False,
        created_utc=datetime.now(timezone.utc).isoformat(),towns=results,dem_tiles=log,
        model=dict(near='GLO-30, 2-20 km, 30 m samples',far='GLO-90, 20-250 km, 90 m samples',excluded_radius_km=2,
                   eye_m=1.6,terrestrial_refraction_k=.13,azimuth_step_deg=.1),
        attribution='produced using Copernicus WorldDEM-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved',
        licence_source='https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM',
        source_code={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OLD/'horizon.py',OLD/'common.py',Path(__file__)]},
        uncertainty='Unquantified modern DSM, observer coordinate and palaeohorizon errors; no numerical one-sigma claim.')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)

if __name__=='__main__':main()
