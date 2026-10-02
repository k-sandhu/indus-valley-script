"""Independent root check of the methods geometry diagnostic's saved endpoints."""
import hashlib
import json
from pathlib import Path

from evaluate_font_pilot import edit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'research/methods/results/font_geometry_sensitivity'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pred_path = OUT / 'predictions_before_evaluation.json'
    eval_path = OUT / 'evaluation_post_reference.json'
    ref_path = ROOT / 'research/corpus/primary/font_fresh20/manual_reference.json'
    predictions = json.loads(pred_path.read_text())
    scored = json.loads(eval_path.read_text())
    truth = {int(row['printed_inscription_id']): row for row in json.loads(ref_path.read_text())['rows']}
    evaluated = {row['id']: row for row in scored['rows']}
    assert predictions['complete'] and len(predictions['rows']) == 20
    assert len(evaluated) == 20 and set(evaluated) == set(truth)
    assert scored['prediction_sha256'] == sha(pred_path)
    assert scored['reference_sha256'] == sha(ref_path)
    assert scored['source_sha256'] == sha(ROOT / 'src/methods/font_geometry_sensitivity.py')
    all_widths = {(kind, top): [] for kind in ['strict', 'shape_only'] for top in [1, 5]}
    for row in predictions['rows']:
        gold = truth[row['id']]
        saved = evaluated[row['id']]
        assert saved['predicted_units'] == len(row['tokens'])
        assert saved['true_drawn_units'] == gold['drawn_unit_count']
        for kind in ['strict', 'shape_only']:
            targets = [set(unit[kind + '_candidate_codes']) for unit in gold['units']]
            for top in [1, 5]:
                guesses = [set(code for alternative in token['alternatives'][:top]
                               for code in alternative['manual_numeric_code_candidates']) for token in row['tokens']]
                key = f'{kind}_top{top}'
                distance = edit(guesses, targets)
                assert saved[key + '_edit_distance'] == distance
                assert saved[key + '_row_compatible'] == (distance == 0)
                assert saved[key + '_candidate_widths'] == list(map(len, guesses))
                all_widths[kind, top].extend(map(len, guesses))
    summary = scored['summary_all20']
    assert summary['predicted_units'] == sum(row['predicted_units'] for row in evaluated.values()) == 96
    assert summary['correct_drawn_unit_count_rows'] == sum(row['predicted_units'] == row['true_drawn_units'] for row in evaluated.values()) == 18
    for kind in ['strict', 'shape_only']:
        for top in [1, 5]:
            key = f'{kind}_top{top}'
            value = summary[key]
            assert value['summed_edit_distance'] == sum(row[key + '_edit_distance'] for row in evaluated.values())
            assert value['candidate_compatible_whole_rows'] == sum(row[key + '_row_compatible'] for row in evaluated.values())
            widths = all_widths[kind, top]
            assert value['maximum_candidate_code_set_width'] == max(widths)
            assert abs(value['mean_candidate_code_set_width'] - sum(widths)/len(widths)) < 1e-12
    for name, digest in predictions['original_hashes_read_only'].items():
        assert sha(ROOT / name) == digest
    result = {'passed': True, 'method': 'Independent iterative candidate-set edit DP and explicit recomputation of all20 summaries.',
              'prediction_sha256': sha(pred_path), 'evaluation_sha256': sha(eval_path),
              'reference_sha256': sha(ref_path), 'audit_source_sha256': sha(Path(__file__)),
              'limits': 'Post-reference development diagnostic; arithmetic audit does not certify crop geometry or ancient reading.'}
    (ROOT / 'research/root_geometry_audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
