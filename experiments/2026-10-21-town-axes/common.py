"""Shared helpers for the town-axes package: hashing, provenance and write-once outputs."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import platform
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    p = Path(path).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def provenance(inputs, code):
    """Hashes of inputs and code, the interpreter and the time of the run."""
    return {
        "utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "inputs": {rel(p): sha256_file(p) for p in inputs},
        "code": {rel(p): sha256_file(p) for p in code},
    }


def write_new(path, obj):
    """Write JSON to a path that must not exist yet; return its SHA-256."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def finite(x, nd=6):
    """Round a float for JSON, mapping non-finite values to None."""
    if x is None:
        return None
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return None
    if xf != xf or xf in (float("inf"), float("-inf")):
        return None
    return round(xf, nd)
