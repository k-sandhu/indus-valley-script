"""Reconstruct preserved masks and exclude connected additional faces."""
import os
import sys
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-06-modern-restoration'
RAW.mkdir(parents=True, exist_ok=True)
for key in ['TMP', 'TEMP', 'MPLCONFIGDIR']:
    os.environ[key] = str(RAW / 'tmp')
(RAW / 'tmp').mkdir(exist_ok=True)
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'src/six_hour'))
import markov_baseline as old

SEED = 20261006
UNKNOWN = old.UNKNOWN

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f'Frozen endpoint exists: {path}')
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')

class Corpus:
    def __init__(self):
        source = ROOT / 'data/normalized/lipi_clean_rtl_singleline.jsonl'
        benchmark = json.loads((ROOT / 'results/restoration/benchmark.json').read_text(encoding='utf-8'))
        assert digest(source) == benchmark['input_sha256']
        assert digest(ROOT / 'src/methods/conditional_structure.py') == benchmark['model_dependency_sha256']
        self.rows, exclusions = old.load_records(source, min_length=3, unique=True)
        self.groups = old.group_records(self.rows)
        self.assignment, loads = old.make_folds(self.rows, self.groups, 5, SEED)
        pm = old.read_jsonl(ROOT / 'results/restoration/baseline_slot_audit.jsonl')
        pmb = old.read_jsonl(ROOT / 'results/restoration/local_slot_audit.jsonl')
        self.lookup, correspondence = old.verify_saved(self.rows, self.groups, self.assignment, loads, benchmark, pm, pmb)
        self.references = {}
        for name, location in [
            ('Markov1', 'experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl'),
            ('Markov2', 'experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl')]:
            values = old.read_jsonl(ROOT / location)
            assert len(values) == len(pm)
            for a, b in zip(pm, values):
                assert all(a[k] == b[k] for k in ['record_id', 'slot', 'actual', 'length', 'artifact', 'group', 'fold'])
            self.references[name] = values
        self.keys = [(x['record_id'], x['slot']) for x in pm]
        self.keyindex = {k: i for i, k in enumerate(self.keys)}
        self.template = [{k: x[k] for k in ['record_id', 'slot', 'actual', 'length', 'artifact', 'group', 'fold', 'position']} for x in pm]
        self.frequencies = Counter(x['actual'] for x in pm)
        observed = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
        self.raw = old.read_jsonl(observed)
        # Union all faces, including unusable ones: a damaged face can link objects.
        allrows = []
        for raw in self.raw:
            r = dict(raw)
            r['seq'] = tuple(map(str, r.get('signs_reading_rtl', [])))
            r['artifact'] = str(r.get('object_family_id', r.get('artifact_id', r['record_id'])))
            r['artifact_aliases'] = list(map(str, r.get('artifact_aliases', [r['artifact']])))
            if r['artifact'] not in r['artifact_aliases']:
                r['artifact_aliases'].append(r['artifact'])
            allrows.append(r)
        allrows += self.rows
        parent = list(range(len(allrows)))
        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        def join(i, j):
            a, b = find(i), find(j)
            parent[max(a, b)] = min(a, b)
        aliases, sequences = {}, {}
        for i, r in enumerate(allrows):
            for a in r['artifact_aliases']:
                if a in aliases:
                    join(i, aliases[a])
                else:
                    aliases[a] = i
            if r['seq']:
                if r['seq'] in sequences:
                    join(i, sequences[r['seq']])
                else:
                    sequences[r['seq']] = i
        self.face_roots = [find(i) for i in range(len(self.raw))]
        self.record_roots = {r['record_id']: find(len(self.raw) + i) for i, r in enumerate(self.rows)}
        self.candidates = []
        excluded = Counter()
        benchmark_strings = {r['seq'] for r in self.rows}
        for i, r in enumerate(allrows[:len(self.raw)]):
            seq = r['seq']
            if not seq:
                excluded['empty'] += 1
            elif r.get('complete_observed') is not True or r.get('has_blank_space') or r.get('has_unknown_sign') or any(s in {'000', '999', 'P000', '?', UNKNOWN} for s in seq):
                excluded['incomplete_or_unknown'] += 1
            elif r.get('max_damage', 0) or r.get('max_uncertainty', 0):
                excluded['damage_or_uncertainty'] += 1
            elif seq in benchmark_strings:
                excluded['benchmark_string'] += 1
            else:
                r['full_root'] = self.face_roots[i]
                self.candidates.append(r)
        connected = defaultdict(set)
        for r in self.rows:
            connected[self.record_roots[r['record_id']]].add(self.lookup[r['record_id']])
        bridges = [v for v in connected.values() if len(v) > 1]
        self.audit = {
            'status': 'Verified computation', 'correspondence': correspondence,
            'additional_saved_models_checked': list(self.references), 'benchmark_exclusions': exclusions,
            'input_sha256': digest(source), 'observed_sha256': digest(observed),
            'saved_prediction_sha256': {name: digest(ROOT / p) for name, p in [
                ('Markov1', 'experiments/2026-10-02-six-hour/markov-baseline/main/markov_slot_audit.jsonl'),
                ('Markov2', 'experiments/2026-10-02-six-hour/markov-order2/main/markov2_slot_audit.jsonl')]},
            'observed_faces': len(self.raw), 'extra_candidate_faces': len(self.candidates),
            'extra_candidate_tokens': sum(len(r['seq']) for r in self.candidates),
            'candidate_exclusions': dict(excluded), 'full_graph_bridged_benchmark_sets': len(bridges),
            'full_graph_bridged_benchmark_components': sum(map(len, bridges)),
            'full_graph_max_benchmark_components': max(map(len, connected.values())),
            'outer_extra': []}
        for f in range(5):
            _, _, _, detail = self.outer(f)
            self.audit['outer_extra'].append(detail)

    def extra(self, held):
        forbidden = {self.record_roots[r['record_id']] for r in held}
        retained = [r for r in self.candidates if r['full_root'] not in forbidden]
        chosen = {}
        for r in sorted(retained, key=lambda x: str(x['record_id'])):
            chosen.setdefault(r['seq'], r)
        extra = list(chosen.values())
        assert not {r['full_root'] for r in extra} & forbidden
        return extra, {'candidate_faces': len(self.candidates),
            'excluded_connected_faces': len(self.candidates) - len(retained),
            'retained_faces': len(retained), 'retained_face_tokens': sum(len(r['seq']) for r in retained),
            'added_texts': len(extra), 'added_tokens': sum(len(r['seq']) for r in extra),
            'added_short_texts': sum(len(r['seq']) < 3 for r in extra),
            'added_multiline_texts': sum(r.get('single_line') is False for r in extra),
            'added_directions': dict(Counter(r.get('direction', 'MISSING') for r in extra)),
            'remaining_connected_to_held': 0}

    def outer(self, fold):
        train = [r for i, r in enumerate(self.rows) if self.assignment[i] != fold]
        test = [r for i, r in enumerate(self.rows) if self.assignment[i] == fold]
        extra, detail = self.extra(test)
        return train, test, extra, {'fold': fold, **detail}

    def inner(self, fold):
        train, test, _, _ = self.outer(fold)
        groups = old.group_records(train)
        assign, _ = old.make_folds(train, groups, 3, SEED + fold)
        for k in range(3):
            fit = [r for i, r in enumerate(train) if assign[i] != k]
            val = [r for i, r in enumerate(train) if assign[i] == k]
            extra, detail = self.extra(test + val)
            assert not {self.lookup[r['record_id']] for r in fit} & {self.lookup[r['record_id']] for r in val + test}
            yield fit, val, extra, {'outer_fold': fold, 'inner_fold': k, **detail}

    def scores(self, rows, probs, signs):
        index = {s: i for i, s in enumerate(signs)}
        unknown = index[UNKNOWN]
        scores = []
        j = 0
        for r in rows:
            for slot, actual in enumerate(r['seq']):
                p = probs[j]
                assert np.all(np.isfinite(p)) and abs(float(p.sum()) - 1) < 2e-6
                rank = np.argsort(-p, kind='stable')
                s = dict(self.template[self.keyindex[r['record_id'], slot]])
                s.update({f'top{k}': bool(actual in [signs[t] for t in rank[:k]]) for k in [1, 5, 10]})
                s.update(known_in_training=actual in index, model_top_mass=float(p[rank[0]]),
                    top_is_unknown=signs[rank[0]] == UNKNOWN,
                    bucket_loss_bits=-float(np.log2(max(float(p[index.get(actual, unknown)]), 1e-300))),
                    suggestions=[{'code': signs[t], 'model_mass': float(p[t])} for t in rank[:10]])
                scores.append(s)
                j += 1
        assert j == len(probs)
        return scores

def probability_stats(rows, probs, signs):
    index = {s: i for i, s in enumerate(signs)}
    actual = [s for r in rows for s in r['seq']]
    targets = np.array([index.get(s, index[UNKNOWN]) for s in actual])
    order = np.argsort(-probs, axis=1, kind='stable')
    correct = np.array([signs[j] == s for j, s in zip(order[:, 0], actual)])
    return {'slots': len(actual), 'top1': float(correct.mean()),
        'bucket_loss_bits': float(-np.log2(probs[np.arange(len(actual)), targets].clip(1e-300)).mean())}

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--output', default=str(OWN / 'benchmark-audit.json'))
    args = p.parse_args()
    c = Corpus()
    save(args.output, c.audit)
    print(json.dumps(c.audit, indent=2))
