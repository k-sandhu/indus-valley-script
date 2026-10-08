"""Freeze v3, prepare source-only blind materials, and emit quarantined line proposals."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import random
import shutil
import time
import platform
import hashlib
import crop_v3 as C
import pipeline as P

DEFAULT=P.HERE/'repair/2026-10-08-v3'
SECTIONS=[('number_order',22,78,28),('end_sorted',79,130,26),('beginning_sorted',131,180,26)]
SEED=2026100880
COUNT_SEED=2026100891
DEVELOPMENT=[22,25,30,37,62,78,100,129,130,145]

def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def clean(row):return {k:v for k,v in row.items() if k!='ink_components'}
def checked(run):
    manifest=read(run/'freeze-manifest.json')
    assert all(digest(P.HERE/p)==h for p,h in manifest['code_hashes'].items()),'Frozen implementation changed'
    assert digest(P.PDF)==manifest['source_sha256']
    return manifest

def freeze(run):
    if run.exists():raise FileExistsError('Use a new endpoint directory')
    old=read(P.HERE/'blind/selection.json')['rows'];v2=read(P.HERE/'repair/2026-10-07-v2/blind/selection.json')['rows']
    exclude=sorted(set(DEVELOPMENT)|{r['pdf_page'] for r in old+v2})
    names=['crop_v3.py','prepare_crop_v3.py','evaluate_crop_v3.py','pipeline.py','layout_v3.py','evaluate.py','evaluate_repair.py',
           'chart-snapshot.json','development/classifier.pt','development/digits.npz','development/calibration.json',
           'V3-CONVENTIONS.md']
    manifest=dict(status='Frozen evaluation',created_utc=now(),parameters=C.PARAM,
        inherited_column_parameters=C.OLD.PARAM,code_hashes={p:digest(P.HERE/p) for p in names},
        source_sha256=digest(P.PDF),recognizer_refitted=False,calibration_refitted=False,
        development=dict(v2_rows=80,v2_count_pages=21,original_development_pages=DEVELOPMENT,
            result='repair/2026-10-08-development-v3h/development.json',result_sha256=digest(P.HERE/'repair/2026-10-08-development-v3h/development.json')),
        sample=dict(seed=SEED,sections=SECTIONS,n=80,unit='numbered occurrence plus its provisional continuation lines',
            excluded_pages=exclude,exclusion='All pages containing any earlier evaluation target, plus original development pages',
            original_target_count=60,v2_target_count=80),
        source_row_counts=dict(seed=COUNT_SEED,random_pages_per_section=6,stress_pages=[62,129,130],
            previous_count_pages=read(P.HERE/'repair/2026-10-07-v2/blind/selection.json')['count_pages'],
            measures=['numbered occurrences','all physical glyph lines']),
        release_rule=read(P.HERE/'repair/2026-10-07-v2/freeze-manifest.json')['release_rule'],
        fresh_reference_exists=False,all_full_proposals_quarantined=True,
        environment=dict(python=platform.python_version(),numpy=P.np.__version__,torch=P.torch.__version__,
            opencv=P.cv2.__version__,device=P.DEVICE),
        attribution='Kimmo Koskenniemi and Asko Parpola, Corpus of Texts in the Indus Script (1979), University of Helsinki, CC BY 4.0; raster cropping and numerical proposals are modifications')
    run.mkdir(parents=True);P.write(run/'freeze-manifest.json',manifest)
    print(json.dumps(dict(frozen_utc=manifest['created_utc'],freeze_sha256=digest(run/'freeze-manifest.json'))),flush=True)

def frame(run):
    manifest=checked(run);path=run/'frame.json'
    if path.exists():return read(path)
    rows=[];pages=[]
    with P.fitz.open(P.PDF) as doc:
        for p in range(22,181):
            _,_,found,meta=C.process(doc,p,None,False)
            pages.append(dict(pdf_page=p,layout=meta));rows.extend(clean(r) for r in found)
    result=dict(status='Frozen evaluation',freeze_sha256=digest(run/'freeze-manifest.json'),rows=rows,pages=pages,
        eligible_numbered_rows=sum(r['line_kind']=='numbered' and r['pdf_page'] not in manifest['sample']['excluded_pages'] for r in rows))
    P.write(path,result);return result

def packet(run):
    manifest=checked(run)
    if (run/'prediction-freeze.json').exists():raise FileExistsError('Prediction endpoint already exists')
    blind=run/'blind'
    if blind.exists():raise FileExistsError('Do not overwrite a partially constructed blind packet')
    fr=frame(run);rng=random.Random(SEED);selected=[];denominators={};eligible_pages={}
    for section,lo,hi,n in SECTIONS:
        pool=[r for r in fr['rows'] if r['section']==section and r['line_kind']=='numbered' and r['pdf_page'] not in manifest['sample']['excluded_pages']]
        denominators[section]=len(pool);eligible_pages[section]=sorted(set(r['pdf_page'] for r in pool));selected.extend(rng.sample(pool,n))
    selected.sort(key=lambda r:(r['pdf_page'],r['pdf_column'],r['row_index']))
    count_rng=random.Random(COUNT_SEED);random_pages=[]
    for section,lo,hi,n in SECTIONS:
        pool=[p for p in range(lo,hi+1) if p not in manifest['source_row_counts']['previous_count_pages'] and p not in [62,129,130]]
        random_pages.extend(count_rng.sample(pool,6))
    count_pages=sorted(set(random_pages+[62,129,130]));blind.mkdir()
    shutil.copyfile(P.HERE/'V3-CONVENTIONS.md',blind/'CONVENTIONS.md')
    shutil.copytree(P.HERE/'repair/2026-10-07-v2/blind/position-chart',blind/'position-chart')
    rec=P.Recognizer(P.templates(),P.HERE/'development/classifier.pt');predictions=[];locators=[]
    with P.fitz.open(P.PDF) as doc:
        for page in sorted(set(r['pdf_page'] for r in selected)):
            gray4,gray2,found,meta=C.process(doc,page,None,True);by_key={r['occurrence_key']:r for r in found}
            for index,target in enumerate(selected):
                if target['pdf_page']!=page:continue
                primary=by_key[target['occurrence_key']]
                lines=[primary]+[r for r in found if r['continuation_of']==primary['occurrence_key']]
                prediction=clean(primary);prediction['sample_index']=index;prediction['units']=[];prediction['printed_lines']=[]
                boxes=[r['glyph_pdf_box'] for r in lines];field=primary['margin_pdf_box']
                context=[max(0,min([field[0]]+[b[0] for b in boxes])-6),max(55,min(b[1] for b in boxes)-18),
                    min(doc[page-1].rect.width,max([field[2]]+[b[2] for b in boxes])+9),min(795,max(b[3] for b in boxes)+18)]
                source=f'row_{index:03d}_pdf{page}.png'
                doc[page-1].get_pixmap(matrix=P.fitz.Matrix(5,5),clip=P.fitz.Rect(context),colorspace=P.fitz.csGRAY).save(blind/source)
                exacts=[]
                for j,line in enumerate(lines):
                    units,cost=C.segment_units(gray4,gray2,line,rec);prediction['units'].extend(units)
                    prediction['printed_lines'].append(dict(occurrence_key=line['occurrence_key'],line_kind=line['line_kind'],
                        glyph_pdf_box=line['glyph_pdf_box'],units=units,segmentation_cost=cost))
                    name=f'exact_{index:03d}.png' if j==0 else f'exact_{index:03d}_continuation{j}.png'
                    doc[page-1].get_pixmap(matrix=P.fitz.Matrix(5,5),clip=P.fitz.Rect(line['glyph_pdf_box']),colorspace=P.fitz.csGRAY).save(blind/name)
                    exacts.append(dict(file=name,sha256=digest(blind/name),glyph_pdf_box=line['glyph_pdf_box'],line_kind=line['line_kind']))
                predictions.append(prediction)
                locators.append(dict(sample_index=index,pdf_page=page,section=primary['section'],pdf_column=primary['pdf_column'],
                    target_glyph_pdf_box=primary['glyph_pdf_box'],target_field_pdf_box=field,context_pdf_box=context,
                    source_crop=source,source_crop_sha256=digest(blind/source),exact_crop=exacts[0]['file'],
                    exact_crop_sha256=exacts[0]['sha256'],printed_line_crops=exacts,source_orientation=0))
            print(json.dumps(dict(packet_page=page,selected_so_far=len(predictions))),flush=True)
        countfolder=blind/'page-count-source';countfolder.mkdir();counts=[]
        for page in count_pages:
            rows=[r for r in fr['rows'] if r['pdf_page']==page]
            counts.append(dict(pdf_page=page,rows=rows,layout=next(p['layout'] for p in fr['pages'] if p['pdf_page']==page)))
            doc[page-1].get_pixmap(matrix=P.fitz.Matrix(2,2),colorspace=P.fitz.csGRAY).save(countfolder/f'pdf{page}.png')
    P.write(run/'predictions.json',dict(status='Frozen evaluation',freeze_sha256=digest(run/'freeze-manifest.json'),rows=predictions))
    P.write(run/'count-page-detections.json',dict(status='Frozen evaluation',pages=counts))
    P.write(blind/'selection.json',dict(status='Frozen evaluation',seed=SEED,rows=locators,denominators=denominators,
        eligible_pages=eligible_pages,excluded_pages=manifest['sample']['excluded_pages'],count_pages=count_pages,
        random_count_pages=sorted(random_pages),stress_pages=[62,129,130],count_seed=COUNT_SEED))
    packet_hashes={str(p.relative_to(blind)).replace('\\','/'):digest(p) for p in blind.rglob('*') if p.is_file()}
    P.write(run/'prediction-freeze.json',dict(status='Frozen evaluation',created_utc=now(),rows=len(predictions),
        prediction_sha256=digest(run/'predictions.json'),selection_sha256=digest(blind/'selection.json'),
        freeze_sha256=digest(run/'freeze-manifest.json'),count_detections_sha256=digest(run/'count-page-detections.json'),
        reference_exists=False,packet_hashes=packet_hashes))
    print(json.dumps(dict(prediction_frozen=True,rows=len(predictions),denominators=denominators,count_pages=count_pages)),flush=True)

def full(run,raw,resume):
    checked(run);raw=raw.resolve()
    if not raw.is_relative_to(P.RAW):raise ValueError('Full output must remain under local raw')
    if raw.exists() and not resume:raise FileExistsError('Use new raw output, or resume hash-checked pages')
    raw.mkdir(parents=True,exist_ok=True);pagefolder=raw/'pages';pagefolder.mkdir(exist_ok=True)
    freeze_hash=digest(run/'freeze-manifest.json');source_hash=digest(P.PDF);rec=P.Recognizer(P.templates(),P.HERE/'development/classifier.pt');metadata=[];started=time.monotonic()
    with P.fitz.open(P.PDF) as doc:
        for page in range(22,181):
            path=pagefolder/f'pdf{page}.jsonl';metapath=pagefolder/f'pdf{page}.meta.json'
            if resume and path.exists() and metapath.exists():
                meta=read(metapath);assert meta['freeze_sha256']==freeze_hash and digest(path)==meta['sha256'];metadata.append(meta);continue
            if path.exists() or metapath.exists():raise FileExistsError(f'Partial page {page}; preserve and use a new raw output')
            gray4,gray2,rows,layout=C.process(doc,page,rec,True)
            with path.open('w',encoding='utf-8',newline='\n') as out:
                for row in rows:
                    row=clean(row);row.update(pipeline_freeze_sha256=freeze_hash,source_sha256=source_hash,
                        inventory_version='helsinki1979-crop-v3-2026-10-08',review_status='unreviewed',released=False,
                        source_licence='CC BY 4.0',candidate_status='proposal')
                    row['boundary_blanks']=[dict(left_unit=i,right_unit=i+1,gap_pdf_points=b['unit_pdf_box'][0]-a['unit_pdf_box'][2],interpretation='unresolved')
                        for i,(a,b) in enumerate(zip(row['units'],row['units'][1:])) if b['unit_pdf_box'][0]-a['unit_pdf_box'][2]>=9]
                    for i,u in enumerate(row['units']):
                        kinds=sorted({P.AUXILIARY_CODES[c] for alt in u['alternatives'] for c in alt['codes'] if c in P.AUXILIARY_CODES})
                        if kinds:row['auxiliaries'].append(dict(unit_index=i,kind_candidates=kinds,ancient_unit_extent=None))
                    out.write(json.dumps(row,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n')
            meta=dict(pdf_page=page,layout=layout,rows=len(rows),units=sum(len(r['units']) for r in rows),
                flags=dict(Counter(f for r in rows for f in r['flags'])),freeze_sha256=freeze_hash,sha256=digest(path),bytes=path.stat().st_size)
            P.write(metapath,meta);metadata.append(meta)
            print(json.dumps(dict(full_page=page,rows=len(rows),units=meta['units'],seconds=round(time.monotonic()-started,1))),flush=True)
    combined=raw/'proposals.jsonl'
    if combined.exists():raise FileExistsError('Combined full output already exists')
    with combined.open('wb') as out:
        for page in range(22,181):
            with (pagefolder/f'pdf{page}.jsonl').open('rb') as source:shutil.copyfileobj(source,out)
    result=dict(status='Exploratory',freeze_sha256=freeze_hash,all_quarantined=True,released_rows=0,
        rows=sum(p['rows'] for p in metadata),units=sum(p['units'] for p in metadata),pages=len(metadata),
        numbered_occurrences=sum(p['layout']['numbered_lines'] for p in metadata),
        continuation_lines=sum(p['layout']['continuation_lines'] for p in metadata),
        sections={s:sum(p['rows'] for p in metadata if lo<=p['pdf_page']<=hi) for s,lo,hi,n in SECTIONS},
        path=str(combined.relative_to(P.ROOT)).replace('\\','/'),sha256=digest(combined),bytes=combined.stat().st_size,
        raw_page_directory=str(pagefolder.relative_to(P.ROOT)).replace('\\','/'),seconds=time.monotonic()-started,page_results=metadata,
        coverage_note='Detection census, not independently verified edition-wide completeness. Fresh counts pending.')
    P.write(run/'full-summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='page_results'}),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['freeze','packet','full']);ap.add_argument('--run',type=Path,default=DEFAULT)
    ap.add_argument('--raw-output',type=Path,default=P.RAW/'2026-10-08-v3/full-v1');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    run=args.run.resolve()
    if not run.is_relative_to(P.HERE):raise ValueError('Endpoint must be owned')
    if args.command=='freeze':freeze(run)
    elif args.command=='packet':packet(run)
    else:full(run,args.raw_output,args.resume)
if __name__=='__main__':main()
