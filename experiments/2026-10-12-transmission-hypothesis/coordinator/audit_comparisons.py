"""Check historical comparison joins and retain unresolved transitions.

Decisions are source-qualified scholarly judgments in the input, not scores
computed by this program. Passing checks does not authenticate an ancestry.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
ROOT=PACKAGE.parents[1]
RIVALS={'R1','R2','R3','R4','R5'}
RELATIONS={'positive_observation','compatible_only','counter_observation_under_stated_assumption','unresolved'}
STATES={'observed','attributed_inference','unresolved'}
TYPES={'material_operation','textual_operation','comparative_reconstruction','learning_relation','population_opportunity','later_reorganization'}
DECISIONS={'supported_endpoint','supported_intermediate','rival_comparison','unresolved_join','demoted_bridge'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):return json.loads(path.read_text('utf-8'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,default=HERE/'comparisons-v1.json')
    parser.add_argument('--output',type=Path,default=HERE/'run-v1');args=parser.parse_args()
    if args.output.exists():raise SystemExit('Output directory exists; no overwrite.')
    data=load(args.input);checks=[];inputs={};ledgers={};census=[]

    def check(name,condition,detail=None):checks.append({'check':name,'passed':bool(condition),'detail':detail})

    def refs(references,label):
        found=[]
        for reference in references:
            name=reference['file'];path=ROOT/name
            if name not in ledgers:
                ledger=load(path);records=ledger['observations'] if isinstance(ledger,dict) else ledger
                ids=[record.get('observation_id',record.get('id')) for record in records]
                check('Distinct observation IDs: '+name,len(ids)==len(set(ids)) and None not in ids)
                ledgers[name]=dict(zip(ids,records));inputs[name]=sha(path)
            for id in reference['ids']:
                check(label+' observation '+id,id in ledgers[name],name)
                if id in ledgers[name]:found.append((name,id))
        return found

    comparisons=data['comparisons']
    check('Distinct comparison IDs',len({row['id'] for row in comparisons})==len(comparisons))
    for row in comparisons:
        cid=row['id'];joined=refs(row['observations'],cid)
        check(cid+' decision vocabulary',row['decision'] in DECISIONS)
        check(cid+' scope and feature explicit',all(bool(row[key]) for key in ['family','feature','proposition','chronology','dependencies','conclusion']))
        rivals=row['rivals'];check(cid+' five named rivals',set(rivals)==RIVALS)
        for name,rival in rivals.items():
            check(cid+'/'+name+' relation vocabulary',rival['relation'] in RELATIONS)
            check(cid+'/'+name+' prediction and unresolved discriminator',bool(rival['prediction']) and bool(rival['missing_discriminator']))
            refs(rival['observations'],cid+'/'+name)
            if rival['relation']=='counter_observation_under_stated_assumption':
                check(cid+'/'+name+' counterclaim assumption explicit',bool(rival.get('assumption')))
        unresolved=[];opportunity=[];unsupported=[]
        for i,edge in enumerate(row['transitions']):
            label=cid+'/transition'+str(i+1)
            check(label+' type and state vocabulary',edge['type'] in TYPES and edge['state'] in STATES)
            check(label+' feature and endpoints explicit',all(bool(edge[key]) for key in ['feature','from','to']))
            support=refs(edge['observations'],label)
            if edge['state']=='unresolved':unresolved.append(i+1)
            elif not support:unsupported.append(i+1)
            if edge['state']=='attributed_inference':
                check(label+' inference premises explicit',bool(edge.get('premises')))
            if edge['type']=='population_opportunity':opportunity.append(i+1)
        # This checks declarations and references, not semantic support or exclusion.
        gate=(bool(row['transitions']) and not unresolved and not unsupported and not opportunity and
              all(edge['feature_specific'] for edge in row['transitions']) and
              bool(row.get('rival_discrimination_basis')))
        if row.get('claims_traced_local_literary_descent'):
            check(cid+' declared traced-descent claim meets stated completeness gate',gate)
        check(cid+' endpoint claim has joined support',row['decision'] not in {'supported_endpoint','supported_intermediate'} or bool(joined))
        census.append({'id':cid,'family':row['family'],'decision':row['decision'],
                       'unresolved_transition_indices':unresolved,'opportunity_only_indices':opportunity,
                       'unsupported_resolved_transition_indices':unsupported,
                       'declared_local_descent_record_completeness':gate,
                       'claims_traced_local_literary_descent':bool(row.get('claims_traced_local_literary_descent')),
                       'rival_relations':{name:rival['relation'] for name,rival in rivals.items()},
                       'scope':'Declared-reference completeness only. Historical relevance is manually reviewed.'})
    inputs[args.input.resolve().relative_to(ROOT).as_posix()]=sha(args.input)
    inputs[(HERE/'AUDIT-PROTOCOL.md').relative_to(ROOT).as_posix()]=sha(HERE/'AUDIT-PROTOCOL.md')
    inputs[(HERE/'AUDIT-AMENDMENT.md').relative_to(ROOT).as_posix()]=sha(HERE/'AUDIT-AMENDMENT.md')
    args.output.mkdir(parents=True)
    result={'created_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Existing source-ID joins, comparison schema and declared requirements. Semantic support and rival discrimination are manual scholarly judgments, not validated by this program.',
            'code_sha256':sha(Path(__file__)),'input_sha256':inputs,'comparisons':census,
            'checks_passed':sum(row['passed'] for row in checks),'checks_failed':sum(not row['passed'] for row in checks),
            'checks':checks}
    with (args.output/'audit.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'comparisons':len(census),'checks_passed':result['checks_passed'],'checks_failed':result['checks_failed']}))
    if result['checks_failed']:raise SystemExit(1)


if __name__=='__main__':main()
