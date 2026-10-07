"""Aggregate identical queries and paired component-bootstrap contrasts."""
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from data import Corpus, ROOT, OWN, RAW, old, UNKNOWN, save, digest
from run import read_json, read_prob

METRICS = ['top1', 'top5', 'top10', 'bucket_loss_bits', 'common_bucket_loss_bits']

def ordered(c, scores):
    bykey = {(s['record_id'], s['slot']): s for s in scores}
    assert len(scores) == len(bykey) == 8009
    result = [bykey[k] for k in c.keys]
    for a, b in zip(c.template, result):
        assert all(a[k] == b[k] for k in ['record_id', 'slot', 'actual', 'fold', 'group', 'length', 'artifact'])
    return result

def common_loss(c, scores, p, signs, fold):
    """Coarsen added-text outputs to the original outer-training alphabet."""
    train, test, _, _ = c.outer(fold)
    alphabet = {s for r in train for s in r['seq']}
    index = {s: i for i, s in enumerate(signs)}
    novel = [i for i, s in enumerate(signs) if s not in alphabet]
    unknown_mass = p[:, novel].sum(axis=1)
    actuals = [s for r in test for s in r['seq']]
    assert len(actuals) == len(scores) == len(p)
    for i, (s, actual) in enumerate(zip(scores, actuals)):
        assert s['actual'] == actual
        mass = p[i, index[actual]] if actual in alphabet and actual in index else unknown_mass[i]
        s['common_bucket_loss_bits'] = -float(np.log2(max(mass, 1e-300)))
    return scores

def load_prediction(c, info, fold):
    p, signs = read_prob(ROOT / info['probability_file'])
    assert digest(ROOT / info['probability_file']) == info['probability_sha256']
    values = old.read_jsonl(ROOT / info['query_file'])
    assert digest(ROOT / info['query_file']) == info['query_sha256']
    return common_loss(c, values, p, signs, fold)

def subset_summary(scores):
    result = {'slots': len(scores)}
    for k in METRICS:
        result[k] = float(np.mean([s[k] for s in scores])) if scores else None
    ece = 0.
    for i in range(5):
        ss = [s for s in scores if min(int(s['model_top_mass'] * 5), 4) == i]
        if ss:
            ece += abs(sum(s['model_top_mass'] - int(s['top1']) for s in ss)) / len(scores)
    result['expected_calibration_error'] = ece if scores else None
    result['unknown_true_rate'] = float(np.mean([not s['known_in_training'] for s in scores])) if scores else None
    return result

def strata(c):
    labels = {'all': np.ones(8009, dtype=bool)}
    for pos in ['initial', 'internal', 'final']:
        labels['position/' + pos] = np.array([s['position'] == pos for s in c.template])
    for name, lo, hi in [('1', 1, 1), ('2-4', 2, 4), ('5-19', 5, 19), ('20+', 20, 8009)]:
        labels['frequency/' + name] = np.array([lo <= c.frequencies[s['actual']] <= hi for s in c.template])
    return labels

def bootstrap_matrix(c, repeats=2000):
    rng = np.random.default_rng(23101)
    # Same draws as sampling 1,526 component indices with replacement.
    weights = np.zeros((repeats, len(c.groups)), dtype=np.float64)
    for i in range(repeats):
        weights[i] = np.bincount(rng.integers(0, len(c.groups), len(c.groups)), minlength=len(c.groups))
    return weights

def paired(c, first, second, labels, draws):
    result = {}
    group = np.array([s['group'] for s in c.template])
    n_groups = len(c.groups)
    for label, mask in labels.items():
        count = np.bincount(group[mask], minlength=n_groups).astype(float)
        denominators = draws @ count
        valid = denominators > 0
        entry = {'slots': int(mask.sum()), 'groups_with_queries': int((count > 0).sum()), 'metrics': {}}
        for metric in METRICS:
            delta = np.array([float(b[metric]) - float(a[metric]) for a, b in zip(first, second)])
            sums = np.bincount(group[mask], weights=delta[mask], minlength=n_groups)
            boot = (draws @ sums)[valid] / denominators[valid]
            entry['metrics'][metric] = {'difference': float(delta[mask].mean()),
                'component_bootstrap_95_ci': np.quantile(boot, [.025, .975]).tolist()}
        # ECE is nonlinear: recompute bin sums and absolute values in each draw.
        samples, points = [], []
        for scores in [first, second]:
            mass = np.array([s['model_top_mass'] for s in scores])
            correct = np.array([s['top1'] for s in scores]).astype(float)
            bins = np.minimum((mass * 5).astype(int), 4)
            sums = np.stack([np.bincount(group[mask & (bins == j)],
                weights=(mass - correct)[mask & (bins == j)], minlength=n_groups) for j in range(5)], axis=1)
            samples.append(np.abs(draws @ sums)[valid].sum(axis=1) / denominators[valid])
            points.append(float(np.abs(sums.sum(axis=0)).sum() / count.sum()))
        entry['metrics']['expected_calibration_error'] = {'difference': points[1] - points[0],
            'component_bootstrap_95_ci': np.quantile(samples[1] - samples[0], [.025, .975]).tolist()}
        result[label] = entry
    return {'direction': 'new minus comparator', 'repeats': len(draws), 'seed': 23101,
        'bootstrap_population_components': n_groups, 'strata': result}

def summarize(c, scores, labels):
    result = old.summarize(scores)
    result['strata'] = {label: subset_summary([s for s, included in zip(scores, mask) if included]) for label, mask in labels.items()}
    result['common_alphabet_bucket_cross_entropy_bits'] = result['strata']['all']['common_bucket_loss_bits']
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='main')
    parser.add_argument('--output', default='aggregate-results.json')
    parser.add_argument('--curves', action='store_true')
    parser.add_argument('--families', nargs='+', default=['classical', 'gru', 'transformer', 'metadata', 'ensemble'])
    args = parser.parse_args()
    c = Corpus(); labels = strata(c); draws = bootstrap_matrix(c)
    for ss in c.references.values():
        for s in ss:
            s['common_bucket_loss_bits'] = s['bucket_loss_bits']
    result = {'status': 'Exploratory', 'queries': 8009, 'components': 1526,
        'benchmark_audit_sha256': digest(OWN / 'benchmark-audit.json'),
        'native_loss_note': 'Additional text can introduce new codes. Common-alphabet loss coarsens their mass into the original fold UNKNOWN bucket.',
        'comparators': {n: summarize(c, ordered(c, ss), labels) for n, ss in c.references.items()}, 'models': {}, 'direct_contrasts': {}}
    allscores = {}
    if not args.curves:
        for added in [False, True]:
            for family in args.families:
                for objective in ['loss', 'top1']:
                    name = f'{family}/extra{int(added)}/{objective}'
                    scores, entries, by_seed = [], [], {str(s): [] for s in [20261006, 20261007, 20261008]}
                    for fold in range(5):
                        e = read_json(OWN / args.run / f'{family}-f{fold}-extra{int(added)}-selection.json')
                        info = e['outer'][objective]
                        scores += load_prediction(c, info, fold)
                        entries.append({'fold': fold, 'selected_index': e['selected'][objective], 'inner': e['inner'],
                            'config': info.get('config'), 'ngram_weight': info.get('ngram_weight'),
                            'neural_family': e.get('family'), 'epochs': info.get('epochs')})
                        if family in ['gru', 'transformer', 'metadata']:
                            for seed in by_seed:
                                p, signs = read_prob(RAW / args.run / (info['label'] + f'-s{seed}.npz'))
                                _, test, _, _ = c.outer(fold)
                                one = c.scores(test, p, signs)
                                by_seed[seed] += common_loss(c, one, p, signs, fold)
                    scores = ordered(c, scores)
                    allscores[name] = scores
                    entry = {'summary': summarize(c, scores, labels), 'fold_selection': entries,
                        'paired': {n: paired(c, ordered(c, ss), scores, labels, draws) for n, ss in c.references.items()}}
                    if any(by_seed.values()):
                        entry['seed_summaries'] = {s: summarize(c, ordered(c, ss), labels) for s, ss in by_seed.items()}
                        entry['seed_range'] = {k: [min(e[k] for e in entry['seed_summaries'].values()), max(e[k] for e in entry['seed_summaries'].values())]
                            for k in ['top1', 'top5', 'top10', 'bucket_cross_entropy_bits', 'expected_calibration_error']}
                    result['models'][name] = entry
                    print(name, entry['summary']['top1'], entry['summary']['bucket_cross_entropy_bits'], flush=True)
        for family in args.families:
            a, b = f'{family}/extra0/loss', f'{family}/extra1/loss'
            result['direct_contrasts'][family + '/extra_minus_noextra'] = paired(c, allscores[a], allscores[b], labels, draws)
        for added in ([False, True] if 'metadata' in args.families else []):
            unconditioned = []
            for fold in range(5):
                meta = read_json(OWN / args.run / f'metadata-f{fold}-extra{int(added)}-selection.json')
                e = read_json(OWN / args.run / f'{meta["family"]}-f{fold}-extra{int(added)}-selection.json')
                unconditioned += load_prediction(c, e['outer']['loss'], fold)
            result['direct_contrasts'][f'metadata/extra{int(added)}/conditioned_minus_selected_family'] = paired(c, ordered(c, unconditioned), allscores[f'metadata/extra{int(added)}/loss'], labels, draws)
    else:
        result['native_loss_note'] += ' Learning-curve subsets can also omit codes known in the full outer training set; they remain pooled in UNKNOWN, so curve loss comparisons retain vocabulary-coarsening differences. Accuracy and OOV rates are the curve diagnostics.'
        for added in [False, True]:
            for family in ['classical', 'neural']:
                for fraction in [.25, .5, .75, 1.]:
                    name = f'{family}/extra{int(added)}/p{int(fraction*100)}'
                    scores, entries = [], []
                    by_seed = {str(s): [] for s in [20261006, 20261007, 20261008]}
                    for fold in range(5):
                        e = read_json(OWN / args.run / f'curve-f{fold}-extra{int(added)}-p{int(fraction*100)}.json')
                        scores += load_prediction(c, e[family], fold)
                        entries.append({k: e[k] for k in ['fold', 'fraction', 'training_components', 'training_texts', 'training_tokens', 'neural_family']})
                        if family == 'neural':
                            base = ROOT / e[family]['probability_file']
                            for seed in by_seed:
                                p, signs = read_prob(base.with_name(base.stem + f'-s{seed}.npz'))
                                _, test, _, _ = c.outer(fold)
                                one = c.scores(test, p, signs)
                                by_seed[seed] += common_loss(c, one, p, signs, fold)
                    scores = ordered(c, scores)
                    allscores[name] = scores
                    result['models'][name] = {'summary': summarize(c, scores, labels), 'training': entries,
                        'paired': {n: paired(c, ordered(c, ss), scores, labels, draws) for n, ss in c.references.items()}}
                    if family == 'neural':
                        result['models'][name]['seed_summaries'] = {s: summarize(c, ordered(c, ss), labels) for s, ss in by_seed.items()}
                    print(name, result['models'][name]['summary']['top1'], flush=True)
                result['direct_contrasts'][f'{family}/extra{int(added)}/100_minus_75'] = paired(c, allscores[f'{family}/extra{int(added)}/p75'], allscores[f'{family}/extra{int(added)}/p100'], labels, draws)
    save(OWN / args.output, result)

if __name__ == '__main__':
    main()
