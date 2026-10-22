"""Convert between render pixels, UTM and WGS84 using an imagery render sidecar.

Usage:
  coords.py <render.png.json> px2geo x y [x y ...]
  coords.py <render.png.json> geo2px lat lon [lat lon ...]
  coords.py <render.png.json> utm2px e n [e n ...]
"""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
import numpy as np
from pyproj import Transformer


def main():
    side = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    m = np.asarray(side["pixel_to_utm"], float)
    inv = np.linalg.inv(m)
    mode = sys.argv[2]
    vals = list(map(float, sys.argv[3:]))
    pairs = list(zip(vals[::2], vals[1::2]))
    to_geo = Transformer.from_crs(side["epsg"], 4326, always_xy=True)
    to_utm = Transformer.from_crs(4326, side["epsg"], always_xy=True)
    for a, b in pairs:
        if mode == "px2geo":
            e, n, _ = m @ np.array([a, b, 1.0])
            lon, lat = to_geo.transform(e, n)
            print(f"px ({a:.1f},{b:.1f}) -> UTM ({e:.1f},{n:.1f}) -> lat {lat:.6f} lon {lon:.6f}")
        elif mode == "geo2px":
            e, n = to_utm.transform(b, a)
            x, y, _ = inv @ np.array([e, n, 1.0])
            print(f"lat {a:.6f} lon {b:.6f} -> UTM ({e:.1f},{n:.1f}) -> px ({x:.1f},{y:.1f})")
        elif mode == "utm2px":
            x, y, _ = inv @ np.array([a, b, 1.0])
            print(f"UTM ({a:.1f},{b:.1f}) -> px ({x:.1f},{y:.1f})")


if __name__ == "__main__":
    main()
