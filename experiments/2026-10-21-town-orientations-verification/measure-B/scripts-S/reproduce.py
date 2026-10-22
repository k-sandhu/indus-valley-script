"""Reproduce share S from picks: rerun measure_lines.py on every picks file, rebuild every town input
from its spec, rerun systems.py, and compare with the saved outputs. Writes only to a scratch directory.

Also checks that every line has a source locator (source_id present in the town's sources with a
citation or composite path and a page) and a positive sigma, and that every plan source has a north
class with evidence.

Usage (from repo root, with the infra venv and -I):
  reproduce.py <scratch-dir> <slug> [<slug> ...]
"""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
PKG = ROOT / 'experiments/2026-10-21-town-orientations-verification'
MB = PKG / 'measure-B'
TOOLS = PKG / 'tools'
PY = sys.executable
scratch = Path(sys.argv[1]); scratch.mkdir(parents=True, exist_ok=False)
slugs = sys.argv[2:]
ok = True

def close(a, b, tol=1e-9):
    if isinstance(a, float) or isinstance(b, float):
        return a is not None and b is not None and math.isclose(a, b, rel_tol=0, abs_tol=tol)
    return a == b

for slug in slugs:
    spec_path = MB / f'town-inputs-S/{slug}-spec-v1.json'
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    # 1. rerun every line file from its picks
    new_spec = json.loads(json.dumps(spec))
    for lf in new_spec.get('line_files', []):
        lines_path = ROOT / lf['path']
        picks_path = Path(str(lines_path).replace('-lines-', '-picks-'))
        saved = json.loads(lines_path.read_text(encoding='utf-8'))
        sidecar = saved['render_sidecar']
        out = scratch / f'{slug}-{lines_path.name}'
        r = subprocess.run([PY, '-I', str(TOOLS / 'measure_lines.py'), str(picks_path), sidecar, str(out)], capture_output=True, text=True)
        if r.returncode:
            print(slug, 'measure_lines failed', r.stderr[-500:]); ok = False; continue
        new = json.loads(out.read_text(encoding='utf-8'))
        for a, b in zip(saved['lines'], new['lines']):
            for k in ['bearing_deg', 'theta_deg', 'sigma_deg', 'length_m']:
                if not close(a[k], b[k]):
                    print(slug, a['id'], k, a[k], b[k]); ok = False
        if saved.get('arrow') and not close(saved['arrow']['direction_px_deg'], new['arrow']['direction_px_deg']):
            print(slug, 'arrow differs'); ok = False
        lf['path'] = out.as_posix()
    # 2. rebuild town input and rerun systems
    sp = scratch / f'{slug}-spec.json'; sp.write_text(json.dumps(new_spec, indent=1, ensure_ascii=False), encoding='utf-8')
    tin = scratch / f'{slug}-input.json'; tout = scratch / f'{slug}-town.json'; summ = scratch / 'summary.csv'
    for cmd in ([PY, '-I', str(MB / 'scripts-S/build_town.py'), str(sp), str(tin)],
                [PY, '-I', str(TOOLS / 'systems.py'), str(tin), str(tout), '--summary', str(summ)]):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode:
            print(slug, 'failed', cmd[2], r.stderr[-500:]); ok = False
    saved_town = json.loads((MB / f'towns/{slug}.json').read_text(encoding='utf-8'))
    new_town = json.loads(tout.read_text(encoding='utf-8'))
    if saved_town['main_system_by_source'] != new_town['main_system_by_source']:
        print(slug, 'main systems differ'); ok = False
    ss = {(s['source_id'], s['id']): s for s in saved_town['systems']}
    for s in new_town['systems']:
        t = ss.get((s['source_id'], s['id']))
        if t is None or not all(close(s[k], t[k]) for k in ['n', 'total_length_m', 'theta_deg', 'se_deg']):
            print(slug, 'system differs', s['id']); ok = False
    # 3. completeness checks on the saved town
    src = {s['id']: s for s in saved_town['sources']}
    for l in saved_town['lines']:
        s = src.get(l['source_id'])
        if s is None:
            print(slug, l['id'], 'no source entry'); ok = False; continue
        if s['kind'] == 'plan' and not (s.get('citation') and s.get('pdf_page') and s.get('printed_page') and s.get('figure')):
            print(slug, l['id'], 'plan locator incomplete'); ok = False
        if s['kind'] == 'imagery' and not (s.get('composite_path') and s.get('scene_ids')):
            print(slug, l['id'], 'imagery locator incomplete'); ok = False
        if not (l.get('sigma_deg') and l['sigma_deg'] > 0):
            print(slug, l['id'], 'sigma missing'); ok = False
        if s['kind'] == 'plan' and not l.get('north_class'):
            print(slug, l['id'], 'line lacks north class'); ok = False
    for s in saved_town['sources']:
        if s['kind'] == 'plan' and not (s.get('north_class') and s.get('north_evidence')):
            print(slug, s['id'], 'plan lacks north class or evidence'); ok = False
    if not saved_town['lines'] and not saved_town.get('unmeasurable_reason'):
        print(slug, 'unmeasured without reason'); ok = False
    print(slug, 'lines', len(saved_town['lines']), 'systems', len(saved_town['systems']), 'OK' if ok else 'PROBLEM SO FAR')
print('ALL OK' if ok else 'PROBLEMS FOUND')
