"""Date comparison with the other package, part matched by an explicit mapping.

Supersedes the automatic part matching in comparison-v3/comparison.json#/dates,
which paired Harappa's Mound AB with the other package's Mound F.
Run from the package directory with the infra venv: python -I coordinator/compare_dates.py
"""
from pathlib import Path
import csv, json, hashlib
PKG = Path(__file__).resolve().parents[1]; OTHER = PKG.parent / '2026-10-21-town-axes'
# Our part that corresponds to the part the other package dated.
MAP = {'chanhu-daro': 'planned settlement', 'dholavira': 'castle', 'farmana': 'planned settlement', 'harappa': 'Mound F',
       'kalibangan': 'lower town', 'kanmer': 'fortified settlement', 'rangpur': 'Harappan built settlement',
       'lothal': 'lower town', 'mohenjo-daro': 'lower town', 'rojdi': 'main settlement and enclosure', 'surkotada': 'citadel'}
theirs = {t['town']: t for t in json.loads((OTHER / 'dates-v1/dates.json').read_text(encoding='utf-8'))['towns']}
out = {}
for v in ('strict', 'liberal'):
    ours = {(r['slug'], r['part']): r for r in csv.DictReader(open(PKG / f'dates-v1/dates-{v}-v1.csv', encoding='utf-8'))}
    rows = []
    for town, part in MAP.items():
        o, t = ours.get((town, part)), theirs.get(town)
        if not o or not t or t.get('D_year') is None: continue
        d = float(o['D_year']) - t['D_year']; tol = max(100, t['sigma_D'])
        rows.append(dict(town=town, our_part=part, our_D=float(o['D_year']), our_sigma=float(o['sigma_D_years']), our_level=o['level'],
                         their_part=t['date_part'], their_D=t['D_year'], their_sigma=t['sigma_D'], their_tier=t['date_tier'],
                         delta=d, tolerance=tol, agree=abs(d) <= tol))
    n = len(rows); k = sum(r['agree'] for r in rows)
    out[v] = dict(n=n, agree=k, fraction=k / n if n else None, verdict='agree' if n and k / n >= 0.8 else 'disagree', rows=rows)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
path = PKG / 'comparison-v3/dates-matched.json'
if path.exists(): raise FileExistsError(path)
path.write_text(json.dumps(dict(schema_version='1.0', task='date-comparison', synthetic=False,
    provenance=dict(inputs={str(p.relative_to(PKG.parents[1])): sha(p) for p in (OTHER / 'dates-v1/dates.json', PKG / 'dates-v1/dates-strict-v1.csv', PKG / 'dates-v1/dates-liberal-v1.csv')},
                    code={'coordinator/compare_dates.py': sha(__file__)}), mapping=MAP, **out), indent=1), encoding='utf-8')
for v in out: print(v, out[v]['n'], out[v]['agree'], out[v]['verdict'], [ (r['town'], r['delta']) for r in out[v]['rows'] if not r['agree']])
