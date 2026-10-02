"""Deterministic chart-label sample; no OCR or project template input is read."""
from pathlib import Path
import hashlib
import json
import random
import fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).parent
SOURCE=ROOT.parents[2]/"research/corpus/primary/koskenniemi_parpola1979.pdf"
doc=fitz.open(SOURCE)
rng=random.Random(20261002)
sample=[]
for page in (20,21):
    eligible=[(c,r) for c in range(1,10) for r in range(35)] if page==20 else [(c,r) for c in range(10) for r in range(35) if c<9 or r<22]
    chosen=rng.sample(eligible,15)
    chosen.sort()
    for c,r in chosen:
        # Broad original-PDF crop includes both labels and associated glyph for locator context.
        # Geometry was calibrated visually on the unprocessed original PDF page.
        left=(62 if page==20 else 47)+49.5*c
        top=65+20.05*r
        rect=fitz.Rect(left-3,top-1,left+48,top+23)
        target=ROOT/f"pdf{page:02d}_c{c:02d}_r{r:02d}.png"
        doc[page-1].get_pixmap(matrix=fitz.Matrix(8,8),clip=rect).save(target)
        sample.append({"pdf_page":page,"printed_page":page-1,"column_0based":c,"row_0based":r,"clip_points":list(rect),"image":target.name})
    sheet=Image.new("RGB",(1530,1200),"white")
    draw=ImageDraw.Draw(sheet)
    for j,(c,r) in enumerate(chosen):
        x=(j%3)*510; y=(j//3)*240
        draw.text((x+10,y+8),f"PDF{page} COLUMN {c} ROW {r}",fill="black",stroke_width=0)
        im=Image.open(ROOT/f"pdf{page:02d}_c{c:02d}_r{r:02d}.png").convert("RGB")
        sheet.paste(im,(x+10,y+35))
    sheet.save(ROOT/f"sample_sheet_pdf{page:02d}.png")
manifest={"source":str(SOURCE.resolve()),"source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),"seed":20261002,
          "rng":"Python random.Random, one generator used sequentially for PDF20 then PDF21",
          "eligible_order":"column-major then row-major, zero-based",
          "grid":"10 columns,35 row levels each; PDF21 column9 occupied rows0–21 only",
          "pdf20_exclusion":"column0 excluded because independently audited by corpus agent",
          "pdf21_rank400":"column9,row20 occupied but no visible lower code; retained in sampling frame",
          "sample":sample}
(ROOT/"sampling_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(json.dumps(sample,indent=2))
