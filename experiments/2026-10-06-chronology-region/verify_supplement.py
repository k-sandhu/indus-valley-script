"""Check post-outcome aggregates against the frozen endpoint and local witnesses."""
import argparse,collections,json,hashlib,sys
from pathlib import Path
sys.dont_write_bytecode=True
import pandas as pd
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[1];RAW=ROOT/'data/raw/2026-10-06-chronology-region'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--main',default='main-2026-10-07-v1');p.add_argument('--supplement',default='exploratory-2026-10-07-v1');p.add_argument('--output',default='verification-supplement-2026-10-07-v1.json');a=p.parse_args()
    target=OWN/a.output;assert not target.exists();s=OWN/a.supplement;m=OWN/a.main
    completion=json.loads((s/'completion.json').read_text());assert completion['code_sha256']==sha(OWN/'supplement.py') and completion['amendment_sha256']==sha(OWN/'AMENDMENT-2026-10-07.md')
    comparisons=0;intervals=0
    for theme in ['time','region']:
        baseline={r['comparison']:r for r in json.loads((m/(theme+'_comparisons.json')).read_text())}
        for r in json.loads((s/(theme+'_intervals.json')).read_text()):
            if 'type_adjusted' not in r:continue
            for mode in ['type_adjusted','site_type_adjusted']:
                if mode not in r:continue
                for key,value in r[mode].items():
                    assert value['effect']==baseline[r['comparison']][mode][key]['effect']
                    if value['effect'] is not None:assert value['valid_bootstraps']==499;intervals+=1
                comparisons+=1
    base={r['region']:r for r in json.loads((m/'regional_models.json').read_text())};models=0
    for r in json.loads((s/'model_intervals.json').read_text()):
        for k,v in r['losses'].items():
            assert abs(v['mean']-base[r['region']]['adjusted']['losses'][k]['mean'])<1e-12
            assert v['valid_bootstraps']==499;models+=1
    coverage=pd.read_csv(s/'external_coverage.csv');assert coverage.faces.sum()==42 and coverage.known_tokens.sum()==149 and coverage.unreadable_tokens.sum()==19 and coverage.clear_faces.sum()==16
    members=json.loads((RAW/a.main/'record_membership.json').read_text());member={r['record_id']:r for r in members};raw=[json.loads(x) for x in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text().splitlines()]
    totals=collections.defaultdict(lambda:collections.Counter())
    for r in raw:
        info=member[r['record_id']];totals[info['fold']]['faces']+=1;totals[info['fold']]['observed_slots']+=len(r['signs_reading_rtl'])
        if info['clear']:totals[info['fold']]['clear_faces']+=1;totals[info['fold']]['clear_tokens']+=len(r['signs_reading_rtl'])
    for r in json.loads((s/'actual_fold_counts.json').read_text()):
        assert all(r[k]==totals[r['fold']][k] for k in ['faces','observed_slots','clear_faces','clear_tokens'])
    presence=pd.read_csv(s/'presence_by_type.csv',dtype={'sign':str})
    sampled=presence.iloc[::max(1,len(presence)//40)];presence_checks=0
    for item in sampled.to_dict('records'):
        rs=[r for r in raw if r['site']=='Harappa' and member[r['record_id']]['type']==item['type'] and member[r['record_id']]['periods']==[item['period']] and any(x!='000' for x in r['signs_reading_rtl'])]
        n=len({member[r['record_id']]['physical'] for r in rs});k=len({member[r['record_id']]['physical'] for r in rs if item['sign'] in r['signs_reading_rtl']})
        assert n==item['components'] and k==item['components_bearing'];presence_checks+=1
    result={'status':'Verified computation of Exploratory supplement','effect_groups_unchanged':comparisons,'supported_metric_intervals_with_499_replicates':intervals,'model_point_estimates_unchanged':models,'external_coverage_accounting':'passed','actual_fold_counts_independently_rebuilt':'passed','sampled_type_presence_counts_independently_rebuilt':presence_checks,'limitation':'Bootstrap draws/coverage calibration are not independently verified by this checker.','sha256':{p.name:sha(p) for p in s.iterdir() if p.is_file()}}
    target.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
if __name__=='__main__':main()
