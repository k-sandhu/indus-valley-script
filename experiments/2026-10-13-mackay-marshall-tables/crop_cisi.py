"""Crop CISI basic-data lines for checking joins by eye.

    python -P experiments/2026-10-13-mackay-marshall-tables/crop_cisi.py OUT.png 1:403:M-109 2:471:M-878 ...

Each argument is volume:pdf_page:CISI number. The page image is extracted from the held
scan (CISI 1, first scan copy; CISI 2, archive.org copy), enlarged three times, read with
Tesseract to find the line that starts with the CISI number, and cropped to that line with
two lines of context. Lines the OCR misses are reported, and the half-column is cropped
instead so the entry can be found by eye. Output is local-only.
"""
import re
import subprocess
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/2026-10-13-mackay-marshall-tables/cisi"
PDF = {
    "1": ROOT / "research/literature/sources/joshi_parpola_1987_cisi1.pdf",
    "2": ROOT / "data/raw/2026-10-06-evidence-census/sites-deep/a-pakistan-afghanistan/common-revision/cisi2-archive.pdf",
}


def page_image(vol: str, pdfp: int) -> Path:
    out = RAW / f"cisi{vol}_pdf{pdfp}_x3.png"
    if not out.exists():
        d = fitz.open(PDF[vol])
        p = d[pdfp - 1]
        if vol == "2":
            # The archive.org copy layers a faint page image under a masked full-resolution
            # one, so the page is rendered rather than extracted.
            p.get_pixmap(dpi=600).save(out)
            g = ImageOps.autocontrast(Image.open(out).convert("L"), cutoff=2)
            g.point(lambda v: 255 if v > 150 else 0).convert("RGB").save(out)
            return out
        pix = fitz.Pixmap(d, p.get_images()[0][0])
        if pix.n - pix.alpha > 3 or pix.alpha:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        tmp = RAW / f"cisi{vol}_pdf{pdfp}.png"
        pix.save(tmp)
        im = Image.open(tmp)
        im.resize((im.size[0] * 3, im.size[1] * 3), Image.LANCZOS).save(out)
    return out


def tokens(img: Path):
    tsv = img.with_suffix(".tsv")
    if not tsv.exists():
        t = subprocess.run(["tesseract", str(img), "-", "--psm", "4", "tsv"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace").stdout
        tsv.write_text(t, encoding="utf-8")
    out = []
    for line in tsv.read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 12 and f[11].strip():
            out.append((f[11].strip(), int(f[6]), int(f[7]), int(f[9])))
    return out


def main():
    out_name, specs = sys.argv[1], sys.argv[2:]
    crops = []
    for spec in specs:
        vol, pdfp, cisi = spec.split(":")
        img = page_image(vol, int(pdfp))
        im = Image.open(img)
        w, h = im.size
        n = re.sub(r"\D", "", cisi)
        hit = None
        for text, left, top, height in tokens(img):
            t = re.sub(r"[^0-9]", "", text.replace("I", "1").replace("l", "1").replace("O", "0"))
            if text.upper().startswith("M") and t == n:
                hit = (left, top, height)
                break
        if hit:
            left, top, height = hit
            x0 = 0 if left < w / 2 else w // 2
            crops.append((spec, im.crop((x0, max(0, top - 2 * height - 10), x0 + w // 2, min(h, top + 3 * height + 10)))))
            print(spec, "found at", left, top)
        else:
            # Fallback: interpolate from neighbouring entry numbers that OCR did read.
            anchors = []
            for text, left, top, height in tokens(img):
                t = re.sub(r"[^0-9]", "", text)
                if text.upper().startswith("M") and t and abs(int(t) - int(n)) <= 40 and int(t) != int(n):
                    anchors.append((int(t), left, top, height))
            col = None
            if anchors:
                near = sorted(anchors, key=lambda a: abs(a[0] - int(n)))[:4]
                col = 0 if sum(a[1] for a in near) / len(near) < w / 2 else 1
                same = sorted(a for a in anchors if (a[1] < w / 2) == (col == 0))
                below = [a for a in same if a[0] < int(n)]
                above = [a for a in same if a[0] > int(n)]
                if below and above:
                    (n0, _, y0, hh), (n1, _, y1, _) = below[-1], above[0]
                    y = int(y0 + (y1 - y0) * (int(n) - n0) / (n1 - n0))
                elif below:
                    n0, _, y0, hh = below[-1]
                    step = (below[-1][2] - below[0][2]) / max(1, below[-1][0] - below[0][0]) if len(below) > 1 else 3 * hh
                    y = int(y0 + step * (int(n) - n0))
                elif above:
                    n1, _, y1, hh = above[0]
                    step = (above[-1][2] - above[0][2]) / max(1, above[-1][0] - above[0][0]) if len(above) > 1 else 3 * hh
                    y = int(y1 - step * (n1 - int(n)))
                else:
                    y = None
                if y is not None:
                    y = max(5 * hh, min(h - 5 * hh, y))
                    x0 = 0 if col == 0 else w // 2
                    crops.append((spec + " (interpolated)", im.crop((x0, max(0, y - 5 * hh), x0 + w // 2, min(h, y + 5 * hh)))))
                    print(spec, "interpolated at", y)
                    continue
            print(spec, "not found by OCR")
    if not crops:
        return
    width = max(c.size[0] for _, c in crops)
    total = sum(c.size[1] + 30 for _, c in crops)
    canvas = Image.new("RGB", (width, total), "white")
    draw = ImageDraw.Draw(canvas)
    y = 0
    for spec, c in crops:
        draw.rectangle([0, y, width, y + 26], fill=(255, 235, 200))
        draw.text((6, y + 6), spec, fill="black")
        canvas.paste(c, (0, y + 26))
        y += c.size[1] + 30
    canvas.save(RAW / out_name)
    print(RAW / out_name, canvas.size)


if __name__ == "__main__":
    main()
