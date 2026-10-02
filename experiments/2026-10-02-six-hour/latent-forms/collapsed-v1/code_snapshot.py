"""Closed-form coincident-component smoothing control on frozen records."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

from review_reference_selector import dual_certificate

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/latent-forms'
SOURCE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms/main-v1'
K = 20


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


class Profile:
    def __init__(self, reference):
        self.cells = Counter((j, c) for row in reference for j, c in enumerate(row))
        self.logs = [[math.log((self.cells[j, c] + 3) / (len(reference) + 3 * K)) for c in range(K)] for j in range(6)]

    def weights(self, rows):
        counts = Counter((j, c) for row in rows for j, c in enumerate(row))
        return np.asarray([[math.fsum(counts[j, c] * self.logs[j][r] for j in range(6)) for r in range(K)] for c in range(K)])

    def score(self, rows, mapping):
        return math.fsum(self.logs[j][mapping[c]] for row in rows for j, c in enumerate(row))


def main():
    out = BASE / 'collapsed-v1'
    if out.exists():
        raise RuntimeError('Preserve prior endpoint.')
    out.mkdir()
    files = [BASE / 'main-v1/results.json', BASE / 'review-v1/verification.json', SOURCE / 'worlds.json']
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    result = json.loads((BASE / 'main-v1/results.json').read_text())
    worlds = json.loads((SOURCE / 'worlds.json').read_text())
    world_lookup = {(w['seed'], w['variant'], w['shift']): w for w in worlds}
    rows = {tuple(r[n] for n in ('seed', 'variant', 'shift', 'reference_records', 'algorithm')): r for r in result['rows']}
    choices, outcomes, certificates, checks = [], [], [], []
    for choice in result['choices']:
        key = choice['seed'], choice['variant'], choice['reference_records']
        world = world_lookup[key[0], key[1], 0.]
        reference = world['reference'][:key[2]]
        cv = 0.
        for fold in range(3):
            train = [row for i, row in enumerate(reference) if choice['folds'][i] != fold]
            test = [row for i, row in enumerate(reference) if choice['folds'][i] == fold]
            cv += Profile(train).score(test, list(range(K))) / math.log(2)
        scores = dict(choice['scores'], collapsed_profile=cv)
        order = ['graph_multistart', 'length_slot', 'collapsed_profile', 'latent_mixture']
        selected = max(order, key=lambda name: scores[name])
        choices.append(dict(seed=key[0], variant=key[1], reference_records=key[2], selected=selected, scores=scores,
                            mixture_minus_collapsed_CV_bits=scores['latent_mixture'] - cv))
        fitted = Profile(reference)
        for shift in (0., .35):
            case = world_lookup[key[0], key[1], shift]
            matrix = fitted.weights(case['training'])
            _, mapping = linear_sum_assignment(matrix, maximize=True)
            certificate = dual_certificate(matrix, mapping)
            condition = dict(seed=key[0], variant=key[1], shift=shift, reference_records=key[2])
            certificates.append(dict(**condition, **certificate))
            score = fitted.score(case['training'], mapping)
            matrix_score = math.fsum(matrix[c, mapping[c]] for c in range(K))
            checks.append(dict(check='direct/weighted profile score', passed=abs(score - matrix_score) < 1e-7))
            checks.append(dict(check='profile assignment dual bound', passed=certificate['success'] and abs(certificate['gap']) <= 1e-7 and certificate['minimum_slack'] > -1e-7))
            maps = dict(collapsed_profile=mapping.tolist())
            maps['reference_selected_four'] = mapping.tolist() if selected == 'collapsed_profile' else rows[key[0], key[1], shift, key[2], selected]['mapping']
            for name, chosen in maps.items():
                outcomes.append(dict(**condition, algorithm=name, mapping=chosen, exact_recovery=chosen == case['truth'],
                                     symbol_accuracy=sum(a == b for a, b in zip(chosen, case['truth'])) / K,
                                     collapsed_train_log2=fitted.score(case['training'], chosen) / math.log(2),
                                     collapsed_test_bits_per_token=-fitted.score(case['heldout'], chosen) / (2400 * math.log(2)),
                                     reference_choice=selected))
    combined = list(result['rows']) + outcomes
    aggregates = []
    for variant in ('same_length_0', 'same_length_35', 'same_length_70'):
        for size in (40, 400):
            for method in ('collapsed_profile', 'reference_selected_four'):
                group = [r for r in outcomes if r['variant'] == variant and r['reference_records'] == size and r['algorithm'] == method]
                aggregates.append(dict(variant=variant, reference_records=size, algorithm=method, complete_recovery=sum(r['exact_recovery'] for r in group),
                                       conditions=len(group), mean_symbol_accuracy=math.fsum(r['symbol_accuracy'] for r in group) / len(group)))
    seeds = sorted({r['seed'] for r in combined})
    draws = np.random.default_rng(1510261002).integers(0, 12, (20000, 12))
    paired = []
    for variant in ('same_length_0', 'same_length_35', 'same_length_70'):
        for method, comparator in [('latent_mixture', 'collapsed_profile'), ('reference_selected_four', 'reference_selected_three')]:
            for metric in ('exact_recovery', 'symbol_accuracy'):
                delta = []
                for seed in seeds:
                    means = {name: math.fsum(float(r[metric]) for r in combined if r['seed'] == seed and r['variant'] == variant and r['algorithm'] == name) / 4 for name in (method, comparator)}
                    delta.append(means[method] - means[comparator])
                differences = np.asarray(delta)
                paired.append(dict(variant=variant, algorithm=method, comparator=comparator, metric=metric, mean_difference=float(differences.mean()),
                                   percentile_95_interval=np.quantile(differences[draws].mean(axis=1), [.025, .975]).tolist(), system_differences=delta,
                                   systems=12, conditions_per_system=4, bootstrap_draws=20000, bootstrap_seed=1510261002))
    checks.append(dict(check='frozen input hashes', passed=all(digest(ROOT / path) == sha for path, sha in hashes.items())))
    summary = dict(completed_utc=datetime.now(timezone.utc).isoformat(), protocol_sha256=digest(BASE / 'COLLAPSED_PROTOCOL.md'),
                   code_sha256=digest(Path(__file__)), source_hashes=hashes, checks_total=len(checks), checks_passed=sum(c['passed'] for c in checks),
                   checks=checks, aggregates=aggregates, choice_counts=dict(Counter(f"{c['variant']}/{c['reference_records']}/{c['selected']}" for c in choices)))
    for name, value in [('verification.json', summary), ('rows.json', outcomes), ('reference-choices.json', choices), ('assignment-duals.json', certificates), ('paired-comparisons.json', paired)]:
        write(out / name, value)
    (out / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(checks=summary['checks_total'], passed=summary['checks_passed'], aggregates=aggregates, choices=summary['choice_counts'])))


if __name__ == '__main__':
    main()
