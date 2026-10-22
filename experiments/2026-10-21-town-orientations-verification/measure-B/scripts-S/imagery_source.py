"""Print the imagery source entry for a town from the imagery manifest, or from an on-disk acquisition result.

Usage: imagery_source.py <manifest.json> <slug> [--acquisition-dir DIR]
With --acquisition-dir, scene ids and datetimes are read from DIR/acquisition-result.json when the
manifest has no composite for the town.
"""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('manifest'); p.add_argument('slug'); p.add_argument('--acquisition-dir')
a = p.parse_args()
m = json.loads(Path(a.manifest).read_text(encoding='utf-8'))
t = next(x for x in m['towns'] if x['slug'] == a.slug)
out = dict(id='imagery', kind='imagery', manifest_path='experiments/2026-10-21-town-orientations-verification/infra-v1/imagery-manifest-v1.json')
if t.get('composite'):
    c = t['composite']
    used = [s for s in t['scenes'] if s.get('used_in_composite')]
    out.update(composite_path=c['path'], composite_sha256=c['sha256'], scene_ids=t['composite_scene_ids'],
               scene_datetimes=[s['datetime'] for s in t['scenes'] if s['item_id'] in t['composite_scene_ids']],
               epsg=t['epsg'], tile=t['tile'], manifest_status=t['status'], rights_notice=m['rights_notice'])
else:
    out.update(manifest_status=t['status'], manifest_missing_reason=t.get('missing_reason'))
    if a.acquisition_dir:
        d = Path(a.acquisition_dir)
        r = json.loads((d / 'acquisition-result.json').read_text(encoding='utf-8'))
        comp = d / 'median-composite.tif'
        h = hashlib.sha256(comp.read_bytes()).hexdigest() if comp.exists() else None
        out.update(acquisition_result=(d / 'acquisition-result.json').as_posix(), acquisition_result_keys=sorted(r.keys()) if isinstance(r, dict) else None,
                   composite_path=comp.as_posix() if comp.exists() else None, composite_sha256=h)
print(json.dumps(out, indent=2))
