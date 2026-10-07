"""Verify reproduction, field corrections and preservation of earlier endpoints."""
import argparse, ast, csv, hashlib, json, shutil
from pathlib import Path
from build_corrections import ROOT, OWN, PKG, OLD, RAW, read, write, digest
DOCS={'PROTOCOL.md','README.md','REPORT.md','RETROSPECTIVE.md','TEST-DESIGNS.md','registry-entry.json',
      'amendment-2026-10-07-frenez/README.md','amendment-2026-10-07-frenez/REPORT.md',
      'amendment-2026-10-07-frenez/RETROSPECTIVE.md','amendment-2026-10-07-frenez/TEST-DESIGNS.md',
      'amendment-2026-10-07-frenez/registry-entry.json'}
def equal_dirs(a,b):
    names=sorted(p.name for p in a.iterdir()if p.is_file())
    assert names==sorted(p.name for p in b.iterdir()if p.is_file())
    for n in names:assert digest(a/n)==digest(b/n),n
    return names
def funcs(p):
    return {x.name:ast.dump(x,include_attributes=False)for x in ast.parse(p.read_text(encoding='utf-8-sig')).body if isinstance(x,ast.FunctionDef)and x.name!='main'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--manifest',action='store_true');a=ap.parse_args()
    out=Path(a.output).resolve();out.relative_to(OWN)
    if out.exists():ap.error('Use a fresh output file.')
    inputs=OWN/'inputs-05';rows=read(inputs/'evidence-table.json')['rows'];rr={r['id']:r for r in rows}
    with (inputs/'evidence-table.csv').open(encoding='utf-8-sig',newline='')as f:csvrows=list(csv.DictReader(f))
    cells=0
    for r,c in zip(rows,csvrows):
        for k,v in r.items():
            expected=json.dumps(v,ensure_ascii=False)if isinstance(v,(dict,list))else''if v is None else str(v)
            assert c[k]==expected,(r['id'],k);cells+=1
    assert len(rows)==len(csvrows)==65
    assert all(rr[x]['count_kind']=='exact, temporally unaligned'for x in ['keeladi','kodumanal','perumbalai'])
    assert rr['kodumanal']['marked_object_count']==1955
    assert rr['sivagalai-habitation']['marked_object_count']==150
    assert rr['thulukkarpatti-I']['marked_object_count']==4797
    assert not rr['pirak']['include_in_additive_coverage']
    assert not any(d['selected_for_coverage']for d in rr['pirak-II']['dating_assessments'])
    assert next(d for d in rr['pirak-IIIA']['dating_assessments']if d['selected_for_coverage'])['grade']=='C'
    assert next(d for d in rr['perumbalai']['dating_assessments']if d['selected_for_coverage'])['calendar_strength']=='low'
    assert rr['porunthal-I']['marked_object_count']==1
    assert any(d['start_year']==-3900 and not d['selected_for_coverage']for d in rr['harappa-ravi']['dating_assessments'])
    assert all(d['calendar_strength']=='low'for x in ['daimabad-II','daimabad-III']for d in rr[x]['dating_assessments'])
    assert all(rr[x]['marked_object_count']==0 and not rr[x]['include_in_additive_coverage']for x in ['sivagalai-A2-Urn-3','adichanallur-urn-burials'])
    dd=read(inputs/'dating-details.json');assert all(x in rr for x in dd['specimen_units']['ids_without_script'])
    assert dd['count_audit']['transposition_arithmetic']['candidate_phase_sum']==190
    ss={s['id']:s for s in read(inputs/'sources.json')['sources']}
    assert ss['lal1960']['printed_year']==1962 and ss['lal1960']['year']==1960
    assert ss['cisi2-1991']['opened']and not ss['jarrige-santoni1979']['opened']and not ss['magee-petrie2010']['opened']
    assert '46–47' in ss['harappa-hearth-gallery']['venue']
    cc={c['id']:c for c in read(inputs/'continuity-claims.json')['claims']}
    assert 'Alok Tripathi'in cc['bet-dwarka-relation']['authors']
    contact={c['id']:c for c in read(inputs/'contact-items.json')['cases']}
    assert contact['bnf-cuneiform-stamp']['images_reviewed']
    assert all(d['grade']=='D'for x in ['bnf-cuneiform-stamp','bahrain-tokens2026']for d in contact[x]['dating_assessments'])
    inherited=funcs(OLD/'analyze_coverage.py');current=funcs(OWN/'analyze_coverage.py')
    assert inherited==current
    reproduced={
        'inputs':equal_dirs(inputs,OWN/'reproduction-inputs-02'),
        'coverage':equal_dirs(OWN/'run-2026-10-07-04',OWN/'reproduction-run-02'),
        'sensitivity':equal_dirs(OWN/'sensitivity-04',OWN/'reproduction-sensitivity-02'),
        'coverage_documentation':equal_dirs(OWN/'coverage-02',OWN/'reproduction-coverage-02')}
    assert digest(OWN/'power-targets.json')==digest(OWN/'reproduction-power-01.json')
    assert digest(OWN/'recovery-audit.json')==digest(OWN/'reproduction-recovery-01.json')
    baseline=read(OWN/'baseline-integrity.json')['files'];changed=[];unchanged=0
    for x in baseline:
        p=ROOT/x['path'];assert p.exists(),x['path']
        if digest(p)!=x['sha256']:
            rel=p.relative_to(PKG).as_posix();assert rel in DOCS,rel;changed.append(x['path'])
        else:unchanged+=1
    result=dict(status='Verified computation',documentary_status='Exploratory',csv_rows=len(rows),csv_cells=cells,
        estimator_functions_identical=list(current),reproduced_files=reproduced,power_reproduced=True,recovery_audit_reproduced=True,
        source_hash_checks=read(OWN/'run-2026-10-07-04/verification.json')['source_hash_checks'],
        baseline_files=len(baseline),unchanged_baseline_files=unchanged,authorized_documentation_changes=changed,
        protected_endpoints_unchanged=True,correction_assertions_passed=True)
    write(out,result)
    if a.manifest:
        manifest=OWN/'file-manifest.json'
        if manifest.exists():ap.error('Manifest exists; do not overwrite.')
        oldpaths={x['path']for x in baseline};new=[]
        for base in [PKG,ROOT/'data/raw/2026-10-06-backward-chronology']:
            for p in sorted(base.rglob('*')):
                if p.is_file()and p.relative_to(ROOT).as_posix()not in oldpaths:
                    new.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)))
        rawnew=[x for x in new if x['path'].startswith('data/')]
        write(manifest,dict(status='Verified computation',created=new,changed=[dict(path=s,bytes=(ROOT/s).stat().st_size,sha256=digest(ROOT/s))for s in changed],
            excludes_self=manifest.relative_to(ROOT).as_posix(),created_files=len(new),changed_files=len(changed),
            created_directories=[p.relative_to(ROOT).as_posix()for base in [OWN,RAW]for p in [base,*sorted(base.rglob('*'))]if p.is_dir()],
            new_raw_bytes=sum(x['bytes']for x in rawnew),free_disk_bytes=shutil.disk_usage(ROOT).free))
    print(json.dumps({k:v for k,v in result.items()if k not in ['reproduced_files','authorized_documentation_changes']},indent=2))
if __name__=='__main__':main()
