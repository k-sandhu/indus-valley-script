"""Reviewer recomputation of the two-coder agreement and the freeze timeline (aggregates and hashes only).

Reads pdf-2026-10-09-v1/mapping-v2-frozen.json (first coder) and the local merged second return, recomputes
the Mayig, Wells and Helsinki agreement figures with its own code, and checks the hash and time chain:
mapping hash in the freeze record, the git blob of the mapping at commit c6164ee, the packet manifest hashes
and the return file times. From the repository root:
    python -B -X utf8 experiments/2026-10-08-bonta-review/review-pdf/agreement_recheck.py
"""
import collections, datetime, hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OWN = ROOT / 'experiments/2026-10-08-bonta-review'
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rd = lambda p: json.loads(Path(p).read_text(encoding='utf-8'))

first = rd(OWN / 'pdf-2026-10-09-v1/mapping-v2-frozen.json')['rows']
second = rd(RAW / 'second-coder-v1/returns/coder2-merged.json')['rows']
assert [r['sign_id'] for r in first] == [r['sign_id'] for r in second]
ids = [r['sign_id'] for r in first]
well = lambda x: str(int(str(x).removeprefix('W'))).zfill(3)


def sets(rows, dom):
    if dom == 'mayig':
        return {r['sign_id']: set(r['mayig_candidates']) for r in rows}
    if dom == 'wells':
        return {r['sign_id']: {well(x) for x in r['wells_candidates']} for r in rows}
    return {r['sign_id']: {c['cell_id'] for c in r['helsinki_candidates']} for r in rows}


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca = collections.Counter(a for a, _ in pairs)
    cb = collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in ca) / n ** 2
    return n, po, pe, (po - pe) / (1 - pe)


out = {'status': 'Verified recomputation', 'domains': {}}
for dom in ('mayig', 'wells', 'helsinki'):
    A, B = sets(first, dom), sets(second, dom)
    exact = [i for i in ids if len(A[i]) == len(B[i]) == 1 and A[i] == B[i]]
    paired = [(next(iter(A[i])), next(iter(B[i]))) for i in ids if len(A[i]) == len(B[i]) == 1]
    n, po, pe, k = kappa(paired)
    out['domains'][dom] = {'targets': len(ids), 'exact_singleton': len(exact),
                           'overlap': sum(bool(A[i] & B[i]) for i in ids),
                           'disjoint_nonempty': sum(bool(A[i]) and bool(B[i]) and not A[i] & B[i] for i in ids),
                           'missing': sum(not A[i] or not B[i] for i in ids), 'paired_singletons': n,
                           'observed_agreement': round(po, 4), 'chance_agreement': round(pe, 4), 'kappa': round(k, 4)}
A, B = sets(first, 'mayig'), sets(second, 'mayig')
tt = lambda s: 'caption form' if s.startswith('U') else 'Table 18 drawing' if int(s[1:]) <= 65 else 'field or anchor target'
out['mayig_overlap_by_type'] = {t: [sum(bool(A[i] & B[i]) for i in ids if tt(i) == t), sum(tt(i) == t for i in ids)]
                                for t in ('Table 18 drawing', 'caption form', 'field or anchor target')}
both_high = [i for r1, r2, i in zip(first, second, ids) if r1['confidence'] == r2['confidence'] == 'high']
out['both_high'] = {'targets': len(both_high), 'exact_singleton': sum(len(A[i]) == len(B[i]) == 1 and A[i] == B[i] for i in both_high),
                    'not_exact': [i for i in both_high if not (len(A[i]) == len(B[i]) == 1 and A[i] == B[i])]}
out['second_confidence_counts'] = dict(collections.Counter(r['confidence'] for r in second))
out['disjoint_targets'] = [i for i in ids if A[i] and B[i] and not A[i] & B[i]]
out['first_missing_targets'] = [i for i in ids if not A[i]]

# Freeze chain
freeze = rd(OWN / 'pdf-2026-10-09-v1/mapping-freeze-v2.json')
mp = OWN / 'pdf-2026-10-09-v1/mapping-v2-frozen.json'
blob = subprocess.run(['git', 'show', 'c6164ee:experiments/2026-10-08-bonta-review/pdf-2026-10-09-v1/mapping-v2-frozen.json'],
                      cwd=ROOT, capture_output=True).stdout
commit_time = subprocess.run(['git', 'log', '-1', '--format=%ad', '--date=iso', 'c6164ee'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
manifest = rd(RAW / 'second-coder-v1/packet-manifest-v2.json')
bad = [f['path'] for f in manifest['files'] if sha(RAW / 'second-coder-v1' / f['path']) != f['sha256']]
mt = lambda p: datetime.datetime.fromtimestamp(Path(p).stat().st_mtime).isoformat(timespec='seconds')
out['freeze_chain'] = {
    'mapping_sha256_now': sha(mp), 'recorded_in_freeze_v2': freeze['sha256'], 'freeze_record_created_utc': freeze['created_utc'],
    'git_blob_sha256_at_c6164ee': hashlib.sha256(blob).hexdigest(), 'git_commit_c6164ee_time': commit_time,
    'registration_first_mapping_sha256': rd(OWN / 'two-coder-2026-10-09-v1/registration.json')['first_mapping_sha256'],
    'packet_manifest_files': len(manifest['files']), 'packet_hash_mismatches': bad,
    'packet_flags': {k: manifest[k] for k in ('contains_first_mapping', 'contains_author_values')},
    'mtimes_local': {'mapping-v2-frozen.json': mt(mp), 'packet-manifest-v2.json': mt(RAW / 'second-coder-v1/packet-manifest-v2.json'),
                     'return-template-v2.json': mt(RAW / 'second-coder-v1/return-template-v2.json'),
                     'coder2-part1.json': mt(RAW / 'second-coder-v1/returns/coder2-part1.json'),
                     'coder2-part2.json': mt(RAW / 'second-coder-v1/returns/coder2-part2.json'),
                     'coder2-merged.json': mt(RAW / 'second-coder-v1/returns/coder2-merged.json')}}
(Path(__file__).resolve().parent / 'agreement-recheck.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print(json.dumps(out, indent=1))
