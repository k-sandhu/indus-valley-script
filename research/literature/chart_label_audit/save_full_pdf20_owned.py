"""Numeric labels manually read from original high-resolution chart crops."""
from pathlib import Path
import csv,json
BASE=Path(__file__).parent.parent/'chart_complete'
BASE.mkdir(exist_ok=True)
LABELS={
 5:[(110,94),(110,739),(111,167),(111,483),(112,93),(112,293),
    (113,745),(114,173),(114,91),(114,373),(114,528),(115,555),
    (116,326),(117,215),(117,214),(117,266),(118,497),(118,724),
    (119,25),(119,509),(120,154),(120,469),(121,1),(121,23),
    (121,258),(121,423),(121,764),(121,768),(122,2),(122,231),
    (122,765),(122,769),(123,3),(123,199),(123,766)],
 6:[(123,770),(124,4),(124,16),(124,438),(124,678),(124,767),
    (124,771),(125,5),(125,17),(125,715),(125,799),(126,6),
    (126,18),(126,670),(126,723),(127,7),(127,19),(127,690),
    (128,20),(129,314),(129,21),(129,315),(130,22),(131,594),
    (131,310),(132,498),(132,311),(133,473),(134,499),(135,500),
    (136,529),(136,397),(136,717),(136,796),(137,437)],
 7:[(138,82),(138,459),(139,15),(139,292),(140,14),(141,492),
    (141,130),(141,729),(142,24),(142,280),(143,493),(144,8),
    (144,501),(145,9),(145,543),(146,756),(147,10),(147,424),
    (148,331),(149,759),(150,294),(151,12),(151,784),(152,250),
    (153,485),(153,383),(154,153),(154,265),(154,289),(154,511),
    (155,514),(156,445),(156,681),(157,495),(158,319)],
 8:[(159,221),(159,735),(160,220),(160,155),(161,355),(162,591),
    (163,152),(163,332),(164,399),(165,216),(166,277),(167,777),
    (168,778),(169,565),(170,291),(171,228),(172,242),(172,226),
    (172,347),(173,455),(173,365),(173,682),(174,553),(174,446),
    (175,218),(175,416),(176,219),(177,243),(177,719),(178,327),
    (178,794),(179,330),(179,789),(180,346),(181,217)],
 9:[(182,81),(182,253),(183,757),(184,299),(184,475),(185,99),
    (185,402),(186,100),(186,708),(186,782),(186,790),(187,552),
    (188,101),(188,306),(189,303),(190,403),(191,107),(192,516),
    (193,185),(193,676),(194,186),(194,434),(195,329),(195,300),
    (196,302),(197,109),(197,308),(198,131),(199,384),(200,54),
    (200,701),(201,52),(201,108),(202,53),(202,582)],
}
AMBIGUOUS={(7,22):{'lower_alternatives':[764],'confidence':'medium','note':'Upper loop of middle digit faint; best784,764 possible. Preserve ambiguity.'}}
ZOOM_NOTES={(5,21):'12x original label crop reads469; preliminary6x misreading459 corrected by visual source.',
            (6,31):'12x original label crop confirms upper136.',
            (7,22):'12x original crop does not fully remove lower middle-digit ambiguity.'}
rows=[]
for col,labels in LABELS.items():
    assert len(labels)==35
    for row,(rank,code) in enumerate(labels):
        start,stop=(0,11) if row<12 else ((12,23) if row<24 else (24,34))
        amb=AMBIGUOUS.get((col,row),{})
        left=62+49.5*col;top=65+20.05*row
        rows.append({'pdf_page':20,'printed_page':19,'column_0based':col,'row_0based':row,
                     'upper_rank':rank,'lower_stable_finnish_code':code,
                     'upper_confidence':'high','lower_confidence':amb.get('confidence','high'),
                     'upper_alternatives':[],'lower_alternatives':amb.get('lower_alternatives',[]),
                     'upper_rank_underlined':False,'lower_code_underlined':False,
                     'numeric_underlining_note':'No underline on numeric labels; glyph/group dashed dividers are separate.',
                     'cell_clip_points':[left-3,top-1,left+48,top+23],
                     'source_image':f'pdf20_c{col}_rows{start}_{stop}.png',
                     'note':amb.get('note',ZOOM_NOTES.get((col,row),'')),
                     'audit_scope':'numeric labels only; glyph not transcribed'})
(BASE/'manual_numeric_labels.json').write_text(json.dumps({'method':'Initial independent original-image reading preserved in manual_numeric_labels_before_duplicate_adjudication.json; current source reinspection corrects c7r25 to383 and c9r19 to676. Later duplicate-label flags do not enforce uniqueness. Numeric labels only.','rows':rows},indent=2),encoding='utf-8')
with (BASE/'manual_numeric_labels.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(f'Saved {len(rows)} manual numeric-label cells.')
