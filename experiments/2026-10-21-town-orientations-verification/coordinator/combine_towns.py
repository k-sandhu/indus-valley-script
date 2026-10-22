"""Combine the two blind measurers into town deviations under the frozen rule.

Implements the town-deviation rule of PROTOCOL.md (the other package's rule with
our measurer A and B in place of its img-A and img-B), the agreement between our
measurers, and the settlement tables that analysis/score_frozen.py reads.

Usage, from the repository root with the infra venv:
  python -I coordinator/combine_towns.py --parts coordinator/part-assignment-v1.json --out table-v1
"""
from pathlib import Path
import argparse, csv, json, math, hashlib, sys
from pyproj import Transformer

PKG = Path(__file__).resolve().parents[1]
DISCOVERY = {'mohenjo-daro', 'harappa', 'kalibangan'}
SE_MAX = 2.0          # imagery systems with a larger standard error do not enter
NEAR_M = 200.0        # two systems lie in the same part when their lines come this close
FLOOR = 0.3


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load_measurer(m):
    import re
    towns, version = {}, {}
    for f in sorted((PKG / f'measure-{m}' / 'towns').glob('*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        slug = d.get('slug') or f.stem
        # A redone town is written beside the old file with a -vN suffix; the highest version wins.
        mv = re.search(r'-v(\d+)$', f.stem); v = int(mv.group(1)) if mv else 1
        if v >= version.get(slug, 0):
            towns[slug] = dict(data=d, path=str(f.relative_to(PKG))); version[slug] = v
    return towns


def lonlat_lines(lines):
    out = []
    for ln in lines:
        if ln.get('endpoints_lonlat'):
            out.append([tuple(p) for p in ln['endpoints_lonlat']])
        elif ln.get('endpoints_utm') and ln.get('epsg'):
            t = Transformer.from_crs(int(ln['epsg']), 4326, always_xy=True)
            out.append([t.transform(*p) for p in ln['endpoints_utm']])
    return out


def seg_dist_m(a, b):
    lat0 = math.radians((a[0][1] + b[0][1]) / 2)
    def xy(p): return (p[0] * 111320 * math.cos(lat0), p[1] * 110540)
    A = [xy(p) for p in a]; B = [xy(p) for p in b]
    def pt_seg(p, s, e):
        vx, vy = e[0] - s[0], e[1] - s[1]; L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - s[0]) * vx + (p[1] - s[1]) * vy) / L))
        return math.hypot(p[0] - s[0] - t * vx, p[1] - s[1] - t * vy)
    def cross(o, p, q): return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    if (cross(A[0], A[1], B[0]) * cross(A[0], A[1], B[1]) < 0) and (cross(B[0], B[1], A[0]) * cross(B[0], B[1], A[1]) < 0):
        return 0.0
    return min(pt_seg(A[0], *B), pt_seg(A[1], *B), pt_seg(B[0], *A), pt_seg(B[1], *A))


def near(lines1, lines2):
    g1, g2 = lonlat_lines(lines1), lonlat_lines(lines2)
    return bool(g1 and g2) and min(seg_dist_m(a, b) for a in g1 for b in g2) <= NEAR_M


def systems_of(d, kind):
    kinds = {s['id']: s for s in d.get('sources', [])}
    out = []
    for s in d.get('systems', []):
        src = kinds.get(s['source_id'], {})
        if (src.get('kind') or ('imagery' if s['source_id'] == 'imagery' else 'plan')) != kind:
            continue
        lines = [ln for ln in d.get('lines', []) if ln.get('source_id') == s['source_id'] and ln.get('id') in s['line_ids']]
        parts = sorted({ln.get('part', '') for ln in lines})
        main = d.get('main_system_by_source', {}).get(s['source_id']) == s['id']
        north = src.get('north_class') or (lines[0].get('north_class') if lines else None)
        out.append(dict(source_id=s['source_id'], id=s['id'], theta=s['theta_deg'], se=s['se_deg'], length=s['total_length_m'],
                        n=s['n'], lines=lines, parts=parts, main=main, north=north,
                        citation=src.get('citation', ''), survey_year=src.get('survey_year')))
    return out


def wmean(vals):
    w = [1 / v['se'] ** 2 for v in vals]
    m = sum(wi * v['theta'] for wi, v in zip(w, vals)) / sum(w)
    return m, math.sqrt(1 / sum(w))


def combine(a, b, same_part):
    """The rule's steps 1, 2, 4 and 5 for two candidate values (either may be None)."""
    if a and b and same_part(a, b):
        m, se = wmean([a, b])
        sigma = max(se, abs(a['theta'] - b['theta']) / 2, FLOOR)
        disc = abs(a['theta'] - b['theta']) > 3 * math.hypot(a['se'], b['se']) and abs(a['theta'] - b['theta']) > 1.5
        return dict(theta=m, sigma=sigma, used=['A', 'B'], discordant=disc, step='1: both, same part')
    if a and b:
        return None  # different parts: resolved by the caller
    v = a or b
    if v:
        return dict(theta=v['theta'], sigma=max(v['se'], FLOOR), used=['A' if a else 'B'], discordant=False, step='2: one measurer')
    return None


def town_value(slug, A, B):
    rec = dict(slug=slug)
    sa = systems_of(A['data'], 'imagery') if A else []
    sb = systems_of(B['data'], 'imagery') if B else []
    ma = next((s for s in sa if s['main'] and s['se'] <= SE_MAX), None)
    mb = next((s for s in sb if s['main'] and s['se'] <= SE_MAX), None)
    rec['imagery_main'] = {k: (dict(theta=v['theta'], se=v['se'], length=v['length'], n=v['n'], parts=v['parts']) if v else None)
                           for k, v in (('A', next((s for s in sa if s['main']), None)), ('B', next((s for s in sb if s['main']), None)))}
    res = combine(ma, mb, lambda x, y: near(x['lines'], y['lines']))
    if res is None and ma and mb:
        # Different parts: choose the part with the larger total length both measurers report there.
        def total(part_sys, others):
            return part_sys['length'] + sum(o['length'] for o in others if near(o['lines'], part_sys['lines']))
        la, lb = total(ma, sb), total(mb, sa)
        if la >= lb:
            other = max((s for s in sb if s['se'] <= SE_MAX and near(s['lines'], ma['lines'])), key=lambda s: s['length'], default=None)
            res = combine(ma, other, lambda x, y: True) if other else combine(ma, None, None)
            res['step'] = '1: different parts, A part longer'; res['part_lines'] = ma['parts']
        else:
            other = max((s for s in sa if s['se'] <= SE_MAX and near(s['lines'], mb['lines'])), key=lambda s: s['length'], default=None)
            res = combine(other, mb, lambda x, y: True) if other else combine(None, mb, None)
            res['step'] = '1: different parts, B part longer'; res['part_lines'] = mb['parts']
        res['discordant'] = abs(ma['theta'] - mb['theta']) > 3 * math.hypot(ma['se'], mb['se']) and abs(ma['theta'] - mb['theta']) > 1.5
    if res:
        res['source'] = 'imagery'
        if 'part_lines' not in res:
            res['part_lines'] = sorted(set((ma or {}).get('parts', []) + (mb or {}).get('parts', [])))
    else:
        # Step 3: plans with true arrows, or grid arrows with 0.5 deg added in quadrature.
        def best_plan(systems):
            ok = [dict(s, se=(math.hypot(s['se'], 0.5) if s['north'] == 'grid' else s['se'])) for s in systems
                  if s['main'] and s['north'] in ('true', 'grid')]
            return max(ok, key=lambda s: s['length'], default=None)
        pa = best_plan(systems_of(A['data'], 'plan') if A else [])
        pb = best_plan(systems_of(B['data'], 'plan') if B else [])
        same = lambda x, y: bool(set(x['parts']) & set(y['parts'])) or (x['citation'] and x['citation'] == y['citation'])
        res = combine(pa, pb, same)
        if res is None and pa and pb:
            pick = pa if pa['length'] >= pb['length'] else pb
            res = combine(pick if pick is pa else None, pick if pick is pb else None, None); res['step'] = '3: plans, different parts, longer kept'
        if res:
            res['source'] = 'plan'; res['part_lines'] = sorted(set((pa or {}).get('parts', []) + (pb or {}).get('parts', [])))
            res['step'] = '3: ' + res['step']
    rec['value'] = res
    pts = [t['data'].get('located_point') for t in (A, B) if t and t['data'].get('located_point')]
    pts = [p for p in pts if p.get('latitude') is not None]
    rec['lat'] = sum(p['latitude'] for p in pts) / len(pts) if pts else None
    rec['lon'] = sum(p['longitude'] for p in pts) / len(pts) if pts else None
    return rec


def agreement(Aall, Ball):
    rows = []
    for slug in sorted(set(Aall) & set(Ball)):
        for kind in ('imagery', 'plan'):
            sa = [s for s in systems_of(Aall[slug]['data'], kind) if s['main']]
            sb = [s for s in systems_of(Ball[slug]['data'], kind) if s['main']]
            if kind == 'imagery':
                pairs = [(sa[0], sb[0])] if sa and sb else []
            else:
                pairs = [(x, y) for x in sa for y in sb if (x['citation'] and x['citation'] == y['citation'])]
            for x, y in pairs:
                d = (x['theta'] - y['theta'] + 45) % 90 - 45
                rows.append(dict(slug=slug, kind=kind, source=x['citation'] or x['source_id'], theta_A=x['theta'], se_A=x['se'],
                                 theta_B=y['theta'], se_B=y['se'], delta=d, z=d / math.hypot(x['se'], y['se']),
                                 same_part=(near(x['lines'], y['lines']) if kind == 'imagery' else bool(set(x['parts']) & set(y['parts'])))))
    def summ(rs):
        if not rs: return None
        ds = [r['delta'] for r in rs]
        return dict(n=len(rs), rms=math.sqrt(sum(d * d for d in ds) / len(ds)), mean=sum(ds) / len(ds),
                    within_1=sum(abs(d) <= 1 for d in ds), within_2=sum(abs(d) <= 2 for d in ds),
                    abs_z_gt_2=sum(abs(r['z']) > 2 for r in rs))
    return dict(pairs=rows, imagery=summ([r for r in rows if r['kind'] == 'imagery']),
                imagery_same_part=summ([r for r in rows if r['kind'] == 'imagery' and r['same_part']]),
                plan=summ([r for r in rows if r['kind'] == 'plan']))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parts', type=Path, required=True, help='JSON: {slug: {measured part label: dating part}}')
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    out = PKG / a.out
    if out.exists(): raise FileExistsError(out)
    out.mkdir(parents=True)
    Aall, Ball = load_measurer('A'), load_measurer('B')
    parts = json.loads((PKG / a.parts).read_text(encoding='utf-8')) if not a.parts.is_absolute() else json.loads(a.parts.read_text(encoding='utf-8'))
    dates = {}
    for variant in ('strict', 'liberal'):
        for r in csv.DictReader(open(PKG / f'dates-v1/dates-{variant}-v1.csv', encoding='utf-8')):
            dates.setdefault(variant, {})[(r['slug'], r['part'])] = r
    towns = [town_value(s, Aall.get(s), Ball.get(s)) for s in sorted(set(Aall) | set(Ball))]
    fields = ['slug', 'part', 'role', 'lat', 'lon', 'theta_deg', 'sigma_theta_deg', 'D_year', 'sigma_D_years']
    for variant in ('strict', 'liberal'):
        rows = []
        for t in towns:
            v = t['value']
            if not v or t['lat'] is None: continue
            mapping = parts.get(t['slug'], {})
            dparts = sorted({mapping.get(p) for p in v['part_lines'] if mapping.get(p)})
            t.setdefault('dating_part', {})[variant] = dparts
            if len(dparts) != 1: continue
            d = dates[variant].get((t['slug'], dparts[0]))
            if not d: continue
            rows.append(dict(slug=t['slug'], part=dparts[0], role='discovery' if t['slug'] in DISCOVERY else 'confirmation',
                             lat=f"{t['lat']:.6f}", lon=f"{t['lon']:.6f}", theta_deg=f"{v['theta']:.4f}", sigma_theta_deg=f"{v['sigma']:.4f}",
                             D_year=d['D_year'], sigma_D_years=d['sigma_D_years']))
        with open(out / f'settlement-table-{variant}.csv', 'x', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    inputs = {v['path']: sha(PKG / v['path']) for v in list(Aall.values()) + list(Ball.values())}
    (out / 'town-values.json').write_text(json.dumps(dict(schema_version='1.0', task='town-deviation', synthetic=False,
        provenance=dict(inputs=inputs, code={str(Path(__file__).relative_to(PKG)): sha(__file__)},
                        parts=sha(PKG / a.parts), dates={v: sha(PKG / f'dates-v1/dates-{v}-v1.csv') for v in ('strict', 'liberal')}),
        rule=dict(imagery_se_max_deg=SE_MAX, same_part_within_m=NEAR_M, floor_deg=FLOOR), towns=towns), indent=1, default=str), encoding='utf-8')
    (out / 'measurer-agreement.json').write_text(json.dumps(dict(schema_version='1.0', task='measurer-agreement', synthetic=False,
        provenance=dict(inputs=inputs), **agreement(Aall, Ball)), indent=1, default=str), encoding='utf-8')
    print('towns', len(towns), 'with value', sum(1 for t in towns if t['value']))


if __name__ == '__main__':
    main()
