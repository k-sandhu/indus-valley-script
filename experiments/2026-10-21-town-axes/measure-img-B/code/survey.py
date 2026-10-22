"""Download a zoom-18 mosaic around a point and write a gridded JPEG preview (role img-B).

Usage: python survey.py <name> <lon> <lat> <half_width_m> [scale]
Prints the mosaic record; the preview grid is labelled in mosaic pixels.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tiles  # noqa: E402
from view import crop_grid  # noqa: E402

if __name__ == "__main__":
    name, lon, lat, h = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    sc = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6
    r = tiles.mosaic_around(name, lon, lat, 18, h)
    from PIL import Image
    W, H = Image.open(tiles.ROOT / r["path"]).size
    out = tiles.RAW / "views" / f"{name}_preview.jpg"
    crop_grid(str(tiles.ROOT / r["path"]), 0, 0, W, H, str(out), 100, sc)
    x, y = tiles.lonlat_to_px(lon, lat, 18)
    r["point_in_mosaic_px"] = [round(x - r["origin_px"][0]), round(y - r["origin_px"][1])]
    r["size"] = [W, H]
    print(json.dumps(r))
    s = tiles.imagery_summary(lon, lat)
    print(json.dumps(s["layers"][0] if s["layers"] else {}))
