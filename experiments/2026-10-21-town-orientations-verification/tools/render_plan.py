"""Render a PDF page or image region with a reversible labelled pixel grid."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse
import fitz
import numpy as np
from PIL import Image,ImageDraw
from common import sha256,write_json,check_space

def page_image(source,page=1,dpi=300,region=None):
    """Return RGB image and mapping from image pixel centres to source coordinates.

    PDF source coordinates are unrotated MuPDF page points, x right and y down.
    Raster source coordinates are pixel centres; dpi scales a 72 dpi source.
    """
    if Path(source).suffix.lower()==".pdf":
        with fitz.open(source) as doc:
            pg=doc[page-1]
            if pg.rotation:
                raise ValueError("PDF page rotation must be zero; export an unrotated image explicitly")
            rect=fitz.Rect(region) if region else pg.rect
            pix=pg.get_pixmap(dpi=dpi,clip=rect,alpha=False)
            im=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
            scale=dpi/72
            m=[[1/scale,0,(pix.x+.5)/scale],[0,1/scale,(pix.y+.5)/scale],[0,0,1]]
    else:
        im=Image.open(source).convert("RGB")
        box=region or [0,0,im.width,im.height]
        im=im.crop(tuple(map(int,box)));scale=dpi/72
        im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
        m=[[1/scale,0,box[0]+.5/scale-.5],[0,1/scale,box[1]+.5/scale-.5],[0,0,1]]
    return im,np.asarray(m)

def render(source,output,page=1,dpi=300,region=None,grid=200):
    if Path(output).exists() or Path(str(output)+".json").exists():raise FileExistsError(output)
    im,m=page_image(source,page,dpi,region)
    if grid:
        draw=ImageDraw.Draw(im)
        for x in range(0,im.width,grid):
            draw.line([(x,0),(x,im.height)],fill=(80,160,220),width=1);draw.text((x+3,3),str(x),fill="blue",stroke_width=1,stroke_fill="white")
        for y in range(0,im.height,grid):
            draw.line([(0,y),(im.width,y)],fill=(80,160,220),width=1);draw.text((3,y+3),str(y),fill="blue",stroke_width=1,stroke_fill="white")
    check_space(output,im.width*im.height*4+10000)
    Path(output).parent.mkdir(parents=True,exist_ok=True);im.save(output)
    side=dict(schema_version=1,kind="plan",source=str(Path(source).resolve()),source_sha256=sha256(source),png_sha256=sha256(output),page=page,dpi=dpi,region=region,pixel_to_source=m.tolist(),pixel_convention="integer coordinates are pixel centres",source_units="PDF points" if Path(source).suffix.lower()==".pdf" else "source pixel centres")
    write_json(str(output)+".json",side);return side

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("source");p.add_argument("output");p.add_argument("--page",type=int,default=1);p.add_argument("--dpi",type=int,default=300);p.add_argument("--region",type=float,nargs=4);p.add_argument("--grid",type=int,default=200);a=p.parse_args();render(a.source,a.output,a.page,a.dpi,a.region,a.grid)
if __name__=="__main__":main()
