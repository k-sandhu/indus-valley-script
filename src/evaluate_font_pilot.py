"""Evaluate every frozen image-only pilot endpoint; retain partial unblinding."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/visual_digitization/fresh_font_pilot_corrected'

def edit(pred,truth):
    n,m=len(pred),len(truth);d=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1):d[i][0]=i
    for j in range(m+1):d[0][j]=j
    for i in range(1,n+1):
        for j in range(1,m+1):
            d[i][j]=min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(not bool(pred[i-1]&truth[j-1])))
    return d[n][m]

def main():
    inp=OUT/'predictions_before_gold.json';gold=ROOT/'research/corpus/primary/font_row_audit/manual_reference.json'
    pred=json.loads(inp.read_text());truth=json.loads(gold.read_text());ref={int(r['printed_inscription_id']):r for r in truth['rows']}
    assert pred['complete'] and len(pred['rows'])==len(ref)==10
    result={'scope':'Frozen image-only glyph/segmentation pilot; AI source reference, not expert gold or archaeological decipherment.',
        'prediction_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),'reference_sha256':hashlib.sha256(gold.read_bytes()).hexdigest(),
        'partial_unblinding':truth['release_protocol']['partial_unblinding'],
        'crop_repair':'Initial wide-left template crops included numeric label ink. That source-observed defect was repaired, all four predeclared segmentation penalties retained. Partial row1020 information arrived during this repair. Outputs with contaminated templates remain separate.',
        'numeric_label_limitation':'Template labels were manual provisional readings before complete independent chart adjudication; segmentation/codes cannot be certified by this pilot.',
        'endpoints':{}}
    for penalty in ['0.5','1','2','4']:
        rows=[]
        for r in pred['rows']:
            g=ref[r['id']];tokens=r['variants'][penalty]['tokens']
            row={'id':r['id'],'true_units':g['glyph_unit_count'],'predicted_units':len(tokens)}
            for kind in ['strict','shape_only']:
                sets=[set(u[f'{kind}_candidate_codes']) for u in g['units']]
                for top in [1,5]:
                    guesses=[{int(a['code_ocr']) for a in t['alternatives'][:top] if a['code_ocr'] is not None} for t in tokens]
                    distance=edit(guesses,sets)
                    row[f'{kind}_top{top}_edit_distance']=distance
                    row[f'{kind}_top{top}_row_compatible']=distance==0
            rows.append(row)
        summaries={}
        for name,selected in [('all10',rows),('excluding_partially_disclosed1020',[r for r in rows if r['id']!=1020])]:
            sums={'rows':len(selected),'true_units':sum(r['true_units'] for r in selected),
                  'predicted_units':sum(r['predicted_units'] for r in selected),
                  'correct_unit_count_rows':sum(r['true_units']==r['predicted_units'] for r in selected)}
            for kind in ['strict','shape_only']:
                for top in [1,5]:
                    key=f'{kind}_top{top}'
                    sums[key]={'summed_edit_distance':sum(r[key+'_edit_distance'] for r in selected),
                              'candidate_compatible_whole_rows':sum(r[key+'_row_compatible'] for r in selected)}
            summaries[name]=sums
        result['endpoints'][penalty]={'summary':summaries,'rows':rows}
    (OUT/'evaluation_all_endpoints.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v['summary'] for k,v in result['endpoints'].items()},indent=2))
if __name__=='__main__':main()
