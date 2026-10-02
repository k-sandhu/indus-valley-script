"""Describe text recurrence inside a source-defined physical-use frame."""
from __future__ import annotations
from collections import Counter,defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'experiments/2026-10-02-six-hour/lothal-physical-use'

def main():
    output=BASE/'graphic-coverage'
    if output.exists():
        raise RuntimeError('Use a fresh endpoint.')
    table=ROOT/'data/six-hour/lothal/table-coding/reviewed-pass.csv'
    objects={r['object_id']:r for r in csv.DictReader(table.open(encoding='utf-8'))}
    source=ROOT/'data/normalized/lipi_observed_faces.jsonl'
    faces=defaultdict(list)
    for line in source.open(encoding='utf-8'):
        record=json.loads(line)
        match=re.match(r'^L-(\d+)(?:[A-Za-z]|\.|$)',record['source_cisi'])
        if match and ('L-'+str(int(match[1]))) in objects:
            faces['L-'+str(int(match[1]))].append(record)
    groups=defaultdict(list)
    cohort=[]
    for object_id,row in objects.items():
        eligible=[r for r in faces[object_id] if r['clean_rtl_singleline'] and r['length']>=3]
        for record in eligible:
            groups[tuple(record['signs_reading_rtl'])].append((object_id,record))
        if 161<=int(object_id.split('-')[1])<=172:
            cohort.append({'object_id':object_id,'faces':len(faces[object_id]),'eligible_faces':len(eligible),
                           'motif_assertions':dict(Counter(r['symbol'] for r in faces[object_id]))})
    # Store our group IDs and aggregate category counts, excluding source strings.
    summaries=[]
    for group_i,(text,members) in enumerate(sorted(groups.items(),key=lambda x:(-len(x[1]),x[0]))):
        ids=sorted({obj for obj,r in members})
        summaries.append({'group_id':f'G{group_i+1:02d}','objects':len(ids),'faces':len(members),
            'object_ids':ids,'length':len(text),'physical_types':dict(Counter(objects[obj]['physical_type'] for obj in ids)),
            'context_codes':dict(Counter(objects[obj]['context_code'] for obj in ids)),
            'motif_assertions':dict(Counter(r['symbol'] for obj,r in members)),
            'text_digest':hashlib.sha256('|'.join(text).encode()).hexdigest()})
    result={'status':'descriptive-source-frame-recurrence','eligible_objects':sum(x['objects'] for x in summaries),
        'distinct_complete_strings':len(summaries),'string_group_size_distribution':dict(Counter(x['objects'] for x in summaries)),
        'groups_spanning_physical_types':sum(len(x['physical_types'])>1 for x in summaries),
        'groups':summaries,'elephant_stamp_source_cohort':cohort,
        'source_table_sha256':hashlib.sha256(table.read_bytes()).hexdigest(),
        'corpus_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'protocol_sha256':hashlib.sha256((BASE/'GRAPHIC-COVERAGE-PROTOCOL.md').read_bytes()).hexdigest(),
        'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.mkdir()
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (output/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k:v for k,v in result.items() if k not in ['groups','elephant_stamp_source_cohort']},indent=2))

if __name__=='__main__':
    main()
