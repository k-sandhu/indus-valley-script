"""Recount the documented sequence-screen denominator without exporting sequences."""
from pathlib import Path
import argparse
import hashlib
import json
from collections import Counter
import pyarrow.parquet as pq
from build_release import HERE,ROOT,dump

def main():
    p=argparse.ArgumentParser();p.add_argument('--release',type=Path,default=HERE/'release');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if not a.out.resolve().is_relative_to(HERE) or a.out.exists():raise ValueError('Choose a fresh owned output file')
    forward=set();directions=set();pins=[]
    for filename in ['lipi_observed_faces.jsonl','mayig_faces.jsonl']:
        data=(ROOT/'data/normalized'/filename).read_bytes();pins.append(dict(file=filename,sha256=hashlib.sha256(data).hexdigest()))
        for line in data.decode().splitlines():
            row=json.loads(line)
            for field in ['signs_visual_ltr','signs_reading_rtl']:
                seq=row.get(field,[])
                if len(seq)<2:continue
                value=tuple(str(x).lstrip('0') or '0' for x in seq);directions.add(value)
                if field=='signs_visual_ltr':forward.add(value)
    counts=Counter()
    for version in ['v1','v2']:
        for row in pq.read_table(a.release/'data'/f'benchmark_rows_{version}.parquet').to_pylist():
            units=json.loads(row['reference_json']).get('units',[])
            if all(len(u.get('strict_candidate_codes',[]))==1 for u in units):
                if len(units)>=2:counts['at_least_two']+=1
                if len(units)>=3:counts['at_least_three']+=1
    dump(a.out,dict(status='Verified computation',source_files=pins,minimum_source_units=2,forward_distinct_sequences=len(forward),both_recorded_directions_distinct_sequences=len(directions),complete_singleton_benchmark_reference_rows=dict(counts),Mayig_namespace='P prefixes retained',basis='Reference units all have exactly one strict candidate; packaging screen input scope'))

if __name__=='__main__':main()
