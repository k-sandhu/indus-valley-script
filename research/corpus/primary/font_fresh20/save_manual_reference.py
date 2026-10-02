"""Serialize independent source-only annotations for the frozen fresh20 pilot."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import runpy

OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'koskenniemi_parpola1979.pdf'
SHA='7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27'
# Only our prior direct-source reference is reused; no root or machine files.
REFS=dict(runpy.run_path(str(OUT.parent/'font_row_audit/save_manual_reference.py'))['REFS'])
REFS.update({
    242:(20,8,15,'Two parallel broad curved strokes'),
    168:(20,3,17,'Oval at left joined to two angular right branches'),
    509:(20,5,19,'Upper short vertical pair with dashed auxiliary underline'),
    421:(21,8,27,'Circle with inward upper V and dashed auxiliary underline'),
    9:(20,7,13,'Two full-height vertical bars, rank145'),
    765:(20,5,30,'Two full-height vertical bars, rank122'),
    134:(20,0,16,'Standing figure with U-shaped upper head/prongs'),
    179:(20,2,24,'Plain fish with horizontal internal divider'),
    205:(21,5,32,'U with one upper short vertical stroke inside'),
    211:(21,6,12,'U with one curved inner branch at each upper side'),
    30:(21,4,4,'Upper rectangular enclosure with small loop above; no lower edge'),
    68:(21,3,4,'Rectangle with top/bottom inner ticks and two middle horizontal strokes'),
    541:(20,2,33,'Upper-horned fish with dashed auxiliary underline'),
    13:(21,9,15,'Narrow diagonal-hatched editorial marker'),
    597:(21,9,14,'Narrow diagonal-hatched editorial marker'),
    18:(20,6,12,'Short strokes in two rows of three'),
    700:(21,8,4,'Outer circle enclosing diagonally crossed small inner oval'),
    38:(21,1,16,'Opposing triangle-like wings around two central stacked ovals'),
    155:(20,8,3,'Curved upright enclosing left oval, with dashed auxiliary underline'),
    512:(20,2,34,'Horned fish with four surrounding short strokes'),
    53:(20,9,33,'Tall sloping staff with small divided triangular flag to right'),
    189:(20,3,11,'Hatched central bird-like body with two upper projections and curved lower legs'),
    163:(21,8,12,'Circle divided by three crossing diameters'),
    138:(20,1,11,'Standing figure with combed upper right arm'),
    12:(20,7,21,'Five full-height vertical bars'),
    192:(21,7,34,'Two large upper ovals joined by a central descending staff'),
    513:(20,2,13,'Plain fish with four surrounding short strokes'),
    2:(20,5,28,'Pair of short vertical strokes at lower/middle position'),
    123:(21,2,14,'Wide four-armed angled cross outline'),
    106:(21,9,13,'Broad diagonal-hatched editorial marker'),
    599:(21,9,12,'Broad diagonal-hatched editorial marker'),
    685:(20,0,21,'Horned standing figure between two similarly curved brackets, underlined'),
    164:(21,8,19,'Diamond with inward cross-like notches'),
    248:(21,6,10,'U with trident-like tips on both upper sides'),
    190:(20,3,20,'Upright oval with multiple radiating strokes'),
    70:(21,9,20,'Large empty rectangle: editorial whole-text-loss marker'),
    461:(20,2,21,'Fish with short inner vertical stem, underlined'),
    29:(21,3,13,'Tall rectangular outline with small squares/feet at lower outer corners'),
    139:(20,1,23,'Standing figure joined to a tall D-shaped right outline'),
    42:(20,4,11,'Tall staff with upper horizontal comb'),
    51:(20,4,20,'Tall E-like staff with multiple horizontal strokes'),
    20:(20,6,18,'Grouped short strokes: four upper and four lower'),
    1:(20,5,22,'Single upper short vertical stroke'),
    214:(20,5,14,'Three upper staffs with horizontal ticks joined on a curved lower base'),
    111:(21,7,15,'Simple diamond outline'),
    133:(20,0,26,'Standing figure with plain upper central stem'),
    505:(20,0,18,'Horned standing figure between two similarly curved brackets'),
    243:(20,8,27,'Five parallel broad curves'),
    36:(21,1,6,'Connected double opposing-triangle/bow-tie outline'),
    514:(20,7,30,'S-like curve with four short strokes at left and three at right'),
    116:(21,8,7,'Oval outline with three slanting internal strokes'),
    110:(20,0,31,'Two connected standing figures'),
})

ROWS=[
    (0,8,'1023','11 40',[204,242,186,177,[9,765],168,509,421]),
    (0,9,'1024','11 40',[204,134,86,179,205,154,220]),
    (0,10,'1025','11 40',[127,19]),
    (0,11,'1026','11 91',[204,211,197,25,[9,765],30,[9,765]]),
    (0,19,'1034','11 91',[204,68,541,[13,597]]),
    (0,20,'1035','11 40',[126,18,25,700,38]),
    (0,21,'1036','11 40',[420,155,512,53,189]),
    (0,22,'1037','11 40',[163,138,12,192]),
    (0,33,'1048','11 40',[513,[9,765],2,126,123]),
    (1,8,'1059','11 40',[[106,599],[106,599],685,25,164]),
    (1,9,'1060','11 40',[204,248,86,2,126,139,190]),
    (1,11,'1062','11 40',[70]),
    (1,12,'1063','11 40',[70]),
    (1,14,'1065','11 40',[95,[10,766],197,461,180,25,29,139,[9,765]]),
    (1,17,'1068','11 40',[95,[10,766],197,177,42]),
    (1,19,'1070','11 40',[51,139,208]),
    (1,20,'1071','14 40',[127,20,1,177,214,111]),
    (1,21,'1072','11 40',[133,204,505,243,36]),
    (1,23,'1074','11 40',[204,514,25,163]),
    (1,33,'1084','11 40',[50,116,110]),
]
UNDER={('1023',6),('1023',7),('1034',2),('1036',1),('1059',2),('1065',3)}
AUX={('1034',3):'editorial_unbounded_end_damage',('1059',0):'editorial_hatched_damage_or_inaccessible_span',('1059',1):'editorial_hatched_damage_or_inaccessible_span',('1062',0):'editorial_entire_text_lost',('1063',0):'editorial_entire_text_lost'}
SHAPE_ALIASES={
    9:[9,543,765,769],765:[9,543,765,769],
    10:[10,424,766,770],766:[10,424,766,770],
    509:[25,509],421:[420,421],541:[180,541],155:[155,220],
    685:[505,685],461:[178,461],
}


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SHA
    manifest=json.loads((OUT/'source_selection_manifest.json').read_text(encoding='utf-8'))
    chosen={(r['col_0based'],r['row_0based']):r for r in manifest['rows']}
    assert {(c,r) for c,r,*_ in ROWS}==set(chosen)
    payload={
        'purpose':'Fresh20 source-only manual drawn-unit/glyph reference for a frozen digitization pilot',
        'source_pdf':'research/corpus/primary/koskenniemi_parpola1979.pdf',
        'source_sha256':SHA,'pdf_page_1based':30,'printed_page':29,
        'license':'CC BY 4.0, official University of Helsinki repository',
        'attribution':'Kimmo Koskenniemi and Asko Parpola, Corpus of Texts in the Indus Script, 1979',
        'annotator':'/root/corpus, AI visual inspection, no expert adjudicator',
        'source_chart_reference':'Original PDF20 and21, direct rendered chart comparison, with selected high-resolution checks',
        'method':'Manual source-only visual comparison, no machine glyph predictions, candidates or page30 matcher consulted. Our earlier manually read source references were reused only as source-chart locators.',
        'selection':{'random_seed':20261015,'rule':manifest['selection_rule'],'rows':[[c,r] for c,r,*_ in ROWS]},
        'release_protocol':{
            'full_blind_until_freeze':True,
            'details_withheld':'No selected-row codes, counts or glyph details sent to root before its predictions-complete notice.',
            'freeze_notice_received':'Root reported research/visual_digitization/font_fresh20/predictions_before_gold.json complete before release.',
            'prediction_file_access':'None. Searches and reads for this pilot were confined to corpus sources and our own direct-source annotations.',
        },
        'confidence_definition':'High is qualitative visual clarity after source-chart comparison, not calibrated accuracy. Ambiguous fine codes retain candidate sets rather than contextual inference.',
        'unit_count_definition':'Counts are modern drawn units in the1979 publication, including editorial auxiliary marks. They are not ancient inscription length, words, morphemes, numerals, physical sides or original lines.',
        'boundary_policy':'All original physical side/line boundaries remain unknown. Source printed rows can combine multiple original lines/sides. These lists preserve visual LTR layout only.',
        'auxiliary_definitions_source':'1979 section6.6 printed16–17/PDF17–18. Empty large rectangle denotes broken formerly inscribed object with no text surviving; hatched patches distinguish uncertain/lost or inaccessible spans, whose original sign count is not assumed here.',
        'created_utc':datetime.now(timezone.utc).isoformat(),'rows':[],
    }
    for col,row,label,classification,readings in ROWS:
        m=chosen[(col,row)]
        units=[]
        for pos,reading in enumerate(readings):
            codes=reading if isinstance(reading,list) else [reading]
            kind=AUX.get((label,pos),'charted_glyph')
            unit={
                'position_visual_ltr_0based':pos,
                'code':codes[0] if len(codes)==1 else None,
                'strict_candidate_codes':codes,
                'shape_only_candidate_codes':sorted({s for code in codes for s in SHAPE_ALIASES.get(code,[code])}),
                'confidence':'high_qualitative' if len(codes)==1 else 'unresolved_fine_code',
                'unit_kind':kind,
                'dashed_auxiliary_underline':(label,pos) in UNDER,
                'chart_references':[{'code':code,'pdf_page_1based':REFS[code][0],'col_0based':REFS[code][1],'row_0based':REFS[code][2],'description':REFS[code][3]} for code in codes],
            }
            if kind!='charted_glyph':
                unit['original_ancient_glyph_count']='unknown'
                unit['semantic_value']=None
                unit['marker_note']='Modern editorial graphic; never counted as one ancient glyph or assigned a word/number value.'
            elif len(codes)>1:
                unit['ambiguity_reason']='Distinct original chart codes/ranks have visually similar full-height bars. Exact source code is not forced from local context.'
            units.append(unit)
        item={
            'pdf_page_1based':30,'col_0based':col,'row_0based':row,
            'printed_inscription_id':label,'classification_literal':classification,
            'source_crop':m['crop'],'source_crop_sha256':m['sha256'],
            'source_crop_pdf_points':m['clip_pdf_points'],
            'drawn_unit_count':len(units),
            'charted_glyph_drawn_units':sum(u['unit_kind']=='charted_glyph' for u in units),
            'editorial_auxiliary_drawn_units':sum(u['unit_kind']!='charted_glyph' for u in units),
            'auxiliary_only':all(u['unit_kind']!='charted_glyph' for u in units),
            'source_contains_loss_or_inaccessibility':any(u['unit_kind']!='charted_glyph' for u in units),
            'visual_ltr_codes':[u['code'] for u in units],
            'visual_ltr_candidate_codes':[u['strict_candidate_codes'] for u in units],
            'original_side_line_boundary':'unknown','original_ancient_text_length':'not_inferred',
            'units':units,
        }
        if label=='1059':
            item['damage_note']='Two separately drawn wide hatched patches form a source editorial span; their number is not assumed to equal two lost ancient signs or to establish an original side.'
        if label=='1034':
            item['damage_note']='Narrow terminal hatched marker has unknown lost-end extent. Other surviving glyphs retained.'
        if label in {'1062','1063'}:
            item['damage_note']='Only a large empty editorial rectangle survives in the printed row. No ancient glyph sequence is reconstructed.'
        if label=='1074':
            item['segmentation_note']='The charted compound514 includes left four/right three short strokes around an S-like curve. A further upper short pair is a separate glyph25; high-resolution source and chart crops preserve this distinction.'
        if label=='1071':
            item['reinspection_note']='Four-over-four short group is one charted drawn unit20. Isolated upper short stroke compared to original short-marker family is1, not an inferred missing glyph.'
        payload['rows'].append(item)
    payload['summary']={
        'selected_printed_rows':len(payload['rows']),
        'drawn_units':sum(r['drawn_unit_count'] for r in payload['rows']),
        'charted_glyph_drawn_units':sum(r['charted_glyph_drawn_units'] for r in payload['rows']),
        'editorial_auxiliary_drawn_units':sum(r['editorial_auxiliary_drawn_units'] for r in payload['rows']),
        'auxiliary_only_rows':sum(r['auxiliary_only'] for r in payload['rows']),
        'rows_with_loss_or_inaccessible_spans':sum(r['source_contains_loss_or_inaccessibility'] for r in payload['rows']),
        'single_code_drawn_units':sum(u['code'] is not None for r in payload['rows'] for u in r['units']),
        'ambiguous_fine_code_drawn_units':sum(u['code'] is None for r in payload['rows'] for u in r['units']),
        'dashed_underlined_drawn_units':sum(u['dashed_auxiliary_underline'] for r in payload['rows'] for u in r['units']),
    }
    file=OUT/'manual_reference.json'
    file.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'summary':payload['summary'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}))


if __name__=='__main__':
    main()
