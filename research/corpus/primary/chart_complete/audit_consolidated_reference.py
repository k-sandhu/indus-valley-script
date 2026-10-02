"""Independent source-table/atlas consistency audit, not palaeographic validation."""
from pathlib import Path
import json,hashlib
from collections import Counter
import fitz,numpy as np
from PIL import Image

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[3]
def load(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def key(r): return r['pdf_page'],r['column'],r['row']
def sha(path): return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

reference_path='research/chart_reference/manual_numeric_reference.json'
atlas_path='output/chart_atlas/reference.json'
reference=load(reference_path);atlas=load(atlas_path)
expected={}
def add(p,c,r,rank,code,alternatives):
    expected[p,c,r]={'rank':rank,'code':code,'candidates':set([code]+alternatives)}
a=load('research/corpus/primary/chart_complete/column0_reinspection.json')
for r in a['rows']: add(20,0,r['row_0based'],r['rank'],r['code'],r.get('alternatives',[]))
for c in load('research/corpus/primary/chart_complete/manual_columns1_4.json')['columns']:
    for r in c['rows']: add(20,c['col_0based'],r['row_0based'],r['rank'],r['code'],r.get('alternatives',[]))
for path in ['research/literature/chart_complete/manual_numeric_labels.json','research/literature/chart_complete/full21_audit.json']:
    for r in load(path)['rows']:
        add(r['pdf_page'],r['column_0based'],r['row_0based'],r['upper_rank'],r['lower_stable_finnish_code'],r.get('lower_alternatives',[]))
for r in load('research/literature/chart_complete/duplicate_labels/adjudication.json')['rows']:
    add(r['pdf_page'],r['column_0based'],r['row_0based'],r['upper_rank'],r['lower_stable_finnish_code'],r.get('lower_alternatives',[]))
# Explicit unresolved cross-reader union, rather than selecting by uniqueness.
expected[20,4,21]['candidates']={465,485,486}
expected[20,4,21]['preferred_unresolved']=True

frame={(20,c,r) for c in range(10) for r in range(35)}
frame|={(21,c,r) for c in range(9) for r in range(35)}
frame|={(21,9,r) for r in range(22)}
counts=Counter(key(r) for r in reference['rows'])
actual={key(r):r for r in reference['rows']}
issues=[]
for k in sorted(frame):
    if k not in actual or k not in expected:
        issues.append({'key':k,'issue':'missing cell'});continue
    a,e=actual[k],expected[k]
    if a['rank']!=e['rank']:issues.append({'key':k,'issue':'rank source disagreement','actual':a['rank'],'expected':e['rank']})
    if set([a['code']]+a['alternatives'])!=e['candidates']:
        issues.append({'key':k,'issue':'candidate set differs from current source/adjudication'})
    if not e.get('preferred_unresolved') and a['code']!=e['code']:
        issues.append({'key':k,'issue':'preferred code differs from current source/adjudication'})
    if a['alternatives'] and a['numeric_confidence']=='high':
        issues.append({'key':k,'issue':'alternatives paired with high confidence'})

atlas_issues=[];doc=fitz.open(ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf')
for r in atlas['rows']:
    k=key(r)
    for field in ['rank','code','alternatives','numeric_confidence','dashed_auxiliary']:
        if r.get(field)!=actual.get(k,{}).get(field):
            atlas_issues.append({'key':k,'issue':'atlas metadata mismatch','field':field})
    p=ROOT/'output/chart_atlas'/r['image']
    if not p.exists():atlas_issues.append({'key':k,'issue':'missing image'});continue
    expected_pix=doc[r['pdf_page']-1].get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(r['source_crop_pdf_points']))
    arr=np.frombuffer(expected_pix.samples,dtype=np.uint8).reshape(expected_pix.height,expected_pix.width,expected_pix.n)
    stored=np.array(Image.open(p).convert('RGB'))
    if arr.shape!=stored.shape or not np.array_equal(arr,stored):
        atlas_issues.append({'key':k,'issue':'image pixels differ from exact claimed original source crop'})

frozen=load('research/visual_digitization/font_fresh20/predictions_before_gold.json')
frozen_chart_path='research/visual_digitization/font_fresh20/chart_reference_at_prediction_freeze.json'
source_pin='7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27'
gold_pin='061130347c5feb52acb79427e672fade16b553e10aab00fb6c1fca493172e279'
result={
 'scope':'Source-table coverage, uncertainty, pins and exact atlas-image consistency only. No claim of numerical-label/glyph expert accuracy or accepted full inscription corpus.',
 'source_pdf_sha256_verified':sha('research/corpus/primary/koskenniemi_parpola1979.pdf')==source_pin,
 'consolidated_reference_sha256':sha(reference_path),'atlas_reference_sha256':sha(atlas_path),
 'frame_cells':len(frame),'reference_rows':len(reference['rows']),'unique_keys':len(actual),
 'missing_keys':sorted(frame-set(actual)),'unexpected_keys':sorted(set(actual)-frame),
 'duplicate_keys':[k for k,v in counts.items() if v>1],
 'ambiguous_lower_code_cells':sum(bool(r['alternatives']) for r in reference['rows']),
 'source_overlay_issues':issues,'atlas_issues':atlas_issues,
 'atlas_images_checked':len(atlas['rows']),
 'frozen_old_chart_hash_matches_prediction_pin':sha(frozen_chart_path)==frozen['manual_chart_sha256'],
 'fresh20_gold_unchanged':sha('research/corpus/primary/font_fresh20/manual_reference.json')==gold_pin,
 'c4r21_all_three_candidates_preserved':set([actual[20,4,21]['code']]+actual[20,4,21]['alternatives'])=={465,485,486},
 'c4r1_corrected_rank86_retained':actual[20,4,1]['rank']==86,
 'limits':'Images are context crops and can contain neighbouring ink. Exact pixel provenance does not certify glyph crop geometry or underlying numerical readings. No historical benchmark updated.'
}
(BASE/'consolidated_atlas_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
