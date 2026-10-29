"""Load every configuration from the private Hub repository with datasets.load_dataset and compare with the local
Parquet files: splits, row counts, feature schema, and every cell (image columns compared as decoded PNG bytes).

Usage (repository root, indus-ml Python; short cache path, no long lock names):
  python -B hub_load_check.py --cache C:/hfc030/ds --out hub-load-check.json
Read-only against the Hub.
"""
import argparse, hashlib, io, json, re
from pathlib import Path

import pyarrow.parquet as pq
import yaml
from datasets import get_dataset_config_names, load_dataset

ROOT = Path(__file__).resolve().parents[3]
REL = ROOT / "experiments/2026-10-08-hf-public-release/release"
REPO = "ksaw008/indus-reference-benchmarks"
ap = argparse.ArgumentParser()
ap.add_argument("--cache", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()

card = (REL / "README.md").read_text(encoding="utf-8")
meta = yaml.safe_load(re.match(r"---\n(.*?)\n---\n", card, re.S).group(1))
yaml_cfg = {c["config_name"]: c for c in meta["configs"]}
hub_names = get_dataset_config_names(REPO)
out = {"hub_config_names": hub_names, "n_hub": len(hub_names), "n_yaml": len(yaml_cfg),
       "names_equal_yaml": sorted(hub_names) == sorted(yaml_cfg), "configs": {}}
table_counts = {m.group(1): int(m.group(2)) for m in re.finditer(r"^\| `([a-z0-9_]+)` \| (\d+) \|", card, re.M)}

def norm(v):
    """Make a Parquet-decoded value comparable: PIL images -> PNG-decoded bytes hash; other values as plain Python."""
    if isinstance(v, dict) and "bytes" in v and "path" in v:
        return ("img", hashlib.sha256(v["bytes"]).hexdigest() if v["bytes"] else None)
    try:
        from PIL.Image import Image as PILImage
        if isinstance(v, PILImage):
            return ("pil", v.size, v.mode, hashlib.sha256(v.tobytes()).hexdigest())
    except Exception:
        pass
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    return v

total_rows = 0
for name, cfg in yaml_cfg.items():
    rec = {}
    path = REL / cfg["data_files"][0]["path"]
    split = cfg["data_files"][0]["split"]
    ds = load_dataset(REPO, name, cache_dir=a.cache)
    rec["splits"] = {s: len(ds[s]) for s in ds}
    rec["expected_split"] = split
    n = sum(rec["splits"].values())
    total_rows += n
    rec["card_rows"] = table_counts.get(name)
    rec["rows_match_card"] = n == table_counts.get(name)
    t = pq.read_table(path)
    rec["local_rows"] = t.num_rows
    rec["rows_equal_local"] = n == t.num_rows
    hub_cols = list(ds[split].column_names)
    rec["columns_equal"] = hub_cols == t.column_names
    # compare via arrow tables (raw storage) so image bytes are compared exactly
    hub_tbl = ds[split].data.table
    nz = lambda s: str(s).replace("list<item:", "list<element:")  # datasets re-encodes the list child name
    rec["arrow_schema_equal_names_types"] = [(f.name, nz(f.type)) for f in hub_tbl.schema] == [(f.name, nz(f.type)) for f in t.schema]
    mism = []
    for col in t.column_names:
        la, ha = t.column(col).to_pylist(), hub_tbl.column(col).to_pylist()
        if la != ha:
            bad = [i for i, (x, y) in enumerate(zip(la, ha)) if x != y]
            mism.append({"column": col, "n_rows_differ": len(bad), "first": bad[:3]})
    rec["cells_equal_local"] = not mism
    rec["column_mismatches"] = mism
    feats = {k: str(v) for k, v in ds[split].features.items()}
    rec["image_features"] = [k for k, v in feats.items() if "Image" in v]
    out["configs"][name] = rec
    print(name, rec["splits"], "card", rec["card_rows"], "cells_equal" if rec["cells_equal_local"] else "DIFF", flush=True)
out["total_rows"] = total_rows
out["all_equal"] = all(r["rows_equal_local"] and r["cells_equal_local"] and r["columns_equal"] and r["rows_match_card"] and r["arrow_schema_equal_names_types"] for r in out["configs"].values())
Path(a.out).write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print("total rows", total_rows, "all_equal", out["all_equal"], "names_equal_yaml", out["names_equal_yaml"])
