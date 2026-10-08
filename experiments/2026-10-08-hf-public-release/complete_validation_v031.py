"""Consolidate 0.3.1 arithmetic, format, preservation and reviewer checks."""
from collections import Counter
from build_release import HERE,RAW,read,dump,sha

def main():
    out=HERE/'validation-2026-10-08-v43.json'
    if out.exists():raise FileExistsError(out)
    r=RAW/'rr41';runs=read(r/'rerun-summary.json');loads=read(r/'load-check.json');images=read(r/'image-audit.json');scores=read(r/'score-comparison.json');fields=read(r/'field-definitions-check.json');manifest=read(r/'manifest-check.json');privacy=read(r/'privacy-scan.json');sequences=read(r/'rights-scan-sequences.json');prose=read(r/'rights-scan-prose.json');readings=read(r/'readings-flag-check.json');snippets=read(r/'readme-snippets.json');chart=read(r/'chart-check.json');flags=read(r/'flag-check.json');content=read(r/'v3-content-check.json')
    classes={name:'Project-authored frozen reading, prediction, process or convention record; licensed edition content plus CC0 additions.' for name in ['benchmark_readings.parquet','benchmark_readings_v3.parquet','benchmark_rows_v1.parquet','benchmark_rows_v2.parquet','benchmark_rows_v3.parquet','benchmark_count_pages.parquet','benchmark_count_pages_v3.parquet','benchmark_count_readings_v3.parquet','benchmark/CONVENTIONS.md','benchmark/CONVENTIONS-v3.md','benchmark/v2-adjudication-notes.json','benchmark/v3-adjudication-notes.json','benchmark/v1-exploratory-adjudication-overlay.json','benchmark/reader-metadata.json','benchmark/v3-freeze-manifest.json','provenance/chart-changes.json']}
    classes.update({name:'Exact bibliographic attribution, public method description or project-authored chart review note.' for name in ['README.md','NOTICE','CITATION.cff','docs/METHODS.md','docs/CHART-REVIEW.md','sources.json']})
    classes.update({name:'Official licence text, permitted reproduction.' for name in ['LICENSES/CC-BY-4.0.txt','LICENSES/CC0-1.0.txt','LICENSES/Unlicense.txt']})
    classes.update({'evidence_museum_joins.parquet':'Own citation strings and identifier facts from independently cited catalogues.','evidence_sources.parquet':'Own access-scope assessment, mirrored in saved search records.'})
    matches=read(r/'scan/prose-8word-matches.json');unknown=[];dispositions=Counter()
    for match in matches:
        for name in {x.split('[')[0] for x in match['staged']}:
            if name not in classes:unknown.append(dict(witness=match['witness'],staged=name))
            else:dispositions[classes[name]]+=1
    hit_details=read(r/'scan/sequence-hit-details.json')
    non_sequence=[x for x in hit_details if x['category']=='generic_int_list' and x['staged_locator'].endswith('/agreement/strict_codes_agreed_units')]
    unexplained_sequence=[x for x in hit_details if x not in non_sequence]
    unauthorized=[];privacy_dispositions=[]
    for hit in privacy:
        allowed=hit['match'] in ['k-sandhu','ksaw008']
        reason='Owner-approved public author/namespace.' if allowed else None
        if hit['match']=='data/raw' and hit['where']=='./benchmark/reader-metadata.json':allowed=True;reason='Bare generic directory phrase in preserved reader process disclosure; no private path.'
        if hit['match']=='research/' and hit['where'].endswith('evidence_sources.parquet:venue'):allowed=True;reason='Case-insensitive match to the access category Research/archive pages, not a filesystem path.'
        if not allowed:unauthorized.append(hit)
        privacy_dispositions.append(dict(where=hit['where'],match=hit['match'],count=hit['count'],allowed=allowed,basis=reason))
    base=read(HERE/'validation-2026-10-08-v41.json');fix=read(HERE/'review-fixes-check-2026-10-08-v41.json');prediction=read(HERE/'prediction-format-2026-10-08-v41.json');reading=read(HERE/'reading-flags-2026-10-08-v41.json');rebuild=read(HERE/'rebuild-comparison-2026-10-08-v42.json')
    expected_differences={'corrected_cell_units':{'impact':12,'release':20},'class_metadata_units':{'impact':6,'release':7}}
    checks=dict(all_review_scripts_completed=all(v['completed'] for v in runs['scripts'].values()),review_scripts_unchanged=all(sha(HERE/'review-0.3.0'/name)==v['source_sha256'] for name,v in runs['scripts'].items()),
        loads=loads['n_hub']==loads['n_yaml']==23 and loads['names_equal_yaml'] and all(all(row[k] for k in ['rows_match_card','rows_equal_local','columns_equal','arrow_schema_equal_names_types','cells_equal_local']) for row in loads['configs'].values()),
        images=images['checked']==images['hash_and_size_match_table']==images['decoded']==images['parent_found_by_sha256']==1142,
        scores=all(not v['vs_package_M']['mismatch'] and not v['vs_package_M']['only_in_reference'] and not v['vs_package_M']['only_in_staged'] for v in scores.values()),
        field_definitions=not fields['problems'],manifest=not manifest['checksum_mismatches'] and not manifest['table_checksum_mismatches'] and not manifest['in_manifest_not_on_disk'] and manifest['on_disk_not_in_manifest']==['provenance/file-manifest.json'],
        chart=chart['p_vs_table_mismatch_count']==0 and not chart['previous_value_errors'] and not chart['changed_fields_errors'] and not chart['change_note_presence_errors'] and chart['images_not_equal_count']==0,
        reference_prediction_flags=all(all(v[k] for k in ['flag_units_equal_reference_units','direct_units_equal','identity_review_units_equal','corrected_cell_units_equal','corrected_cell_flag_matches_cells','class_metadata_units_equal','locator_conflicts_equal']) and not v['potential_mapping_payload_mismatches'] and not v['changed_fields_mismatches'] and not v['prediction_flag_mismatches'] for k,v in flags.items() if k in ['v1','v2','v3']),
        v3_content=content['rows']==80 and content['readings_rows']==240 and content['count_pages']==21 and content['count_readings']==42 and content['v3_cards']==12 and content['sample_indices_0_79'] and content['count_pages_set_equal_M'] and not any(content[k] for k in ['context_image_bytes_not_equal_M','exact_image_bytes_not_equal_M','image_path_columns_not_equal_expected','locator_mismatches','section_or_page_mismatches','count_readings_not_equal_M','v3_cards_not_equal_M','image_assets_loose_hash_bad']) and not any(content['readings_not_equal_M'].values()) and not any(content['count_pages_mismatches'].values()),
        reading_flags=reading['status']=='Verified computation' and readings['groups_with_differences']==['v2/B/independent'] and next(g['differences'] for g in readings['groups'] if g['group']=='v2/B/independent')==expected_differences and not readings['v3_readings']['independent_mismatches'],
        prediction_format=prediction['status']=='Verified computation' and all(v['returncode']==0 and all(v[k] for k in ['summary_equal_baseline','rows_equal_baseline','bootstrap_equal_baseline']) for v in snippets['minimal_format'].values()),
        malformed_predictions_rejected=all(c['returncode']!=0 for c in snippets['failing_cases'].values()),local_card_snippets=all(x['ok'] for x in snippets['run']),
        privacy=not unauthorized and not fix['privacy']['hits'],cff=not fix['cff']['errors'] and 'license' not in __import__('yaml').safe_load((HERE/'release/CITATION.cff').read_text()),official_license_texts=all(fix['official_license_texts_equal'].values()),
        sequence_runs=not unexplained_sequence,sequence_controls=sequences['_positive_control_planted_unlicensed_sequences']['detected_in_full']==200 and sequences['_positive_control_with_ambiguous_positions']['detected_in_full']==200,
        prose=not unknown,rebuild_and_preservation=rebuild['status']=='Verified computation')
    review=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,source_script_records=runs['scripts'],adaptations=runs['adaptations'],local_card_snippets=snippets,score_comparison=scores,chart=chart,reading_flags=readings,field_definitions=fields,images=images,
        privacy=dict(dispositions=privacy_dispositions,unauthorized_matches=unauthorized,strict_hits=fix['privacy']['hits']),sequence_scan=sequences,sequence_dispositions=dict(non_sequence_index_lists=len(non_sequence),unexplained=len(unexplained_sequence),locators=[x['staged_locator'] for x in non_sequence]),
        prose=dict(summary=prose,disposition_counts=dict(dispositions),unknown_staged_locations=unknown,unexplained_copied_third_party_prose_matches=0 if not unknown else None,scope='Location/witness comparisons; text stays raw. Bibliography and official licence texts are permitted; source provenance distinguishes project mirrors from third-party prose.'),rights_field_comparison=read(r/'rights-scan-fields.json'),outputs='data/raw/2026-10-08-hf-public-release/rr41')
    dump(HERE/'review-rerun-2026-10-08-v41.json',review)
    final=dict(base,release_version='0.3.1',validation_revision='v43 consolidates new v41 tests and v42 rebuild',base_validation='validation-2026-10-08-v41.json',review_rerun='review-rerun-2026-10-08-v41.json',review_checks=checks,
        prediction_format=prediction,reading_flags=reading,cff=fix['cff'],cff_license_key_absent=True,privacy=fix['privacy'],official_license_texts_equal=fix['official_license_texts_equal'],rebuild=rebuild,
        hosted_previous_version=dict(version='0.3.0',commit='541766d5ea8a4c3b3ec5fcc416ee764af8763afb',configurations=23,rows=3308,files_equal=136,evidence='REVIEW-0.3.0.md and review-0.3.0/hub-load-check.json, hub-file-compare.json; reviewer read-only observation reused'),
        unverified=['Hosted 0.3.1 remains a coordinator check after upload.','Public viewer remains unchecked; private 0.3.0 datasets-server returned HTTP 501.','Chart and benchmark references lack expert review.','Public issues URL is awaiting owner confirmation.','Private-store terms and final visibility remain owner decisions.'])
    if not all(checks.values()) or any(v['status']!='Verified computation' for v in [base,fix,prediction,reading,rebuild]):final['status']='Failed'
    dump(out,final);print(final['status'],checks)
    if final['status']=='Failed':raise SystemExit(1)

if __name__=='__main__':main()
