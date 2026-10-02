from pathlib import Path
from PIL import Image
import json, hashlib, datetime

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'data/raw/2026-10-02-connections-and-priority/harappa-short-records/witness-crops'
OUT.mkdir(parents=True, exist_ok=True)
parent = ROOT / 'research/corpus/plate_audit/H2238_gallery/harappa_three_groups.jpg'
im = Image.open(parent)
items = []
for name, box in [('group2-middle', (310,210,525,350)), ('group1-middle', (10,185,208,325)), ('group3-bottom', (605,347,796,490))]:
    p = OUT / (name+'.png')
    if p.exists():
        raise FileExistsError(p)
    im.crop(box).save(p)
    items.append({'witness':name,'parent_path':str(parent.relative_to(ROOT)).replace('\\','/'),'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'crop_path':str(p.relative_to(ROOT)).replace('\\','/'),'bounds_xyxy':box,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'operation':'rectangular crop without resampling or retouching'})
(OUT/'manifest.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'crops':items},indent=2)+'\n',encoding='utf-8')
