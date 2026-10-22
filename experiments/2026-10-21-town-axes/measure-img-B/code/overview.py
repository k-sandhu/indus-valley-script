"""Download an overview mosaic around a point and print its record (role img-B).

Usage: python overview.py <name> <lon> <lat> <zoom> <half_width_m>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tiles  # noqa: E402

if __name__ == "__main__":
    name, lon, lat, z, h = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    r = tiles.mosaic_around(name, lon, lat, z, h)
    from PIL import Image
    im = Image.open(tiles.ROOT / r["path"])
    r["size"] = im.size
    r["m_per_px"] = tiles.m_per_px(lat, z)
    print(json.dumps(r))
    s = tiles.imagery_summary(lon, lat)
    print(json.dumps(s["layers"][0] if s["layers"] else {}))
