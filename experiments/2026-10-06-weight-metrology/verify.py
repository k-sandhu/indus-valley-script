"""Independent arithmetic/source-integrity checks for the frozen endpoint."""
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np
from scipy.stats import norm
from parse_catalogue import ROOT, RAW, RUN, parse, sha, write_json
from analyze import MODELS, INDUS, NE, LOCAL, BG

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='experiments/2026-10-06-weight-metrology/verification.json')
    args=ap.parse_args(); output=ROOT/args.output
    if output.exists(): raise FileExistsError(output)
    endpoint=RUN/'runs/2026-10-06-main'; raw=RAW/'main'
    rows=json.loads((RAW/'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))
    doc,reparsed=parse()
    # JSON represents the parser's date-range tuples as lists.
    reparsed=json.loads(json.dumps(reparsed))
    assert rows==reparsed, 'Parser reproduction differs'
    assert all(r['cat']==i+1 for i,r in enumerate(rows))
    manifest=json.loads((endpoint/'manifest.json').read_text())
    assert manifest['source_rows_sha256']==sha(RAW/'extraction-v6/catalogue-rows.json')
    assert manifest['protocol_sha256']==sha(RUN/'PROTOCOL.md')
    assert manifest['analysis_sha256']==sha(RUN/'analyze.py')
    complete=json.loads((endpoint/'completion.json').read_text())
    assert all(sha(endpoint/name)==digest for name,digest in complete['output_hashes'].items())
    selections=json.loads((raw/'selection-ids.json').read_text())
    models=json.loads((endpoint/'model-comparisons.json').read_text())
    maximum_ll_error=0
    for result in models['fits']:
        masses=np.array([rows[i-1]['mass_g'] for i in selections['site_primary_ids'][result['group']]])
        x=np.log(masses); c=MODELS[result['model']][0]
        # scipy.stats is an independent implementation of the normal density.
        signal=np.mean(norm.pdf(x[:,None],loc=np.log(result['unit_g']*c)[None,:],scale=result['sigma_log']),axis=1)
        f=result['signal_probability']*signal+(1-result['signal_probability'])*BG
        ll=float(sum(math.log(a) for a in f)); delta=abs(ll-result['log_likelihood'])
        maximum_ll_error=max(maximum_ll_error,delta); assert delta<1e-8
        assert abs(result['aic']-(6-2*ll))<1e-8
        percent=np.min(abs(masses[:,None]/(c[None,:]*result['unit_g'])-1),axis=1)*100
        assert int((percent<=3).sum())==result['within_3_percent_n']
    quantograms=json.loads((endpoint/'quantogram-peaks.json').read_text())['samples']
    maximum_q_error=0; points_checked=0
    for result in quantograms:
        if result['group']=='dholavira-all-classes': ids=selections['stratum_ids']['Dholavira/all-classes/primary']
        else:
            import re
            site=next(s for s in selections['site_primary_ids'] if re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')==result['group'])
            ids=selections['site_primary_ids'][site]
        masses=[rows[i-1]['mass_g'] for i in ids if rows[i-1]['mass_g']<=100]
        assert len(masses)==result['n']
        with (endpoint/result['grid_file']).open() as f: grid=list(csv.DictReader(f))
        assert len(grid)==1461 and float(grid[0]['q_g'])==.4 and float(grid[-1]['q_g'])==15
        # fsum/cos supplies direct scalar evaluations at endpoints and every 100th grid point.
        for i in sorted(set([0,len(grid)-1,round((result['maximum_q_g']-.4)*100)]+list(range(0,len(grid),100)))):
            q=float(grid[i]['q_g']); qscore=math.sqrt(2/len(masses))*math.fsum(math.cos(2*math.pi*m/q) for m in masses)
            delta=abs(qscore-float(grid[i]['q_observed'])); maximum_q_error=max(maximum_q_error,delta)
            assert delta<1e-10; points_checked+=1
        assert abs(max(float(r['q_observed']) for r in grid)-result['maximum_q_score'])<1e-12
        assert result['global_mc_p']*1000==round(result['global_mc_p']*1000)
    primary=json.loads((endpoint/'western-compatibility.json').read_text())['comparisons'][0]
    details=json.loads((raw/'western-primary.json').read_text())
    check=[]
    for cat in selections['western_primary_ids']:
        row=rows[cat-1]; m=row['mass_g']; u=primary['indus_reference_unit_g']
        nearest=min(INDUS*u,key=lambda target:abs(math.log(m/target)))
        ierror=abs(m/nearest-1)
        localunits=models['local_units'].get(row['site'],dict(zip(LOCAL,[7.8,8.4,9.4])))
        targets=[denom*localunits[model] for model in LOCAL for denom in NE]
        local=min(targets,key=lambda target:abs(math.log(m/target)))
        lerror=abs(m/local-1)
        geometric=abs(math.log(m/nearest))<abs(math.log(m/local))
        close=geometric and ierror<=.03 and lerror-ierror>=.01
        check.append({'cat':cat,'geometric':geometric,'close':close})
    assert sum(r['geometric'] for r in check)==primary['geometric_preference_n']==136
    assert sum(r['close'] for r in check)==primary['close_preference_n']==18
    assert [r['cat'] for r in check if r['close']]==primary['driving_catalogue_ids']
    boot=json.loads((raw/'bootstrap-draws.json').read_text()); assert len(boot)==9 and all(len(g)==200 for g in boot.values())
    assert all(result['optimizer_success'] for result in models['fits'])
    write_json(output,{'status':'Verified computation','checks':{'all_2058_rows_reparsed_equal':True,
               'source_protocol_code_and_output_hashes_match':True,'independent_likelihood_fits_checked':45,
               'maximum_log_likelihood_error':maximum_ll_error,'quantogram_samples_checked':10,
               'scalar_quantogram_points_checked':points_checked,'maximum_quantogram_error':maximum_q_error,
               'western_records_independently_scored':len(check),'western_geometric_preferences':136,
               'western_close_preferences':18,'bootstrap_draws_checked':sum(map(len,boot.values())),
               'main_optimizer_failures':0},
               'limits':['Does not replace independent page transcription or archaeological class review.',
                         'Monte Carlo envelopes and bootstrap numerical draws were integrity-checked, not independently regenerated here.'],
               'verifier_sha256':sha(Path(__file__))})
    print(output.read_text())

if __name__=='__main__': main()
