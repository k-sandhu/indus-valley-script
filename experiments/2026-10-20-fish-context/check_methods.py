"""Hand examples for the frozen study; no real confirmation access."""
import importlib.util
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('fishstudy',HERE/'study.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)


def main():
    checks=[]
    def check(name,value):
        checks.append({'check':name,'pass':bool(value)})
    for name in ['SEAL','SEAL:S','SEAL:R','SEAL:C','SEAL:CY']:
        check('seal subtype '+name,s.is_seal({'object_type':name}))
    for name in ['TAG','TAB:B','TAB:C','POT:T:g']:
        check('nonseal '+name,not s.is_seal({'object_type':name}))
    table=s.coding();fish=s.fish_codes(table)
    check('plain fish in family','220' in fish)
    check('plain short 7',s.stroke(table,'017',True)==('B001',7))
    check('long 2 retained separately',s.stroke(table,'032',True)==('B031',2))
    check('enclosed 7 excluded by strict rule',s.stroke(table,'048',True) is None)
    fake=[{'seq':('017','220'),'component':'a','record_id':'a','object_type':'SEAL:S'},
          {'seq':('032','220'),'component':'b','record_id':'b','object_type':'SEAL:S'},
          {'seq':('003','740'),'component':'c','record_id':'c','object_type':'SEAL:S'}]
    model={'numbers':s.learn_numbers(fake,table,fish),'order':{'codes':['220','235','240']}}
    check('two stroke families stay separate',len(s.number_events(fake,table,fish))==3)
    for family in ['B001','B031']:
        ps=[s.probability({'genre':'seal','stroke_family':family,'value':v,'item':'220'},model['numbers']) for v in s.VALUES]
        check('probabilities normalized '+family,np.allclose(np.sum(ps,axis=0),1))
    result,_,_=s.score_numbers(fake,table,fish,model)
    check('astronomy excludes tall pair',result['narrow_celestial']['plain_fish_events']==1)
    ordered=[{'seq':('220','235'),'component':str(i)} for i in range(20)]
    result,_=s.score_order(ordered,fish,model)
    check('order positive control',result['pass'] and result['positive']==20)
    reversed_rows=[{'seq':('235','220'),'component':str(i)} for i in range(20)]
    result,_=s.score_order(reversed_rows,fish,model)
    check('order negative control',not result['pass'] and result['negative']==20)
    check('binomial hand value',abs(s.sign_result({str(i):1 for i in range(5)})['p_one_sided']-1/32)<1e-12)
    check('component copy counts once',s.score_order(ordered+ordered,fish,model)[0]['components']==20)
    out={'checks':checks,'pass':all(c['pass'] for c in checks),'checks_count':len(checks)}
    s.write_json(HERE/'methods-checks-v1.json',out)
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
