"""Independent read-only audit of the frozen follow-on source-font endpoint."""
import hashlib
import json
from pathlib import Path
import random
import statistics

from audit_font_pilot import distance

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/visual_digitization/font_fresh20'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pp = OUT/'predictions_before_gold.json'
    gp = ROOT/'research/corpus/primary/font_fresh20/manual_reference.json'
    cp = OUT/'chart_reference_at_prediction_freeze.json'
    prediction = json.loads(pp.read_text())
    reference = json.loads(gp.read_text())
    chart = json.loads(cp.read_text())
    saved = json.loads((OUT/'evaluation_frozen_endpoint.json').read_text())
    metadata = json.loads((OUT/'template_metadata.json').read_text())
    for key,path in [('prediction_sha256',pp),('reference_sha256',gp),('chart_snapshot_sha256',cp)]:
        assert saved[key] == sha(path)
    assert saved['chart_snapshot_sha256'] == prediction['manual_chart_sha256']
    assert saved['evaluation_source_sha256'] == sha(ROOT/'src/evaluate_font_fresh20.py')
    assert prediction['source_sha256'] == sha(ROOT/'src/font_fresh20.py')
    assert prediction['font_dependency_sha256'] == sha(ROOT/'src/font_pilot.py')
    expected_coordinates = sorted(random.Random(20261015).sample([(c,r) for c in range(2) for r in range(8,35)],20))
    assert [(r['column'],r['row']) for r in prediction['rows']] == expected_coordinates
    assert prediction['complete'] and prediction['penalty_frozen'] == 1
    gold = {int(r['printed_inscription_id']):r for r in reference['rows']}
    ids = [r['id'] for r in prediction['rows']]
    assert len(ids)==len(set(ids))==len(gold)==20 and set(ids)==set(gold)
    assert all(r['id']==(1015 if r['column']==0 else 1051)+r['row'] for r in prediction['rows'])
    chart_map = {f"{r['pdf_page']}:{r['column']}:{r['row']}":r for r in chart['rows']}
    assert len(chart_map) == len(chart['rows'])
    for entry in metadata:
        assert entry['source_row'] == chart_map[entry['key']]
    rows = []
    for r in prediction['rows']:
        g = gold[r['id']]
        assert len(g['units']) == g['drawn_unit_count']
        assert g['charted_glyph_drawn_units'] + g['editorial_auxiliary_drawn_units'] == g['drawn_unit_count']
        x = {'id':r['id'],'true_drawn_units':len(g['units']),
             'charted_glyph_drawn_units':g['charted_glyph_drawn_units'],
             'editorial_auxiliary_drawn_units':g['editorial_auxiliary_drawn_units'],
             'predicted_units':len(r['tokens']), 'auxiliary_only':g['auxiliary_only'],
             'source_contains_loss_or_inaccessibility':g['source_contains_loss_or_inaccessibility']}
        for token in r['tokens']:
            for alternative in token['alternatives']:
                source = chart_map[alternative['template_key']]
                assert alternative['manual_numeric_code_candidates'] == sorted(set([source['code']] + source['alternatives']))
        for kind in ['strict','shape_only']:
            target = [set(u[kind+'_candidate_codes']) for u in g['units']]
            for top in [1,5]:
                guesses = [{code for alternative in t['alternatives'][:top] for code in alternative['manual_numeric_code_candidates']} for t in r['tokens']]
                key = f'{kind}_top{top}'
                x[key+'_edit_distance'] = distance(guesses,target)
                x[key+'_row_compatible'] = x[key+'_edit_distance'] == 0
                x[key+'_candidate_widths'] = list(map(len,guesses))
        assert x == next(t for t in saved['rows'] if t['id']==r['id'])
        rows.append(x)
    summaries = {}
    for name,selected in [('all20_prespecified',rows),
                          ('excluding_auxiliary_only_source_classified_sensitivity',[r for r in rows if not r['auxiliary_only']]),
                          ('excluding_all_loss_or_inaccessibility_source_classified_sensitivity',[r for r in rows if not r['source_contains_loss_or_inaccessibility']])]:
        summary = {'rows':len(selected),
                   'true_drawn_units':sum(r['true_drawn_units'] for r in selected),
                   'charted_glyph_drawn_units':sum(r['charted_glyph_drawn_units'] for r in selected),
                   'editorial_auxiliary_drawn_units':sum(r['editorial_auxiliary_drawn_units'] for r in selected),
                   'predicted_units':sum(r['predicted_units'] for r in selected),
                   'correct_drawn_unit_count_rows':sum(r['true_drawn_units']==r['predicted_units'] for r in selected)}
        for kind in ['strict','shape_only']:
            for top in [1,5]:
                key=f'{kind}_top{top}'
                widths=[w for r in selected for w in r[key+'_candidate_widths']]
                summary[key]={'summed_edit_distance':sum(r[key+'_edit_distance'] for r in selected),
                              'candidate_compatible_whole_rows':sum(r[key+'_row_compatible'] for r in selected),
                              'mean_candidate_code_set_width':statistics.mean(widths),
                              'maximum_candidate_code_set_width':max(widths)}
        assert summary == saved['summary'][name]
        summaries[name]=summary
    units=[u for r in reference['rows'] for u in r['units']]
    result={'scope':'Independent read-only arithmetic/provenance audit; no expert glyph certification or ancient text-length claim.',
            'source_sha256':sha(Path(__file__)),
            'prediction_sha256':sha(pp),'reference_sha256':sha(gp),'chart_snapshot_sha256':sha(cp),
            'selection_and_id_coverage_verified':True,'all_recorded_source_hashes_match':True,
            'all_template_candidate_sets_equal_frozen_chart_sets':True,
            'all_row_scores_and_summaries_reproduced':True,
            'reference_candidate_sizes':{kind:{'units':len(units),
                'ambiguous_units':sum(len(u[kind+'_candidate_codes'])>1 for u in units),
                'max_candidate_set_size':max(len(u[kind+'_candidate_codes']) for u in units),
                'total_candidates':sum(len(u[kind+'_candidate_codes']) for u in units)} for kind in ['strict','shape_only']},
            'summary':summaries}
    target=ROOT/'research/methods/results/font_fresh20_audit'
    target.mkdir(parents=True,exist_ok=True)
    (target/'audit.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
