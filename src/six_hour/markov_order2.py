"""Second-order masked-state restoration with a first-order backoff prior."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src/six_hour'))
import markov_baseline as baseline
GRID = [5, 20, 100, 500, 2000, None]


class Restorer:
    def __init__(self, rows, alpha):
        self.base = baseline.MarkovRestorer(rows, 20)
        self.signs, self.index = self.base.signs, self.base.index
        self.end_index = self.base.end_index
        self.start_index = self.end_index+1
        self.alpha = alpha
        counts = defaultdict(Counter)
        for row in rows:
            sequence = [self.index[s] for s in row['seq']]+[self.end_index]
            a = b = self.start_index
            for target in sequence:
                counts[a, b][target] += 1
                a, b = b, target
        self.observed = {}
        for history, targets in counts.items():
            if alpha is None:
                continue
            prior = self.prior(history[1])
            values = alpha*prior.copy()
            for target, number in targets.items():
                values[target] += number
            self.observed[history] = values/(sum(targets.values())+alpha)
        assert all(abs(v.sum()-1) < 1e-12 for v in self.observed.values())

    def prior(self, latest):
        return np.r_[self.base.start, 0.] if latest == self.start_index else self.base.transition[latest]

    def probability(self, first, latest):
        values = self.observed.get((first, latest))
        return values if values is not None else self.prior(latest)

    def distribution(self, row, slot):
        if self.alpha is None:
            return self.base.distribution(row, slot)
        n = self.end_index
        sequence = [self.index.get(v, self.index[baseline.UNKNOWN]) for v in row['seq']]+[n]
        score = np.ones(n)
        for position in range(slot, min(len(sequence), slot+3)):
            a = self.start_index if position < 2 else sequence[position-2]
            b = self.start_index if position < 1 else sequence[position-1]
            if position == slot:
                score *= self.probability(a, b)[:n]
            elif position == slot+1:
                target = sequence[position]
                score *= np.array([self.probability(a, candidate)[target] for candidate in range(n)])
            else:
                target = sequence[position]
                score *= np.array([self.probability(candidate, b)[target] for candidate in range(n)])
        return score/score.sum()

    def score_rows(self, rows, details=False):
        # Existing reporting uses only distribution(), signs and index.
        return baseline.MarkovRestorer.score_rows(self, rows, details=details)


def tune(rows, seed, criterion='top1'):
    groups = baseline.group_records(rows)
    assignments, _ = baseline.make_folds(rows, groups, 3, seed)
    totals = Counter()
    losses = Counter()
    for fold in range(3):
        train = [r for i, r in enumerate(rows) if assignments[i] != fold]
        test = [r for i, r in enumerate(rows) if assignments[i] == fold]
        for alpha in GRID:
            scores = Restorer(train, alpha).score_rows(test)
            totals[alpha] += sum(s['top1'] for s in scores)
            losses[alpha] += sum(s['bucket_loss_bits'] for s in scores)
    chosen = max(GRID, key=lambda alpha: (totals[alpha] if criterion == 'top1' else -losses[alpha], GRID.index(alpha)))
    slots = sum(len(r['seq']) for r in rows)
    names = [str(a) if a is not None else 'backoff_only' for a in GRID]
    return chosen, dict(zip(names, [totals[a]/slots for a in GRID])), dict(zip(names, [losses[a]/slots for a in GRID]))


def self_test():
    rows = [{'seq': tuple(s)} for s in ['ABC', 'ABC', 'ACB', 'BAC', 'CAC', 'BBB', 'CAB']]
    model = Restorer(rows, 2)
    query = {'seq': ('A', 'B', 'C')}
    tests = {}
    for slot in range(3):
        full = []
        for candidate in model.signs:
            seq = [model.index[v] for v in query['seq']]
            seq[slot] = model.index[candidate]
            seq.append(model.end_index)
            a = b = model.start_index
            value = 1.
            for target in seq:
                value *= model.probability(a, b)[target]
                a, b = b, target
            full.append(value)
        expected = np.array(full)/sum(full)
        tests[f'complete_likelihood_slot_{slot}'] = bool(np.allclose(expected, model.distribution(query, slot), atol=1e-14, rtol=1e-12))
        hidden = list(query['seq']); hidden[slot] = 'REPLACED_TARGET'
        tests[f'hidden_target_independence_{slot}'] = bool(np.array_equal(model.distribution({'seq': hidden}, slot), model.distribution(query, slot)))
    backoff = Restorer(rows, None)
    tests['backoff_exact_first_order'] = all(np.array_equal(backoff.distribution(query, s), backoff.base.distribution(query, s)) for s in range(3))
    tests['second_history_changes_row'] = not np.allclose(model.probability(model.index['A'], model.index['B']), model.probability(model.index['B'], model.index['B']))
    tests['all_rows_normalized'] = all(abs(p.sum()-1) < 1e-12 for p in model.observed.values())
    tests['boundary_states_excluded_from_candidate_alphabet'] = len(model.distribution(query, 0)) == len(model.signs)
    assert all(tests.values()), tests
    return tests


def run(args):
    out = ROOT/args.output
    if out.exists():
        raise RuntimeError('Use a fresh endpoint.')
    out.mkdir(parents=True)
    started = time.perf_counter()
    try:
        tests = self_test()
        source = ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl'
        original = ROOT/'results/restoration'
        benchmark = json.loads((original/'benchmark.json').read_text(encoding='utf-8'))
        assert baseline.digest(source) == benchmark['input_sha256']
        rows, exclusions = baseline.load_records(source, min_length=3, unique=True)
        groups = baseline.group_records(rows)
        assignments, loads = baseline.make_folds(rows, groups, 5, 20261006)
        pm = baseline.read_jsonl(original/'baseline_slot_audit.jsonl')
        pmb = baseline.read_jsonl(original/'local_slot_audit.jsonl')
        lookup, correspondence = baseline.verify_saved(rows, groups, assignments, loads, benchmark, pm, pmb)
        first = baseline.read_jsonl(ROOT/'experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl')
        scores = []; folds = []
        for fold in ([0] if args.pilot else range(5)):
            train = [r for i, r in enumerate(rows) if assignments[i] != fold]
            test = [r for i, r in enumerate(rows) if assignments[i] == fold]
            chosen, inner, inner_loss = tune(train, 20261006+fold, args.criterion)
            model = Restorer(train, chosen)
            current = model.score_rows(test, details=True)
            for row in current:
                row['fold'] = fold; row['group'] = lookup[row['record_id']]
            scores.extend(current)
            folds.append({'fold': fold, 'chosen_alpha': chosen, 'inner_top1': inner, 'vocabulary': len(model.signs),
                'inner_bucket_loss': inner_loss, 'selection_criterion': args.criterion,
                'train_texts': len(train), 'test_texts': len(test), 'observed_two_state_histories': len(model.observed)})
            print(json.dumps({'fold': fold, 'alpha': chosen, 'seconds': time.perf_counter()-started}), flush=True)
        selected = {(r['record_id'], r['slot']) for r in scores}
        comparators = {name: [r for r in old if (r['record_id'], r['slot']) in selected] for name, old in [('Markov1', first), ('PMB', pmb)]}
        if args.criterion == 'bucket_loss':
            earlier = baseline.read_jsonl(ROOT/'experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl')
            comparators['Markov2_top1_selected'] = [r for r in earlier if (r['record_id'], r['slot']) in selected]
        for old in comparators.values():
            for a, b in zip(scores, old):
                assert tuple(a[k] for k in ['record_id', 'slot', 'actual', 'fold', 'group']) == tuple(b[k] for k in ['record_id', 'slot', 'actual', 'fold', 'group'])
        result = {'experiment_id': 'MARKOV-04' if args.criterion == 'bucket_loss' else 'MARKOV-03',
            'status': 'one-fold-pilot' if args.pilot else 'declared-post-comparator-model',
            'parameters': vars(args), 'self_tests': tests, 'correspondence': correspondence, 'folds': folds, 'exclusions': exclusions,
            'models': {'Markov2': baseline.summarize(scores), **{name: baseline.summarize(old) for name, old in comparators.items()}},
            'paired': {name: baseline.paired(old, scores, args.bootstrap, seed=23101) for name, old in comparators.items()},
            'input_sha256': baseline.digest(source), 'source_sha256': baseline.digest(__file__),
            'helper_sha256': baseline.digest(ROOT/'src/six_hour/markov_baseline.py'),
            'protocol_sha256': baseline.digest(out.parent/'PROTOCOL.md'), 'elapsed_seconds': time.perf_counter()-started}
        (out/'markov2_slot_audit.jsonl').write_text('\n'.join(json.dumps(r) for r in scores)+'\n', encoding='utf-8')
        (out/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
        print(json.dumps({'top1': result['models']['Markov2']['top1'], 'seconds': result['elapsed_seconds']}))
    except Exception as error:
        (out/'failure.json').write_text(json.dumps({'type': type(error).__name__, 'message': str(error)}, indent=2)+'\n', encoding='utf-8')
        (out/'failed_code_snapshot.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--pilot', action='store_true')
    parser.add_argument('--bootstrap', type=int, default=10000)
    parser.add_argument('--criterion', choices=['top1','bucket_loss'], default='top1')
    parser.add_argument('--output', default='experiments/2026-10-02-six-hour/markov-order2/main')
    args = parser.parse_args()
    print(json.dumps(self_test())) if args.self_test else run(args)
