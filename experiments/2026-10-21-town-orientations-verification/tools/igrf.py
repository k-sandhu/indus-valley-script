"""Evaluate IGRF-14, 1900–2030, from the official NOAA coefficient text file.

East-positive declination is added to a bearing measured from magnetic north.
The field is evaluated at WGS84 geodetic coordinates and ellipsoid altitude.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,math,tempfile
from datetime import datetime,timedelta
import ppigrf
from common import sha256,write_json

def field(lat,lon,year,altitude_m=0,coefficients=None):
    if not 1900<=year<=2030:raise ValueError('IGRF-14 year must be in [1900,2030]')
    if not -90<=lat<=90 or not -180<=lon<=180:raise ValueError('invalid geodetic location')
    if not coefficients:raise ValueError('official coefficient path is required')
    text=Path(coefficients).read_text(encoding='ascii')
    if '14th Generation' not in text[:200]:raise ValueError('not an IGRF-14 coefficient file')
    y=int(year);date=datetime(y,1,1)+timedelta(days=(year-y)*((datetime(y+1,1,1)-datetime(y,1,1)).days))
    # NOAA uses g/h rows, while ppigrf accepts SHC. Interpolate in decimal
    # years first, then synthesize a constant SHC to avoid leap-day weighting.
    rows=[]
    for line in text.splitlines():
        parts=line.split()
        if not parts or parts[0] not in ['g','h']:continue
        n,m=int(parts[1]),int(parts[2]);values=list(map(float,parts[3:]))
        if year>=2025:value=values[-2]+(year-2025)*values[-1]
        else:
            idx=int((year-1900)//5);fraction=(year-(1900+5*idx))/5
            value=values[idx]*(1-fraction)+values[idx+1]*fraction
        rows.append(f"{n} {m if parts[0]=='g' else -m} {value:.12g} {value:.12g}")
    with tempfile.TemporaryDirectory(prefix='.igrf14-eval-',dir=Path(coefficients).resolve().parent) as tmp:
        shc=Path(tmp)/'converted.shc';shc.write_text('1 13 2 1 1\n1900.0 2030.0\n'+'\n'.join(rows)+'\n',encoding='ascii')
        be,bn,bu=ppigrf.igrf(lon,lat,altitude_m/1000,date,coeff_fn=str(shc))
    east,north,up=float(be.ravel()[0]),float(bn.ravel()[0]),float(bu.ravel()[0])
    return dict(latitude=lat,longitude=lon,decimal_year=year,altitude_m=altitude_m,declination_deg=math.degrees(math.atan2(east,north)),north_nT=north,east_nT=east,down_nT=-up,coefficients_sha256=sha256(coefficients),model='IGRF-14',declination_sign='positive east')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('latitude',type=float);p.add_argument('longitude',type=float);p.add_argument('year',type=float);p.add_argument('--coefficients',required=True);p.add_argument('--altitude-m',type=float,default=0);p.add_argument('--output');a=p.parse_args();r=field(a.latitude,a.longitude,a.year,a.altitude_m,a.coefficients)
    if a.output:write_json(a.output,r)
    else:print(__import__('json').dumps(r,indent=2))
if __name__=='__main__':main()
