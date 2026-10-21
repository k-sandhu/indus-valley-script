"""Build the bounded circular-seal frame without importing scores or sign strings."""
import csv, hashlib, json, random
from pathlib import Path
import fitz
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-20-foreign-script-audit'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, x):
    with p.open('x', encoding='utf-8') as f: json.dump(x, f, indent=2, ensure_ascii=False)
def main():
    rows = [json.loads(s) for s in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    frame = [r for r in rows if r['object_type']=='SEAL:C']
    links=list(csv.DictReader((ROOT/'experiments/2026-10-13-image-index-and-units/run-2026-10-13/images/face-image-links.csv').open(encoding='utf-8')))
    clean=[]
    for r in frame:
        images=[dict(file='data/lipi/public/seal_images/'+l['file'], sha256=l['sha256'],kind=l['kind'],sides=l['sides'],relation=l['relation'],cisi_pdf_page=l['cisi_pdf_page']) for l in links if l['record_id']==r['record_id']]
        clean.append(dict(record_id=r['record_id'],family=r['object_family_id'],cisi=r['source_cisi'],site=r['site'],region=r['region'],object_type=r['object_type'],images=images,metadata=r['metadata']))
    write(HERE/'frame.json', clean)
    pdf=ROOT/'data/raw/2026-10-06-chronology-region/review-response-sources-2026-10-07-v1/laursen2010.pdf'
    doc=fitz.open(pdf)
    for n in [5,6,7,13,14,15,16,17,18,19,21,22,23,33]:
        doc[n-1].get_pixmap(matrix=fitz.Matrix(2,2)).save(str(RAW/f'laursen-pdf-{n:02}.png'))
    (RAW/'laursen-extracted.txt').write_text('\n'.join(f'\nPDF PAGE {i+1}\n'+p.get_text() for i,p in enumerate(doc)),encoding='utf-8')
    random.Random(20261020).shuffle(clean)
    key=[]; packet=[]
    for i,r in enumerate(clean,1):
        opaque=f'A{i:02}'
        key.append(dict(opaque_id=opaque,record_id=r['record_id']))
        packet.append(dict(opaque_id=opaque,images=[dict(path=str(ROOT/l['file']),kind=l['kind'],sha256=l['sha256']) for l in r['images']]))
    write(RAW/'review-packet.json',dict(instructions='Independently inspect every available image. Record seal/impression polarity, direction evidence, damage, visible sign count and mapping confidence; keep alternatives. No scores are supplied. Images may contain original catalogue captions. Rows without an image are unavailable, not negative evidence.',objects=packet,additional_primary_plate=str(RAW/'laursen-pdf-21.png')))
    write(RAW/'review-identity-key.json',key)
    write(HERE/'frame-freeze.json',dict(frame_sha256=digest(HERE/'frame.json'),input_sha256=digest(ROOT/'data/normalized/lipi_observed_faces.jsonl'),faces=len(clean),families=len({r['family'] for r in clean}),faces_with_indexed_image=sum(bool(r['images']) for r in clean),pdf_sha256=digest(pdf)))
    print((HERE/'frame-freeze.json').read_text())
if __name__=='__main__': main()
