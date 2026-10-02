"""Source-keyed descriptive analysis. Full code tables stay local-only."""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import product, combinations
import json, csv, hashlib, datetime, argparse, shutil

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OLD = ROOT/'experiments/2026-10-02-six-hour/harappa-object-frame'
RAW = ROOT/'data/raw/2026-10-02-connections-and-priority/harappa-short-records'
FORM = {'700':'A','861':'D','154':'C','156':'C'}
COUNT = {'003':3,'033':3,'034':4}
SIDES = ['top','middle','bottom']

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def csv_write(p,rows):
    if not rows:
        return
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def signature(modules):
    return tuple(sorted(tuple(m) for m in modules))

def orbit_key(modules,reflection=False):
    t=tuple(tuple(x) for x in modules)
    candidates=[t[k:]+t[:k] for k in range(3)]
    if reflection:
        rev=t[::-1]
        candidates += [rev[k:]+rev[:k] for k in range(3)]
    return min(candidates)

def run(label):
    out=BASE/label
    local=RAW/label
    if out.exists() or local.exists():
        raise FileExistsError('Endpoint exists; choose a fresh label.')
    obs=read(BASE/'observations.json')
    endpoint=read(OLD/'annotated/results.json')
    all_rows=[json.loads(x) for x in (ROOT/'data/normalized/lipi_observed_faces.jsonl').read_text(encoding='utf-8').splitlines()]
    by_key=defaultdict(list)
    for r in all_rows:
        by_key[r['source_cisi']].append(r)
    physical=[o for o in endpoint['physical_objects'] if o.get('target_id') and 2218 <= int(o['target_id'][2:]) <= 2239]
    old_face={(r['observation_id'],r['side']):r for r in endpoint['face_observations'] if r.get('side') in SIDES}
    crop={r['specimen']:r for r in read(OLD/'figure4-native-crop-manifest.json')['crops']}
    index=read(ROOT/'data/lipi/src/assets/data/seal_id_and_image_mapping.json')
    assets=[p.name for p in (ROOT/'data/lipi/public/seal_images').iterdir() if p.is_file()]
    objects,faces,joins,locators=[],[],[],[]
    for o in sorted(physical,key=lambda x:x['target_id']):
        key=o['target_id']; specimen=o['source_coordinate']['specimen']
        rs=sorted(by_key[key],key=lambda x:x['record_id'])
        modules=[]; family_rows={}
        for r in rs:
            code=r['signs_visual_ltr']
            assert len(code)==2 and code[0] in FORM and code[1] in COUNT
            family=FORM[code[0]]
            modules.append(tuple(code))
            family_rows[family]=r
        assert set(family_rows)=={'C','A','D'}
        group=o['published_engraver_group']['value']
        dep=o['deposition_association']['value']
        known={}
        source_views=[]
        for k,side in enumerate(SIDES):
            f=old_face[(o['observation_id'],side)]
            family=f.get('descriptive_form')
            position=f.get('form_position_beside_strokes')
            if family is None and side=='top':
                family='C'
            n=obs['counts_by_displayed_specimen'][str(specimen)][k]
            candidates=[n] if n is not None else [3,4]
            if family is not None:
                known[family]=candidates
            source_views.append({'side':side,'family':family,'position':position,'count_candidates':candidates})
            faces.append({'target_id':key,'source_specimen':specimen,'source_registration':o['registration']['literal'],'published_engraver_group':group,'deposition_association':dep,'displayed_side':side,'observed_family':family,'displayed_form_position':position,'direct_stroke_count':n,'conditional_stroke_candidates':'|'.join(map(str,candidates)),'family_status':'unresolved' if family is None else 'broad visible source family','count_basis':'source-pixel reading' if n is not None else 'published cohort three-or-four domain','matched_derivative_record_by_family':family_rows[family]['record_id'] if family else None,'alignment_scope':'family-correspondence only; physical orientation unassigned','crop_path':crop[specimen]['path'],'crop_sha256':crop[specimen]['sha256']})
        # Complete missing broad family only under the published repeated-inventory premise.
        conditional_known=dict(known)
        for family in ['C','A','D']:
            conditional_known.setdefault(family,[3,4])
        counts={fam:COUNT[family_rows[fam]['signs_visual_ltr'][1]] for fam in ['C','A','D']}
        module_by_family={fam:family_rows[fam]['signs_visual_ltr'] for fam in ['C','A','D']}
        completions=list(product(*(conditional_known[fam] for fam in ['C','A','D'])))
        photos=index.get(key,[])
        filenames=[n for n in assets if n.split('_')[0]==key]
        objects.append({'target_id':key,'source_specimen':specimen,'registration':o['registration'],'published_engraver_group':group,'deposition_association':dep,'phase':o['phase'],'imported_row_ids':[r['record_id'] for r in rs],'source_views':source_views,'conditional_count_candidates_C_A_D':conditional_known,'conditional_completions_C_A_D':completions,'derivative_counts_C_A_D':counts,'derivative_modules_by_family':module_by_family,'exact_module_signature':signature(modules),'ordered_derivative_modules':modules,'image_index_references':photos,'image_asset_filename_matches':filenames,'derivative_dimensions_mm':{k:rs[0]['metadata'].get(k) for k in ['horizontal(mm)','vertical(mm)','thickness(mm)']},'dimension_basis':'unverified derivative metadata; source figure has scale, no individual reported dimensions'})
        for r in rs:
            joins.append({'target_id':key,'source_specimen':specimen,'source_registration':o['registration']['literal'],'source_group':group,'source_deposition':dep,'imported_record':r})
        locators.append({'target_id':key,'specimen':specimen,'registration':o['registration']['literal'],'figure':4,'pdf_page':15,'displayed_author_page':14,'mapped_book_page':334,'caption_pdf_page':16,'crop_path':crop[specimen]['path'],'crop_sha256':crop[specimen]['sha256'],'crop_bounds_xyxy':crop[specimen]['pixel_bounds_xyxy']})
    assert len(objects)==22 and len(faces)==66
    grouped=defaultdict(list)
    for o in objects:
        grouped[signature(o['ordered_derivative_modules'])].append(o['target_id'])
    exact_groups=list(grouped.values())
    representation={}
    for name,key_func in [('fixed_imported_row_order',lambda m:tuple(m)),('cyclic_imported_row_rotation',lambda m:orbit_key(m)),('rotation_and_imported_row_reversal',lambda m:orbit_key(m,True)),('unordered_exact_modules',signature),('unordered_broad_family_and_stroke_count',lambda m:tuple(sorted((FORM[a],COUNT[b]) for a,b in m)))]:
        g=defaultdict(list)
        for o in objects:
            g[key_func(o['ordered_derivative_modules'])].append(o['target_id'])
        representation[name]={'classes':len(g),'class_sizes':sorted([len(v) for v in g.values()],reverse=True),'same_class_object_pairs':sum(len(v)*(len(v)-1)//2 for v in g.values()),'scope':'Imported face serialization only; no physical prism order has been established.'}
    exact_pairs,source_pairs=[],[]
    for a,b in combinations(objects,2):
        differing=[fam for fam in ['C','A','D'] if a['derivative_modules_by_family'][fam]!=b['derivative_modules_by_family'][fam]]
        count_diff=[fam for fam in ['C','A','D'] if a['derivative_counts_C_A_D'][fam]!=b['derivative_counts_C_A_D'][fam]]
        exact_pairs.append({'object_a':a['target_id'],'object_b':b['target_id'],'exact_module_difference_count':len(differing),'changed_families':'|'.join(differing),'stroke_count_difference_count':len(count_diff),'changed_count_families':'|'.join(count_diff),'same_source_deposit':a['registration']['excavation_unit']==b['registration']['excavation_unit'],'same_published_engraver_group':a['published_engraver_group']==b['published_engraver_group']})
        ds={sum(x!=y for x,y in zip(u,v)) for u in a['conditional_completions_C_A_D'] for v in b['conditional_completions_C_A_D']}
        source_pairs.append({'object_a':a['target_id'],'object_b':b['target_id'],'conditional_min_count_differences':min(ds),'conditional_max_count_differences':max(ds),'compatible_identical_count_profile':0 in ds,'compatible_one_changed_count':1 in ds})
    native_known=[f for f in faces if f['direct_stroke_count'] is not None]
    family_count=Counter((f['observed_family'],f['direct_stroke_count']) for f in native_known)
    complete_source=[o for o in objects if all(len(v)==1 for v in o['conditional_count_candidates_C_A_D'].values())]
    profile_bounds={}
    for prof in [(3,3,3),(3,3,4),(3,4,4),(4,4,4)]:
        key=''.join(map(str,prof))
        options=[{tuple(sorted(c)) for c in o['conditional_completions_C_A_D']} for o in objects]
        profile_bounds[key]={'certain_objects':sum(s=={prof} for s in options),'possible_objects':sum(prof in s for s in options)}
    expected=(3,4,3)
    module_profile_bound={'certain_objects':sum(set(map(tuple,o['conditional_completions_C_A_D']))=={expected} for o in objects),'possible_objects':sum(expected in set(map(tuple,o['conditional_completions_C_A_D'])) for o in objects),'profile_order':['C','A','D'],'counts':expected}
    scope_group=[]
    for group in [1,2,3]:
        sub=[o for o in objects if o['published_engraver_group']==group]
        nf=[f for f in native_known if f['published_engraver_group']==group]
        scope_group.append({'published_group':group,'objects':len(sub),'deposition_associations':dict(Counter(o['deposition_association'] for o in sub)),'directly_counted_faces':len(nf),'complete_count_profiles':sum(o in complete_source for o in sub),'derivative_count_profiles_C_A_D':dict(Counter(str(tuple(o['derivative_counts_C_A_D'][f] for f in ['C','A','D'])) for o in sub))})
    comparison_keys=['H-1682','H-1710','H-1714']
    comparison_rows=[r for r in all_rows if r['source_cisi'] in comparison_keys]
    summary={
      'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'scope':'Exploratory real source/corpus study; 22 source-defined tablets, 66 faces; no simulated inputs.',
      'objects':22,'faces':66,'complete_clean_two_code_rows':sum(r['imported_record']['clean_rtl_singleline'] and r['imported_record']['complete_observed'] and r['imported_record']['length']==2 for r in joins),
      'exact_unordered_module_set_class_sizes':sorted(map(len,exact_groups),reverse=True),
      'exceptions':[{'target_id':o['target_id'],'source_specimen':o['source_specimen'],'published_engraver_group':o['published_engraver_group'],'deposition_association':o['deposition_association'],'changed_field': 'A stroke token: three long bars rather than four' if o['target_id']=='H-2238' else 'C graphic variant: straight rather than branching internal arrangement','source_count_verification':'A count unreadable in individually registered drawing' if o['target_id']=='H-2238' else 'fine variant remains a derivative graphic assignment; source authors report microscopic production groups'} for o in objects if o['target_id'] in ['H-2238','H-2237']],
      'representations':representation,
      'pair_counts':{'all_object_pairs':len(exact_pairs),'exact_same_modules':sum(r['exact_module_difference_count']==0 for r in exact_pairs),'exact_one_module_changed':sum(r['exact_module_difference_count']==1 for r in exact_pairs),'exact_two_modules_changed':sum(r['exact_module_difference_count']==2 for r in exact_pairs),'count_only_changes':sum(r['exact_module_difference_count']==1 and r['stroke_count_difference_count']==1 for r in exact_pairs),'graphic_variant_only_changes':sum(r['exact_module_difference_count']==1 and r['stroke_count_difference_count']==0 for r in exact_pairs)},
      'derivative_family_count_table':[{'family':family,'count':n,'faces':sum(o['derivative_counts_C_A_D'][family]==n for o in objects)} for family in ['C','A','D'] for n in [3,4]],
      'native_source':{'directly_counted_faces':len(native_known),'unassigned_count_faces':66-len(native_known),'direct_family_count_table':[{'family':fam,'count':n,'faces':v} for (fam,n),v in sorted(family_count.items())],'complete_count_profile_objects':len(complete_source),'complete_count_profile_specimens':[o['source_specimen'] for o in complete_source],'complete_count_profile_keys':[o['target_id'] for o in complete_source],'source_count_compatible_with_imported_count':sum(f['direct_stroke_count']==COUNT[by_key[f['target_id']][next(i for i,r in enumerate(by_key[f['target_id']]) if FORM[r['signs_visual_ltr'][0]]==f['observed_family'])]['signs_visual_ltr'][1]] for f in native_known),'direct_broad_family_faces':sum(f['observed_family'] is not None for f in faces),'unresolved_broad_family_faces':sum(f['observed_family'] is None for f in faces),'conditional_count_profile_bound':module_profile_bound,'conditional_sorted_count_profile_bounds':profile_bounds,'conditional_four_stroke_family_bounds':[{'family':fam,'minimum':sum(o['conditional_count_candidates_C_A_D'][fam]==[4] for o in objects),'maximum':sum(4 in o['conditional_count_candidates_C_A_D'][fam] for o in objects)} for fam in ['C','A','D']],'pair_bounds':{'certain_identical_count_profile_pairs':sum(r['conditional_max_count_differences']==0 for r in source_pairs),'possible_identical_count_profile_pairs':sum(r['compatible_identical_count_profile'] for r in source_pairs),'possible_one_count_difference_pairs':sum(r['compatible_one_changed_count'] for r in source_pairs),'certain_one_count_difference_pairs':sum(r['conditional_min_count_differences']==r['conditional_max_count_differences']==1 for r in source_pairs)},'bounds_premises':'Three-or-four domain and one C/A/D face per object as published; unreadable bottom families are completed conditionally, and counts are free across missing faces.'},
      'production_and_deposit_summary':scope_group,
      'photo_panels':{'registered_individual_joins':0,'panels':9,'direct_counts':8,'ambiguous_counts':1,'group2_A_count_candidates':[3,4],'separate_observer_review':'root informed image reading; three prominent grooves plus unresolved narrow left trace'},
      'image_routes':{'indexed_tablet_keys':sum(bool(o['image_index_references']) for o in objects),'matching_asset_filename_tablet_keys':sum(bool(o['image_asset_filename_matches']) for o in objects),'registered_native_drawing_crops':22,'unregistered_cohort_photographs':2},
      'comparison':{'source_defined_keys':comparison_keys,'records':len(comparison_rows),'same_context_seal':'H-1682','same_context_seal_export_length':by_key['H-1682'][0]['length'],'published_description':'Three additional signs precede the shared C-plus-three-stroke set, PDF17/author16. The imported row has four tokens, so the two segmentations remain separate.','exact_export_C_module_match':'H-2237 carries the same C variant and short-three-stroke module as H-1682; the other 21 carry the alternate C variant.'},
      'local_outputs':{'joined_rows':str((local/'joined_rows.jsonl').relative_to(ROOT)).replace('\\','/'),'objects':str((local/'objects.json').relative_to(ROOT)).replace('\\','/'),'source_faces_csv':str((local/'source_faces.csv').relative_to(ROOT)).replace('\\','/'),'pair_tables':str(local.relative_to(ROOT)).replace('\\','/')},
      'interpretation_scope':'Counts are visible strokes and module tokens. No numerical unit, commodity content, named referent or physical oriented-face map is supplied.'
    }
    inputs=[BASE/'PROTOCOL.md',BASE/'observations.json',OLD/'annotated/results.json',OLD/'figure4-native-crop-manifest.json',OLD/'figure4-caption-ledger.json',OLD/'corrections/2026-10-02-scale-and-pagination/correction.json',ROOT/'data/normalized/lipi_observed_faces.jsonl',ROOT/'data/lipi/src/assets/data/seal_id_and_image_mapping.json',ROOT/'data/lipi/src/assets/fonts/indus-font.woff2',ROOT/'research/literature/sources/meadow_kenoyer_2000_tiny_seals.pdf',ROOT/'research/corpus/plate_audit/H2238_gallery/harappa_three_groups.jpg',ROOT/'research/corpus/plate_audit/H2238_gallery/harappa_slide79.jpg',ROOT/'research/corpus/plate_audit/H2238_gallery/gallery_provenance_observations.json']
    out.mkdir(parents=True);local.mkdir(parents=True)
    dump(local/'objects.json',objects)
    (local/'joined_rows.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in joins),encoding='utf-8')
    csv_write(local/'source_faces.csv',faces)
    csv_write(local/'exact_module_pairs.csv',exact_pairs)
    csv_write(local/'conditional_source_count_pairs.csv',source_pairs)
    (local/'comparison_rows.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in comparison_rows),encoding='utf-8')
    summary['local_output_hashes']=[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(local.iterdir())]
    dump(out/'results.json',summary)
    dump(out/'source-locators.json',{'source_url':'https://www.harappa.com/sites/default/files/pdf/Kenoyer2000_The%20Tiny%20Steatite%20Seals%20of%20Harappa.pdf','rights_status':'rights-unverified, source witnesses local-only','source_hashes':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':digest(p),'bytes':p.stat().st_size} for p in inputs],'registered_crop_locators':locators,'gallery_photo_routes':obs['gallery_photo']})
    shutil.copyfile(__file__,out/'code_snapshot.py')
    dump(out/'protocol-capture.json',{'path':str((BASE/'PROTOCOL.md').relative_to(ROOT)).replace('\\','/'),'sha256':digest(BASE/'PROTOCOL.md'),'observations_sha256':digest(BASE/'observations.json')})
    print(json.dumps({'endpoint':str(out.relative_to(ROOT)),'local_dataset':str(local.relative_to(ROOT)),'summary':summary},ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--endpoint',default='main-v1');args=ap.parse_args();run(args.endpoint)
