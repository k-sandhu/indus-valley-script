"""Contact sheet of the distinct Wayback versions of one tile (role img-B).

Usage: python wbsheet.py <lon> <lat> <out.png> [zoom]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tiles  # noqa: E402

if __name__ == "__main__":
    lon, lat, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    z = int(sys.argv[4]) if len(sys.argv) > 4 else 18
    res = [r for r in tiles.wb_scan(lon, lat, z) if r["sha256"]]
    n = len(res)
    cols = min(4, n)
    rows = (n + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 260, rows * 275), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for i, r in enumerate(res):
        zz, tx, ty = r["tile"]
        p = tiles.RAW / "wayback" / "tiles" / r["holding_release"] / str(zz) / str(ty) / f"{tx}.jpg"
        im = Image.open(p).convert("RGB")
        X, Y = (i % cols) * 260, (i // cols) * 275
        sheet.paste(im, (X, Y + 17))
        d.text((X + 2, Y + 2), f"{r['holding_release']} {r['holding_release_date']}", fill=(255, 255, 0))
    sheet.save(out)
    print(json.dumps([(r["holding_release"], r["holding_release_date"], r["n_releases"]) for r in res]))
