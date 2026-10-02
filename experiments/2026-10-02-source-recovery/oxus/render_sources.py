"""Recover the observed native images and faithful crops without replacing witnesses."""
from pathlib import Path
import hashlib, json
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
RAW=ROOT/"data/raw/2026-10-02-source-recovery/oxus"
records=[]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def save(data,name,parent,method,**details):
    path=RAW/name
    if path.exists():
        assert digest(path.read_bytes())==digest(data), f"Existing witness differs: {path}"
    else:
        path.write_bytes(data)
    records.append({"path":path.relative_to(ROOT).as_posix(),"parent":parent.relative_to(ROOT).as_posix(),"parent_sha256":digest(parent.read_bytes()),"sha256":digest(data),"bytes":len(data),"transformation":method,**details})

sarianidi=RAW/"sarianidi1998.pdf"
doc=fitz.open(sarianidi)
for index in [3,7,*range(59,100),188,189,190]:
    image=doc[index].get_images(full=True)[0]
    block=doc.extract_image(image[0])
    save(block['image'],f"sarianidi-native-pdf{index+1:03}.png",sarianidi,"native embedded image extraction; no resampling",pdf_page_1_based=index+1,xref=image[0],width=block['width'],height=block['height'])

page=RAW/"sarianidi-native-pdf087.png"
im=Image.open(page)
from io import BytesIO
for name,bounds in [("gonur-fig41-photo-panel.png",(46,108,767,568)),("gonur-fig41-drawing-panel.png",(46,568,767,850))]:
    buf=BytesIO();im.crop(bounds).save(buf,format="PNG")
    save(buf.getvalue(),name,page,"unchanged rectangular pixel crop",crop_bounds_xyxy=list(bounds))

kircho=RAW/"kircho2008.pdf";doc=fitz.open(kircho)
for name,index,matrix,clip in [
    ("kircho-plate94-pdf272.png",271,2,None),
    ("kircho-plate94-2-crop.png",271,5,[112,32,262,96]),
    ("kircho-context-pdf049.png",48,2,None),
    ("kircho-sealings-pdf105.png",104,2,None),
]:
    pix=doc[index].get_pixmap(matrix=fitz.Matrix(matrix,matrix),clip=fitz.Rect(clip) if clip else None)
    save(pix.tobytes("png"),name,kircho,"PyMuPDF unchanged page render",pdf_page_1_based=index+1,pdf_crop_bounds_xyxy=clip,render_scale=matrix,width=pix.width,height=pix.height)

later=RAW/"sarianidi2005.pdf";doc=fitz.open(later)
pix=doc[129].get_pixmap(matrix=fitz.Matrix(1.5,1.5))
save(pix.tobytes("png"),"sarianidi2005-fig114-pdf130.png",later,"PyMuPDF unchanged page-spread render",pdf_page_1_based=130,render_scale=1.5,width=pix.width,height=pix.height)

manifest=OUT/"derived-image-manifest.json"
payload=json.dumps({"images":records},indent=2,ensure_ascii=False)+"\n"
if manifest.exists():
    assert manifest.read_text(encoding="utf-8")==payload, "Existing manifest differs; use a new endpoint."
else:
    manifest.write_text(payload,encoding="utf-8")
print(f"Verified/saved {len(records)} image witnesses.")
