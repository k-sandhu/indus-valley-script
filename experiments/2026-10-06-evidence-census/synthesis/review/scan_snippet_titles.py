"""Reviewer scan: source-ledger titles that look like copied search-result prose.

Heuristics (any one flags a title): length over 180 characters; starts with a lowercase letter or a bullet;
contains an ellipsis; has two or more sentence breaks ('. ' followed by a capital letter).
Prints counts, record ids and the first 45 characters only, so the scan itself does not re-copy text.
"""
import json, glob, re, collections, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
base = ROOT / 'experiments/2026-10-06-evidence-census'
files = sorted(glob.glob(str(base / 'sites-deep/**/*sources.json'), recursive=True)) + sorted(glob.glob(str(base / 'collections-and-datasets/**/*sources.json'), recursive=True)) + sorted(glob.glob(str(base / 'sites-and-publications/**/*sources.json'), recursive=True))
flags = []
tot = collections.Counter()
for f in files:
    d = json.loads(Path(f).read_text(encoding='utf-8-sig'))
    ss = d if isinstance(d, list) else d.get('sources', [])
    rel = Path(f).relative_to(base).as_posix()
    for s in ss:
        if not isinstance(s, dict):
            continue
        t = s.get('title')
        if not isinstance(t, str):
            continue
        tot[rel] += 1
        why = []
        if len(t) > 180: why.append('len>180')
        if re.match(r'^[a-z\u2022\-\*]', t.strip()): why.append('starts-lowercase-or-bullet')
        if '...' in t or '\u2026' in t: why.append('ellipsis')
        if len(re.findall(r'[a-z0-9\)\]]\.\s+[A-Z]', t)) >= 2: why.append('multi-sentence')
        if why:
            flags.append((rel, s.get('id', s.get('source_id')), len(t), len(t.split()), '+'.join(why), t[:45].replace('\n', ' ')))
by = collections.Counter(f[0] for f in flags)
print('files scanned', len(files), 'records with titles', sum(tot.values()))
for k, v in sorted(by.items()):
    print(f'{v:4d} flagged of {tot[k]:4d}  {k}')
print('total flagged', len(flags))
if len(sys.argv) > 1 and sys.argv[1] == 'list':
    for f in flags:
        print(f[0].split('/')[0][:4], f[0].split('/')[-1][:22].ljust(22), str(f[1])[:26].ljust(26), f[2], f[3], f[4], '|', f[5])
