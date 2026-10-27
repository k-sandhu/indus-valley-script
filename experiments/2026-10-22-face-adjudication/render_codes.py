"""Render held catalogue-font codes after the visual pass has been sealed."""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "data/raw/2026-10-22-face-adjudication"
FONT = ROOT / "data/raw/2026-10-08-bonta-extension/source-2026-10-09/lipi-font-local.ttf"
FACES = ROOT / "data/normalized/lipi_observed_faces.jsonl"


def main():
    freeze = json.loads((ROOT / "experiments/2026-10-22-face-adjudication/VISUAL-PASS-1-FREEZE.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((ROOT / freeze["path"]).read_bytes()).hexdigest() == freeze["sha256"]
    manifest = json.loads((LOCAL / "neutral-manifest.json").read_text(encoding="utf-8"))
    faces = {r["record_id"]: r for r in map(json.loads, FACES.open(encoding="utf-8"))}
    out = LOCAL / "catalogue-codes"
    out.mkdir(exist_ok=False)
    font = ImageFont.truetype(str(FONT), 42)
    label = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
    codes = []
    for offset in range(0, len(manifest), 8):
        subset = manifest[offset:offset + 8]
        im = Image.new("RGB", (950, 175 * len(subset)), "white")
        draw = ImageDraw.Draw(im)
        for n, r in enumerate(subset):
            raw = faces[r["source_record_id"]]["text_code_visual_ltr"]
            segments = [re.findall(r"\d{3}", part) for part in raw.split("/")]
            draw.text((10, 175*n+5), r["review_id"] + " " + r["cisi"] + " — source visual LTR segments", font=label, fill="black")
            for j, seg in enumerate(segments):
                y = 175*n+32+j*46
                draw.text((10,y), str(j+1) + ": " + "-".join(seg), font=label, fill="black")
                for k, code in enumerate(seg):
                    glyph = chr(0xE000 + int(code))
                    draw.text((400+k*49, y-5), glyph, font=font, fill="black")
            codes.append({"review_id":r["review_id"],"face_id":r["face_id"],"raw_code":raw,"segments":segments,"direction":faces[r["source_record_id"]]["direction"]})
        im.save(out / f"sheet-{offset//8+1}.png")
    (out / "codes.json").write_text(json.dumps(codes,indent=2)+'\n',encoding="utf-8")
    record={"utc":datetime.now(timezone.utc).isoformat(),"phase":"catalogue-alignment-after-visual-freeze","source_path":FACES.relative_to(ROOT).as_posix(),"source_sha256":hashlib.sha256(FACES.read_bytes()).hexdigest(),"font_path":FONT.relative_to(ROOT).as_posix(),"font_sha256":hashlib.sha256(FONT.read_bytes()).hexdigest(),"transform":"U+E000 plus decimal code, as source glyphs.vue specifies; no source-image editing","visual_freeze_sha256":freeze["sha256"]}
    (out / "source-access.json").write_text(json.dumps(record,indent=2)+'\n',encoding="utf-8")
    print(json.dumps(record,indent=2))


if __name__ == "__main__":
    main()
