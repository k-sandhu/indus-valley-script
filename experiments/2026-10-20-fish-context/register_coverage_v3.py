"""Repair missing-value handling with the project's canonical inventory rules."""
from collections import Counter
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
spec=importlib.util.spec_from_file_location('fish_study',HERE/'study.py')
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
spec2=importlib.util.spec_from_file_location('inventory_rules',ROOT/'experiments/2026-10-12-data-inventory/coverage.py')
inventory=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(inventory)


def main():
    dest=HERE/'register-v3';dest.mkdir(exist_ok=False)
    local=s.RAW/'register-v3';local.mkdir(exist_ok=False)
    objects=s.read_rows(s.RAW/'register-v2/objects.jsonl')
    fields=[('material','material'),('findspot_area','area-section'),('house_or_block','block-house'),
            ('room_or_grid','room-grid'),('depth','depth'),('period','period'),('phase','phase'),
            ('width_mm','horizontal(mm)'),('height_mm','vertical(mm)'),('thickness_mm','thickness(mm)')]
    coverage=Counter();changes=Counter()
    for r in objects:
        for field,key in fields:
            vals=sorted({inventory.norm(m.get(key)) for m in r['metadata_by_face'].values() if inventory.usable(key,m.get(key))})
            before=r['field_status'][field]['values']
            if vals!=before:changes[field]+=1
            rec={'values':vals,'value_status':'catalogued' if vals else 'unknown',
                 'source':'pinned observational metadata; primary table assertions remain separate'}
            if not vals:rec['unknown_reason']='not-reported-in-held-export'
            r['field_status'][field]=rec
            if vals:coverage[field]+=1
        r['record_version']='fish-context-register-v3'
    s.dump_jsonl(local/'objects.jsonl',objects)
    out={'objects':len(objects),'metadata_coverage':dict(coverage),'objects_changed_from_v2':dict(changes),
         'reason':'v2 counted the placeholder - - as a depth. v3 uses the canonical inventory norm() and usable() rules for every field.',
         'previous_preserved':'experiments/2026-10-20-fish-context/register-v2/coverage.json',
         'assertions':'data/raw/2026-10-20-fish-context/register-v2/assertions.jsonl',
         'source_controls':'data/raw/2026-10-20-fish-context/register-v2/source-controls.jsonl',
         'hashes':{str(p.relative_to(ROOT)):s.sha256(p) for p in [Path(__file__),ROOT/'experiments/2026-10-12-data-inventory/coverage.py',local/'objects.jsonl']}}
    s.write_json(dest/'coverage.json',out)
    print(json.dumps(out,indent=2))


if __name__=='__main__':main()
