"""Audit curated references and evaluate declared categorical/classification restrictions.

No source counts are interpreted as frequencies or confidence scores.
The supplied ledger encodes expert-readable judgements; this script checks their
consequences and integrity, not the truth of historical transmission.
"""
from pathlib import Path
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AXES = {'composition','redaction','manuscript','narrated_time','archaeological_context'}
CONTROL_SET = {'selective_local_transmission','shared_indo_iranian_inheritance','convergence',
               'genre_selection','later_reorganization_second_urbanization'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--check-witnesses',action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f'Refusing preexisting output: {args.output}')
    sources, observations, claims = [json.loads((HERE/n).read_text(encoding='utf-8'))
                                    for n in ['sources.json','observations.json','claims.json']]
    S = {s['id']:s for s in sources}; O = {o['id']:o for o in observations}
    checks = []
    def check(name, condition):
        checks.append({'check':name,'passed':bool(condition)})
        if not condition: raise ValueError(name)
    check('unique source identifiers',len(S)==len(sources))
    check('unique observation identifiers',len(O)==len(observations))
    check('unique claim identifiers',len({c['id'] for c in claims})==len(claims))
    for o in observations:
        check(o['id']+' source references',bool(o['source_ids']) and set(o['source_ids'])<=S.keys())
        check(o['id']+' five separate date axes',set(o['date_axes'])==AXES and all(o['date_axes'].values()))
        check(o['id']+' locus and scope',bool(o['locus']) and bool(o['permitted_inference_and_limit']))
    for c in claims:
        check(c['id']+' observation references',set(c['observation_ids'])<=O.keys())
        if c['kind']=='transmission_hypothesis':
            check(c['id']+' alternatives explicit',set(c['controls'])==CONTROL_SET)
            check(c['id']+' intermediate references are archaeological',all(O[i]['evidence_type']=='archaeology' for i in c['intermediate_archaeological_ids']))
    witness_count = 0
    if args.check_witnesses:
        for s in sources:
            for w in s['witnesses']:
                p=ROOT/w['path'];witness_count+=1
                check(s['id']+' witness '+p.name,p.exists() and p.stat().st_size==w['bytes'] and sha(p)==w['sha256'])
    hypotheses=[c for c in claims if c['kind']=='transmission_hypothesis']
    later={'rv_family_late_addition','rv_later_book','brahmana','buddhist'}
    family={'rv_family_unflagged'}
    policies = [
        ('all_curated',lambda o:True,False,False),
        ('exclude_late_RV_and_later_text',lambda o:o['evidence_type'] not in later,False,False),
        ('also_require_locus_specific_core_authentication',lambda o:o['evidence_type'] not in later|family,False,False),
        ('require_intermediate_archaeological_witness',lambda o:True,True,False),
        ('require_intermediate_and_cross_domain_diagnostic',lambda o:True,True,True)]
    sensitivity=[]
    for name,predicate,intermediate,diagnostic in policies:
        kept={i for i,o in O.items() if predicate(o)}
        text={i for i in kept if O[i]['evidence_type'].startswith('rv') or O[i]['evidence_type'] in {'brahmana','buddhist'}}
        eligible=[c['id'] for c in hypotheses if
                  (not intermediate or bool(set(c['intermediate_archaeological_ids']) & kept)) and
                  (not diagnostic or c['diagnostic_feature_crosses_text_archaeology'])]
        sensitivity.append(dict(policy=name,observations_retained=len(kept),textual_observations_retained=len(text),
                                represented_text_components=sorted({O[i]['component'] for i in text}),
                                candidate_hypotheses_passing_declared_requirements=eligible,
                                interpretation='Eligibility of curated hypotheses under named restrictions; not proof or probability of transmission.'))
    bounds=[]
    for oid in ['A03','A04','A05']:
        for row in O[oid]['values']['rows']:
            check(oid+' percentage sum '+row['context'],abs(sum(row[k] for k in ['wild','domesticated','immature','uncertain'])-100)<=0.02)
            bounds.append(dict(observation=oid,**row,domesticated_lower=row['domesticated'],
                               domesticated_upper=round(row['domesticated']+row['uncertain'],2)))
    early,late=bounds[:2]
    rice=dict(unit='reported percentage points, not raw independent trials',bounds=bounds,
              masudpur_VII_late_exceeds_mature_for_all_uncertain_assignments=late['domesticated_lower']>early['domesticated_upper'],
              masudpur_I_vs_bahola_order_guaranteed=bounds[3]['domesticated_lower']>bounds[2]['domesticated_upper'],
              within_site_comparison_survives_removal_of_either_Masudpur_VII_context=False,
              pgw_domestication_endpoint_available=O['A06']['values']['pgw_spikelet_contexts_retained']>0,
              limitations='Only uncertain bases are reassigned. Immature bases retain source classification; published rounding retained. No inferential confidence interval, rate of historical change or pooled chronological regression fitted.')
    check('no PGW spikelet endpoint invented',rice['pgw_domestication_endpoint_available'] is False)
    args.output.mkdir(parents=True)
    inputs={n:sha(HERE/n) for n in ['PROTOCOL.md','assemble-ledger.py','audit.py','sources.json','observations.json','claims.json']}
    out=dict(created_utc=datetime.now(timezone.utc).isoformat(),input_hashes=inputs,
             counts={'sources':len(sources),'observations':len(observations),'claims':len(claims),
                     'witnesses_verified':witness_count,'checks_passed':len(checks)},
             evidence_type_counts=dict(Counter(o['evidence_type'] for o in observations)),
             sensitivity=sensitivity,rice_classification_sensitivity=rice,checks=checks)
    (args.output/'audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out['counts']))

if __name__=='__main__':main()
