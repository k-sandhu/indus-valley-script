"""Compare this verification with experiments/2026-10-21-town-axes after its report.

Writes comparison-v1/: the two settlement tables in one CSV format, bearing,
astronomy and date comparisons, and the other package's frozen rules applied to
our numbers (variants V1 to V4 of PROTOCOL.md, plus a hybrid V1b, a rerun of its
exploratory table V4x through our independent scorer and astronomy, and V5, its
Amendment 1 rerun on our own plan measurements; V4x and V5 are post-outcome).
comparison-v1/ is superseded: its V4x kept only the four primary towns. comparison-v2/ is
superseded: its V5 averaged plan values on either side of the +-45 deg fold linearly.

Run from the repository root with the infra venv:
  python -I experiments/2026-10-21-town-orientations-verification/coordinator/compare_town_axes.py
"""
from pathlib import Path
import csv, json, math, hashlib, subprocess, sys

PKG = Path(__file__).resolve().parents[1]
OTHER = PKG.parent / '2026-10-21-town-axes'
OUT = PKG / 'comparison-v3'
sys.path.insert(0, str(PKG / 'analysis')); sys.path.insert(0, str(PKG / 'astronomy'))
from predict import predict, validation_gate  # noqa: E402
import score_frozen  # noqa: E402

FIELDS = ['slug', 'part', 'role', 'lat', 'lon', 'theta_deg', 'sigma_theta_deg', 'D_year', 'sigma_D_years']
TMAP = lambda t: t.replace('sun-', '').replace('-', '_')
DISC = {'mohenjo-daro', 'harappa', 'kalibangan'}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def jload(p): return json.loads(Path(p).read_text(encoding='utf-8'))


def write_csv(path, rows):
    with open(path, 'x', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader()
        for r in rows: w.writerow({k: r[k] for k in FIELDS})


def rows_from(table):
    out = []
    for r in table:
        out.append(dict(slug=r['slug'], part=r['part'], role=r['role'], lat=float(r['lat']), lon=float(r['lon']),
                        theta_deg=float(r['theta_deg']), sigma_theta_deg=float(r['sigma_theta_deg']),
                        D_year=float(r['D_year']), sigma_D_years=float(r['sigma_D_years'])))
    return out


def brief(res):
    def g(d, *ks):
        for k in ks: d = d.get(k) if isinstance(d, dict) else None
        return d
    return dict(n=res['n'], stage1_would_choose=g(res, 'stage1', 'would_choose'), stage1_chosen=g(res, 'stage1', 'chosen'),
                stage1_chi2=g(res, 'stage1', 'chi2'), P0=dict((k, res['P0'][k]) for k in ('status', 'r', 'one_sided_p', 'spearman_rho', 'all_leave_one_out_positive')),
                P1=dict(status=res['P1']['status'], positive_fraction=res['P1']['positive_fraction'], no_town_below_minus_2sigma=res['P1']['no_town_below_minus_2sigma']),
                P2=dict((k, res['P2'][k]) for k in ('status', 'eligible_n', 'sign_match_n')),
                P3=dict(status=res['P3']['status'], chi2=res['P3'].get('chi2')), power=res['power'].get('probability_P0_pass'),
                credence=res['credence'], status=res['status'], D1=res['D1'])


def main():
    if OUT.exists(): raise FileExistsError(OUT)
    OUT.mkdir()
    validation_gate()
    their_csv = list(csv.DictReader(open(OTHER / 'table-v1/settlement-axes.csv', encoding='utf-8')))
    their_dates = {t['town']: t for t in jload(OTHER / 'dates-v1/dates.json')['towns']}
    their_choice = jload(OTHER / 'discovery-v1/choice.json')
    their_conf = jload(OTHER / 'confirmation-v1/results.json')
    expl_table = jload(OTHER / 'exploratory-v1/table.json')
    expl_choice = jload(OTHER / 'exploratory-v1/choice.json')
    expl_res = jload(OTHER / 'exploratory-v1/results.json')
    ours_tv = jload(PKG / 'table-v1/town-values.json')
    our_dates = {v: {(r['slug'], r['part']): r for r in csv.DictReader(open(PKG / f'dates-v1/dates-{v}-v1.csv', encoding='utf-8'))} for v in ('strict', 'liberal')}

    # Their primary table in our CSV format.
    theirs = []
    for r in their_csv:
        if r['theta_deg'] and r['D_year']:
            theirs.append(dict(slug=r['town'], part=r['part'], role=r['role'], lat=float(r['lat']), lon=float(r['lon']),
                               theta_deg=float(r['theta_deg']), sigma_theta_deg=float(r['sigma_theta_deg']),
                               D_year=float(r['D_year']), sigma_D_years=float(r['sigma_D'])))
    write_csv(OUT / 'theirs-primary.csv', theirs)
    their_by = {r['town']: r for r in their_csv}

    # Our primary values with their dates for the matching part (V1), and with our dates (V2).
    match_part = {'lothal': 'dock', 'dholavira': 'middle town'}
    ours = [t for t in ours_tv['towns'] if t['value']]
    v1 = []
    for t in ours:
        parts = {p['part']: p for p in their_dates[t['slug']]['parts']}
        p = parts[match_part[t['slug']]]
        v1.append(dict(slug=t['slug'], part=match_part[t['slug']], role='discovery' if t['slug'] in DISC else 'confirmation',
                       lat=t['lat'], lon=t['lon'], theta_deg=t['value']['theta'], sigma_theta_deg=t['value']['sigma'],
                       D_year=float(p['D_year']), sigma_D_years=float(p['sigma_D'])))
    write_csv(OUT / 'ours-primary-their-dates.csv', v1)
    v2 = {v: rows_from(csv.DictReader(open(PKG / f'table-v1/settlement-table-{v}.csv', encoding='utf-8'))) for v in ('strict', 'liberal')}

    # Bearings: towns with a primary value in both tables.
    bearings = []
    for t in ours:
        o = their_by.get(t['slug'])
        if not o or not o['theta_deg']: continue
        d = t['value']['theta'] - float(o['theta_deg']); s = math.hypot(t['value']['sigma'], float(o['sigma_theta_deg']))
        bearings.append(dict(slug=t['slug'], ours=t['value']['theta'], sigma_ours=t['value']['sigma'], our_part=t['value']['part_lines'],
                             theirs=float(o['theta_deg']), sigma_theirs=float(o['sigma_theta_deg']), their_part=o['part'],
                             their_img_A=o['theta_img_A'], their_img_B=o['theta_img_B'], delta=d, z=d / s, same_part=t['slug'] == 'lothal'))
    w = [1 / (b['sigma_ours'] ** 2 + b['sigma_theirs'] ** 2) for b in bearings]
    wm = sum(wi * b['delta'] for wi, b in zip(w, bearings)) / sum(w); wse = 1 / math.sqrt(sum(w))
    frac = sum(abs(b['z']) <= 2.5 for b in bearings) / len(bearings)
    bearing_verdict = 'agree' if ((abs(wm) <= 2 * wse or abs(wm) <= 0.5) and frac >= 0.8) else 'disagree'
    # compare.py on the common towns, with the other package's dates in both tables so that ΔD is zero.
    common = {b['slug'] for b in bearings}
    write_csv(OUT / 'compare-ours.csv', [r for r in v1 if r['slug'] in common])
    write_csv(OUT / 'compare-theirs.csv', [dict(r, D_year=next(x['D_year'] for x in v1 if x['slug'] == r['slug']), sigma_D_years=next(x['sigma_D_years'] for x in v1 if x['slug'] == r['slug'])) for r in theirs if r['slug'] in common])
    cp = subprocess.run([sys.executable, '-I', str(PKG / 'analysis/compare.py'), str(OUT / 'compare-ours.csv'), str(OUT / 'compare-theirs.csv'),
                         '--output', str(OUT / 'compare-py-bearings.json')], capture_output=True, text=True)
    if cp.returncode: raise RuntimeError(cp.stderr)

    # Astronomy: our predictions at their coordinates and dates for every per-town value they report.
    def lat_lon_D(town, table='primary'):
        if table == 'primary':
            r = their_by[town]; return float(r['lat']), float(r['lon']), float(r['D_year'])
        r = next(x for x in expl_table['towns'] if x['town'] == town); return r['lat'], r['lon'], r['D_year']
    astro = []
    def add(source, town, target, theirs_val, table='primary'):
        lat, lon, D = lat_lon_D(town, table)
        t, rate = predict(TMAP(target), lat, lon, D)
        astro.append(dict(source=source, town=town, target=TMAP(target), lat=lat, lon=lon, D_year=D, theirs=theirs_val, ours=t, delta=t - theirs_val))
    for c in their_choice['candidates']:
        for tw in c['towns']: add('discovery-v1/choice.json', tw['town'], c['target'], tw['theta_pred'])
    for c in expl_choice['candidates']:
        for tw in c['towns']: add('exploratory-v1/choice.json', tw['town'], c['target'], tw['theta_pred'], 'exploratory')
    for key, field, target in (('P1_pleiades', 'theta_alcyone', 'alcyone'), ('P2_aldebaran', 'theta_aldebaran', 'aldebaran')):
        for tw in their_conf[key]['per_town']: add(f'confirmation-v1/results.json#{key}', tw['town'], target, tw[field])
        for tw in expl_res[key]['per_town']: add(f'exploratory-v1/results.json#{key}', tw['town'], target, tw[field], 'exploratory')
    for tw in their_conf['P3_chosen_target']['per_town']: add('confirmation-v1/results.json#P3', tw['town'], their_conf['P3_chosen_target']['target'], tw['theta_pred'])
    for tw in expl_res['P3_chosen_target']['per_town']: add('exploratory-v1/results.json#P3', tw['town'], expl_res['P3_chosen_target']['target'], tw['theta_pred'], 'exploratory')
    by_target = {}
    for a in astro: by_target[a['target']] = max(by_target.get(a['target'], 0), abs(a['delta']))
    astro_verdict = 'agree' if max(by_target.values()) <= 0.10 else 'disagree'

    # Dates, part by part, for towns dated in both.
    dates = []
    for town, td in their_dates.items():
        if td.get('D_year') is None: continue
        for v in ('strict', 'liberal'):
            for (s, part), r in our_dates[v].items():
                if s != town: continue
                dates.append(dict(variant=v, town=town, our_part=part, our_D=float(r['D_year']), our_sigma=float(r['sigma_D_years']), our_level=r['level'],
                                  their_part=td['date_part'], their_D=td['D_year'], their_sigma=td['sigma_D'], their_tier=td['date_tier'],
                                  delta=float(r['D_year']) - td['D_year']))

    # Frozen rules applied to our numbers.
    fixed = TMAP(their_choice['chosen_target'])
    kw = dict(simulations=20000)
    variants = {}
    variants['V1_ours_theirdates_ourastro'] = brief(score_frozen.score(v1, fixed_target=fixed, **kw))
    hybrid = [r for r in theirs if r['role'] == 'discovery'] + v1
    write_csv(OUT / 'hybrid-their-discovery-our-confirmation.csv', hybrid)
    variants['V1b_their_discovery_our_confirmation'] = brief(score_frozen.score(hybrid, fixed_target=fixed, **kw))
    for v in ('strict', 'liberal'):
        variants[f'V2_ours_ourdates_{v}'] = brief(score_frozen.score(v2[v], fixed_target=fixed, **kw)) if v2[v] else dict(n=0)
    # V3: their deviations with our dates for their dated part where we date it.
    their_part_to_ours = {'mohenjo-daro': ('lower town', 'lower town'), 'harappa': ('Mound F', 'Mound F'),
                          'lothal': ('lower town', 'lower town'), 'dholavira': ('castle', 'castle')}
    for v in ('strict', 'liberal'):
        rows = []
        for r in theirs:
            key = (r['slug'], their_part_to_ours[r['slug']][0])
            d = our_dates[v].get(key)
            if d: rows.append(dict(r, D_year=float(d['D_year']), sigma_D_years=float(d['sigma_D_years'])))
        write_csv(OUT / f'V3-theirs-ourdates-{v}.csv', rows)
        variants[f'V3_theirs_ourdates_{v}'] = brief(score_frozen.score(rows, fixed_target=fixed, **kw)) if rows else dict(n=0)
    variants['V4_theirs_theirdates_ourastro'] = brief(score_frozen.score(theirs, **kw))
    expl_rows = [dict(slug=t['town'], part=t['date_part'] or '', role=t['role'], lat=t['lat'], lon=t['lon'], theta_deg=t['theta_deg'],
                      sigma_theta_deg=t['sigma_theta_deg'], D_year=t['D_year'], sigma_D_years=t['sigma_D'])
                 for t in expl_table['towns'] if t['theta_deg'] is not None and t['D_year'] is not None and t['lat'] is not None]
    write_csv(OUT / 'theirs-exploratory.csv', expl_rows)
    variants['V4x_their_exploratory_ourastro'] = brief(score_frozen.score(expl_rows, **kw))

    import importlib.util
    spec = importlib.util.spec_from_file_location('combine', PKG / 'coordinator/combine_towns.py'); cmb = importlib.util.module_from_spec(spec); spec.loader.exec_module(cmb)
    MA, MB = cmb.load_measurer('A'), cmb.load_measurer('B')
    def plan_main(T, slug):
        if slug not in T: return None
        mains = [x for x in cmb.systems_of(T[slug]['data'], 'plan') if x['main']]
        return max(mains, key=lambda x: x['length'], default=None)
    our_primary = {t['slug']: t for t in ours}
    deltas = []
    for slug, t in our_primary.items():
        for T in (MA, MB):
            pm = plan_main(T, slug)
            if pm: deltas.append(pm['theta'] - t['value']['theta'])
    n_towns_with_both = len({slug for slug in our_primary if plan_main(MA, slug) or plan_main(MB, slug)})
    s_delta = math.sqrt(sum(d * d for d in deltas) / len(deltas)) if n_towns_with_both >= 3 else 3.0
    v5 = []
    for t in expl_table['towns']:
        if t['D_year'] is None or t['lat'] is None: continue
        slug = t['town']
        if slug in our_primary:
            o = our_primary[slug]; theta, sig = o['value']['theta'], o['value']['sigma']
        else:
            a, b = plan_main(MA, slug), plan_main(MB, slug)
            vals = [dict(x) for x in (a, b) if x]
            if not vals: continue
            if len(vals) == 2:  # align on the 90-degree circle before averaging
                vals[1]['theta'] += 90 * round((vals[0]['theta'] - vals[1]['theta']) / 90)
            w5 = [1 / x['se'] ** 2 for x in vals]; theta = sum(wi * x['theta'] for wi, x in zip(w5, vals)) / sum(w5)
            theta = (theta + 45) % 90 - 45
            base = max(math.sqrt(1 / sum(w5)), abs(vals[0]['theta'] - vals[1]['theta']) / 2 if len(vals) == 2 else 0, 0.3)
            sig = math.sqrt(base ** 2 + s_delta ** 2)
        v5.append(dict(slug=slug, part=t['date_part'] or '', role=t['role'], lat=t['lat'], lon=t['lon'], theta_deg=theta,
                       sigma_theta_deg=sig, D_year=t['D_year'], sigma_D_years=t['sigma_D']))
    write_csv(OUT / 'V5-amendment1-our-plans-their-dates.csv', v5)
    variants['V5_amendment1_our_plans_their_dates'] = dict(brief(score_frozen.score(v5, **kw)), s_delta_deg=s_delta,
        plan_minus_imagery_deltas=deltas, towns=[r['slug'] for r in v5],
        rule='Their Amendment 1: towns without our primary value take the inverse-variance mean of our two measurers main plan systems (per measurer, the main system of its longest plan source), whatever the north label, with sigma^2 = max(SE, half difference, 0.3)^2 + s_delta^2; s_delta = 3 deg when fewer than three towns have both imagery and plans; dates from their exploratory table.')
    their_outcome = dict(primary=dict(n=their_conf['n_all'], P0=their_conf['P0_all'].get('passes'), P0_decided=their_conf['P0_all'].get('decided'),
                                      chosen=their_choice['chosen_target'], credence=their_conf['credence_rule']),
                         exploratory=dict(n=expl_res['n_all'], P0_r=expl_res['P0_all']['pearson_r'], P0_p=expl_res['P0_all']['p_one_sided'],
                                          chosen=expl_choice['chosen_target'], credence_rule=expl_res['credence_rule']))
    v1b = variants['V1_ours_theirdates_ourastro']
    outcome_reproduced = (v1b['P0']['status'] == 'undecided') == (their_conf['P0_all'].get('decided') is False) and abs(v1b['credence'] - their_conf['credence_rule']['posterior']) < 1e-9

    record = dict(schema_version='1.0', task='town-axes-comparison', synthetic=False,
        provenance=dict(inputs={str(p.relative_to(PKG.parents[1])): sha(p) for p in [
            OTHER / 'REPORT.md', OTHER / 'table-v1/settlement-axes.csv', OTHER / 'dates-v1/dates.json', OTHER / 'discovery-v1/choice.json',
            OTHER / 'confirmation-v1/results.json', OTHER / 'exploratory-v1/table.json', OTHER / 'exploratory-v1/choice.json',
            OTHER / 'exploratory-v1/results.json', PKG / 'table-v1/town-values.json', PKG / 'dates-v1/dates-strict-v1.csv',
            PKG / 'dates-v1/dates-liberal-v1.csv']},
            code={str(p.relative_to(PKG)): sha(p) for p in [Path(__file__), PKG / 'analysis/score_frozen.py', PKG / 'astronomy/predict.py', PKG / 'astronomy/core.py', PKG / 'astronomy/horizon.py']}),
        bearings=dict(rows=bearings, weighted_mean_delta=wm, weighted_mean_se=wse, fraction_abs_z_le_2_5=frac, verdict=bearing_verdict),
        astronomy=dict(rows=astro, max_abs_delta_by_target=by_target, verdict=astro_verdict),
        dates=dates, variants=variants, their_outcome=their_outcome,
        frozen_outcome_reproduced=outcome_reproduced)
    (OUT / 'comparison.json').write_text(json.dumps(record, indent=1, default=str), encoding='utf-8')
    print(json.dumps(dict(bearings=record['bearings'], astronomy_max=by_target, astro_verdict=astro_verdict,
                          variants={k: {kk: v.get(kk) for kk in ('n', 'stage1_would_choose', 'stage1_chosen', 'P0', 'P1', 'P2', 'P3', 'credence', 'status', 'power')} for k, v in variants.items()},
                          outcome_reproduced=outcome_reproduced), indent=1, default=str))


if __name__ == '__main__':
    main()
