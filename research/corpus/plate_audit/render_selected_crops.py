from pathlib import Path
import fitz, json, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
src=ROOT/'research/literature/sources/joshi_parpola_1987_cisi1.pdf'
pdf=fitz.open(src)
# Manually selected context crops retain impression and printed identification.
# Fractions are page coordinates; enlarging a scanned plate adds no new detail.
spec=[
 ('M-8A',43,.28,.49,.99,.99),('M-16A',48,.52,.06,.98,.38),
 ('M-34A',54,.46,.37,.88,.96),('M-58A',63,.54,.06,.99,.35),
 ('M-65A',65,.58,.37,.99,.64),('M-73A',68,.50,.05,.91,.33),
 ('M-77A',69,.01,.71,.35,.96),('M-81A',70,.35,.25,.98,.58),
 ('M-93A',72,.37,.72,.62,.96),('M-94A',72,.65,.71,.94,.96),
 ('M-107A',75,.64,.28,.95,.51),('M-115A',76,.33,.65,.69,.94),
 ('M-129A',79,.34,.29,.63,.49),('M-132A',79,.34,.74,.63,.95),
 ('M-135A',80,.37,.26,.97,.48),('M-140A',81,.34,.29,.66,.49),
 ('M-141A',81,.65,.28,.94,.49),('M-144A',81,.64,.73,.94,.96),
 ('M-147A',82,.66,.28,.96,.48),('M-150A',83,.01,.27,.34,.52),
 ('M-152A',83,.65,.26,.99,.52),('M-173A',87,.01,.27,.36,.47),
 ('M-178A',87,.28,.77,.49,.98),('M-181A',88,.68,.06,.98,.25),
 ('M-183A',88,.68,.26,.98,.44),
]
manifest=[]
for ident,n,x0,y0,x1,y1 in spec:
    p=pdf[n-1]
    clip=fitz.Rect(p.rect.width*x0,p.rect.height*y0,p.rect.width*x1,p.rect.height*y1)
    dest=OUT/f'{ident}_impression.png'
    p.get_pixmap(matrix=fitz.Matrix(4,4),clip=clip).save(dest)
    manifest.append({'id':ident,'pdf_page':n,'printed_page':n-36,'crop_fraction':[x0,y0,x1,y1],
                     'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(OUT/'crop_manifest.json').write_text(json.dumps({'source_path':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
 'source_url':'https://ignca.gov.in/Asi_data/76884.pdf','source_license':'No explicit open license found; local research excerpts, no bulk republication.',
 'citation':'Joshi, Jagat Pati and Asko Parpola (eds.) 1987. Corpus of Indus Seals and Inscriptions, Vol. 1: Collections in India. MASI86 / AASF B239.',
 'rendering':'PyMuPDF raster rendering at 4x; context crops, no glyph alteration.', 'crops':manifest},indent=2)+'\n',encoding='utf-8')
print('Rendered',len(manifest),'context crops')
