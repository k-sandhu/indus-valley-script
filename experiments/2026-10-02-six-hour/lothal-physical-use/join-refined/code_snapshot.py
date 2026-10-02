"""Summarize an image-reviewed physical-use table and audit corpus joining."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT/'data/six-hour/lothal/table-coding/reviewed-pass.csv'
CORPUS = ROOT/'data/normalized/lipi_observed_faces.jsonl'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',default='experiments/2026-10-02-six-hour/lothal-physical-use/main')
    args = parser.parse_args()
    target = ROOT/args.output
    if target.exists():
        raise RuntimeError('Use a fresh output endpoint.')
    rows = list(csv.DictReader(TABLE.open(encoding='utf-8')))
    objects = {r['object_id']:r for r in rows}
    ids = [int(r['object_id'].split('-')[1]) for r in rows]
    assert ids == list(range(124,217))
    matches = defaultdict(list)
    for line in CORPUS.open(encoding='utf-8'):
        record = json.loads(line)
        assert isinstance(record['source_cisi'],str)
        assert isinstance(record['clean_rtl_singleline'],bool)
        for source in [record['source_cisi']]:
            match = re.match(r'^L-(\d+)(?:[A-Za-z]|\.|$)',source)
            if match and ('L-'+str(int(match[1]))) in objects:
                matches['L-'+str(int(match[1]))].append(record)
                break
    joined = []
    by_type = defaultdict(Counter)
    for object_id,row in objects.items():
        faces = matches[object_id]
        principal = [r for r in faces if r['clean_rtl_singleline'] and r['length']>=3]
        clean = [r for r in faces if r['clean_rtl_singleline']]
        families = sorted({r['object_family_id'] for r in faces})
        joined.append({'object_id':object_id,'record_ids':[r['record_id'] for r in faces],
                       'families':families,'faces':len(faces),'clean_faces':len(clean),
                       'principal_faces':len(principal),'physical_type':row['physical_type'],
                       'context_code':row['context_code'],'source_impressions':int(row['impressions'])})
        by_type[row['physical_type']].update({'published_objects':1,'joined_objects':int(bool(faces)),
              'faces':len(faces),'clean_faces':len(clean),'principal_faces':len(principal),
              'principal_objects':int(bool(principal)),'source_impressions':int(row['impressions'])})
    contexts = Counter(r['context_code'] for r in rows)
    result = {'experiment_id':'ARCH-02','status':'source-table-and-coverage-audit',
              'objects':len(rows),'source_impressions':sum(int(r['impressions']) for r in rows),
              'impression_count_distribution':dict(Counter(r['impressions'] for r in rows)),
              'context_counts':dict(contexts),'physical_type_counts':dict(Counter(r['physical_type'] for r in rows)),
              'joined_objects':sum(bool(r['faces']) for r in joined),'joined_faces':sum(r['faces'] for r in joined),
              'principal_objects':sum(bool(r['principal_faces']) for r in joined),
              'principal_faces':sum(r['principal_faces'] for r in joined),
              'multiple_families_for_one_source_object':[r['object_id'] for r in joined if len(r['families'])>1],
              'missing_objects':[r['object_id'] for r in joined if not r['faces']],
              'by_physical_type':dict(by_type),
              'source_table_sha256':hashlib.sha256(TABLE.read_bytes()).hexdigest(),
              'corpus_sha256':hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
              'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'prose_source_comparisons':{
                  'pdf_9_printed_71_context_counts':{'W':35,'O':11},
                  'pdf_10_printed_72_context_counts':{'W1':18,'W2':11,'?':17},
                  'pdf_21_printed_83_impressions':{'total':130,'single_objects':63,'multiple_impressions':67}},
              'annotation_scope':'Root manual reading of the published table, then a second pixel inspection. Expert review remains an acquisition task.'}
    target.mkdir(parents=True)
    (target/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (target/'code_snapshot.py').write_bytes(Path(__file__).read_bytes())
    # Detailed join combines a source table and a rights-unresolved corpus.
    local = ROOT/('data/six-hour/lothal/table-coding/'+target.name+'-joined-records.json')
    if local.exists():
        raise RuntimeError('Use a fresh local join filename.')
    local.write_text(json.dumps(joined,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
