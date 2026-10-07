"""Independent scalar checks, current parser reproduction and frozen integrity."""
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from scipy.stats import norm
from parse_catalogue import ROOT, RAW, RUN, parse, sha, write_json
import analyze as a

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',default='experiments/2026-10-06-weight-metrology/runs/2026-10-07-review-response-v4')
    ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/review-response-verification.json');args=ap.parse_args()
    out=ROOT/args.output
    if out.exists():raise FileExistsError(out)
    run=ROOT/args.run;manifest=json.loads((run/'manifest.json').read_text());completion=json.loads((run/'completion.json').read_text())
    assert all(sha(run/name)==h for name,h in completion['output_hashes'].items())
    assert manifest['protocol_sha256']==sha(RUN/'PROTOCOL.md')
    assert all(sha(RUN/name)==h for name,h in manifest['code_hashes'].items())
    rowpath=ROOT/manifest['rows_path'];assert sha(rowpath)==manifest['rows_sha256'];raw=rowpath.parent
    rows=json.loads(rowpath.read_text(encoding='utf8'));doc,reparsed=parse();assert rows==json.loads(json.dumps(reparsed));doc.close()
    frozen=json.loads((RUN/'history/2026-10-07-before-review-response/frozen-hashes.json').read_text())
    assert all(sha(RUN/'runs/2026-10-06-main'/name)==h for name,h in frozen.items())
    sel=json.loads((raw/'selection-ids.json').read_text());sitefits=json.loads((run/'model-comparisons.json').read_text())['fits']
    strata=json.loads((run/'stratified-estimates.json').read_text())['fits'];bands=json.loads((run/'mass-band-estimates.json').read_text())['fits']
    llmax=0;checked=0
    for f,ids in [(f,sel['sites'][f['group']]) for f in sitefits]+[(f,sel['strata'][f['group']]) for f in strata]+[(f,sel['strata']['Dholavira/band/'+f['group']]) for f in bands]:
        x=np.log([rows[i-1]['mass_g'] for i in ids]);c=a.MODELS[f['model']][0]
        signal=norm.pdf(x[:,None],loc=np.log(c*f['unit_g'])[None,:],scale=f['sigma_log']).mean(axis=1)
        ll=float(np.log(f['signal_probability']*signal+(1-f['signal_probability'])*a.BG).sum());delta=abs(ll-f['log_likelihood']);llmax=max(llmax,delta)
        assert delta<1e-8;assert abs(f['aic']-(2*f.get('parameter_count',3)-2*ll))<1e-8;checked+=1
    tests=json.loads((run/'dholavira-model-tests.json').read_text());x=np.log([rows[i-1]['mass_g'] for i in sel['sites']['Dholavira']]);c=a.INDUS
    for f in tests['alternative_models']:
        v=f['parameters']
        if f['model']=='two-unit':
            u1,u2,s1,s2,w,p=v
            signal=w*norm.pdf(x[:,None],loc=np.log(u1*c),scale=s1).mean(axis=1)+(1-w)*norm.pdf(x[:,None],loc=np.log(u2*c),scale=s2).mean(axis=1)
        else:
            u,s,extra,p=v;targets=u*c
            if f['model']=='absolute-error':means=np.log(targets);sd=np.sqrt(s*s+(extra/targets)**2)
            else:means=np.log(targets+extra*(targets<5));sd=s
            signal=norm.pdf(x[:,None],loc=means,scale=sd).mean(axis=1)
        ll=float(np.log(p*signal+(1-p)*a.BG).sum());assert abs(ll-f['log_likelihood'])<1e-8
        assert abs(f['aic']-(2*f['parameter_count']-2*ll))<1e-8;checked+=1
    quant=json.loads((run/'quantogram-peaks.json').read_text())['samples'];points=0;qmax=0
    for f in quant:
        if f['group']=='dholavira-all-classes':ids=sel['strata']['Dholavira/all-classes/primary']
        elif f['group'] in ('1-3-to-5','5-to-100'):ids=sel['strata']['Dholavira/band/'+('1.3-to-5' if f['group']=='1-3-to-5' else f['group'])]
        else:ids=next(ids for name,ids in sel['sites'].items() if a.re_slug(name)==f['group'])
        masses=[rows[i-1]['mass_g'] for i in ids if rows[i-1]['mass_g']<=100]
        grid=list(csv.DictReader((run/f['grid_file']).open()));assert len(grid)==1461;assert len(masses)==f['n'];assert f['seed']==20261007
        for ix in sorted(set([0,1460,round((f['maximum_q_g']-.4)*100)]+list(range(0,1461,100)))):
            q=float(grid[ix]['q_g']);score=math.sqrt(2/len(masses))*math.fsum(math.cos(2*math.pi*m/q) for m in masses)
            delta=abs(score-float(grid[ix]['q_observed']));assert delta<1e-10;qmax=max(qmax,delta);points+=1
    western=json.loads((run/'western-compatibility.json').read_text())['comparisons'];westchecked=0
    for f in western:
        ds=json.loads((raw/f'western-{f["frame"]}.json').read_text());g=k=0
        local=[u*c for u in f['canonical_local_units_g'] for c in f['local_levels']]
        for d in ds:
            m=rows[d['cat']-1]['mass_g'];it=min(a.INDUS*f['indus_reference_unit_g'],key=lambda t:abs(math.log(m/t)))
            lt=min(local,key=lambda t:abs(math.log(m/t)));ie=abs(m/it-1);le=abs(m/lt-1)
            geo=abs(math.log(m/it))<abs(math.log(m/lt));close=geo and ie<=f['close_threshold'] and le-ie>=.01
            assert geo==d['geometric_preference'] and close==d['close_preference'];g+=geo;k+=close;westchecked+=1
        assert g==f['geometric_preference_n'] and k==f['close_preference_n']
    nulls=json.loads((run/'western-chance-baselines.json').read_text());draws=json.loads((raw/'western-null-counts.json').read_text())
    for f in nulls['nulls']:
        values=np.array(draws[f['null']][f['frame']]);assert len(values)==f['draws'];assert values[:,1].mean()==f['close_mean']
        assert values[:,0].mean()==f['geometric_mean'];assert (values[:,1]>=f['observed_close_n']).mean()==f['fraction_ge_observed_close']
    book=json.loads((raw/'ascalone-dholavira-heavier-list.json').read_text())['rows'];assert len(book)==len({r['cat'] for r in book})==95
    assert 220 not in [r['cat'] for r in json.loads((run/'western-screen-objects.json').read_text())['objects']]
    write_json(out,{'status':'Verified computation','run_status':'Exploratory','run':args.run,'checks':{'parser_rows_reproduced':2058,'frozen_files_unchanged':len(frozen),
      'likelihoods_independently_evaluated':checked,'maximum_likelihood_error':llmax,'quantogram_groups':len(quant),'scalar_quantogram_points':points,'maximum_cosine_error':qmax,
      'western_scores_independently_checked':westchecked,'null_summary_frames_checked':len(nulls['nulls']),'book_list_unique_n':95},
      'limits':['Checks arithmetic and source integrity, not historical attribution or causal error mechanism.','Stored bootstrap and Monte Carlo draws/envelopes checked; full rerun command is in README.']})
    print(out.read_text())

if __name__=='__main__':main()
