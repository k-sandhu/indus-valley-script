"""Independent 0.3.0 preservation, flag, sensitivity and rebuild checks."""
from pathlib import Path
import argparse
import copy
import json
import pyarrow.parquet as pq
from build_release import HERE,RAW,ROOT,P,M,V3,read,sha,dump,environment
from validate_release import equal


def main():
    environment();ap=argparse.ArgumentParser();ap.add_argument('--rebuild',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--records',type=Path,default=HERE/'build-records/r35');args=ap.parse_args()
    if args.out.exists():raise FileExistsError(args.out)
    release=HERE/'release';checks={};details={}
    original=HERE/'history/2026-10-08-release-v0.2.0'
    # Compare using each build's portable labels, preserving every frozen payload field.
    oldmap=read(HERE/'build-records/r10/portable-source-map.json');newmap=read(args.records/'portable-source-map.json')
    def restore(value,mapping):
        if isinstance(value,dict):return {k:restore(v,mapping) for k,v in value.items()}
        if isinstance(value,list):return [restore(v,mapping) for v in value]
        if isinstance(value,str):
            import re
            return re.sub(r'source-\d{4}',lambda x:mapping.get(x.group(),x.group()),value)
        return value
    for version in ['v1','v2']:
        old=pq.read_table(original/'data'/f'benchmark_rows_{version}.parquet').to_pylist()
        new=pq.read_table(release/'data'/f'benchmark_rows_{version}.parquet').to_pylist()
        mismatch=[]
        for a,b in zip(old,new):
            for field in ['reference_json','prediction_json','locator_json']:
                mismatch+=equal(restore(json.loads(a[field]),oldmap),restore(json.loads(b[field]),newmap),f'{version}/{a["sample_index"]}/{field}')
        checks[version+'_frozen_payloads_preserved']=len(old)==len(new) and not mismatch
        details[version+'_payload_mismatches']=mismatch
    impact=read(P/'impact-v2.1.json')
    for version in ['v1','v2','v3']:
        rows=pq.read_table(release/'data'/f'benchmark_rows_{version}.parquet').to_pylist()
        flags=[(r['sample_index'],x) for r in rows for x in json.loads(r['reference_chart_correction_flags_json'])]
        changed={(s,x['unit_index']) for s,x in flags if x['candidate_fields_would_change']}
        possible={(s,x['unit_index']) for s,x in flags if x['candidate_identity_review']}
        group=impact['M_references'][version]
        expected={(x['sample_index'],x['unit_index']) for x in group['unit_changes']}
        potential={(x['sample_index'],x['unit_index']) for x in group['potential_mappings']}
        checks[version+'_P_unit_identity_flags']=changed==expected and possible==potential
        details[version+'_chart_flags']=dict(direct_changed_units=len(changed),candidate_identity_review_units=len(possible),
            corrected_cell_flags=sum(x['corrected_cell'] for s,x in flags),locator_conflicts=sum(x['locator_conflict'] for s,x in flags))
    # Recompute the documented sensitivity from original M inputs, without staged refs.
    import sys
    sys.path.insert(0,str(release/'code'));import score_core as E
    refs=copy.deepcopy(read(V3/'blind/adjudicated-reference.json')['rows'])
    for r in refs:
        if r['sample_index']==35:r['units'][2]['strict_candidate_codes']=[23]
        if r['sample_index']==70:r['units'][4]['strict_candidate_codes']=[23]
    refs={r['sample_index']:r for r in refs};preds=read(V3/'predictions.json')['rows']
    summary=E.aggregate([E.score_row(p,refs[p['sample_index']]) for p in preds])
    sensitivity=read(release/'benchmark/v3-reading-choice-sensitivity.json')
    checks['reading_choice_sensitivity']=not equal(summary,sensitivity['summary']) and summary['strict_top5']['whole_rows_all_sample']['success']==64
    paths={p.relative_to(release).as_posix():sha(p) for p in release.rglob('*') if p.is_file()}
    other={p.relative_to(args.rebuild).as_posix():sha(p) for p in args.rebuild.rglob('*') if p.is_file()}
    mismatch=[p for p in paths.keys()|other.keys() if paths.get(p)!=other.get(p)]
    checks['byte_identical_fresh_rebuild']=not mismatch
    oldfiles=read(original/'provenance/file-manifest.json')
    checks['v0_2_0_archive_preserved']=all(sha(original/r['path'])==r['sha256'] for r in oldfiles)
    script_records=read(RAW/'rr35/rerun-summary.json')['scripts']
    checks['reviewer_files_unchanged']=all(sha(HERE/'review'/name)==r['source_sha256'] for name,r in script_records.items())
    result=dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,details=details,
        rebuild=dict(files=len(paths),matching=len(paths)-len(mismatch),mismatches=mismatch),
        preservation=dict(previous_release_files=len(oldfiles)+1,old_manifest_sha256=sha(original/'provenance/file-manifest.json')),
        sensitivity_strict_top5=summary['strict_top5']['whole_rows_all_sample'])
    dump(args.out,result);print(json.dumps(result,indent=2))
    if not all(checks.values()):raise SystemExit(1)

if __name__=='__main__':main()
