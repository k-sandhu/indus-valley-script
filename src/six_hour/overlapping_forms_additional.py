"""Post-outcome objective, observed-label and equality diagnostics."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

try:
    import matplotlib
except ModuleNotFoundError:
    local_runtime = Path(__file__).resolve().parents[2] / 'experiments/2026-10-02-six-hour/stamp-geometry/local-witness/runtime-packages'
    sys.path.append(str(local_runtime))
    import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from overlapping_forms_review import equality, FormModel
from review_reference_selector import Model

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'experiments/2026-10-02-six-hour/overlapping-forms'
VARIANTS = ['separated', 'same_length_0', 'same_length_35', 'same_length_70']
METHODS = ['length_slot', 'graph_multistart', 'reference_selected', 'form_observed_slot']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    out = BASE / 'additional-v1'
    if out.exists():
        raise RuntimeError('Preserve previous endpoints.')
    out.mkdir()
    inputs = [p for folder in ('main-v1', 'review-v1') for p in (BASE / folder).iterdir() if p.is_file()]
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs}
    result = json.loads((BASE / 'main-v1/results.json').read_text())
    audit = json.loads((BASE / 'review-v1/verification.json').read_text())
    reviewed = json.loads((BASE / 'review-v1/reviewed-rows.json').read_text())
    diagnostics = json.loads((BASE / 'review-v1/objective-diagnostics.json').read_text())
    ties = json.loads((BASE / 'review-v1/linear-alternatives.json').read_text())
    worlds = json.loads((BASE / 'main-v1/worlds.json').read_text())
    lookup = {(w['seed'], w['variant'], w['shift']): w for w in worlds}
    bootstrap = np.random.default_rng(1210261002).integers(0, 12, (20000, 12))
    seeds = sorted({r['seed'] for r in reviewed})
    benefits = []
    for variant in VARIANTS:
        for metric in ('exact_recovery', 'symbol_accuracy'):
            differences = []
            for seed in seeds:
                group = [r for r in reviewed if r['seed'] == seed and r['variant'] == variant]
                means = {method: sum(float(r[metric]) for r in group if r['algorithm'] == method) / 4 for method in ('reference_selected', 'form_observed_slot')}
                differences.append(means['form_observed_slot'] - means['reference_selected'])
            delta = np.asarray(differences)
            benefits.append(dict(variant=variant, metric=metric, direction='supplied-form diagnostic minus reference-selected decoder',
                                 mean_difference=float(delta.mean()), percentile_95_interval=np.quantile(delta[bootstrap].mean(axis=1), [.025, .975]).tolist(),
                                 system_differences=differences, systems=12, conditions_per_system=4, bootstrap_seed=1210261002, bootstrap_draws=20000))
    wrong_linear = []
    for row in result['rows']:
        if row['algorithm'] not in ('length_slot', 'form_observed_slot') or row['exact_recovery']:
            continue
        key = row['seed'], row['variant'], row['shift'], row['reference_records']
        world = lookup[key[:3]]
        reference = world['reference'][:key[3]]
        if row['algorithm'] == 'length_slot':
            model = Model(reference, 20)
            training = Counter((len(record), pos, c) for record in world['training'] for pos, c in enumerate(record))
            returned = model.slot(world['training'], row['mapping'])
            truth = model.slot(world['training'], world['truth'])
        else:
            model = FormModel(reference, world['reference_labels'][:key[3]])
            training = Counter((label, pos, c) for record, label in zip(world['training'], world['training_labels']) for pos, c in enumerate(record))
            returned = model.score(world['training'], world['training_labels'], row['mapping'])
            truth = model.score(world['training'], world['training_labels'], world['truth'])
        delta = equality(model.cells, training, row['mapping'], world['truth'])
        wrong_linear.append(dict(condition=list(key), algorithm=row['algorithm'], returned_minus_truth_bits=returned - truth,
                                 exact_truth_likelihood_equal=not delta, prime_exponents=delta if abs(returned - truth) <= 1e-7 else None))
    graph_summary = []
    for variant in VARIANTS:
        failed = [d for d in diagnostics if d['condition'][1] == variant and not d['graph_recovered']]
        graph_summary.append(dict(variant=variant, graph_failures=len(failed),
                                  returned_scores_above_truth=sum(d['graph_returned_minus_truth_bits'] > 1e-7 for d in failed),
                                  truth_scores_above_returned=sum(d['graph_returned_minus_truth_bits'] < -1e-7 for d in failed),
                                  numerical_equalities=sum(abs(d['graph_returned_minus_truth_bits']) <= 1e-7 for d in failed)))
    tie_groups = Counter(f"{t['condition'][1]}/{t['condition'][3]}/{t['algorithm']}" for t in ties if t['witnesses'])
    selected_ties = 0
    for tie in ties:
        if tie['algorithm'] != 'length_slot' or not tie['witnesses']:
            continue
        condition = tuple(tie['condition'])
        row = next(r for r in result['rows'] if tuple(r[n] for n in ('seed', 'variant', 'shift', 'reference_records')) == condition and r['algorithm'] == 'reference_selected')
        selected_ties += int(row['reference_choice'] == 'length_slot')
    summary = dict(completed_utc=datetime.now(timezone.utc).isoformat(), input_hashes=hashes,
                   additional_protocol_sha256=digest(BASE / 'ADDITIONAL_PROTOCOL.md'), code_sha256=digest(Path(__file__)),
                   matplotlib_version=matplotlib.__version__, matplotlib_import_path=matplotlib.__file__,
                   tie_group_counts=dict(tie_groups), selected_conditions_with_exact_slot_ties=selected_ties,
                   graph_objective_diagnostics=graph_summary,
                   wrong_linear_counts=dict(Counter(r['algorithm'] for r in wrong_linear)),
                   wrong_linear_with_exact_truth_equal=dict(Counter(r['algorithm'] for r in wrong_linear if r['exact_truth_likelihood_equal'])),
                   all_input_bytes_preserved=all(digest(ROOT / path) == value for path, value in hashes.items()))
    for name, value in [('label-benefits.json', benefits), ('wrong-linear-truth-equalities.json', wrong_linear), ('summary.json', summary)]:
        write(out / name, value)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    styles = [('length_slot', 'Length/slot', '#0072B2', 'o'), ('graph_multistart', 'Graph', '#D55E00', 's'),
              ('reference_selected', 'Reference selected', '#009E73', '^'), ('form_observed_slot', 'Supplied form labels', '#CC79A7', 'D')]
    for ax, size in zip(axes, (40, 400)):
        for method, label, color, marker in styles:
            ys = [next(r['complete_recovery'] / r['conditions'] * 100 for r in audit['aggregates'] if r['variant'] == variant and r['reference_records'] == size and r['algorithm'] == method) for variant in VARIANTS]
            ax.plot(range(4), ys, label=label, color=color, marker=marker, linewidth=1.5, markersize=5)
        ax.set_title(f'{size} reference records')
        ax.set_xticks(range(4), ['Separated\nlengths', 'Same length\nalpha = 0', 'Same length\nalpha = .35', 'Same length\nalpha = .70'])
        ax.set_ylim(-3, 103)
        ax.grid(axis='y', alpha=.25)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_ylabel('Complete returned maps (%)')
    axes[1].legend(frameon=False, loc='lower left', fontsize=9)
    fig.suptitle('Fresh twenty-symbol administrative systems', fontsize=13)
    fig.tight_layout()
    fig.savefig(out / 'recovery.png', dpi=180)
    fig.savefig(out / 'recovery.svg')
    plt.close(fig)
    (out / 'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
