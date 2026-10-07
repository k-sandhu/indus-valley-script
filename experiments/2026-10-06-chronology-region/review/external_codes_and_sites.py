"""Reviewer aggregates on the external set: human-figure Wells codes and site composition.

Counts only (no sequences, no per-object scores). Uses the Mayig schema descriptions to list Wells
codes whose class description names a person/man/human figure, and tabulates external versus core
known-token counts for each such code that occurs at least once. Also tabulates external faces by
region and site, and the site/type of the circular-seal faces.
"""
import json, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
rows = [json.loads(l) for l in open(ROOT / 'data/normalized/lipi_observed_faces.jsonl', encoding='utf-8')]
schema = json.load(open(ROOT / 'data/normalized/mayig_sign_schema.json', encoding='utf-8'))['signs']
EXT = ['Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia']
CORE = ['Inter-Riverine', 'Lower Indus', 'Gujarat/Kutch', 'Eastern Headwaters', 'Upper Indus']
ext = collections.Counter(); core = collections.Counter()
for r in rows:
    tgt = ext if r['region'] in EXT else core if r['region'] in CORE else None
    if tgt is None: continue
    for s in r['signs_reading_rtl']:
        if s != '000': tgt[s] += 1
ne, nc = sum(ext.values()), sum(core.values())
human = {}
for p, v in schema.items():
    d = re.sub(r'[-]', '', v['description']).lower()
    if re.search(r'\b(person|man|human|figure|persons|people)\b', d):
        for w in v['wells_graphemes']: human[w[1:]] = p
table = [{'wells': w, 'mayig_class': p, 'external_tokens': ext[w], 'core_tokens': core[w], 'external_percent': round(100 * ext[w] / ne, 3), 'core_percent': round(100 * core[w] / nc, 3)}
         for w, p in sorted(human.items()) if ext[w]]
sites = {reg: dict(collections.Counter(r['site'] for r in rows if r['region'] == reg)) for reg in EXT}
baluch = {'Nindowari-damb', 'Sibri', 'Miri Qalat', 'Murda Sang', 'Ornach area'}
out = {'status': 'Reviewer check, not a package result', 'external_known_tokens': ne, 'core_known_tokens': nc,
       'human_figure_wells_codes_with_external_tokens': table,
       'top_external_codes': [{'code': s, 'external_tokens': n, 'core_tokens': core[s], 'core_percent': round(100 * core[s] / nc, 3)} for s, n in ext.most_common(10)],
       'external_faces_by_region_and_site': sites,
       'iranian_plateau_faces_from_baluchistan_or_makran_sites': sum(n for s, n in sites['Iranian Plateau'].items() if s in baluch), 'iranian_plateau_faces': sum(sites['Iranian Plateau'].values()),
       'external_faces_by_object_type': dict(collections.Counter(r['object_type'] for r in rows if r['region'] in EXT))}
Path(__file__).with_name('external_codes_and_sites.json').write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps({k: v for k, v in out.items() if k not in ('external_faces_by_region_and_site',)}, indent=1, ensure_ascii=False)[:3500])
