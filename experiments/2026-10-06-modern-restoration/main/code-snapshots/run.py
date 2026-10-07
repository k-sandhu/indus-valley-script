"""Rerunnable stages, resumable caches and refusing-to-overwrite endpoints."""
import argparse
import json
import math
import pickle
import time
from pathlib import Path
import numpy as np
from data import Corpus, ROOT, OWN, RAW, SEED, UNKNOWN, old, digest, save, probability_stats
from models import MKN, NGRAM_GRID, NEURAL_GRID, SEEDS, fit_net, predict_net, self_test

def progress(**values):
    print(json.dumps(values), flush=True)

def mean_inner(entries):
    n = sum(e['slots'] for e in entries)
    return {k: sum(e[k] * e['slots'] for e in entries) / n for k in ['top1', 'bucket_loss_bits']}

def choices(stats):
    loss = min(range(len(stats)), key=lambda j: (stats[j]['bucket_loss_bits'], j))
    acc = min(range(len(stats)), key=lambda j: (-stats[j]['top1'], j))
    return {'loss': loss, 'top1': acc}

def artifact_paths(run, label):
    return RAW / run / (label + '.npz'), OWN / run / (label + '.json')

def cache_prob(path, probs, signs):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    np.savez_compressed(path, probs=probs, signs=np.array(signs))

def read_prob(path):
    with np.load(path, allow_pickle=False) as f:
        return f['probs'], f['signs'].tolist()

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def write_scores(corpus, run, label, rows, probs, signs, seed_probs=None):
    scores = corpus.scores(rows, probs, signs)
    path = RAW / run / (label + '-queries.jsonl')
    if path.exists():
        raise FileExistsError(path)
    path.write_text(''.join(json.dumps(s) + '\n' for s in scores), encoding='utf-8')
    result = {'summary': old.summarize(scores), 'probability_file': str((RAW / run / (label + '.npz')).relative_to(ROOT)).replace('\\', '/'),
        'query_file': str(path.relative_to(ROOT)).replace('\\', '/'), 'probability_sha256': digest(RAW / run / (label + '.npz')),
        'query_sha256': digest(path)}
    if seed_probs is not None:
        result['seeds'] = {str(seed): old.summarize(corpus.scores(rows, p, signs)) for seed, p in zip(SEEDS, seed_probs)}
    return result

def classical(c, run):
    for fold in range(5):
        train, test, extra, extra_detail = c.outer(fold)
        for added in [False, True]:
            label = f'classical-f{fold}-extra{int(added)}'
            final = OWN / run / (label + '-selection.json')
            if final.exists():
                continue
            totals = [[] for _ in NGRAM_GRID]
            details = []
            for inner, (fit, val, more, detail) in enumerate(c.inner(fold)):
                details.append(detail)
                for j, config in enumerate(NGRAM_GRID):
                    name = f'{label}-inner{inner}-c{j}'
                    probpath, statpath = artifact_paths(run, name)
                    if statpath.exists():
                        info = read_json(statpath)
                    else:
                        start = time.perf_counter()
                        m = MKN(fit + (more if added else []), **config)
                        p = m.predict(val)
                        cache_prob(probpath, p, m.signs)
                        info = {**probability_stats(val, p, m.signs), 'config': config,
                            'discounts': m.discounts, 'seconds': time.perf_counter() - start,
                            'train_texts': len(fit), 'extra': detail if added else None}
                        save(statpath, info)
                    totals[j].append(info)
                progress(stage='classical_inner', fold=fold, extra=added, inner=inner)
            stats = [mean_inner(e) for e in totals]
            selected = choices(stats)
            outer = {}
            for objective, j in selected.items():
                name = f'{label}-outer-c{j}'
                probpath, statpath = artifact_paths(run, name)
                if statpath.exists():
                    info = read_json(statpath)
                else:
                    m = MKN(train + (extra if added else []), **NGRAM_GRID[j])
                    p = m.predict(test)
                    cache_prob(probpath, p, m.signs)
                    info = write_scores(c, run, name, test, p, m.signs)
                    info.update(config=NGRAM_GRID[j], discounts=m.discounts)
                    with (RAW / run / (name + '-counts.pkl')).open('wb') as f:
                        pickle.dump(m, f)
                    save(statpath, info)
                outer[objective] = {'config_index': j, 'label': name, **info}
            save(final, {'fold': fold, 'extra': added, 'grid': NGRAM_GRID, 'inner': stats,
                'selected': selected, 'outer': outer, 'extra_detail': extra_detail, 'inner_extra_details': details})
            progress(stage='classical_outer', fold=fold, extra=added, metrics=outer['loss']['summary'])

def neural_inner(c, run, fold, added, family, configs, prefix):
    totals = [[] for _ in configs]
    for inner, (fit, val, more, detail) in enumerate(c.inner(fold)):
        for j, config in enumerate(configs):
            base_label = f'{prefix}-inner{inner}-c{j}'
            meanpath, meanstat = artifact_paths(run, base_label)
            if meanstat.exists():
                totals[j].append(read_json(meanstat))
                continue
            probs, infos, signs = [], [], None
            for seed in SEEDS:
                name = f'{base_label}-s{seed}'
                probpath, statpath = artifact_paths(run, name)
                if statpath.exists():
                    p, current_signs = read_prob(probpath)
                    info = read_json(statpath)
                else:
                    model, encoder, p, info = fit_net(fit + (more if added else []), val, config, seed)
                    current_signs = encoder.signs
                    cache_prob(probpath, p, current_signs)
                    info.update(config=config, validation=probability_stats(val, p, current_signs),
                        extra=detail if added else None)
                    save(statpath, info)
                    del model
                assert signs is None or signs == current_signs
                signs = current_signs
                probs.append(p); infos.append(info)
                progress(stage='neural_inner_seed', family=family, fold=fold, extra=added,
                    inner=inner, config=j, seed=seed, epochs=info['epochs'], seconds=info['seconds'])
            meanp = np.mean(probs, axis=0)
            cache_prob(meanpath, meanp, signs)
            stat = {**probability_stats(val, meanp, signs), 'config': config,
                'epochs': {str(seed): info['epochs'] for seed, info in zip(SEEDS, infos)},
                'seed_validation': {str(seed): info['validation'] for seed, info in zip(SEEDS, infos)}}
            save(meanstat, stat)
            totals[j].append(stat)
    return [mean_inner(e) for e in totals], totals

def neural_outer(c, run, train, test, extra, config, epochs, label):
    probpath, statpath = artifact_paths(run, label)
    if statpath.exists():
        return read_json(statpath)
    probs, infos, signs = [], [], None
    for seed in SEEDS:
        name = f'{label}-s{seed}'
        onepath, onestat = artifact_paths(run, name)
        if onestat.exists():
            p, current_signs = read_prob(onepath)
            info = read_json(onestat)
        else:
            checkpoint = RAW / run / (name + '-weights.pt')
            model, encoder, _, info = fit_net(train + extra, None, config, seed,
                epochs=epochs[str(seed)], checkpoint=checkpoint)
            p = predict_net(model, encoder.dataset(test))
            current_signs = encoder.signs
            cache_prob(onepath, p, current_signs)
            info.update(summary=old.summarize(c.scores(test, p, current_signs)), weights_sha256=digest(checkpoint), config=config)
            save(onestat, info)
            del model
        assert signs is None or signs == current_signs
        signs = current_signs
        probs.append(p); infos.append(info)
        progress(stage='neural_outer_seed', label=label, seed=seed, epochs=info['epochs'], seconds=info['seconds'])
    meanp = np.mean(probs, axis=0)
    cache_prob(probpath, meanp, signs)
    info = write_scores(c, run, label, test, meanp, signs, probs)
    info.update(config=config, epochs=epochs, seed_fits=infos)
    save(statpath, info)
    return info

def neural(c, run):
    for fold in range(5):
        train, test, extra, extra_detail = c.outer(fold)
        for added in [False, True]:
            for family, configs in NEURAL_GRID.items():
                prefix = f'{family}-f{fold}-extra{int(added)}'
                final = OWN / run / (prefix + '-selection.json')
                if final.exists():
                    continue
                stats, totals = neural_inner(c, run, fold, added, family, configs, prefix)
                selected, outer = choices(stats), {}
                for objective, j in selected.items():
                    epochs = {str(seed): int(math.ceil(np.median([e['epochs'][str(seed)] for e in totals[j]]))) for seed in SEEDS}
                    label = f'{prefix}-outer-c{j}'
                    info = neural_outer(c, run, train, test, extra if added else [], configs[j], epochs, label)
                    outer[objective] = {'config_index': j, 'label': label, **info}
                save(final, {'fold': fold, 'extra': added, 'family': family, 'grid': configs,
                    'inner': stats, 'selected': selected, 'outer': outer, 'extra_detail': extra_detail})
                progress(stage='neural_selection', family=family, fold=fold, extra=added, inner=stats)

def metadata(c, run):
    for fold in range(5):
        train, test, extra, detail = c.outer(fold)
        for added in [False, True]:
            prefix = f'metadata-f{fold}-extra{int(added)}'
            final = OWN / run / (prefix + '-selection.json')
            if final.exists():
                continue
            earlier = {family: read_json(OWN / run / f'{family}-f{fold}-extra{int(added)}-selection.json') for family in NEURAL_GRID}
            family = min(earlier, key=lambda f: (earlier[f]['inner'][earlier[f]['selected']['loss']]['bucket_loss_bits'], list(NEURAL_GRID).index(f)))
            baseconfig = earlier[family]['outer']['loss']['config']
            configs = [{**baseconfig, 'metadata': True}]
            stats, totals = neural_inner(c, run, fold, added, family, configs, prefix)
            epochs = {str(seed): int(math.ceil(np.median([e['epochs'][str(seed)] for e in totals[0]]))) for seed in SEEDS}
            label = f'{prefix}-outer-c0'
            info = neural_outer(c, run, train, test, extra if added else [], configs[0], epochs, label)
            entry = {'config_index': 0, 'label': label, **info}
            save(final, {'fold': fold, 'extra': added, 'family': family, 'grid': configs, 'inner': stats,
                'selected': {'loss': 0, 'top1': 0}, 'outer': {'loss': entry, 'top1': entry},
                'base_family_inner': {f: e['inner'][e['selected']['loss']] for f, e in earlier.items()}, 'extra_detail': detail})
            progress(stage='metadata_selection', fold=fold, extra=added, family=family, inner=stats)

def geometric(a, b, weight):
    logits = weight * np.log(a.clip(1e-300)) + (1 - weight) * np.log(b.clip(1e-300))
    logits -= logits.max(axis=1, keepdims=True)
    p = np.exp(logits)
    return p / p.sum(axis=1, keepdims=True)

def constituent(run, fold, added, family):
    e = read_json(OWN / run / f'{family}-f{fold}-extra{int(added)}-selection.json')
    j = e['selected']['loss']
    return e, j

def best_neural(run, fold, added):
    options = {f: constituent(run, fold, added, f)[0] for f in ['gru', 'transformer', 'metadata']}
    return min(options, key=lambda f: (options[f]['inner'][options[f]['selected']['loss']]['bucket_loss_bits'], list(options).index(f)))

def ensemble(c, run):
    weights = [0., .25, .5, .75, 1.]
    for fold in range(5):
        _, test, _, _ = c.outer(fold)
        for added in [False, True]:
            prefix = f'ensemble-f{fold}-extra{int(added)}'
            final = OWN / run / (prefix + '-selection.json')
            if final.exists():
                continue
            ce, cj = constituent(run, fold, added, 'classical')
            family = best_neural(run, fold, added)
            ne, nj = constituent(run, fold, added, family)
            totals = [[] for _ in weights]
            for inner, (_, val, _, _) in enumerate(c.inner(fold)):
                a, signs = read_prob(RAW / run / f'classical-f{fold}-extra{int(added)}-inner{inner}-c{cj}.npz')
                b, ns = read_prob(RAW / run / f'{family}-f{fold}-extra{int(added)}-inner{inner}-c{nj}.npz')
                assert signs == ns
                for j, weight in enumerate(weights):
                    totals[j].append(probability_stats(val, geometric(a, b, weight), signs))
            stats = [mean_inner(e) for e in totals]
            selected = choices(stats)
            a, signs = read_prob(ROOT / ce['outer']['loss']['probability_file'])
            b, ns = read_prob(ROOT / ne['outer']['loss']['probability_file'])
            assert signs == ns
            outer = {}
            for objective, j in selected.items():
                label = f'{prefix}-outer-c{j}'
                probpath, statpath = artifact_paths(run, label)
                if statpath.exists():
                    info = read_json(statpath)
                else:
                    p = geometric(a, b, weights[j])
                    cache_prob(probpath, p, signs)
                    info = write_scores(c, run, label, test, p, signs)
                    info.update(ngram_weight=weights[j], neural_family=family,
                        classical_config=ce['outer']['loss']['config'], neural_config=ne['outer']['loss']['config'])
                    save(statpath, info)
                outer[objective] = {'config_index': j, 'label': label, **info}
            save(final, {'fold': fold, 'extra': added, 'family': family, 'weights': weights,
                'inner': stats, 'selected': selected, 'outer': outer})
            progress(stage='ensemble_selection', fold=fold, extra=added, family=family, weights={k: weights[v] for k, v in selected.items()})

def curves(c, run):
    for fold in range(5):
        train, test, extra, detail = c.outer(fold)
        groups = old.group_records(train)
        order = np.random.default_rng(SEED + fold).permutation(len(groups))
        for added in [False, True]:
            ce, _ = constituent(run, fold, added, 'classical')
            family = best_neural(run, fold, added)
            ne, _ = constituent(run, fold, added, family)
            for fraction in [.25, .5, .75, 1.]:
                prefix = f'curve-f{fold}-extra{int(added)}-p{int(fraction*100)}'
                final = OWN / run / (prefix + '.json')
                if final.exists():
                    continue
                selected_groups = order[:int(math.ceil(len(groups) * fraction))]
                indices = {i for g in selected_groups for i in groups[g]}
                subset = [r for i, r in enumerate(train) if i in indices]
                if fraction == 1.:
                    classical_info, neural_info = ce['outer']['loss'], ne['outer']['loss']
                else:
                    label = prefix + '-classical'
                    m = MKN(subset + (extra if added else []), **ce['outer']['loss']['config'])
                    p = m.predict(test)
                    cache_prob(RAW / run / (label + '.npz'), p, m.signs)
                    classical_info = write_scores(c, run, label, test, p, m.signs)
                    classical_info['config'] = ce['outer']['loss']['config']
                    neural_info = neural_outer(c, run, subset, test, extra if added else [], ne['outer']['loss']['config'], ne['outer']['loss']['epochs'], prefix + '-neural')
                save(final, {'fold': fold, 'extra': added, 'fraction': fraction,
                    'training_components': len(selected_groups), 'training_texts': len(subset),
                    'training_tokens': sum(len(r['seq']) for r in subset),
                    'extra_detail': detail if added else None, 'neural_family': family,
                    'classical': classical_info, 'neural': neural_info})
                progress(stage='curve', fold=fold, extra=added, fraction=fraction)

def freeze(c, run):
    record = OWN / 'frozen-model/manifest.json'
    if record.exists():
        raise FileExistsError(record)
    candidates = []
    for added in [False, True]:
        for family in ['classical', 'gru', 'transformer', 'metadata', 'ensemble']:
            entries = [constituent(run, f, added, family)[0] for f in range(5)]
            # Each original training mask appears in four training populations.
            n = [sum(len(r['seq']) for r in c.outer(f)[0]) for f in range(5)]
            loss = np.average([e['inner'][e['selected']['loss']]['bucket_loss_bits'] for e in entries], weights=n)
            candidates.append({'family': family, 'extra': added, 'pooled_inner_bits': float(loss)})
    chosen = min(candidates, key=lambda e: e['pooled_inner_bits'])
    family, added = chosen['family'], chosen['extra']
    entries = [constituent(run, f, added, family)[0] for f in range(5)]
    extra, detail = c.extra([])
    rows = c.rows + (extra if added else [])
    rawdir = RAW / 'frozen-model'; rawdir.mkdir(exist_ok=True)
    def modal_config(values):
        keys = [json.dumps(x, sort_keys=True) for x in values]
        return json.loads(min(set(keys), key=lambda k: (-keys.count(k), keys.index(k))))
    model_files, recipe = [], {}
    if family in ['classical', 'ensemble']:
        config = modal_config([e['outer']['loss']['classical_config' if family == 'ensemble' else 'config'] for e in entries])
        model = MKN(rows, **config)
        path = rawdir / 'counts.pkl'
        with path.open('wb') as f:
            pickle.dump(model, f)
        model_files.append({'path': str(path.relative_to(ROOT)).replace('\\', '/'), 'sha256': digest(path)})
        recipe['classical_config'] = config
    if family != 'classical':
        if family == 'ensemble':
            config = modal_config([e['outer']['loss']['neural_config'] for e in entries])
            neural_entries = [constituent(run, f, added, entries[f]['family'])[0] for f in range(5)]
            recipe['ngram_weight'] = float(np.median([e['outer']['loss']['ngram_weight'] for e in entries]))
        else:
            config = modal_config([e['outer']['loss']['config'] for e in entries])
            neural_entries = entries
        epochs = {str(seed): int(math.ceil(np.median([e['outer']['loss']['epochs'][str(seed)] for e in neural_entries]))) for seed in SEEDS}
        for seed in SEEDS:
            path = rawdir / f'seed-{seed}.pt'
            model, _, _, _ = fit_net(rows, None, config, seed, epochs=epochs[str(seed)], checkpoint=path)
            del model
            model_files.append({'path': str(path.relative_to(ROOT)).replace('\\', '/'), 'sha256': digest(path)})
        recipe.update(neural_config=config, epochs=epochs, seeds=SEEDS)
    save(record, {'status': 'Frozen evaluation', 'created_date': '2026-10-07',
        'selection_status': 'Exploratory carry-forward recipe selected using reused-benchmark inner results',
        'chosen': chosen, 'candidate_inner_losses': candidates, 'recipe': recipe,
        'training_texts': len(rows), 'training_tokens': sum(len(r['seq']) for r in rows),
        'extra_detail': detail if added else None, 'files': model_files,
        'code_sha256': {p.name: digest(p) for p in [OWN / 'data.py', OWN / 'models.py', OWN / 'run.py']},
        'protocol_sha256': digest(OWN / 'PROTOCOL.md'), 'benchmark_audit': c.audit,
        'future_rule': 'Load these counts/weights and recipe unchanged on a newly acquired population. No tuning against fresh targets.'})
    progress(stage='freeze', chosen=chosen)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, choices=['classical', 'neural', 'metadata', 'ensemble', 'curves', 'freeze', 'checks'])
    parser.add_argument('--run', default='main')
    args = parser.parse_args()
    c = Corpus()  # Always verify saved population before any model fitting.
    (OWN / args.run).mkdir(exist_ok=True)
    (RAW / args.run).mkdir(exist_ok=True)
    if args.stage == 'checks':
        save(OWN / args.run / 'checks.json', self_test())
    else:
        globals()[args.stage](c, args.run)

if __name__ == '__main__':
    main()
