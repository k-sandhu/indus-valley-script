"""Full transport continuation: frozen inference unchanged, invalid windows unresolved."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import shutil
import time
import crop_v3 as C
import pipeline as P
import prepare_crop_v3 as F

def finite_tree(x):
    if isinstance(x,float) and not math.isfinite(x):return False
    if isinstance(x,dict):return all(finite_tree(v) for v in x.values())
    if isinstance(x,list):return all(finite_tree(v) for v in x)
    return True
def witness_tree(x):
    if isinstance(x,float) and not math.isfinite(x):return str(x)
    if isinstance(x,dict):return {k:witness_tree(v) for k,v in x.items()}
    if isinstance(x,list):return [witness_tree(v) for v in x]
    return x

def run_full(run,raw,reuse,resume):
    freeze=F.checked(run);fh=F.digest(run/'freeze-manifest.json');source_hash=freeze['source_sha256']
    raw=raw.resolve();reuse=reuse.resolve()
    if not raw.is_relative_to(P.RAW) or not reuse.is_relative_to(P.RAW):raise ValueError('Use only local raw output/reuse')
    if raw.exists() and not resume:raise FileExistsError('Use a new output or hash-checked resume')
    raw.mkdir(parents=True,exist_ok=True);pages=raw/'pages';pages.mkdir(exist_ok=True)
    transport=run/'full-transport-manifest.json';own_hash=F.digest(__file__)
    if transport.exists():assert F.read(transport)['code_sha256']==own_hash
    else:P.write(transport,dict(status='Exploratory',created_utc=F.now(),code_sha256=own_hash,pipeline_freeze_sha256=fh,
        rule='Unchanged frozen inference; any unit with a non-finite score/confidence exports alternatives=[] and confidence=null with unresolved flag. Retain string-valued non-finite witnesses locally.',
        failed_original_run=str(reuse.relative_to(P.ROOT)),new_output=str(raw.relative_to(P.ROOT))))
    rec=P.Recognizer(P.templates(),P.HERE/'development/classifier.pt');meta=[];started=time.monotonic()
    witness=raw/'invalid-unit-witnesses.jsonl'
    with P.fitz.open(P.PDF) as doc,witness.open('a',encoding='utf-8') as invalid:
        for page in range(22,181):
            target=pages/f'pdf{page}.jsonl';mp=pages/f'pdf{page}.meta.json'
            old=reuse/'pages'/f'pdf{page}.jsonl';om=reuse/'pages'/f'pdf{page}.meta.json'
            if old.exists() and om.exists() and not target.exists():
                m=F.read(om);assert m['freeze_sha256']==fh and F.digest(old)==m['sha256']
                m=dict(m,path=str(old.relative_to(P.ROOT)).replace('\\','/'),reused_completed_page=True);meta.append(m);continue
            if resume and target.exists() and mp.exists():
                m=F.read(mp);assert m['freeze_sha256']==fh and F.digest(target)==m['sha256'];meta.append(m);continue
            if target.exists() or mp.exists():raise FileExistsError('Partial page; preserve it and choose a new raw output')
            _,_,rows,layout=C.process(doc,page,rec,True);bad=0
            with target.open('w',encoding='utf-8',newline='\n') as out:
                for original in rows:
                    r=F.clean(original);r.update(pipeline_freeze_sha256=fh,source_sha256=source_hash,
                        inventory_version='helsinki1979-crop-v3-2026-10-08',review_status='unreviewed',released=False,
                        source_licence='CC BY 4.0',candidate_status='proposal')
                    for i,u in enumerate(r['units']):
                        if not finite_tree(u):
                            invalid.write(json.dumps(dict(occurrence_key=r['occurrence_key'],unit_index=i,raw_unit=witness_tree(u)),allow_nan=False)+'\n')
                            u.update(alternatives=[],confidence=None,unit_kind='unresolved_empty_or_nonfinite_window',
                                transport_flag='nonfinite_frozen_recognition_window');r['flags'].append('nonfinite_recognition_window');bad+=1
                    if any(u['confidence'] is None for u in r['units']):r.update(minimum_unit_confidence=None,confidence_product=None)
                    r['boundary_blanks']=[dict(left_unit=i,right_unit=i+1,gap_pdf_points=b['unit_pdf_box'][0]-a['unit_pdf_box'][2],interpretation='unresolved')
                        for i,(a,b) in enumerate(zip(r['units'],r['units'][1:])) if b['unit_pdf_box'][0]-a['unit_pdf_box'][2]>=9]
                    for i,u in enumerate(r['units']):
                        kinds=sorted({P.AUXILIARY_CODES[c] for a in u['alternatives'] for c in a['codes'] if c in P.AUXILIARY_CODES})
                        if kinds:r['auxiliaries'].append(dict(unit_index=i,kind_candidates=kinds,ancient_unit_extent=None))
                    assert finite_tree(r)
                    out.write(json.dumps(r,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n')
            m=dict(pdf_page=page,layout=layout,rows=len(rows),units=sum(len(r['units']) for r in rows),
                flags=dict(Counter(f for r in rows for f in r['flags'])),freeze_sha256=fh,sha256=F.digest(target),bytes=target.stat().st_size,
                path=str(target.relative_to(P.ROOT)).replace('\\','/'),nonfinite_units_unresolved=bad,transport_manifest_sha256=F.digest(transport))
            P.write(mp,m);meta.append(m);print(json.dumps(dict(full_page=page,rows=len(rows),units=m['units'],unresolved_nonfinite=bad,seconds=round(time.monotonic()-started,1))),flush=True)
    combined=raw/'proposals.jsonl'
    if combined.exists():raise FileExistsError('Combined output exists')
    with combined.open('wb') as out:
        for m in meta:
            with (P.ROOT/m['path']).open('rb') as src:shutil.copyfileobj(src,out)
    result=dict(status='Exploratory',freeze_sha256=fh,transport_manifest_sha256=F.digest(transport),all_quarantined=True,released_rows=0,
        rows=sum(m['rows'] for m in meta),units=sum(m['units'] for m in meta),pages=len(meta),
        numbered_occurrences=sum(m['layout']['numbered_lines'] for m in meta),continuation_lines=sum(m['layout']['continuation_lines'] for m in meta),
        sections={s:sum(m['rows'] for m in meta if lo<=m['pdf_page']<=hi) for s,lo,hi,n in F.SECTIONS},
        path=str(combined.relative_to(P.ROOT)).replace('\\','/'),sha256=F.digest(combined),bytes=combined.stat().st_size,
        raw_page_directory=str(pages.relative_to(P.ROOT)).replace('\\','/'),seconds=time.monotonic()-started,
        original_completed_inference_seconds=254.0,reused_pages=sum(m.get('reused_completed_page',False) for m in meta),
        nonfinite_units_unresolved=sum(m.get('nonfinite_units_unresolved',0) for m in meta),page_results=meta,
        coverage_note='Detection census, not independently verified edition-wide completeness. Fresh source counts pending; invalid windows explicitly unresolved.')
    if (run/'full-summary.json').exists():raise FileExistsError('Full summary already exists')
    P.write(run/'full-summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='page_results'}),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,default=F.DEFAULT)
    ap.add_argument('--raw-output',type=Path,default=P.RAW/'2026-10-08-v3/full-v2')
    ap.add_argument('--reuse',type=Path,default=P.RAW/'2026-10-08-v3/full-v1');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    if not args.run.resolve().is_relative_to(P.HERE):raise ValueError('Use an owned run')
    run_full(args.run.resolve(),args.raw_output,args.reuse,args.resume)
if __name__=='__main__':main()
