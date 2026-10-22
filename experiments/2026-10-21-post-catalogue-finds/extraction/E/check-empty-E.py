"""Check whether empty OCR pages contain any rendered ink, without viewing them."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pdf",type=Path)
    ap.add_argument("raw",type=Path)
    ap.add_argument("output",type=Path)
    args=ap.parse_args()
    records=[]
    for n in [2,6,224,337]:
        with tempfile.TemporaryDirectory(prefix=f"empty-{n:04d}-",dir=args.raw/"temporary") as td:
            base=Path(td)/"page"
            subprocess.run(["pdftoppm","-f",str(n),"-l",str(n),"-singlefile","-r","100","-gray",
                            str(args.pdf),str(base)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            path=base.with_suffix(".pgm")
            with path.open("rb") as f:
                assert f.readline().strip()==b"P5"
                line=f.readline()
                while line.startswith(b"#"):
                    line=f.readline()
                width,height=map(int,line.split())
                assert f.readline().strip()==b"255"
                pixels=f.read()
            path.unlink()
        dark=sum(v<240 for v in pixels)
        records.append(dict(pdf_page=n,width=width,height=height,nonwhite_pixels=dark,
                            text_file_bytes=(args.raw/"text"/"iar-1996-97-archive"/f"p{n:04d}.txt").stat().st_size,
                            blank_render=dark==0))
    (args.output/"empty-pages-E.json").write_text(json.dumps(records,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(records,indent=2))


if __name__=="__main__":
    main()
