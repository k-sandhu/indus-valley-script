"""Convert between render PNG pixels and UTM or lat/lon using a render sidecar.

Usage:
  python -I coords.py <render.png.json> px  x y [x y ...]
  python -I coords.py <render.png.json> utm E N [E N ...]
  python -I coords.py <render.png.json> ll  lat lon [lat lon ...]
"""
import json
import sys
from pathlib import Path

import numpy as np
from pyproj import Transformer


def main():
    side = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    mode = sys.argv[2]
    vals = list(map(float, sys.argv[3:]))
    pts = np.asarray(vals).reshape(-1, 2)
    m = np.asarray(side["pixel_to_utm"])
    inv = np.linalg.inv(m)
    to_ll = Transformer.from_crs(side["epsg"], 4326, always_xy=True)
    from_ll = Transformer.from_crs(4326, side["epsg"], always_xy=True)
    for a, b in pts:
        if mode == "px":
            e, n, _ = m @ np.array([a, b, 1.0])
        elif mode == "utm":
            e, n = a, b
        elif mode == "ll":
            e, n = from_ll.transform(b, a)
        else:
            raise SystemExit("mode must be px, utm or ll")
        x, y, _ = inv @ np.array([e, n, 1.0])
        lon, lat = to_ll.transform(e, n)
        print(f"px=({x:.1f},{y:.1f}) utm=({e:.1f},{n:.1f}) lat={lat:.6f} lon={lon:.6f}")


if __name__ == "__main__":
    main()
