"""Additional unchanged rectangles for boundary/cut inspection."""
import hashlib
import json
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-02-connections-and-priority/lothal-contact"
SRC = ROOT / "data/six-hour/lothal/independent-review/figure-native-pdf39.png"
spec = [
    ("L165-right-margin", "L165", [925,800,1100,1050], "Figure6 left group, first view right margin"),
    ("L161-upper-margin", "L161", [2280,535,2570,725], "Figure6 upper-right group, left view upper margin"),
    ("L162-upper-margin", "L162", [1550,1570,1740,1720], "Figure6 lower-centre group, left view upper margin"),
]
im = Image.open(SRC)
rows = []
for name,obj,box,panel in spec:
    out = RAW / f"{name}.png"
    im.crop(box).save(out)
    rows.append({"crop_id":name,"object_id":obj,"purpose":"cuts","panel":panel,
        "pdf_page_one_based":39,"printed_page":101,"figure":6,
        "source_path":SRC.relative_to(ROOT).as_posix(),
        "source_sha256":hashlib.sha256(SRC.read_bytes()).hexdigest(),
        "box_xyxy_source_pixels":box,"path":out.relative_to(ROOT).as_posix(),
        "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "size":list(Image.open(out).size),
        "method":"Unchanged source pixel rectangle; no scaling, tone change or annotation",
        "rights_status":"rights-unverified; local-only"})
(HERE/"additional-crop-manifest.json").write_text(json.dumps({
    "basis":"First crops showed marginal cut groups requiring a wider or isolated rectangle; no prediction changed.",
    "protocol_sha256":hashlib.sha256((HERE/"PROTOCOL.md").read_bytes()).hexdigest(),
    "crops":rows},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"additional_crops":len(rows)}))
