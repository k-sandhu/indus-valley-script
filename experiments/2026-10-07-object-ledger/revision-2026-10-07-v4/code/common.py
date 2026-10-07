"""Local input adapters and conservative identity/placeholder rules."""
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-07-object-ledger'
CENSUS = 'experiments/2026-10-06-evidence-census/synthesis/'
V6 = 'data/raw/2026-10-06-evidence-census/synthesis/main-2026-10-07-v6/'
MUSEUM = 'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07/'
HARP = 'experiments/2026-10-02-six-hour/harappa-object-frame/'
PATHS = {
    'lipi': 'data/normalized/lipi_observed_faces.jsonl',
    'mayig': 'data/normalized/mayig_faces.jsonl',
    'museum': MUSEUM + 'focused-records.json',
    'pairs': MUSEUM + 'paired-comparisons.json',
    'joins': V6 + 'confirmed-object-joins.json',
    'candidates': V6 + 'candidate-object-joins.json',
    'absent': V6 + 'absent-catalogue-identifiers.json',
    'sections': CENSUS + 'review/cisi1-class-split.csv',
    'catalogue': CENSUS + 'catalogue-coverage.csv',
    'corrections': CENSUS + 'batch-corrections.json',
    'harappa': HARP + 'annotated/results.json',
    'harappa_caption': HARP + 'figure4-caption-ledger.json',
    'harappa_correction': HARP + 'corrections/2026-10-02-scale-and-pagination/correction.json',
    'lothal': 'data/six-hour/lothal/table-coding/reviewed-pass.csv',
    'lothal_review': 'data/six-hour/lothal/independent-review/independent-first-pass.csv',
    'periods': 'experiments/2026-10-06-chronology-region/main-2026-10-07-v1/period_mapping.json',
    'external': 'experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad/site-rows.json',
    'external_sources': 'experiments/2026-10-06-evidence-census/sites-deep/d-finds-abroad/sources.json',
    'oxus': 'experiments/2026-10-02-source-recovery/oxus/observations.json',
    'coverage': 'experiments/2026-10-06-research-program/local-site-coverage.json',
}

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read(path):
    p = ROOT / path
    if p.suffix == '.csv':
        with p.open(encoding='utf-8-sig', newline='') as f:
            return list(csv.DictReader(f))
    if p.suffix == '.jsonl':
        return [json.loads(l) for l in p.read_text(encoding='utf-8-sig').splitlines() if l]
    return json.loads(p.read_text(encoding='utf-8-sig'))

def write(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def missing(v):
    return v is None or str(v).strip().casefold() in {'', '-', '--', '- -', 'none', 'unknown', 'others', '?'}

def cisi(v):
    m = re.fullmatch(r'([A-Za-z]+)[ -]*(\d+)(?:[A-C])?(?:\s*(?:bis|ter|quater))?', str(v).strip(), re.I)
    return f'{m[1].upper()}-{int(m[2])}' if m else None

def coarse(v):
    s = str(v).strip().casefold()
    if s.startswith(('seal:i', 'seal impression')) or s in {'sealing', 'sealings'}:
        return 'sealing'
    if s.startswith('seal'):
        return 'seal'
    if s.startswith(('tab', 'tablet')):
        return 'tablet'
    if s.startswith(('pot', 'post', 'pottery')):
        return 'pottery'
    return s

def site(v):
    return re.sub(r'[^a-z0-9]', '', str(v).casefold())

def rank(key):
    return hashlib.sha256(('object-ledger-20261007|' + str(key)).encode()).hexdigest(), str(key)

def round_robin(rows, grouping, key):
    buckets = defaultdict(list)
    for r in rows:
        buckets[grouping(r)].append(r)
    for b in buckets.values():
        b.sort(key=lambda r: rank(key(r)))
    for i in range(max((len(v) for v in buckets.values()), default=0)):
        for k in sorted(buckets, key=str):
            if i < len(buckets[k]):
                yield buckets[k][i]

def fresh(path, root):
    p = Path(path).resolve()
    allowed = root.resolve()
    if not p.is_relative_to(allowed) or p == allowed:
        raise ValueError(f'Output must be a new subdirectory of {allowed}')
    p.mkdir(parents=True, exist_ok=False)
    return p

def load_inputs():
    return {k: read(p) for k, p in PATHS.items()}

def candidate_frame(inputs):
    families = defaultdict(list)
    bases = defaultdict(set)
    for f in inputs['lipi']:
        families[f['object_family_id']].append(f)
        b = cisi(f['source_cisi'])
        if b:
            bases[b].add(f['object_family_id'])
    external = {'Persian Gulf', 'Mesopotamia', 'Iranian Plateau', 'Central Asia'}
    frame = {}
    dispositions = []
    for fam, faces in families.items():
        bs = {cisi(f['source_cisi']) for f in faces} - {None}
        b = next(iter(bs)) if len(bs) == 1 else None
        if len(bs) > 1 or (b and len(bases[b]) != 1):
            dispositions.append({'family': fam, 'reason': 'ambiguous catalogue bases or shared base across families'})
            continue
        is_external = any(f['region'] in external for f in faces)
        if not b and not is_external:
            dispositions.append({'family': fam, 'reason': 'no unambiguous published catalogue base for core filler'})
            continue
        key = b or f'LIPI-{fam}'
        f = faces[0]
        n = max(x['length'] for x in faces)
        length_bin = '0' if n == 0 else '1-2' if n <= 2 else '3-5' if n <= 5 else '6-9' if n <= 9 else '10+'
        damaged = any(x['has_unknown_sign'] or not x['complete_observed'] or str(x['metadata'].get('preservation', '')).casefold() not in {'complete', '', '-', '--'} for x in faces)
        frame[key] = {'key': key, 'catalogue_key': b, 'family': fam, 'site': f['site'], 'region': f['region'], 'type': coarse(f['object_type']), 'length_bin': length_bin, 'damaged': damaged, 'multi_face': len(faces) > 1, 'faces': faces}
    return frame, dispositions
