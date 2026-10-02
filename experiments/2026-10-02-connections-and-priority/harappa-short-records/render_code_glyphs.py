from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'data/raw/2026-10-02-connections-and-priority/harappa-short-records/font-witness'
if OUT.exists() and any(OUT.iterdir()):
    raise FileExistsError('Font witness exists; preserve its bytes and use a new directory for another render.')
OUT.mkdir(parents=True,exist_ok=True)
source = ROOT/'data/lipi/src/assets/fonts/indus-font.woff2'
im = Image.new('RGB',(900,250),'white')
d = ImageDraw.Draw(im)
f = ImageFont.truetype(str(source),100)
codes = [3,33,34,154,156,700,861]
for i,code in enumerate(codes):
    d.text((i*125+10,5),f'{code:03}',fill='black')
    d.text((i*125+10,55),chr(0xe000+code),font=f,fill='black')
p = OUT/'seven-observation-codes.png'
im.save(p)
(OUT/'manifest.json').write_text(json.dumps({'parent_path':str(source.relative_to(ROOT)).replace('\\','/'),'parent_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'font_code_rule':'glyph U+E000 plus decimal sign code, as characterize() in upstream Vue source','codepoints':[hex(0xe000+n) for n in codes],'operation':'render imported observation font; shape witness only; no interpretation fields','path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
