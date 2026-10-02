"""Provisional image-template extraction from the licensed 1979 plotted corpus.

Conventional OCR locates numerical labels only. Glyphs are matched as images.
All identities and row boundaries remain provisional until independently checked.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time

import cv2
import fitz
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import distance_transform_edt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"research/visual_digitization"
PDF=ROOT/"research/corpus/primary/koskenniemi_parpola1979.pdf"


def render(page):
    doc=fitz.open(PDF); pix=doc[page-1].get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY)
    return np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width).copy()


def mask(gray):
    return gray<190


def trim_x(binary):
    xx=np.flatnonzero(binary.sum(axis=0)>=2)
    if not len(xx):return None
    return binary[:,xx[0]:xx[-1]+1]


def row_centers(gray,x,count):
    """Track printed numerical baselines; scan spacing is not perfectly uniform."""
    profile=mask(gray[125:1560,x-51:x-21]).sum(axis=1).astype(float)
    smooth=gaussian_filter1d(profile,1.2)
    peaks,_=find_peaks(smooth,distance=7,prominence=.3)
    peaks=peaks+125
    output=[]
    for row in range(count):
        # Anchor every row to the page grid. Recursive tracking could lock
        # onto the upper rank and shift every later row in that column.
        expected=162.+40.25*row
        candidates=[int(y) for y in peaks if abs(y-expected)<=7]
        if candidates:
            y=max(candidates,key=lambda y:(smooth[y-125]*np.exp(-((y-expected)/10.)**2),y))
        else:y=round(expected)
        output.append(y-10)
    return output


def numeric_labels(cells):
    """Batch only the numerical patches into an ordinary OCR column."""
    results={}
    temp=OUT/"numeric_ocr";temp.mkdir(parents=True,exist_ok=True)
    for start in range(0,len(cells),80):
        chunk=cells[start:start+80]
        canvas=Image.new("L",(200,80*len(chunk)),255)
        for i,cell in enumerate(chunk):
            im=Image.fromarray(cell["number_patch"]).resize((120,56))
            canvas.paste(im,(40,i*80+12))
        path=temp/f"batch_{start:04d}.png";canvas.save(path)
        proc=subprocess.run(["tesseract",str(path),"stdout","--psm","6","-l","eng",
             "-c","tessedit_char_whitelist=0123456789","tsv"],capture_output=True,text=True,
             encoding="utf-8",errors="replace",check=True)
        (temp/f"batch_{start:04d}.tsv").write_text(proc.stdout,encoding="utf-8")
        for item in csv.DictReader(io.StringIO(proc.stdout),delimiter="\t"):
            value=item.get("text","").strip()
            if not value.isdigit():continue
            center=int(item["top"])+int(item["height"])/2
            index=int(center//80)
            if not 0<=index<len(chunk):continue
            key=chunk[index]["key"]
            candidate={"value":value,"confidence":float(item["conf"])}
            if key not in results or candidate["confidence"]>results[key]["confidence"]:
                results[key]=candidate
    return results


def templates():
    cells=[]; images={}
    # Grid is a source-specific extraction aid, recorded and visually auditable.
    for page,x0,count in [(20,176.,35),(21,153.,35)]:
        gray=render(page);Image.fromarray(gray).save(OUT/f"page_{page}.png")
        for col in range(10):
            x=round(x0+100.4*col)
            centers=row_centers(gray,x,count)
            for row,y in enumerate(centers):
                if page==21 and col==9 and row>=22:continue
                key=f"{page}:{col}:{row}"
                binary=trim_x(mask(gray[y-19:y+20,x-20:x+24]))
                if binary is None:continue
                # Extract lower code and upper rank as separate text-only patches.
                # Separate the two numerical baselines before OCR. A blank
                # scan row must not be bridged into a rank/code combination.
                patch=gray[y-15:y+23,x-51:x-21]
                projected=mask(patch).any(axis=1)
                edges=np.diff(np.r_[False,projected,False].astype(int))
                bands=[(a,b) for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)) if b-a>=5]
                if bands:
                    a,b=max(bands,key=lambda ab:ab[1])
                    code_patch=np.full((18,30),255,dtype=np.uint8)
                    body=patch[a:b]
                    if body.shape[0]<=18:
                        top=(18-body.shape[0])//2;code_patch[top:top+body.shape[0]]=body
                        if not(page==21 and col==9 and row==20):
                            cells.append({"key":key+":code","number_patch":code_patch})
                cells.append({"key":key+":rank","number_patch":gray[y-12:y+4,x-51:x-21]})
                images[key]={"key":key,"pdf_page":page,"column":col,"grid_row":row,
                             "crop_xyxy_2x":[x-20,y-19,x+24,y+20],"binary":binary}
    labels=numeric_labels(cells)
    out=[];template_dir=OUT/"templates";template_dir.mkdir(exist_ok=True)
    for key,item in images.items():
        code=labels.get(key+":code",{});rank=labels.get(key+":rank",{})
        binary=item.pop("binary")
        png=template_dir/(key.replace(":","_")+".png")
        Image.fromarray(np.where(binary,0,255).astype(np.uint8)).save(png)
        item.update({"code_ocr":code,"rank_ocr":rank,"image_path":str(png.relative_to(ROOT)),
                     "glyph_height_pixels":int(np.count_nonzero(binary.any(axis=1))),
                     "glyph_width_pixels":binary.shape[1],
                     "label_status":"UNVERIFIED numerical OCR; no canonical transcription"})
        out.append(item)
    bycode={}
    for item in out:
        if item["code_ocr"].get("value"):
            bycode.setdefault(item["code_ocr"]["value"],[]).append(item["key"])
    (OUT/"template_manifest_unverified.json").write_text(json.dumps({
        "source_pdf_sha256":hashlib.sha256(PDF.read_bytes()).hexdigest(),
        "source_license":"CC BY4.0 per institutional entry; attribute Koskenniemi and Parpola1979",
        "scope":"Numerical labels and glyph crops are provisional; upper number is rank, lower is code.",
        "templates":out,"duplicate_ocr_codes":{k:v for k,v in bycode.items() if len(v)>1}},indent=2),encoding="utf-8")
    print(json.dumps({"templates":len(out),"labelled":sum(bool(x["code_ocr"]) for x in out),
                      "duplicate_codes":sum(len(v)>1 for v in bycode.values())}),flush=True)


def load_templates():
    manifest=json.loads((OUT/"template_manifest_unverified.json").read_text(encoding="utf-8"))
    output=[]
    for item in manifest["templates"]:
        b=np.asarray(Image.open(ROOT/item["image_path"]).convert("L"))<190
        output.append(dict(item,binary=b))
    return output


def comparable(a,b,dy):
    h=max(a.shape[0],b.shape[0])+12;w=max(a.shape[1],b.shape[1])+8
    aa=np.zeros((h,w),bool);bb=np.zeros((h,w),bool)
    ax=(w-a.shape[1])//2;bx=(w-b.shape[1])//2
    aa[6:6+a.shape[0],ax:ax+a.shape[1]]=a
    bb[6+dy:6+dy+b.shape[0],bx:bx+b.shape[1]]=b
    return aa,bb


def match(binary,library):
    choices=[]
    for template in library:
        b=template["binary"]
        if abs(binary.shape[1]-b.shape[1])>max(4,.25*b.shape[1]):continue
        best=float("inf")
        for dy in [-3,0,3]:
            a1,b1=comparable(binary,b,dy)
            if not a1.any() or not b1.any():continue
            da=distance_transform_edt(~a1);db=distance_transform_edt(~b1)
            d=(float(db[a1].mean())+float(da[b1].mean()))/2
            # Preserve widths and graphic height; no context or proposed meaning.
            d+=.035*abs(binary.shape[1]-b.shape[1])
            best=min(best,d)
        value=template["code_ocr"].get("value")
        choices.append({"template_key":template["key"],"code_ocr":value.zfill(3) if value else None,
                        "rank_ocr":template["rank_ocr"].get("value"),"distance_pixels":best})
    return sorted(choices,key=lambda x:(x["distance_pixels"],x["template_key"]))[:5]


def segment(strip,library):
    binary=mask(strip); projected=binary.sum(axis=0)>=2
    edges=np.diff(np.r_[False,projected,False].astype(int))
    components=list(zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1)))
    n=len(components); costs=[float("inf")]*(n+1);paths=[None]*(n+1);costs[0]=0.;paths[0]=[]
    for i in range(n):
        if paths[i] is None:continue
        for j in range(i,min(n,i+12)):
            x0=components[i][0];x1=components[j][1]
            if x1-x0>65:break
            if j>i and components[j][0]-components[j-1][1]>20:break
            b=binary[:,x0:x1];alternatives=match(b,library)
            if not alternatives:continue
            score=alternatives[0]["distance_pixels"]*float(b.sum())/100+.15
            if costs[i]+score<costs[j+1]:
                costs[j+1]=costs[i]+score
                paths[j+1]=paths[i]+[{"x_bounds":[int(x0),int(x1)],"alternatives":alternatives,
                                    "distance_pixels":alternatives[0]["distance_pixels"]}]
        # Always retain unmatched ink rather than silently dropping a component.
        if costs[i]+30<costs[i+1]:
            costs[i+1]=costs[i]+30
            paths[i+1]=paths[i]+[{"x_bounds":list(map(int,components[i])),"alternatives":[],
                                 "status":"UNMATCHED"}]
    return paths[n],float(costs[n])


def corpus_page(page=30,rows=10):
    gray=render(page);library=load_templates();result=[];start=time.monotonic()
    crops=OUT/"row_candidates";crops.mkdir(exist_ok=True)
    # Prototype page30's consecutive row IDs and geometry were directly inspected.
    if page!=30:raise ValueError("Only directly inspected page30 geometry is currently supported")
    for col,(x0,x1,id0) in enumerate([(150,512,1015),(680,1036,1051)]):
        for r in range(rows):
            y=round(155.+40.25*r)
            strip=gray[y-19:y+20,x0:x1]
            tokens,cost=segment(strip,library)
            ident=str(id0+r); path=crops/f"row_{ident}.png"
            im=Image.fromarray(strip).convert("RGB");draw=ImageDraw.Draw(im)
            for t in tokens:
                a,b=t["x_bounds"];draw.rectangle((a,0,b-1,38),outline="red")
            im.resize((im.width*3,im.height*3)).save(path)
            result.append({"printed_id_visual_check":ident,"pdf_page":page,"column":col,
                "crop_xyxy_2x":[x0,y-19,x1,y+20],"tokens_visual_ltr":tokens,"path_cost":cost,
                "status":"PROVISIONAL; numerical template labels, segmentation, side boundaries and graphic identities unverified",
                "boundary_warning":"A plotted row may contain several original lines/sides. Do not treat this as a single original text."})
            print(json.dumps({"id":ident,"tokens":len(tokens),"cost":cost,
                              "seconds":time.monotonic()-start}),flush=True)
    (OUT/"page30_candidates_unverified.json").write_text(json.dumps(result,indent=2),encoding="utf-8")


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    ap=argparse.ArgumentParser();ap.add_argument("mode",choices=["templates","page"])
    ap.add_argument("--rows",type=int,default=10);args=ap.parse_args()
    templates() if args.mode=="templates" else corpus_page(rows=args.rows)


if __name__=="__main__":main()
