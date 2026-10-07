"""Independent count/combination checks and planned coverage diagnostics for D1.

Run from the repository root with -B; use fresh output and coverage names.
No existing endpoint is written. No new inferential test is selected here.
"""
from __future__ import annotations
import argparse, collections, csv, functools, hashlib, itertools, json, math
from pathlib import Path
import numpy as np
import analyze as base
import post_launch as assay

ORIGIN = 'post-launch amendment'
CHECKS = collections.Counter()


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def rows(path):
    with path.open(encoding='utf-8', newline='') as stream: return list(csv.DictReader(stream))
def close(actual, expected, label, tolerance=2e-9):
    assert np.allclose(actual, expected, rtol=tolerance, atol=tolerance), (label, actual, expected)
    CHECKS[label] += 1
def equal(actual, expected, label):
    assert actual == expected, (label, actual, expected)
    CHECKS[label] += 1
def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
def table(path, values):
    values = [{'origin': ORIGIN, 'status': 'Exploratory', **x} for x in values]
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(values[0]))
        writer.writeheader(); writer.writerows(values)


@functools.lru_cache(maxsize=100000)
def absence(n, k, m):
    return math.comb(n-k, m) / math.comb(n, m) if n-k >= m else 0.0


def exact_diversity(counts, m):
    counts = [x for x in counts if x]
    n = sum(counts)
    if not n: return (0.0, 0.0)
    denominator = math.comb(n, m)
    richness = sum(1-absence(n, x, m) for x in counts)
    entropy = 0.0
    for x in counts:
        for k in range(max(1, m-(n-x)), min(x, m)+1):
            probability = math.comb(x, k)*math.comb(n-x, m-k)/denominator
            entropy -= probability*(k/m)*math.log2(k/m)
    return richness, entropy


def expected_inventory(units, cells, budgets):
    signs = {s for ids in cells.values() for i in ids for s in units[i]['codes']}
    result = 0.0
    for sign in signs:
        probability = 1.0
        for cell, ids in cells.items():
            k = sum(sign in units[i]['codes'] for i in ids)
            probability *= absence(len(ids), k, budgets[cell])
        result += 1-probability
    return result


def holm(ps):
    order = sorted(range(len(ps)), key=ps.__getitem__)
    adjusted, previous = [0.0]*len(ps), 0.0
    for rank, index in enumerate(order):
        previous = max(previous, min(1.0, ps[index]*(len(ps)-rank)))
        adjusted[index] = previous
    return adjusted


def independent_units(c):
    units = []
    for pid, members in enumerate(c.physical):
        ids = [i for i in members if c.rows[i]['site'] == 'Harappa']
        if not ids: continue
        types = sorted({c.rows[i]['type'] for i in ids})
        periods = sorted({p for i in ids for p in base.periods(c.rows[i]['metadata'].get('time'))}, key=base.PERIODS.index)
        counts = collections.Counter(s for i in ids for s in c.rows[i]['signs_reading_rtl'])
        units.append({'physical': pid, 'text': int(c.tid[ids[0]]), 'indices': ids,
            'type': types[0] if len(types) == 1 else None, 'types': types, 'admissible': periods,
            'period': periods[0] if len(periods)==1 else 'interval' if periods else 'undated',
            'codes': sorted(s for s in counts if s!='000'), 'faces': len(ids),
            'slots': sum(counts.values()), 'known_tokens': sum(n for s,n in counts.items() if s!='000'),
            'unreadable_tokens': counts['000']})
    return units


def independent_frequency(c, a, b, targets):
    types = sorted({c.rows[i]['type'] for i in a})
    def fraction(i, signs):
        sequence = c.rows[i]['signs_reading_rtl']
        return sum(s in signs for s in sequence)/sum(s!='000' for s in sequence)
    cells = collections.defaultdict(list)
    for i in b: cells[(c.rows[i]['type'], len(c.rows[i]['signs_reading_rtl']))].append(i)
    values = {}
    for target, signs in targets.items():
        per_type = collections.defaultdict(list)
        for i in a:
            key = (c.rows[i]['type'], len(c.rows[i]['signs_reading_rtl']))
            ext = fraction(i, signs)
            ref = sum(fraction(j, signs) for j in cells[key])/len(cells[key])
            per_type[key[0]].append((ext, ref))
        external = sum(sum(x[0] for x in per_type[t])/len(per_type[t]) for t in types)/len(types)
        core = sum(sum(x[1] for x in per_type[t])/len(per_type[t]) for t in types)/len(types)
        values[target] = {'type_external_fraction': external, 'type_matched_core_fraction': core, 'type_excess': external-core}
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', default='post-launch-2026-10-07-v1')
    parser.add_argument('--output', default='verification-post-launch-2026-10-07-v1.json')
    parser.add_argument('--coverage', default='post-launch-coverage-2026-10-07-v1')
    args = parser.parse_args()
    for name in [args.run, args.output, args.coverage]:
        if Path(name).name != name: raise ValueError('Use single fresh directory/file names.')
    endpoint, local = base.OWN/args.run, base.RAW/args.run
    output, coverage = base.OWN/args.output, base.OWN/args.coverage
    if output.exists() or coverage.exists(): raise FileExistsError('Existing outputs are preserved.')
    audit = read(endpoint/'audit.json')
    c = base.Corpus()
    for field, path in [('input_sha256', c.path), ('code_sha256', base.OWN/'post_launch.py'),
                        ('reused_analyzer_sha256', base.OWN/'analyze.py'),
                        ('amendment_sha256', base.OWN/'POST-LAUNCH-PROTOCOL-2026-10-07.md')]:
        equal(audit[field], digest(path), 'pinned_hash')
    baseline = read(base.OWN/'post-launch-document-baseline-2026-10-07-v1/preservation.json')['baseline_files']
    immutable = [x for x in baseline if not x['authorized_document_update']]
    for entry in immutable: equal(digest(base.ROOT/entry['path']), entry['sha256'], 'original_file_preserved')
    for entry in baseline:
        if entry['authorized_document_update']:
            equal(digest(base.OWN/'post-launch-document-baseline-2026-10-07-v1'/Path(entry['path']).name), entry['sha256'], 'original_document_snapshot')
    for path in endpoint.glob('*.json'):
        equal(read(path)['origin'], ORIGIN, 'origin_json'); equal(read(path)['status'], 'Exploratory', 'status_json')
    for path in endpoint.glob('*.csv'):
        for row in rows(path):
            equal(row['origin'], ORIGIN, 'origin_csv'); equal(row['status'], 'Exploratory', 'status_csv')
    identifications = read(endpoint/'sign_identifications.json')
    for name, sha in identifications['inputs'].items(): equal(digest(base.ROOT/name), sha, 'sign_reference_hash')
    schema = read(base.ROOT/'data/normalized/mayig_sign_schema.json')['signs']
    crosswalk = read(base.ROOT/'data/normalized/mayig_wells_class_crosswalk.json')['by_wells_id']
    atlas = read(base.ROOT/'output/chart_atlas/reference.json')['rows']
    manual = read(base.ROOT/'research/chart_reference/manual_numeric_reference.json')['rows']
    for identification in identifications['identifications']:
        code, cls = identification['wells_code'], identification['mayig_class']
        equal('W'+code in schema[cls]['wells_graphemes'], True, 'schema_mapping')
        equal(cls in crosswalk[code], True, 'crosswalk_mapping')
        for locator in identification['locators']:
            for source in [atlas, manual]:
                matches = [x for x in source if (x['pdf_page'],x['column'],x['row']) == (locator['pdf_page'],locator['column'],locator['row'])]
                equal(len(matches), 1, 'chart_locator_unique'); equal(matches[0]['code'], locator['code'], 'chart_locator_code')
    for count_tuple in [(3,2), (2,2,1), (1,1,1,1), (4,1,1)]:
        labels = [j for j,n in enumerate(count_tuple) for _ in range(n)]
        for m in range(1,len(labels)+1):
            subsets = [collections.Counter(labels[i] for i in ids) for ids in itertools.combinations(range(len(labels)),m)]
            richness = sum(len(x) for x in subsets)/len(subsets)
            entropy = sum(-sum((n/m)*math.log2(n/m) for n in x.values()) for x in subsets)/len(subsets)
            close(assay.diversity(count_tuple,m), [richness,entropy], 'explicit_subset_rarefaction')
            close(exact_diversity(count_tuple,m), [richness,entropy], 'combination_formula')
    units = independent_units(c)
    equal(units, read(local/'harappa_units.json')['units'], 'all_harappa_family_fields')
    for row in rows(endpoint/'media_period_summary.csv'):
        selected = [x for x in units if x['period']==row['period'] and x['type'] is not None]
        counts = collections.Counter(x['type'] for x in selected)
        for field, expected in [('physical_families',len(selected)), ('faces',sum(x['faces'] for x in selected)),
                                ('known_tokens',sum(x['known_tokens'] for x in selected)), ('unreadable_tokens',sum(x['unreadable_tokens'] for x in selected))]:
            equal(int(row[field]),expected,'media_period_count')
        close([float(row['type_richness']),float(row['shannon_bits'])], exact_diversity(counts.values(),len(selected)), 'media_period_diversity')
    for row in rows(endpoint/'media_period_type_counts.csv'):
        selected = [x for x in units if x['period']==row['period'] and x['type']==row['type']]
        for field, expected in [('physical_families',len(selected)),('faces',sum(x['faces'] for x in selected)),
                                ('known_tokens',sum(x['known_tokens'] for x in selected)),('unreadable_tokens',sum(x['unreadable_tokens'] for x in selected))]:
            equal(int(row[field]),expected,'media_type_count')
    for row in rows(endpoint/'media_rarefaction.csv'):
        counts = collections.Counter(x['type'] for x in units if x['period']==row['period'] and x['type'] is not None)
        close([float(row['expected_type_richness']),float(row['expected_shannon_bits'])],exact_diversity(counts.values(),int(row['family_budget'])),'media_curve_combination_check')
    membership = read(local/'external_membership.json')
    ext = read(endpoint/'external_frequency.json')
    a,b = membership['external_indices'],membership['core_indices']
    for target, values in independent_frequency(c,a,b,assay.TARGETS).items():
        for key,value in values.items(): close(ext['results'][target][key],value,'external_matched_fraction')
    for row in rows(endpoint/'external_target_counts.csv'):
        ids = a if row['population']=='external_matched' else [i for i,r in enumerate(c.rows) if r['region'] in (base.CORE if row['population']=='core_all' else base.EXTERNAL) and (row['population']!='external_clear' or r['clear'])]
        counts = [sum(s in assay.TARGETS[row['target']] for s in c.rows[i]['seq']) for i in ids]
        equal(int(row['target_tokens']),sum(counts),'external_target_token_count')
        equal(int(row['target_bearing_faces']),sum(x>0 for x in counts),'external_target_face_count')
        equal(int(row['known_tokens']),sum(sum(s!='000' for s in c.rows[i]['seq']) for i in ids),'external_known_denominator')
    boot = read(local/'external_bootstrap_draws.json')
    for j,target in enumerate(boot['targets']):
        for k,field in enumerate(boot['fields']): close(ext['results'][target]['intervals95'][field],np.quantile(np.asarray(boot['draws'])[:,j,k],[.025,.975]),'external_saved_bootstrap_quantile')
    for reference in ext['grouped_references']:
        saved = read(local/f"external_{reference['unit']}_permutation_draws.json")
        draws = np.asarray(saved['draws'])
        ps = [(1+int(np.sum(draws[:,j]>=reference['effects'][t]['type_excess']-1e-12)))/(len(draws)+1) for j,t in enumerate(saved['targets'])]
        adjusted = holm(ps[:2])+holm(ps[2:])
        for j,target in enumerate(saved['targets']):
            close(reference['tests'][target]['one_sided_p'],ps[j],'external_saved_permutation_p')
            close(reference['tests'][target]['holm_p'],adjusted[j],'external_saved_holm')
    media = read(endpoint/'media_comparison.json'); md = read(local/'media_draws.json')
    ps = []
    for j,field in enumerate(md['fields']):
        close(media['effects'][field]['interval95'],np.quantile(np.asarray(md['bootstrap'])[:,j],[.025,.975]),'media_saved_bootstrap_quantile')
        if j>=2: ps.append((1+int(np.sum(np.asarray(md['permutation'])[:,j]>=media['effects'][field]['effect']-1e-12)))/2000)
    for j,field in enumerate(md['fields'][2:]):
        close(media['effects'][field]['one_sided_p'],ps[j],'media_saved_permutation_p')
        close(media['effects'][field]['holm_p'],holm(ps)[j],'media_saved_holm')
    alloc = read(local/'period_allocations.json')['allocations']
    equal(len(alloc),205,'period_allocation_count')
    for allocation in alloc:
        for unit in units:
            chosen = allocation['labels'][str(unit['physical'])]
            allowed = unit['admissible'] or ['undated']
            equal(chosen in allowed or (not allocation['scenario'].startswith('uniform_') and chosen==unit['period']),True,'admissible_whole_family_allocation')
    early = read(endpoint/'early_inventory.json'); er = read(local/'early_raw_draws.json')
    selected_early,selected_later = er['early_unit_indices'],er['later_unit_indices']
    equal(len({s for i in selected_early for s in units[i]['codes']}),early['raw_family_reference']['early_inventory'],'early_inventory_union')
    close(expected_inventory(units,{'all':selected_later},{'all':len(selected_early)}),early['raw_family_reference']['later_exact_expected_inventory'],'early_exact_combination_expectation')
    close(np.mean(er['inventory_draws']),early['raw_family_reference']['later_sample_mean_inventory'],'early_saved_random_mean')
    close(np.quantile(er['inventory_draws'],[.025,.975]),early['raw_family_reference']['later_sample_interval95'],'early_saved_random_spread')
    eps,tps = [],[]
    early_cells_output = []
    for name, result in early['adjusted'].items():
        saved = read(local/f'early_{name}_draws.json')
        ga = {tuple(x['cell']):x['indices'] for x in saved['early_cells']}
        gb = {tuple(x['cell']):x['indices'] for x in saved['later_cells']}
        budgets = {k:min(len(v),len(gb[k])) for k,v in ga.items()}
        for population,cells in [('early',ga),('later',gb)]:
            expected = expected_inventory(units,cells,budgets)
            close(result[f'expected_{population}_inventory'],expected,'early_adjusted_combination_expectation')
            for cell, ids in cells.items():
                group = [units[i] for i in ids]
                early_cells_output.append({'adjustment':name,'population':population,'type':cell[0],'family_slots':cell[1] if len(cell)>1 else 'all',
                    'physical_families':len(ids),'text_components':len({x['text'] for x in group}),'faces':sum(x['faces'] for x in group),
                    'known_tokens':sum(x['known_tokens'] for x in group),'unreadable_tokens':sum(x['unreadable_tokens'] for x in group),'sample_family_budget':budgets[cell]})
        close(result['interval95'],np.quantile(saved['bootstrap'],[.025,.975]),'early_saved_bootstrap_quantile')
        p=(1+sum(x<=result['early_minus_later']+1e-12 for x in saved['permutation']))/2000
        close(result['one_sided_p'],p,'early_saved_permutation_p'); eps.append(p)
        text_draws=read(local/f'early_{name}_text_draws.json')['draws']
        tp=(1+sum(x<=result['text_component_sensitivity']['effect']+1e-12 for x in text_draws))/2000
        close(result['text_component_sensitivity']['one_sided_p'],tp,'early_text_saved_p'); tps.append(tp)
    for j,result in enumerate(early['adjusted'].values()):
        close(result['holm_p'],holm(eps)[j],'early_saved_holm')
        close(result['text_component_sensitivity']['holm_p'],holm(tps)[j],'early_text_saved_holm')
    # These aggregate coverage fields were required by the pre-outcome protocol.
    # They are saved separately because the completed assay endpoint is immutable.
    coverage.mkdir()
    region_type,stages = collections.defaultdict(list),collections.defaultdict(list)
    matched_set=set(a); eligible_set=set(i for i,r in enumerate(c.rows) if r['region'] in base.EXTERNAL and r['clear'])
    for i,r in enumerate(c.rows):
        if r['region'] not in base.EXTERNAL: continue
        region_type[(r['region'],r['type'])].append(i)
        stage='matched' if i in matched_set else 'clear_but_unmatched' if i in eligible_set else 'not_clear'
        stages[(stage,r['type'])].append(i)
    def count_rows(groups,dimensions):
        result=[]
        for key,ids in sorted(groups.items()):
            for sign in ['090','091']:
                counts=[c.rows[i]['seq'].count(sign) for i in ids]
                result.append({**dict(zip(dimensions,key)),'sign':sign,'faces':len(ids),'physical_families':len({int(c.pid[i]) for i in ids}),
                    'known_tokens':sum(sum(s!='000' for s in c.rows[i]['seq']) for i in ids),'unreadable_tokens':sum(c.rows[i]['seq'].count('000') for i in ids),
                    'target_tokens':sum(counts),'target_bearing_faces':sum(x>0 for x in counts),'target_bearing_families':len({int(c.pid[i]) for i,n in zip(ids,counts) if n})})
        return result
    table(coverage/'external_region_type_counts.csv',count_rows(region_type,['region','type']))
    table(coverage/'external_selection_counts.csv',count_rows(stages,['selection_stage','type']))
    table(coverage/'early_adjusted_denominators.csv',early_cells_output)
    summary={'origin':ORIGIN,'status':'Verified computation','checks':dict(CHECKS),
        'checks_total':sum(CHECKS.values()),'original_immutable_files_preserved':len(immutable),
        'original_document_snapshots_verified':4,'harappa_families_rebuilt':len(units),
        'scope':'Independent raw counts and combinatorial expectations; all saved test p-values/corrections and principal interval quantiles checked. Random label allocations are not independently replayed here; the assay asserts margins in 13993 draws.',
        'coverage_origin':'Previously specified regional, selection and cell-denominator diagnostics completed without editing the assay endpoint.',
        'code_sha256':digest(Path(__file__)),'assay_run':args.run,'coverage_directory':coverage.relative_to(base.ROOT).as_posix(),
        'immutable_assay_files':[{ 'path':p.relative_to(base.ROOT).as_posix(),'sha256':digest(p)} for directory in [endpoint,local] for p in sorted(directory.iterdir()) if p.is_file()]}
    write(coverage/'coverage_checks.json',{'origin':ORIGIN,'status':'Exploratory','source_run':args.run,'files':['external_region_type_counts.csv','external_selection_counts.csv','early_adjusted_denominators.csv'],'verification':output.relative_to(base.ROOT).as_posix()})
    write(output,summary)
    print(json.dumps({k:summary[k] for k in ['checks_total','original_immutable_files_preserved','harappa_families_rebuilt']},indent=2))


if __name__=='__main__': main()
