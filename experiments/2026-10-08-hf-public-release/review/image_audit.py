"""Reviewer check of the 949 staged PNGs: provenance prefixes, hashes against the recorded parents, modes, sizes, metadata chunks, colour content.
Run from the repository root:
  python -B experiments/2026-10-08-hf-public-release/review/image_audit.py
"""
import collections
import hashlib
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
REL = PKG / "release"
rows = pq.read_table(REL / "data/image_assets.parquet").to_pylist()
by_comp = collections.Counter((r["component"], r["role"]) for r in rows)
prefix = collections.Counter("/".join(r["source_path"].split("/")[:-1]) for r in rows)
modes = collections.Counter()
sizes = collections.defaultdict(list)
text_chunks = collections.Counter()
colour = 0
hash_ok = parent_exists = parent_hash_ok = 0
big = []
for r in rows:
    p = REL / r["image_path"]
    b = p.read_bytes()
    hash_ok += hashlib.sha256(b).hexdigest() == r["sha256"]
    sp = ROOT / r["source_path"]
    if sp.exists():
        parent_exists += 1
        parent_hash_ok += sp.read_bytes() == b
    with Image.open(p) as im:
        modes[im.mode] += 1
        sizes[r["component"]].append(im.size)
        for k in im.info:
            text_chunks[k] += 1
        if im.mode in ("RGB", "RGBA", "P"):
            a = np.asarray(im.convert("RGB")).astype(int)
            if (np.abs(a[..., 0] - a[..., 1]).max() > 24) or (np.abs(a[..., 1] - a[..., 2]).max() > 24):
                colour += 1
        if max(im.size) > 3000:
            big.append((r["image_path"], im.size))
out = dict(images=len(rows), sha256_matches_table=hash_ok, parent_files_present=parent_exists, staged_bytes_equal_parent=parent_hash_ok,
           by_component_role=[[list(k), v] for k, v in by_comp.items()], source_prefixes=dict(prefix), modes=dict(modes),
           png_info_keys=dict(text_chunks), images_with_colour_pixels=colour, larger_than_3000px=big[:10],
           size_range_by_component={k: [min(v), max(v)] for k, v in sizes.items()}, licences=sorted({r["license"] for r in rows}),
           source_urls=sorted({r["source_url"] for r in rows}))
(PKG / "review/image-audit.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
