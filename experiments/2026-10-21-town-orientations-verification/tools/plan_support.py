"""Inspect selected plan pages without opening excluded chapters or studies.

The scan command reports page counts and candidate caption lines only. Numerical
orientation sentences are suppressed and their page locations recorded alone.
"""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import argparse,re,shutil,subprocess,concurrent.futures
import fitz
from PIL import Image,ImageDraw
from common import write_json,record

def guard(path,page=None):
    s=str(Path(path).resolve()).replace('\\','/').lower()
    if '/2026-10-21-town-axes/' in s:raise ValueError('excluded study')
    if 'jansen_urban1987_interim2_govscan_77275' in s and page is not None and 36<=page<=47:raise ValueError('excluded PDF pages')

def scan(path,output,limit=0):
    guard(path);candidates=[];encounters=[]
    with fitz.open(path) as d:
        for i,pg in enumerate(d):
            n=i+1
            if 'jansen_urban1987_interim2_govscan_77275' in str(path) and 36<=n<=47:continue
            if limit and n>limit:break
            lines=pg.get_text().splitlines()
            for line in lines:
                if re.search(r'orient|\b[0-9]+\s*[°º]|\b[0-9]+\s*deg',line,re.I):encounters.append(n);continue
                if re.search(r'\bplan\b|ground.plan|site.map',line,re.I):candidates.append(dict(pdf_page=n,line=line))
        result=dict(source=str(path),page_count=len(d),candidate_lines=candidates,orientation_text_encounter_pages=sorted(set(encounters)))
    write_json(output,result)
    print('pages',result['page_count'],'candidates',len(candidates),'suppressed encounter pages',len(set(encounters)))
    for c in candidates[:120]:print(c['pdf_page'],c['line'])

def contact(path,pages,output,dpi=50):
    guard(path);tiles=[]
    with fitz.open(path) as d:
        for n in pages:
            guard(path,n);pix=d[n-1].get_pixmap(dpi=dpi,alpha=False)
            im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples);im.thumbnail((430,520))
            tile=Image.new('RGB',(450,550),'white');tile.paste(im,(10,25));ImageDraw.Draw(tile).text((10,5),f'PDF page {n}',fill='red');tiles.append(tile)
    sheet=Image.new('RGB',(450*min(4,len(tiles)),550*((len(tiles)+3)//4)),(210,210,210))
    for i,t in enumerate(tiles):sheet.paste(t,((i%4)*450,(i//4)*550))
    Path(output).parent.mkdir(parents=True,exist_ok=True);sheet.save(output)

def ocr(path,pages,output,dpi=110):
    guard(path)
    def one(n):
        guard(path,n)
        with fitz.open(path) as d:pix=d[n-1].get_pixmap(dpi=dpi,alpha=False)
        proc=subprocess.run(['C:/Program Files/Tesseract-OCR/tesseract.exe','stdin','stdout','--psm','3'],input=pix.tobytes('png'),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
        text=proc.stdout.decode('utf-8');lines=[];encounter=False
        for line in text.splitlines():
            if re.search(r'orient|\d\s*[°º]|\d\s*deg',line,re.I):encounter=True;continue
            lines.append(line)
        return dict(pdf_page=n,text='\n'.join(lines),stated_orientation_text_suppressed=encounter)
    with concurrent.futures.ThreadPoolExecutor(4) as pool:rows=list(pool.map(one,pages))
    write_json(output,dict(source=str(path),pages=rows))
    for row in rows:print('PDF PAGE',row['pdf_page']);print(row['text'])

def north_labels(path,pages,output,fraction,save_crop=False):
    """Read north words at four image rotations; never extract numeric angles."""
    import io
    rows=[]
    with fitz.open(path) as d:
        for n in pages:
            guard(path,n);pg=d[n-1];w,h=pg.rect.width,pg.rect.height
            clip=fitz.Rect(fraction[0]*w,fraction[1]*h,fraction[2]*w,fraction[3]*h)
            pix=pg.get_pixmap(dpi=240,clip=clip,alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            if save_crop:
                crop=Path(output).with_name(Path(output).stem+f'-page-{n}.png')
                if crop.exists():raise FileExistsError(crop)
                im.save(crop)
            for angle in [0,90,180,270]:
                buf=io.BytesIO();im.rotate(angle,expand=True).save(buf,format='PNG')
                proc=subprocess.run(['C:/Program Files/Tesseract-OCR/tesseract.exe','stdin','stdout','--psm','11'],input=buf.getvalue(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
                text=proc.stdout.decode('utf-8');labels=[]
                for line in text.splitlines():
                    if re.search(r'\bnorth\b',line,re.I):labels.append(re.sub(r'[^A-Za-z :;.,_-]','',line).strip())
                if labels:rows.append(dict(pdf_page=n,crop_fraction=fraction,ocr_rotation=angle,labels=labels))
    write_json(output,dict(source=str(path),observations=rows));print(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('scan');s.add_argument('source');s.add_argument('output');s.add_argument('--limit',type=int,default=0)
    s=sub.add_parser('contact');s.add_argument('source');s.add_argument('output');s.add_argument('--pages',type=int,nargs='+',required=True);s.add_argument('--dpi',type=int,default=50)
    s=sub.add_parser('ocr');s.add_argument('source');s.add_argument('output');s.add_argument('--pages',type=int,nargs='+',required=True);s.add_argument('--dpi',type=int,default=110)
    s=sub.add_parser('north');s.add_argument('source');s.add_argument('output');s.add_argument('--pages',type=int,nargs='+',required=True);s.add_argument('--fraction',type=float,nargs=4,default=[0,0,1,1]);s.add_argument('--save-crop',action='store_true')
    a=p.parse_args()
    if a.cmd=='scan':scan(a.source,a.output,a.limit)
    elif a.cmd=='contact':contact(a.source,a.pages,a.output,a.dpi)
    elif a.cmd=='ocr':ocr(a.source,a.pages,a.output,a.dpi)
    else:north_labels(a.source,a.pages,a.output,a.fraction,a.save_crop)
if __name__=='__main__':main()
