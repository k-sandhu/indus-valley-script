"""Serialize visually read chart labels; this script performs no OCR or matching.

Arrays below were read from original PDF20, with full columns at 6x, all rows
reinspected at 12x, and specific ambiguous digits at 20x. Numerical geometry
only describes conservative source regions; it does not recognize labels.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / 'koskenniemi_parpola1979.pdf'
SOURCE_SHA = '7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27'

READINGS = {
    1: (
        [19,19,20,20,21,22,23,23,24,25,25,26,26,27,28,29,30,30,31,31,32,33,34,35,35,36,37,37,38,39,40,40,41,42,42],
        [148,786,149,772,741,307,135,427,449,388,237,138,763,353,336,697,340,305,136,450,570,348,137,139,390,304,316,718,366,417,140,96,141,142,780],
    ),
    2: (
        [43,43,44,44,45,45,46,47,47,48,49,50,50,51,51,52,53,54,54,55,56,56,57,57,58,58,59,59,60,60,61,62,62,62,63],
        [288,359,77,452,328,269,408,323,264,87,354,177,517,513,321,546,521,588,325,558,178,461,522,669,179,463,530,172,86,568,520,180,236,541,512],
    ),
    3: (
        [63,64,65,66,66,67,67,68,69,70,70,71,71,72,73,73,74,75,75,75,76,76,77,77,78,79,80,81,82,83,84,84,85,85,86],
        [120,181,183,188,531,503,263,515,524,356,747,189,489,527,184,460,368,168,579,695,190,544,193,490,357,781,419,722,195,194,191,557,443,127,126],
    ),
    4: (
        [86,86,87,88,88,89,89,90,91,91,91,92,92,93,94,94,95,95,96,97,98,98,99,100,101,102,103,103,104,105,106,107,108,108,109],
        [151,506,748,466,547,84,801,592,45,44,523,42,182,350,247,464,43,404,212,733,51,486,26,470,795,382,187,295,476,272,238,342,174,573,561],
    ),
}
X_BOUNDS = {0:(54,105),1:(105,157),2:(156,208),3:(208,260),4:(260,313)}
CONFIDENCE_DESCRIPTION = (
    'High means the printed numeric label appeared unambiguous after direct '
    'high-resolution visual reinspection. This is qualitative, not a '
    'calibrated probability. No labels were inferred from rank order, sign '
    'shape, neighbouring values, OCR, font models or machine matches.'
)
RECHECKS = {
    (1,28): 'First 6x reading 356 corrected to 366 on 12x original.',
    (2,25): 'Possible 453/463 at 6x resolved to 463 on original 20x crop col2_row25_label_20x.png.',
    (3,16): 'First 6x reading 358 corrected to 368 on 12x original.',
    (4,1): 'Upper 86 and lower 506 rechecked at 12x.',
    (4,18): 'Upper rank 96 rechecked at 12x.',
    (4,21): 'Initial 6x486, then12x485, then fresh20x favours486. Preserve candidate union[485,486] with medium confidence; initial high-confidence485 was too strong. Source crop numeric_recheck_c4_r21_20x.png.',
    (4,25): 'First 6x reading 352 corrected to 382 on 12x original.',
    (4,28): 'First 6x reading 475 corrected to 476 on original 20x crop col4_row28_label_20x.png.',
    (4,30): 'First upper-rank reading 105 corrected to 106 on 12x original.',
}


def common():
    return {
        'purpose': 'Independent manual numeric-label reference, not glyph or inscription transcription',
        'source_pdf': 'research/corpus/primary/koskenniemi_parpola1979.pdf',
        'source_sha256': SOURCE_SHA,
        'pdf_page_1based': 20,
        'printed_page': 19,
        'source_page_pdf_points': [0,0,595,841],
        'license': 'CC BY 4.0, official Helsinki repository/portal',
        'attribution': 'Kimmo Koskenniemi and Asko Parpola, 1979, Corpus of Texts in the Indus Script',
        'annotator': '/root/corpus, AI visual annotation, no expert adjudicator',
        'method': 'Direct original PDF raster crops at 6x; every row rechecked at 12x; selected digits at 20x. No OCR, machine labels, templates or predicted inscriptions consulted.',
        'number_definition': 'Upper printed integer is rank; lower printed integer is the stable Finnish sign/variant code. They are separately read, preserving repeated ranks and codes.',
        'confidence_definition': CONFIDENCE_DESCRIPTION,
        'coordinate_definition': 'PDF point coordinates. Nominal cell boxes are conservative visually chosen row regions using a 20.05 point pitch, not exact ink bounds; they deliberately overlap adjacent whitespace. Column and check crops have exact render clip coordinates.',
        'created_utc': datetime.now(timezone.utc).isoformat(),
    }


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    payload = common()
    payload['columns'] = []
    for col, (ranks, codes) in READINGS.items():
        assert len(ranks) == len(codes) == 35
        x0, x1 = X_BOUNDS[col]
        rows = []
        for row, (rank, code) in enumerate(zip(ranks, codes)):
            y0 = round(64 + 20.05*row, 2)
            item = {
                'row_0based': row,
                'col_0based': col,
                'rank': rank,
                'printed_rank': str(rank),
                'code': code,
                'printed_code': str(code),
                'rank_confidence': 'high',
                'code_confidence': 'high',
                'confidence': 'high',
                'alternatives': [],
                'candidate_codes': [code],
                'unresolved': False,
                'source_cell_pdf_points': [x0,y0,x1,round(y0+25,2)],
            }
            if (col,row) in RECHECKS:
                item['reinspection_note'] = RECHECKS[(col,row)]
            if (col,row)==(4,21):
                item['code_confidence']=item['confidence']='medium'
                item['alternatives']=[485]
                item['candidate_codes']=[485,486]
            rows.append(item)
        payload['columns'].append({
            'col_0based': col,
            'whole_column_crop': f'pdf20_col{col}_6x.png',
            'whole_column_crop_pdf_points': [x0,60,x1,774],
            'reinspection_crops': [f'pdf20_col{col}_{part}_12x.png' for part in ['top','middle','bottom']],
            'rows': rows,
        })
    payload['cell_count'] = sum(len(c['rows']) for c in payload['columns'])
    (BASE / 'manual_columns1_4.json').write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')

    # Preserve the initial reference, rather than silently replacing its error.
    original = BASE.parent / '1979_chart_pdf20_column0_manual.json'
    initial = json.loads(original.read_text(encoding='utf-8'))
    revised = common()
    revised['column_0based'] = 0
    revised['supersedes_for_numeric_labels'] = 'research/corpus/primary/1979_chart_pdf20_column0_manual.json'
    revised['original_reference_sha256'] = hashlib.sha256(original.read_bytes()).hexdigest()
    revised['original_reference_preserved'] = True
    revised['corrections'] = [{
        'row_0based':4, 'field':'code','initial_value':585,'revised_value':586,
        'evidence':'col0_row4_label_20x.png, exact clip [54,144,80,168]; last numeral curved 6, not angular 5',
        'reason':'Initial 4x visual reading error, corrected from higher-resolution original. No machine prediction consulted.',
    }]
    revised['auxiliary_annotation_definition'] = 'Dashed horizontal line below glyph is a source auxiliary uncertainty annotation, not part of glyph: 1979 section 5.4 printed p15/PDF16, referring to 6.6 printed p17/PDF18.'
    revised['underline_reinspection'] = 'All 35 rows inspected on 12x original. Row34 bottom inspected additionally through PDF y802 at 16x: solid platform is glyph; no dashed auxiliary underline present.'
    dashed_rows = {2,3,6,8,10,14,17,20,21,23,25,27,30,32}
    revised['rows'] = []
    for item in initial['rows']:
        row = item['row_0based']
        item = dict(item)
        item['col_0based'] = 0
        if row == 4:
            item['code'] = 586
            item['printed_code'] = '586'
            item['reinspection_note'] = revised['corrections'][0]['reason']
        y0 = round(64+20.05*row,2)
        item['source_cell_pdf_points'] = [54,y0,105,round(y0+25,2)]
        item['rank_confidence'] = item['code_confidence'] = 'high'
        item['alternatives'] = []
        item['unresolved'] = False
        item['dashed_auxiliary_underline'] = row in dashed_rows
        revised['rows'].append(item)
    revised['cell_count'] = 35
    revised['dashed_auxiliary_count'] = len(dashed_rows)
    (BASE / 'column0_reinspection.json').write_text(json.dumps(revised,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'new_cells':payload['cell_count'],'column0_reinspected':35,'column0_corrections':revised['corrections'],'dashed_auxiliary_count':len(dashed_rows)}))


if __name__ == '__main__':
    main()
