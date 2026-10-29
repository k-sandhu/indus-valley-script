"""Compare every definite reading flag with the chart impact and explain unions."""
import argparse
from collections import Counter
import json
from pathlib import Path
import pyarrow.parquet as pq
from build_release import HERE,P,ROOT,dump,read
from chart_changes import ChartChanges,cell_key

def locations(unit,field):
    values=unit.get(field) or []
    return {cell_key(x) for v in values.values() for x in (v if isinstance(v,list) else [v])} if isinstance(values,dict) else {cell_key(x) for x in values}

def main():
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    impact=read(P/'impact-v2.1.json');comparison=read(P/'comparison-v2.1.json')
    changes=ChartChanges(read(ROOT/'research/chart_reference/manual_numeric_reference.json'),read(P/'chart-reference-v2.1.json'),comparison,impact)
    groups={(x['benchmark'],x['reader'],x['kind']):x for x in impact['public_readings']}
    totals=Counter();bad=[];extra=[];v3=Counter();definite=[]
    for config in ['benchmark_readings','benchmark_readings_v3']:
        for row in pq.read_table(a.release/'data'/(config+'.parquet')).to_pylist():
            key=(row['benchmark'],row['reader'],row['kind']);reference=json.loads(row['reading_json']);flags=json.loads(row['chart_correction_flags_json']);group=groups.get(key)
            for i,(unit,flag) in enumerate(zip(reference['units'],flags)):
                index=unit.get('unit_index',i);sample=row['sample_index'];base=dict(benchmark=key[0],reader=key[1],kind=key[2],sample_index=sample,unit_index=index)
                derived,potential=changes.candidate_changes(unit)
                expected=sorted({x['field'] for x in group['unit_changes'] if x['sample_index']==sample and x['unit_index']==index}) if group else derived
                if flag['candidate_fields_would_change']!=expected:bad.append(dict(**base,expected=expected,actual=flag['candidate_fields_would_change']))
                if flag['candidate_fields_would_change']:
                    definite.append(dict(**base,fields=flag['candidate_fields_would_change']))
                    if row['kind']!='adjudicated':totals['/'.join(key)]+=1
                if row['benchmark']=='v3':v3[row['kind']]+=bool(flag['candidate_fields_would_change'])
                if key==('v2','B','independent'):
                    strict=locations(unit,'chart_locations') if 'chart_locations' in unit else locations(unit,'chart_references')
                    strict_changed=strict.intersection(changes.changes)
                    totals['v2/B/strict_cells']+=bool(strict_changed);totals['v2/B/union_cells']+=flag['corrected_cell']
                    totals['v2/B/strict_class']+=any('rank' in changes.changes[c] for c in strict_changed)
                    totals['v2/B/union_class']+=any('rank' in fields for fields in flag['changed_fields'].values())
                    if flag['corrected_cell'] and not strict_changed:extra.append(dict(**base,shape_only_cells=sorted(locations(unit,'shape_only_chart_locations').intersection(changes.changes)),additional_class=any('rank' in fields for fields in flag['changed_fields'].values())))
    expected_counts={'v1/A/primary':6,'v1/B/primary':5,'v2/A/independent':15,'v2/B/strict_cells':12,'v2/B/union_cells':20,'v2/B/strict_class':6,'v2/B/union_class':7}
    for key,value in expected_counts.items():
        if totals[key]!=value:bad.append(dict(group=key,expected=value,actual=totals[key]))
    if len(extra)!=8 or any(not x['shape_only_cells'] for x in extra):bad.append(dict(extra_shape_only_units=len(extra)))
    output=dict(status='Verified computation' if not bad else 'Failed',definite_independent_units_compared_with_impact=sum(totals[k] for k in ['v1/A/primary','v1/B/primary','v2/A/independent']),group_counts=dict(totals),v3_definite_units=dict(v3),definite_units=definite,v2_reader_b_additional_shape_only_units=extra,mismatches=bad,rule='corrected_cell uses all three location fields; candidate-field changes use field-specific locations intersected with original membership, matching the chart impact rule.')
    dump(a.out,output);print(json.dumps({k:output[k] for k in ['status','definite_independent_units_compared_with_impact','group_counts','v3_definite_units']}))
    if bad:raise SystemExit(1)

if __name__=='__main__':main()
