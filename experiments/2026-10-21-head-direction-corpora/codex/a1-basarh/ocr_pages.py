"""Make local OCR drafts of rendered pages; these require image review.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/ocr_pages.py --pages <owned PNG directory> --out <owned scratch directory> [--workers 4]
Uses the installed Tesseract executable and preserves its text output locally.
"""
import argparse
import concurrent.futures
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    def work(png):
        target = args.out / png.stem
        if target.with_suffix(".txt").exists():
            return
        proc = subprocess.run([r"C:\Program Files\Tesseract-OCR\tesseract.exe", str(png), str(target), "--psm", "3"], capture_output=True, text=True)
        if proc.returncode:
            print(png.name + " failed: " + proc.stderr, flush=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(work, sorted(args.pages.glob("*.png"))))
    print("OCR files: " + str(len(list(args.out.glob("*.txt")))), flush=True)


if __name__ == "__main__":
    main()
