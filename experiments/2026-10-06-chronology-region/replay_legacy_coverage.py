"""Reproduce the four preserved caption coverage files in a fresh local raw path.

This uses the count-only part of verify_post_launch.py. It does not invoke that
checker's obsolete original-protocol preservation assumption or add a test.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import analyze as base
import verify_post_launch as legacy

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True); parser.add_argument('--raw-dir',required=True)
    args=parser.parse_args(); output=Path(args.output_dir).resolve(); local=Path(args.raw_dir).resolve()
    if not output.is_relative_to(base.RAW): raise ValueError('Unsuppressed legacy diagnostics stay in the assigned local raw directory.')
    if output.exists(): raise FileExistsError('Choose a fresh coverage output directory.')
    c=base.Corpus(); units=read(local/'harappa_units.json')['units']; membership=read(local/'external_membership.json')
    early=[]
    for name in ['type','type_length']:
        saved=read(local/f'early_{name}_draws.json')
        ga={tuple(r['cell']):r['indices'] for r in saved['early_cells']}; gb={tuple(r['cell']):r['indices'] for r in saved['later_cells']}
        budgets={k:min(len(ids),len(gb[k])) for k,ids in ga.items()}
        for population,cells in [('early',ga),('later',gb)]:
            for cell,ids in cells.items():
                group=[units[i] for i in ids]
                early.append({'adjustment':name,'population':population,'type':cell[0],'family_slots':cell[1] if len(cell)>1 else 'all',
                    'physical_families':len(ids),'text_components':len({u['text'] for u in group}),'faces':sum(u['faces'] for u in group),
                    'known_tokens':sum(u['known_tokens'] for u in group),'unreadable_tokens':sum(u['unreadable_tokens'] for u in group),'sample_family_budget':budgets[cell]})
    matched=set(membership['external_indices']); eligible={i for i,r in enumerate(c.rows) if r['region'] in base.EXTERNAL and r['clear']}
    regions=collections.defaultdict(list); stages=collections.defaultdict(list)
    for i,r in enumerate(c.rows):
        if r['region'] not in base.EXTERNAL: continue
        regions[(r['region'],r['type'])].append(i)
        stage='matched' if i in matched else 'clear_but_unmatched' if i in eligible else 'not_clear'
        stages[(stage,r['type'])].append(i)
    def counts(groups,dimensions):
        rows=[]
        for key,ids in sorted(groups.items()):
            for sign in ['090','091']:
                values=[c.rows[i]['seq'].count(sign) for i in ids]
                rows.append({**dict(zip(dimensions,key)),'sign':sign,'faces':len(ids),'physical_families':len({int(c.pid[i]) for i in ids}),
                    'known_tokens':sum(sum(s!='000' for s in c.rows[i]['seq']) for i in ids),'unreadable_tokens':sum(c.rows[i]['seq'].count('000') for i in ids),
                    'target_tokens':sum(values),'target_bearing_faces':sum(v>0 for v in values),'target_bearing_families':len({int(c.pid[i]) for i,v in zip(ids,values) if v})})
        return rows
    output.mkdir(parents=True)
    legacy.table(output/'external_region_type_counts.csv',counts(regions,['region','type']))
    legacy.table(output/'external_selection_counts.csv',counts(stages,['selection_stage','type']))
    legacy.table(output/'early_adjusted_denominators.csv',early)
    legacy.write(output/'coverage_checks.json',{'origin':'post-launch amendment','status':'Exploratory','source_run':local.name,
        'files':['external_region_type_counts.csv','external_selection_counts.csv','early_adjusted_denominators.csv'],
        'verification':'Count-only replay from saved populations; preservation checked by the second-amendment verifier.'})
    print(json.dumps({'legacy_coverage_files':4,'output_directory':str(output)}))

if __name__=='__main__': main()
