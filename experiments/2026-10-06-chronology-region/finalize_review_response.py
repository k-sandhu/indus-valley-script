"""Final source, documentation, preservation and adapter checks with explicit paths."""
from __future__ import annotations
import argparse, ast, collections, datetime, hashlib, importlib.util, json, re, shutil, subprocess, sys
from pathlib import Path
OWN=Path(__file__).resolve().parent; ROOT=OWN.parents[1]; RAW=ROOT/'data/raw/2026-10-06-chronology-region'
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')

def compare_endpoints(old,new):
    spec=importlib.util.spec_from_file_location('preserved_review_compare',OWN/'review/compare_outputs.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    checked=[]
    for source in sorted(old.iterdir()):
        if source.suffix not in ['.json','.csv']: continue
        target=new/source.name
        if not target.exists(): raise FileNotFoundError(target)
        module.diffs.clear()
        if source.suffix=='.json': module.cmp(read(source),read(target),'',module.IGNORE)
        else:
            # All CSV bytes were deterministic on this machine.
            assert source.read_bytes()==target.read_bytes(),source.name
        assert not module.diffs,(source.name,module.diffs[:3])
        checked.append(source.name)
    return checked

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True); parser.add_argument('--inventory-path',required=True)
    args=parser.parse_args(); output=Path(args.output_dir).resolve(); inventory=Path(args.inventory_path).resolve()
    if (output/'final_checks.json').exists() or inventory.exists(): raise FileExistsError('Final audit and inventory already exist.')
    if not (output/'verification.json').exists(): raise FileNotFoundError('Run the new scientific verification first.')
    baseline=read(OWN/'review-response-baseline-2026-10-07-v1/preservation.json')['baseline_files']
    bootstrap={'experiments/2026-10-06-chronology-region/REVIEW-AMENDMENT-2026-10-07.md',
               'experiments/2026-10-06-chronology-region/review_response_setup.py'}
    immutable=[]; updated=[]
    for entry in baseline:
        path=ROOT/entry['path']
        if entry['authorized_document_update']:
            assert digest(OWN/'review-response-baseline-2026-10-07-v1'/path.name)==entry['sha256']
            assert digest(path)!=entry['sha256'],path
            updated.append({'path':entry['path'],'prior_sha256':entry['sha256'],'current_sha256':digest(path)})
        else:
            assert digest(path)==entry['sha256'],path
            immutable.append(entry['path'])
    original=(OWN/'review-response-baseline-2026-10-07-v1/PROTOCOL.md').read_bytes()
    current=(OWN/'PROTOCOL.md').read_bytes()
    assert current.startswith(original)
    appended='\n\n---\n\n'+(OWN/'REVIEW-AMENDMENT-2026-10-07.md').read_text(encoding='utf-8')
    assert current[len(original):].decode('utf-8').replace('\r\n','\n')==appended
    source_manifest=read(OWN/'review-response-sources-2026-10-07-v1/sources.json')
    source_checks=[]
    for record in source_manifest['stored_source_checks']:
        assert digest(ROOT/record['local_witness'])==record['sha256']
        source_checks.append(record)
    acquired=read(RAW/'review-response-sources-2026-10-07-v1/acquisition.json')
    for record in acquired:
        if 'path' in record:
            path=ROOT/record['path']; assert path.stat().st_size==record['bytes'] and digest(path)==record['sha256']
    by_id={r['id']:r for r in source_manifest['sources']}
    assert by_id['suga2024']['title']=='Diachronic Changes in the Indus Script Based on the Proposed Arrangement of the Indus Seal'
    assert 'section 1.3/1.4 content attribution is withdrawn' in by_id['fuls2022']['use']
    assert 'Twins are not discussed' in by_id['vidale2004']['locations'][0]
    import pandas as pd
    checklist=pd.read_csv(OWN/'review-response-sources-2026-10-07-v1/external_literature_check.csv',keep_default_na=False)
    assert checklist.loc[checklist['site']=='Ur','source_id'].iloc[0]=='frenez2023'
    source_scope_checks=['Suga title','Fuls attribution withdrawn','Vidale 2004 scope','Ur checklist correction']
    # Reuse the Sonnet comparator; no legacy endpoint is edited.
    adapter=RAW/'output-adapter-replay-2026-10-07-v1'
    comparisons=[]
    for prior,current in [('main-2026-10-07-v1','output-adapter-main-2026-10-07-v1'),
                          ('exploratory-2026-10-07-v1','output-adapter-supplement-2026-10-07-v1'),
                          ('post-launch-2026-10-07-v1','output-adapter-post-launch-2026-10-07-v1')]:
        comparisons.append({'prior':prior,'rerun':(adapter/current).relative_to(ROOT).as_posix(),'identical_aggregate_files':compare_endpoints(OWN/prior,adapter/current)})
    receipts=[read(adapter/'verification-main.json'),read(adapter/'verification-supplement.json')]
    # The document generator supplies an exact, repeatable check of its tables.
    import review_documents
    for name,text in review_documents.documents().items(): assert (OWN/name).read_text(encoding='utf-8')==text,name
    registry=read(OWN/'registry-entry.json')
    assert set(registry)=={'id','theme','status','question','outcome','challenge','remedy','evidence','retry_when'}
    assert registry['status']=='Exploratory' and 'before the matched-frequency computation' in registry['remedy']
    future={inventory.resolve(),(output/'final_checks.json').resolve(),(output/'support_diagnostics.json').resolve()}
    links=[]
    for name in ['README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md']:
        document=OWN/name
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',document.read_text(encoding='utf-8')):
            if '://' in target or target.startswith('#'): continue
            path=(document.parent/target.split('#',1)[0]).resolve()
            assert path.exists() or path in future,(name,target)
            links.append({'document':name,'target':target})
    for path in registry['evidence']: assert (ROOT/path).exists() or (ROOT/path).resolve() in future,path
    syntax=[]
    for name in ['review_response_setup.py','review_response.py','run_with_output.py','verify_review_response.py',
                 'review_source_checks.py','review_documents.py','finalize_review_response.py']:
        ast.parse((OWN/name).read_text(encoding='utf-8')); syntax.append({'path':name,'sha256':digest(OWN/name)})
    process=subprocess.run([sys.executable,'-B','tools/review_prose.py','--path',str(OWN.relative_to(ROOT)),'--no-write'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',check=True)
    prose=json.loads(process.stdout); assert not prose['flags']
    # Catalogue exception promised in the amendment; no object identifiers stored.
    records=[json.loads(line) for line in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    h2590=[]
    for period in ['3B','3C']:
        matches=[r for r in records if r['site']=='Harappa' and re.fullmatch(r'Period '+period+r'(?:-\d+)?',str(r['metadata']['time']))]
        h2590.append({'period':period,'faces':len(matches),'H2590_faces':sum(2590 in [int(x) for x in re.findall(r'\bH-?(\d+)',str(r['source_cisi']),re.I)] for r in matches)})
    tests=read(OWN/'review-response-2026-10-07-v1/permutation_tests.json')['tests']
    other=read(OWN/'review-response-2026-10-07-v1/other_permutation_references.json')
    media=read(OWN/'review-response-2026-10-07-v1/media_comparisons.json')['comparisons']
    decisions=[]
    for subset in ['all','period_labelled','mound_e']:
        for statistic in ['rarefied_richness_difference','rarefied_shannon_difference_bits']:
            values=[next(r for r in media if r['subset']==subset and r['seed']==seed)['effects'][statistic]['holm_p'] for seed in [21,22]]
            decisions.append({'family':'media','comparison':subset,'statistic':statistic,'holm_values':values,'seeds_agree':(values[0]<.05)==(values[1]<.05)})
    for adjustment in ['type','type_length']:
        for unit in ['physical','text']:
            selected=[r for r in other['early_inventory'] if r['adjustment']==adjustment]
            values=[r['holm_p'] if unit=='physical' else r['text_component_sensitivity']['holm_p'] for r in selected]
            decisions.append({'family':'early_inventory','comparison':adjustment,'unit':unit,'holm_values':values,'seeds_agree':(values[0]<.05)==(values[1]<.05)})
    assert all(r['seeds_agree'] for r in decisions)
    write(output/'support_diagnostics.json',{'origin':'second post-launch amendment','status':'Exploratory','H2590_exception_counts':h2590,'other_seed_decisions':decisions,
        'main_component_label_draws':sum(r.get('permutations',0) for r in tests),
        'budget_scope':'Frequency divergence and sign tests share labels; media, external targets, early inventory and score flips have separate recorded schedules.'})
    disk=shutil.disk_usage(ROOT)
    write(output/'final_checks.json',{'origin':'second post-launch amendment','status':'Verified computation','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'immutable_files_pinned_at_archival_step':len(immutable),'original_pre_task_immutable_files':len([p for p in immutable if p not in bootstrap]),
        'new_amendment_setup_files_also_pinned':sorted(bootstrap),'authorized_document_updates':updated,
        'original_protocol_exactly_preserved_with_dated_append':True,'source_payload_hash_checks':source_checks,'new_acquisition_hash_checks':acquired,
        'attribution_checks':source_scope_checks,'output_adapter_replays':comparisons,'legacy_verification_receipts':receipts,
        'total_identical_legacy_aggregate_files':sum(len(r['identical_aggregate_files']) for r in comparisons),
        'document_generator_exact_match':True,'local_markdown_links_checked':len(links),'registry_schema_and_evidence_paths_checked':True,
        'syntax_checks':syntax,'prose_review_no_write':prose,'scientific_verification':str(output/'verification.json'),
        'disk_free_bytes':disk.free,'scope':'Preservation, sources, documentation and redirected legacy replay. Scientific checks are recorded separately.'})
    baseline_by_path={r['path']:r for r in baseline}; entries=[]
    for folder in [OWN,RAW]:
        for path in sorted(folder.rglob('*')):
            if not path.is_file() or path.resolve()==inventory: continue
            key=path.relative_to(ROOT).as_posix()
            previous=baseline_by_path.get(key)
            if previous is None or key in bootstrap: action='created'
            elif digest(path)!=previous['sha256']: action='changed'
            else: continue
            entries.append({'path':key,'action':action,'local_only':path.is_relative_to(RAW),'bytes':path.stat().st_size,'sha256':digest(path)})
    entries.append({'path':inventory.relative_to(ROOT).as_posix(),'action':'created','local_only':inventory.is_relative_to(RAW),'bytes':None,'sha256':None})
    entries.sort(key=lambda r:r['path'])
    write(inventory,{'package':'D1','origin':'second post-launch amendment','date':'2026-10-07','owned_directory':OWN.relative_to(ROOT).as_posix(),
        'local_raw_directory':RAW.relative_to(ROOT).as_posix(),'created_file_count':sum(r['action']=='created' for r in entries),
        'changed_file_count':sum(r['action']=='changed' for r in entries),'new_owned_files':sum(r['action']=='created' and not r['local_only'] for r in entries),
        'new_raw_files':sum(r['action']=='created' and r['local_only'] for r in entries),'total_new_bytes_excluding_self':sum(r['bytes'] or 0 for r in entries if r['action']=='created'),
        'baseline_note':'The amendment and setup script were created before the archival enumeration; they are counted as created here, while still checked as pinned files.',
        'self_reference':'Own bytes/hash left null to avoid recursive hashing.','files':entries})
    print(json.dumps({'immutable_pins':len(immutable),'original_immutable_files':len(immutable)-len(bootstrap),'authorized_document_updates':len(updated),
        'identical_legacy_aggregates':sum(len(r['identical_aggregate_files']) for r in comparisons),'prose_flags':len(prose['flags']),
        'created_files':sum(r['action']=='created' for r in entries),'changed_files':sum(r['action']=='changed' for r in entries)},indent=2))

if __name__=='__main__': main()
