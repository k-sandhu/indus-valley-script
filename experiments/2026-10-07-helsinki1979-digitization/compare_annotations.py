"""Compare the six preregistered repeat readings without adjudicating originals."""
import argparse
import hashlib
import json
from pathlib import Path
from evaluate import align

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    d=json.loads(Path(path).read_text(encoding='utf-8'))
    return d['rows'] if isinstance(d,dict) else d


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=HERE/'evaluation/annotation-comparison-v1.json');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(HERE) or out.exists():raise ValueError('Comparison output must be new and owned')
    primary={}; hashes={}
    for name in ('a','b','c'):
        p=HERE/f'blind/reference-{name}.json';hashes[p.name]=sha(p)
        for r in read(p):assert r['sample_index'] not in primary;primary[r['sample_index']]=r
    repeated=[]
    for name in ('a','b','c'):
        p=HERE/f'blind/reference-{name}-repeat.json';hashes[p.name]=sha(p)
        repeated.extend(read(p))
    assert len(repeated)==6 and {r['sample_index'] for r in repeated}=={5,13,30,35,42,51}
    rows=[]
    for r in sorted(repeated,key=lambda x:x['sample_index']):
        p=primary[r['sample_index']]
        a=[set(int(c) for c in u['strict_candidate_codes']) for u in p['units']]
        b=[set(int(c) for c in u['strict_candidate_codes']) for u in r['units']]
        comp=align(a,b)
        rows.append(dict(sample_index=r['sample_index'],primary_count=p['drawn_unit_count'],repeat_count=r['drawn_unit_count'],
            count_agrees=p['drawn_unit_count']==r['drawn_unit_count'],number_agrees=p['printed_inscription_id']==r['printed_inscription_id'],
            classification_agrees=p['classification_literal']==r['classification_literal'],
            candidate_set_edit_distance=comp['edits'],whole_row_candidate_compatible=comp['edits']==0 and all(a) and all(b),
            candidate_sets_identical=a==b,primary_crop_correct=p.get('crop_correct'),repeat_crop_correct=r.get('crop_correct')))
    result=dict(status='Verified computation',scope='Six prespecified source-only repeat readings; primary reference remains unchanged',
        rows_compared=len(rows),matching_counts=sum(r['count_agrees'] for r in rows),matching_numbers=sum(r['number_agrees'] for r in rows),
        matching_classifications=sum(r['classification_agrees'] for r in rows),
        whole_candidate_compatible_rows=sum(r['whole_row_candidate_compatible'] for r in rows),
        identical_candidate_set_rows=sum(r['candidate_sets_identical'] for r in rows),
        reference_hashes=hashes,code_sha256=sha(__file__),rows=rows)
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
