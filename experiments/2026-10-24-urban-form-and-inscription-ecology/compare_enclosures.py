"""Exploratory arithmetic on six source-reported pairs of enclosure dimensions."""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import math

P=Path(__file__).resolve().parent
SELECTED={
 'W-DHO-005': ('Dholavira, reported inner enclosure arms',0,1),
 'EAST-KALIBANGAN-002': ('Kalibangan I, early enclosure',0,1),
 'EAST-KALIBANGAN-008': ('Kalibangan II, citadel',0,1),
 'EAST-KALIBANGAN-009': ('Kalibangan II, lower city',0,1),
 'EAST-SURKOTADA-006': ('Surkotada IC, citadel interior',0,1),
 'EAST-SURKOTADA-016': ('Surkotada IC, annexe interior',0,1),
}

def main(out):
    out.mkdir()
    source=P/'run-v3/observations.json'
    observations={r['id']:r for r in json.loads(source.read_text(encoding='utf-8'))}
    rows=[]
    for oid,(label,i,j) in SELECTED.items():
        r=observations[oid]
        vals=r.get('quantity',r.get('values'))
        a,b=vals[i],vals[j]
        assert r['unit']=='m' and a>0 and b>0
        ratio=max(a,b)/min(a,b)
        independent=float(max(Fraction(str(a)),Fraction(str(b)))/min(Fraction(str(a)),Fraction(str(b))))
        assert math.isclose(ratio,independent,rel_tol=1e-14)
        rows.append(dict(observation_id=oid,label=label,town=r['town'],phase=r['phase'],dimensions_m=[a,b],
                         longer_to_shorter_ratio=ratio,independent_fraction_ratio=independent,
                         ratio_uncertainty=None,missing_uncertainty_reason='Source supplies no dimension error model; printed precision is not a standard error',
                         source_id=r['source_id'],locator=r['locator'],original_scope=r.get('denominator',r.get('count_or_measurement_scope')),
                         source_uncertainty=r.get('uncertainty'),
                         scope='Ratio of two published arm or interior dimensions, not a measured whole-town shape or evidence of an intentional canonical module'))
    result=dict(status_class='exploratory',synthetic=False,source_measurements_new=0,derived_dimension_pairs=len(rows),towns=3,
                rows=rows,passed=True,
                selection='Six named enclosure-arm/interior records with explicit paired metre lengths; Kalibangan lower-city gap excluded; no apsidal rectangle area computed',
                independent_unit='Architectural part within a town and phase; six rows are not six independent towns',
                input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:r[k] for k in ['observation_id','longer_to_shorter_ratio']} for r in rows],indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    main(parser.parse_args().out)
