"""Post-endpoint source-led residual comparison; seven selected rounded masses."""
import argparse
import json
import math
import statistics
from pathlib import Path
from parse_catalogue import ROOT, RAW, RUN, sha, write_json
from analyze import INDUS, NE

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output', default='experiments/2026-10-06-weight-metrology/gulf-supplement.json')
    ap.add_argument('--raw-output', default='data/raw/2026-10-06-weight-metrology/gulf-supplement-scores-v3.json')
    args=ap.parse_args()
    output=ROOT/args.output; rawout=ROOT/args.raw_output
    if output.exists() or rawout.exists(): raise FileExistsError('Use new output paths')
    source=RAW/'gulf-bibby-rows.json'
    rows=json.loads(source.read_text())['rows']
    fits=json.loads((RUN/'runs/2026-10-06-main/model-comparisons.json').read_text())['fits']
    u=next(f['unit_g'] for f in fits if f['group']=='Dholavira' and f['model']=='indus_binary_decimal')
    gulf=[1/8,1,2,12.5,50,100]
    refs={'main_indus_13_65':(13.65,INDUS), 'main_indus_dholavira':(u,INDUS),
          'gulf_13_5':(13.5,gulf),'gulf_13_65':(13.65,gulf),
          'shekel_7_8':(7.8,NE),'shekel_8_4':(8.4,NE),'shekel_9_4':(9.4,NE)}
    details=[]
    for row in rows:
        result={'id':row['id'],'references':{}}
        for name,(unit,denoms) in refs.items():
            multiple=min(denoms,key=lambda d:abs(math.log(row['mass_g']/(unit*d))))
            result['references'][name]={'multiple':float(multiple),
                'absolute_log_error':abs(math.log(row['mass_g']/(unit*multiple))),
                'relative_error':abs(row['mass_g']/(unit*multiple)-1)}
        details.append(result)
    aggregates=[]
    for name,(unit,denoms) in refs.items():
        errors=[r['references'][name]['relative_error'] for r in details]
        preferred=[r['id'] for r in details if all(r['references'][name]['absolute_log_error']<
                   r['references'][local]['absolute_log_error'] for local in ['shekel_7_8','shekel_8_4','shekel_9_4'])]
        aggregates.append({'reference':name,'unit_g':unit,'n':len(rows),
                'within_2_percent_n':int(sum(e<=.02 for e in errors)),
                'within_3_percent_n':int(sum(e<=.03 for e in errors)),
                'within_5_percent_n':int(sum(e<=.05 for e in errors)),
                'median_error_percent':100*statistics.median(errors),
                'maximum_error_percent':100*max(errors),
                'smaller_residual_than_all_western_ids':preferred})
    result={'status':'Exploratory','source_rows_sha256':sha(source),
                'amendment_sha256':sha(RUN/'GULF-AMENDMENT.md'),'code_sha256':sha(Path(__file__)),
                'references':aggregates,'limitations':['Seven source-selected rounded masses; no population inference.',
                'The 50-fold Gulf level is a post-endpoint source-led addition.']}
    json.dumps(result,allow_nan=False)
    write_json(rawout,details)
    write_json(output,result)
    print(json.dumps(aggregates,indent=2))

if __name__=='__main__': main()
