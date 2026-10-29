"""Run the dataset card's loading snippets verbatim from the repository root (cache redirected to the raw directory)."""
import os, json
raw = os.path.abspath("data/raw/2026-10-08-hf-public-release")
os.environ["HF_DATASETS_CACHE"] = raw + "/hfc"
os.environ["HF_HOME"] = raw + "/hfc-home"
os.environ["TMP"] = os.environ["TEMP"] = raw + "/tmp-review"
os.environ["HF_HUB_OFFLINE"] = "1"

# --- card snippet 1 ---
from datasets import load_dataset
repo = "experiments/2026-10-08-hf-public-release/release"
chart = load_dataset(repo, "chart_reference", split="train")
rows = load_dataset(repo, "benchmark_rows_v2", split="test")
sites = load_dataset(repo, "evidence_sites", split="train")
print("snippet1", len(chart), len(rows), len(sites))

# --- card snippet 2 ---
from datasets import get_dataset_config_names, load_dataset
tables = {name: load_dataset(repo, name)
          for name in get_dataset_config_names(repo)}
print("snippet2", {k: {s: len(v[s]) for s in v} for k, v in tables.items()})

# --- card snippet 3 ---
import json
from pathlib import Path
from PIL import Image

reference = json.loads(rows[0]["reference_json"])
image = Image.open(Path(repo) / rows[0]["context_image_path"])
print("snippet3", list(reference.keys())[:10], image.size, image.mode)
print("row0 keys", list(rows[0].keys()))
print("exact path", rows[0]["exact_image_path"])
