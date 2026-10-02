from pathlib import Path
import json
BASE=Path(__file__).parent
manifest=json.loads((BASE/'fresh21_sampling_manifest.json').read_text())
labels={
 (0,10):(208,703), (0,28):(217,549), (1,3):(224,234),
 (1,16):(232,38), (1,20):(234,793), (2,34):(268,696),
 (3,15):(275,73), (3,23):(279,451), (5,1):(308,429),
 (6,12):(332,211), (7,0):(346,785), (7,8):(352,309),
 (8,17):(378,284), (8,26):(383,420), (8,27):(383,421),
 (8,33):(387,363), (9,2):(388,426), (9,11):(395,596),
 (9,16):(397,13), (9,18):(398,542),
}
assert len(labels)==20
assert not(set(labels)&{tuple(x) for x in manifest['previous15_excluded']})
rows=[]
for item in manifest['sample']:
    c,r=item['column_0based'],item['row_0based']
    rank,code=labels[c,r]
    rows.append({**item,'upper_rank':rank,'lower_stable_finnish_code':code,
                 'upper_confidence':'high','lower_confidence':'high',
                 'upper_alternatives':[],'lower_alternatives':[],
                 'upper_rank_underlined':False,'lower_code_underlined':False,
                 'numeric_underlining_note':'No numeric underline; glyph-group dashed dividers are separate.',
                 'note':'12x original label crop also inspected.' if (c,r) in [(0,10),(8,33)] else ''})
out={'source_sha256':manifest['sha256'],'seed':manifest['seed'],
     'sampling_method':manifest['rng'],'previous15_excluded':manifest['previous15_excluded'],
     'method':'Manual original-image reading. Root references, automated OCR, templates and predictions not inspected.',
     'scope':'Numeric labels only; no glyph correspondence, allograph, numerical or phonetic inference.',
     'rows':rows}
(BASE/'fresh21_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(f'Saved {len(rows)} fresh independent PDF21 cells, all high-confidence numeric labels.')
