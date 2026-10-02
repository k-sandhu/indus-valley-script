"""Consolidate manual source labels while retaining errors and ambiguity."""
from __future__ import annotations
import json,hashlib,csv
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/chart_reference'

def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))

def compare_fresh():
    OUT.mkdir(exist_ok=True)
    first=load('research/root_chart/manual_columns.json')
    audit=load('research/literature/chart_complete/fresh21_audit.json')
    comparisons=[]
    source=fitz.open(ROOT/first['source_pdf'])
    for r in audit['rows']:
        c,row=r['column_0based'],r['row_0based']
        rank=first['columns'][str(c)]['ranks'][row]
        code=first['columns'][str(c)]['codes'][row]
        correct_rank=rank==r['upper_rank'];correct_code=code==r['lower_stable_finnish_code']
        item={'column':c,'row':row,'root_rank_before_fresh_audit':rank,'root_code_before_fresh_audit':code,
              'independent_rank':r['upper_rank'],'independent_code':r['lower_stable_finnish_code'],
              'rank_agreement':correct_rank,'code_agreement':correct_code}
        if not(correct_rank and correct_code):
            path=OUT/f'fresh_mismatch_c{c}_r{row}.png'
            source[20].get_pixmap(matrix=fitz.Matrix(12,12),clip=fitz.Rect(*r['clip_points'])).save(path)
            item['original_crop']=str(path.relative_to(ROOT))
        comparisons.append(item)
    result={'design':'Fresh blind independent numeric spotcheck of root first pass, excluding previous15 audited cells.',
            'seed':audit['seed'],'n':len(comparisons),
            'joint_agreement':sum(x['rank_agreement'] and x['code_agreement'] for x in comparisons),
            'rank_agreement':sum(x['rank_agreement'] for x in comparisons),
            'code_agreement':sum(x['code_agreement'] for x in comparisons),
            'root_source_sha256':hashlib.sha256((ROOT/'research/root_chart/manual_columns.json').read_bytes()).hexdigest(),
            'audit_sha256':hashlib.sha256((ROOT/'research/literature/chart_complete/fresh21_audit.json').read_bytes()).hexdigest(),
            'comparisons':comparisons,'scope':'Numeric digit readings only; not glyph identity or semantic validation.'}
    (OUT/'fresh20_before_correction.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='comparisons'},indent=2))

def manual_labels(final=False):
    output=[]
    a=load('research/corpus/primary/chart_complete/column0_reinspection.json')
    b=load('research/corpus/primary/chart_complete/manual_columns1_4.json')
    for col,rows in [(0,a['rows'])]+[(c['col_0based'],c['rows']) for c in b['columns']]:
        for r in rows:
            output.append({'pdf_page':20,'column':col,'row':r['row_0based'],'rank':r['rank'],
                'code':r['code'],'alternatives':r.get('alternatives',[]),'numeric_confidence':r['confidence'],
                'source':'corpus independent manual reinspection',
                'dashed_auxiliary':r.get('dashed_auxiliary_underline',None)})
    for r in load('research/literature/chart_complete/manual_numeric_labels.json')['rows']:
        output.append({'pdf_page':20,'column':r['column_0based'],'row':r['row_0based'],'rank':r['upper_rank'],
            'code':r['lower_stable_finnish_code'],'alternatives':r.get('lower_alternatives',[]),
            'numeric_confidence':r['lower_confidence'],'source':'literature independent manual reading',
            'dashed_auxiliary':None})
    if final:
        for r in load('research/literature/chart_complete/full21_audit.json')['rows']:
            output.append({'pdf_page':21,'column':r['column_0based'],'row':r['row_0based'],'rank':r['upper_rank'],
                'code':r['lower_stable_finnish_code'],'alternatives':r.get('lower_alternatives',[]),
                'numeric_confidence':r['lower_confidence'],
                'source':'Independent full337 reading plus original-crop disagreement adjudication; alternatives preserved.',
                'dashed_auxiliary':None})
        assert len(output)==687
        assert len({(r['pdf_page'],r['column'],r['row']) for r in output})==687
        # Later duplicate alerts locate source checks, not an assumption of unique codes.
        adjudication=load('research/literature/chart_complete/duplicate_labels/adjudication.json')
        bykey={(r['pdf_page'],r['column'],r['row']):r for r in output}
        for reviewed in adjudication['rows']:
            key=(reviewed['pdf_page'],reviewed['column_0based'],reviewed['row_0based'])
            target=bykey[key]
            target.update(code=reviewed['lower_stable_finnish_code'],rank=reviewed['upper_rank'],
                alternatives=reviewed.get('lower_alternatives',[]),numeric_confidence=reviewed['lower_confidence'],
                source='Later original-source duplicate-label reinspection; historical validation inputs unchanged.')
        # Two source readers disagree here. Preserve every explicit reading, no context repair.
        target=bykey[20,4,21]
        target.update(code=465,alternatives=[485,486],numeric_confidence='medium',
            source='Source readers disagree: literature465; corpus485/486. Full union retained.')
        target=bykey[20,4,1]
        target.update(rank=86,rank_alternatives=[],
            source='Lower506 retained. Both source readers concur rank86 after original24x reinspection; previous85 archived.')
        return sorted(output,key=lambda r:(r['pdf_page'],r['column'],r['row']))
    first=load('research/root_chart/manual_columns.json')
    # Known independent fresh-audit corrections do not turn that audit into new validation.
    corrections={(r['column_0based'],r['row_0based']):r for r in
                 load('research/literature/chart_complete/fresh21_audit.json')['rows']}
    for c,values in first['columns'].items():
        for row,(rank,code) in enumerate(zip(values['ranks'],values['codes'])):
            cnum=int(c);r=corrections.get((cnum,row))
            if r:rank,code=r['upper_rank'],r['lower_stable_finnish_code']
            ambiguous=values.get('ambiguous_rows',{}).get(str(row),{})
            output.append({'pdf_page':21,'column':cnum,'row':row,'rank':rank,'code':code,
                'alternatives':ambiguous.get('alternatives',[]),'numeric_confidence':ambiguous.get('confidence','high'),
                'source':'root manual pass with explicitly recorded independent corrections; full reinspection pending',
                'dashed_auxiliary':row in values['dashed_annotation_rows']})
    assert len(output)==687
    assert len({(r['pdf_page'],r['column'],r['row']) for r in output})==687
    return sorted(output,key=lambda r:(r['pdf_page'],r['column'],r['row']))

def save_labels(final=False):
    OUT.mkdir(exist_ok=True)
    result={'status':('Manual numeric reference with uncertainty retained; NOT a glyph-transcribed corpus.' if final else 'Manual numeric reference; NOT a glyph-transcribed corpus. PDF21 full independent reinspection pending.'),
        'source_sha256':'7bfc35f2a8bbcb58f13c42e1835f5b3ebd17a1f9947786b6c5933623df83cf27',
        'license':'CC BY 4.0; attribute Koskenniemi and Parpola (1979), Corpus of Texts in the Indus Script; official Helsinki source.',
        'rows':manual_labels(final),
        'limitations':['Qualitative numeric confidence is not calibrated accuracy.',
            'Repeated codes/ranks retained; auxiliary uncertainty graphics are not lexical distinctions.',
            'Numeric label correctness does not certify image crop or glyph segmentation.',
            'No chart labels are analytical corpus inputs.']}
    name='manual_numeric_reference.json' if final else 'manual_numeric_reference_provisional.json'
    for r in result['rows']:r.setdefault('rank_alternatives',[])
    result['lower_code_ambiguous_cells']=sum(bool(r['alternatives']) for r in result['rows'])
    result['upper_rank_ambiguous_cells']=sum(bool(r['rank_alternatives']) for r in result['rows'])
    result['numeric_ambiguous_cells']=sum(bool(r['alternatives'] or r['rank_alternatives']) for r in result['rows'])
    result['source_url']='https://researchportal.helsinki.fi/en/publications/corpus-of-texts-in-the-indus-script/'
    result['adjudication_limit']='AI visual readers, no expert certification. Fresh20 and initial OCR failures remain separate and unchanged.'
    (OUT/name).write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (OUT/name.replace('.json','.csv')).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['pdf_page','column','row','rank','rank_alternatives','code','alternatives','numeric_confidence','source','dashed_auxiliary']);writer.writeheader();writer.writerows(result['rows'])
    print(json.dumps({'cells':len(result['rows']),'ambiguous':result['numeric_ambiguous_cells'],'path':name}))

if __name__=='__main__':
    import sys
    save_labels('final' in sys.argv) if 'labels' in sys.argv else compare_fresh()
