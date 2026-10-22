"""Render one grey page at a time per worker and preserve local OCR only."""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("raw", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--last", type=int, default=337)
    args = ap.parse_args()
    digest = hashlib.file_digest(args.pdf.open("rb"), "sha256").hexdigest()
    assert digest == "3bb42d877df5a6c45367e7aacb9588206a71447dae4c32fde8f2ff9b5bba23c3"
    textdir = args.raw / "text" / "iar-1996-97-archive"
    tempdir = args.raw / "temporary"
    textdir.mkdir(parents=True, exist_ok=True)
    tempdir.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["OMP_THREAD_LIMIT"] = "1"
    exe = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    def page(n):
        target = textdir / f"p{n:04d}"
        record = args.raw / "processing" / f"p{n:04d}.json"
        record.parent.mkdir(parents=True, exist_ok=True)
        if target.with_suffix(".txt").exists() and record.exists():
            return json.loads(record.read_text(encoding="utf-8"))
        started = time.monotonic()
        with tempfile.TemporaryDirectory(prefix=f"p{n:04d}-", dir=tempdir) as td:
            image = Path(td) / "page"
            subprocess.run(["pdftoppm", "-f", str(n), "-l", str(n), "-singlefile",
                            "-r", "300", "-gray", "-png", str(args.pdf), str(image)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                subprocess.run([exe, str(image.with_suffix(".png")), str(target),
                                "-l", "eng", "--dpi", "300", "txt", "tsv"],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=env)
            finally:
                image.with_suffix(".png").unlink(missing_ok=True)
        edges = []
        tsv = target.with_suffix(".tsv")
        with tsv.open(encoding="utf-8", newline="") as f:
            items = list(csv.DictReader(f, delimiter="\t"))
        height = int(items[0]["height"])
        for r in items:
            s = r["text"].strip()
            y = int(r["top"])
            if re.fullmatch(r"\d{1,3}|[ivxlcdmIVXLCDM]{1,7}", s) and (y < height * .16 or y > height * .86):
                edges.append(dict(value=s, top=y, left=int(r["left"]), confidence=float(r["conf"])))
        tsv.unlink()
        result = dict(pdf_page=n, edge_numbers=edges, seconds=round(time.monotonic()-started, 2),
                      text_sha256=hashlib.sha256(target.with_suffix(".txt").read_bytes()).hexdigest())
        record.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
        return result

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(page, range(1, args.last+1)):
            results.append(result)
            if len(results) % 10 == 0 or len(results) == args.last:
                print(json.dumps(dict(ocr_pages=len(results), total=args.last)), flush=True)
    metadata = dict(source_id="iar-1996-97-archive", source_sha256=digest, pages=args.last,
                    render_dpi=300, colour="grey", language="eng", workers=args.workers,
                    text_basis="tesseract", rendered_files_retained=0,
                    source_rights="rights-unverified", local_only_text=str(textdir).replace("\\", "/"))
    (args.output / "ocr-provenance-E.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(metadata), flush=True)


if __name__ == "__main__":
    main()
