"""Convert UTM easting/northing to latitude/longitude (or back) for crop centring."""
import sys
from pyproj import Transformer
epsg=int(sys.argv[1]);mode=sys.argv[2];a=float(sys.argv[3]);b=float(sys.argv[4])
if mode=='toll':
    lon,lat=Transformer.from_crs(epsg,4326,always_xy=True).transform(a,b);print(f"{lat:.6f} {lon:.6f}")
else:
    e,n=Transformer.from_crs(4326,epsg,always_xy=True).transform(b,a);print(f"{e:.1f} {n:.1f}")
