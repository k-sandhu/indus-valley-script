"""Crop printed table rows from the local page images for checking by eye.

Run from the repository root:
    python -P experiments/2026-10-13-mackay-marshall-tables/crop_rows.py mackay 20 49 56
    python -P experiments/2026-10-13-mackay-marshall-tables/crop_rows.py marshall 11 26

Page images are rendered by render_pages.py into data/raw/2026-10-13-mackay-marshall-tables/
{mackay1938,marshall1931}/pages/. Tesseract (TSV output) finds the printed row number in
the number column; the crop takes that line with one line of context above and below.
If the number is not found, the crop falls back to the row's position interpolated from the
numbers that were found on the same page. Crops are local-only.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-13-mackay-marshall-tables"
TAB = RAW / "epachayan-indus-script/outputs"
CROPS = RAW / "crops"


def ocr_numbers(img_path: Path, x_max_frac: float, x_min_frac: float = 0.0):
    """Return {number: y_centre} for integer tokens in a left column band."""
    cache = img_path.with_suffix(".tsv")
    if not cache.exists():
        tsv = subprocess.run(["tesseract", str(img_path), "-", "--psm", "4", "tsv"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        cache.write_text(tsv, encoding="utf-8")
    tsv = cache.read_text(encoding="utf-8")
    w = Image.open(img_path).size[0]
    found = {}
    for line in tsv.splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 12 or not f[11].strip():
            continue
        left, top, width, height = map(int, f[6:10])
        tok = re.sub(r"[^0-9A-Za-z]", "", f[11])
        if x_min_frac * w <= left <= x_max_frac * w and re.fullmatch(r"\d{1,3}[A-Da-d]?", tok):
            found.setdefault(tok.upper(), top + height // 2)
    return found


def locate(page_img: Path, label: str, band, lo: int, hi: int):
    """Locate a row by its printed number.

    Numbers read by OCR within [lo, hi] (the rows the transcription assigns to this page or
    column) are fitted with a Theil-Sen line y = a + b*n; misread numbers fall off the line.
    An exact OCR hit is used if it lies on the line, otherwise the line's prediction.
    """
    nums = ocr_numbers(page_img, band[1], band[0])
    n = int(re.match(r"\d+", label).group())
    pts = [(int(k), y) for k, y in nums.items() if re.fullmatch(r"\d+", k) and lo <= int(k) <= hi]
    if len(pts) < 3:
        return (nums[label.upper()], "ocr-unchecked") if label.upper() in nums else (None, "none")
    slopes = sorted((y1 - y0) / (n1 - n0) for i, (n0, y0) in enumerate(pts) for (n1, y1) in pts[i + 1:] if n1 != n0)
    b = slopes[len(slopes) // 2]
    a = sorted(y - b * k for k, y in pts)[len(pts) // 2]
    pred = int(a + b * n)
    if label.upper() in nums and abs(nums[label.upper()] - pred) < 0.6 * abs(b):
        return nums[label.upper()], "ocr"
    return pred, "fitted"


def crop(page_img: Path, y: int, out: Path, half_height: int, x_range=(0.0, 1.0)):
    im = Image.open(page_img)
    w, h = im.size
    box = (int(x_range[0] * w), max(0, y - half_height), int(x_range[1] * w), min(h, y + half_height))
    im.crop(box).save(out)


def main():
    which, labels = sys.argv[1], sys.argv[2:]
    CROPS.mkdir(parents=True, exist_ok=True)
    if which == "mackay":
        table = list(csv.DictReader(open(TAB / "mackay_seal_table.csv", encoding="utf-8")))
        rows = {r["no"]: r for r in table}
        for lab in labels:
            r = rows[lab]
            printed = int(r["pdf_page"]) + 324
            img = RAW / f"mackay1938/pages/p{printed}.png"
            on_page = [int(re.match(r"\d+", t["no"]).group()) for t in table if t["pdf_page"] == r["pdf_page"]]
            y, how = locate(img, lab, (0.0, 0.26), min(on_page), max(on_page))
            if y is None:
                print(lab, "not located on", img.name)
                continue
            out = CROPS / f"mackay_{lab}.png"
            crop(img, y, out, 70)
            print(lab, img.name, y, how, out.name)
    else:
        table = list(csv.DictReader(open(TAB / "marshall_seal_table_transcribed.csv", encoding="utf-8")))
        rows = {r["plate_no"]: r for r in table}
        for lab in labels:
            r = rows[lab]
            m = re.match(r"p(\d+)([LR])", r["source_page"])
            page, side = m.group(1), m.group(2)
            img = RAW / f"marshall1931/p{page}.png"
            band = (0.0, 0.12) if side == "L" else (0.47, 0.60)
            xr = (0.0, 0.56) if side == "L" else (0.44, 1.0)
            in_col = [int(re.match(r"\d+", t["plate_no"]).group()) for t in table if t["source_page"] == r["source_page"]]
            y, how = locate(img, lab, band, min(in_col), max(in_col))
            if y is None:
                print(lab, "not located on", img.name)
                continue
            out = CROPS / f"marshall_{lab}.png"
            crop(img, y, out, 55, xr)
            print(lab, img.name, side, y, how, out.name)


if __name__ == "__main__":
    main()
