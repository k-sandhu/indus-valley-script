"""Image tooling for the Part 2 transcription checks.

Commands (all outputs are local-only, under data/raw/2026-10-12-round-seal-tradition/):
    python witness_tools.py grid <image> <out>            # downsampled page with a coordinate grid
    python witness_tools.py crops                         # cut every crop listed in crops.json
    python witness_tools.py composite <record_id> [...]   # witness crops beside the rendered Lipi code
    python witness_tools.py glyphs <code> [...]           # glyph sheet for Wells codes
    python witness_tools.py blind <set_name>              # code-free crop sheets for Reader 2

The Lipi font maps Wells code n to U+E000 + n (data/lipi/src/pages/index.vue, recorded
by the 2026-10-08 Bonta extension). Seal photographs are mirrored to impression
orientation when a crop is marked "mirror": true.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

import paths

CROPS = paths.HERE / "crops.json"
OUT = paths.RAW / "witness"
LABEL_FONT = "C:/Windows/Fonts/segoeui.ttf"


# Decoded TTF written by experiments/2026-10-08-bonta-extension/render_glyphs.py from the same
# WOFF2 (SHA-256 b2758032...56bf, recorded in its glyph-witness-index.json). Decoding WOFF2
# again needs the Brotli extension, which this environment lacks.
DECODED_TTF = paths.DATA / "data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf"


def _ttf() -> Path:
    ttf = paths.RAW / "lipi-font-local.ttf"
    if ttf.exists():
        return ttf
    try:
        import brotli  # noqa: F401  (WOFF2 decoding dependency)
        from fontTools.ttLib import TTFont
        f = TTFont(str(paths.LIPI_FONT))
        f.flavor = None
        ttf.parent.mkdir(parents=True, exist_ok=True)
        f.save(str(ttf))
        return ttf
    except ImportError:
        return DECODED_TTF


def label_font(size=22):
    return ImageFont.truetype(LABEL_FONT, size)


def glyph(code: str, size=96) -> Image.Image:
    ft = ImageFont.truetype(str(_ttf()), size)
    im = Image.new("RGB", (int(size * 1.25), int(size * 1.6)), "white")
    d = ImageDraw.Draw(im)
    if code in ("000", "999"):
        d.text((10, size // 2), "?" if code == "000" else "_", font=label_font(size // 2), fill="red")
    else:
        ch = chr(0xE000 + int(code))
        box = d.textbbox((0, 0), ch, font=ft)
        w, h = box[2] - box[0], box[3] - box[1]
        d.text(((im.width - w) / 2 - box[0], (size * 1.25 - h) / 2 - box[1]), ch, font=ft, fill="black")
    d.text((8, int(size * 1.3)), code, font=label_font(size // 4), fill="#1f4e9a")
    return im


def render_code(code: str, size=96) -> Image.Image:
    """Render an ICIT code string in its visual left-to-right order, with edge marks."""
    first, last = code[0], code[-1]
    body = code[1:] if first in "+]" else code
    body = body[:-1] if body and body[-1] in "+[" else body
    lines = [[t.zfill(3) for t in line.split("-") if t] for line in body.split("/")]
    rows = []
    for line in lines:
        ims = [glyph(t, size) for t in line]
        w = sum(i.width for i in ims) + 2 * 40
        row = Image.new("RGB", (w, ims[0].height), "white")
        d = ImageDraw.Draw(row)
        x = 40
        for i in ims:
            row.paste(i, (x, 0))
            x += i.width
        d.text((6, size // 3), first if first in "+]" else "", font=label_font(28), fill="red")
        d.text((w - 30, size // 3), last if last in "+[" else "", font=label_font(28), fill="red")
        rows.append(row)
    out = Image.new("RGB", (max(r.width for r in rows), sum(r.height for r in rows)), "white")
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    return out


def grid(src: Path, dst: Path, step=200, max_side=1600):
    im = Image.open(src).convert("RGB")
    scale = max_side / max(im.size)
    small = im.resize((int(im.width * scale), int(im.height * scale)))
    d = ImageDraw.Draw(small)
    f = label_font(14)
    for x in range(0, im.width, step):
        d.line([(x * scale, 0), (x * scale, small.height)], fill=(255, 0, 0), width=1)
        d.text((x * scale + 2, 2), str(x), font=f, fill=(255, 0, 0))
    for y in range(0, im.height, step):
        d.line([(0, y * scale), (small.width, y * scale)], fill=(0, 0, 255), width=1)
        d.text((2, y * scale + 2), str(y), font=f, fill=(0, 0, 255))
    dst.parent.mkdir(parents=True, exist_ok=True)
    small.save(dst)


def load_crops() -> dict:
    return json.loads(CROPS.read_text(encoding="utf-8"))


def cut(spec: dict) -> Image.Image:
    src = paths.DATA / spec["source"]
    im = Image.open(src).convert("RGB")
    if spec.get("box"):
        im = im.crop(tuple(spec["box"]))
    if spec.get("rotate"):
        im = im.rotate(spec["rotate"], expand=True, fillcolor="white")
    if spec.get("mirror"):
        im = ImageOps.mirror(im)
    return im


def crops():
    data = load_crops()
    records = []
    for cid, spec in data["crops"].items():
        im = cut(spec)
        dst = OUT / "crops" / f"{cid}.png"
        dst.parent.mkdir(parents=True, exist_ok=True)
        im.save(dst)
        src = paths.DATA / spec["source"]
        records.append({"crop": cid, "source": spec["source"],
                        "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
                        "box": spec.get("box"), "mirror": spec.get("mirror", False),
                        "png": paths.rel(dst)})
    (OUT / "crops-index.json").write_text(json.dumps(records, indent=1) + "\n", encoding="utf-8")
    print(len(records), "crops written")


def composite(record_id: str, height=520):
    C = paths.import_ffcore()
    faces = {f["record_id"]: f for f in C.load_faces()}
    face = faces[record_id]["face"]
    data = load_crops()
    cids = [c for c, s in data["crops"].items() if record_id in s.get("records", [])]
    panels = []
    for cid in cids:
        im = cut(data["crops"][cid])
        s = height / im.height
        im = im.resize((max(1, int(im.width * s)), height))
        cap = Image.new("RGB", (max(im.width, 300), height + 40), "white")
        cap.paste(im, (0, 0))
        ImageDraw.Draw(cap).text((4, height + 6), cid + (" (mirrored)" if data["crops"][cid].get("mirror") else ""),
                                 font=label_font(22), fill="black")
        panels.append(cap)
    code_im = render_code(face["text_code_visual_ltr"])
    meta = (f"{record_id}  {face['site']}  {face['object_type']}  dir={face['direction']}  "
            f"code={face['text_code_visual_ltr']}  cisi={face['source_cisi']}")
    width = max([code_im.width + 20, 900] + [sum(p.width for p in panels) + 20 * len(panels)])
    out = Image.new("RGB", (width, (height + 60 if panels else 0) + code_im.height + 60), "white")
    x = 10
    for p in panels:
        out.paste(p, (x, 10))
        x += p.width + 20
    y = (height + 60) if panels else 10
    d = ImageDraw.Draw(out)
    d.text((10, y), meta, font=label_font(22), fill="black")
    out.paste(code_im, (10, y + 36))
    dst = OUT / "composites" / f"{record_id}.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst)
    print(paths.rel(dst))


def glyphs(codes):
    ims = [glyph(c.zfill(3)) for c in codes]
    cols = 10
    w, h = ims[0].width, ims[0].height
    sheet = Image.new("RGB", (cols * w, ((len(ims) + cols - 1) // cols) * h), "white")
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * w, (k // cols) * h))
    dst = OUT / "glyph-sheets" / f"glyphs-{codes[0]}-{codes[-1]}-{len(codes)}.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dst)
    print(paths.rel(dst))


def blind(set_name: str, height=700):
    """Write one code-free image per item for Reader 2, named by a neutral item number."""
    data = load_crops()
    items = data["blind_sets"][set_name]
    dst_dir = OUT / "blind" / set_name
    dst_dir.mkdir(parents=True, exist_ok=True)
    key = {}
    for k, item in enumerate(items, start=1):
        panels = []
        for cid in item["crops"]:
            im = cut(data["crops"][cid])
            s = height / im.height
            panels.append(im.resize((max(1, int(im.width * s)), height)))
        out = Image.new("RGB", (sum(p.width for p in panels) + 20 * (len(panels) + 1), height + 20), "white")
        x = 20
        for p in panels:
            out.paste(p, (x, 10))
            x += p.width + 20
        name = f"item{k:02d}.png"
        out.save(dst_dir / name)
        key[name] = item["record_id"]
    (paths.RAW / "witness" / f"blind-key-{set_name}.json").write_text(json.dumps(key, indent=1) + "\n",
                                                                      encoding="utf-8")
    print(len(items), "items in", paths.rel(dst_dir))


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "grid":
        grid(Path(args[0]), Path(args[1]), *(int(a) for a in args[2:3]))
    elif cmd == "crops":
        crops()
    elif cmd == "composite":
        for r in args:
            composite(r)
    elif cmd == "glyphs":
        glyphs(args)
    elif cmd == "blind":
        blind(args[0])
    else:
        raise SystemExit("unknown command " + cmd)
