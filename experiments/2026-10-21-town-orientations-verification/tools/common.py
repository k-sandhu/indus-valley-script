"""Shared coordinates, provenance and immutable JSON output for measurement tools."""
from __future__ import annotations
import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from pyproj import Geod, Transformer

GEOD = Geod(ellps="WGS84")

def utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def record(path, url, rights_status="own-work", rights_notice="Project output; CC0 1.0", **extra):
    p = Path(path)
    result = dict(path=p.as_posix(), url=url, retrieved_utc=utc(), bytes=p.stat().st_size,
                sha256=sha256(p), format=p.suffix.lstrip("."), rights_status=rights_status,
                rights_notice=rights_notice)
    result.update(extra)
    return result

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def write_json(path, data):
    """Create once. A completed result is never silently replaced."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    def native(value):
        if isinstance(value,np.generic):return value.item()
        if isinstance(value,np.ndarray):return value.tolist()
        raise TypeError(type(value).__name__)
    payload=json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False,default=native)+'\n'
    check_space(p, len(payload.encode('utf-8')))
    with p.open("x", encoding="utf-8", newline="\n") as f:f.write(payload)

def check_space(path, expected_bytes):
    """Check a conservative output bound; retain at least 250 MB on this drive."""
    parent=Path(path).resolve().parent
    while not parent.exists():parent=parent.parent
    if expected_bytes > 1_000_000 and shutil.disk_usage(parent).free-expected_bytes < 250_000_000:
        raise OSError('Write would breach the 250 MB free-space reserve')

def fold(bearing):
    theta = (bearing + 45.0) % 90.0 - 45.0
    return 45.0 if math.isclose(theta, -45.0, abs_tol=1e-12) else theta

def delta(a, b, period=180.):
    return (a - b + period / 2) % period - period / 2

def affine_points(matrix, points):
    a = np.asarray(matrix, float).reshape(3, 3)
    p = np.asarray(points, float)
    return (np.c_[p, np.ones(len(p))] @ a.T)[:, :2]

def geodesic_bearing(xy, epsg):
    t = Transformer.from_crs(epsg, 4326, always_xy=True)
    lon, lat = t.transform(*np.asarray(xy).T)
    fwd, back, length = GEOD.inv(lon[0], lat[0], lon[1], lat[1])
    reverse_forward = back - 180.
    # Circular mean is essential at the 0/360 boundary.
    az = math.degrees(math.atan2(math.sin(math.radians(fwd)) + math.sin(math.radians(reverse_forward)),
                                 math.cos(math.radians(fwd)) + math.cos(math.radians(reverse_forward)))) % 360
    return az, length, list(map(list, zip(lon, lat)))

def pixel_bearing(points):
    dx, dy = np.diff(np.asarray(points, float), axis=0)[0]
    return math.degrees(math.atan2(dx, -dy)) % 360

def code_hashes():
    return {p.name: sha256(p) for p in sorted(Path(__file__).parent.glob("*.py"))}
