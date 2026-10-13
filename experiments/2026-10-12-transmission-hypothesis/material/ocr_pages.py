"""Render selected primary PDF pages and preserve Tesseract OCR locally.

Acquisition is not inspection. No source is corrected; each derivative carries hashes.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import fitz


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("pages", help="One-based pages, comma-separated, with inclusive ranges")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    pages = set()
    for item in args.pages.split(","):
        if "-" in item:
            a, b = map(int, item.split("-"))
            pages.update(range(a, b+1))
        else:
            pages.add(int(item))
    doc = fitz.open(args.source)
    if not pages or min(pages) < 1 or max(pages) > len(doc):
        raise ValueError("Selected page outside actual PDF")
    engine = shutil.which("tesseract")
    if engine is None:
        raise RuntimeError("Tesseract is required")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    source_hash = digest(args.source)
    records = []
    for n in sorted(pages):
        image = args.output_dir / f"pdf{n}.png"
        doc[n-1].get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False).save(image)
        records.append({"source_path": args.source.as_posix(), "source_sha256": source_hash,
                        "pdf_page": n, "render_path": image.as_posix(), "render_sha256": digest(image),
                        "render_method": "PyMuPDF 1.8 raster scale; alpha disabled"})

    def recognize(row):
        stem = args.output_dir / f"pdf{row['pdf_page']}"
        result = subprocess.run([engine, row["render_path"], str(stem), "-l", "eng", "--psm", "3"], capture_output=True, text=True)
        text_path = stem.with_suffix(".txt")
        row.update(ocr_method="Tesseract eng --psm 3, uncorrected", ocr_exit_code=result.returncode,
                   ocr_stderr=result.stderr, redistribution="local-only source derivative")
        if result.returncode == 0 and text_path.exists():
            row.update(text_path=text_path.as_posix(), text_sha256=digest(text_path), characters=len(text_path.read_text(encoding="utf-8")))
        return row
    with ThreadPoolExecutor(max_workers=3) as pool:
        records = list(pool.map(recognize, records))
    version = subprocess.run([engine, "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    payload = {"engine_version": version, "records": records}
    (args.output_dir / "manifest.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"source": args.source.name, "pages": len(pages), "succeeded": sum(r["ocr_exit_code"] == 0 for r in records)}))


if __name__ == "__main__":
    main()
