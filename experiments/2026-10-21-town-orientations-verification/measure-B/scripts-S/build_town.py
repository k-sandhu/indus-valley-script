"""Assemble a town input file for systems.py from a spec and measure_lines outputs.

Spec fields: slug, measurer, located_point, sources (list of source dicts), line_files (list of
{"path", "source_id", "systems": {line_id: system_label}, "exclude": [line_ids], "part_override": name}), registrations,
notes, unmeasurable_reason. For every plan line file, the measured arrow, north record, scale and
metres-per-pixel are copied into the matching source entry. Every line keeps all refinement fields.

Usage: build_town.py <spec.json> <town-input.json>
"""
import json
import sys
from pathlib import Path

spec = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
out = Path(sys.argv[2])
if out.exists():
    raise SystemExit('output exists')
sources = {s['id']: dict(s) for s in spec['sources']}
lines = []
for lf in spec.get('line_files', []):
    res = json.loads(Path(lf['path']).read_text(encoding='utf-8'))
    sid = lf['source_id']
    if res['source_id'] != sid:
        raise SystemExit(f"source id mismatch in {lf['path']}: {res['source_id']} != {sid}")
    src = sources[sid]
    src['measurement_file'] = Path(lf['path']).as_posix()
    if res['kind'] == 'plan':
        src['north_record'] = res['north']
        src['arrow_measurement'] = res['arrow']
        src['metres_per_render_pixel'] = res['metres_per_render_pixel']
        src['render_sidecar'] = res.get('render_sidecar')
        src['source_sha256'] = res['source_sha256']
        if src.get('north_class') != res['north']['class']:
            raise SystemExit(f'north class mismatch for {sid}')
    systems = lf.get('systems', {})
    for row in res['lines']:
        if row['id'] in lf.get('exclude', []):
            continue
        r = dict(row)
        r['source_id'] = sid
        if row['id'] in systems:
            r['system'] = systems[row['id']]
        if lf.get('part_override'):
            r['part_as_picked'] = r.get('part')
            r['part'] = lf['part_override']
        for k in ['source_id', 'id', 'part', 'kind', 'identification', 'system', 'endpoints_px', 'length_m', 'bearing_deg', 'theta_deg', 'sigma_deg']:
            if k not in r:
                raise SystemExit(f'missing {k} in {row["id"]}')
        if res['kind'] == 'imagery' and ('endpoints_utm' not in r or 'epsg' not in r):
            raise SystemExit('imagery line lacks UTM endpoints')
        if res['kind'] == 'plan' and 'endpoints_plan_m' not in r:
            raise SystemExit('plan line lacks plan metres')
        lines.append(r)
town = dict(schema_version=1, slug=spec['slug'], measurer=spec.get('measurer', 'B'),
            located_point=spec['located_point'], sources=list(sources.values()), lines=lines,
            registrations=spec.get('registrations', []), notes=spec.get('notes', ''),
            unmeasurable_reason=spec.get('unmeasurable_reason'))
for k in ['imagery_status', 'imagery_unmeasurable_reason']:
    if k in spec:
        town[k] = spec[k]
out.parent.mkdir(parents=True, exist_ok=True)
with out.open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(town, indent=2, ensure_ascii=False) + '\n')
print(out, len(lines), 'lines')
