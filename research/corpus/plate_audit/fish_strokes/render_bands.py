"""Primary impression glyph-band crops for the complete fish/stroke audit frame."""
from pathlib import Path
import fitz, json, hashlib
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
src=ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
pdf=fitz.open(src)
# Manually located normalized impression bands. No retouching or mirroring.
spec=[
 ('M-7A',42,.04,.535,.635,.65),
 ('M-35A',55,.59,.07,.94,.18),
 ('M-42A',57,.60,.395,.94,.49),
 ('M-43A',57,.62,.708,.94,.816),
 ('M-46A',58,.47,.69,.82,.78),
 ('M-81A',70,.665,.255,.98,.38),
 ('M-86A',71,.65,.29,.94,.38),
 ('M-89A',72,.065,.282,.325,.355),
 ('M-91A',72,.695,.278,.95,.35),
 ('M-107A',75,.64,.27,.95,.385),
 ('M-140A',81,.34,.278,.66,.386),
 ('M-144A',81,.64,.72,.94,.835),
 ('M-147A',82,.66,.27,.96,.397),
]
manifest=[]
for ident,n,x0,y0,x1,y1 in spec:
    p=pdf[n-1]
    clip=fitz.Rect(p.rect.width*x0,p.rect.height*y0,p.rect.width*x1,p.rect.height*y1)
    dest=OUT/f'{ident}_band.png'
    pix=p.get_pixmap(matrix=fitz.Matrix(6,6),clip=clip)
    pix.save(dest)
    manifest.append({'id':ident,'pdf_page':n,'printed_page':n-36,
                     'crop_fraction':[x0,y0,x1,y1], 'file':dest.name,
                     'width':pix.width,'height':pix.height,
                     'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(OUT/'band_manifest.json').write_text(json.dumps({'source_url':'https://ignca.gov.in/Asi_data/76884.pdf',
    'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
    'rendering':'PyMuPDF at 6x. Enlarging the scan adds no detail. Glyph bands are excerpts from labelled context plates.',
    'crops':manifest},indent=2)+'\n',encoding='utf-8')
print('Rendered',len(manifest),'bands')
