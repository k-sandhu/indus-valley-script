#!/usr/bin/env python3
"""Inventory local holdings: files and bytes by package, PDF hashes, and
source records harvested from earlier packages.

Tracked output (counts only) goes to --out. The full file list, PDF hash
table and harvested source index name third-party files and stay local under
--raw-out. Both directories must be new.

Usage (from the repository root):
    python -I experiments/2026-10-12-data-inventory/holdings.py \
        --out experiments/2026-10-12-data-inventory/run-2026-10-12/holdings \
        --raw-out data/raw/2026-10-12-data-inventory/holdings-v1
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOCAL_ROOTS = [
    "data",
    "research/literature/sources",
    "research/literature/primary",
    "research/literature/nonlinguistic_controls",
    "research/corpus/primary",
]
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".gif"}
DATA_EXT = {".json", ".jsonl", ".csv", ".tsv", ".sql", ".xml", ".parquet", ".geojson", ".zip", ".gz"}
SOURCE_RECORD_NAMES = re.compile(r"(sources|source-register|source_register|acquisition|source_retrieval_log|source_identity_index|observations)[^/]*\.json$", re.I)
TITLE_KEYS = ("title", "exact_title", "source_title", "publication_title")
LOCATOR_KEYS = ("url", "source_url", "final_url", "doi", "local_path", "path", "local_witness", "witness", "source", "filename")


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def package_of(rel: str) -> str:
    parts = rel.split("/")
    if parts[0] == "data" and len(parts) > 2 and parts[1] == "raw":
        return "data/raw/" + parts[2]
    if parts[0] == "data" and len(parts) > 1:
        return "data/" + parts[1]
    return "/".join(parts[:3])


def walk_files():
    for base in LOCAL_ROOTS:
        root = ROOT / base
        if not root.exists():
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for name in filenames:
                p = pathlib.Path(dirpath) / name
                try:
                    size = p.stat().st_size
                except OSError:
                    continue
                yield p, p.relative_to(ROOT).as_posix(), size


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def harvest(obj, origin, out):
    if isinstance(obj, dict):
        title = next((obj[k] for k in TITLE_KEYS if isinstance(obj.get(k), str) and len(obj[k].strip()) >= 8), None)
        locators = {k: obj[k] for k in LOCATOR_KEYS if isinstance(obj.get(k), str) and obj[k].strip()}
        if title and locators:
            out.append({
                "title": title.strip(),
                "year": obj.get("year") or obj.get("date"),
                "locators": locators,
                "rights": obj.get("rights") or obj.get("rights_status") or obj.get("reuse") or obj.get("license"),
                "record_file": origin,
            })
        for v in obj.values():
            harvest(v, origin, out)
    elif isinstance(obj, list):
        for v in obj:
            harvest(v, origin, out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--raw-out", required=True)
    args = ap.parse_args()
    out = ROOT / args.out
    raw = ROOT / args.raw_out
    for d in (out, raw):
        if d.exists():
            sys.exit(f"refusing to overwrite existing output {d}")

    by_pkg = collections.defaultdict(lambda: {"files": 0, "bytes": 0, "pdf": 0, "images": 0, "data_files": 0, "ext": collections.Counter()})
    files = []
    pdfs = []
    for p, rel, size in walk_files():
        ext = p.suffix.lower()
        pkg = package_of(rel)
        rec = by_pkg[pkg]
        rec["files"] += 1
        rec["bytes"] += size
        rec["ext"][ext or "(none)"] += 1
        entry = {"path": rel, "bytes": size, "ext": ext}
        if ext == ".pdf":
            rec["pdf"] += 1
            entry["sha256"] = sha256(p)
            pdfs.append(entry)
        elif ext in IMAGE_EXT:
            rec["images"] += 1
        elif ext in DATA_EXT:
            rec["data_files"] += 1
        files.append(entry)

    pdf_groups = collections.defaultdict(list)
    for e in pdfs:
        pdf_groups[e["sha256"]].append(e["path"])
    distinct_pdf_bytes = sum(next(e["bytes"] for e in pdfs if e["sha256"] == h) for h in pdf_groups)

    # Harvest source records from earlier packages.
    harvested = []
    record_files = 0
    for base in ("experiments", "research/literature", "research/corpus", "knowledge/provenance"):
        for dirpath, _d, filenames in os.walk(ROOT / base):
            if "__pycache__" in dirpath:
                continue
            for name in filenames:
                rel = (pathlib.Path(dirpath) / name).relative_to(ROOT).as_posix()
                if not SOURCE_RECORD_NAMES.search(name):
                    continue
                try:
                    obj = json.loads((pathlib.Path(dirpath) / name).read_text(encoding="utf-8"))
                except (ValueError, OSError, UnicodeDecodeError):
                    continue
                record_files += 1
                harvest(obj, rel, harvested)
    distinct_titles = collections.defaultdict(list)
    for h in harvested:
        distinct_titles[norm_title(h["title"])].append(h)
    pdf_paths = {e["path"] for e in pdfs}
    titles_with_local_pdf = sum(
        1 for recs in distinct_titles.values()
        if any(str(v).replace("\\", "/") in pdf_paths for x in recs for v in x["locators"].values())
    )

    out.mkdir(parents=True)
    raw.mkdir(parents=True)
    with (raw / "files.jsonl").open("w", encoding="utf-8") as fh:
        for e in files:
            fh.write(json.dumps(e) + "\n")
    with (raw / "pdf-hashes.jsonl").open("w", encoding="utf-8") as fh:
        for h, paths in sorted(pdf_groups.items(), key=lambda kv: kv[1][0]):
            fh.write(json.dumps({"sha256": h, "paths": paths}) + "\n")
    with (raw / "harvested-sources.jsonl").open("w", encoding="utf-8") as fh:
        for h in harvested:
            fh.write(json.dumps(h, ensure_ascii=False, default=str) + "\n")

    packages = {
        k: {"files": v["files"], "bytes": v["bytes"], "pdf": v["pdf"], "images": v["images"],
            "data_files": v["data_files"], "top_extensions": dict(v["ext"].most_common(6))}
        for k, v in sorted(by_pkg.items())
    }
    summary = {
        "date": "2026-10-12",
        "roots": LOCAL_ROOTS,
        "files": len(files),
        "bytes": sum(e["bytes"] for e in files),
        "pdf_files": len(pdfs),
        "pdf_bytes": sum(e["bytes"] for e in pdfs),
        "distinct_pdfs_by_sha256": len(pdf_groups),
        "distinct_pdf_bytes": distinct_pdf_bytes,
        "pdf_hashes_with_more_than_one_copy": sum(1 for v in pdf_groups.values() if len(v) > 1),
        "image_files": sum(v["images"] for v in by_pkg.values()),
        "packages": packages,
        "local_listing": {"files": f"{args.raw_out}/files.jsonl", "pdf_hashes": f"{args.raw_out}/pdf-hashes.jsonl"},
    }
    harvest_summary = {
        "date": "2026-10-12",
        "rule": "JSON records with a title of at least eight characters and a URL, DOI or path, found in files whose names match sources/source-register/acquisition/retrieval/identity/observations JSON under experiments/, research/literature/, research/corpus/ and knowledge/provenance/. Heuristic: schemas differ, so some records are missed or counted under variant titles.",
        "record_files_parsed": record_files,
        "harvested_records": len(harvested),
        "distinct_normalized_titles": len(distinct_titles),
        "distinct_titles_with_a_locator_matching_a_local_pdf_path": titles_with_local_pdf,
        "local_index": f"{args.raw_out}/harvested-sources.jsonl",
    }
    (out / "holdings-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out / "literature-harvest-summary.json").write_text(json.dumps(harvest_summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("files", "bytes", "pdf_files", "distinct_pdfs_by_sha256", "image_files")}, indent=2))
    print(json.dumps({k: harvest_summary[k] for k in ("record_files_parsed", "harvested_records", "distinct_normalized_titles", "distinct_titles_with_a_locator_matching_a_local_pdf_path")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
