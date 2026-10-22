"""Build the frozen layout-date tables of the verification from the dating record.

Strict variant: the dating run's proposed candidates under the three levels of
evidence, unchanged. Liberal variant: the strict dates, plus, for parts with no
strict candidate, the IntCal20 median of the oldest radiocarbon determination
attributed to the part's layout phase (the other study's sensitivity rule), or a
published calibrated date for the first wall where no determination is listed.
The decisions below were made before any measurement output existed.

Run from the repository root with the infra venv:
  venv-infra/Scripts/python.exe -I experiments/2026-10-21-town-orientations-verification/coordinator/build_dates.py
"""
from pathlib import Path
import csv, json, hashlib, math, sys

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG / 'analysis'))
from calibrate import calibrate  # noqa: E402

DATING = PKG / 'dating-v1'
OUT = PKG / 'dates-v1'
CURVE = PKG.parents[1] / 'data/raw/2026-10-21-town-orientations-verification/astro/intcal20.14c'
DISCOVERY = {'mohenjo-daro', 'harappa', 'kalibangan'}

# Liberal-variant decisions for parts without a strict candidate.
# 'dets': which determinations of radiocarbon.csv date the layout phase, chosen by
# the dating run's phase attribution; 'parts': which parts the date applies to.
LIBERAL = {
    'mohenjo-daro': dict(parts=['citadel / perimeter wall', 'lower town'], published=(-2707, -2575),
        basis='Published calibrated result for a core from the first mud-brick perimeter wall, 2708-2576 cal BC '
              '(sindhi2026, quoting the 2025-26 preliminary report, p. 8); midpoint; no determination with lab code is listed.'),
    'lothal': dict(parts=['acropolis', 'lower town'], dets=['TF-133', 'TF-135'],
        basis='Determinations attributed to Period A, Phase II, the layout phase (rao1979).'),
    'surkotada': dict(parts=['citadel', 'residential annexe'], dets=['TF-1305', 'TF-1310', 'TF-1304 / TF-1309 (combined)', 'PRL-85'],
        basis='Determinations attributed to Period IA, the layout phase (joshi1990 and laboratory lists).'),
    'rakhigarhi': dict(parts=['citadel / acropolis', 'lower town'], dets=['BS-3368 / S-4215', 'BS-3389 / S-4237'],
        basis='Determinations labelled Mature Harappan, the period of the Period II layout; structural subphase unresolved.'),
    'rakhigarhi-rgr6': dict(town='rakhigarhi', parts=['RGR-6 antecedent settlement'], dets=['BS-3344 / S-4190', 'BS-3324 / S-4180'],
        basis='Determinations labelled Early Harappan, the period of the Period IB organized settlement.'),
    'gola-dhoro': dict(parts=['walled enclosure'], dets=['Beta-217983'],
        basis='Determination attributed to Phase 2, the enclosure phase.'),
    'khirsara': dict(parts=None, dets='all',
        basis='Mature Harappan occupation determinations; their link to first construction is unresolved.'),
    'kuntasi': dict(parts=None, dets=['BS-567', 'PRL-1370'],
        basis='Period I determinations; the first enclosure phase is not separated.'),
    'rojdi': dict(parts=None, dets='phase:Rojdi A',
        basis='Rojdi A determinations, the earliest occupation phase; the enclosure phase is not separated.'),
    'balakot': dict(parts=None, dets='all',
        basis='Period II (Mature Harappan) determinations; the founding layout phase is not separated.'),
    'allahdino': dict(parts=None, dets='all',
        basis='Mature Harappan determinations; architectural subphase unresolved.'),
    'lakhanjo-daro': dict(parts=None, dets='all',
        basis='Single Mature Indus determination from an excavated area; layout link unresolved.'),
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def interval68(result):
    years = result['astronomical_year']; p = result['probability']
    order = sorted(range(len(years)), key=lambda i: years[i])
    c = 0.0; lo = hi = None
    for i in order:
        c += p[i]
        if lo is None and c >= 0.1587: lo = years[i]
        if hi is None and c >= 0.8413: hi = years[i]
    return lo, hi


def main():
    OUT.mkdir(exist_ok=True)
    cands = list(csv.DictReader(open(DATING / 'candidates.csv', encoding='utf-8')))
    dets = list(csv.DictReader(open(DATING / 'radiocarbon.csv', encoding='utf-8')))
    fields = ['slug', 'part', 'role', 'layout_phase_label', 'level', 'year_bce', 'D_year', 'sigma_D_years', 'basis', 'source_key', 'flags']
    strict, liberal, calib = [], [], []
    for r in cands:
        if r['level']:
            flags = []
            if r['slug'] == 'bhirrana': flags.append('very early published chronology; review before use')
            if r['slug'] == 'dholavira' and r['part'] == 'castle': flags.append('Stage I nucleus date; exposed castle walls are later')
            row = dict(slug=r['slug'], part=r['part'], role='discovery' if r['slug'] in DISCOVERY else 'confirmation',
                       layout_phase_label=r['layout_phase_label'], level=r['level'], year_bce=r['candidate_year_bce'],
                       D_year=r['candidate_astronomical_year'], sigma_D_years=r['sigma_D_years'],
                       basis=f"level {r['level']} candidate of the dating run", source_key=r['source_key'], flags='; '.join(flags))
            strict.append(row); liberal.append(dict(row))
    have = {(r['slug'], r['part']) for r in strict}
    for key, spec in LIBERAL.items():
        town = spec.get('town', key)
        parts = spec['parts'] or [r['part'] for r in cands if r['slug'] == town]
        if 'published' in spec:
            a, b = spec['published']; D = (a + b) / 2; sigma = 150.0; src = 'published calibrated range'
            calib.append(dict(key=key, published_range_astronomical=[a, b], D_year=D))
        else:
            pool = [d for d in dets if d['slug'] == town]
            if spec['dets'] == 'all': chosen = pool
            elif isinstance(spec['dets'], str) and spec['dets'].startswith('phase:'):
                chosen = [d for d in pool if d['phase_label'] == spec['dets'][6:]]
            else: chosen = [d for d in pool if d['lab_code'] in spec['dets']]
            if not chosen: raise ValueError(f'no determinations for {key}')
            results = []
            for d in chosen:
                res = calibrate(float(d['conventional_age_bp']), float(d['error_bp']), CURVE)
                lo, hi = interval68(res)
                results.append(dict(lab_code=d['lab_code'], BP=float(d['conventional_age_bp']), sigma_BP=float(d['error_bp']),
                                    median_astronomical_year=res['median_astronomical_year'], interval68_astronomical=[lo, hi]))
            oldest = min(results, key=lambda x: x['median_astronomical_year'])
            D = oldest['median_astronomical_year']; lo, hi = oldest['interval68_astronomical']
            sigma = max(150.0, (hi - lo) / 2); src = f"IntCal20 median of oldest determination {oldest['lab_code']}"
            calib.append(dict(key=key, determinations=results, oldest=oldest['lab_code'], D_year=D, sigma_D_years=sigma))
        for part in parts:
            if (town, part) in have: continue
            liberal.append(dict(slug=town, part=part, role='discovery' if town in DISCOVERY else 'confirmation',
                                layout_phase_label=next((r['layout_phase_label'] for r in cands if r['slug'] == town and r['part'] == part), ''),
                                level='L', year_bce=f'{1 - D:.0f}', D_year=f'{D:.1f}', sigma_D_years=f'{sigma:.0f}',
                                basis=spec['basis'] + ' ' + src, source_key='dating-v1', flags='liberal variant only'))
    for name, rows in (('dates-strict-v1.csv', strict), ('dates-liberal-v1.csv', liberal)):
        path = OUT / name
        if path.exists(): raise FileExistsError(path)
        with open(path, 'x', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    rec = OUT / 'calibrations-v1.json'
    if rec.exists(): raise FileExistsError(rec)
    rec.write_text(json.dumps(dict(schema_version='1.0', task='layout-dates', synthetic=False,
        provenance=dict(inputs={str(p): sha(p) for p in (DATING / 'candidates.csv', DATING / 'radiocarbon.csv', CURVE)},
                        code={str(Path(__file__)): sha(__file__), str(PKG / 'analysis/calibrate.py'): sha(PKG / 'analysis/calibrate.py')}),
        liberal_rule='For a part without a strict candidate: the IntCal20 median calendar year of the oldest determination '
                     'attributed to its layout phase; sigma_D = max(150 years, half the 68.3% interval of that determination).',
        calibrations=calib, counts=dict(strict_rows=len(strict), liberal_rows=len(liberal))), indent=2), encoding='utf-8')
    print(len(strict), 'strict rows;', len(liberal), 'liberal rows')


if __name__ == '__main__':
    main()
