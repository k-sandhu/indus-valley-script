"""Exact grouped-rank witnesses for a frozen three-form product generator."""
import ast
import csv
from fractions import Fraction as F
import hashlib
from itertools import combinations
import json
from pathlib import Path
import shutil
import time

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'knowledge').is_dir())
BASE = ROOT / 'experiments/2026-10-02-six-hour/latent-generator-identification'
GROUPS = [(0, 1), (2, 3), (4, 5)]
ALPHAS = [0., .35, .70]
CONVENTIONS = ['normalized_binary64', 'rounded_thresholds_continuous_uniform']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def serial(value):
    return [str(value.numerator), str(value.denominator)]


def determinant(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    if len(matrix) == 2:
        return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    a, b, c = matrix
    return a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])


def pivot_columns(matrix):
    """Select independent columns by exact minors, in ascending order."""
    columns = []
    for column in range(len(matrix[0])):
        proposed = columns + [column]
        for rows in combinations(range(3), len(proposed)):
            minor = [[matrix[r][c] for c in proposed] for r in rows]
            if determinant(minor):
                columns.append(column)
                break
        if len(columns) == 3:
            break
    return columns


def exact_probabilities(values, convention):
    raw = [F(float(v)) for v in values]
    assert all(v >= 0 for v in raw) and sum(raw) > 0
    if convention == CONVENTIONS[0]:
        total = sum(raw)
        return [v / total for v in raw]
    cumulative = np.cumsum(np.asarray(values, dtype=np.float64))
    thresholds = [F(float(np.clip(v, 0., 1.))) for v in cumulative[:-1]]
    return [thresholds[0]] + [b-a for a, b in zip(thresholds, thresholds[1:])] + [F(1)-thresholds[-1]]


def profile(spec, alpha, convention):
    factors = (1-alpha)*np.asarray(spec['extended'], dtype=np.float64) + alpha*np.asarray(spec['background'], dtype=np.float64)
    probabilities = [[exact_probabilities(p, convention) for p in form] for form in factors]
    assert factors.shape == (3, 6, 20)
    assert all(sum(p) == 1 and min(p) >= 0 for form in probabilities for p in form)
    error = max(abs(float(q)-float(v)) for form, rawform in zip(probabilities, factors) for p, rawp in zip(form, rawform) for q, v in zip(p, rawp))
    sums = [serial(sum(F(float(v)) for v in p)) for form in factors for p in form]
    weights = {}
    for shift in [0., .35]:
        rawmix = np.asarray(spec['mixture'], dtype=np.float64)
        changed = (1-shift)*rawmix + shift*np.roll(rawmix, 1)
        pi = exact_probabilities(changed, convention)
        assert min(pi) > 0 and sum(pi) == 1
        weights[str(shift)] = [serial(v) for v in pi]
    return probabilities, error, sums, weights


def grouped(probabilities, first, second):
    matrix = [[left*right for left in form[first] for right in form[second]] for form in probabilities]
    assert all(sum(row) == 1 for row in matrix)
    for i, row in enumerate(matrix):
        assert [sum(row[20*a:20*(a+1)]) for a in range(20)] == probabilities[i][first]
        assert [sum(row[a*20+b] for a in range(20)) for b in range(20)] == probabilities[i][second]
    columns = pivot_columns(matrix)
    rank = len(columns)
    rows = next(rows for rows in combinations(range(3), rank) if determinant([[matrix[r][c] for c in columns] for r in rows]))
    minor = [[matrix[r][c] for c in columns] for r in rows]
    singular = np.linalg.svd(np.asarray([[float(v) for v in row] for row in matrix]), compute_uv=False)
    return {'slots': [first, second], 'rank': rank, 'kruskal_rank': 3 if rank == 3 else (1 if matrix[0] == matrix[1] == matrix[2] else None),
            'pivot_columns': columns, 'pivot_codes': [[c//20, c%20] for c in columns], 'minor_rows': list(rows),
            'minor': [[serial(v) for v in row] for row in minor], 'determinant': serial(determinant(minor)),
            'singular_values_diagnostic': singular.tolist(), 'smallest_largest_ratio_diagnostic': float(singular[-1]/singular[0]),
            'exact_row_sums_and_slot_marginals': True}


def selfcheck():
    assert pivot_columns([[F(1), F(0), F(0)], [F(0), F(1), F(0)], [F(0), F(0), F(1)]]) == [0, 1, 2]
    assert pivot_columns([[F(1), F(2)], [F(1), F(2)], [F(1), F(2)]]) == [0]
    assert determinant([[F(1), F(2), F(3)], [F(0), F(1), F(4)], [F(5), F(6), F(0)]]) == 1


def run():
    output, boundary = BASE/'main', BASE/'collapsed-control'
    if output.exists() or boundary.exists():
        raise FileExistsError('Use fresh identification endpoints')
    output.mkdir()
    boundary.mkdir()
    shutil.copyfile(__file__, output/'code_snapshot.py')
    shutil.copyfile(__file__, boundary/'code_snapshot.py')
    started = time.monotonic()
    try:
        selfcheck()
        parameters = json.loads((BASE/'sources/parameters.json').read_text())
        source = (BASE/'sources/generator.py').read_text()
        parsed = ast.parse(source)
        variant_node = next(n.value for n in parsed.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VARIANTS' for t in n.targets))
        assert ast.literal_eval(variant_node) == [('separated', None), ('same_length_0', 0.), ('same_length_35', .35), ('same_length_70', .70)]
        stream = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'stream')
        expression = next(n.value for n in stream.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'forms' for t in n.targets))
        code = compile(ast.Expression(expression), '<frozen generator factors>', 'eval')
        assert len(parameters) == 12
        assert [p['seed'] for p in parameters] == [1010261002+1000*i for i in range(12)]
        results, controls = [], []
        for spec in parameters:
            numpy_spec = {**spec, 'extended': [[np.asarray(p) for p in form] for form in spec['extended']], 'background': np.asarray(spec['background'])}
            for alpha in ALPHAS:
                inherited = eval(code, {'np': np, 'alpha': alpha, 'spec': numpy_spec})
                assert np.array_equal(inherited, (1-alpha)*np.asarray(spec['extended']) + alpha*np.asarray(spec['background']))
                for convention in CONVENTIONS:
                    probabilities, error, sums, weights = profile(spec, alpha, convention)
                    matrices = [grouped(probabilities, *pair) for pair in GROUPS]
                    ranks = [m['kruskal_rank'] for m in matrices]
                    condition = None if any(r is None for r in ranks) else sum(ranks) >= 8
                    results.append({'seed': spec['seed'], 'alpha': alpha, 'convention': convention, 'grouped_matrices': matrices,
                                    'mixing_weights_by_shift': weights, 'max_probability_change_from_raw_binary64': error,
                                    'raw_slot_rational_sums': sums, 'rank_sum': None if None in ranks else sum(ranks), 'threshold': 8,
                                    'corollary2_condition': condition, 'slot_support_counts': [[sum(v > 0 for v in p) for p in form] for form in probabilities]})
            for convention in CONVENTIONS:
                probabilities, error, sums, weights = profile(spec, 1., convention)
                assert all(form == probabilities[0] for form in probabilities)
                assert all(p == probabilities[0][0] for form in probabilities for p in form)
                matrices = [grouped(probabilities, *pair) for pair in GROUPS]
                controls.append({'seed': spec['seed'], 'alpha': 1., 'convention': convention, 'grouped_matrices': matrices,
                                 'rank_sum': sum(m['kruskal_rank'] for m in matrices), 'threshold': 8, 'corollary2_condition': False,
                                 'alternative_positive_weights': [[serial(v) for v in [F(1,5), F(3,10), F(1,2)]], [serial(v) for v in [F(3,10), F(3,10), F(2,5)]]],
                                 'identical_component_products': True, 'weight_sums': [serial(F(1)), serial(F(1))],
                                 'same_population_law': True, 'weight_multisets_differ': True})
            print(json.dumps({'seed': spec['seed'], 'completed_profiles': len(results), 'completed_boundary_profiles': len(controls)}), flush=True)
        hashes = {name: sha(BASE/name) for name in ['PROTOCOL.md', 'sources/parameters.json', 'sources/generator.py']}
        result = {'status': 'complete', 'post_outcome': True, 'population_interpretation': 'independent continuous uniforms; not a PRNG state-space claim',
                  'systems': 12, 'main_generator_profiles': 36, 'probability_conventions_per_profile': 2, 'grouped_matrices_checked': 216,
                  'all_main_conditions': all(p['corollary2_condition'] is True for p in results), 'profiles': results,
                  'input_hashes': hashes, 'source_sha256': sha(__file__), 'elapsed_seconds': time.monotonic()-started}
        write(output/'results.json', result)
        write(boundary/'results.json', {'status': 'complete', 'constructed_control': True, 'generator_alpha_not_in_main_grid': 1.,
                                        'systems': 12, 'conventions': 2, 'profiles': controls, 'input_hashes': hashes, 'source_sha256': sha(__file__)})
        with (output/'ranks.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.writer(handle)
            writer.writerow(['seed', 'alpha', 'convention', 'pair', 'rank', 'kruskal_rank', 'pivot_columns', 'determinant_numerator', 'determinant_denominator', 'smallest_largest_singular_ratio_diagnostic'])
            for p in results:
                for m in p['grouped_matrices']:
                    writer.writerow([p['seed'], p['alpha'], p['convention'], str(m['slots']), m['rank'], m['kruskal_rank'], str(m['pivot_columns']), *m['determinant'], m['smallest_largest_ratio_diagnostic']])
        print(json.dumps({k: result[k] for k in ['status', 'all_main_conditions', 'grouped_matrices_checked', 'elapsed_seconds']}))
    except Exception as exc:
        write(output/'failure.json', {'exception': type(exc).__name__, 'message': str(exc), 'source_sha256': sha(__file__)})
        raise


if __name__ == '__main__':
    run()
