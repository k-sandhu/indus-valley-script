"""Post-reference geometry development diagnostic, preserving frozen matcher.

This diagnostic uses already-revealed source truth to obtain corrected crop
geometry. It is not fresh validation. Original prediction/evaluation files are
read-only, and frozen numeric alternatives and penalty1 remain unchanged.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import time

from PIL import Image

from audit_font_pilot import distance

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
import font_pilot as font

FROZEN = ROOT/'research/visual_digitization/font_fresh20'
PDF = ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf'
GOLD = ROOT/'research/corpus/primary/font_fresh20/manual_reference.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vertical_bounds(row):
    """Only declared source coordinates are read; glyph codes/counts ignored."""
    if 'recommended_crop_xyxy_2x' in row:
        _,y0,_,y1=row['recommended_crop_xyxy_2x']
        return [math.floor(y0),math.ceil(y1)],'2x image pixels; inclusive start/exclusive stop'
    if 'recommended_vertical_bounds_2x' in row:
        y0,y1=row['recommended_vertical_bounds_2x']
        return [math.floor(y0),math.ceil(y1)],'2x image pixels'
    if 'recommended_vertical_bounds_pdf_points' in row:
        y0,y1=row['recommended_vertical_bounds_pdf_points']
        return [math.floor(2*y0),math.ceil(2*y1)],'PDF points multiplied by2'
    raise ValueError('Geometry row must explicitly supply recommended_vertical_bounds_2x or recommended_vertical_bounds_pdf_points')


def evaluate(path, out):
    prediction=json.loads(path.read_text())
    reference=json.loads(GOLD.read_text())
    gold={int(r['printed_inscription_id']):r for r in reference['rows']}
    assert prediction['complete'] and len(prediction['rows'])==len(gold)==20
    ids=[r['id'] for r in prediction['rows']]
    assert len(set(ids))==20 and set(ids)==set(gold)
    scored=[]
    for r in prediction['rows']:
        g=gold[r['id']]
        assert len(g['units'])==g['drawn_unit_count']
        x={'id':r['id'],'true_drawn_units':g['drawn_unit_count'],
           'charted_glyph_drawn_units':g['charted_glyph_drawn_units'],
           'editorial_auxiliary_drawn_units':g['editorial_auxiliary_drawn_units'],
           'predicted_units':len(r['tokens'])}
        for kind in ['strict','shape_only']:
            target=[set(u[kind+'_candidate_codes']) for u in g['units']]
            for top in [1,5]:
                guesses=[{code for a in t['alternatives'][:top] for code in a['manual_numeric_code_candidates']} for t in r['tokens']]
                key=f'{kind}_top{top}'
                x[key+'_edit_distance']=distance(guesses,target)
                x[key+'_row_compatible']=x[key+'_edit_distance']==0
                x[key+'_candidate_widths']=list(map(len,guesses))
        scored.append(x)
    summary={'rows':len(scored),'true_drawn_units':sum(r['true_drawn_units'] for r in scored),
             'charted_glyph_drawn_units':sum(r['charted_glyph_drawn_units'] for r in scored),
             'editorial_auxiliary_drawn_units':sum(r['editorial_auxiliary_drawn_units'] for r in scored),
             'predicted_units':sum(r['predicted_units'] for r in scored),
             'correct_drawn_unit_count_rows':sum(r['true_drawn_units']==r['predicted_units'] for r in scored)}
    for kind in ['strict','shape_only']:
        for top in [1,5]:
            key=f'{kind}_top{top}'; widths=[w for r in scored for w in r[key+'_candidate_widths']]
            summary[key]={'summed_edit_distance':sum(r[key+'_edit_distance'] for r in scored),
                          'candidate_compatible_whole_rows':sum(r[key+'_row_compatible'] for r in scored),
                          'mean_candidate_code_set_width':statistics.mean(widths),
                          'maximum_candidate_code_set_width':max(widths)}
    original=json.loads((FROZEN/'evaluation_frozen_endpoint.json').read_text())
    result={'design':'Post-reference source-geometry development diagnostic; not fresh validation',
            'prediction_sha256':sha(path),'reference_sha256':sha(GOLD),
            'source_sha256':sha(Path(__file__)),
            'original_frozen_evaluation_sha256':sha(FROZEN/'evaluation_frozen_endpoint.json'),
            'summary_all20':summary,'original_frozen_summary_all20':original['summary']['all20_prespecified'],
            'rows':scored,'limitations':[
                'Geometry was corrected after revealing the source reference; this is development, not independent validation.',
                'Penalty1, matcher, image-template library and frozen14-ambiguity numeric candidate snapshot remain unchanged.',
                'Candidate-set compatibility is not unique fine-code accuracy; drawn-unit counts do not establish boundaries or ancient text lengths.',
                'Editorial marks are retained in the prespecified twenty-row drawn-unit denominator.',
                'AI source annotations are not expert gold, and the original frozen acquisition failure is not replaced.']}
    (out/'evaluation_post_reference.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'stage':'geometry_diagnostic_evaluation','summary':summary}),flush=True)


def main(args):
    started=time.monotonic()
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    geom_path=Path(args.geometry)
    geometry=json.loads(geom_path.read_text())
    by_id={int(r['id']):r for r in geometry['rows']}
    frozen_path=FROZEN/'predictions_before_gold.json'
    chart=FROZEN/'chart_reference_at_prediction_freeze.json'
    frozen=json.loads(frozen_path.read_text())
    assert frozen['complete'] and frozen['penalty_frozen']==1
    ids=[r['id'] for r in frozen['rows']]
    assert len(by_id)==20 and set(ids)==set(by_id)
    assert sha(chart)==frozen['manual_chart_sha256']
    assert geometry['frozen_predictions_sha256']==sha(frozen_path)
    assert geometry['original_pdf_sha256']==sha(PDF)
    assert geometry['manual_reference_sha256_unchanged']==sha(GOLD)
    original_hashes={str(p.relative_to(ROOT)):sha(p) for p in [frozen_path,chart,FROZEN/'evaluation_frozen_endpoint.json']}
    font.OUT=out
    library=font.crop_library(chart)
    assert sha(out/'template_metadata.json')==sha(FROZEN/'template_metadata.json')
    by_key={t['key']:t for t in library}
    page=font.render(30)
    result={'design':'Post-reference source-geometry development diagnostic; reference already revealed before geometry choice.',
            'complete':False,'penalty_frozen':1,'parameters':vars(args),
            'source_sha256':sha(Path(__file__)),'font_dependency_sha256':sha(ROOT/'src/font_pilot.py'),
            'matcher_dependency_sha256':sha(ROOT/'src/visual_transcription.py'),
            'pdf_sha256':sha(PDF),'geometry_sha256':sha(geom_path),
            'chart_snapshot_sha256':sha(chart),'frozen_prediction_sha256':sha(frozen_path),
            'same_template_metadata_sha256':sha(out/'template_metadata.json'),
            'original_hashes_read_only':original_hashes,'rows':[],
            'scope':'Only corrected source vertical bounds change. Horizontal rectangles, penalty1, image matcher and frozen numeric candidate unions remain identical. Prediction file is completed and hashed before evaluation against already-known source truth.'}
    path=out/'predictions_before_evaluation.json'
    for r in frozen['rows']:
        g=by_id[r['id']]
        assert g['column']==r['column'] and g['row']==r['row']
        assert g['original_frozen_crop_xyxy_2x']==r['crop_xyxy_2x']
        y_bounds,units=vertical_bounds(g)
        x0,_,x1,_=r['crop_xyxy_2x'];y0,y1=y_bounds
        assert [g['recommended_crop_xyxy_2x'][i] for i in [0,2]]==[x0,x1]
        assert 0<=y0<y1<=page.shape[0] and 0<=x0<x1<=page.shape[1]
        strip=page[y0:y1,x0:x1]
        components,choices=font.candidates(strip,library)
        tokens,cost=font.paths(components,choices,1)
        for t in tokens:
            for a in t['alternatives']:
                template=by_key[a['template_key']]
                a['manual_numeric_code_candidates']=sorted(set([template['code_manual']]+template['numeric_alternatives']))
        result['rows'].append({'id':r['id'],'column':r['column'],'row':r['row'],
                               'crop_xyxy_2x':[x0,y0,x1,y1],
                               'original_crop_xyxy_2x':r['crop_xyxy_2x'],
                               'source_vertical_geometry_row':g,'geometry_coordinate_interpretation':units,
                               'tokens':tokens,'cost':cost,'physical_line_side_boundary':'unknown'})
        Image.fromarray(strip).resize((strip.shape[1]*3,strip.shape[0]*3)).save(out/f"row_{r['id']}.png")
        result['complete']=len(result['rows'])==20
        result['elapsed_seconds']=time.monotonic()-started
        path.write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps({'stage':'geometry_diagnostic_prediction','id':r['id'],'tokens':len(tokens),'done':len(result['rows']),'seconds':result['elapsed_seconds']}),flush=True)
    assert all(sha(ROOT/p)==h for p,h in original_hashes.items())
    frozen_prediction_hash=sha(path)
    evaluate(path,out)
    assert sha(path)==frozen_prediction_hash
    assert all(sha(ROOT/p)==h for p,h in original_hashes.items())


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--geometry',required=True)
    parser.add_argument('--output',default='research/methods/results/font_geometry_sensitivity')
    main(parser.parse_args())
