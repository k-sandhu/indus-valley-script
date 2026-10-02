"""Independent scalar construction and elimination audit of grouped ranks."""
import ast
from fractions import Fraction
import hashlib
import json
from math import prod
from pathlib import Path
import shutil
import time

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'knowledge').is_dir())
BASE = ROOT/'experiments/2026-10-02-six-hour/latent-generator-identification'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unpack(pair):
    return Fraction(int(pair[0]), int(pair[1]))


def exact_distribution(raw, convention):
    if convention == 'normalized_binary64':
        fractions = [Fraction(v) for v in raw]
        return [v/sum(fractions) for v in fractions]
    previous, running = Fraction(0), 0.0
    probabilities = []
    for value in raw[:-1]:
        running += value
        current = Fraction(max(0., min(1., running)))
        probabilities.append(current-previous)
        previous = current
    probabilities.append(Fraction(1)-previous)
    assert sum(probabilities) == 1 and min(probabilities) >= 0
    return probabilities


def elimination(matrix):
    rows = [row[:] for row in matrix]
    count, swaps, pivots = 0, 0, []
    for column in range(len(rows[0])):
        pivot = next((r for r in range(count, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        if pivot != count:
            rows[pivot], rows[count] = rows[count], rows[pivot]
            swaps += 1
        value = rows[count][column]
        pivots.append(value)
        rows[count] = [v/value for v in rows[count]]
        for r in range(count+1, len(rows)):
            multiplier = rows[r][column]
            rows[r] = [a-multiplier*b for a, b in zip(rows[r], rows[count])]
        count += 1
        if count == len(rows):
            break
    determinant = (-1)**swaps*prod(pivots) if count == len(rows) == len(rows[0]) else Fraction(0)
    return count, determinant


def run():
    output = BASE/'review'
    if output.exists():
        raise FileExistsError('Use a fresh identification review')
    output.mkdir()
    shutil.copyfile(__file__, output/'code_snapshot.py')
    started = time.monotonic()
    try:
        main = json.loads((BASE/'main/results.json').read_text())
        boundary = json.loads((BASE/'collapsed-control/results.json').read_text())
        assert main['status'] == boundary['status'] == 'complete'
        assert sha(BASE/'main/code_snapshot.py') == sha(BASE/'collapsed-control/code_snapshot.py') == main['source_sha256'] == boundary['source_sha256']
        for name, value in main['input_hashes'].items():
            assert sha(BASE/name) == value == boundary['input_hashes'][name]
        parameters = json.loads((BASE/'sources/parameters.json').read_text())
        lookup = {p['seed']: p for p in parameters}
        assert len(lookup) == 12
        parsed = ast.parse((BASE/'sources/generator.py').read_text())
        assignment = next(n for n in parsed.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'VARIANTS' for t in n.targets))
        assert ast.literal_eval(assignment.value) == [('separated', None), ('same_length_0', 0.), ('same_length_35', .35), ('same_length_70', .70)]
        stream = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == 'stream')
        assert 'random((n, 7))' in ast.unparse(stream) and 'draw[j + 1]' in ast.unparse(stream)
        expected_main = {(p['seed'], a, c) for p in parameters for a in [0., .35, .70] for c in ['normalized_binary64', 'rounded_thresholds_continuous_uniform']}
        expected_control = {(p['seed'], 1., c) for p in parameters for c in ['normalized_binary64', 'rounded_thresholds_continuous_uniform']}
        assert {(p['seed'], p['alpha'], p['convention']) for p in main['profiles']} == expected_main
        assert {(p['seed'], p['alpha'], p['convention']) for p in boundary['profiles']} == expected_control
        assert len(main['profiles']) == 72 and len(boundary['profiles']) == 24
        entries, marginals, minors, full_products, mixing_vectors = 0, 0, 0, 0, 0
        for saved in main['profiles']+boundary['profiles']:
            spec, alpha, convention = lookup[saved['seed']], saved['alpha'], saved['convention']
            raw = [[[float(p[k])*(1.-alpha)+float(spec['background'][k])*alpha for k in range(20)] for p in form] for form in spec['extended']]
            probabilities = [[exact_distribution(p, convention) for p in form] for form in raw]
            assert len(probabilities) == 3 and all(len(form) == 6 for form in probabilities)
            if alpha != 1.:
                sums = [sum(Fraction(v) for v in p) for form in raw for p in form]
                assert sums == [unpack(v) for v in saved['raw_slot_rational_sums']]
                supports = [[sum(v > 0 for v in p) for p in form] for form in probabilities]
                assert supports == saved['slot_support_counts']
                assert all(n == (5 if alpha == 0 else 20) for form in supports for n in form)
                error = max(abs(float(v)-w) for form, original in zip(probabilities, raw) for p, oldp in zip(form, original) for v, w in zip(p, oldp))
                assert error == saved['max_probability_change_from_raw_binary64']
                for shift in [0., .35]:
                    mixing = [float(spec['mixture'][i])*(1.-shift)+float(spec['mixture'][(i-1)%3])*shift for i in range(3)]
                    pi = exact_distribution(mixing, convention)
                    assert sum(pi) == 1 and min(pi) > 0
                    assert pi == [unpack(v) for v in saved['mixing_weights_by_shift'][str(shift)]]
                    mixing_vectors += 1
            ranks = []
            assert [m['slots'] for m in saved['grouped_matrices']] == [[0,1], [2,3], [4,5]]
            for saved_matrix in saved['grouped_matrices']:
                a, b = saved_matrix['slots']
                matrix = [[probabilities[i][a][column//20]*probabilities[i][b][column%20] for column in range(400)] for i in range(3)]
                entries += 1200
                assert all(sum(row) == 1 for row in matrix)
                for i in range(3):
                    for code in range(20):
                        assert sum(matrix[i][code*20+other] for other in range(20)) == probabilities[i][a][code]
                        assert sum(matrix[i][other*20+code] for other in range(20)) == probabilities[i][b][code]
                        marginals += 2
                rank, _ = elimination(matrix)
                assert rank == saved_matrix['rank'] == (1 if alpha == 1. else 3)
                ranks.append(rank)
                columns = saved_matrix['pivot_columns']
                minor = [[matrix[r][c] for c in columns] for r in saved_matrix['minor_rows']]
                assert minor == [[unpack(v) for v in row] for row in saved_matrix['minor']]
                minor_rank, det = elimination(minor)
                assert minor_rank == rank and det != 0 and det == unpack(saved_matrix['determinant'])
                assert saved_matrix['pivot_codes'] == [[c//20, c%20] for c in columns]
                assert saved_matrix['kruskal_rank'] == rank
                minors += 1
            for form in probabilities:
                for start in range(20):
                    codes = [(start+3*j)%20 for j in range(6)]
                    complete = prod(form[j][codes[j]] for j in range(6))
                    pairs = prod(form[a][codes[a]]*form[b][codes[b]] for a, b in [(0,1),(2,3),(4,5)])
                    assert complete == pairs
                    full_products += 1
            assert sum(ranks) == saved['rank_sum']
            assert saved['threshold'] == 8 and saved['corollary2_condition'] == (sum(ranks) >= 8)
            if alpha == 1.:
                assert all(form == probabilities[0] for form in probabilities)
                assert all(p == probabilities[0][0] for form in probabilities for p in form)
                weights = [[unpack(v) for v in row] for row in saved['alternative_positive_weights']]
                assert all(sum(w) == 1 and min(w) > 0 for w in weights)
                assert sorted(weights[0]) != sorted(weights[1])
                for start in range(20):
                    component = prod(probabilities[0][j][(start+j)%20] for j in range(6))
                    assert sum(w*component for w in weights[0]) == sum(w*component for w in weights[1]) == component
        assert main['all_main_conditions'] is True
        result = {'status': 'pass', 'main_parameter_profiles': 36, 'main_convention_profiles': 72, 'collapsed_parameter_profiles': 12,
                  'collapsed_convention_profiles': 24, 'exact_grouped_entries_reconstructed': entries, 'exact_slot_marginals_checked': marginals,
                  'independently_eliminated_minor_certificates': minors, 'positive_normalized_mixing_vectors_checked': mixing_vectors,
                  'exact_full_product_grouping_checks': full_products, 'main_conditions': 'all ranks 3/3/3, sum9>=8',
                  'collapsed_conditions': 'all ranks1/1/1; distinct positive mixing vectors yield identical product law',
                  'main_results_sha256': sha(BASE/'main/results.json'), 'collapsed_results_sha256': sha(BASE/'collapsed-control/results.json'),
                  'audit_source_sha256': sha(__file__), 'elapsed_seconds': time.monotonic()-started}
        (output/'verification.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result, indent=2))
    except Exception as exc:
        (output/'failure.json').write_text(json.dumps({'exception': type(exc).__name__, 'message': str(exc), 'source_sha256': sha(__file__)}, indent=2)+'\n')
        raise


if __name__ == '__main__':
    run()
