"""Copy the Check 2 crops under random labels for blind reading.

For every seal in object-lists.json with view crops, one composite image is written to
data/raw/2026-10-13-plate-checks/blind/: the impression of side A on the left and the
object photograph of side A on the right, each scaled to the same height. The header
shows only the random label, the photograph kinds, the catalogue's number of signs and
its direction code. Labels are a shuffle drawn from the operating system's generator.
Version 2 (13 October 2026): the Lipi crops carry the catalogue caption with the CISI
number below the photograph; version 1 composites (blind/) showed it and were withdrawn
after the first was opened. Version 2 (blind-v2/) removed captions by a gap rule that missed many and was withdrawn
after a low-resolution check of its bottom strips showed captions. Version 3 removes
the caption by the row-fill rule in strip_caption and draws new labels. The key
(label to pair, group and CISI number) goes to blind-key-v3/KEY.json, a separate
directory that is not opened until every blinded seal has a recorded reading. The
script prints only counts.
"""
import hashlib
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CROPS = ROOT / "data/lipi/public/seal_images"
OUT = ROOT / "data/raw/2026-10-13-plate-checks/blind-v3"
KEYDIR = ROOT / "data/raw/2026-10-13-plate-checks/blind-key-v3"
HEIGHT = 520


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_runs(a, thr=0.015, merge=2):
    dark = (a < 120).mean(1) > thr
    runs, i, h = [], 0, a.shape[0]
    while i < h:
        if dark[i]:
            j = i
            while j < h and dark[j]:
                j += 1
            if runs and i - runs[-1][1] <= merge:
                runs[-1] = (runs[-1][0], j)
            else:
                runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


def strip_caption(im, fill=0.45):
    """Remove the catalogue caption printed below the photograph in Lipi crops.

    Rows of the object are mostly non-white; rows of the caption are mostly white with a
    short line of print. Scanning up from the bottom, the crop is cut two rows below the
    lowest row in which at least 45% of the pixels are darker than the page (value < 215).
    A cut that would remove more than 35% of the crop is not applied. Returns the image
    and the cut row (None if uncut).
    """
    import numpy as np
    a = np.asarray(im)
    h = a.shape[0]
    filled = (a < 215).mean(1)
    rows = np.flatnonzero(filled >= fill)
    if rows.size:
        cut = min(h, int(rows[-1]) + 2)
        if cut < h and cut >= 0.65 * h:
            return im.crop((0, 0, im.width, cut)), cut
    return im, None


def scaled(path):
    im, cut = strip_caption(Image.open(path).convert("L"))
    f = HEIGHT / im.height
    return im.resize((max(1, round(im.width * f)), HEIGHT), Image.LANCZOS), (im.size, cut)


def main():
    lists = json.loads((HERE / "object-lists.json").read_text(encoding="utf-8"))
    seals = [t for t in lists["check2"] if t["view_crops"]]
    labels = ["S%02d" % i for i in range(1, len(seals) + 1)]
    random.SystemRandom().shuffle(labels)
    OUT.mkdir(parents=True, exist_ok=False)
    KEYDIR.mkdir(parents=True, exist_ok=True)
    key, sheet = {}, {}
    for label, t in zip(labels, seals):
        parts, kinds, sources = [], [], []
        for kind in ("impression", "object", "other"):
            name = t["view_crops"].get(kind)
            if name:
                im, size = scaled(CROPS / name)
                parts.append(im)
                kinds.append(kind)
                sources.append({"file": name, "kind": kind, "used_size": size[0], "caption_cut_row": size[1], "sha256": sha256(CROPS / name)})
        gap, head = 24, 40
        width = sum(p.width for p in parts) + gap * (len(parts) + 1)
        canvas = Image.new("L", (width, HEIGHT + head + gap), 255)
        x = gap
        for p in parts:
            canvas.paste(p, (x, head))
            x += p.width + gap
        d = ImageDraw.Draw(canvas)
        d.text((gap, 10), "%s   %s   catalogue signs: %d   direction: %s" % (
            label, " | ".join(kinds), t["length"], t["direction"]), fill=0)
        out = OUT / ("%s.png" % label)
        canvas.save(out)
        key[label] = {"pair": t["pair"], "group": t["group"], "cisi": t["cisi"], "family": t["family"],
                      "sources": sources, "composite_sha256": sha256(out)}
        sheet[label] = {"kinds": kinds, "catalogue_signs": t["length"], "direction": t["direction"]}
    (KEYDIR / "KEY.json").write_text(json.dumps(dict(sorted(key.items())), indent=1), encoding="utf-8")
    (OUT / "SHEET.json").write_text(json.dumps(dict(sorted(sheet.items())), indent=1), encoding="utf-8")
    print({"blinded_seals": len(seals), "composites": len(key)})


if __name__ == "__main__":
    main()
