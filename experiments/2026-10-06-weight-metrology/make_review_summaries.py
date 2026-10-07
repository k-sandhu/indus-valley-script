"""Build aggregate-only review tables without rewriting any endpoint."""
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
import analyze as a
from parse_catalogue import ROOT, RUN, sha, write_json

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='experiments/2026-10-06-weight-metrology/runs/2026-10-07-review-response-v4')
    ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/summary-tables-review-response');args=ap.parse_args()
    out=ROOT/args.output;run=ROOT/args.run
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    def read(name):return json.loads((run/name).read_text(encoding='utf8'))
    counts=read('counts.json');flat=[]
    for s in counts['sites']:
        for cls,n in s['classes'].items():flat.append({'site':s['site'],'class':cls,'catalogue_n':n,'site_primary_n':s['primary_n']})
    a.write_csv(out/'counts-by-site-class.csv',flat,['site','class','catalogue_n','site_primary_n'])
    bands=read('mass-band-estimates.json')['fits'];est=[]
    for f in bands:
        row={k:f[k] for k in ['group','n','unit_g','signal_cv_percent','signal_probability','within_3_percent_n']}
        row.update(unit_ci95_low_g=f['bootstrap']['unit_ci95_g'][0],unit_ci95_high_g=f['bootstrap']['unit_ci95_g'][1]);est.append(row)
    a.write_csv(out/'mass-band-estimates.csv',est,list(est[0]))
    q=read('quantogram-peaks.json')['samples']
    a.write_csv(out/'quantogram-peaks.csv',q,['group','n','maximum_q_g','maximum_q_score','global_mc95','global_mc_p','score_at_13_65','seed'])
    nulls=read('western-chance-baselines.json')['nulls'];a.write_csv(out/'western-chance-baselines.csv',nulls,list(nulls[0]))
    comp=read('western-compatibility.json')['comparisons']
    a.write_csv(out/'western-sensitivities.csv',comp,['frame','n','indus_reference_unit_g','geometric_preference_n','close_preference_n','close_preference_fraction','close_preference_wilson95'])
    manifest=read('manifest.json');rows=json.loads((ROOT/manifest['rows_path']).read_text(encoding='utf8'))
    coverage=[]
    for site in sorted(set(r['site'] for r in rows)):
        group=[r for r in rows if r['site']==site]
        coverage.append({'site':site,'n':len(group),'area_provided_n':sum(bool(r['area']) for r in group),'level_provided_n':sum(bool(r['level']) for r in group),
                         'grid_provided_n':sum(bool(r['grids']) for r in group),'period_provided_n':sum(bool(r['period_literal']) for r in group),
                         'condition_classes':dict(Counter(r['preservation'] for r in group))})
    write_json(out/'context-coverage.json',{'status':'Exploratory','sites':coverage,'source_contextual_total_note':'Dholavira p.136 says 505 contexted objects; parser field counts are not an independently reconciled set.'})
    draws=json.loads((ROOT/manifest['rows_path']).parent.joinpath('bootstrap-draws.json').read_text())
    diff=np.array([r['unit_g'] for r in draws['1.3-to-5']])-np.array([r['unit_g'] for r in draws['5-to-100']])
    write_json(out/'band-difference.json',{'status':'Exploratory','difference_small_minus_middle_g':bands[1]['unit_g']-bands[2]['unit_g'],
              'independent_band_bootstrap_difference_ci95_g':np.quantile(diff,[.025,.975]).tolist(),'draws':len(diff),
              'interval_scope':'Independent object bootstrap draws from the disjoint recorded mass bands; conditional on models and observed-band selection.'})
    write_json(out/'manifest.json',{'status':'Exploratory','source_endpoint':args.run,'files':{f.name:sha(f) for f in out.iterdir() if f.is_file()},
               'code_sha256':sha(Path(__file__)),'raw_payloads_tracked':False})
    print(out)

if __name__=='__main__':main()
