"""Join v2 numbering to existing consumers without writing or scoring them."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import collections
import json
import re
from audit import ROOT, OWN, RAW, read, write, sha, key
import pyarrow.parquet as pq

M = ROOT / 'experiments/2026-10-07-helsinki1979-digitization'
N = ROOT / 'data/raw/2026-10-08-helsinki1979-row-verification'
O = ROOT / 'experiments/2026-10-08-hf-public-release/release'
inputs = {}


def rel(path):
    return path.relative_to(ROOT).as_posix()


def pin(path):
    inputs[rel(path)] = {'sha256': sha(path), 'bytes': path.stat().st_size}
    return path


def load(path):
    return read(pin(path))


def table(path, columns=None):
    return pq.read_table(pin(path), columns=columns).to_pylist()


def ck(value):
    if isinstance(value, dict):
        return key(value)
    if value.startswith('p'):
        return value
    p, c, r = map(int, value.split(':'))
    return f'p{p}_c{c}_r{r}'


old = {key(r): r for r in load(ROOT / 'research/chart_reference/manual_numeric_reference.json')['rows']}
new = {key(r): r for r in load(OWN / 'chart-reference-v2.json')['rows']}
order = {cell: i for i, cell in enumerate(old)}
changes = {c['cell']: c['fields'] for c in load(OWN / 'comparison.json')['changes']}
old_labels = {cell: set([r['code']] + r['alternatives']) for cell, r in old.items()}
new_labels = {cell: set([r['code']] + r['alternatives']) for cell, r in new.items()}
code_cells = collections.defaultdict(set)
for cell, codes in old_labels.items():
    for code in codes:
        code_cells[code].add(cell)
affected_codes = set().union(*(old_labels[c] for c in changes))


def locations(unit, field='strict_candidate_codes'):
    values = unit.get('shape_only_chart_locations') if field == 'shape_only_candidate_codes' else None
    if values is None:
        values = unit.get('chart_locations', unit.get('chart_references', []))
    if isinstance(values, dict):
        bycode = {int(c): {ck(x) for x in (v if isinstance(v, list) else [v])} for c, v in values.items()}
        return set().union(*bycode.values()) if bycode else set(), bycode
    return {ck(v) for v in values}, {}


def reference_changes(rows, source):
    details, potential, touched, classes = [], [], [], []
    for row in rows:
        sample = row['sample_index']
        for i, unit in enumerate(row.get('units', [])):
            locs, bycode = locations(unit)
            base = dict(source=source, sample_index=sample, unit_index=unit.get('unit_index', i))
            if locs.intersection(changes):
                touched.append(dict(**base, cells=sorted(locs.intersection(changes))))
            if any('rank' in changes.get(c, {}) for c in locs):
                classes.append(dict(**base, cells=sorted(c for c in locs if 'rank' in changes.get(c, {}))))
            for field in ('strict_candidate_codes', 'shape_only_candidate_codes'):
                field_locs, field_bycode = locations(unit, field)
                codes = set(unit.get(field, []))
                mapped, join = set(), []
                for code in codes:
                    candidates = field_bycode.get(code, field_locs).intersection(code_cells[code])
                    if candidates:
                        mapped.update(set().union(*(new_labels[c] for c in candidates)))
                        if any(c in changes for c in candidates):
                            join.append(dict(old_code=code, cells=sorted(candidates)))
                    else:
                        mapped.add(code)
                        if code in affected_codes:
                            possibilities = {c: sorted(new_labels[c]) for c in sorted(code_cells[code])}
                            if any(new_labels[c] != {code} for c in code_cells[code]):
                                potential.append(dict(**base, field=field, old_code=code,
                                                      possible_cell_mappings=possibilities,
                                                      reason='Candidate lacks a matching chart location; graphic identity needs review.'))
                if mapped != codes:
                    details.append(dict(**base, field=field, old_codes=sorted(codes), new_codes=sorted(mapped),
                                        join='explicit chart location intersected with old candidate membership', joins=join))
    affected = {(r['sample_index'], r['unit_index']) for r in details}
    pot_units = {(r['sample_index'], r['unit_index']) for r in potential}
    summary = dict(rows=len(rows), units=sum(len(r.get('units', [])) for r in rows),
                   definite_changed_rows=len({s for s, u in affected}), definite_changed_units=len(affected),
                   changed_candidate_fields=len(details),
                   strict_changed_units=len({(r['sample_index'], r['unit_index']) for r in details if r['field'].startswith('strict')}),
                   shape_changed_units=len({(r['sample_index'], r['unit_index']) for r in details if r['field'].startswith('shape')}),
                   potential_units_needing_identity_review=len(pot_units), potential_candidate_fields=len(potential),
                   affected_chart_location_units=len(touched), class_metadata_units=len(classes))
    return dict(summary=summary, unit_changes=details, potential_mappings=potential,
                affected_chart_locations=touched, class_metadata_locations=classes)


def prediction_changes(rows, source):
    out = []
    for row in rows:
        for i, unit in enumerate(row.get('units', [])):
            for a, alt in enumerate(unit.get('alternatives', [])):
                location = alt.get('template_key')
                if not location:
                    continue
                cell = ck(location)
                if cell not in changes:
                    continue
                updates = {}
                if set(alt.get('codes', [])) != new_labels[cell]:
                    updates['codes'] = dict(old=alt.get('codes'), new=sorted(new_labels[cell]))
                if set(alt.get('ranks', [])) != {new[cell]['rank']}:
                    updates['ranks'] = dict(old=alt.get('ranks'), new=[new[cell]['rank']])
                if updates:
                    out.append(dict(source=source, sample_index=row['sample_index'], unit_index=i,
                                    alternative_index=a, cell=cell, fields=updates))
    changed_units = {(r['sample_index'], r['unit_index']) for r in out}
    top1 = {(r['sample_index'], r['unit_index']) for r in out if r['alternative_index'] == 0}
    return dict(summary=dict(rows=len(rows), units=sum(len(r.get('units', [])) for r in rows),
                             changed_rows=len({s for s, u in changed_units}), changed_units=len(changed_units),
                             changed_alternatives=len(out), top1_changed_units=len(top1),
                             top1_changed_rows=len({s for s, u in top1})), alternative_changes=out)


def card_path(folder, index, n=60):
    path = folder / f'chart_{index // n * n:03d}.png'
    if path.exists():
        pin(path)
    cell = list(old)[index]
    return dict(path=rel(path), exists=path.exists(), card_offset=index % n, cells_per_sheet=n,
                code_strip_changes=old_labels[cell] != new_labels[cell],
                rank_strip_changes=n == 80 and old[cell]['rank'] != new[cell]['rank'])


def main():
    mrefs = {}
    v3_rows = []
    for version, files in {
        'v1': [M / 'blind' / f'reference-{s}.json' for s in ('a', 'b', 'c')],
        'v2': [M / 'repair/2026-10-07-v2/blind/adjudicated-reference.json'],
        'v3': [M / 'repair/2026-10-08-v3/blind/adjudicated-reference.json']
    }.items():
        rows = [r for path in files for r in load(path)['rows']]
        assert len({r['sample_index'] for r in rows}) == len(rows)
        mrefs[version] = reference_changes(rows, ';'.join(rel(p) for p in files))
        if version == 'v3':
            v3_rows = rows

    notes_path = M / 'repair/2026-10-08-v3/blind/adjudication-notes.json'
    chart_notes = load(notes_path)['card_label_observations']
    hypotheses, conflicts = [], []
    v3_byid = {r['sample_index']: r for r in v3_rows}
    for note in chart_notes[:4]:
        cell = ck(note['card_location'])
        claimed = int(re.match(r'\d+', note['printed_code_beside_cell']).group())
        hypotheses.append(dict(cell=cell, reported_printed_code=claimed, audit_printed_code=new[cell]['code'],
                               supported=claimed == new[cell]['code'], source=rel(notes_path), field='card_label_observations'))
        for used in note['used_in']:
            sample = int(re.search(r'row (\d+)', used).group(1))
            unit_numbers = [int(s) for s in re.findall(r'\d+', used.split('unit', 1)[1])]
            for u in unit_numbers:
                unit = v3_byid[sample]['units'][u]
                locs, _ = locations(unit)
                if cell not in locs:
                    conflicts.append(dict(sample_index=sample, unit_index=u, reported_card_cell=cell,
                                          stored_reference_cells=sorted(locs), stored_codes=unit['strict_candidate_codes'],
                                          reported_cell_v2_code=new[cell]['code'], source=rel(notes_path),
                                          reason='Card-label used_in observation conflicts with the stored adjudicated reference location. Requires graphic identity review before mapping.'))

    snapshot = {key(r): r for r in load(M / 'chart-snapshot.json')['rows']}
    lib = {ck(r['key']): r for r in load(M / 'development/templates.json')}
    pin(M / 'pipeline.py')
    templates = []
    for cell in changes:
        row = lib[cell]
        delta = {}
        for field, before, after in [('codes', row['codes'], sorted(new_labels[cell])),
                                     ('rank', row['rank'], new[cell]['rank']),
                                     ('rank_candidates', row['rank_candidates'], [new[cell]['rank']]),
                                     ('chart_code_confidence', row['chart_code_confidence'], new[cell]['numeric_confidence'])]:
            if before != after:
                delta[field] = dict(old=before, new=after)
        templates.append(dict(cell=cell, template_index=order[cell], template_file=rel(M / 'development/templates.json'),
                              snapshot_file=rel(M / 'chart-snapshot.json'), fields=delta,
                              snapshot_matches_v1=snapshot[cell] == old[cell],
                              cards=[card_path(M / 'blind/chart_sheets', order[cell], 80)] +
                                    [card_path(M / f'repair/{folder}/blind/position-chart', order[cell])
                                     for folder in ('2026-10-07-v1', '2026-10-07-v2', '2026-10-08-v3')]))

    ncharts = []
    for run in ('pilot-2026-10-08-v1', 'pilot-2026-10-08-v2', 'adjudication-pilot-v1'):
        for folder in sorted((N / run).glob('*/charts')):
            for cell in changes:
                original = M / 'repair/2026-10-07-v2/blind/position-chart' / f'chart_{order[cell] // 60 * 60:03d}.png'
                target = folder / original.name
                if target.exists():
                    pin(target)
                    ncharts.append(dict(cell=cell, path=rel(target), card_offset=order[cell] % 60,
                                        code_strip_changes=old_labels[cell] != new_labels[cell],
                                        identical_to_M_v2_card=sha(target) == sha(original),
                                        original_path=rel(original)))
    pin(ROOT / 'experiments/2026-10-08-helsinki1979-row-verification/generate_packets.py')

    o_chart = table(O / 'data/chart_reference.parquet', ['cell_id', 'pdf_page', 'column', 'row', 'rank', 'code',
                    'alternatives', 'rank_alternatives', 'numeric_confidence'])
    chart_changes = []
    for index, r in enumerate(o_chart):
        cell = key(r)
        delta = {f: dict(old=r[f], new=new[cell][f]) for f in
                 ('rank', 'code', 'alternatives', 'rank_alternatives', 'numeric_confidence') if r[f] != new[cell][f]}
        if delta:
            chart_changes.append(dict(table=rel(O / 'data/chart_reference.parquet'), row_index=index,
                                      cell_id=r['cell_id'], cell=cell, fields=delta))
    orefs, opreds = {}, {}
    for version in ('v1', 'v2'):
        path = O / 'data' / f'benchmark_rows_{version}.parquet'
        rows = table(path, ['sample_index', 'reference_json', 'prediction_json'])
        refs = [json.loads(r['reference_json']) for r in rows]
        preds = [json.loads(r['prediction_json']) for r in rows]
        # Extracted source rows remain local for reviewer replay; tracked outputs contain locators and deltas.
        write(RAW / f'public-{version}-extracted.json', rows)
        orefs[version] = reference_changes(refs, rel(path) + ':reference_json')
        opreds[version] = prediction_changes(preds, rel(path) + ':prediction_json')
    readings_path = O / 'data/benchmark_readings.parquet'
    readings = table(readings_path)
    write(RAW / 'public-reading-extracted.json', readings)
    reading_groups = collections.defaultdict(list)
    for r in readings:
        reading = json.loads(r['reading_json'])
        if 'sample_index' not in reading:
            reading['sample_index'] = r['sample_index']
        reading_groups[(r['benchmark'], r['reader'], r['kind'])].append(reading)
    reading_results = [{'benchmark': group[0], 'reader': group[1], 'kind': group[2],
                        **reference_changes(rows, rel(readings_path) + ':reading_json')}
                       for group, rows in sorted(reading_groups.items())]
    o_cards = table(O / 'data/benchmark_chart_cards.parquet')
    release_cards = []
    for cell in changes:
        for v, n in [('v1', 80), ('v2', 60)]:
            name = f'chart_{order[cell] // n * n:03d}'
            matches = [r for r in o_cards if r['benchmark'] == v and r['card_id'] == name]
            for r in matches:
                path = O / r['image_path']
                pin(path)
                release_cards.append(dict(cell=cell, benchmark=v, card_id=name, path=rel(path), card_offset=order[cell] % n,
                                          code_strip_changes=old_labels[cell] != new_labels[cell],
                                          rank_strip_changes=n == 80 and old[cell]['rank'] != new[cell]['rank']))
    expectations = load(O / 'benchmark/expected-metrics.json')
    for file in ('code/score_benchmark.py', 'code/score_core.py', 'code/verify_benchmarks.py'):
        path = O / file
        if path.exists():
            pin(path)
    impacted_expectations = ['summary.strict_top1', 'summary.strict_top5', 'summary.shape_only_top1',
                            'summary.shape_only_top5', 'summary.calibration', 'rows[*].strict_top1',
                            'rows[*].strict_top5', 'rows[*].shape_only_top1', 'rows[*].shape_only_top5',
                            'rows[*].uniquely_resolved_exact_sequence', 'row_bootstrap_95',
                            'negative_result_criteria.top5_rows_80', 'exploratory_sensitivities (v1)']
    expected_row_review = {}
    cardinality_changes = {}
    for version in ('v1', 'v2'):
        ref_deltas = orefs[version]['unit_changes']
        pred_deltas = [a for a in opreds[version]['alternative_changes']
                       if 'codes' in a['fields'] and a['alternative_index'] < 5]
        samples = sorted({a['sample_index'] for a in ref_deltas + pred_deltas})
        expected_row_review[version] = dict(sample_indices=samples, rows=len(samples),
            field=f'{version}.rows[*] (match sample_index)',
            reason='Reference candidate sets or stored top-five code sets change; recomputed metrics may agree or differ.')
        cardinality_changes[version] = sum(r['field'] == 'strict_candidate_codes' and
                                           len(r['old_codes']) != len(r['new_codes']) for r in ref_deltas)
    result = dict(status='Exploratory', mapping_policy='Explicit cell identity and old code membership. Unlocated affected candidates remain potential mappings. No scores recomputed.',
                  M_references=mrefs, M_templates=templates, N_charts=ncharts,
                  M_v3_chart_hypotheses=hypotheses, M_v3_reported_location_conflicts=conflicts,
                  public_chart_reference_changes=chart_changes, public_references=orefs, public_predictions=opreds,
                  public_readings=reading_results, public_cards=release_cards,
                  scorer_expectations=dict(path=rel(O / 'benchmark/expected-metrics.json'), versions=list(expectations),
                                           fields_requiring_new_versioned_run=impacted_expectations,
                                           expected_row_records_to_review=expected_row_review,
                                           direct_strict_candidate_cardinality_changes=cardinality_changes,
                                           unchanged_by_number_mapping=['crop', 'inscription number', 'classification literal',
                                                                        'drawn unit count', 'source row recall', 'confidence values',
                                                                        'reference ambiguous-unit and unique-reference-row counts under the direct joins'],
                                           scores_recomputed=False))
    write(OWN / 'impact.json', result)
    after = {path: sha(ROOT / path) for path in inputs}
    integrity = dict(status='Verified computation', files=len(inputs),
                     unchanged=all(after[p] == v['sha256'] for p, v in inputs.items()),
                     changed_inputs=[p for p, v in inputs.items() if after[p] != v['sha256']], inputs=inputs)
    assert integrity['unchanged'], integrity['changed_inputs']
    write(OWN / 'consumer-input-integrity.json', integrity)
    print(json.dumps(dict(M={v: d['summary'] for v, d in mrefs.items()},
                          public_references={v: d['summary'] for v, d in orefs.items()},
                          public_predictions={v: d['summary'] for v, d in opreds.items()},
                          public_chart_changed_rows=len(chart_changes), templates=len(templates),
                          N_card_matches=len(ncharts), N_cards_all_identical=all(r['identical_to_M_v2_card'] for r in ncharts),
                          release_cards=len(release_cards), pinned_inputs=len(inputs))))


if __name__ == '__main__':
    main()
