"""Recount F-0027 (identical complete texts among long seal texts) from the protocol text alone.

The population follows experiments/2026-10-12-seal-text-identity/PROTOCOL.md, "Population", and imports
nothing from that package. It is a re-implementation, not a blind one: the population function at the top of
the package's analysis.py was read while looking for its output path. Sites outside South Asia are fixed here from the export's
region labels: Persian Gulf, Mesopotamia and Central Asia, plus the two Iranian sites Susa and Luristan;
Balochistan sites in the "Iranian Plateau" region stay in. Writes a new run directory and compares the
counts with the frozen summary. Usage, from the repository root:

    python experiments/2026-10-15-route-test/reproduce-f0027/recount.py \
        --faces <path to data/normalized/lipi_observed_faces.jsonl> \
        --out experiments/2026-10-15-route-test/reproduce-f0027/run-2026-10-15
"""
import argparse
import hashlib
import json
from collections import Counter
from math import comb
from pathlib import Path

FROZEN = Path('experiments/2026-10-12-seal-text-identity/run-2026-10-12/summary.json')
EXPECTED_FACES_SHA256 = '1220f5591a42abe7c6696ac014aba90e7c49fdce6b0ccba0b85bb45f950c30db'
OUTSIDE_REGIONS = {'Persian Gulf', 'Mesopotamia', 'Central Asia'}
OUTSIDE_SITES = {'Susa', 'Luristan'}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def population(faces, drop_blank_code=False):
    chosen = {}
    for f in faces:
        signs = f['signs_reading_rtl']
        if not f['object_type'].startswith('SEAL'):
            continue
        if not (f['complete_observed'] and f['single_line'] and not f['has_unknown_sign'] and len(signs) >= 2):
            continue
        if drop_blank_code and '000' in signs:
            continue
        if f['region'] in OUTSIDE_REGIONS or f['site'] in OUTSIDE_SITES or f['site'] in ('Unknown', '', None):
            continue
        family = f['object_family_id']
        if family not in chosen or float(f['record_id']) < float(chosen[family]['record_id']):
            chosen[family] = f
    return list(chosen.values())


def by_length(seals):
    rows = {}
    for length in sorted({len(s['signs_reading_rtl']) for s in seals}):
        texts = Counter(tuple(s['signs_reading_rtl']) for s in seals if len(s['signs_reading_rtl']) == length)
        rows[str(length)] = dict(seals=sum(texts.values()),
                                 observed_identical_pairs=sum(comb(k, 2) for k in texts.values()))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--faces', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    faces_hash = sha256(args.faces)
    faces = [json.loads(line) for line in open(args.faces, encoding='utf-8')]
    frozen = json.loads(FROZEN.read_text(encoding='utf-8'))['S3_whole_text_reuse']['by_length']
    frozen_counts = {k: dict(seals=v['seals'], observed_identical_pairs=v['observed_identical_pairs'])
                     for k, v in frozen.items()}

    variants = {}
    for name, drop in (('protocol_text', False), ('protocol_text_without_code_000', True)):
        rows = by_length(population(faces, drop))
        long_rows = {k: v for k, v in rows.items() if int(k) >= 6}
        variants[name] = dict(
            eligible_seals=sum(v['seals'] for v in rows.values()),
            seals_six_or_more=sum(v['seals'] for v in long_rows.values()),
            identical_pairs_six_or_more=sum(v['observed_identical_pairs'] for v in long_rows.values()),
            identical_pairs_four_or_more=sum(v['observed_identical_pairs'] for k, v in rows.items() if int(k) >= 4),
            by_length=rows,
            lengths_differing_from_frozen=sorted((k for k in set(rows) | set(frozen_counts)
                                                  if rows.get(k) != frozen_counts.get(k)), key=int))
    result = dict(
        finding='F-0027', date='2026-10-15',
        claim='No two of the 445 seals with six or more signs shared their complete text.',
        frozen_endpoint=str(FROZEN.as_posix()) + '#/S3_whole_text_reuse/by_length',
        frozen_endpoint_sha256=sha256(FROZEN),
        faces_sha256=faces_hash, faces_hash_matches_recorded=faces_hash == EXPECTED_FACES_SHA256,
        recount_sha256=sha256(__file__),
        frozen=dict(seals_six_or_more=sum(v['seals'] for k, v in frozen_counts.items() if int(k) >= 6),
                    identical_pairs_six_or_more=sum(v['observed_identical_pairs'] for k, v in frozen_counts.items()
                                                    if int(k) >= 6),
                    by_length=frozen_counts),
        recount=variants)
    (out/'recount.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    for name, v in variants.items():
        print(name, v['eligible_seals'], v['seals_six_or_more'], v['identical_pairs_six_or_more'],
              v['identical_pairs_four_or_more'], 'differs at lengths', v['lengths_differing_from_frozen'])
    print('frozen', result['frozen']['seals_six_or_more'], result['frozen']['identical_pairs_six_or_more'])


if __name__ == '__main__':
    main()
