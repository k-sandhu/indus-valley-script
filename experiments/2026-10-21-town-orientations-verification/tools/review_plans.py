"""Low-resolution plan contact sheets with guarded page selection and safe text."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,re,io
import fitz
from PIL import Image,ImageDraw
from common import read_json,check_space
from plan_support import guard
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('input');ap.add_argument('output');a=ap.parse_args()
    rows=read_json(a.input);tiles=[]
    for row in rows:
        path=row['source'];guard(path)
        with fitz.open(path) as doc:
            for n in row['pages']:
                guard(path,n);pg=doc[n-1];pix=pg.get_pixmap(dpi=65,alpha=False)
                im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.thumbnail((580,740))
                tile=Image.new('RGB',(600,780),'white');tile.paste(im,(10,30));ImageDraw.Draw(tile).text((10,5),row['id']+' PDF '+str(n),fill='red');tiles.append(tile)
                safe=[x for x in pg.get_text().splitlines() if not re.search(r'orient|\d\s*[°º]|\d\s*deg',x,re.I)]
                print(row['id'],n,'PAGECOUNT',len(doc),'TEXT',' | '.join(safe)[-1900:])
    cols=min(3,len(tiles));sheet=Image.new('RGB',(cols*600,780*((len(tiles)+cols-1)//cols)),(205,205,205))
    for j,t in enumerate(tiles):sheet.paste(t,((j%cols)*600,(j//cols)*780))
    buf=io.BytesIO();sheet.save(buf,format='PNG');payload=buf.getvalue()
    check_space(a.output,len(payload))
    Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_bytes(payload)
if __name__=='__main__':main()
