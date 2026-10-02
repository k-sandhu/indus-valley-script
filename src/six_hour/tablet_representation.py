"""Partition frozen tablet display observations under declared transformations."""
from datetime import datetime,timezone
import hashlib
from itertools import product
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'experiments/2026-10-02-six-hour/harappa-object-frame/display-summary/results.json'
BASE=ROOT/'experiments/2026-10-02-six-hour/tablet-representation'

def exchange(state):
    form,middle,bottom=state
    return (1-form,bottom,middle)

def end_reverse(state):
    form,middle,bottom=state
    return (form,1-middle,1-bottom)

def independent_middle_reverse(state):
    form,middle,bottom=state
    return (form,1-middle,bottom)

def independent_bottom_reverse(state):
    form,middle,bottom=state
    return (form,middle,1-bottom)

def orbit(state,generators):
    reached={state};pending=[state]
    while pending:
        current=pending.pop()
        for transform in generators:
            changed=transform(current)
            if changed not in reached:
                reached.add(changed);pending.append(changed)
    return tuple(sorted(reached))

def main():
    out=BASE/'main'
    if out.exists():
        raise RuntimeError('Fresh endpoint required.')
    source=json.loads(INPUT.read_text(encoding='utf-8'))
    states=list(product(range(2),repeat=3))
    generators={'fixed_display':[],'unordered_lower_faces':[exchange],
        'unordered_with_common_reversal':[exchange,end_reverse],
        'unordered_with_independent_reversals':[exchange,independent_middle_reverse,independent_bottom_reverse]}
    observed={}
    objects=[]
    for pattern in source['patterns']:
        state=(0 if pattern['middle_form']=='A' else 1,0 if pattern['middle_position']=='left' else 1,0 if pattern['bottom_position']=='left' else 1)
        observed[state]=pattern['count']
        for obj in pattern['source_objects']:
            a,d=(state[1],state[2]) if state[0]==0 else (state[2],state[1])
            objects.append({**obj,'display_state':list(state),'A_position':'left' if a==0 else 'right',
                'D_position':'left' if d==0 else 'right','same_displayed_side':a==d})
    packages=[]
    for name,transforms in generators.items():
        partitions=sorted({orbit(state,transforms) for state in states})
        groups=[]
        for members in partitions:
            belonging=[obj for obj in objects if tuple(obj['display_state']) in members]
            groups.append({'display_states':[list(s) for s in members],'objects':len(belonging),'target_ids':[obj['target_id'] for obj in belonging]})
        assert len({state for group in partitions for state in group})==8
        assert sum(len(group) for group in partitions)==8
        assert sum(g['objects'] for g in groups)==19
        packages.append({'representation':name,'possible_classes':len(partitions),'groups':groups})
    same=sum(o['same_displayed_side'] for o in objects);different=len(objects)-same
    missing=source['unresolved_object_pairs'];total=len(objects)+missing
    checks={'all_eight_display_classes_observed':len(observed)==8,
        'all_19_resolved_objects_once':len(objects)==19 and len({o['target_id'] for o in objects})==19,
        'three_unresolved_retained':missing==3,
        'all_generators_involutions':all(t(t(s))==s for transforms in generators.values() for t in transforms for s in states),
        'common_reverse_commutes_with_face_exchange':all(exchange(end_reverse(s))==end_reverse(exchange(s)) for s in states),
        'independent_classification_matches_common_reverse_orbits':sorted(g['objects'] for g in packages[2]['groups'])==sorted([same,different]),
        'class_counts_8_4_2_1':[p['possible_classes'] for p in packages]==[8,4,2,1]}
    assert all(checks.values())
    result={'experiment_id':'ARCH-03','created_utc':datetime.now(timezone.utc).isoformat(),'status':'conditional-representation-audit',
        'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((BASE/'PROTOCOL.md').read_bytes()).hexdigest(),
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'packages':packages,'resolved_objects':objects,
        'missing_observation_bounds':{'total':total,'unresolved':missing,'same_displayed_side':{'observed':same,'possible_total':[same,same+missing]},
            'opposite_displayed_side':{'observed':different,'possible_total':[different,different+missing]}},'checks':checks}
    out.mkdir();(out/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (out/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'checks_passed':len(checks),'class_counts':[p['possible_classes'] for p in packages],'same':same,'opposite':different}))

if __name__=='__main__':
    main()
