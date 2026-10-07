"""Review stored calculations, independent scalar MKN checks and trained invariance."""
import argparse
import json
import math
import pickle
from collections import Counter, defaultdict
import numpy as np
import torch
from data import Corpus, ROOT, OWN, RAW, SEED, UNKNOWN, old, digest, save
from models import MKN, MaskedNet, DEVICE, predict_net, self_test
from run import read_json, read_prob

class ScalarMKN:
    """Separate flat counts and scalar recursion, without wildcard indexing."""
    def __init__(self, rows, config, signs):
        self.signs = signs; self.index = {s: i for i, s in enumerate(signs)}
        self.order = config['order']; self.n = len(signs); self.bos = self.n + 1
        occurrence = [Counter() for _ in range(self.order + 1)]
        for r in rows:
            seq = [self.bos] * (self.order - 1) + [self.index[s] for s in r['seq']] + [self.n]
            for pos in range(self.order - 1, len(seq)):
                for k in range(1, self.order + 1):
                    occurrence[k][tuple(seq[pos - k + 1:pos + 1])] += 1
        counts = [Counter() for _ in occurrence]
        counts[-1] = occurrence[-1]
        for k in range(1, self.order):
            followers = defaultdict(set)
            for gram in occurrence[k + 1]:
                followers[gram[1:]].add(gram[0])
            counts[k] = Counter({g: len(lefts) for g, lefts in followers.items()})
        bottom = np.array([counts[1][(i,)] + .5 for i in range(self.n + 1)])
        self.bottom = bottom / bottom.sum(); self.rows = {}; self.discounts = {}
        for k in range(2, self.order + 1):
            coc = Counter(counts[k].values())
            y = coc[1] / (coc[1] + 2 * coc[2]) if coc[1] + 2 * coc[2] else .5
            ds = [1 - 2*y*coc[2]/coc[1] if coc[1] else .5,
                2 - 3*y*coc[3]/coc[2] if coc[2] else 1.,
                3 - 4*y*coc[4]/coc[3] if coc[3] else 1.5]
            self.discounts[k] = [max(.05, min(j - .05, config['discount_scale']*d)) for j, d in enumerate(ds, 1)]
            contexts = defaultdict(Counter)
            for gram, value in counts[k].items():
                contexts[gram[:-1]][gram[-1]] = value
            self.rows[k] = contexts

    def scalar(self, hist, target):
        if not hist:
            return self.bottom[target]
        values = self.rows[len(hist) + 1].get(hist)
        prior = self.scalar(hist[1:], target)
        if values is None:
            return prior
        ds = self.discounts[len(hist) + 1]
        total = sum(values.values())
        value = values.get(target, 0)
        retained = (value - ds[min(value, 3) - 1]) / total if value else 0.
        backoff = sum(ds[min(v, 3) - 1] for v in values.values()) / total
        return retained + backoff * prior

    def complete(self, row, slot):
        seq = [self.index.get(s, self.index[UNKNOWN]) for s in row['seq']]
        probabilities = []
        for candidate in range(self.n):
            current = seq.copy(); current[slot] = candidate
            padded = [self.bos] * (self.order - 1) + current + [self.n]
            logp = 0.
            for pos in range(self.order - 1, len(padded)):
                logp += math.log(self.scalar(tuple(padded[pos - self.order + 1:pos]), padded[pos]))
            probabilities.append(logp)
        p = np.exp(np.array(probabilities) - max(probabilities))
        return p / p.sum()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='main')
    parser.add_argument('--output', default='verification.json')
    parser.add_argument('--classical-only', action='store_true')
    args = parser.parse_args()
    c = Corpus()
    result = {'status': 'Verified computation', 'self_tests': self_test(),
        'correspondence': c.audit['correspondence'], 'classical': [], 'neural': [], 'ensemble': [], 'integrity': []}
    rng = np.random.default_rng(SEED)
    for fold in range(5):
        train, test, extra, detail = c.outer(fold)
        for added in [False, True]:
            entry = read_json(OWN / args.run / f'classical-f{fold}-extra{int(added)}-selection.json')
            checked = set()
            for objective in ['loss', 'top1']:
                info = entry['outer'][objective]
                if info['label'] in checked:
                    continue
                checked.add(info['label'])
                p, signs = read_prob(ROOT / info['probability_file'])
                rebuilt = MKN(train + (extra if added else []), **info['config'])
                q = rebuilt.predict(test)
                assert signs == rebuilt.signs and np.array_equal(p, q)
                independent = ScalarMKN(train + (extra if added else []), info['config'], signs)
                queries = []
                j = 0
                for r in test:
                    for slot in range(len(r['seq'])):
                        queries.append((r, slot, j)); j += 1
                indices = sorted(set([0, len(queries) - 1] + rng.choice(len(queries), 12, replace=False).tolist()))
                maximum = 0.
                for i in indices:
                    r, slot, j = queries[i]
                    full = independent.complete(r, slot)
                    maximum = max(maximum, float(np.max(np.abs(full - p[j]))))
                    assert np.allclose(full, p[j], atol=1e-13, rtol=1e-10)
                    hidden = dict(r); hidden['seq'] = list(r['seq']); hidden['seq'][slot] = 'REPLACED_HIDDEN'
                    assert np.array_equal(rebuilt.distribution(r, slot), rebuilt.distribution(hidden, slot))
                for r, slot, j in queries:
                    hidden = dict(r); hidden['seq'] = list(r['seq']); hidden['seq'][slot] = 'REPLACED_HIDDEN'
                    assert np.array_equal(p[j], rebuilt.distribution(hidden, slot))
                result['classical'].append({'label': info['label'], 'all_queries_reproduced': len(p),
                    'independent_complete_queries': len(indices), 'max_probability_difference': maximum,
                    'hidden_invariance_queries': len(p), 'graph_exclusion': detail})
    if not args.classical_only:
        for fold in range(5):
            _, test, _, _ = c.outer(fold)
            for added in [False, True]:
                for family in ['gru', 'transformer', 'metadata']:
                    e = read_json(OWN / args.run / f'{family}-f{fold}-extra{int(added)}-selection.json')
                    done = set()
                    for objective in ['loss', 'top1']:
                        info = e['outer'][objective]
                        if info['label'] in done:
                            continue
                        done.add(info['label'])
                        for seed in [20261006, 20261007, 20261008]:
                            prefix = info['label'] + f'-s{seed}'
                            checkpoint = torch.load(RAW / args.run / (prefix + '-weights.pt'), map_location=DEVICE, weights_only=False)
                            encoder = checkpoint['encoder']
                            model = MaskedNet(encoder, **checkpoint['config']).to(DEVICE)
                            model.load_state_dict(checkpoint['state_dict'])
                            q = predict_net(model, encoder.dataset(test))
                            p, signs = read_prob(RAW / args.run / (prefix + '.npz'))
                            assert signs == encoder.signs and np.array_equal(q, p)
                            # Check every encoded query input independently of its target tensor.
                            # Identical forward inputs imply identical masked predictions.
                            checked_inputs = 0
                            if seed == 20261006:
                                for original in test:
                                    a = encoder.dataset([original])
                                    for slot in range(len(original['seq'])):
                                        hidden = dict(original); hidden['seq'] = list(original['seq']); hidden['seq'][slot] = 'REPLACED_HIDDEN'
                                        b = encoder.dataset([hidden])
                                        assert all(torch.equal(a[k][slot], b[k][slot]) for k in [0, 1, 3, 4])
                                        checked_inputs += 1
                            r = test[0]
                            for slot in [0, len(r['seq']) // 2, len(r['seq']) - 1]:
                                hidden = dict(r); hidden['seq'] = list(r['seq']); hidden['seq'][slot] = 'REPLACED_HIDDEN'
                                a = predict_net(model, encoder.dataset([r]))
                                b = predict_net(model, encoder.dataset([hidden]))
                                assert np.array_equal(a[slot], b[slot])
                            result['neural'].append({'label': prefix, 'all_probabilities_reproduced': len(p),
                                'hidden_invariance_prediction_slots': 3, 'all_hidden_query_inputs_checked': checked_inputs})
                            del model
        for fold in range(5):
            for added in [False, True]:
                entry = read_json(OWN / args.run / f'ensemble-f{fold}-extra{int(added)}-selection.json')
                classical = read_json(OWN / args.run / f'classical-f{fold}-extra{int(added)}-selection.json')
                checked = set()
                for objective in ['loss', 'top1']:
                    info = entry['outer'][objective]
                    if info['label'] in checked:
                        continue
                    checked.add(info['label'])
                    neural = read_json(OWN / args.run / f'{info["neural_family"]}-f{fold}-extra{int(added)}-selection.json')
                    a, signs = read_prob(ROOT / classical['outer']['loss']['probability_file'])
                    b, other_signs = read_prob(ROOT / neural['outer']['loss']['probability_file'])
                    p, stored_signs = read_prob(ROOT / info['probability_file'])
                    assert signs == other_signs == stored_signs
                    weight = info['ngram_weight']
                    independent = a.clip(1e-300) ** weight * b.clip(1e-300) ** (1 - weight)
                    independent /= independent.sum(axis=1, keepdims=True)
                    change = float(np.max(np.abs(p - independent)))
                    assert np.allclose(p, independent, atol=1e-12, rtol=1e-12)
                    assert digest(ROOT / info['probability_file']) == info['probability_sha256']
                    result['ensemble'].append({'label': info['label'], 'query_rows': len(p),
                        'maximum_independent_probability_difference': change,
                        'stored_hash_passed': True})
        # Check final aggregate hashes, query keys and primary selection from saved inner grids.
        for path in sorted((OWN / args.run).glob('*-selection.json')):
            e = read_json(path)
            assert e['selected']['loss'] == min(range(len(e['inner'])), key=lambda j: (e['inner'][j]['bucket_loss_bits'], j))
            assert e['selected']['top1'] == min(range(len(e['inner'])), key=lambda j: (-e['inner'][j]['top1'], j))
            result['integrity'].append(path.name)
    save(OWN / args.output, result)
    print(json.dumps({'classical_records': len(result['classical']), 'neural_records': len(result['neural']), 'verified': True}))

if __name__ == '__main__':
    main()
