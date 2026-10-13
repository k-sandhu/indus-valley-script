"""Render a new PDF QA endpoint and record machine checks before visual review."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, subprocess
import fitz
from PIL import Image, ImageDraw, ImageFont

def file_record(path):
    return dict(path=path.as_posix(),bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pdf',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True)
    subprocess.run(['pdftoppm','-r','110','-png',str(a.pdf),str(a.output/'page')],check=True)
    pages=sorted(a.output.glob('page-*.png'),key=lambda f:int(f.stem.split('-')[-1]))
    if not pages:raise ValueError('No Poppler page renders.')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    sheets=[]
    # Four pages per contact sheet keeps tables and their margins inspectable.
    for start in range(0,len(pages),4):
        batch=pages[start:start+4]
        sheet=Image.new('RGB',(1220,1660),'#dce3e3')
        draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(batch):
            image=Image.open(path).convert('RGB')
            image.thumbnail((580,760))
            x=20+(j%2)*610;y=38+(j//2)*820
            draw.text((x,y-27),f'Page {start+j+1}',font=font,fill='#223333')
            sheet.paste(image,(x,y))
        target=a.output/f'contact-{start+1:02d}-{start+len(batch):02d}.png'
        sheet.save(target);sheets.append(target)
    doc=fitz.open(a.pdf)
    text='\n'.join(page.get_text() for page in doc)
    images=sum(len(page.get_images(full=True)) for page in doc)
    links=sum(len(page.get_links()) for page in doc)
    per_page=[]
    for n,page in enumerate(doc):
        per_page.append(dict(page=n+1,characters=len(page.get_text()),images=len(page.get_images()),links=len(page.get_links())))
    report=dict(generated_utc=datetime.now(timezone.utc).isoformat(),
        stage='Machine extraction and Poppler rendering complete; visual inspection pending',
        pdf=file_record(a.pdf),pages=len(doc),page_renders=len(pages),embedded_image_occurrences=images,
        link_annotations=links,unicode_replacement_count=text.count('\ufffd'),black_square_count=text.count('\u25a0'),
        unresolved_placeholder_count=text.count('@@'),per_page=per_page,
        contact_sheets=[file_record(path) for path in sheets])
    (a.output/'machine-inspection.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['pages','page_renders','link_annotations','unicode_replacement_count','black_square_count','unresolved_placeholder_count']}))

if __name__=='__main__':main()
