"""Supplementary digit comparisons prompted by v3 card-label observations."""
from audit import ROOT, RAW, read, key, write
import fitz
from PIL import Image, ImageDraw, ImageFont

cells=['p20_c4_r1','p21_c7_r5','p20_c4_r13','p21_c1_r19','p21_c6_r31','p21_c6_r32',
       'p20_c8_r15','p20_c8_r17','p21_c0_r1','p21_c9_r17','p21_c0_r29','p21_c6_r9',
       'p21_c3_r4','p21_c4_r22','p21_c8_r16','p21_c9_r5',
       'p21_c8_r5','p20_c3_r18','p21_c8_r2','p21_c7_r5']
atlas={key(r):r for r in read(ROOT/'output/chart_atlas/reference.json')['rows']}
doc=fitz.open(ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf')
folder=RAW/'digits-24x'
folder.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for start in range(0,len(cells),4):
    ims=[]
    for cell in cells[start:start+4]:
        r=atlas[cell]
        box=r['source_crop_pdf_points']
        # Lower-left numeric band of the reused cell rectangle; includes class and code.
        rect=fitz.Rect(box[0],box[1]+(box[3]-box[1])*.25,
                       box[0]+(box[2]-box[0])*.48,box[1]+(box[3]-box[1])*.8)
        pix=doc[r['pdf_page']-1].get_pixmap(matrix=fitz.Matrix(24,24),clip=rect,alpha=False)
        im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        im.save(folder/f'{cell}.png')
        ims.append((cell,im))
    w=max(im.width for c,im in ims);h=max(im.height for c,im in ims)+40
    sheet=Image.new('RGB',(w*2,h*2),'white');draw=ImageDraw.Draw(sheet)
    for i,(cell,im) in enumerate(ims):
        x,y=i%2*w,i//2*h
        draw.text((x+4,y),cell,fill='blue',font=font);sheet.paste(im,(x,y+40))
    sheet.save(folder/f'sheet-{start:02d}.png')
write(folder/'manifest.json',{'scale':24,'cells':cells,'method':'Numeric-band clips; no OCR or PDF text layer.'})
