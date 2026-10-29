"""Verify figures, copied source identities and the assembled PDF and archive."""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
PACKAGE=Path(__file__).resolve().parents[1]
RUN=sys.argv[1] if len(sys.argv)>1 else 'run-v4'
OUT=Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-axis-visual-atlas')/RUN
m=json.loads((OUT/'figures.json').read_text(encoding='utf-8'))
assert len(m['figures'])==32
assert [r['number'] for r in m['figures']]==list(range(1,33))
for r in m['inputs']:
    assert hashlib.sha256((ROOT/r['logical_path']).read_bytes()).hexdigest()==r['sha256'],r['logical_path']
overflow=[]
for r in m['figures']:
    assert r['source'] and r['caption'] and r['source_records']
    for fmt,meta in r['files'].items():
        p=OUT/meta['relative_path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['sha256']
        if fmt=='png':
            im=Image.open(p);im.verify()
            assert Image.open(p).width==3040
        elif fmt=='svg':assert ET.parse(p).getroot().tag.endswith('svg')
        else:
            doc=fitz.open(p);assert len(doc)==1
            page=doc[0]
            for block in page.get_text('dict')['blocks']:
                if 'lines' not in block:continue
                for line in block['lines']:
                    for span in line['spans']:
                        x0,y0,x1,y1=span['bbox']
                        if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                            overflow.append({'figure':r['number'],'text':span['text'],'bbox':span['bbox']})
            assert len(page.get_text())>150
assert not overflow,overflow
pdf=OUT/'town-axis-visual-atlas-2026-10-24.pdf'
doc=fitz.open(pdf);assert len(doc)==35
assert len(doc.get_toc())==34
assert 'Copernicus WorldDEM-30' in doc[0].get_text()
assert 'this reading fails' in doc[-1].get_text()
assert '0.5' in doc[-1].get_text()
for i,r in enumerate(m['figures']):
    original=fitz.open(OUT/r['files']['pdf']['relative_path'])
    assert original[0].get_text()==doc[i+3].get_text()
delivery=json.loads((PACKAGE/f'delivery-{RUN}.json').read_text())
archive=Path(next(r['physical_path'] for r in delivery['files'] if r['physical_path'].endswith('.zip')))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert sum(n.startswith('png/') and n.endswith('.png') for n in z.namelist())==32
    assert sum(n.startswith('svg/') and n.endswith('.svg') for n in z.namelist())==32
    assert sum(n.startswith('pdf/') and n.endswith('.pdf') for n in z.namelist())==32
    for source in (PACKAGE/'code').glob('*'):
        if source.is_file():assert z.read('code/'+source.name)==source.read_bytes()
horizon_rows=[json.loads(line) for line in (ROOT/'experiments/2026-10-24-q1032-town-axis-register/run-v5/horizons.jsonl').read_text().splitlines()]
good=[r for r in horizon_rows if r['usable_at_corrected_site']]
assert len(good)==30 and len({r['town'] for r in good})==20
record={'status':'pass','run':RUN,'figures':32,'formats_each':['PNG','SVG','PDF'],
 'atlas_pages':35,'bookmarks':34,'atlas_figure_text_matches_individual_pdfs':True,'input_hashes_checked':len(m['inputs']),
 'figure_file_hashes_checked':96,'off_page_text_spans':overflow,'archive_integrity':'pass','delivery_archive_checked':str(archive),'packaged_recipes_match_current_code':True,
 'source_plates_local_only':[r['number'] for r in m['figures'] if r['group']=='Source plates'],
 'all_usable_horizon_profiles_retained':30,'towns_with_usable_horizon_profiles':20,
 'new_sources':0,'new_archaeological_measurements':0,'coverage_changes':0,
 'verification_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(PACKAGE/f'checks-{RUN}.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
