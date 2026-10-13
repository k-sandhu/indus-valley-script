"""Read the printed CISI captions inside every Lipi image crop with tesseract.

Usage (from the repository root):
    python -P experiments/2026-10-13-image-index-and-units/crop_ocr.py [--workers 12]

The Lipi crops are cut from the CISI plates together with the printed caption below each
photograph. Each crop is converted to grey, enlarged so that its shorter side is at least
600 pixels, and read with tesseract in sparse-text mode (psm 11). The raw text is saved
locally (it is text from the catalogue pages) in
data/raw/2026-10-13-image-index-and-units/crop-ocr/crop-ocr.jsonl, one record per file with
the file name, SHA-256 and OCR text. build_index.py extracts catalogue keys from this text
to check every file name against its caption. The output file is never overwritten.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
CROPS = ROOT / "data/lipi/public/seal_images"
OUT = ROOT / "data/raw/2026-10-13-image-index-and-units/crop-ocr/crop-ocr.jsonl"


def read_one(name):
    path = CROPS / name
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    try:
        im = Image.open(path).convert("L")
    except OSError as exc:
        return {"file": name, "sha256": digest, "error": str(exc)}
    w, h = im.size
    scale = max(1.0, 600.0 / max(1, min(w, h)))
    scale = min(scale, 4.0)
    if scale > 1.0:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, "c.png")
        im.save(png)
        r = subprocess.run(["tesseract", png, "-", "--psm", "11"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    return {"file": name, "sha256": digest, "size": [w, h], "scale": round(scale, 3), "ocr": r.stdout}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    if OUT.exists():
        sys.exit(f"refusing to overwrite {OUT}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    names = sorted(p.name for p in CROPS.iterdir() if p.is_file())
    with mp.Pool(a.workers) as pool, OUT.open("w", encoding="utf-8") as fh:
        for i, rec in enumerate(pool.imap(read_one, names, chunksize=16), 1):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if i % 500 == 0:
                print(i, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
