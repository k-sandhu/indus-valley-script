"""Compare immutable parent run03 with amended coverage; check reproduction."""
from __future__ import annotations
import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OWN=Path(__file__).resolve().parent
BASE=OWN.parent

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--output',required=True)
    p.add_argument('--reproduction');a=p.parse_args()
    run=Path(a.run).resolve();run.relative_to(OWN)
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():p.error('Choose a fresh output directory.')
    old=BASE/'run-2026-10-07-03'
    bs=load(old/'summary.json');ns=load(run/'summary.json')
    bb=load(old/'coverage.json')['bins'];nb=load(run/'coverage.json')['bins']
    differences=[]
    for b,n in zip(bb,nb):
        assert b['start_year']==n['start_year'] and b['end_year']==n['end_year']
        deltas={k:n[k]-b[k] for k in n if isinstance(n[k],int) and k not in ['start_year','end_year']}
        differences.append(dict(start_year=n['start_year'],end_year=n['end_year'],label=n['label'],
            deltas=deltas,added_assemblage_ids=sorted(set(n['assemblage_ids'])-set(b['assemblage_ids'])),
            removed_assemblage_ids=sorted(set(b['assemblage_ids'])-set(n['assemblage_ids']))))
    rows=load(OWN/'evidence-table.json')['rows'];base_rows=load(BASE/'evidence-table.json')['rows']
    assert rows[:len(base_rows)]==base_rows
    added=rows[len(base_rows):]
    functions={}
    for file in [BASE/'analyze_coverage.py',OWN/'analyze_coverage.py']:
        tree=ast.parse(file.read_text(encoding='utf-8'))
        functions[file.as_posix()]={x.name:ast.dump(x,include_attributes=False) for x in tree.body if isinstance(x,ast.FunctionDef)}
    values=list(functions.values());same_functions=[k for k in values[0] if values[0][k]==values[1].get(k)]
    assert set(same_functions)==set(values[0]),'Coverage estimators/checks must be unchanged.'
    g=['grade_A','phase_or_historical_AB','high_moderate_calendar_AB']
    assert all(bs['gaps'][k]==ns['gaps'][k] for k in g)
    eligible=[r for r in added if r['include_in_additive_coverage'] and not r['adjacent_region'] and
              any(d['selected_for_coverage'] and d['start_year'] is not None and d['end_year'] is not None for d in r['dating_assessments'])]
    exact=[r for r in eligible if r['count_kind']=='exact' and r['marked_object_count'] is not None]
    integrity=[]
    for f in load(OWN/'baseline-integrity.json')['baseline_files']:
        q=ROOT/f['path'];actual=hashlib.sha256(q.read_bytes()).hexdigest()
        integrity.append(dict(path=f['path'],sha256=actual,unchanged=actual==f['sha256']))
    assert all(f['unchanged'] for f in integrity)
    reproduction=None
    if a.reproduction:
        rep=Path(a.reproduction).resolve();rep.relative_to(OWN)
        names=['coverage.json','coverage.csv','summary.json','dating-audit.json','regional-gaps.json','verification.json']
        checks=[dict(file=name,sha256=hashlib.sha256((run/name).read_bytes()).hexdigest(),
                    identical=(run/name).read_bytes()==(rep/name).read_bytes())for name in names]
        assert all(x['identical'] for x in checks)
        reproduction=dict(files_checked=len(checks),all_identical=True,files=checks)
    comparison=dict(status='Verified computation',parent_run=old.relative_to(ROOT).as_posix(),amended_run=run.relative_to(ROOT).as_posix(),
        parent_rows_unchanged=len(base_rows),added_rows=len(added),added_dated_additive_rows=len(eligible),
        added_dated_additive_row_ids=[r['id'] for r in eligible],
        added_exact_dated_object_rows=len(exact),added_distinct_reported_exact_objects=sum(r['marked_object_count'] for r in exact),
        exact_object_count_note='Reported sherds/specimens, not minimum vessels and not all marks at these sites. No across-century sum.',
        unchanged_gap_series=g,centuries_with_changed_assemblage_count=sum(d['deltas']['assemblages']!=0 for d in differences),
        centuries_with_changed_numeric_object_upper=sum(d['deltas']['exact_objects_possible_upper']!=0 for d in differences),
        summary_deltas={k:ns[k]-bs[k] for k in ['inventory_rows','sources','continuity_claims','dated_additive_rows_in_window','rows_with_verified_images','rows_without_selected_calendar_interval','zero_A_centuries','zero_AB_centuries','zero_high_moderate_AB_centuries']},
        coverage_functions_unchanged=same_functions,baseline_files_checked=len(integrity),all_baseline_files_unchanged=True,
        reproduction=reproduction,bins=differences)
    out.mkdir()
    write(out/'comparison.json',comparison);write(out/'baseline-verification.json',dict(status='Verified computation',files_checked=len(integrity),all_unchanged=True,files=integrity))
    with (out/'coverage-deltas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['label']+list(differences[0]['deltas'])
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for d in differences:w.writerow({'label':d['label'],**d['deltas']})
    md=['# Amended century coverage','',
        'Status: Verified computation. Archaeological assessments remain Exploratory. Each row counts possible overlap in one century. A broad source interval does not establish an observation in every century. Exact-object bounds cover reported sherds/specimens with usable counts; unknown counts remain separate. Never sum the upper column across centuries. Definitions and inclusion decisions are in [PROTOCOL](../PROTOCOL.md) and [dating audit](../'+run.name+'/dating-audit.json).','',
        '| BCE interval | Assemblages | A | B | C | D | A/B high or moderate calendar | Image rows | Exact lower–upper | Unknown-count rows | Added assemblages | Added exact upper |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for n,d in zip(nb,differences):
        md.append(f"| {n['label']} | {n['assemblages']} | {n['grade_A']} | {n['grade_B']} | {n['grade_C']} | {n['grade_D']} | {n['high_moderate_calendar_AB']} | {n['assemblages_with_verified_images']} | {n['exact_objects_assignable_lower']}–{n['exact_objects_possible_upper']} | {n['unknown_object_count_assemblages']} | {d['deltas']['assemblages']} | {d['deltas']['exact_objects_possible_upper']} |")
    md += ['', 'The longest internal A/B gap with high/moderate calendar strength remains **1300–700 BCE, 600 years**. All A/B brackets, including low-strength legacy dates, retain the two gaps **800–700** and **400–300 BCE**. The Indus northwest has12 dated additive rows; South India has4. See [summary](../'+run.name+'/summary.json), fields `gaps` and `regions`, and [comparison](comparison.json).','']
    (out/'COVERAGE.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps({k:v for k,v in comparison.items() if k not in ['bins','reproduction']},indent=2))

if __name__=='__main__':main()
