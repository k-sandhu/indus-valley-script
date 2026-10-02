"""Render primary-source glyph comparisons without imposing a sign merger."""
from pathlib import Path
import datetime, hashlib, json
import requests
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "renders"
OUT.mkdir(exist_ok=True)
source = ROOT / "sources/joshi_parpola_1987_cisi1.pdf"
doc = fitz.open(source)
# Coordinates are fractions of the PDF page; photographs only, labels retained
# separately in the manifest. A 'bis' view is the same object, never another token.
items = [
 ("M599B",187,(.51,.195,.88,.31)),
 ("M600B",187,(.51,.34,.72,.445)),
 ("M601B",187,(.52,.5,.88,.595)),
 ("M602B",187,(.52,.64,.89,.74)),
 ("M603B",187,(.53,.79,.88,.91)),
 ("M604B",188,(.54,.045,.90,.17)),
 ("M604B_bis",188,(.54,.185,.90,.295)),
]
manifest=[]
for key,pageno,box in items:
 page=doc[pageno-1]
 width,height=page.rect.width,page.rect.height
 clip=fitz.Rect(box[0]*width,box[1]*height,box[2]*width,box[3]*height)
 path=OUT/(key+"_primary_crop.png")
 page.get_pixmap(matrix=fitz.Matrix(4,4),clip=clip).save(path)
 manifest.append(dict(object_surface=key,pdf_page=pageno,printed_page=pageno-36,normalized_box=box,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),file=str(path.relative_to(ROOT))))
url="https://www.harappa.com/sites/default/files/essays/mahfig4.gif"
response=requests.get(url,timeout=45)
response.raise_for_status()
rawpath=ROOT/"sources/mahadevan_parpola_review_fig4.gif"
rawpath.write_bytes(response.content)
Image.open(rawpath).convert("RGB").save(OUT/"mahadevan_parpola_review_fig4.png")
manifest.append(dict(figure="Mahadevan review Fig4",url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(response.content).hexdigest()))
(ROOT/"copper_variant_image_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print("Rendered",len(items),"object-surface views plus review glyph chart")
