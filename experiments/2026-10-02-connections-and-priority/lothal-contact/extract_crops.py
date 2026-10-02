"""Extract unchanged source pixel rectangles; no resampling or enhancement."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RAW = ROOT / "data/raw/2026-10-02-connections-and-priority/lothal-contact"
RAW.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / "data/six-hour/lothal/independent-review"
SPEC = [
    ("L206-profile",36,[440,730,960,1280],"L206","contact", "Figure3 top row left"),
    ("L206-rear",36,[1480,750,2010,1230],"L206","contact", "Figure3 top row right"),
    ("L190-contact",37,[690,1410,980,1800],"L190","contact", "Figure4 second row, second view"),
    ("L190-profile",37,[990,1410,1240,1800],"L190","contact", "Figure4 second row, third view"),
    ("L190-end",37,[1630,1410,1940,1790],"L190","contact", "Figure4 second row, fifth view"),
    ("L193-profile",38,[350,730,730,1000],"L193","contact", "Figure5 upper-left group, top-left view"),
    ("L193-rear",38,[740,730,1160,1000],"L193","contact", "Figure5 upper-left group, top-right view"),
    ("L193-stamp",38,[350,1000,740,1310],"L193","stamp", "Figure5 upper-left group, lower-left view"),
    ("L124-rear",40,[830,740,1170,1070],"L124","contact", "Figure7 top-left group, right view"),
    ("L126-rear",40,[1610,770,1940,1050],"L126","contact", "Figure7 top-right group, right view"),
    ("L161-group",39,[2250,530,2970,940],"L161","all_views", "Figure6 upper-right group, both views"),
    ("L161-cut-zone",39,[2280,535,2500,710],"L161","cuts", "Figure6 upper-right group, left view top margin"),
    ("L165-group",39,[690,540,1590,1240],"L165","all_views", "Figure6 left group, three views"),
    ("L165-side",39,[1110,960,1590,1240],"L165","contact", "Figure6 left group, lower-right side view"),
    ("L168-group",39,[1630,960,2040,1500],"L168","all_views", "Figure6 centre group, two views"),
    ("L168-cut-zone",39,[1880,990,2030,1250],"L168","cuts", "Figure6 centre group, upper view right margin"),
    ("L163-group",39,[700,1380,1460,1880],"L163","all_views", "Figure6 lower-left group, four views"),
    ("L163-side",39,[700,1690,1070,1880],"L163","cuts", "Figure6 lower-left group, lower-left side view"),
    ("L163-rear",39,[1100,1690,1460,1880],"L163","contact", "Figure6 lower-left group, lower-right rear view"),
    ("L162-group",39,[1530,1560,2150,1880],"L162","all_views", "Figure6 lower-centre group, both views"),
    ("L162-left",39,[1530,1560,1820,1880],"L162","cuts", "Figure6 lower-centre group, left view"),
]
records = []
for name,page,box,obj,purpose,panel in SPEC:
    src = SOURCE / f"figure-native-pdf{page}.png"
    im = Image.open(src)
    assert 0 <= box[0] < box[2] <= im.width
    assert 0 <= box[1] < box[3] <= im.height
    out = RAW / f"{name}.png"
    im.crop(box).save(out)
    records.append({"crop_id":name,"object_id":obj,"purpose":purpose,"panel":panel,
        "pdf_page_one_based":page,"printed_page":page+62,"figure":page-33,
        "source_path":src.relative_to(ROOT).as_posix(),
        "source_sha256":hashlib.sha256(src.read_bytes()).hexdigest(),
        "box_xyxy_source_pixels":box,"path":out.relative_to(ROOT).as_posix(),
        "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
        "size":list(Image.open(out).size),
        "method":"Unchanged source pixel rectangle; no scaling, tone change or annotation",
        "stamp_exclusion":"Separate contact-only rectangle where practical; full-group crop retains stamp for source linkage",
        "rights_status":"rights-unverified; local-only"})
(HERE / "crop-manifest.json").write_text(json.dumps({
    "protocol_sha256":hashlib.sha256((HERE/"PROTOCOL.md").read_bytes()).hexdigest(),
    "crops":records},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"crops":len(records),"source_images":len(set(r['source_path'] for r in records))}))
