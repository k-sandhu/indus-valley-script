"""Exploratory area/source corrections after REVIEW.md; small compressed references."""
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import time
import numpy as np
from scipy.stats import rankdata, false_discovery_control, spearmanr
import analyze as main
import sensitivity

EXTENTS = [
    ('Harappa', 100, 'Harappa', 'visible mounds', 'about', None),
    ('Mohenjo-daro', 400, 'Mohenjo daro', 'third-millennium settlement bounding extent', 'at least', [2000, 2000]),
    ('Rakhigarhi', 100, 'Rakhigarhi', 'surface extent', 'over', None),
    ('Lothal', 8, 'Lothal', 'Integration-era urban enclosure', 'over', None),
    ('Lothal', 12, 'Lothal', 'mound-base bounding rectangle', 'bounding conversion', [400, 300]),
    ('Nausharo', 6, 'Nausharo', 'attested inhabited area', 'about; original extent suggested larger', None),
    ('Banawali', 16, 'Banawali', 'ruins bounding square', 'bounding conversion', [400, 400]),
    ('Chanhu-daro', 3, 'Chanu daro', 'visible surface bounding rectangle', 'bounding conversion', [200, 150]),
    ('Kot-Diji', 2.4, 'Kot diji', 'mound bounding rectangle', 'bounding conversion', [200, 120]),
    ('Surkotada', .72, 'Surkotada', 'fortification bounding rectangle', 'bounding conversion', [120, 60]),
]
INPUT_TABLE = main.OWN / 'site-extents-review-2026-10-07.json'
SEED = 2026100704
B = 9999


def fresh(path):
    if path.exists():
        raise FileExistsError(f'Preserve existing output: {path}')


def prepare():
    fresh(INPUT_TABLE)
    original = json.loads((main.OWN / 'site-table.json').read_text(encoding='utf-8'))
    sites = deepcopy(original['sites'])
    by = {s['site']: s for s in sites}
    by['Banawali'] = {'site': 'Banawali', 'area_reference': 16, 'area_min': 16, 'area_max': 16,
                      'site_type': 'town, provisional', 'sources': [],
                      'type_basis': 'Vidale calls it an urban site; town is a provisional 16-ha category.'}
    witness = main.RAW / 'source-downloads-2026-10-07-02/kenoyer2005.txt'
    text = witness.read_text(encoding='utf-8')
    for site, area, heading, definition, qualifier, dims in EXTENTS:
        marker = heading + ' di Massimo Vidale'
        offset = text.find(marker)
        assert offset >= 0, marker
        item = {'id': 'K2005', 'author_of_section': 'Massimo Vidale', 'area': area,
                'location': f'Vidale section {heading}; {definition}', 'definition': definition,
                'qualifier': qualifier, 'section_character_offset_in_existing_text': offset,
                'witness': witness.relative_to(main.ROOT).as_posix()}
        if dims:
            item['bounding_dimensions_metres'] = dims
            assert abs(dims[0] * dims[1] / 10000 - area) < 1e-12
        by[site]['sources'].append(item)
        by[site]['area_min'] = min(by[site]['area_min'], area)
        by[site]['area_max'] = max(by[site]['area_max'], area)
    for site in ['Rakhigarhi', 'Ganweriwala']:
        by[site]['sources'].append({'id': 'K2005', 'area': 80,
                                   'location': 'Kenoyer settlement-hierarchy paragraph, first tier',
                                   'definition': 'settlement hierarchy', 'qualifier': 'estimate'})
    sites.append(by['Banawali'])
    base = {s['site']: s['area_reference'] for s in sites}
    entries = dict(base)
    for site, area, heading, definition, qualifier, dims in EXTENTS:
        if site == 'Lothal' and area == 12:
            continue
        entries[site] = area
    main.write(INPUT_TABLE, {'status': 'Exploratory', 'stage': 'post-review amendment',
        'frozen_table_sha256': main.sha(main.OWN / 'site-table.json'),
        'protocol_sha256': main.sha(main.OWN / 'PROTOCOL.md'),
        'source_witness_sha256': main.sha(witness), 'units': 'hectares',
        'notes': 'Lowest/highest printed numerical anchors mix stated extent definitions; open bounds have no finite established maximum. Rakhigarhi early 10-15 ha excluded; Nausharo hypothetical double extent excluded.',
        'sites': sites, 'vectors': {'expanded_reference': base, 'site_entries': entries,
            'lowest_printed_anchor': {s['site']: s['area_min'] for s in sites},
            'highest_printed_anchor': {s['site']: s['area_max'] for s in sites}}})
    print('Prepared 19-site supplementary table before the new area computation.')


def run(name):
    out = main.OWN / name
    raw = main.RAW / name
    fresh(out); fresh(raw)
    out.mkdir(); raw.mkdir()
    start = time.time()
    table = json.loads(INPUT_TABLE.read_text(encoding='utf-8'))
    rows = [json.loads(line) for line in main.INPUT.read_text(encoding='utf-8').splitlines()]
    groups, principal, seals, _ = main.grouping(rows)
    signs = json.loads((main.OWN / 'run-2026-10-07-01/input-summary.json').read_text())['top_signs']
    rr = [r for r in principal if any(s != '000' for s in r['signs_reading_rtl'])]
    Y, N = main.counts(rr, signs)
    strata = main.blocks([r['object_type'] for r in rr])
    P = np.zeros_like(Y)
    for ix in strata:
        P[ix] = Y[ix].sum(0) / N[ix].sum()
    D = Y - N[:, None] * P
    names = sorted({r['site'] for r in rr})
    labels = np.array([names.index(r['site']) for r in rr])
    ns = np.bincount(labels, minlength=len(names))
    settings = []
    for vector, areas in table['vectors'].items():
        for cohort, minimum, omitted in [('at_least_3', 3, set()), ('at_least_20', 20, set()),
                                        ('without_two_cities', 3, {'Harappa', 'Mohenjo-daro'})]:
            selected = [s for s in names if s in areas and s not in omitted and ns[names.index(s)] >= minimum]
            indices = np.array([names.index(s) for s in selected])
            ar = rankdata(np.log2([areas[s] for s in selected])); ar -= ar.mean()
            settings.append((vector, cohort, selected, indices, ar))

    def statistics(lab):
        totals = np.column_stack([np.bincount(lab, weights=D[:, j], minlength=len(names))
                                  for j in range(len(signs))])
        denoms = np.bincount(lab, weights=N, minlength=len(names))
        residuals = totals / denoms[:, None]
        values = []
        for vector, cohort, selected, ix, ar in settings:
            ranks = rankdata(residuals[ix], axis=0); ranks -= ranks.mean(0)
            denom = np.sqrt((ar @ ar) * (ranks * ranks).sum(0))
            values.append(np.divide(ar @ ranks, denom, out=np.zeros(len(signs)), where=denom > 0))
        return np.array(values)

    observed = statistics(labels)
    rng = np.random.default_rng(SEED)
    null = np.empty((B, len(settings), len(signs)))
    for b in range(B):
        lab = main.shuffle(labels, strata, rng)
        if b < 3:
            assert all(np.array_equal(np.sort(lab[ix]), np.sort(labels[ix])) for ix in strata)
        null[b] = statistics(lab)
    comparisons = []
    for j, (vector, cohort, selected, ix, ar) in enumerate(settings):
        tests = [dict(sign=s, **main.tail(observed[j, k], null[:, j, k], True)) for k, s in enumerate(signs)]
        for t, q in zip(tests, main.bh([t['p'] for t in tests])):
            t['q_bh_ten_signs'] = q
        independent = sensitivity.correlations(Y, N, N[:, None] * P, labels, ix,
                                               [table['vectors'][vector][s] for s in selected])
        assert np.allclose(independent, observed[j], rtol=0, atol=1e-14)
        comparisons.append({'vector': vector, 'cohort': cohort, 'sites': selected,
            'independent_sites': len(selected), 'readable_objects': int(ns[ix].sum()),
            'readable_tokens': int(N[np.isin(labels, ix)].sum()),
            'areas_ha': [table['vectors'][vector][s] for s in selected], 'tests': tests})
    flat = [t for c in comparisons for t in c['tests']]
    for t, q in zip(flat, false_discovery_control([t['p'] for t in flat], method='bh')):
        t['q_bh_all_120_new_comparisons'] = float(q)
    np.savez_compressed(raw / 'area_references.npz', values=null)
    main.write(out / 'area.json', {'status': 'Exploratory', 'stage': 'post-review amendment',
        'seed': SEED, 'permutations': B, 'signs': signs, 'blocks': len(strata),
        'movable_objects': sum(len(ix) for ix in strata if len(ix) > 1), 'comparisons': comparisons})
    bull1 = Counter(r['symbol'] for r in rows if r['symbol'].startswith('Bull1'))
    bull_i = Counter(r['symbol'] for r in rows if r['symbol'].startswith('Bull:i'))
    gaur = [r for r in rows if r['symbol'] == 'Gaur']
    salut = [r for r in rows if r['site'] == 'Salut']
    main.write(raw / 'salut-rows.json', salut)
    main.write(out / 'motif-mapping.json', {'status': 'Exploratory', 'stage': 'post-review amendment',
        'bull1_prefix_face_counts': dict(sorted(bull1.items())), 'pooled_as': 'unicorn',
        'bull_i_face_counts_unpooled': dict(sorted(bull_i.items())),
        'bull_i_rare_clean_objects': sum(main.motif(r['symbol']) in bull_i and r['complete_observed'] and
            r['single_line'] and r['direction'] in {'R/L', 'L/R'} and r['signs_reading_rtl'] and
            '000' not in r['signs_reading_rtl'] for r in seals),
        'gaur_faces': len(gaur), 'gaur_faces_with_trough': sum(r['metadata'].get('cult') == 'Trough' for r in gaur),
        'bull1_cult_counts': dict(Counter(r['metadata'].get('cult') for r in rows if r['symbol'].startswith('Bull1'))),
        'salut_face_count': len(salut),
        'salut_aggregate': [dict(site=r['site'], object_type=r['object_type'], motif=r['symbol'],
                               cult=r['metadata'].get('cult'), positions=len(r['signs_reading_rtl'])) for r in salut],
        'support': ['O2019 Table 9: 1045 unicorns / 1385 seal symbols, 82 short-horned bulls',
                    'FS2016 printed pp.116-117/Fig.9: Bos gaurus at a trough; ST1 seal and sherd'],
        'limitation': 'Corroborating counts/context do not replace an image-checked codebook. Salūt TAG Elep/two-sign record disagrees with the published two-bison sherd/three-or-four-sign description.'})
    source = main.OWN / 'exploratory-2026-10-07-01/results.json'
    relabelled = json.loads(source.read_text(encoding='utf-8'))
    assert relabelled['motif_length_conditioned']['status'] == 'Frozen evaluation'
    relabelled['motif_length_conditioned']['status'] = 'Exploratory'
    main.write(out / 'results-corrected-label.json', relabelled)
    main.write(out / 'summary.json', {'status': 'Exploratory', 'stage': 'post-review amendment',
        'input_sha256': main.sha(main.INPUT), 'protocol_sha256': main.sha(main.OWN / 'PROTOCOL.md'),
        'supplementary_table_sha256': main.sha(INPUT_TABLE),
        'frozen_table_sha256': main.sha(main.OWN / 'site-table.json'), 'code_sha256': main.sha(__file__),
        'inherited_code_sha256': main.sha(main.OWN / 'analyze.py'),
        'corrected_label_source_sha256': main.sha(source),
        'reference_sha256': main.sha(raw / 'area_references.npz'),
        'output_hashes': {p.name: main.sha(p) for p in out.glob('*.json')},
        'runtime_seconds': time.time() - start})
    print('Finished', name, 'seconds', round(time.time() - start, 2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--run')
    args = parser.parse_args()
    if args.prepare == bool(args.run):
        raise ValueError('Choose exactly --prepare or --run <fresh-name>.')
    prepare() if args.prepare else run(args.run)
