"""Cut tail strips for blocks whose text runs below their last strip (AMENDMENT-1.md).

Usage (from the repository root):
  python experiments/2026-10-13-cisi-basic-data-full/make_tail_strips.py

make_strips.py ended each block at the last text row it detected with a darkness threshold of 128,
which misses the faint lines at the foot of several CISI 2 pages. This script measures each block's
text extent again with a threshold of 170 (ignoring the vertical rule at the left edge of a
half-column and 25 px at the page edges) and, where the text continues more than 3 px below the
last strip, cuts tail strips: t01 is the block's last strip again, for context, and the following
windows run down to the last text row, with the same window height and overlap as make_strips.py.
Tail strips go to data/raw/2026-10-13-cisi-basic-data-full/strips/<block>/t01.png, t02.png, ...;
tails.json in this directory lists the affected blocks and their missing heights, with no values.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "data/raw/2026-10-13-cisi-basic-data-full"
WINDOW = {"cisi2": (640, 90, 25), "cisi1": (460, 65, 15)}


def main():
    blocks = json.loads((RAW / "strips.json").read_text(encoding="utf-8"))
    tails = []
    for blk in blocks:
        im = Image.open(ROOT / blk["render"])
        a = np.asarray(im, dtype=np.uint8)
        x0, x1 = blk["strips"][0]["x"]
        ink = (a[:, x0 + 30:x1 - 10] < 170).sum(axis=1)
        rows = np.where(ink >= 3)[0]
        rows = rows[(rows > 20) & (rows < im.height - 25)]
        if not len(rows):
            continue
        last_ink = int(rows[-1])
        last = blk["strips"][-1]
        if last_ink <= last["y"][1] + 3:
            continue
        height, overlap, band = WINDOW[blk["volume"]]
        full = (a[:, x0:x1] < 128).sum(axis=1)
        bottom = min(im.height, last_ink + 15)

        def snap(y):
            lo, hi = max(0, y - band), min(bottom, y + band)
            return lo + int(np.argmin(full[lo:hi])) if hi > lo else y

        outdir = RAW / "strips" / blk["block"]
        for old in outdir.glob("t*.png"):
            old.unlink()
        files, y0, y1 = [], last["y"][0], last["y"][1]
        while True:
            name = outdir / f"t{len(files) + 1:02d}.png"
            im.crop((x0, y0, x1, y1)).save(name)
            files.append({"file": name.relative_to(ROOT).as_posix(), "y": [y0, y1]})
            if y1 >= bottom:
                break
            y0 = snap(y1 - overlap)
            y1 = bottom if y0 + height >= bottom else snap(y0 + height)
        tails.append({"block": blk["block"], "last_strip_bottom": last["y"][1], "last_text_row": last_ink,
                      "missing_px": last_ink - last["y"][1], "tail_strips": len(files)})
        print(blk["block"], "missing", last_ink - last["y"][1], "px;", len(files), "tail strips")
    (HERE / "tails.json").write_text(json.dumps(tails, indent=1) + "\n", encoding="utf-8")
    (RAW / "tails-local.json").write_text(json.dumps(tails, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
