"""Agreement of the two measurers' main systems on the same published plans.

Bearings are taken relative to each plan's own arrow, so this measures how
reproducibly two measurers read the same drawing, not true orientation.
Run from the package directory with the infra venv: python -I coordinator/plan_agreement.py
"""
from pathlib import Path
import json, math, hashlib, importlib.util, statistics

PKG = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('c', PKG / 'coordinator/combine_towns.py'); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
A, B = c.load_measurer('A'), c.load_measurer('B')
pairs = json.loads((PKG / 'coordinator/plan-pairs-v1.json').read_text(encoding='utf-8'))['pairs']
rows = []
for slug, sa, sb, label in pairs:
    def main_of(T, sid):
        for s in c.systems_of(T[slug]['data'], 'plan'):
            if s['source_id'] == sid and s['main']: return s
        raise KeyError((slug, sid))
    x, y = main_of(A, sa), main_of(B, sb)
    raw = lambda s: [ln.get('bearing_raw_deg', ln.get('bearing_deg')) for ln in s['lines']]
    d = (x['theta'] - y['theta'] + 45) % 90 - 45
    rows.append(dict(slug=slug, figure=label, theta_A=x['theta'], se_A=x['se'], n_A=x['n'], north_A=x['north'],
                     theta_B=y['theta'], se_B=y['se'], n_B=y['n'], north_B=y['north'], delta=d, z=d / math.hypot(x['se'], y['se']),
                     north_class_agrees=x['north'] == y['north']))
ds = [r['delta'] for r in rows]
summary = dict(n=len(rows), median_abs=statistics.median(abs(d) for d in ds), rms=math.sqrt(sum(d * d for d in ds) / len(ds)),
               within_1=sum(abs(d) <= 1 for d in ds), within_2=sum(abs(d) <= 2 for d in ds), abs_z_gt_2=sum(abs(r['z']) > 2 for r in rows),
               north_class_disagreements=[r['slug'] + ': ' + r['figure'] for r in rows if not r['north_class_agrees']])
out = PKG / 'agreement-v1/plan-agreement.json'
out.parent.mkdir(exist_ok=True)
if out.exists(): raise FileExistsError(out)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
out.write_text(json.dumps(dict(schema_version='1.0', task='plan-agreement', synthetic=False,
    provenance=dict(inputs={A[s]['path']: sha(PKG / A[s]['path']) for s in {p[0] for p in pairs}} | {B[s]['path']: sha(PKG / B[s]['path']) for s in {p[0] for p in pairs}} | {'coordinator/plan-pairs-v1.json': sha(PKG / 'coordinator/plan-pairs-v1.json')},
                    code={'coordinator/plan_agreement.py': sha(__file__), 'coordinator/combine_towns.py': sha(PKG / 'coordinator/combine_towns.py')}),
    summary=summary, pairs=rows), indent=1), encoding='utf-8')
for r in rows: print(f"{r['slug']:12s} {r['figure'][:42]:42s} A {r['theta_A']:+7.2f}±{r['se_A']:.2f} B {r['theta_B']:+7.2f}±{r['se_B']:.2f} d {r['delta']:+6.2f} z {r['z']:+5.1f} {'' if r['north_class_agrees'] else 'north: '+r['north_A']+'/'+r['north_B']}")
print(json.dumps(summary, indent=1))
