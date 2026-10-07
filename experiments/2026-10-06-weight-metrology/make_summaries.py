"""Tabular derivatives of the frozen endpoint; no refitting or reselection."""
import argparse
import csv
import json
from pathlib import Path
from parse_catalogue import ROOT, RAW, RUN, sha, write_json

def table(path, rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/summary-tables')
    args=ap.parse_args(); out=ROOT/args.output
    if out.exists(): raise FileExistsError(out)
    out.mkdir(parents=True)
    endpoint=RUN/'runs/2026-10-06-main'
    models=json.loads((endpoint/'model-comparisons.json').read_text())['fits']
    unit=[]
    for r in models:
        if 'bootstrap' not in r: continue
        b=r['bootstrap']
        unit.append({'site':r['group'],'model':r['model'],'n':r['n'],'unit_g':r['unit_g'],
            'unit_ci95_lower_g':b['unit_ci95_g'][0],'unit_ci95_upper_g':b['unit_ci95_g'][1],
            'signal_cv_percent':r['signal_cv_percent'],'cv_ci95_lower_percent':b['signal_cv_ci95_percent'][0],
            'cv_ci95_upper_percent':b['signal_cv_ci95_percent'][1],'signal_probability':r['signal_probability'],
            'within_3_percent_n':r['within_3_percent_n'],'aic_minus_background':r['aic_minus_background'],
            'unit_boundary_bootstrap_n':b['unit_boundary_draws'],'sigma_boundary_bootstrap_n':b['sigma_boundary_draws']})
    table(out/'unit-estimates.csv',unit)
    counts=json.loads((endpoint/'counts.json').read_text())['sites']; countrows=[]
    for r in counts:
        for name,n in r['balance_classes'].items():
            countrows.append({'site':r['site'],'class':name,'catalogue_n_in_class':n,
                              'catalogue_n_site':r['catalogue_n'],'primary_n_site':r['primary_n']})
    table(out/'counts-by-site-class.csv',countrows)
    q=json.loads((endpoint/'quantogram-peaks.json').read_text())['samples']
    table(out/'quantogram-peaks.csv',[{k:r[k] for k in ['group','n','maximum_q_g','maximum_q_score','global_mc95','global_mc_p','score_at_13_65']} for r in q])
    w=json.loads((endpoint/'western-compatibility.json').read_text())['comparisons']; west=[]
    for r in w:
        west.append({k:r[k] for k in ['frame','n','indus_reference_unit_g','close_threshold','geometric_preference_n','geometric_preference_fraction','close_preference_n','close_preference_fraction','mixture_preference_n','geometric_mixture_disagreement_n']})
    table(out/'western-sensitivities.csv',west)
    rows=json.loads((RAW/'extraction-v6/catalogue-rows.json').read_text()); d=[r for r in rows if r['site']=='Dholavira']
    write_json(out/'context-coverage.json',{'site':'Dholavira','catalogue_n':len(d),
        'parsed_nonempty_fields':{field:sum(bool(r[field]) for r in d) for field in ['area','level','grids','period_literal']},
        'source_context_count':505,'source_location':'Ascalone 2022 printed p. 136, Table 6.2',
        'interpretation':'Parsed fields and the source archaeological-context count use different definitions; no one-to-one reconciliation was completed.'})
    write_json(out/'manifest.json',{'source_endpoint':'experiments/2026-10-06-weight-metrology/runs/2026-10-06-main',
        'source_completion_sha256':sha(endpoint/'completion.json'),'code_sha256':sha(Path(__file__)),
        'outputs':{p.name:sha(p) for p in out.iterdir() if p.is_file()}})
    print(str(out))

if __name__=='__main__': main()
