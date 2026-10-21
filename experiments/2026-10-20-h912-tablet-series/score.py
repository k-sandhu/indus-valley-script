"""Frozen graphic prediction and explicit literal/quota equivalence check."""
from collections import Counter, defaultdict
from fractions import Fraction
import argparse
import json
import math
from pathlib import Path
import sys
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from bench.common import read_rows, write_json, read_json, sha256, envelope
RAW = ROOT/'data/raw/2026-10-20-h912-tablet-series'
DOMAIN = list(range(1, 25))
ALPHA = .05 / 2


def primary(rows):
    return [e for e in rows if e['harappa_tablet'] and e['v_code'] == '700' and e['strict_stroke']]


def unique_prototypes(rows):
    # A whole recorded carrier, with its faces exchangeable. Keep its component.
    seen, out = set(), []
    for e in sorted(rows, key=lambda e: e['record_id']):
        key = json.dumps([e['object_type'], e['prototype'], e['seq']], sort_keys=True)
        if key not in seen:
            seen.add(key); out.append(e)
    return out


def fit(rows):
    rows = unique_prototypes(primary(rows))
    counts = Counter(e['value'] for e in rows if not e['fish'])
    pooled = {str(n): float(Fraction(2*counts[n]+1, 2*sum(counts.values())+len(DOMAIN))) for n in DOMAIN}
    fitted = {}
    for stroke in ('B001', 'B031'):
        c = Counter(e['value'] for e in rows if not e['fish'] and e['stroke'] == stroke)
        fitted[stroke] = {str(n): (c[n]+2*pooled[str(n)])/(sum(c.values())+2) for n in DOMAIN}
    return {'domain': DOMAIN, 'nonfish_counts': dict(counts), 'pooled': pooled,
            'stroke_conditioned': fitted, 'reference_pseudo_observations': 2,
            'fixed_four': {str(n): .9 if n == 4 else .1/23 for n in DOMAIN},
            'construction': 'Equal weight per whole-carrier prototype; no held-out fitting.'}


def summarize(values):
    pos = sum(v > 1e-12 for v in values)
    neg = sum(v < -1e-12 for v in values)
    p = float(binomtest(pos,pos+neg,.5,alternative='greater').pvalue) if pos+neg else None
    mean = sum(values)/len(values) if values else None
    loo = min((sum(values)-v)/(len(values)-1) for v in values) if len(values)>1 else None
    return {'components':len(values),'positive':pos,'negative':neg,'ties':len(values)-pos-neg,
            'mean_bits':mean,'minimum_loo_mean_bits':loo,'p_one_sided':p,
            'pass':bool(pos+neg>=8 and p<=ALPHA and mean>0 and loo>0)}


def evaluate(rows, model):
    target = unique_prototypes([e for e in primary(rows) if e['fish']])
    comparisons = {}
    details = {}
    for name in ('pooled','stroke_conditioned','fixed_quota'):
        by = defaultdict(list)
        for e in target:
            n = str(e['value'])
            literal = model['fixed_four'][n]
            q = model['fixed_four'][n] if name=='fixed_quota' else (
                model['pooled'][n] if name=='pooled' else model['stroke_conditioned'][e['stroke']][n])
            by[e['component']].append(math.log2(literal/q))
        vals = {k:sum(v)/len(v) for k,v in by.items()}
        comparisons[name] = summarize(list(vals.values()))
        details[name] = vals
    objects = {e['object_family_id'] for e in primary(rows) if e['fish']}
    return {'target_events':len(target),'target_objects_before_prototype_collapse':len(objects),
            'target_components':len({e['component'] for e in target}),
            'values':dict(Counter(e['value'] for e in target)),
            'orders':dict(Counter('n-V-fish' if e['v_position']==1 else 'n-fish-V' for e in target)),
            'comparisons':comparisons,
            'literal_quota_maximum_probability_difference':0.0,
            'equivalence':'Literal four-vessel contents and a four-unit entitlement assign the same graphic-event probabilities. Their distinguishing observations are physical delivery/content/use relations, absent from these score inputs.',
            'direct_associations_in_transcription_score_inputs':0,
            'physical_prediction_status':'Not evaluable from transcription: source associations are audited separately.',
            'functional_credence_rule':'0.35 remains when no physically anchored prediction can be evaluated; a structural pass alone adds at most 0.05.'}, details


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('action',choices=['fit','confirm'])
    args=ap.parse_args()
    if args.action=='fit':
        rows=read_rows(RAW/'discovery-v1/events.jsonl')
        model=fit(rows)
        write_json(HERE/'discovery-v1/model.json',model)
        result,details=evaluate(rows,model)
        write_json(HERE/'discovery-v1/scoring-diagnostics.json',result)
        print(json.dumps(result,indent=2))
    else:
        rows=read_rows(RAW/'confirmation-v1/events.jsonl')
        result,details=evaluate(rows,read_json(HERE/'discovery-v1/model.json'))
        write_json(HERE/'confirmation-v1/comparison.json',envelope('h912-tablet-series',result,
             paths=[Path(__file__),HERE/'analyze.py',HERE/'PREDICTIONS.json',HERE/'discovery-v1/model.json']))
        write_json(RAW/'confirmation-v1/score-details.json',details)
        print(json.dumps(result,indent=2))


if __name__=='__main__':main()
