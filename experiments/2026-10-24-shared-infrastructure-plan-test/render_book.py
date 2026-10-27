"""Render all report pages for visual review and flag text outside the page."""
import argparse
import hashlib
import json
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

P=Path(__file__).resolve().parent
RAW=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-shared-infrastructure-plan-test')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main(pdf,tag):
    out=RAW/'review'/f'book-{tag}'
    out.mkdir(exist_ok=False)
    doc=fitz.open(pdf)
    issues=[];pages=[]
    for i,page in enumerate(doc):
        f=out/f'page-{i+1:03d}.png'
        page.get_pixmap(matrix=fitz.Matrix(1.1,1.1),alpha=False).save(f)
        text=page.get_text()
        if '\ufffd' in text:issues.append({'page':i+1,'kind':'replacement-character'})
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines',[]):
                for span in line['spans']:
                    if not span['text'].strip():continue
                    x0,y0,x1,y1=span['bbox']
                    if x0<-.5 or y0<-.5 or x1>page.rect.width+.5 or y1>page.rect.height+.5:
                        issues.append({'page':i+1,'kind':'text-outside-page','text':span['text'][:100],'bbox':span['bbox']})
        pages.append({'page':i+1,'physical_path':str(f),'sha256':sha(f),
                      'size_points':[page.rect.width,page.rect.height],
                      'text_characters':len(text),'images':len(page.get_images())})
    contacts=[]
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    for start in range(0,len(pages),12):
        sheet=Image.new('RGB',(1600,1550),'#e4e9e5');draw=ImageDraw.Draw(sheet)
        for j,row in enumerate(pages[start:start+12]):
            im=Image.open(row['physical_path']);im.thumbnail((380,455))
            x=10+(j%4)*400;y=35+(j//4)*510
            sheet.paste(im,(x+(380-im.width)//2,y))
            draw.text((x,y-27),f"Page {row['page']}",font=font,fill='#193337')
        path=out/f'contact-{start//12+1:02d}.png';sheet.save(path)
        contacts.append({'physical_path':str(path),'sha256':sha(path)})
    result={'pdf_physical_path':str(pdf),'pdf_sha256':sha(pdf),'page_count':len(pages),
            'render_scale':1.1,'page_renders':pages,'contacts':contacts,'automated_layout_issues':issues,
            'visual_review_status':'pending human/tool image inspection','automated_passed':not issues}
    (P/f'book-render-{tag}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'pages':len(pages),'contacts':len(contacts),'automated_issues':issues}))

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--pdf',type=Path,required=True);a.add_argument('--tag',required=True)
    args=a.parse_args();main(args.pdf,args.tag)
