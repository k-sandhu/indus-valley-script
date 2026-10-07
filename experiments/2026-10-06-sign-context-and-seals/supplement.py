"""Exploratory descriptive coverage of all seal types and dimension missingness."""
import argparse, json, re
from collections import Counter, defaultdict
from pathlib import Path
import analyze as main

def missing_reason(value):
    if value is None or str(value).strip()=='': return 'blank'
    try:
        v=float(value)
        return 'positive' if v>0 else 'zero_placeholder' if v==0 else 'negative'
    except ValueError:
        return 'nonnumeric_range' if re.search(r'\d.*[-–].*\d',str(value)) else 'nonnumeric_other'

def run():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run',default='supplement-2026-10-07-01')
    args=ap.parse_args()
    out=main.OWN/args.run
    out.mkdir(exist_ok=False)
    rows=[json.loads(l) for l in main.INPUT.read_text(encoding='utf-8').splitlines()]
    _,_,seals,_=main.grouping(rows); result={'status':'Exploratory','input_sha256':main.sha(main.INPUT),'seal_components':len(seals),
         'scope':'All seal types; h*v is a bounding-box product, not measured area for nonrectangular seals. No new inference.',
         'dimension_missingness':{},'type_groups':[]}
    for k in ['horizontal(mm)','vertical(mm)','thickness(mm)']:
        result['dimension_missingness'][k]={}
        for pop,rr in [('all_seals',seals),('square_seals',[r for r in seals if r['object_type']=='SEAL:S'])]:
            result['dimension_missingness'][k][pop]=dict(Counter(missing_reason(r['metadata'].get(k)) for r in rr))
    for typ in sorted({r['object_type'] for r in seals}):
        rr=[r for r in seals if r['object_type']==typ]; measured=[]
        for r in rr:
            h,v=main.positive(r['metadata'].get('horizontal(mm)')),main.positive(r['metadata'].get('vertical(mm)'))
            if h and v: measured.append((r,h,v,(h*v)**.5))
        result['type_groups'].append({'object_type':typ,'objects':len(rr),'measured_both_face_dimensions':len(measured),
              'characteristic_bounding_box_size_mm':main.numeric_summary([x[3] for x in measured]),
              'horizontal_mm':main.numeric_summary([x[1] for x in measured]),'vertical_mm':main.numeric_summary([x[2] for x in measured])})
    main.write(out/'dimension-coverage.json',result)
    print('all-seal descriptive coverage written')

if __name__=='__main__': run()
