"""Manual original-chart numeric labels. No OCR, template, or root table input."""
from pathlib import Path
import json,csv
BASE=Path(__file__).parent
LABELS={
 0:[(203,90),(203,698),(204,156),(204,119),(205,129),(205,233),
    (206,457),(206,78),(207,349),(208,102),(208,703),(209,103),
    (209,245),(210,104),(210,223),(210,389),(210,732),(211,271),
    (211,260),(212,48),(213,324),(214,360),(214,775),(215,105),
    (215,312),(215,798),(216,580),(217,95),(217,549),(218,579),
    (219,755),(220,39),(220,442),(221,40),(221,504)],
 1:[(222,46),(222,422),(223,343),(224,234),(224,235),(225,35),
    (226,36),(227,229),(227,298),(228,37),(229,32),(230,241),
    (230,33),(230,412),(230,593),(231,240),(232,38),(232,583),
    (233,564),(234,350),(234,793),(235,117),(236,378),(237,34),
    (238,249),(238,198),(239,688),(239,689),(240,122),(240,728),
    (241,488),(242,124),(243,47),(244,282),(245,313)],
 2:[(245,393),(246,562),(247,560),(248,432),(248,791),(249,672),
    (250,335),(251,287),(252,575),(253,85),(254,125),(254,736),
    (255,232),(255,712),(256,123),(256,507),(257,372),(258,574),
    (259,453),(260,742),(260,478),(261,441),(262,59),(263,721),
    (264,60),(264,545),(265,61),(265,687),(266,345),(267,64),
    (268,69),(268,62),(268,92),(268,554),(268,696)],
 3:[(269,758),(270,66),(270,65),(270,67),(270,68),(270,396),
    (270,400),(270,693),(271,405),(272,318),(272,290),(273,731),
    (273,792),(274,29),(275,72),(275,73),(275,74),(275,317),
    (275,783),(276,27),(276,491),(277,536),(278,572),(279,451),
    (280,28),(280,256),(281,358),(282,259),(283,31),(283,502),
    (284,477),(284,171),(284,456),(284,738),(285,49)],
 4:[(286,589),(287,711),(288,50),(288,683),(289,30),(289,261),
    (290,436),(291,576),(292,371),(292,773),(293,57),(293,55),
    (293,447),(294,334),(295,279),(296,56),(296,686),(297,725),
    (298,379),(298,704),(299,444),(300,270),(300,333),(301,41),
    (301,479),(302,567),(303,275),(303,519),(304,79),(304,800),
    (305,58),(305,716),(306,80),(306,474),(307,362)],
 5:[(308,75),(308,429),(309,76),(310,246),(310,548),(311,201),
    (311,720),(312,202),(312,707),(313,359),(313,267),(313,375),
    (314,88),(314,779),(315,710),(315,197),(316,398),(316,532),
    (317,407),(317,322),(318,283),(319,714),(319,746),(320,203),
    (320,484),(321,751),(322,337),(322,705),(323,128),(323,776),
    (324,204),(324,526),(325,205),(325,209),(326,205)],
 6:[(326,413),(327,206),(327,207),(327,414),(327,706),(328,749),
    (329,494),(329,774),(330,367),(331,385),(332,248),(332,210),
    (332,211),(332,276),(332,395),(332,428),(332,480),(333,364),
    (334,752),(335,448),(336,361),(337,213),(337,281),(338,401),
    (339,121),(340,83),(341,89),(342,165),(342,726),(343,471),
    (344,239),(345,285),(345,262),(345,578),(346,192)],
 7:[(346,785),(347,581),(348,737),(349,169),(349,533),(350,506),
    (351,496),(352,170),(352,309),(353,196),(353,296),(353,694),
    (354,709),(355,381),(355,98),(355,111),(355,157),(355,387),
    (355,415),(355,684),(356,175),(357,734),(358,176),(359,115),
    (360,377),(361,118),(362,525),(363,112),(364,161),(364,537),
    (365,540),(365,255),(366,158),(366,431),(367,200)],
 8:[(367,727),(368,159),(368,691),(369,160),(369,700),(370,671),
    (371,251),(372,116),(372,257),(373,301),(374,297),(375,587),
    (376,163),(376,254),(377,569),(377,338),(378,63),(378,284),
    (379,113),(380,164),(380,556),(381,584),(381,788),(382,114),
    (382,797),(383,162),(383,420),(383,421),(383,510),(384,352),
    (385,433),(386,430),(386,802),(387,363),(387,227)],
 9:[(388,418),(388,166),(388,426),(388,730),(389,487),(390,677),
    (391,351),(392,468),(392,409),(393,406),(394,753),(395,596),
    (395,454),(396,599),(396,106),(397,597),(397,13),(398,598),
    (398,542),(399,762),(400,70),(401,595)],
}
AMBIGUOUS={
 (8,16):{'lower_confidence':'medium','lower_alternatives':[53],'note':'Post-duplicate source reinspection:63 best,53 possible. Preserve both; not selected by uniqueness.'},
 (4,22):{'lower_confidence':'medium','lower_alternatives':[533],
         'note':'First lower digit is degraded;333 best,533 possible. Original12x crop inspected; no reference prediction used.'},
 (0,1):{'lower_confidence':'medium','lower_alternatives':[598]},
 (0,18):{'lower_confidence':'medium','lower_alternatives':[250]},
 (0,29):{'lower_confidence':'medium','lower_alternatives':[679]},
 (3,2):{'lower_confidence':'medium','lower_alternatives':[55]},
 (3,4):{'lower_confidence':'medium','lower_alternatives':[58]},
 (4,6):{'lower_confidence':'medium','lower_alternatives':[435]},
 (5,34):{'lower_confidence':'medium','lower_alternatives':[206,208],
          'note':'Original12x post-comparison crop now has205 best,206/208 possible; initial206 retained in before-adjudication file. Do not choose by mapping agreement.'},
 (6,9):{'lower_confidence':'medium','lower_alternatives':[386]},
 (6,17):{'lower_confidence':'medium','lower_alternatives':[354]},
 (7,6):{'lower_confidence':'medium','lower_alternatives':[495]},
 (8,5):{'lower_confidence':'medium','lower_alternatives':[571]},
 (9,5):{'lower_confidence':'medium','lower_alternatives':[577]},
}
rows=[]
for col,labels in LABELS.items():
    assert len(labels)==(35 if col<9 else 22)
    for row,(rank,code) in enumerate(labels):
        start,stop=(0,11) if row<12 else ((12,min(23,len(labels)-1)) if row<24 else (24,34))
        amb=AMBIGUOUS.get((col,row),{})
        left=47+49.5*col;top=65+20.05*row
        rows.append({'pdf_page':21,'printed_page':20,'column_0based':col,'row_0based':row,
                     'upper_rank':rank,'lower_stable_finnish_code':code,
                     'upper_confidence':amb.get('upper_confidence','high'),
                     'lower_confidence':amb.get('lower_confidence','high'),
                     'upper_alternatives':amb.get('upper_alternatives',[]),
                     'lower_alternatives':amb.get('lower_alternatives',[]),
                     'upper_rank_underlined':False,'lower_code_underlined':False,
                     'numeric_underlining_note':'No numeric underline; glyph-group dashed dividers are separate.',
                     'cell_clip_points':[left-3,top-1,left+48,top+23],
                     'source_image':f'full_pdf21/pdf21_c{col}_rows{start}_{stop}.png',
                     'note':amb.get('note','Post-comparison original12x reinspection preserves unresolved5/6 candidate union; do not choose by mapping agreement.' if amb else ''),
                     'audit_scope':'Numeric labels only; no glyph/semantic validation.'})
out={'source_sha256':'7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27',
     'method':'Manual original-image reading. Initial337 reference was independent of root reference/OCR/templates/predictions and is preserved separately. Current entries include post-comparison source adjudication of22 disagreements and later duplicate-label source checks; no prediction resolves ambiguity.',
     'completed':len(rows)==337,'expected_occupied_cells':337,'rows':rows,
     'fresh20_preserved_separately':'fresh21_audit.json; do not treat full-chart reconciliation as a new blind test.'}
(BASE/'full21_audit.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
with (BASE/'full21_audit.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(f'Saved {len(rows)}/337 manually read cells.')
