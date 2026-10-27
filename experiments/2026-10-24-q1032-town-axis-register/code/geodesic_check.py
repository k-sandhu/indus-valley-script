"""Independent WGS84 inverse-geodesic calculation for the archived image picks."""
import argparse
import json
import math
from pathlib import Path
from pyproj import Geod, __version__

P=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    x=json.loads((P/'new-observations.json').read_text(encoding='utf-8'));s=x['sources'][0]
    n=256*2**s['zoom'];g=Geod(ellps='WGS84')
    def lonlat(q):
        gx=q[0]+s['origin_global_px'][0];gy=q[1]+s['origin_global_px'][1]
        return gx/n*360-180,math.degrees(math.atan(math.sinh(math.pi*(1-2*gy/n))))
    rows=[]
    for r in x['structures']:
        a1,b1=map(lonlat,r['endpoints_px'])
        rows.append(dict(id=r['id'],endpoints_lonlat=[a1,b1],geodesic=g.inv(*a1,*b1)))
    with Path(a.out).open('x',encoding='utf-8') as f:
        json.dump(dict(method=f'pyproj {__version__} Geod WGS84 inverse; independent of pixel-angle calculation',rows=rows),f,indent=2)

if __name__=='__main__':main()
