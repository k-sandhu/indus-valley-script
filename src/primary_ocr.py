"""Read-only primary scan index. OCR never substitutes for glyph verification.

Caches page text with source hashes and confidence, not a new authored PDF.
Use the source scan locally; its availability is not a redistribution license.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]


def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--pdf",required=True)
    ap.add_argument("--start",type=int,default=1)
    ap.add_argument("--end",type=int,required=True)
    ap.add_argument("--scale",type=int,default=2200)
    ap.add_argument("--out",default="research/primary_index/cisi1")
    args=ap.parse_args()
    pdf=(ROOT/args.pdf).resolve(); out=(ROOT/args.out).resolve()
    out.mkdir(parents=True,exist_ok=True)
    pages=out/"pages"; pages.mkdir(exist_ok=True)
    tmp=ROOT/"tmp"/"pdfs"/"ocr"; tmp.mkdir(parents=True,exist_ok=True)
    poppler=shutil.which("pdftoppm"); tess=shutil.which("tesseract")
    if not poppler or not tess: raise RuntimeError("Poppler and Tesseract required")
    provenance={"source_pdf":str(pdf),"source_sha256":sha256(pdf),
                "purpose":"Primary metadata locator; OCR output is unverified and cannot read Indus signs.",
                "generated_utc":datetime.now(timezone.utc).isoformat(),
                "parameters":vars(args),"poppler":poppler,"tesseract":tess,
                "source_redistribution":"No permission inferred from public availability."}
    (out/"provenance.json").write_text(json.dumps(provenance,indent=2),encoding="utf-8")
    env=os.environ.copy(); env["OMP_THREAD_LIMIT"]="1"
    started=time.monotonic(); count=0
    for p in range(args.start,args.end+1):
        dest=pages/f"page_{p:04d}.txt"
        if dest.exists(): continue
        prefix=tmp/f"page_{p:04d}"
        png=prefix.with_suffix(".png")
        render=subprocess.run([poppler,"-f",str(p),"-l",str(p),"-scale-to",str(args.scale),
                               "-singlefile","-png",str(pdf),str(prefix)],
                              capture_output=True,text=True,encoding="utf-8",errors="replace")
        if render.returncode:
            raise RuntimeError(f"Page {p} rendering failed: {render.stderr[:300]}")
        ocr=subprocess.run([tess,str(png),"stdout","-l","eng","--psm","3"],
                           capture_output=True,text=True,encoding="utf-8",errors="replace",env=env)
        if ocr.returncode:
            raise RuntimeError(f"Page {p} OCR failed: {ocr.stderr[:300]}")
        dest.write_text(ocr.stdout,encoding="utf-8")
        # Literal single-page intermediate, never a computed recursive directory delete.
        png.unlink(missing_ok=True)
        metadata={"pdf_page_one_based":p,"ocr_text_sha256":sha256(dest),
                  "heading_lines":ocr.stdout.splitlines()[:5],
                  "candidate_artifact_ids":sorted(set(re.findall(r"\b(?:M|H|L|K|C|B|A)[- ]\d{1,4}[A-Z]?\b",ocr.stdout))),
                  "ocr_warning":ocr.stderr.strip(),"completed_utc":datetime.now(timezone.utc).isoformat()}
        (pages/f"page_{p:04d}.json").write_text(json.dumps(metadata,indent=2),encoding="utf-8")
        count+=1
        if count%5==0:
            print(json.dumps({"stage":"primary_ocr","pdf_page":p,"new_pages":count,
                              "end":args.end,"elapsed_seconds":time.monotonic()-started}),flush=True)
    index={}
    for path in sorted(pages.glob("*.json")):
        md=json.loads(path.read_text(encoding="utf-8"))
        if not args.start <= md["pdf_page_one_based"] <= args.end:
            continue
        for aid in md["candidate_artifact_ids"]:
            aid=aid.replace(" ","-")
            index.setdefault(aid,[]).append(md["pdf_page_one_based"])
    (out/"artifact_locator_unverified.json").write_text(json.dumps(index,indent=2),encoding="utf-8")
    print(json.dumps({"completed":True,"new_pages":count,"seconds":time.monotonic()-started}),flush=True)


if __name__=="__main__": main()
