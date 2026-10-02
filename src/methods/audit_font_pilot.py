"""Read-only independent arithmetic audit of the source-font pilot."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/visual_digitization/fresh_font_pilot_corrected'


def distance(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        row = [i]
        for j, y in enumerate(b, 1):
            row.append(min(row[-1] + 1, prev[j] + 1,
                           prev[j - 1] + int(not x.intersection(y))))
        prev = row
    return prev[-1]


def main():
    predictions = json.loads((OUT / 'predictions_before_gold.json').read_text())
    reference_path = ROOT / 'research/corpus/primary/font_row_audit/manual_reference.json'
    reference = json.loads(reference_path.read_text())
    observed = json.loads((OUT / 'evaluation_all_endpoints.json').read_text())
    ref = {int(r['printed_inscription_id']): r for r in reference['rows']}
    ids = [r['id'] for r in predictions['rows']]
    assert len(ids) == len(set(ids)) and set(ids) == set(ref)
    assert observed['prediction_sha256'] == hashlib.sha256((OUT / 'predictions_before_gold.json').read_bytes()).hexdigest()
    assert observed['reference_sha256'] == hashlib.sha256(reference_path.read_bytes()).hexdigest()
    result = {'ids_unique_and_exact_reference_match': True,
              'saved_prediction_and_reference_hashes_match': True,
              'all_saved_row_distances_match_independent_recursion': True,
              'reference_candidate_sizes': {
                  kind: {'units': sum(len(r['units']) for r in reference['rows']),
                         'ambiguous_units': sum(len(u[kind+'_candidate_codes']) > 1 for r in reference['rows'] for u in r['units']),
                         'max_candidate_set_size': max(len(u[kind+'_candidate_codes']) for r in reference['rows'] for u in r['units']),
                         'total_candidates': sum(len(u[kind+'_candidate_codes']) for r in reference['rows'] for u in r['units'])}
                  for kind in ['strict', 'shape_only']},
              'endpoints': {}}
    for penalty, saved in observed['endpoints'].items():
        rows = []
        duplicate_top5 = 0
        for r in predictions['rows']:
            g = ref[r['id']]
            tokens = r['variants'][penalty]['tokens']
            row = {'id': r['id'], 'true_units': len(g['units']), 'predicted_units': len(tokens)}
            assert row['true_units'] == g['glyph_unit_count']
            for t in tokens:
                codes = [a['code_ocr'] for a in t['alternatives'][:5] if a['code_ocr'] is not None]
                duplicate_top5 += len(codes) != len(set(codes))
            for kind in ['strict', 'shape_only']:
                truth = [set(u[f'{kind}_candidate_codes']) for u in g['units']]
                for top in [1, 5]:
                    guesses = [{int(a['code_ocr']) for a in t['alternatives'][:top] if a['code_ocr'] is not None} for t in tokens]
                    key = f'{kind}_top{top}'
                    row[key+'_edit_distance'] = distance(guesses, truth)
                    row[key+'_row_compatible'] = row[key+'_edit_distance'] == 0
                    if top == 1 and len(guesses) == len(truth):
                        row[kind+'_direct_position_mismatches'] = sum(not a.intersection(b) for a,b in zip(guesses,truth))
            expected = next(x for x in saved['rows'] if x['id'] == r['id'])
            assert all(row[k] == v for k,v in expected.items())
            rows.append(row)
        summaries = {}
        for name, selected in [('all10', rows), ('excluding_partially_disclosed1020', [r for r in rows if r['id'] != 1020])]:
            summary = {'rows': len(selected), 'true_units': sum(r['true_units'] for r in selected),
                       'predicted_units': sum(r['predicted_units'] for r in selected),
                       'correct_unit_count_rows': sum(r['true_units']==r['predicted_units'] for r in selected)}
            for kind in ['strict', 'shape_only']:
                for top in [1,5]:
                    key = f'{kind}_top{top}'
                    summary[key] = {'summed_edit_distance': sum(r[key+'_edit_distance'] for r in selected),
                                    'candidate_compatible_whole_rows': sum(r[key+'_row_compatible'] for r in selected)}
            assert summary == saved['summary'][name]
            if all(kind+'_direct_position_mismatches' in r for r in selected for kind in ['strict','shape_only']):
                summary['direct_position_mismatches'] = {kind: sum(r[kind+'_direct_position_mismatches'] for r in selected) for kind in ['strict','shape_only']}
            summaries[name] = summary
        result['endpoints'][penalty] = {'summary': summaries,
                                       'tokens_with_duplicate_top5_template_codes': duplicate_top5}
    target = ROOT / 'research/methods/results/font_pilot_audit'
    target.mkdir(parents=True, exist_ok=True)
    (target / 'audit.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
