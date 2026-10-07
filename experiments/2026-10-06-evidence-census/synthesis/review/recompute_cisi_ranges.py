"""Independent recomputation of the CISI 1 range comparison (reviewer script).

Reads only data/normalized/lipi_observed_faces.jsonl and the site-rows.json of batches B and C.
Does not import or reuse the synthesis builder. Writes a small JSON summary to stdout.
"""
import json, re, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LIPI = ROOT / 'data/normalized/lipi_observed_faces.jsonl'
BASE = ROOT / 'experiments/2026-10-06-evidence-census/sites-deep'


def load_rows(p):
    d = json.loads(p.read_text(encoding='utf-8-sig'))
    return d if isinstance(d, list) else (d.get('rows') or d.get('sites'))


def parse_range(text):
    m = re.fullmatch(r'\s*([A-Za-z]+)\s*(\d+)\s*[\u2013\u2014-]\s*(\d+)\s*', text)
    return (m[1], int(m[2]), int(m[3])) if m else None


def parse_key(value):
    m = re.fullmatch(r'\s*([A-Za-z]+)-?(\d+)\s*', str(value))
    return (m[1].casefold(), int(m[2])) if m else None


faces = [json.loads(l) for l in LIPI.read_text(encoding='utf-8-sig').splitlines() if l.strip()]
# index of all keys in the whole corpus, with the site labels they appear under
all_keys = collections.defaultdict(set)
all_keys_raw_unparsed = collections.Counter()
for f in faces:
    k = parse_key(f['source_cisi'])
    if k:
        all_keys[k].add(f['site'])
    else:
        all_keys_raw_unparsed[f['source_cisi']] += 1

ranges = []
for r in load_rows(BASE / 'b-gujarat-kutch-maharashtra/site-rows.json'):
    for c in r.get('cisi_coverage', []):
        if c.get('volume') == 'CISI1' and c.get('identifier_range'):
            ranges.append(dict(batch='B', site=r['canonical_name'], text=c['identifier_range'], slots=c['catalogue_object_slots'],
                               local_site=(r.get('local_corpus') or {}).get('site'), pages=c.get('page_range')))
for r in load_rows(BASE / 'c-north-india/site-rows.json'):
    c = r['cisi_coverage']
    if c.get('entry_range'):
        ranges.append(dict(batch='C', site=r['canonical_name'], text=c['entry_range'], slots=c['catalogue_objects'],
                           local_site=(r.get('local_corpus') or {}).get('site'), pages=c.get('page_range')))

out = []
tot = collections.Counter()
for rg in ranges:
    p = parse_range(rg['text'])
    prefix, lo, hi = p
    assert hi - lo + 1 == rg['slots'], (rg, 'endpoint arithmetic differs from stated slots')
    expected = {(prefix.casefold(), n) for n in range(lo, hi + 1)}
    # (1) key present anywhere in the corpus under the batch's local site label
    local_label = rg['local_site']
    site_keys = {parse_key(f['source_cisi']) for f in faces if f['site'] == local_label} - {None}
    # (2) key present anywhere in the corpus under any label
    any_keys = {k for k in expected if k in all_keys}
    # (3) alias prefix attempt: strip to numeric only compare within site
    present_site = expected & site_keys
    out.append(dict(batch=rg['batch'], site=rg['site'], range=rg['text'], entries=len(expected), local_site_label=local_label,
                    match_site=len(present_site), absent_site=len(expected - present_site),
                    match_any_site_label=len(any_keys), absent_any=len(expected - any_keys),
                    rescued_elsewhere=sorted([(k, sorted(all_keys[k])) for k in (expected - present_site) if k in all_keys])[:5]))
    tot['entries'] += len(expected); tot['match_site'] += len(present_site); tot['absent_site'] += len(expected - present_site)
    tot['match_any'] += len(any_keys)
    tot[rg['batch'] + '_entries'] += len(expected); tot[rg['batch'] + '_match'] += len(present_site)

for o in out:
    print(o['batch'], o['site'], o['range'], 'entries', o['entries'], 'label', o['local_site_label'], 'match', o['match_site'], 'absent', o['absent_site'],
          'match_any_label', o['match_any_site_label'], 'rescued_elsewhere_sample', o['rescued_elsewhere'])
print(dict(tot))
print('unparsed source_cisi raw values (count of faces):', sum(all_keys_raw_unparsed.values()), 'distinct', len(all_keys_raw_unparsed), list(all_keys_raw_unparsed.items())[:15])
