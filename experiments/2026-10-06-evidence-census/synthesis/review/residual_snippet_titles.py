"""Reviewer scan: IDs of source-ledger titles that still look like copied search-result prose.

Strong indicators (any one): length over 150 characters with two or more sentence breaks; length over
60 characters starting with a lowercase letter or bullet (a mid-sentence fragment); length over 250.
Writes only file, record id, character count, word count and indicator names to
synthesis/review/residual-snippet-title-ids.json. It does not write the title text.
"""
import json, glob, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
base = ROOT / 'experiments/2026-10-06-evidence-census'
out = []
seen = set()
for f in sorted(glob.glob(str(base / 'sites-deep/**/*sources.json'), recursive=True)) + sorted(glob.glob(str(base / 'collections-and-datasets/**/*sources.json'), recursive=True)):
    rel = Path(f).relative_to(base).as_posix()
    d = json.loads(Path(f).read_text(encoding='utf-8-sig'))
    ss = d if isinstance(d, list) else d.get('sources', [])
    for s in ss:
        if not isinstance(s, dict) or not isinstance(s.get('title'), str):
            continue
        t = s['title']
        why = []
        sentences = len(re.findall(r'[a-z0-9\)\]\u00b2]\.\s+[A-Z]', t))
        if len(t) > 150 and sentences >= 2: why.append('multi_sentence_over_150')
        if len(t) > 60 and re.match(r'^[a-z\u2022\-\*]', t.strip()): why.append('mid_sentence_fragment_over_60')
        if len(t) > 250: why.append('over_250')
        if why:
            out.append({'file': rel, 'record_id': s.get('id', s.get('source_id')), 'title_characters': len(t), 'title_words': len(t.split()), 'indicators': why,
                        'access_field': s.get('access', s.get('access_state', s.get('access_status')))})
summary = collections.Counter(o['file'] for o in out)
Path(ROOT / 'experiments/2026-10-06-evidence-census/synthesis/review/residual-snippet-title-ids.json').write_text(
    json.dumps({'rule': 'IDs only; no title text. Strong snippet indicators in tracked source ledgers after the coordinator trim.',
                'records': len(out), 'by_file': dict(summary), 'items': out}, indent=1) + '\n', encoding='utf-8')
print(len(out)); print(dict(summary))
acc = collections.Counter(str(o['access_field'])[:40] for o in out)
print(acc.most_common(8))
