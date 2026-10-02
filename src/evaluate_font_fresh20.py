"""Score the complete frozen twenty-row image test without tuning its endpoint."""
import hashlib
import json
import statistics
from pathlib import Path

from evaluate_font_pilot import edit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/visual_digitization/font_fresh20'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prediction_path = OUT / 'predictions_before_gold.json'
    reference_path = ROOT / 'research/corpus/primary/font_fresh20/manual_reference.json'
    chart_snapshot = OUT / 'chart_reference_at_prediction_freeze.json'
    prediction = json.loads(prediction_path.read_text())
    reference = json.loads(reference_path.read_text())
    truth = {int(row['printed_inscription_id']): row for row in reference['rows']}
    predicted_ids = [row['id'] for row in prediction['rows']]
    assert prediction['complete'] and prediction['penalty_frozen'] == 1
    assert len(predicted_ids) == len(set(predicted_ids)) == len(truth) == 20
    assert set(predicted_ids) == set(truth)
    assert sha(chart_snapshot) == prediction['manual_chart_sha256']
    rows = []
    for row in prediction['rows']:
        gold = truth[row['id']]
        tokens = row['tokens']
        assert len(gold['units']) == gold['drawn_unit_count']
        assert gold['charted_glyph_drawn_units'] + gold['editorial_auxiliary_drawn_units'] == gold['drawn_unit_count']
        scored = {
            'id': row['id'], 'true_drawn_units': gold['drawn_unit_count'],
            'charted_glyph_drawn_units': gold['charted_glyph_drawn_units'],
            'editorial_auxiliary_drawn_units': gold['editorial_auxiliary_drawn_units'],
            'predicted_units': len(tokens), 'auxiliary_only': gold['auxiliary_only'],
            'source_contains_loss_or_inaccessibility': gold['source_contains_loss_or_inaccessibility'],
        }
        for kind in ['strict', 'shape_only']:
            target_sets = [set(unit[f'{kind}_candidate_codes']) for unit in gold['units']]
            for top in [1, 5]:
                guess_sets = [set(code for alt in token['alternatives'][:top]
                                  for code in alt['manual_numeric_code_candidates']) for token in tokens]
                distance = edit(guess_sets, target_sets)
                prefix = f'{kind}_top{top}'
                scored[prefix + '_edit_distance'] = distance
                scored[prefix + '_row_compatible'] = distance == 0
                scored[prefix + '_candidate_widths'] = [len(codes) for codes in guess_sets]
        rows.append(scored)
    summaries = {}
    subsets = {
        'all20_prespecified': rows,
        'excluding_auxiliary_only_source_classified_sensitivity': [r for r in rows if not r['auxiliary_only']],
        'excluding_all_loss_or_inaccessibility_source_classified_sensitivity': [r for r in rows if not r['source_contains_loss_or_inaccessibility']],
    }
    for name, selected in subsets.items():
        summary = {
            'rows': len(selected),
            'true_drawn_units': sum(r['true_drawn_units'] for r in selected),
            'charted_glyph_drawn_units': sum(r['charted_glyph_drawn_units'] for r in selected),
            'editorial_auxiliary_drawn_units': sum(r['editorial_auxiliary_drawn_units'] for r in selected),
            'predicted_units': sum(r['predicted_units'] for r in selected),
            'correct_drawn_unit_count_rows': sum(r['true_drawn_units'] == r['predicted_units'] for r in selected),
        }
        for kind in ['strict', 'shape_only']:
            for top in [1, 5]:
                prefix = f'{kind}_top{top}'
                widths = [width for r in selected for width in r[prefix + '_candidate_widths']]
                summary[prefix] = {
                    'summed_edit_distance': sum(r[prefix + '_edit_distance'] for r in selected),
                    'candidate_compatible_whole_rows': sum(r[prefix + '_row_compatible'] for r in selected),
                    'mean_candidate_code_set_width': statistics.mean(widths) if widths else None,
                    'maximum_candidate_code_set_width': max(widths) if widths else None,
                }
        summaries[name] = summary
    result = {
        'scope': 'Frozen image-only acquisition test. AI manual reference; not expert gold or semantic decipherment.',
        'prediction_sha256': sha(prediction_path), 'reference_sha256': sha(reference_path),
        'chart_snapshot_sha256': sha(chart_snapshot), 'evaluation_source_sha256': sha(Path(__file__)),
        'reference_release_protocol': reference['release_protocol'],
        'primary_endpoint': 'All20 rows; penalty1 frozen after the development pilot. No post-reference tuning.',
        'endpoint_definition': 'Levenshtein distance with zero substitution cost when predicted and manual candidate-code sets intersect. Top5 means five image templates, whose numeric candidate labels can expand beyond five codes.',
        'limitations': [
            'Zero edit distance means candidate-set compatibility, not a uniquely certified code sequence.',
            'Correct drawn-unit count does not certify every boundary.',
            'Editorial auxiliary marks have no ancient sign identity and are retained in the all20 denominator.',
            'Source-classified subset scores are sensitivities, not replacement primary endpoints.',
            'Original physical lines, sides and ancient text lengths remain unknown.',
            'The numeric chart snapshot is retained even when later source inspection corrects its labels.',
        ],
        'summary': summaries, 'rows': rows,
    }
    (OUT / 'evaluation_frozen_endpoint.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
