"""Reviewer check 3 (template): compare headline numbers in README.md and REPORT.md with the saved outputs.

Each entry gives the number as printed in the prose, the value recomputed from the saved output file, and a tolerance
equal to half a unit in the last printed digit. Writes review/numbers-check.json. Run from the repository root:
    python -B experiments/2026-10-06-weight-metrology/review/check_numbers.py
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
P = ROOT / 'experiments/2026-10-06-weight-metrology'
RUN = P / 'runs/2026-10-06-main'

models = json.loads((RUN / 'model-comparisons.json').read_text())['fits']
strata = {s['group']: s for s in json.loads((RUN / 'stratified-estimates.json').read_text())['fits']}
west = {c['frame']: c for c in json.loads((RUN / 'western-compatibility.json').read_text())['comparisons']}
quant = {q['group']: q for q in json.loads((RUN / 'quantogram-peaks.json').read_text())['samples']}
counts = {c['site']: c for c in json.loads((RUN / 'counts.json').read_text())['sites']}
gulf = {g['reference']: g for g in json.loads((P / 'gulf-supplement.json').read_text())['references']}
val = json.loads((P / 'parser-validation-v2.json').read_text())
ext = json.loads((P / 'extraction-v6.json').read_text())
ver = json.loads((P / 'verification.json').read_text())
drv = json.loads((RUN / 'western-driving-objects.json').read_text())['objects']
ctx = json.loads((P / 'summary-tables/context-coverage.json').read_text())


def fit(group, model='indus_binary_decimal'):
    return next(f for f in models if f['group'] == group and f['model'] == model)


checks = []


def chk(label, printed, actual, tol):
    ok = abs(printed - actual) <= tol
    checks.append({'claim': label, 'printed': printed, 'recomputed': actual, 'tolerance': tol, 'result': 'confirmed' if ok else 'discrepancy'})


d = fit('Dholavira')
chk('README/REPORT Dholavira unit g', 14.003, d['unit_g'], .0005)
chk('Dholavira bootstrap lower g', 13.819, d['bootstrap']['unit_ci95_g'][0], .0005)
chk('Dholavira bootstrap upper g', 14.518, d['bootstrap']['unit_ci95_g'][1], .0005)
chk('Dholavira signal CV %', 4.32, d['signal_cv_percent'], .005)
chk('Dholavira CV lower %', 2.41, d['bootstrap']['signal_cv_ci95_percent'][0], .005)
chk('Dholavira CV upper %', 15.85, d['bootstrap']['signal_cv_ci95_percent'][1], .005)
chk('Dholavira signal probability', .562, d['signal_probability'], .0005)
chk('Dholavira n', 298, d['n'], 0)
chk('Dholavira within 3% n', 110, d['within_3_percent_n'], 0)
chk('Dholavira within 3% %', 36.91, 100 * d['within_3_percent_fraction'], .005)
chk('Dholavira all-classes n', 568, strata['Dholavira/all-classes/primary']['n'], 0)
chk('Dholavira all-classes CV %', 17.24, strata['Dholavira/all-classes/primary']['signal_cv_percent'], .005)
chk('Dholavira Indus beats binary AIC', 15.262, fit('Dholavira', 'pure_binary')['aic'] - d['aic'], .0005)
r = fit('Rakhigarhi')
chk('Rakhigarhi n', 9, r['n'], 0); chk('Rakhigarhi unit', 14.313, r['unit_g'], .0005)
chk('Rakhigarhi lower', 14.084, r['bootstrap']['unit_ci95_g'][0], .0005); chk('Rakhigarhi upper', 14.560, r['bootstrap']['unit_ci95_g'][1], .0005)
chk('Rakhigarhi CV', 1.46, r['signal_cv_percent'], .005); chk('Rakhigarhi p', .644, r['signal_probability'], .0005); chk('Rakhigarhi within3', 6, r['within_3_percent_n'], 0)
chk('Rakhigarhi AIC tie', 0.0, abs(fit('Rakhigarhi', 'pure_binary')['aic'] - r['aic']), 1e-6)
nw = fit('Nagwada')
chk('Nagwada n', 14, nw['n'], 0); chk('Nagwada unit', 13.605, nw['unit_g'], .0005)
chk('Nagwada lower', 12.500, nw['bootstrap']['unit_ci95_g'][0], .0005); chk('Nagwada upper', 14.699, nw['bootstrap']['unit_ci95_g'][1], .0005)
chk('Nagwada CV', 13.95, nw['signal_cv_percent'], .005); chk('Nagwada p', .990, nw['signal_probability'], .0005); chk('Nagwada within3', 4, nw['within_3_percent_n'], 0)
chk('Nagwada AIC difference', 0.000007, abs(fit('Nagwada', 'pure_binary')['aic'] - nw['aic']), 6e-7)
b = fit('Bagasra')
chk('Bagasra n', 11, b['n'], 0); chk('Bagasra unit', 14.941, b['unit_g'], .0005)
chk('Bagasra lower', 13.696, b['bootstrap']['unit_ci95_g'][0], .0005); chk('Bagasra upper', 15.000, b['bootstrap']['unit_ci95_g'][1], .0005)
chk('Bagasra CV', 11.30, b['signal_cv_percent'], .005); chk('Bagasra p', .990, b['signal_probability'], .0005); chk('Bagasra within3', 2, b['within_3_percent_n'], 0)
chk('Bagasra binary preferred by AIC', 1.914, b['aic'] - fit('Bagasra', 'pure_binary')['aic'], .0005)
for site, n in [('Farmana', 2), ('Shikarpur', 2), ('Kuntasi', 1), ('Nageshwar', 1)]:
    chk(f'{site} primary n', n, counts[site]['primary_n'], 0)

# strata
for lab, g, n, u, cv, w3 in [('Chert', 'Dholavira/certain/material/chert', 100, 14.031, 4.26, 49),
                             ('Other stones', 'Dholavira/certain/material/other-stones', 156, 14.363, 15.13, 38),
                             ('Non-stone', 'Dholavira/certain/material/non-stone', 42, 12.500, 20.20, 4),
                             ('Cuboid', 'Dholavira/certain/shape/Cuboid', 226, 14.069, 4.79, 79),
                             ('Biconic', 'Dholavira/certain/shape/Biconic', 54, 13.101, 17.48, 7),
                             ('Hemisphere', 'Dholavira/certain/shape/Hemisphere', 8, 12.500, 20.20, 1)]:
    s = strata[g]
    chk(f'{lab} n', n, s['n'], 0); chk(f'{lab} unit', u, s['unit_g'], .0005); chk(f'{lab} CV', cv, s['signal_cv_percent'], .005); chk(f'{lab} within3', w3, s['within_3_percent_n'], 0)
for lab, g, n, u, cv in [('Bailey', 'Dholavira/area/Bailey', 14, 13.869, .50), ('Castle', 'Dholavira/area/Castle', 60, 13.990, 3.49),
                         ('Lower Town', 'Dholavira/area/Lower Town', 29, 13.824, 1.80), ('Middle Town', 'Dholavira/area/Middle Town', 122, 14.271, 6.20)]:
    s = strata[g]
    chk(f'{lab} n', n, s['n'], 0); chk(f'{lab} unit', u, s['unit_g'], .0005); chk(f'{lab} CV', cv, s['signal_cv_percent'], .005)
chk('area unprovided CV', 16.04, strata['Dholavira/area/unprovided']['signal_cv_percent'], .005)
chk('area unprovided n', 73, strata['Dholavira/area/unprovided']['n'], 0)
for lab, g, n, cv in [('period IV', 'Dholavira/period/IV', 82, 3.82), ('period V', 'Dholavira/period/V', 80, 13.66), ('period VI', 'Dholavira/period/VI', 23, 1.96),
                      ('period IV-V', 'Dholavira/period/IV-V', 9, 2.28), ('period unprovided', 'Dholavira/period/unprovided', 100, 16.80)]:
    s = strata[g]
    chk(f'{lab} n', n, s['n'], 0); chk(f'{lab} CV', cv, s['signal_cv_percent'], .005)
w_ = strata['Dholavira/certain/wear']; a_ = strata['Dholavira/certain/all-complete']
chk('wear n', 333, w_['n'], 0); chk('wear unit', 13.963, w_['unit_g'], .0005); chk('wear CV', 3.52, w_['signal_cv_percent'], .005); chk('wear p', .480, w_['signal_probability'], .0005)
chk('all-complete n', 363, a_['n'], 0); chk('all-complete unit', 13.944, a_['unit_g'], .0005); chk('all-complete CV', 3.46, a_['signal_cv_percent'], .005); chk('all-complete p', .482, a_['signal_probability'], .0005)

# quantograms
for lab, g, n, qg, qs, env, p in [('Dholavira certain', 'dholavira', 289, 1.71, 8.004, 7.666, .004), ('Dholavira all', 'dholavira-all-classes', 552, 15.00, 13.464, 13.797, .319),
                                  ('Susa', 'susa', 463, 4.13, 7.247, 3.551, .001), ('Girsu', 'telloh-girsu', 67, 8.42, 4.280, 3.360, .001), ('Rakhigarhi', 'rakhigarhi', 9, .44, 2.736, 2.935, .124)]:
    q = quant[g]
    chk(f'{lab} quantogram n', n, q['n'], 0); chk(f'{lab} q g', qg, q['maximum_q_g'], .005); chk(f'{lab} Q', qs, q['maximum_q_score'], .0005)
    chk(f'{lab} envelope', env, q['global_mc95'], .0005); chk(f'{lab} p', p, q['global_mc_p'], .0005)
for lab, g, p in [('Bagasra', 'bagasra', .357), ('Nagwada', 'nagwada', .789), ('Shahr-i Sokhta', 'shahr-i-sokhta', .378), ('Kish', 'tell-ingharra-kish', .815), ('Tepe Yahya', 'tepe-yahya', .190)]:
    chk(f'{lab} quantogram p', p, quant[g]['global_mc_p'], .0005)
peaks = quant['dholavira']['top_separated_peaks']
chk('Dholavira second peak 14.67 g present', 14.67, min(abs(pk['quantum_g'] - 14.67) for pk in peaks) + 14.67, .005)
chk('Dholavira 14.67 peak Q', 7.575, next(pk['score'] for pk in peaks if abs(pk['quantum_g'] - 14.67) < .006), .0005)

# local fits
susa = [f for f in models if f['group'] == 'Susa' and 'bootstrap' in f][0]
girsu = [f for f in models if f['group'] == 'Telloh/Girsu' and 'bootstrap' in f][0]
chk('Susa local unit', 8.313, susa['unit_g'], .0005); chk('Susa local lo', 8.271, susa['bootstrap']['unit_ci95_g'][0], .0005); chk('Susa local hi', 8.357, susa['bootstrap']['unit_ci95_g'][1], .0005)
chk('Susa CV', 2.76, susa['signal_cv_percent'], .005)
chk('Girsu local unit', 8.404, girsu['unit_g'], .0005); chk('Girsu lo', 8.321, girsu['bootstrap']['unit_ci95_g'][0], .0005); chk('Girsu hi', 8.484, girsu['bootstrap']['unit_ci95_g'][1], .0005)
chk('Girsu CV', 2.63, girsu['signal_cv_percent'], .005)
chk('Susa local advantage over Indus (AIC)', 110.826, fit('Susa')['aic'] - susa['aic'], .0005)
chk('Girsu local advantage over Indus (AIC)', 18.923, fit('Telloh/Girsu')['aic'] - girsu['aic'], .0005)
kish_best = min([f for f in models if f['group'] == 'Tell Ingharra/Kish' and f['model'].startswith('shekel')], key=lambda f: f['aic'])
chk('Kish best local loses to background (AIC)', 3.697, kish_best['aic_minus_background'], .0005)

# western
p = west['primary']
chk('western n', 701, p['n'], 0); chk('geometric n', 136, p['geometric_preference_n'], 0); chk('geometric %', 19.40, 100 * p['geometric_preference_fraction'], .005)
chk('geometric Wilson lo', 16.64, 100 * p['geometric_preference_wilson95'][0], .005); chk('geometric Wilson hi', 22.49, 100 * p['geometric_preference_wilson95'][1], .005)
chk('close n', 18, p['close_preference_n'], 0); chk('close %', 2.57, 100 * p['close_preference_fraction'], .005)
chk('close Wilson lo', 1.63, 100 * p['close_preference_wilson95'][0], .005); chk('close Wilson hi', 4.02, 100 * p['close_preference_wilson95'][1], .005)
chk('mixture n', 147, p['mixture_preference_n'], 0); chk('mixture %', 20.97, 100 * p['mixture_preference_fraction'], .005); chk('geometric/mixture disagreement', 11, p['geometric_mixture_disagreement_n'], 0)
chk('2% close', 10, west['threshold-2-percent']['close_preference_n'], 0); chk('5% close', 28, west['threshold-5-percent']['close_preference_n'], 0)
chk('13.65 canonical close', 22, west['canonical-13-65']['close_preference_n'], 0)
chk('remove disagreements close', 18, west['remove-source-disagreements']['close_preference_n'], 0); chk('remove disagreements n', 698, west['remove-source-disagreements']['n'], 0)
chk('expanded close', 24, west['expanded-uncertain-classes']['close_preference_n'], 0); chk('expanded n', 818, west['expanded-uncertain-classes']['n'], 0)
by_site = {}
for o in drv:
    by_site[o['site']] = by_site.get(o['site'], 0) + 1
for site, k, n in [('Susa', 10, 542), ('Telloh/Girsu', 4, 72), ('Tell Ingharra/Kish', 1, 10), ('Tepe Yahya', 2, 32), ('Shahr-i Sokhta', 1, 25)]:
    chk(f'close at {site}', k, by_site.get(site, 0), 0)
    chk(f'eligible at {site}', n, next(s['n'] for s in p['site_counts'] if s['site'] == site), 0)

# extraction / validation
chk('rows', 2058, ext['row_count'], 0)
chk('Greater Indus rows', 938, sum(s['n'] for s in ext['site_counts'] if s['site'] in ('Dholavira', 'Bagasra', 'Nagwada', 'Rakhigarhi', 'Farmana', 'Shikarpur', 'Kuntasi', 'Nageshwar')), 0)
for site, n in [('Dholavira', 870), ('Bagasra', 19), ('Nagwada', 16), ('Rakhigarhi', 15), ('Farmana', 8), ('Shikarpur', 7), ('Kuntasi', 2), ('Nageshwar', 1)]:
    chk(f'{site} rows', n, next(s['n'] for s in ext['site_counts'] if s['site'] == site), 0)
chk('audit errors before repair', 5, val['entry_errors_before_repair'], 0); chk('audit error %', 8.33, 100 * val['entry_error_fraction_before_repair'], .005)
chk('Wilson lo', 3.61, 100 * val['entry_error_wilson95_before_repair'][0], .005); chk('Wilson hi', 18.07, 100 * val['entry_error_wilson95_before_repair'][1], .005)
chk('zero-error upper bound', 6.02, 100 * val['remaining_error_wilson95'][1], .005)
chk('missing mass ids count', 5, len(val['missing_mass_catalogue_ids']), 0)
for k, v in [('area', 473), ('level', 646), ('grids', 739), ('period_literal', 393)]:
    chk(f'context parsed {k}', v, ctx['parsed_nonempty_fields'][k], 0)

# gulf
for lab, ref, k in [('main 13.65', 'main_indus_13_65', 5), ('gulf 13.5', 'gulf_13_5', 6), ('gulf 13.65', 'gulf_13_65', 6), ('shekel 7.8', 'shekel_7_8', 1), ('shekel 8.4', 'shekel_8_4', 1), ('shekel 9.4', 'shekel_9_4', 1)]:
    chk(f'Gulf within 3% {lab}', k, gulf[ref]['within_3_percent_n'], 0)

# verification
vc = ver['checks']
chk('verification: likelihood fits', 45, vc['independent_likelihood_fits_checked'], 0); chk('verification: cosine points', 169, vc['scalar_quantogram_points_checked'], 0)
chk('verification: max LL error', 4.55e-13, vc['maximum_log_likelihood_error'], 5e-15); chk('verification: max cosine error', 2.31e-14, vc['maximum_quantogram_error'], 5e-16)
chk('verification: bootstrap refits', 1800, vc['bootstrap_draws_checked'], 0); chk('verification: western scored', 701, vc['western_records_independently_scored'], 0)

bad = [c for c in checks if c['result'] != 'confirmed']
out = {'n_checked': len(checks), 'n_confirmed': len(checks) - len(bad), 'discrepancies': bad, 'checks': checks}
(P / 'review/numbers-check.json').write_text(json.dumps(out, indent=1) + '\n', encoding='utf-8')
print(json.dumps({'n_checked': len(checks), 'n_confirmed': len(checks) - len(bad)}))
for c in bad:
    print('DISCREPANCY', c)
