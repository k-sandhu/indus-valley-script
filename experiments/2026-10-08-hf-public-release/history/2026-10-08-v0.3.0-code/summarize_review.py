"""Summarize redirected reviewer outputs without copying third-party match text."""
from collections import Counter
import argparse
from pathlib import Path
from build_release import HERE,RAW,read,dump,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--version',default='v8');p.add_argument('--aggregate-version',default='v9');a=p.parse_args()
    version=a.version;aggregate=a.aggregate_version
    if (HERE/f'validation-2026-10-08-{aggregate}.json').exists() or (HERE/f'review-rerun-2026-10-08-{version}.json').exists():raise FileExistsError('Preserve prior aggregate validation; choose fresh version labels.')
    r=RAW/('rr'+version.removeprefix('v'));runs=read(r/'rerun-summary.json');loads=read(r/'load-check.json');images=read(r/'image-audit.json');scores=read(r/'score-comparison.json');fields=read(r/'field-definitions-check.json');manifest=read(r/'manifest-check.json');privacy=read(r/'privacy-scan.json');sequences=read(r/'rights-scan-sequences.json');prose=read(r/'rights-scan-prose.json')
    classes={
        'benchmark_readings.parquet':'Project-authored frozen readings mirrored by other project packages; CC0 additions to CC BY edition content.',
        'benchmark_rows_v1.parquet':'Project-authored frozen predictions/readings; edition-derived content retains CC BY.',
        'benchmark_rows_v2.parquet':'Project-authored frozen predictions/readings mirrored in project manifests.',
        'benchmark_count_pages.parquet':'Project-authored source-count reading notes.',
        'evidence_museum_joins.parquet':'Project-authored citation strings and identifier facts; 49 independently supported pairs.',
        'README.md':'Exact bibliographic titles/publisher strings and own project descriptions.',
        'NOTICE':'Required exact source attribution.',
        'CITATION.cff':'Exact bibliographic publisher/title strings.',
        'benchmark/CONVENTIONS.md':'Project-authored reading rules and exact attribution.',
        'benchmark/v2-adjudication-notes.json':'Project-authored source adjudication notes.',
        'benchmark/v1-exploratory-adjudication-overlay.json':'Project-authored later correction notes.',
        'benchmark/reader-metadata.json':'Project-authored process disclosures.',
        'LICENSES/CC-BY-4.0.txt':'Official licence text, permitted reproduction.',
        'LICENSES/CC0-1.0.txt':'Official licence text, permitted reproduction.',
        'LICENSES/Unlicense.txt':'Official licence text, permitted reproduction.',
        'docs/METHODS.md':'Exact Ascalone bibliographic title.',
        'evidence_sources.parquet':'Project-authored access assessment of museum reuse policy, mirrored in the project search capture; no quoted policy prose.'}
    classes.update({name:'Project-authored v3 reading/convention/freeze record with Helsinki attribution; CC0 additions to CC BY edition content.' for name in [
        'benchmark_readings_v3.parquet','benchmark_rows_v3.parquet','benchmark/CONVENTIONS-v3.md','benchmark/v3-freeze-manifest.json',
        'benchmark/v3-adjudication-notes.json','benchmark_count_pages_v3.parquet','benchmark_count_readings_v3.parquet']})
    details=read(r/'scan/prose-8word-matches.json');unknown=[];classified=Counter()
    for match in details:
        dispositions=set()
        for location in match['staged']:
            name=location.split('[')[0]
            if name not in classes:unknown.append(name)
            else:dispositions.add(classes[name])
        for disposition in dispositions:classified[disposition]+=1
    # The original scanner deliberately flags public account IDs too.
    unauthorized_privacy=[x for x in privacy if x['match'] not in ('k-sandhu','ksaw008')]
    reviewer_unchanged=all(sha(HERE/'review'/name)==value['source_sha256'] for name,value in runs['scripts'].items())
    validation=read(HERE/f'validation-2026-10-08-{version}.json')
    hit_details=read(r/'scan/sequence-hit-details.json')
    non_sequence=[x for x in hit_details if x['category']=='generic_int_list' and x['staged_locator'].endswith('/agreement/strict_codes_agreed_units')]
    unexplained_sequences=[x for x in hit_details if x not in non_sequence]
    checks=dict(all_reviewer_scripts_completed=all(x['completed'] for x in runs['scripts'].values()),reviewer_scripts_unchanged=reviewer_unchanged,
        loads=loads['names_match_yaml'] and len(loads['configs'])==len(validation['configurations']) and all(x['rows_match_card'] and x['paths_exist'] for x in loads['configs'].values()),
        images=images['images']==images['sha256_matches_table']==images['parent_files_present']==images['staged_bytes_equal_parent']==validation['images']['count'],
        field_definitions=not fields['problems'],score_reproduction=all(not x['vs_package_M']['mismatch'] and not x['vs_package_M']['only_in_reference'] and not x['vs_package_M']['only_in_staged'] for x in scores.values()),
        manifests=not manifest['checksum_mismatches'] and not manifest['table_checksum_mismatches'] and not manifest['in_manifest_not_on_disk'] and manifest['on_disk_not_in_manifest']==['provenance/file-manifest.json'],
        no_private_privacy_hits=not unauthorized_privacy,prose_all_matches_disposed=not unknown,
        no_unexplained_sequence_runs=not unexplained_sequences,
        sequence_controls=sequences['_positive_control_planted_unlicensed_sequences']['detected_in_full']==200 and sequences['_positive_control_with_ambiguous_positions']['detected_in_full']==200)
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,outputs=r.relative_to(HERE.parents[1]).as_posix(),adaptations=runs['adaptations'],
        images=images,score_comparison=scores,field_definitions=fields,sequence_scan=sequences,
        sequence_dispositions=dict(non_sequence_index_lists=len(non_sequence),locators=[x['staged_locator'] for x in non_sequence],
            basis='Every hit is a zero-based list of agreed unit positions under agreement.strict_codes_agreed_units, repeated in the adjudication reading and reference. Parent-record validation preserves these fields. No graphic-code run matched.',unexplained=len(unexplained_sequences)),
        prose=dict(summary=prose,disposition_counts=dict(classified),unknown_staged_locations=sorted(set(unknown)),unexplained_copied_third_party_prose_matches=0 if not unknown else None,classification_note='Counts can overlap when one window appears in several locations. Match text remains local raw; exact bibliographic and official legal text are permitted. Project reader/join/assessment matches were sampled by location and witness.'),
        privacy=dict(original_distinct_match_locations=len(privacy),authorized_matches=privacy,unauthorized_matches=unauthorized_privacy,strict_scan_report=f'review-fixes-check-2026-10-08-{version}.json#/privacy'),hosted_snippets=runs['hosted_snippets'],source_script_records=runs['scripts'])
    dump(HERE/f'review-rerun-2026-10-08-{version}.json',result)
    v=read(HERE/f'validation-2026-10-08-{version}.json');fix=read(HERE/f'review-fixes-check-2026-10-08-{version}.json')
    combined=dict(v,validation_revision=f'{aggregate}: consolidated {version} arithmetic and review checks',base_validation=f'validation-2026-10-08-{version}.json',review_rerun=f'review-rerun-2026-10-08-{version}.json',review_fix_checks=f'review-fixes-check-2026-10-08-{version}.json',review_checks=checks,cff=fix['cff'],official_license_texts_equal=fix['official_license_texts_equal'],privacy=fix['privacy'],prediction_validation_cases=fix['prediction_cases'])
    combined['unverified']=[x for x in combined['unverified'] if not x.startswith('Prose-overlap')]
    if result['status']=='Failed' or fix['status']=='Failed':combined['status']='Failed'
    dump(HERE/f'validation-2026-10-08-{aggregate}.json',combined)
    print(result['status'],checks)

if __name__=='__main__':main()
