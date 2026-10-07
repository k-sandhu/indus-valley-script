"""Current revision audit; historical metadata is checked against exact archives."""
import argparse
from collections import Counter
import json
from pathlib import Path
import numpy as np
from scipy.stats import false_discovery_control, spearmanr
import analyze as main
import second_followup as revision


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', default='post-review-2026-10-07-01')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    destination = (main.OWN / args.output).resolve()
    if destination.parent != main.OWN or destination.exists():
        raise ValueError('Choose a fresh check filename in the owned directory.')
    out = main.OWN / args.run
    raw = main.RAW / args.run
    result = json.loads((out / 'summary.json').read_text())
    checks = []

    def check(name, value):
        checks.append({'check': name, 'passed': bool(value)})
        if not value:
            raise AssertionError(name)

    for key, path in [('input_sha256', main.INPUT), ('protocol_sha256', main.OWN / 'PROTOCOL.md'),
                      ('supplementary_table_sha256', revision.INPUT_TABLE),
                      ('frozen_table_sha256', main.OWN / 'site-table.json'),
                      ('code_sha256', Path(revision.__file__)),
                      ('inherited_code_sha256', main.OWN / 'analyze.py')]:
        check(key, main.sha(path) == result[key])
    old_protocol = main.OWN / 'pre-second-followup-2026-10-07/PROTOCOL.md'
    check('original protocol preserved as exact prefix',
          (main.OWN / 'PROTOCOL.md').read_bytes().startswith(old_protocol.read_bytes()))
    check('original protocol hash matches original endpoint', main.sha(old_protocol) ==
          json.loads((main.OWN / 'run-2026-10-07-01/input-summary.json').read_text())['protocol_sha256'])
    historical = json.loads((main.OWN / 'FILE-MANIFEST-RECOVERY-2026-10-07.json').read_text())
    mutable = {'PROTOCOL.md', 'README.md', 'REPORT.md', 'RETROSPECTIVE.md',
               'registry-entry.json', 'sources.json', 'SOURCE-NOTES.md'}
    skipped_plotting = 0
    checked_history = 0
    for item in historical['files']:
        if item.get('sha256') is None:
            continue
        if item['plot_dependency']:
            skipped_plotting += 1
            continue  # do not open/hydrate the known online-only install
        path = main.ROOT / item['path']
        if path.parent == main.OWN and path.name in mutable:
            path = main.OWN / 'pre-second-followup-2026-10-07' / path.name
        elif path.name == 'checks-post-launch-final-2026-10-07-02.json':
            path = main.OWN / 'checks-post-launch-2026-10-07-02.json'
        check('historical artifact ' + item['path'], main.sha(path) == item['sha256'])
        checked_history += 1
    check('exactly the known online-only plotting payload excluded', skipped_plotting == 1670)
    for name, digest in result['output_hashes'].items():
        check('new output hash ' + name, main.sha(out / name) == digest)
    reference_path = raw / 'area_references.npz'
    check('compressed reference hash', main.sha(reference_path) == result['reference_sha256'])
    with np.load(reference_path, allow_pickle=False) as archive:
        null = archive['values']
    check('finite reference shape', null.shape == (9999, 12, 10) and np.isfinite(null).all())
    area = json.loads((out / 'area.json').read_text())
    flat = []
    for j, cohort in enumerate(area['comparisons']):
        ps = []
        for k, test in enumerate(cohort['tests']):
            count = int(np.sum(np.abs(null[:, j, k]) >= abs(test['observed']) - 1e-12))
            expected = (count + 1) / (len(null) + 1)
            check(f'tail {j}:{k}', count == test['exceedances'] and expected == test['p'])
            ps.append(expected); flat.append(test)
        q = false_discovery_control(ps, method='bh')
        check('BH ten signs ' + str(j), np.allclose(q, [t['q_bh_ten_signs'] for t in cohort['tests']], rtol=0, atol=1e-15))
    q = false_discovery_control([t['p'] for t in flat], method='bh')
    check('BH all 120 comparisons', np.array_equal(q, [t['q_bh_all_120_new_comparisons'] for t in flat]))
    rows = [json.loads(l) for l in main.INPUT.read_text(encoding='utf-8').splitlines()]
    groups, principal, seals, _ = main.grouping(rows)
    rr = [r for r in principal if any(s != '000' for s in r['signs_reading_rtl'])]
    check('one selected readable object per physical family', len(rr) == len({r['object_family_id'] for r in rr}))
    signs = area['signs']
    count = [Counter(s for s in r['signs_reading_rtl'] if s != '000') for r in rr]
    Y = np.array([[c[s] for s in signs] for c in count], float)
    N = np.array([sum(c.values()) for c in count], float)
    keys = [r['object_type'] for r in rr]
    blocks = [np.array([i for i, key in enumerate(keys) if key == value]) for value in sorted(set(keys))]
    D = Y.copy()
    for ix in blocks:
        D[ix] -= N[ix, None] * (Y[ix].sum(0) / N[ix].sum())
    names = sorted({r['site'] for r in rr})
    lab = np.array([names.index(r['site']) for r in rr])

    def independent(lab):
        statistics = []
        for cohort in area['comparisons']:
            ix = [names.index(s) for s in cohort['sites']]
            residuals = np.array([D[lab == value].sum(0) / N[lab == value].sum() for value in ix])
            statistics.append([spearmanr(np.log2(cohort['areas_ha']), residuals[:, k]).statistic
                               for k in range(len(signs))])
        return np.array(statistics)

    check('observed correlations with independent SciPy ranks', np.allclose(independent(lab),
          [[t['observed'] for t in c['tests']] for c in area['comparisons']], rtol=0, atol=1e-14))
    rng = np.random.default_rng(2026100704)
    for b in range(3):
        shuffled = lab.copy()
        for ix in blocks:
            if len(ix) > 1:
                shuffled[ix] = rng.permutation(lab[ix])
        check('whole-object block labels preserved ' + str(b),
              all(Counter(shuffled[ix]) == Counter(lab[ix]) for ix in blocks))
        check('independent first reference ' + str(b), np.allclose(independent(shuffled), null[b], rtol=0, atol=1e-14))
    table = json.loads(revision.INPUT_TABLE.read_text())
    check('supplemental source table has 19 sites', len(table['sites']) == 19)
    for site in table['sites']:
        if site['site'] in {'Banawali', 'Harappa', 'Mohenjo-daro', 'Lothal', 'Nausharo', 'Rakhigarhi'}:
            check('added source anchor ' + site['site'], any(s['id'] == 'K2005' and 'section_character_offset_in_existing_text' in s for s in site['sources']))
        for source in site['sources']:
            if 'bounding_dimensions_metres' in source:
                h, v = source['bounding_dimensions_metres']
                check('area conversion ' + site['site'], abs(h * v / 10000 - source['area']) < 1e-12)
    source = json.loads((main.OWN / 'exploratory-2026-10-07-01/results.json').read_text())
    copied = json.loads((out / 'results-corrected-label.json').read_text())
    check('nested corrected label', copied['motif_length_conditioned']['status'] == 'Exploratory')
    copied['motif_length_conditioned']['status'] = 'Frozen evaluation'
    check('corrected copy changes exactly one field', copied == source)
    mapping = json.loads((out / 'motif-mapping.json').read_text())
    check('14 Bull1 code variants', len(mapping['bull1_prefix_face_counts']) == 14)
    check('separate Bull:i codes and counts', mapping['bull_i_face_counts_unpooled'] == {'Bull:i': 1, 'Bull:i:J': 3, 'Bull:i:S': 1})
    check('Gaur trough count', sum(r['symbol'] == 'Gaur' and r['metadata'].get('cult') == 'Trough' for r in rows) == mapping['gaur_faces_with_trough'] == 96)
    check('Salūt exact-site selection', mapping['salut_face_count'] == 2)
    check('three separate clean rare objects', mapping['bull_i_rare_clean_objects'] == 3)
    maintenance = json.loads((main.OWN / 'revision-maintenance-2026-10-07.json').read_text())
    check('removed duplicate equals retained canonical', main.sha(main.ROOT / maintenance['removed_duplicate']['canonical']) == maintenance['removed_duplicate']['sha256'])
    check('duplicate absent', not (main.ROOT / maintenance['removed_duplicate']['path']).exists())
    bibliography = json.loads((main.OWN / 'sources-review-2026-10-07.json').read_text(encoding='utf-8'))
    check('caption quotation accurately counted and short', len(bibliography['caption_quote']['quote'].split()) == bibliography['caption_quote']['words'] < 15)
    check('four missing precedents added', {s['id'] for s in bibliography['sources']} == {'JC2018', 'GC2018', 'JW2018', 'A2013'})
    registry = json.loads((main.OWN / 'registry-entry.json').read_text())
    check('registry current status', registry['status'] == 'Exploratory')
    for path in registry['evidence']:
        check('registry evidence ' + path, (main.ROOT / path).exists())
    main.write(destination, {'status': 'Verified computation', 'stage': 'post-review amendment',
        'passed': len(checks), 'failed': 0, 'historical_artifacts_checked': checked_history,
        'online_only_plotting_files_not_opened': skipped_plotting, 'checks': checks})
    print('Passed', len(checks), 'failed 0; plotting files not opened', skipped_plotting)


if __name__ == '__main__':
    run()
