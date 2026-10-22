"""Retry only the nonblank page whose first OCR pass returned no text."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf",type=Path)
    ap.add_argument("raw",type=Path)
    ap.add_argument("output",type=Path)
    args=ap.parse_args()
    text=args.raw/"text"/"iar-1996-97-archive"/"p0224.txt"
    assert text.stat().st_size==0
    env=os.environ.copy()
    env["OMP_THREAD_LIMIT"]="1"
    with tempfile.TemporaryDirectory(prefix="recover-0224-",dir=args.raw/"temporary") as td:
        image=Path(td)/"page"
        subprocess.run(["pdftoppm","-f","224","-l","224","-singlefile","-r","300","-gray","-png",
                        str(args.pdf),str(image)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            result=subprocess.run([r"C:\Program Files\Tesseract-OCR\tesseract.exe",str(image.with_suffix(".png")),
                                   "stdout","-l","eng","--dpi","300","--psm","11"],
                                   env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        finally:
            image.with_suffix(".png").unlink(missing_ok=True)
    text.write_bytes(result.stdout)
    path=args.raw/"processing"/"p0224.json"
    meta=json.loads(path.read_text(encoding="utf-8"))
    meta["initial_text_sha256"]=meta["text_sha256"]
    meta["text_sha256"]=hashlib.sha256(result.stdout).hexdigest()
    meta["fallback"]="sparse English OCR, psm 11; initial nonblank page had empty text"
    path.write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    record=dict(pdf_page=224,initial_bytes=0,recovered_bytes=len(result.stdout),
                reason="Empty OCR output on a nonblank rendered page",fallback="English psm 11",
                render_retained=False,image_viewed=False)
    (args.output/"ocr-recovery-E.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record))


if __name__=="__main__":
    main()
