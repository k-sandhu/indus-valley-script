"""Validate a local release; writes reports in Package O and scratch in its raw directory."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
import time
import importlib.metadata

from build_release import ROOT, HERE, RAW, M, V2, V3, P, B, S, environment, read, sha, dump, compact, csv_rows
from release_policy import Portable
from extract_images import embedded_images
import score_benchmark

def equal(expected,actual,path=''):
    """Return exact structural/numerical differences; floats tolerate only roundoff."""
    differences=[]
    if isinstance(expected,dict):
        if not isinstance(actual,dict) or set(actual)!=set(expected):
            return [dict(path=path,error='keys differ',expected=list(expected),actual=list(actual) if isinstance(actual,dict) else type(actual).__name__)]
        for key in expected:differences+=equal(expected[key],actual[key],path+'/'+str(key))
    elif isinstance(expected,list):
        if not isinstance(actual,list) or len(expected)!=len(actual):return [dict(path=path,error='length differs')]
        for i,(a,b) in enumerate(zip(expected,actual)):differences+=equal(a,b,path+'/'+str(i))
    elif isinstance(expected,float):
        if not isinstance(actual,(int,float)) or abs(expected-actual)>1e-12:differences.append(dict(path=path,expected=expected,actual=actual))
    elif expected!=actual:differences.append(dict(path=path,expected=expected,actual=actual))
    return differences

def text_fields(obj,path=''):
    if isinstance(obj,str):yield path,obj
    elif isinstance(obj,dict):
        for k,v in obj.items():yield from text_fields(v,path+'/'+str(k))
    elif isinstance(obj,list):
        for i,v in enumerate(obj):yield from text_fields(v,path+'/'+str(i))

def tokens(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?",html.unescape(text).lower())

def sequence_scan(tables,out):
    origins={}
    paths=[ROOT/'data/normalized/lipi_observed_faces.jsonl',ROOT/'data/normalized/mayig_faces.jsonl']
    for p in paths:
        if not p.exists():raise FileNotFoundError('Required contamination-screen input missing: '+str(p))
        for line in p.read_text(encoding='utf8').splitlines():
            record=json.loads(line)
            for field in ['signs_visual_ltr','signs_reading_rtl']:
                value=record.get(field,[])
                if len(value)>=2:
                    sequence=tuple(str(v).lstrip('0') or '0' for v in value)
                    origins.setdefault(sequence,[]).append(dict(input=p.relative_to(ROOT).as_posix(),record_id=record.get('record_id'),field=field))
    matches=[];tested=0
    for config in ['benchmark_rows_v1','benchmark_rows_v2','benchmark_rows_v3']:
        for row in tables[config]:
            ref=json.loads(row['reference_json'])
            units=ref.get('units',[])
            if len(units)>=2 and all(len(u.get('strict_candidate_codes',[]))==1 for u in units):
                tested+=1
                seq=tuple(str(u['strict_candidate_codes'][0]) for u in units)
                for candidate,direction in [(seq,'visual_ltr'),(seq[::-1],'reversed')]:
                    if candidate in origins:matches.append(dict(config=config,sample_index=row['sample_index'],direction=direction,sequence=list(candidate),origins=origins[candidate],disposition='Licensed independent Helsinki reading; no Lipi/Mayig parent input in build allowlist.'))
    dump(out/'sequence-overlaps.json',matches)
    return dict(source_files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)) for p in paths],
        unique_unlicensed_or_excluded_sequences=len(origins),complete_singleton_benchmark_rows_tested=tested,
        matching_directions=len(matches),disposition='Overlap alone cannot identify copying; source provenance is checked separately. Match records remain local-only.',
        match_file=(out/'sequence-overlaps.json').relative_to(ROOT).as_posix())

def prose_scan(release,tables,out):
    """Compare non-bibliographic release strings to available source bodies/OCR."""
    staged=[]
    skip={'title','authors','authors_editors','venue','source_url','url','license','source_locator','source_file','source_path','input_pointer','method_path','image_path','image_paths','data_file'}
    for config,rows in tables.items():
        for i,row in enumerate(rows):
            for field,value in row.items():
                if field in skip:continue
                if field.endswith('_json') and value:
                    for location,text in text_fields(json.loads(value)):
                        if location.split('/')[-1] not in skip:staged.append((f'data/{config}.parquet/{i}/{field}'+location,text))
                elif isinstance(value,str):staged.append((f'data/{config}.parquet/{i}/{field}',value))
    for path in release.rglob('*'):
        if path.is_file() and (path.suffix.lower() in ['.md','.json','.py','.txt','.cff'] or path.name in ['LICENSE','NOTICE','LICENSE-MIT']):
            text=path.read_text(encoding='utf-8-sig')
            # JSON metadata contains exact bibliographic titles; compare eligible values.
            if path.suffix=='.json':
                try:
                    staged += [(path.relative_to(release).as_posix()+loc,s) for loc,s in text_fields(json.loads(text)) if loc.split('/')[-1] not in skip]
                except json.JSONDecodeError:staged.append((path.relative_to(release).as_posix(),text))
            else:staged.append((path.relative_to(release).as_posix(),text))
    n=15;windows={}
    for location,text in staged:
        ts=tokens(text)
        for i in range(len(ts)-n+1):windows.setdefault(tuple(ts[i:i+n]),set()).add(location)
    candidates=[]
    focus=ROOT/'data/raw/2026-10-06-evidence-census/collections-and-datasets/focused-pass-2026-10-07'
    candidates+=list(focus.glob('*.body'))
    for base in [ROOT/'data/raw/2026-10-06-evidence-census/synthesis',ROOT/'data/raw/2026-10-06-weight-metrology']:
        candidates+=list(base.rglob('*.txt'))
    candidates+=list((ROOT/'research/corpus/primary').glob('koskenniemi*.txt'))
    matches=[];inputs=[]
    for path in sorted(set(candidates)):
        if path.stat().st_size>10_000_000:continue
        text=path.read_text(encoding='utf8',errors='replace')
        text=re.sub(r'<[^>]+>',' ',text)
        ts=tokens(text);inputs.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),bytes=path.stat().st_size))
        seen=set()
        for i in range(len(ts)-n+1):
            window=tuple(ts[i:i+n])
            if window in windows and window not in seen:
                seen.add(window);matches.append(dict(raw_source=path.relative_to(ROOT).as_posix(),matching_words=' '.join(window),staged_locations=sorted(windows[window])))
    dump(out/'prose-source-inputs.json',inputs);dump(out/'prose-overlaps.json',matches)
    return dict(window_words=n,eligible_release_strings=len(staged),raw_witnesses_compared=len(inputs),overlap_windows=len(matches),
        overlap_file=(out/'prose-overlaps.json').relative_to(ROOT).as_posix(),
        limitation='Available local text witnesses and bodies only; bibliographic titles excluded. This screen requires review of matches and does not prove a universal absence of copied prose.')

def main():
    environment()
    import datasets
    import pyarrow as pa
    import pyarrow.parquet as pq
    import yaml
    from PIL import Image
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',type=Path,default=HERE/'release')
    parser.add_argument('--out',type=Path,default=HERE/'validation.json')
    parser.add_argument('--raw-out',type=Path,default=RAW/'validation-2026-10-08-v1')
    parser.add_argument('--records',type=Path)
    args=parser.parse_args();release=args.release.resolve();out=args.out.resolve();rawout=args.raw_out.resolve()
    if args.records:args.records=args.records.resolve()
    if not out.is_relative_to(HERE) or not rawout.is_relative_to(RAW) or out.exists() or rawout.exists():
        raise ValueError('Choose new Package O report and local-raw scratch paths.')
    rawout.mkdir(parents=True)
    # Relative cache names avoid the duplicated absolute-path lock names that
    # exceed Windows' filename limit. All caches still live under Package O raw.
    os.chdir(RAW)
    card=(release/'README.md').read_text(encoding='utf8')
    metadata=yaml.safe_load(card.split('---')[1])
    manifest=read(release/'provenance/table-manifest.json')
    records=args.records or HERE/'build-records'/release.name
    if not records.exists():raise FileNotFoundError('Supply --records for the build associated with this release folder.')
    inputs=read(records/'input-manifest.json')
    portable=Portable();portable.mapping=read(records/'portable-source-map.json')
    pin_results=[dict(path=r['path'],matches=sha(ROOT/r['path'])==r['sha256']) for r in inputs]
    tables={};loads=[];failures=[]
    for config in metadata['configs']:
        name=config['config_name'];spec=manifest[name]
        data=datasets.load_dataset(str(release),name,cache_dir='revision-ds',download_mode='force_redownload')
        assert list(data)==[spec['split']]
        table=data[spec['split']]
        for key,feature in table.features.items():
            if isinstance(feature,datasets.Image):table=table.cast_column(key,datasets.Image(decode=False))
        rows=table.to_list();tables[name]=rows
        path=release/spec['data_file'];source=pq.read_table(path)
        schema=[dict(name=f.name,type=str(f.type),nullable=f.nullable) for f in source.schema]
        # Parquet renames a list child's default name from item to element.
        # Compare the element type/nullability, retaining every outer field.
        canonical=lambda s:[dict(f,type=f['type'].replace('item:','element:')) for f in s]
        ok=len(rows)==spec['rows'] and canonical(schema)==canonical(spec['schema']) and sha(path)==spec['sha256']
        logical=hashlib.sha256(compact(rows).encode()).hexdigest()
        ok=ok and logical==spec['logical_sha256']
        loads.append(dict(config=name,rows=len(rows),split=spec['split'],schema=schema,passed=ok,logical_sha256=logical))
        if not ok:failures.append('configuration:'+name)
    images=[];embedded=dict(embedded_images(release))
    import io
    for row in tables['image_assets']:
        p=(release/row['image_path']).resolve()
        assert p.is_relative_to(release)
        content=embedded[row['image_path']] if row['storage']=='embedded' else p.read_bytes()
        original=ROOT/portable.mapping[row['source_path']]
        with Image.open(io.BytesIO(content)) as im:
            format=im.format;size=list(im.size);im.verify()
        ok=format=='PNG' and hashlib.sha256(content).hexdigest()==row['sha256'] and original.read_bytes()==content
        if row['storage']=='embedded':ok=ok and not p.exists()
        images.append(dict(path=row['image_path'],storage=row['storage'],size=size,passed=ok))
        if not ok:failures.append('image:'+row['image_path'])
    dump(rawout/'image-checks.json',images)
    all_paths={r['image_path'] for r in tables['image_assets']}
    referenced=set()
    for name,rows in tables.items():
        for row in rows:
            for key,value in row.items():
                if key in ['image_path','context_image_path','exact_image_path'] and value:referenced.add(value)
                if key=='image_paths':referenced.update(value)
    assert referenced<=all_paths
    source_checks=[]
    def check(name,ok,detail):
        source_checks.append(dict(check=name,passed=bool(ok),detail=detail))
        if not ok:failures.append(name)
    check('source_pin_integrity',all(r['matches'] for r in pin_results),f'{len(pin_results)} source files')
    chart=read(P/'chart-reference-v2.1.json')['rows']
    check('chart_source_rows',len(chart)==len(tables['chart_reference'])==687,'manual reference and staged chart')
    lookup={(r['pdf_page'],r['column'],r['row']):r for r in chart}
    check('chart_selected_fields',all(all(r[k]==lookup[(r['pdf_page'],r['column'],r['row'])].get(k) for k in ['rank','code','alternatives','rank_alternatives','numeric_confidence','dashed_auxiliary']) for r in tables['chart_reference']),'Every numeric label and uncertainty field compared directly.')
    check('chart_ambiguities',sum(bool(r['alternatives']) for r in tables['chart_reference'])==0,'all 16 earlier lower-code ambiguities provisionally settled')
    from chart_changes import ChartChanges,cell_key
    changes=ChartChanges(read(ROOT/'research/chart_reference/manual_numeric_reference.json'),read(P/'chart-reference-v2.1.json'),read(P/'comparison-v2.1.json'),read(P/'impact-v2.1.json'))
    previous_ok=True
    for row in tables['chart_reference']:
        old=changes.old[row['cell_id']];changed=changes.changes.get(row['cell_id'],{})
        for key in ['code','rank','alternatives','rank_alternatives','numeric_confidence']:
            previous_ok=previous_ok and row['previous_'+key]==(old.get(key) if key in changed else None)
        previous_ok=previous_ok and set(row['changed_fields'])==set(changed) and bool(row['change_note'])==bool(changed)
    check('chart_previous_fields',previous_ok,'All five numeric previous-value columns and notes match P field deltas.')
    cov=read(S/'coverage.json')
    check('site_register',len(tables['evidence_sites'])==len(cov['sites'])==115 and all(all(row[k]==src.get(k) for k in ['site','assigned_region','local_faces','local_families','local_cisi_identifiers','IM77_main_selected_objects','IM77_count_status','ICIT_object_count','worldwide_missing_objects']) for row,src in zip(tables['evidence_sites'],cov['sites'])),'v6 selected fields')
    for config,file in [('evidence_field_completeness','field-completeness.csv'),('evidence_catalogue_coverage','catalogue-coverage.csv'),('evidence_catalogue_sections','catalogue-section-split.csv')]:
        source=csv_rows(S/file);staged=tables[config]
        ok=len(source)==len(staged)
        for a,b in zip(source,staged):
            for k,v in a.items():
                actual=b[k];v=portable.value(v)
                if isinstance(actual,(int,float)):ok=ok and float(v)==actual
                elif actual is None:ok=ok and v==''
                else:ok=ok and v==actual
        check(config,ok,'Every original CSV field compared.')
    summary=read(release/'provenance/census-summary.json')
    bc=[r for r in tables['evidence_catalogue_coverage'] if r['edition']=='CISI1-1987' and r['batch'] in ['b-gujarat-kutch-maharashtra','c-north-india']]
    check('CISI1_BC_493_327_166',len(bc)==19 and sum(r['catalogue_entries'] for r in bc)==493 and sum(r['local_matching_entries'] for r in bc)==327 and sum(r['local_absent_entry_keys'] for r in bc)==166,'19 Gujarat/north India ranges')
    check('museum_join_lower_bound',len(tables['evidence_museum_joins'])==summary['museum_joins']['confirmed_identifier_joins']==49 and all(r['cisi'] and r['cisi']!='-' and r['join_method']!='shared_field_and_published_plate' and 'Lipi' not in r['join_evidence'] and r['identifier_sources_json'] for r in tables['evidence_museum_joins']),'42 independent earlier pairs + 7 printed-catalogue supplement pairs; 19 Lipi-only joins excluded')
    # Compare fields to their parents independently of the build manifest.
    for version,base in [('v1',M),('v2',V2),('v3',V3)]:
        selection=read(base/'blind/selection.json')['rows']
        predpath=M/'portable-inputs/data/raw/2026-10-07-helsinki1979-digitization/frozen-evaluation-predictions.json' if version=='v1' else base/'predictions.json'
        preds={r['sample_index']:r for r in read(predpath)['rows']}
        refs=[]
        if version=='v1':
            for letter in 'abc':refs.extend(read(M/f'blind/reference-{letter}.json')['rows'])
        else:refs=read(base/'blind/adjudicated-reference.json')['rows']
        refs={r['sample_index']:r for r in refs};locators={r['sample_index']:r for r in selection}
        rows=tables['benchmark_rows_'+version]
        ok=len(rows)==len(selection) and all(json.loads(r['reference_json'])==portable.value(refs[r['sample_index']]) and json.loads(r['prediction_json'])==portable.value(preds[r['sample_index']]) and json.loads(r['locator_json'])==portable.value(locators[r['sample_index']]) for r in rows)
        check('benchmark_'+version+'_parent_records',ok,'Every substantive frozen reference, prediction and locator field matches; repository-only pointers use portable labels.')
        flags_ok=all(json.loads(r['reference_chart_correction_flags_json'])==changes.reference_flags(refs[r['sample_index']],version,True)
            and json.loads(r['prediction_chart_correction_flags_json'])==changes.prediction_flags(preds[r['sample_index']]) for r in rows)
        check('benchmark_'+version+'_chart_flags',flags_ok,'All unit flags match P explicit joins or template-key changed-cell joins; frozen payloads remain unchanged.')
    for config in ['benchmark_readings','benchmark_readings_v3','benchmark_count_readings','benchmark_count_readings_v3']:
        cache={};ok=True
        for row in tables[config]:
            path=portable.mapping[row['source_file']]
            if path not in cache:cache[path]=read(ROOT/path)
            parent=cache[path]['rows' if config.startswith('benchmark_readings') else 'pages']
            key='sample_index' if config.startswith('benchmark_readings') else 'pdf_page'
            original=next(r for r in parent if r[key]==row[key])
            ok=ok and json.loads(row['reading_json'])==portable.value(original)
        check(config+'_parent_records',ok,'Every reading field matches after portable pointer transformation.')
    for config,path,container,mapping in [
        ('evidence_publications',B/'sites-and-publications/publication-register.json','publications',{'publication_id':'id','title':'title','authors_editors':'authors_editors','year':'year','venue':'venue','url':'url','access_record':'opened'}),
        ('evidence_collections',B/'collections-and-datasets/collection-register.json','collections',{'institution':'institution','region':'region','confirmed_record_minimum':'result_count','count_basis':'count_basis','source_ids':'source_ids','query_date':'query_date'}),
        ('evidence_datasets',B/'collections-and-datasets/dataset-register.json','datasets',{'name':'name','count_basis':'count_basis','reported_reuse_terms':'licence','version_basis':'versioning','source_ids':'source_ids'})]:
        original=portable.value(read(path)[container]);rows=tables[config]
        if config=='evidence_publications':
            from write_release_docs import LOTHAL
            for p in original:
                if 'Lothal Sealings:' in p['title']:p['title']=LOTHAL
        ok=len(original)==len(rows) and all(all(r[k]==p.get(v) for k,v in mapping.items()) for r,p in zip(rows,original))
        if config=='evidence_collections':ok=ok and all(json.loads(r['record_fields_json'])==p.get('record_fields') for r,p in zip(rows,original))
        if config=='evidence_datasets':ok=ok and all(json.loads(r['size_json'])==p.get('size') for r,p in zip(rows,original))
        check(config+'_parent_fields',ok,'Every selected bibliographic, factual or aggregate field compared directly.')
    for config,file in [('weight_mass_bands','mass-band-estimates.csv'),('weight_chance_controls','western-chance-baselines.csv')]:
        original=csv_rows(ROOT/'experiments/2026-10-06-weight-metrology/summary-tables-review-response'/file);rows=tables[config]
        ok=len(original)==len(rows)
        for src,row in zip(original,rows):
            for k,v in src.items():
                key='null_model' if k=='null' else k
                if key.endswith('interval95'):
                    ok=ok and json.loads(v)==json.loads(row[key])
                else:
                    ok=ok and (float(v)==row[key] if isinstance(row[key],(int,float)) else v==row[key])
        check(config+'_parent_values',ok,'Every original aggregate field compared directly.')
    countref=read(V2/'blind/adjudicated-counts.json')['pages'];detection=read(V2/'count-page-detections.json')['pages']
    lookup={r['pdf_page']:r for r in countref};dlookup={r['pdf_page']:r for r in detection}
    check('count_page_parent_geometry',all(json.loads(r['reference_json'])==portable.value(lookup[r['pdf_page']]) and json.loads(r['detections_json'])==[{k:v[k] for k in ['row_anchor_y_2x','margin_xyxy_2x']} for v in dlookup[r['pdf_page']]['rows']] for r in tables['benchmark_count_pages']),'All 21 adjudicated page records and detector geometry fields.')
    countref3=read(V3/'blind/adjudicated-counts.json')['pages'];detection3=read(V3/'count-page-detections.json')['pages']
    lookup3={r['pdf_page']:r for r in countref3};dlookup3={r['pdf_page']:r for r in detection3}
    keys=['line_kind','row_anchor_y_2x','margin_pdf_box','glyph_pdf_box']
    check('v3_count_page_parent_geometry',all(json.loads(r['reference_json'])==portable.value(lookup3[r['pdf_page']])
        and json.loads(r['detections_json'])==[{k:v[k] for k in keys} for v in dlookup3[r['pdf_page']]['rows']]
        for r in tables['benchmark_count_pages_v3']),'All 21 adjudicated page records and numbered/physical-line geometry fields.')
    check('v3_frame',read(release/'benchmark/v3-selection.json')==portable.value(read(V3/'blind/selection.json')),'Every selection field matches the frozen v3 packet.')
    old_pages={r['pdf_page'] for v in ['v1','v2'] for r in tables['benchmark_rows_'+v]}
    check('v3_fresh_target_pages',not old_pages.intersection(r['pdf_page'] for r in tables['benchmark_rows_v3']),'No v3 target page occurred among the earlier 140 benchmark targets.')
    scores={}
    expected=read(release/'benchmark/expected-metrics.json')
    for version in ['v1','v2','v3']:
        start=time.perf_counter();result=score_benchmark.compute(release,version)
        dump(rawout/f'scores-{version}.json',result)
        compared={k:result[k] for k in expected[version]}
        differences=equal(expected[version],compared)
        scores[version]=dict(passed=not differences,differences=differences,summary=result['summary'],negative_result_criteria=result['negative_result_criteria'],seconds=time.perf_counter()-start,
            compared_fields=list(compared),numeric_tolerance=1e-12)
        if differences:failures.append('benchmark:'+version)
    deny={'text_code_visual_ltr','signs_visual_ltr','signs_reading_rtl','source_record_id','graphemes','metadata'}
    structural_hits=[]
    for name,rows in tables.items():
        for row in rows:
            for key in row:
                if key in deny:structural_hits.append(dict(config=name,field=key))
    check('prohibited_record_fields_absent',not structural_hits,'Top-level table schemas exclude corpus sequence, metadata and grapheme fields.')
    audit=read(records/'rights-audit.json')
    inclusions=[r for r in audit['files'] if r['decision'].startswith('include')]
    check('rights_allowlist',all(r['rights_status'] in ['own-work','explicit-license','permission-recorded'] for r in inclusions),'No mixed or unresolved rights asset included.')
    check('no_forbidden_payload_formats',not any(p.suffix.lower() in ['.pdf','.pt','.pkl','.npz','.jpg','.jpeg','.gif','.html','.body'] for p in release.rglob('*') if p.is_file()),'Stage contains Parquet, licensed PNG and authored documentation/code only.')
    sequence=sequence_scan(tables,rawout)
    prose=prose_scan(release,tables,rawout)
    files=[dict(path=p.relative_to(release).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(release.rglob('*')) if p.is_file() and p.relative_to(release).as_posix()!='provenance/file-manifest.json']
    dump(release/'provenance/file-manifest.json',files)
    result=dict(status='Verified computation' if not failures else 'Failed',local_only=True,release_ready_for_public_visibility=False,
        required_user_decisions=['Public issues repository','Hub terms for private Lipi-derived store','Final visibility switch'],
        configurations=loads,total_table_rows=sum(x['rows'] for x in loads),images=dict(count=len(images),failed=sum(not r['passed'] for r in images),all_references_resolve=referenced<=all_paths),
        source_checks=source_checks,source_pins=pin_results,benchmark_scores=scores,sequence_screen=sequence,prose_screen=prose,
        failures=failures,software={k:importlib.metadata.version(k) for k in ['datasets','pyarrow','numpy','PyYAML','Pillow','huggingface_hub']},
        python=sys.version,release_files=len(files)+1,release_bytes=sum(r['bytes'] for r in files)+(release/'provenance/file-manifest.json').stat().st_size,manifest_excludes_self=True,
        unverified=['Hosted 0.3.0 loading/viewer awaits coordinator update; coordinator reports 0.2.0 all 19 configs load.','No expert epigraphic review.','Prose-overlap matches require disposition; screen covers available witnesses only.','Public issues repository is awaiting confirmation.'])
    dump(out,result)
    print(compact(dict(status=result['status'],configs=len(loads),rows=result['total_table_rows'],images=len(images),failures=failures,prose_overlap_windows=prose['overlap_windows'],sequence_matches=sequence['matching_directions'])))
    if failures:sys.exit(1)

if __name__=='__main__':main()
