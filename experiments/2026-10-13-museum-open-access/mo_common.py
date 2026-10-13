"""Shared helpers for the museum open-access harvest (13 October 2026).

Cached, rate-limited GET requests with a request log. Every response body is
written once under data/raw/2026-10-13-museum-open-access/<museum>/cache/ and
never fetched again; requests.jsonl records URL, UTC time, status, bytes and
SHA256. Run scripts from the repository root.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "2026-10-13-museum-open-access"
PKG = Path(__file__).resolve().parent
UA = "indus-valley-script-research/1.0 (+https://github.com/k-sandhu/indus-valley-script)"

_last_request = {"t": 0.0}
_session = requests.Session()
_session.headers.update({"User-Agent": UA, "Accept": "application/json, text/html;q=0.9, */*;q=0.5"})


def _key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]


def cache_dir(museum: str) -> Path:
    d = RAW / museum / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch(museum: str, url: str, delay: float = 1.1, timeout: float = 60.0, binary: bool = False,
          headers: dict | None = None) -> dict:
    """Return {'status', 'path', 'sha256', 'bytes', 'cached', 'url'}; body is on disk."""
    cdir = cache_dir(museum)
    k = _key(url)
    meta_path = cdir / f"{k}.meta.json"
    body_path = cdir / f"{k}.body"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["cached"] = True
        return meta
    wait = delay - (time.time() - _last_request["t"])
    if wait > 0:
        time.sleep(wait)
    t0 = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        r = _session.get(url, timeout=timeout, headers=headers or {})
        status = r.status_code
        content = r.content
        ctype = r.headers.get("Content-Type", "")
    except requests.RequestException as exc:  # recorded, not raised
        status = -1
        content = repr(exc).encode("utf-8")
        ctype = "error"
    _last_request["t"] = time.time()
    body_path.write_bytes(content)
    meta = {
        "url": url,
        "retrieved_utc": t0,
        "status": status,
        "content_type": ctype,
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "path": str(body_path.relative_to(ROOT)).replace("\\", "/"),
    }
    # only cache successful or definitive responses; retryable failures are logged but not cached
    if status in (200, 404, 410, 400):
        meta_path.write_text(json.dumps(meta, indent=1), encoding="utf-8")
    with open(RAW / museum / "requests.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(meta) + "\n")
    meta["cached"] = False
    return meta


def fetch_json(museum: str, url: str, **kw):
    meta = fetch(museum, url, **kw)
    if meta["status"] != 200:
        return meta, None
    try:
        return meta, json.loads((ROOT / meta["path"]).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return meta, None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_key(s: str) -> str:
    """Casefold and keep letters and digits only (the census normalization)."""
    return re.sub(r"[^0-9a-z]", "", (s or "").casefold())


INDUS_SITE_WORDS = [
    "indus", "harappa", "harappan", "mohenjo", "mohenjodaro", "mohenjo-daro", "mohenjo daro",
    "chanhu", "lothal", "kalibangan", "dholavira", "banawali", "rakhigarhi", "nausharo",
    "kot diji", "mehrgarh", "amri", "sutkagen", "allahdino", "surkotada", "rangpur",
]

SEAL_WORDS = ["seal", "sealing", "tablet", "impression", "amulet", "stamp", "sherd", "potsherd", "tag"]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
