"""Exercise real astronomy, CSV parsing, scoring and comparison with synthetic towns."""
from pathlib import Path
import sys,csv,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from score_frozen import score
from compare import compare_settlements
from predict import predict,validation_gate
from horizon import TOWNS

if __name__=='__main__':
    output=OUT/'integration-analysis-v1.json'
    fixture=OUT/'synthetic/settlements-v1.csv'
    if output.exists() or fixture.exists():raise FileExistsError(output)
    validation_gate()
    fixture.parent.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,(slug,(lat,lon)) in enumerate(TOWNS.items()):
        year=-2999+i*100
        t,_=predict('alcyone',lat,lon,year)
        rows.append(dict(slug=slug,part='synthetic whole town',role='discovery' if i<3 else 'confirmation',
             lat=lat,lon=lon,theta_deg=t,sigma_theta_deg=.3,D_year=year,sigma_D_years=100.))
    with fixture.open('x',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    sources=[OUT/'validation-v1.json',OUT/'stars-retrieved-v1.json']+list((OUT/'horizon').glob('*.json'))
    write_json(fixture.with_name(fixture.name+'.provenance.json'),'synthetic-settlement-fixture',
       dict(csv_sha256=sha(fixture),definition='Synthetic deviations set equal to our own Alcyone model, synthetic dates, 0.3deg measurement sigma and 100yr date sigma. These are not measured town bearings or layout dates.'),
       inputs=sources,codes=[__file__],synthetic=True)
    rows=read_table(fixture)
    result=score(rows)
    compared=compare_settlements(rows,rows)
    checks=dict(target_is_alcyone=result['stage1']['chosen']=='alcyone',
       target_chi2_zero=result['P3']['chi2']['target']==0,
       P0_pass=result['P0']['status']=='pass',P3_pass=result['P3']['status']=='pass',
       comparisons_agree=all(compared[k]['verdict']=='agree' for k in ('deviations','dates','astronomy')),
       power_finite=0<=result['power']['probability_P0_pass']<=1)
    write_json(output,'analysis-integration-selftest',dict(all_pass=all(checks.values()),checks=checks,
       score=result,comparison=compared),
       inputs=[fixture]+sources,codes=list(Path(__file__).parent.glob('*.py'))+list((PACKAGE/'astronomy').glob('*.py')),synthetic=True)
    print(json.dumps(dict(checks=checks,power=result['power']['probability_P0_pass'])))
    if not all(checks.values()):raise SystemExit(1)
