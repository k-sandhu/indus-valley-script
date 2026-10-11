"""Render local-only Wells drawing witnesses using Lipi's documented encoding."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/raw/2026-10-08-bonta-extension/source-2026-10-09'
FONT=ROOT/'data/lipi/src/assets/fonts/indus-font.woff2'

def main():
    ds=json.loads((ROOT/'experiments/2026-10-08-bonta-extension/run-2026-10-08-v1/dossiers.json').read_text(encoding='utf-8'))['rows']
    f=TTFont(FONT); cmap=f.getBestCmap(); f.flavor=None
    ttf=RAW/'lipi-font-local.ttf'; f.save(ttf)
    ft=ImageFont.truetype(str(ttf),64)
    label=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
    images=RAW/'glyphs'; images.mkdir(exist_ok=True)
    mapping=[]
    for d in ds:
        cp=0xe000+int(d['code']); im=Image.new('RGB',(160,130),'white'); draw=ImageDraw.Draw(im)
        exists=cp in cmap
        if exists:
            box=draw.textbbox((0,0),chr(cp),font=ft)
            draw.text(((160-(box[2]-box[0]))/2-box[0],(130-(box[3]-box[1]))/2-box[1]),chr(cp),font=ft,fill='black')
        else:draw.text((10,50),'drawing absent',font=label,fill='black')
        path=images/f"W{d['code']}.png";im.save(path)
        mapping.append({'code':d['code'],'unicode':hex(cp),'font_glyph':cmap.get(cp),'drawing_present':exists,
                        'path':path.relative_to(ROOT).as_posix()})
    unknown=[d for d in ds if not d['mayig_candidates']]
    for start in range(0,len(unknown),45):
        batch=unknown[start:start+45];sheet=Image.new('RGB',(1000,9*170),'white');draw=ImageDraw.Draw(sheet)
        for k,d in enumerate(batch):
            x=(k%5)*200;y=(k//5)*170
            im=Image.open(images/f"W{d['code']}.png")
            sheet.paste(im,(x+20,y+25));draw.text((x+16,y+5),f"W{d['code']}  n={d['complete_unique_frame_tokens']}",font=label,fill='black')
            draw.line((x,y+168,x+199,y+168),fill='#cccccc')
        sheet.save(RAW/f'unmapped-glyph-sheet-{start//45+1:02d}.png')
    (RAW/'glyph-witness-index.json').write_text(json.dumps({'font_path':FONT.relative_to(ROOT).as_posix(),
       'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),
       'encoding_witness':'data/lipi/src/pages/index.vue:830; U+E000 plus decimal Wells code',
       'rights':'Local-only source drawing witnesses; no third-party font/image upload or tracking.',
       'rows':mapping},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'codes':len(mapping),'font_drawings':sum(x['drawing_present'] for x in mapping),'unmapped_contact_sheets':(len(unknown)+44)//45}))

if __name__=='__main__':main()
