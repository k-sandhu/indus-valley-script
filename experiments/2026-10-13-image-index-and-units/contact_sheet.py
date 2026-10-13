"""Compose local image crops into labelled contact sheets for visual checking.

Usage (from the repository root):
    python -I experiments/2026-10-13-image-index-and-units/contact_sheet.py OUT.png NAME [NAME ...]
    python -I experiments/2026-10-13-image-index-and-units/contact_sheet.py OUT.png --list FILE.txt

Each NAME is a file in data/lipi/public/seal_images/. Each cell holds the whole crop scaled
to fit (caption included) with a numbered label above it, so the reader can check the
printed caption against the file name. Options: --cols N (default 4), --cell W (default
420 pixels), --labels short|full, --bottom F (show the lower fraction F of each crop,
enlarged, to read a caption). Sheets are written under
data/raw/2026-10-13-image-index-and-units/ and never tracked, because they reproduce
CISI photographs.
"""
import argparse
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
CROPS = ROOT / "data/lipi/public/seal_images"
RAW = ROOT / "data/raw/2026-10-13-image-index-and-units"


def font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sheet(names, out, cols=4, cell=420, labels="full", numbers=None, bottom=None):
    f = font(16)
    label_h = 24
    rows = (len(names) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * cell, rows * (cell + label_h)), "white")
    draw = ImageDraw.Draw(canvas)
    for i, name in enumerate(names):
        r, c = divmod(i, cols)
        x0, y0 = c * cell, r * (cell + label_h)
        num = numbers[i] if numbers else str(i + 1)
        text = num if labels == "short" else f"{num}: {name}"
        draw.text((x0 + 4, y0 + 3), text[:60], fill="red", font=f)
        try:
            im = Image.open(CROPS / name).convert("RGB")
        except (OSError, FileNotFoundError):
            draw.text((x0 + 10, y0 + label_h + 10), "unreadable", fill="red", font=f)
            continue
        if bottom:
            w, h = im.size
            im = im.crop((0, int(h * (1 - bottom)), w, h))
            scale = (cell - 8) / max(im.size)
            im = im.resize((max(1, int(im.size[0] * scale)), max(1, int(im.size[1] * scale))))
        im.thumbnail((cell - 8, cell - 8))
        canvas.paste(im, (x0 + 4, y0 + label_h + 2))
        draw.rectangle([x0, y0, x0 + cell - 1, y0 + cell + label_h - 1], outline="gray")
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--list")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell", type=int, default=420)
    ap.add_argument("--labels", default="full", choices=["full", "short"])
    ap.add_argument("--bottom", type=float, help="show only this lower fraction of each crop, enlarged")
    a = ap.parse_args()
    names = list(a.names)
    if a.list:
        names += [l.strip() for l in pathlib.Path(a.list).read_text(encoding="utf-8").splitlines() if l.strip()]
    out = pathlib.Path(a.out)
    if not out.is_absolute():
        out = RAW / out
    if RAW.resolve() not in out.resolve().parents:
        sys.exit("contact sheets must be written under " + str(RAW))
    print(sheet(names, out, a.cols, a.cell, a.labels, bottom=a.bottom))


if __name__ == "__main__":
    main()
