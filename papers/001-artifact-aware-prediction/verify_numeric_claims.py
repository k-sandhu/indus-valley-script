"""Read-only checks of manuscript numbers and local evidence links; no fitting."""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PAPER = Path(__file__).resolve().parent
SPECS = []


def add(file, checks):
    SPECS.extend((file, selector, expected) for selector, expected in checks.items())


add('research/methods/results/nested_primary/nested_results.json', {
    'observed.records': 2107, 'observed.groups': 1526, 'observed.noninitial_tokens': 8199,
    'observed.gain_bits_per_noninitial_sign': .8899826988,
    'observed.gain_95pct_group_bootstrap_ci': [.8167508463, .9650883868],
    'observed.baseline_noninitial_cross_entropy_bits': 6.3070675476,
    'observed.dependent_noninitial_cross_entropy_bits': 5.4170848488,
    'observed.relative_perplexity': .5396205895,
})
add('research/methods/results/nested_unique_preserved_aliases/nested_results.json', {
    'observed.records': 1596, 'observed.groups': 1526, 'observed.noninitial_tokens': 6413,
    'observed.gain_bits_per_noninitial_sign': .8483578853,
    'observed.gain_95pct_group_bootstrap_ci': [.8069756703, .8903149464],
})
add('research/methods/results/nested_collapsed/nested_results.json', {
    'observed.records': 2107, 'observed.groups': 1506,
    'observed.gain_bits_per_noninitial_sign': .9301646644,
    'observed.gain_95pct_group_bootstrap_ci': [.8624514013, .9974794994],
})
add('research/methods/results/joint_nested_primary_1000/joint_nested_results.json', {
    'null_position_metadata.permutations': 1000,
    'null_position_metadata.p_one_sided': 1/1001,
    'null_position_metadata.mean': -.1033298285,
    'null_position_metadata.95pct_range': [-.1274390055, -.0799999963],
})
add('research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json', {
    'null_position_metadata.permutations': 1000,
    'null_position_metadata.attempts': 6569,
    'null_position_metadata.p_one_sided': 1/1001,
    'null_position_metadata.mean': .0070936302,
    'null_position_metadata.95pct_range': [-.0065489334, .0213552291],
})
add('results/independent_annotator/candidate_event_test.json', {
    'eligible_clear_single_line_length3plus': 86, 'scored_texts': 74,
    'training_unique_texts': 1426, 'training_groups': 1362,
    'training_exclusion.excluded_component_texts': 170,
    'all_clear_weighting.artifact_P_text_groups': 73,
    'all_clear_weighting.noninitial_glyphs': 315,
    'all_clear_weighting.gain_bits_per_noninitial_candidate_event': .7248273762,
    'all_clear_weighting.conditional_cluster_bootstrap_95_ci': [.5507226353, .8993568859],
    'unique_P_text_sensitivity.texts': 73,
    'unique_P_text_sensitivity.gain_bits_per_noninitial_candidate_event': .7190728417,
    'unspecified_seal_subtype_sensitivity.gain_bits_per_noninitial_candidate_event': .7771888352,
    'all_fine_candidates_training_supported_sensitivity.texts': 54,
    'all_fine_candidates_training_supported_sensitivity.gain_bits_per_noninitial_candidate_event': .8778602031,
    'records_with_unsupported_fine_candidate': 20,
})
add('results/restoration/benchmark.json', {
    'unique_texts': 1596, 'artifact_text_groups': 1526,
    'models.baseline.slots': 8009, 'models.local.slots': 8009,
    'models.baseline.top1': .1699338244, 'models.local.top1': .3381196154,
    'models.baseline.top5': .3549756524, 'models.local.top5': .5533774504,
    'models.baseline.top10': .4557372955, 'models.local.top10': .6270445749,
    'paired_gain.gain_accuracy': .1681857910,
    'paired_gain.cluster_bootstrap_95_ci': [.1564411611, .1798025710],
    'models.baseline.equal_text_weight.top1': .1736184555,
    'models.local.equal_text_weight.top1': .3259836359,
    'models.local.confidence_audit.2.mean_model_mass': .4915071324,
    'models.local.confidence_audit.2.exact_accuracy': .3844236760,
    'models.local.confidence_audit.4.mean_model_mass': .8959890550,
    'models.local.confidence_audit.4.exact_accuracy': .8378378378,
})
add('results/restoration_collapsed/benchmark.json', {'models.local.top1': .3589743590})
add('experiments/2026-10-02-six-hour/markov-baseline/main/results.json', {
    'correspondence.verified_queries_per_model': 8009,
    'correspondence.texts': 1596, 'correspondence.components': 1526,
    'models.Markov.top1': .3458609065,
    'models.Markov.top5': .5845923336,
    'models.Markov.top10': .6542639531,
    'models.Markov.expected_calibration_error': .0255636116,
    'models.PMB.expected_calibration_error': .0804843091,
    'models.Markov.bucket_cross_entropy_bits': 5.1194348563,
    'models.PMB.bucket_cross_entropy_bits': 5.7477314692,
    'paired.Markov_minus_PM.metrics.top1_slot.difference': .1759270820,
    'paired.Markov_minus_PM.metrics.top1_slot.cluster_bootstrap_95_ci': [.1638323867,.1883286086],
    'paired.PMB_minus_Markov.metrics.top1_slot.difference': -.0077412910,
    'paired.PMB_minus_Markov.metrics.top1_slot.cluster_bootstrap_95_ci': [-.0159608573,.0004990098],
    'paired.PMB_minus_Markov.metrics.top5_slot.difference': -.0312148833,
    'paired.PMB_minus_Markov.metrics.top5_slot.cluster_bootstrap_95_ci': [-.0385927177,-.0237616294],
    'paired.PMB_minus_Markov.metrics.bucket_loss_bits_slot.difference': .6282966129,
    'paired.PMB_minus_Markov.metrics.bucket_loss_bits_slot.cluster_bootstrap_95_ci': [.5792676247,.6785458023],
})
add('results/gap_restoration/gap_benchmark.json', {
    'models.baseline.exact_count_accuracy': .4191729323,
    'models.local.exact_count_accuracy': .4304511278,
    'models.local.constant_one_glyph_design_control_accuracy': .5106516291,
    'paired_gain.gain_accuracy': .0112781955,
})
add('research/methods/results/gap_design_matched/gap_design_matched.json', {
    'design_matched_models.baseline.exact_count_accuracy': .4561403509,
    'design_matched_models.local.exact_count_accuracy': .4630325815,
    'design_matched_local_minus_independent.gain_accuracy': .0068922306,
    'design_matched_local_minus_independent.cluster_bootstrap_95_ci': [-.0056890013, .0193995527],
    'design_matched_local_minus_constant_one.gain_accuracy': -.0476190476,
    'design_matched_local_minus_constant_one.cluster_bootstrap_95_ci': [-.0777452012, -.0172626387],
    'original_models.local.true_count_distribution.1': 815,
    'original_models.local.true_count_distribution.2': 454,
    'original_models.local.true_count_distribution.3': 327,
})
add('research/methods/results/templates_extended/template_results.json', {
    'contrasts.TEMPLATE_minus_BASELINE.gain_bits_per_noninitial_sign': .1422187821,
    'contrasts.PMB_minus_TEMPLATE.gain_bits_per_noninitial_sign': .7477639167,
    'contrasts.PMB_minus_TEMPLATE.95pct_group_bootstrap_ci': [.6878693705, .8093369233],
})
add('research/methods/results/workflow_templates/template_results.json', {
    'records': 3000,
    'contrasts.PMB_minus_TEMPLATE.gain_bits_per_noninitial_sign': .6311585601,
    'contrasts.PMB_minus_TEMPLATE.95pct_group_bootstrap_ci': [.5876666488, .6768414596],
})


def select(value, selector):
    for key in selector.split('.'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def matches(actual, expected):
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(matches(a, e) for a, e in zip(actual, expected))
    if isinstance(expected, float):
        return math.isclose(actual, expected, rel_tol=1e-8, abs_tol=1e-9)
    return actual == expected


def main():
    cache, hashes, checks = {}, {}, []
    for file, selector, expected in SPECS:
        if file not in cache:
            raw = (ROOT/file).read_bytes()
            cache[file] = json.loads(raw)
            hashes[file] = hashlib.sha256(raw).hexdigest()
        actual = select(cache[file], selector)
        checks.append({'file': file, 'selector': selector, 'expected': expected,
                       'actual': actual, 'pass': matches(actual, expected)})
    for file in ['research/methods/results/joint_nested_primary_1000/joint_nested_results.json',
                 'research/methods/results/joint_nested_unique_conditioned_1000/joint_nested_results.json']:
        null = cache[file]['null_position_metadata']
        observed = cache[file]['observed']['gain_bits_per_noninitial_sign']
        checks.append({'file': file, 'selector': 'computed_exceedances', 'expected': 0,
                       'actual': sum(v >= observed for v in null['values']),
                       'pass': all(v < observed for v in null['values'])})
    file = 'research/methods/results/numerical_equalities/numerical_equalities_audit.json'
    raw = (ROOT/file).read_bytes(); hashes[file] = hashlib.sha256(raw).hexdigest()
    tuples = [[r['L'], r['S'], r['v']] for r in json.loads(raw)['all_admissible_solutions']]
    expected = [[4,20,36], [6,8,10], [10,8,6], [36,20,4]]
    checks.append({'file': file, 'selector': 'positive_integer_triples',
                   'expected': expected, 'actual': tuples, 'pass': tuples == expected})
    files = list(PAPER.glob('*.md')) + [ROOT/'knowledge/retrospectives/methods.md',
                                      ROOT/'knowledge/directions/numerical-methods.md']
    links, missing = [], []
    for path in files:
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if target.startswith(('http:', 'https:', '#')):
                continue
            resolved = path.parent/target.split('#')[0].strip('<>')
            item = {'file': str(path.relative_to(ROOT)).replace('\\','/'),
                    'target': target, 'exists_local': resolved.exists()}
            links.append(item)
            if not resolved.exists(): missing.append(item)
    result = {'created_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'Read-only frozen-result arithmetic and local-link review; no model refits.',
              'numeric_checks': checks, 'source_sha256': hashes,
              'numeric_pass': all(c['pass'] for c in checks),
              'local_links': links, 'missing_local_links': missing,
              'pass': all(c['pass'] for c in checks) and not missing}
    (PAPER/'numeric-review.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'numeric_checks': len(checks), 'numeric_pass': result['numeric_pass'],
                      'local_links': len(links), 'missing_local_links': missing,
                      'pass': result['pass']}))
    if not result['pass']: raise SystemExit(1)


if __name__ == '__main__':
    main()
