"""Declared Pirak/Perumbalai sensitivity; every scenario is Exploratory."""
import argparse, copy, csv, json
from pathlib import Path
import analyze_coverage as cov

OWN=Path(__file__).resolve().parent
KEYS=['assemblages','phase_or_historical_AB','high_moderate_calendar_AB','grade_A']
def gaps(rows):
    bins=[cov.cover(rows,lo,lo+100)for lo in range(-3500,-200,100)]
    return {k:cov.empty_runs(bins,k)for k in KEYS}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',default=str(OWN/'inputs-05'));ap.add_argument('--output',required=True);a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Use a fresh directory.')
    inputs=Path(a.inputs);rows=json.loads((inputs/'evidence-table.json').read_text(encoding='utf-8'))['rows']
    scenarios=[]
    # An envelope is substituted for the two-object parent only in scenarios.
    # It supplies one assemblage, never two date intervals for the same objects.
    for lo in [-1500,-1400,-1300,-1200]:
        for hi in [-1100,-1000,-900,-800,-760]:
            for pg,ps in [('C','low'),('B','moderate')]:
                for per_strength in ['low','moderate']:
                    rr=copy.deepcopy(rows)
                    for r in rr:
                        if r['id'] in ['pirak-II','pirak-IIIA']:r['include_in_additive_coverage']=False
                        if r['id']=='pirak':
                            r['include_in_additive_coverage']=True
                            r['dating_assessments']=[dict(start_year=lo,end_year=hi,grade=pg,calendar_strength=ps,selected_for_coverage=True)]
                        if r['id']=='perumbalai':
                            for d in r['dating_assessments']:
                                if d['selected_for_coverage']:d['calendar_strength']=per_strength
                    g=gaps(rr)
                    scenarios.append(dict(id=f'pirak-{abs(lo)}-{abs(hi)}-{pg}-{ps}-perumbalai-{per_strength}',
                        status='Exploratory',pirak_interval=[lo,hi],pirak_grade=pg,pirak_strength=ps,
                        perumbalai_strength=per_strength,gaps=g))
    # Dependence checks use omission, not selective promotion of the other low-grade contexts.
    leave=[]
    for ids in [['pirak','pirak-II','pirak-IIIA'],['perumbalai'],['daimabad-V'],['thulukkarpatti-I'],['inamgaon'],['sivagalai-II']]:
        leave.append(dict(omitted_ids=ids,gaps=gaps([r for r in rows if r['id']not in ids])))
    ranges={}
    for k in KEYS:
        lengths=[s['gaps'][k]['longest_internal']['years']if s['gaps'][k]['longest_internal']else 0 for s in scenarios]
        ranges[k]=dict(min_years=min(lengths),max_years=max(lengths))
    out.mkdir(parents=True)
    result=dict(status='Exploratory',baseline=gaps(rows),scenario_count=len(scenarios),scenario_ranges=ranges,
        interpretation='Scenario ranges are selection/date sensitivity, not confidence intervals or an estimate of ancient absence.',
        reviewer_method_reused='review/gap_sensitivity.py gaps and row-substitution approach; no reviewer file modified.',
        scenarios=scenarios,leave_one_out=leave)
    cov.write_json(out/'gap-sensitivity.json',result)
    records=[]
    for s in scenarios:
        row={k:v for k,v in s.items()if k!='gaps'};row['pirak_interval']=json.dumps(row['pirak_interval'])
        for k in KEYS:
            g=s['gaps'][k]['longest_internal'];row[k+'_years']=g['years']if g else 0
            row[k+'_interval']=json.dumps([g['start_year'],g['end_year']])if g else ''
        records.append(row)
    with (out/'scenarios.csv').open('w',newline='',encoding='utf-8-sig')as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    print(json.dumps(dict(scenario_count=len(scenarios),ranges=ranges),indent=2))
if __name__=='__main__':main()
