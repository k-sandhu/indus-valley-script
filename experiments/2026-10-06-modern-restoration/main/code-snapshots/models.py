"""Finite-vocabulary modified Kneser–Ney and masked-slot neural models."""
import os
import json
import math
import random
import time
from collections import Counter, defaultdict
from functools import lru_cache
import numpy as np
from data import UNKNOWN, SEED, RAW, probability_stats
import torch
from torch import nn
from torch.nn import functional as F

torch.set_num_threads(4)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
SEEDS = [SEED, SEED + 1, SEED + 2]
NGRAM_GRID = [{'order': k, 'discount_scale': d} for k in [2, 3, 4, 5] for d in [0.75, 1.0]]
NEURAL_GRID = {
    'gru': [{'family': 'gru', 'width': 64, 'layers': 1}, {'family': 'gru', 'width': 128, 'layers': 2}],
    'transformer': [{'family': 'transformer', 'width': 64, 'layers': 2}, {'family': 'transformer', 'width': 128, 'layers': 2}]}

class MKN:
    def __init__(self, rows, order=2, discount_scale=1.0):
        self.order, self.scale = order, discount_scale
        self.signs = sorted({s for r in rows for s in r['seq']}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        self.n = len(self.signs)
        self.end, self.start = self.n, self.n + 1
        raw = [Counter() for _ in range(order + 1)]
        for r in rows:
            sequence = [self.start] * (order - 1) + [self.index[s] for s in r['seq']] + [self.end]
            for pos in range(order - 1, len(sequence)):
                for k in range(1, order + 1):
                    raw[k][tuple(sequence[pos - k + 1:pos + 1])] += 1
        self.counts = [Counter() for _ in range(order + 1)]
        self.counts[order] = raw[order]
        for k in range(1, order):
            # Each distinct (k+1)-gram contributes one distinct left context.
            for gram in raw[k + 1]:
                self.counts[k][gram[1:]] += 1
        bottom = np.full(self.n + 1, .5, dtype=np.float64)
        for (token,), count in self.counts[1].items():
            bottom[token] += count
        self.bottom = bottom / bottom.sum()
        self.discounts, self.rows, self.patterns = {}, {}, {}
        for k in range(2, order + 1):
            coc = Counter(self.counts[k].values())
            n1, n2, n3, n4 = [coc[j] for j in [1, 2, 3, 4]]
            y = n1 / (n1 + 2 * n2) if n1 + 2 * n2 else .5
            estimates = [1 - 2*y*n2/n1 if n1 else .5,
                2 - 3*y*n3/n2 if n2 else 1.0,
                3 - 4*y*n4/n3 if n3 else 1.5]
            ds = np.array([np.clip(d * discount_scale, .05, j - .05) for j, d in enumerate(estimates, 1)])
            self.discounts[k] = {'count_of_counts': dict(coc), 'discounts': ds.tolist()}
            counts = defaultdict(Counter)
            for gram, count in self.counts[k].items():
                counts[gram[:-1]][gram[-1]] = count
            self.rows[k] = {}
            self.patterns[k] = [defaultdict(list) for _ in range(k - 1)]
            for hist, values in counts.items():
                total = sum(values.values())
                sparse = {token: (count - ds[min(count, 3) - 1]) / total for token, count in values.items()}
                gamma = sum(ds[min(count, 3) - 1] for count in values.values()) / total
                self.rows[k][hist] = (sparse, gamma)
                for pos in range(k - 1):
                    key = hist[:pos] + hist[pos + 1:]
                    self.patterns[k][pos][key].append((hist[pos], sparse, gamma))
        self._vector_cache = {}

    def vector(self, hist):
        hist = tuple(hist[-(self.order - 1):])
        if not hist:
            return self.bottom
        if hist in self._vector_cache:
            return self._vector_cache[hist]
        low = self.vector(hist[1:])
        sparse_row = self.rows[len(hist) + 1].get(hist)
        if sparse_row is None:
            return low
        sparse, gamma = sparse_row
        p = gamma * low.copy()
        for token, value in sparse.items():
            p[token] += value
        self._vector_cache[hist] = p
        return p

    def wildcard(self, hist, pos, target):
        """Probability of fixed target for every substituted history state."""
        if not hist:
            return np.full(self.n, self.bottom[target])
        if pos == 0:
            p = np.full(self.n, self.vector(hist[1:])[target])
        else:
            p = self.wildcard(hist[1:], pos - 1, target)
        key = tuple(hist[:pos] + hist[pos + 1:])
        for candidate, sparse, gamma in self.patterns[len(hist) + 1][pos].get(key, []):
            if candidate < self.n:
                p[candidate] = sparse.get(target, 0.) + gamma * p[candidate]
        return p

    def distribution(self, row, slot):
        seq = [self.index.get(s, self.index[UNKNOWN]) for s in row['seq']] + [self.end]
        padded = [self.start] * (self.order - 1) + seq
        offset = self.order - 1
        score = self.vector(tuple(padded[slot:slot + offset]))[:self.n].copy()
        for j in range(slot + 1, min(len(seq), slot + self.order)):
            hist = padded[j:j + offset]
            pos = slot + offset - j
            score *= self.wildcard(hist, pos, seq[j])
        return score / score.sum()

    def predict(self, rows):
        return np.array([self.distribution(r, i) for r in rows for i in range(len(r['seq']))])

    def likelihood(self, sequence):
        padded = [self.start] * (self.order - 1) + [self.index.get(s, self.index[UNKNOWN]) for s in sequence] + [self.end]
        value = 1.
        for j in range(self.order - 1, len(padded)):
            value *= self.vector(tuple(padded[j - self.order + 1:j]))[padded[j]]
        return value

META = ['object_type', 'site', 'region', 'symbol']
def category(row, field):
    value = row.get(field, row.get('metadata', {}).get(field))
    return str(value) if value not in [None, '', '-', '--'] else '__MISSING__'

class Encoder:
    def __init__(self, rows):
        self.signs = sorted({s for r in rows for s in r['seq']}) + [UNKNOWN]
        self.index = {s: i for i, s in enumerate(self.signs)}
        self.mask = len(self.signs)
        self.pad = self.mask + 1
        self.meta = [{v: i + 1 for i, v in enumerate(sorted({category(r, f) for r in rows}))} for f in META]
        self.maxlen = max(len(r['seq']) for r in rows)

    def dataset(self, rows):
        width = max(len(r['seq']) for r in rows)
        x, pos, targets, meta, lengths = [], [], [], [], []
        for r in rows:
            tokens = [self.index.get(s, self.index[UNKNOWN]) for s in r['seq']]
            m = [self.meta[j].get(category(r, f), 0) for j, f in enumerate(META)]
            for i, target in enumerate(tokens):
                masked = tokens.copy()
                masked[i] = self.mask
                masked += [self.pad] * (width - len(tokens))
                x.append(masked); pos.append(i); targets.append(target); meta.append(m); lengths.append(len(tokens))
        return tuple(torch.tensor(a, dtype=torch.long, device=DEVICE) for a in [x, pos, targets, meta, lengths])

class MaskedNet(nn.Module):
    def __init__(self, encoder, family, width, layers, metadata=False):
        super().__init__()
        self.family, self.metadata = family, metadata
        self.pad = encoder.pad
        self.embed = nn.Embedding(len(encoder.signs) + 2, width, padding_idx=self.pad)
        self.dropout = nn.Dropout(.35)
        if family == 'gru':
            self.context = nn.GRU(width, width, layers, batch_first=True,
                bidirectional=True, dropout=.35 if layers > 1 else 0.)
            representation = 2 * width
        else:
            # Reserve positions for the export's longest record and validation lengths.
            self.position = nn.Embedding(128, width)
            layer = nn.TransformerEncoderLayer(width, 4, 2 * width, .35,
                batch_first=True, norm_first=True, activation='gelu')
            self.context = nn.TransformerEncoder(layer, layers, enable_nested_tensor=False)
            representation = width
        if metadata:
            self.categories = nn.ModuleList([nn.Embedding(len(v) + 1, 8) for v in encoder.meta])
            representation += 32
        self.norm = nn.LayerNorm(representation)
        self.output = nn.Linear(representation, len(encoder.signs))

    def forward(self, x, pos, meta, lengths):
        h = self.embed(x)
        if self.family == 'gru':
            # Packed sequences prevent right-padding from changing the backward context.
            packed = nn.utils.rnn.pack_padded_sequence(self.dropout(h), lengths.cpu(), batch_first=True, enforce_sorted=False)
            h, _ = self.context(packed)
            h, _ = nn.utils.rnn.pad_packed_sequence(h, batch_first=True, total_length=x.shape[1])
        else:
            assert x.shape[1] <= self.position.num_embeddings
            h = h + self.position(torch.arange(x.shape[1], device=x.device))[None]
            h = self.context(self.dropout(h), src_key_padding_mask=x == self.pad)
        h = h[torch.arange(len(x), device=x.device), pos]
        if self.metadata:
            h = torch.cat([h] + [e(meta[:, i]) for i, e in enumerate(self.categories)], dim=1)
        return self.output(self.dropout(self.norm(h)))

@torch.no_grad()
def predict_net(model, dataset, batch=1024):
    model.eval()
    x, pos, _, meta, lengths = dataset
    parts = []
    for start in range(0, len(x), batch):
        end = start + batch
        parts.append(F.softmax(model(x[start:end], pos[start:end], meta[start:end], lengths[start:end]), dim=-1).cpu().numpy())
    return np.concatenate(parts).astype(np.float64)

def fit_net(rows, validation, config, seed, epochs=None, checkpoint=None):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    encoder = Encoder(rows)
    model = MaskedNet(encoder, **config).to(DEVICE)
    train = encoder.dataset(rows)
    val = encoder.dataset(validation) if validation else None
    optimizer = torch.optim.AdamW(model.parameters(), lr=.002, weight_decay=.01)
    best_loss, best_epoch, state, history = float('inf'), 0, None, []
    started = time.perf_counter()
    # Regularization and early stopping are fixed in PROTOCOL.md.
    for epoch in range(1, (epochs if epochs is not None else 45) + 1):
        model.train()
        order = torch.randperm(len(train[0]), device=DEVICE)
        total, n = 0., 0
        for start in range(0, len(order), 1024):
            ix = order[start:start + 1024]
            x, pos, targets, meta, lengths = [a[ix] for a in train]
            optimizer.zero_grad(set_to_none=True)
            logits = model(x, pos, meta, lengths)
            loss = F.cross_entropy(logits, targets, label_smoothing=.05)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.)
            optimizer.step()
            total += loss.item() * len(ix); n += len(ix)
        record = {'epoch': epoch, 'train_smoothed_bits': total / n / math.log(2)}
        if val is not None:
            probs = predict_net(model, val)
            targets = val[2].cpu().numpy()
            loss = float(-np.log2(probs[np.arange(len(targets)), targets].clip(1e-300)).mean())
            record['validation_bucket_bits'] = loss
            if loss < best_loss - .001:
                best_loss, best_epoch = loss, epoch
                state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            history.append(record)
            if epoch - best_epoch >= 6:
                break
        else:
            history.append(record)
            best_epoch = epoch
    if state is not None:
        model.load_state_dict(state)
    if checkpoint:
        torch.save({'state_dict': {k: v.detach().cpu() for k, v in model.state_dict().items()},
            'encoder': encoder, 'config': config, 'seed': seed, 'epochs': best_epoch}, checkpoint)
    predictions = predict_net(model, val) if val is not None else None
    info = {'seed': seed, 'epochs': best_epoch, 'history': history,
        'seconds': time.perf_counter() - started, 'parameters': sum(p.numel() for p in model.parameters()),
        'training_texts': len(rows), 'training_tokens': len(train[0]), 'vocabulary': len(encoder.signs)}
    return model, encoder, predictions, info

def self_test():
    rows = [{'seq': tuple(s)} for s in ['ABC', 'ABC', 'ACB', 'BAC', 'CAC', 'BBB', 'CAB']]
    query = {'seq': tuple('ABC')}
    checks = {}
    for config in NGRAM_GRID:
        m = MKN(rows, **config)
        for slot in range(3):
            brute = []
            for candidate in m.signs:
                s = list(query['seq']); s[slot] = candidate
                brute.append(m.likelihood(s))
            brute = np.array(brute) / sum(brute)
            p = m.distribution(query, slot)
            assert np.allclose(p, brute, atol=1e-14, rtol=1e-11), (config, slot, p, brute)
            hidden = list(query['seq']); hidden[slot] = 'HIDDEN'
            assert np.array_equal(p, m.distribution({'seq': hidden}, slot))
        # Independent continuation definition and all observed row normalizations.
        for k in range(1, config['order']):
            grams = set()
            for r in rows:
                s = ['BOS'] * (config['order'] - 1) + list(r['seq']) + ['EOS']
                for j in range(config['order'] - 1, len(s)):
                    grams.add(tuple(s[j - k:j + 1]))
            ref = Counter(g[1:] for g in grams)
            for gram, value in m.counts[k].items():
                decoded = tuple('BOS' if i == m.start else 'EOS' if i == m.end else m.signs[i] for i in gram)
                assert ref[decoded] == value
        assert all(abs(m.vector(h).sum() - 1.) < 1e-12 for table in m.rows.values() for h in table)
        checks[f'mkn_{config}'] = {'brute_force_slots': 3, 'hidden_independence': True, 'continuation_counts': True, 'rows_normalized': True}
    for family in NEURAL_GRID:
        for metadata in [False, True]:
            config = {**NEURAL_GRID[family][0], 'metadata': metadata}
            torch.manual_seed(SEED)
            e = Encoder(rows); m = MaskedNet(e, **config).to(DEVICE).eval()
            a = e.dataset([query]); b = e.dataset([{'seq': tuple('AXC')}])
            p = predict_net(m, a); q = predict_net(m, b)
            assert np.array_equal(p[1], q[1])
            long = {'seq': tuple('ABCCBAC')}
            padded = predict_net(m, e.dataset([query, long]))[:3]
            assert np.allclose(p, padded, atol=1e-7, rtol=2e-6)
            assert np.allclose(p.sum(axis=1), 1, atol=2e-7)
            checks[f'{family}_metadata_{metadata}'] = {'hidden_independence': True, 'padding_invariance': True, 'normalized': True}
    return {'status': 'Verified computation', 'checks': checks, 'torch': torch.__version__,
        'device': torch.cuda.get_device_name() if DEVICE == 'cuda' else DEVICE}

if __name__ == '__main__':
    from data import save, OWN
    save(OWN / 'self-tests.json', self_test())
    print('Self-tests passed')
