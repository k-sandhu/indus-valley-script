"""Independent full-record likelihood check of second-order restoration."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'experiments/2026-10-02-six-hour/markov-order2'
sys.path.insert(0, str(ROOT/'src/six_hour'))
import markov_baseline as baseline


class Direct:
    def __init__(self, records, alpha):
        self.signs = sorted({v for r in records for v in r['seq']})+[baseline.UNKNOWN]
        self.index = {v: i for i, v in enumerate(self.signs)}
        self.n = len(self.signs); self.begin = self.n+1; self.alpha = alpha
        uni = Counter(); start = Counter(); edges = Counter(); triples = Counter(); contexts = Counter()
        for record in records:
            values = [self.index[v] for v in record['seq']]
            uni.update(values); start[values[0]] += 1
            edges.update(zip(values, values[1:]+[self.n]))
            chain = [self.begin, self.begin]+values+[self.n]
            triples.update(zip(chain, chain[1:], chain[2:]))
            contexts.update(zip(chain[:-2], chain[1:-1]))
        units = np.array([uni[i]+.5 for i in range(self.n)])
        initial_prior = units/units.sum()
        dest = np.r_[units, len(records)+.5]; dest /= dest.sum()
        self.first = (np.array([start[i] for i in range(self.n)])+20*initial_prior)/(len(records)+20)
        self.trans = np.zeros((self.n, self.n+1))
        for i in range(self.n):
            row = np.array([edges[i,j] for j in range(self.n+1)])
            self.trans[i] = (row+20*dest)/(row.sum()+20)
        self.triples, self.contexts = triples, contexts
        self.uni, self.starts, self.edges = uni, start, edges
        self.tokens, self.record_count = sum(uni.values()), len(records)

    def exact_factor(self, a, b, target):
        if b == self.begin:
            if target == self.n:
                prior = Fraction(0)
            else:
                unigram = Fraction(2*self.uni[target]+1, 2*self.tokens+self.n)
                prior = (self.starts[target]+20*unigram)/(self.record_count+20)
        else:
            destination = Fraction(2*(self.record_count if target == self.n else self.uni[target])+1,
                                   2*self.tokens+self.n+2*self.record_count+1)
            prior = (self.edges[b,target]+20*destination)/(self.uni[b]+20)
        return prior if self.alpha is None else (self.triples[a,b,target]+self.alpha*prior)/(self.contexts[a,b]+self.alpha)

    def exact_likelihood(self, record, slot, candidate):
        values = [self.index.get(v,self.index[baseline.UNKNOWN]) for v in record['seq']]
        values[slot] = self.index[candidate]
        chain = [self.begin,self.begin]+values+[self.n]
        value = Fraction(1)
        for a,b,target in zip(chain,chain[1:],chain[2:]):
            value *= self.exact_factor(a,b,target)
        return value

    def factor(self, a, b, target):
        a, b, target = np.broadcast_arrays(a, b, target)
        prior = np.empty(a.shape)
        starts = b == self.begin
        if np.any(starts):
            prior[starts] = np.r_[self.first, 0.][target[starts]]
        if np.any(~starts):
            prior[~starts] = self.trans[b[~starts], target[~starts]]
        if self.alpha is None:
            return prior
        count = np.array([self.triples[int(x),int(y),int(z)] for x,y,z in zip(a.flat,b.flat,target.flat)]).reshape(a.shape)
        total = np.array([self.contexts[int(x),int(y)] for x,y in zip(a.flat,b.flat)]).reshape(a.shape)
        return (count+self.alpha*prior)/(total+self.alpha)

    def distribution(self, record, slot):
        values = [self.index.get(v, self.index[baseline.UNKNOWN]) for v in record['seq']]
        chain = [self.begin, self.begin]+values+[self.n]
        candidates = np.arange(self.n)
        masked = slot+2
        masses = np.ones(self.n)
        for j in range(2, len(chain)):
            a = candidates if j-2 == masked else np.array(chain[j-2])
            b = candidates if j-1 == masked else np.array(chain[j-1])
            target = candidates if j == masked else np.array(chain[j])
            masses *= self.factor(a,b,target)
        return masses/masses.sum()


def main(args):
    out = ROOT/args.output
    if out.exists():
        raise RuntimeError('Fresh review endpoint required.')
    out.mkdir()
    try:
        main_path = ROOT/args.input
        result = json.loads((main_path/'results.json').read_text(encoding='utf-8'))
        saved = baseline.read_jsonl(main_path/'markov2_slot_audit.jsonl')
        records, _ = baseline.load_records(ROOT/'data/normalized/lipi_clean_rtl_singleline.jsonl', min_length=3, unique=True)
        groups = baseline.group_records(records)
        assignments, loads = baseline.make_folds(records, groups, 5, 20261006)
        record_lookup = {r['record_id']: r for r in records}
        queries = {(r['record_id'],r['slot']): r for r in saved}
        max_loss_error = max_mass_error = 0.; checked = 0; all_ranks = all_fields = True
        tie_witnesses = []; mismatched_queries = set()
        for fold in result['folds']:
            number = fold['fold']
            train = [r for i,r in enumerate(records) if assignments[i] != number]
            test = [r for i,r in enumerate(records) if assignments[i] == number]
            model = Direct(train, fold['chosen_alpha'])
            for record in test:
                for slot, actual in enumerate(record['seq']):
                    row = queries[record['record_id'],slot]
                    p = model.distribution(record,slot)
                    ordered = np.argsort(-p,kind='stable')
                    predicted = [model.signs[i] for i in ordered]
                    for rank in range(10):
                        reported = row['suggestions'][rank]['code']
                        if reported != predicted[rank]:
                            first = model.exact_likelihood(record,slot,reported)
                            second = model.exact_likelihood(record,slot,predicted[rank])
                            equal = first == second
                            all_ranks &= equal
                            mismatched_queries.add((record['record_id'],slot))
                            tie_witnesses.append({'record_id':record['record_id'],'slot':slot,'rank':rank,
                                'saved_code':reported,'direct_code':predicted[rank],
                                'exact_likelihood_equal':equal,'likelihood':str(first),
                                'direct_other_likelihood':str(second)})
                    actual_index = model.index.get(actual,model.index[baseline.UNKNOWN])
                    loss = -np.log2(p[actual_index])
                    max_loss_error = max(max_loss_error,abs(loss-row['bucket_loss_bits']))
                    max_mass_error = max(max_mass_error,abs(p[ordered[0]]-row['model_top_mass']),
                        max(abs(p[ordered[i]]-row['suggestions'][i]['model_mass']) for i in range(10)))
                    all_fields &= row['actual'] == actual and row['fold'] == number and row['length'] == len(record['seq'])
                    all_fields &= row['top1'] == (predicted[0] == actual)
                    all_fields &= row['top5'] == (actual in predicted[:5]) and row['top10'] == (actual in predicted[:10])
                    changed = dict(record); changed['seq'] = list(record['seq']); changed['seq'][slot] = 'HIDDEN_REPLACEMENT'
                    assert np.array_equal(p,model.distribution(changed,slot))
                    checked += 1
            print(json.dumps({'fold_reviewed':number,'queries':checked}),flush=True)
        summary = baseline.summarize(saved)
        checks = {'8009_unique_queries':len(saved)==len(queries)==checked==8009,
            '1596_strings_1526_components':len(records)==1596 and len(groups)==1526,
            'full_likelihood_rankings_match_up_to_exact_rational_ties':bool(all_ranks),'target_query_outcomes_match':bool(all_fields),
            'all_target_losses_match':bool(max_loss_error<1e-10),'all_saved_candidate_masses_match':bool(max_mass_error<1e-12),
            'every_hidden_target_replacement_invariant':True,
            'saved_aggregate_reproduced':summary==result['models']['Markov2'],
            'code_hash_matches':baseline.digest(main_path/'code_snapshot.py')==result['source_sha256'],
            'protocol_hash_matches':baseline.digest(main_path.parent/'PROTOCOL.md')==result['protocol_sha256']}
        assert all(checks.values()),checks
        (out/'verification.json').write_text(json.dumps({'created_utc':datetime.now(timezone.utc).isoformat(),
            'checks':checks,'max_loss_error_bits':float(max_loss_error),'max_mass_error':float(max_mass_error),
            'float_rank_disagreement_queries':len(mismatched_queries),'exact_tied_rank_witnesses':len(tie_witnesses),
            'method':'Independent flat triple/edge counts and full-record candidate likelihood'},indent=2)+'\n',encoding='utf-8')
        (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
        (out/'tie_slot_audit.jsonl').write_text('\n'.join(json.dumps(r) for r in tie_witnesses)+'\n',encoding='utf-8')
        print(json.dumps({'checks_passed':len(checks),'queries':checked,'max_loss_error':max_loss_error}))
    except Exception as error:
        (out/'failure.json').write_text(json.dumps({'type':type(error).__name__,'message':str(error)},indent=2)+'\n',encoding='utf-8')
        (out/'failed_code_snapshot.py').write_bytes(Path(__file__).read_bytes())
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',default='experiments/2026-10-02-six-hour/markov-order2/review-ties')
    parser.add_argument('--input',default='experiments/2026-10-02-six-hour/markov-order2/main')
    main(parser.parse_args())
