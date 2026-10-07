"""Summarise the author's 60-entry rendered-page audit and verify parser repairs."""
import argparse
import json
import math
from pathlib import Path
from parse_catalogue import ROOT, RAW, write_json, sha

ERRORS = {
    652: 'period omitted: Uruk period, Susa II (lev. 22-17), 3500-3000 BC',
    758: 'period omitted: Old-Babylonian period, 2000-1800 BC',
    892: 'date/period truncated after 2500',
    930: 'period omitted: Shahdad III.2-III.1, Late ICS, 2200-1900 BC',
    1892: 'date/period truncated after 2200',
}

def wilson(k, n):
    z = 1.959963984540054
    p = k / n; a = 1 + z*z/n
    center = (p + z*z/(2*n))/a
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/a
    return [max(0, center-half), min(1, center+half)]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--output', default='experiments/2026-10-06-weight-metrology/parser-validation-v2.json')
    ap.add_argument('--raw-output', default='data/raw/2026-10-06-weight-metrology/manual-validation-v2.json')
    args = ap.parse_args(); output = ROOT/args.output
    if output.exists(): raise FileExistsError(output)
    local = ROOT/args.raw_output
    if local.exists(): raise FileExistsError(local)
    before = {r['cat']:r for r in json.loads((RAW/'extraction-v3/catalogue-rows.json').read_text(encoding='utf-8'))}
    after = {r['cat']:r for r in json.loads((RAW/'extraction-v6/catalogue-rows.json').read_text(encoding='utf-8'))}
    frame = json.loads((RAW/'extraction-v3/validation-renders/sample-frame.json').read_text(encoding='utf-8'))
    sample = frame['sample_ids']
    assert len(sample)==60 and len(set(sample))==60 and set(ERRORS).issubset(sample)
    fields = ['site','context_literal','museum_identifiers','shape_literal','condition_literal',
              'material','dimensions_text','dimensions','mass_g','missing_mass','period_literal',
              'date_ranges_bce','marks_literal','entry_unit_attribution']
    audits = []
    for cat in sample:
        b, a = before[cat], after[cat]
        differences = [f for f in fields if a[f] != b[f]]
        assert differences == (['period_literal'] if cat in ERRORS else [])
        audits.append({'cat':cat, 'checked_by_eye':True, 'review_kind':'author source-informed rendered-PDF review',
                       'render_path':f'data/raw/2026-10-06-weight-metrology/extraction-v4/validation-renders/cat-{cat:04}.png',
                       'fields_checked':fields, 'pre_repair_error':ERRORS.get(cat),
                       'post_repair_unresolved_errors':[],
                       'before_fields':{f:b[f] for f in differences}, 'after_fields':{f:a[f] for f in differences}})
    write_json(local, {'sample_ids':sample, 'review_date':'2026-10-07', 'audits':audits,
                      'clipped_render_repair':'v3 incorrectly treated decimal dimensions as headings for seven sampled crops; v4/v5 rerendered and checked them fully',
                      'rechecked_crop_ids':[158,525,670,1055,1978,2032,2033]})
    missing = [r['cat'] for r in after.values() if r['mass_g'] is None]
    write_json(output, {'status':'Verified computation; author visual review completed; independent review pending',
                        'sample_n':60,'sampling_seed':20261006, 'sampling_frame':[1,2058],
                        'sample_ids':sample, 'field_count_per_entry':len(fields),
                        'entry_errors_before_repair':5,'entry_error_fraction_before_repair':5/60,
                        'entry_error_wilson95_before_repair':wilson(5,60),
                        'mass_or_plus_x_errors_observed':0,
                        'entry_errors_remaining_in_sample':0,'remaining_error_wilson95':wilson(0,60),
                        'error_fields':{'period_literal':5}, 'errors_catalogue_ids':sorted(ERRORS),
                        'missing_mass_catalogue_ids':missing,
                        'post_audit_systematic_repairs':['material-before-mark ordering','absent material becomes null','Ovoid good missing-comma condition'],
                        'source_rows_sha256':sha(RAW/'extraction-v6/catalogue-rows.json'),
                        'audit_path':local.relative_to(ROOT).as_posix(),'audit_sha256':sha(local),
                        'scope':'The repaired sample was rechecked. Its error rate is not an independent estimate for unreviewed entries.'})
    print(json.dumps({'sample_n':60,'errors_before':5,'errors_after':0,'missing_mass_ids':missing}))

if __name__=='__main__': main()
