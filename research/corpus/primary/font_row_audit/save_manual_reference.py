"""Serialize source-only manual glyph comparisons for ten preselected rows.

This is a local AI annotation pilot, not an authoritative epigraphic edition.
No machine glyph candidate, page30 prediction or font matcher was consulted.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent/'koskenniemi_parpola1979.pdf'
SHA = '7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27'

# code: (primary chart PDF page, column, row, literal visual description)
# Coordinates are 0-based column/row; PDF page is 1-based.
REFS = {
    197:(21,5,15,'U with long inner stem ending in a small circle'),
    532:(21,5,17,'Same U-circle glyph with dashed auxiliary underline'),
    28:(21,3,24,'Four-cell horizontal stack in rectangular outline, upright stem above'),
    58:(21,4,30,'Four tall bars connected along their lower baseline'),
    97:(20,0,22,'Small standing figure with crossed looped head'),
    95:(21,0,27,'Tall vertical staff with triangular arrowhead'),
    177:(20,2,11,'Plain oval fish with two side arms and crossing lower tail'),
    4:(20,6,1,'One row of four short vertical strokes'),
    25:(20,5,18,'Pair of upper short vertical strokes'),
    420:(21,8,26,'Circular outline with inward V from top'),
    204:(21,5,30,'U with two inward horizontal strokes at each upper side'),
    186:(20,9,20,'Leaf-topped bent figure with three horizontal strokes at right'),
    50:(21,4,2,'Squat upper enclosure with two side stubs each side and central upward arrow below'),
    19:(20,6,16,'Grouped short strokes: four upper, three lower'),
    690:(20,6,17,'Same four-over-three short group with dashed auxiliary underline'),
    10:(20,7,16,'Three full-height vertical bars'),
    424:(20,7,17,'Three full-height bars with dashed auxiliary underline'),
    766:(20,5,34,'Three full-height bars under rank123'),
    770:(20,6,0,'Three full-height bars under rank123 with dashed auxiliary underline'),
    105:(21,0,23,'Three pointed triangular peaks joined on a lower baseline'),
    45:(20,4,8,'Small U-like lower vessel with upper crossbar and three rising strokes'),
    232:(21,2,12,'Cross with outer paired oblique chevrons'),
    191:(20,9,12,'Tall bent staff with diagonally opposing top and bottom strokes'),
    184:(20,3,14,'Broad segmented fish with top ears, side strokes and crossed tail'),
    180:(20,2,31,'Oval fish with upper horns, side arms and crossed tail'),
    86:(20,2,28,'Oval fish with caret above, side arms and crossed tail'),
    208:(21,6,1,'U with three short vertical strokes inside its upper opening'),
    154:(20,5,20,'Upper short stroke at left and descending bent stroke at right'),
    220:(20,8,1,'Curved vertical stroke enclosing a small oval on its left'),
    215:(20,5,13,'Three circle-headed figures joined on a curved lower base'),
    104:(21,0,13,'Triangle with three horizontal internal dividers'),
    126:(20,3,34,'Tall Y with central upper prong'),
    5:(20,6,7,'One row of five short vertical strokes'),
    152:(21,8,25,'Diamond outline with inward V at its upper corner'),
    74:(21,3,16,'Square with upper loop, three inward left strokes and two lower curved legs'),
    127:(20,3,33,'Tall staff with comb-like slanting strokes at upper left'),
    174:(20,4,32,'Tall central staff interrupted by a small oval'),
    8:(20,7,11,'Single full-height vertical bar, rank144'),
    764:(20,5,26,'Single full-height vertical bar, rank121'),
    92:(21,2,32,'Rectangle divided into two columns and four horizontal cells'),
    87:(20,2,9,'Narrow hatched oval fish with caret above and crossed tail'),
    491:(21,3,20,'Square with upper upright stem and dashed auxiliary underline'),
    27:(21,3,19,'Square with upper upright stem, without underline'),
    47:(21,1,32,'X with a horizontal upper cap'),
    76:(21,5,2,'Upper paired triangles above a rectangular base divided into three columns'),
    187:(20,4,26,'Curved upright with two leaf-like projections near top'),
}

# Pixel bounds refer to the direct 8x original-PDF crops above. They are manual
# approximate glyph bounds, not a segmentation produced by the font matcher.
ROWS = [
    (0,3,'1018','48640',
     [197,28,58,197,97],
     [(1005,48,1070,168),(1228,48,1296,168),(1319,48,1420,168),(1455,48,1522,168),(1564,48,1630,168)]),
    (0,4,'1019','11 40',
     [95,177,4,25,420],
     [(1188,205,1208,327),(1255,205,1323,327),(1357,205,1421,327),(1479,205,1508,327),(1530,205,1626,327)]),
    (0,5,'1020','11 91',
     [204,186,50,690,[424,770],532,204,105,45],
     [(479,366,583,497),(625,366,716,497),(753,366,874,497),(916,366,980,497),(1052,366,1110,497),(1170,366,1238,497),(1282,366,1390,497),(1418,366,1502,497),(1532,366,1625,497)]),
    (0,6,'1021','11 40',
     [204,232,191,184,180,86,208,154,220],
     [(616,529,732,644),(746,529,870,644),(909,529,976,644),(1013,529,1102,644),(1148,529,1206,644),(1252,529,1315,644),(1327,529,1436,644),(1492,529,1546,644),(1585,529,1625,644)]),
    (0,7,'1022','11 40',
     [204,215,104,25,420],
     [(1023,679,1130,797),(1145,679,1299,797),(1345,679,1423,797),(1480,679,1510,797),(1531,679,1622,797)]),
    (1,3,'1054','11 40',
     [126,5,25,152,[10,766],[10,766],105,74],
     [(530,45,589,161),(615,45,706,161),(766,45,789,161),(810,45,915,161),(959,45,1019,161),(1062,45,1125,161),(1143,45,1231,161),(1273,45,1340,161)]),
    (1,4,'1055','11 40',
     [127,174,[8,764]],
     [(1152,198,1228,321),(1231,198,1267,321),(1329,198,1340,321)]),
    (1,5,'1056','14 40',
     [92,92,87,197,491],
     [(785,358,885,480),(908,358,1010,480),(1058,358,1106,480),(1139,358,1206,480),(1250,358,1319,480)]),
    (1,6,'1057','11 40',
     [47,204,86,25,152],
     [(807,518,908,642),(928,518,1030,642),(1052,518,1104,642),(1191,518,1214,642),(1235,518,1337,642)]),
    (1,7,'1058','11 40',
     [204,76,186,25,127,174,187],
     [(572,678,676,801),(700,678,800,801),(840,678,933,801),(991,678,1019,801),(1062,678,1140,801),(1177,678,1216,801),(1268,678,1340,801)]),
]

UNDER = {('1020',3),('1020',4),('1020',5),('1056',4)}
SHAPE_ONLY = {
    690:[19,690], 532:[197,532], 491:[27,491],
    424:[10,424,766,770], 770:[10,424,766,770],
    10:[10,424,766,770], 766:[10,424,766,770],
    8:[8,501,764,768], 764:[8,501,764,768],
}


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
    payload = {
        'purpose':'Fresh source-only ten-row glyph/segmentation pilot; not an accepted large corpus or new ancient evidence',
        'source_pdf':'research/corpus/primary/koskenniemi_parpola1979.pdf',
        'source_sha256':SHA,
        'pdf_page_1based':30,
        'printed_page':29,
        'license':'CC BY 4.0, official Helsinki repository',
        'attribution':'Kimmo Koskenniemi and Asko Parpola, Corpus of Texts in the Indus Script, 1979',
        'annotator':'/root/corpus, AI visual comparisons; no expert adjudicator',
        'method':'Direct original PDF30 crops at8x, individual rechecks at20x; visual comparison to original PDF20/21 chart at4x and selected12x crops. No root glyph matcher, candidate outputs, predicted sequences or automatic OCR consulted.',
        'confidence_definition':'Qualitative clarity of direct source comparison, not a calibrated correctness probability. Ambiguous bar glyphs retain multiple source-chart codes.',
        'boundary_status':'Unknown for each printed row. One printed row may combine original lines/sides. Displayed gaps and classification strings are retained but not promoted to original traversal boundaries.',
        'release_protocol':{
            'root_prediction_frozen_notice':'Received from /root before saving/releasing complete reference.',
            'partial_unblinding':'Before the freeze, /root was told row1020 short4-over3 group and underline distinctions19/690,10/766/424/770,197/532, plus paired short glyph25. Root will retain this disclosure; remaining row/code truth was withheld until freeze notice.',
            'reference_prediction_access':'None: annotator has not opened prediction files or machine candidate outputs.',
        },
        'created_utc':datetime.now(timezone.utc).isoformat(),
        'rows':[],
    }
    for col,row,label,classification,readings,pixel_boxes in ROWS:
        assert len(readings)==len(pixel_boxes)
        xoffset=50 if col==0 else 348
        units=[]
        for pos,(reading,pixels) in enumerate(zip(readings,pixel_boxes)):
            codes=reading if isinstance(reading,list) else [reading]
            under=(label,pos) in UNDER
            box=[round(xoffset+pixels[0]/8,3),round(125+pixels[1]/8,3),round(xoffset+pixels[2]/8,3),round(125+pixels[3]/8,3)]
            shape_codes=sorted(set(c for code in codes for c in SHAPE_ONLY.get(code,[code])))
            unit={
                'position_visual_ltr_0based':pos,
                'code':codes[0] if len(codes)==1 else None,
                'strict_candidate_codes':codes,
                'shape_only_candidate_codes':shape_codes,
                'confidence':'high' if len(codes)==1 else 'unresolved_fine_code',
                'source_glyph_pdf_points_approx':box,
                'dashed_auxiliary_underline':under,
                'chart_references':[
                    {'code':code,'pdf_page_1based':REFS[code][0],'col_0based':REFS[code][1],'row_0based':REFS[code][2],'description':REFS[code][3]}
                    for code in codes
                ],
            }
            if len(codes)>1:
                unit['ambiguity_reason']='Original chart assigns distinct codes/ranks to visually similar full-height bar drawings. No rank was inferred from text context. The candidate set is cautious visual compatibility, not a proof that the font images are mathematically identical.'
            if label=='1056' and pos==2:
                unit['reinspection_note']='Body hatching and upper caret directly match the chart glyph87 at PDF20c2r9; this is a charted glyph, not treated as a generic editorial damage patch. Initial broad comparison to87/86/596 was resolved on12x original chart and20x source.'
            if label=='1021' and pos==6:
                unit['reinspection_note']='Three upper inner strokes rechecked at20x and compared to original U-family chart:208. Earlier provisional internal note413 was a two-versus-three count error, resolved before release.'
            units.append(unit)
        item={
            'pdf_page_1based':30,'col_0based':col,'row_0based':row,
            'printed_inscription_id':label,
            'classification_literal':classification,
            'source_crop':f'pdf30_col{col}_rows3_7_8x.png',
            'visual_ltr_codes':[u['code'] for u in units],
            'visual_ltr_candidate_codes':[u['strict_candidate_codes'] for u in units],
            'glyph_unit_count':len(units),
            'segmentation_confidence':'high_qualitative',
            'original_side_line_boundary':'unknown',
            'units':units,
        }
        if label=='1018':
            item['layout_note']='Large displayed gap after first U-circle unit; classification48640 includes third-position6, defined as two-sided object. It suggests a physical boundary but its exact reconstruction is not certified here.'
        if label=='1020':
            item['underline_span_note']='Continuous dashed auxiliary line spans the grouped short array, the adjacent tall triplet and the following U-circle glyph (positions3–5), not the complete row.'
        if label=='1054':
            item['segmentation_note']='Two groups of three tall bars separated by a wider gap than within-group spacing; preserved as two drawn units. No numerical value assigned.'
        payload['rows'].append(item)
    payload['summary']={
        'printed_rows':len(payload['rows']),
        'glyph_units':sum(r['glyph_unit_count'] for r in payload['rows']),
        'single_code_units':sum(u['code'] is not None for r in payload['rows'] for u in r['units']),
        'ambiguous_fine_code_units':sum(u['code'] is None for r in payload['rows'] for u in r['units']),
        'auxiliary_underlined_units':sum(u['dashed_auxiliary_underline'] for r in payload['rows'] for u in r['units']),
    }
    (OUT/'manual_reference.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(payload['summary']))


if __name__=='__main__':
    main()
