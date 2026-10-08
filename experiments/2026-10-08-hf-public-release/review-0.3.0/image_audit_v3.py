"""Audit all 1,142 release PNGs (1,067 embedded in Parquet, 75 loose).

For each image_assets row: locate the bytes (embedded column of the owning table, or the loose file), check sha256 and byte count against the
table, decode with Pillow, record mode, size, metadata chunks and colour content, and find a parent file by SHA-256 among the
PNG files of package M's three benchmark folders, package N's reader charts and the original chart atlas. Embedded images are matched through
the path column of their table, so an image cannot be matched by position.

Run from the repository root with the indus-ml Python: python -B experiments/2026-10-08-hf-public-release/review-0.3.0/image_audit_v3.py
Writes review-0.3.0/image-audit.json.
"""
import collections
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
REL = PKG / "release"
M = ROOT / "experiments/2026-10-07-helsinki1979-digitization"
sha = lambda b: hashlib.sha256(b).hexdigest()

# parent index: sha256 -> first matching relative path (searching directories that hold the original PNGs)
parent_dirs = [ROOT / "output/chart_atlas/cells", M / "repair", M / "blind", M / "evaluation"]
index = {}
for d in parent_dirs:
    for p in d.rglob("*.png"):
        index.setdefault(sha(p.read_bytes()), p.relative_to(ROOT).as_posix())

# embedded bytes by logical path
emb = {}
spec = {"chart_reference": [("image", "image_path")], "benchmark_rows_v1": [("context_image", "context_image_path"), ("exact_image", "exact_image_path")],
        "benchmark_rows_v2": [("context_image", "context_image_path"), ("exact_image", "exact_image_path")],
        "benchmark_rows_v3": [("context_image", "context_image_path"), ("exact_image", "exact_image_path")]}
for table, pairs in spec.items():
    for r in pq.read_table(REL / f"data/{table}.parquet").to_pylist():
        for col, pcol in pairs:
            if r.get(col) and r[col].get("bytes") and r.get(pcol):
                emb.setdefault(r[pcol], []).append(r[col]["bytes"])

rows = pq.read_table(REL / "data/image_assets.parquet").to_pylist()
out = collections.Counter()
problems = []
by_comp = collections.Counter()
modes = collections.Counter()
info_keys = collections.Counter()
colour = 0
no_parent = []
sizes = collections.defaultdict(list)
for r in rows:
    path = r["image_path"]
    by_comp[(r["component"], r["role"], r["storage"])] += 1
    if r["storage"] == "embedded":
        cands = emb.get(path, [])
        if len(cands) != 1:
            problems.append((path, f"{len(cands)} embedded candidates"))
            continue
        b = cands[0]
    else:
        f = REL / path
        if not f.exists():
            problems.append((path, "loose file missing"))
            continue
        b = f.read_bytes()
    out["checked"] += 1
    if sha(b) == r["sha256"] and len(b) == r["bytes"]:
        out["hash_and_size_match_table"] += 1
    else:
        problems.append((path, "sha256/size differs from image_assets"))
    try:
        im = Image.open(io.BytesIO(b))
        im.load()
        out["decoded"] += 1
        modes[im.mode] += 1
        sizes[r["component"]].append(im.size)
        for k in im.info:
            info_keys[k] += 1
        a = np.asarray(im.convert("RGB")).astype(int)
        if (np.abs(a[..., 0] - a[..., 1]).max() > 24) or (np.abs(a[..., 1] - a[..., 2]).max() > 24):
            colour += 1
    except Exception as e:  # noqa: BLE001
        problems.append((path, repr(e)))
    if sha(b) in index:
        out["parent_found_by_sha256"] += 1
    else:
        no_parent.append(path)
# loose files on disk but not in image_assets, and vice versa
disk = {p.relative_to(REL).as_posix() for p in (REL / "images").rglob("*.png")}
listed_loose = {r["image_path"] for r in rows if r["storage"] == "loose_png"}
res = dict(image_assets_rows=len(rows), **out, by_component_role_storage=[[list(k), v] for k, v in by_comp.items()],
           loose_files_on_disk=len(disk), loose_on_disk_equals_loose_listed=disk == listed_loose,
           modes=dict(modes), png_info_keys=dict(info_keys), images_with_colour_pixels=colour,
           problems=problems[:20], no_parent_by_sha256=no_parent[:20], no_parent_count=len(no_parent),
           licences=sorted({r["license"] for r in rows}), source_urls=sorted({r["source_url"] for r in rows}),
           size_range_by_component={k: [min(v), max(v)] for k, v in sizes.items()},
           storage_total_bytes=sum(r["bytes"] for r in rows), parent_index_files=len(index))
Path(__file__).with_name("image-audit.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
