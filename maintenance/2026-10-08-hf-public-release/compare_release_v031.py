"""Compare fresh bytes, preserved frozen payloads and protected review witnesses."""
import argparse
from pathlib import Path
import sys
import pyarrow.parquet as pq
from build_release import HERE,ROOT,read,dump,sha
from release_policy import bytes_safe

def main():
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');p.add_argument('--rebuild',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--review-out',type=Path,required=True);a=p.parse_args()
    if a.out.exists() or a.review_out.exists():raise FileExistsError('Fresh outputs required')
    script=HERE/'review-0.3.0/rebuild_compare_v3.py';source=script.read_text(encoding='utf8')
    code=source.replace('Path(__file__).with_name("rebuild-comparison.json")','REVIEW_OUT').replace('ROOT / "experiments/2026-10-08-hf-public-release/release"','RELEASE')
    previous=sys.argv;sys.argv=[str(script),'--rebuild',str(a.rebuild.resolve())]
    try:exec(compile(code,str(script),'exec'),dict(__file__=str(script),__name__='__main__',REVIEW_OUT=a.review_out,RELEASE=a.release.resolve()))
    finally:sys.argv=previous
    rebuild=read(a.review_out);plan=read(HERE/'preservation-plan-2026-10-08-v031.json')
    archive=HERE/'history/2026-10-08-release-v0.3.0'
    protected=[name for name,expected in plan['reviewer_hashes'].items() if sha(HERE/name)!=expected]
    archive_changed=[name for name,expected in plan['release_0_3_0'].items() if sha(archive/name)!=expected]
    comparisons={}
    for old in sorted((archive/'data').glob('*.parquet')):
        new=a.release/'data'/old.name;before=pq.read_table(old).to_pylist();after=pq.read_table(new).to_pylist()
        omit={'chart_correction_flags_json'} if old.stem in ['benchmark_readings','benchmark_readings_v3'] else set()
        normalize=lambda rows:bytes_safe([{k:v for k,v in r.items() if k not in omit} for r in rows])
        comparisons[old.stem]=dict(rows=len(after),schemas_unchanged=pq.read_schema(old)==pq.read_schema(new),all_original_values_preserved=normalize(before)==normalize(after),allowed_changed_fields=sorted(omit))
    checks=dict(rebuild_equal=not rebuild['unequal'] and not rebuild['only_in_release'] and not rebuild['only_in_rebuild'],reviewer_files_unchanged=not protected,reviewed_archive_unchanged=not archive_changed,all_table_values_preserved_except_reading_flags=all(r['all_original_values_preserved'] for r in comparisons.values()),schemas_preserved=all(r['schemas_unchanged'] for r in comparisons.values()))
    dump(a.out,dict(status='Verified computation' if all(checks.values()) else 'Failed',checks=checks,rebuild=rebuild,table_preservation=comparisons,protected_reviewer_files=len(plan['reviewer_hashes']),changed_reviewer_files=protected,changed_archive_files=archive_changed,review_rebuild_script_sha256=sha(script)))
    if not all(checks.values()):raise SystemExit(1)

if __name__=='__main__':main()
