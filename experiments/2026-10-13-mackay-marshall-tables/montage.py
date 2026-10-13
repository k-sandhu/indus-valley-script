"""Stack row crops into one image for reading by eye.

    python -P experiments/2026-10-13-mackay-marshall-tables/montage.py OUT.png crop1.png crop2.png ...

Paths are relative to data/raw/2026-10-13-mackay-marshall-tables/crops/. A thin black rule
separates crops; the file name is written at the left of each crop's top edge.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

CROPS = Path(__file__).resolve().parents[2] / "data/raw/2026-10-13-mackay-marshall-tables/crops"


def main():
    out, names = sys.argv[1], sys.argv[2:]
    ims = [Image.open(CROPS / n).convert("RGB") for n in names]
    width = max(i.size[0] for i in ims)
    label_h = 28
    total = sum(i.size[1] + label_h + 4 for i in ims)
    canvas = Image.new("RGB", (width, total), "white")
    draw = ImageDraw.Draw(canvas)
    y = 0
    for n, im in zip(names, ims):
        draw.rectangle([0, y, width, y + label_h], fill=(255, 235, 200))
        draw.text((8, y + 6), n, fill="black")
        y += label_h
        canvas.paste(im, (0, y))
        y += im.size[1]
        draw.rectangle([0, y, width, y + 3], fill="black")
        y += 4
    scale = min(1.0, 1900 / width)
    if scale < 1.0:
        canvas = canvas.resize((int(width * scale), int(total * scale)), Image.LANCZOS)
    canvas.save(CROPS / out)
    print(CROPS / out, canvas.size)


if __name__ == "__main__":
    main()
