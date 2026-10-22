"""Recover footer labels without retaining page renders."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf",type=Path)
    ap.add_argument("raw",type=Path)
    args=ap.parse_args()
    env=os.environ.copy()
    env["OMP_THREAD_LIMIT"]="1"
    exe=r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    def page(n):
        recpath=args.raw/"processing"/f"p{n:04d}.json"
        meta=json.loads(recpath.read_text(encoding="utf-8"))
        bottom=[r for r in meta["edge_numbers"] if r["top"]>2800]
        if len(bottom)==1 and bottom[0]["value"]==str(n-8):
            return n,dict(printed_page=str(n-8),basis="full-page footer OCR")
        with tempfile.TemporaryDirectory(prefix=f"footer-{n:04d}-",dir=args.raw/"temporary") as td:
            image=Path(td)/"footer"
            subprocess.run(["pdftoppm","-f",str(n),"-l",str(n),"-singlefile","-r","300","-gray","-png",
                            "-x","0","-y","2930","-W","2550","-H","150",str(args.pdf),str(image)],
                            check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            try:
                result=subprocess.run([exe,str(image.with_suffix(".png")),"stdout","-l","eng","--psm","7",
                                       "-c","tessedit_char_whitelist=0123456789"],env=env,check=True,
                                      stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            finally:
                image.with_suffix(".png").unlink(missing_ok=True)
        value=result.stdout.strip()
        if value==str(n-8):
            return n,dict(printed_page=value,basis="footer-only OCR")
        return n,dict(printed_page="",basis="no confirmed running-head or footer label")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        result=dict(pool.map(page,range(9,338)))
    (args.raw/"footer-labels.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(confirmed_footer_labels=sum(bool(r["printed_page"]) for r in result.values()))))


if __name__=="__main__":
    main()
