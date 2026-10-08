"""Reviewer check: load every configuration of the staged release with datasets.load_dataset.

Run from the repository root:
  python -B experiments/2026-10-08-hf-public-release/review/load_check.py

Writes review/load-check.json. The Hugging Face cache and temp files go under the package's raw directory.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "experiments/2026-10-08-hf-public-release"
RELEASE = PKG / "release"
RAW = ROOT / "data/raw/2026-10-08-hf-public-release/review-cache"
RAW.mkdir(parents=True, exist_ok=True)
for var in ("HF_HOME", "TMP", "TEMP", "MPLCONFIGDIR"):
    os.environ[var] = str(RAW)
os.environ["HF_HUB_OFFLINE"] = "1"
os.chdir(RAW)  # short relative paths avoid the Windows lock-file path limit

import yaml  # noqa: E402
from datasets import get_dataset_config_names, load_dataset  # noqa: E402
from PIL import Image  # noqa: E402

card = (RELEASE / "README.md").read_text(encoding="utf-8")
front = re.match(r"---\n(.*?)\n---\n", card, re.S)
meta = yaml.safe_load(front.group(1))
configs = meta["configs"]
out = {"yaml_keys": sorted(meta.keys()), "n_configs_yaml": len(configs), "configs": {}}

# card row counts from the configuration table
table_counts = {}
for m in re.finditer(r"^\| `([a-z0-9_]+)` \| (\d+) \|", card, re.M):
    table_counts[m.group(1)] = int(m.group(2))

rel = str(RELEASE)
CACHE = "ds"  # relative cache name: the absolute-path lock name exceeds the Windows limit
names = get_dataset_config_names(rel)
out["config_names_from_library"] = names
out["names_match_yaml"] = sorted(names) == sorted(c["config_name"] for c in configs)

for c in configs:
    name = c["config_name"]
    rec = {"data_files": c["data_files"]}
    # check every data_files path exists
    paths = [d["path"] for d in c["data_files"]]
    rec["paths_exist"] = all((RELEASE / p).is_file() for p in paths)
    ds = load_dataset(rel, name, cache_dir=CACHE)
    rec["splits"] = {s: len(ds[s]) for s in ds}
    rec["expected_splits"] = [d["split"] for d in c["data_files"]]
    rec["card_rows"] = table_counts.get(name)
    rec["rows_match_card"] = sum(rec["splits"].values()) == table_counts.get(name)
    rec["features"] = {k: str(v) for k, v in ds[list(ds)[0]].features.items()}
    out["configs"][name] = rec

# image resolution through relative paths across every table that carries image paths
sample = {}
path_cols = {
    "chart_reference": ["image_path"],
    "benchmark_rows_v1": ["context_image_path", "exact_image_path"],
    "benchmark_rows_v2": ["context_image_path", "exact_image_path"],
    "benchmark_chart_cards": ["image_path"],
    "benchmark_count_pages": ["image_paths"],
    "image_assets": ["image_path"],
}
total = 0
bad = []
for name, cols in path_cols.items():
    ds = load_dataset(rel, name, cache_dir=CACHE)
    sp = list(ds)[0]
    n_ok = 0
    for row in ds[sp]:
        for col in cols:
            v = row[col]
            if v is None:
                continue
            for p in (v if isinstance(v, list) else [v]):
                total += 1
                fp = RELEASE / p
                try:
                    with Image.open(fp) as im:
                        im.load()
                    n_ok += 1
                except Exception as e:  # noqa: BLE001
                    bad.append({"config": name, "path": p, "error": repr(e)})
    sample[name] = n_ok
out["image_paths_opened_by_config"] = sample
out["image_paths_checked"] = total
out["image_failures"] = bad
all_pngs = sorted(p.relative_to(RELEASE).as_posix() for p in (RELEASE / "images").rglob("*.png"))
ia = load_dataset(rel, "image_assets", cache_dir=CACHE)["train"]
listed = sorted(ia["image_path"])
out["png_files_on_disk"] = len(all_pngs)
out["image_assets_rows"] = len(listed)
out["on_disk_equals_image_assets"] = all_pngs == listed
(PKG / "review/load-check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "configs"}, indent=1))
for n, r in out["configs"].items():
    print(n, r["splits"], "card", r["card_rows"], "ok" if r["rows_match_card"] else "MISMATCH", "paths" if r["paths_exist"] else "NOPATH")
