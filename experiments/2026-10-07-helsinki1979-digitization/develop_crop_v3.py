"""Development on the already annotated v2 rows; never a fresh evaluation."""
import argparse
import copy
import json
from pathlib import Path
import time
from PIL import Image,ImageDraw
import crop_v3 as C
import pipeline as P
import evaluate as E
import evaluate_repair as ER


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--layout-only',action='store_true');args=ap.parse_args()
    out=args.out.resolve()
    if not out.is_relative_to(P.HERE) or out.exists():raise ValueError('Use a new owned development output')
    out.mkdir(parents=True);raw=P.RAW/'2026-10-08-v3'/out.name;raw.mkdir(parents=True,exist_ok=True)
    before=json.loads((P.HERE/'repair/2026-10-07-v2/predictions.json').read_text())['rows']
    refs={r['sample_index']:r for r in json.loads((P.HERE/'repair/2026-10-07-v2/blind/adjudicated-reference.json').read_text())['rows']}
    rec=None if args.layout_only else P.Recognizer(P.templates(),P.HERE/'development/classifier.pt')
    counts=json.loads((P.HERE/'repair/2026-10-07-v2/blind/adjudicated-counts.json').read_text())['pages']
    count_results=[];rows=[];page_results=[];start=time.monotonic();code_hash=P.sha(P.HERE/'crop_v3.py')
    with P.fitz.open(P.PDF) as doc:
        for page in sorted({r['pdf_page'] for r in before}|{r['pdf_page'] for r in counts}|{62,66,112,129,130}):
            gray4,gray2,found,meta=C.process(doc,page,None,read_fields=not args.layout_only)
            page_results.append(dict(pdf_page=page,layout=meta));print(json.dumps(dict(page=page,layout=meta['numbered_lines'],continuations=meta['continuation_lines'],seconds=round(time.monotonic()-start,1))),flush=True)
            if any(c['pdf_page']==page for c in counts):
                count_results.append(ER.recall_page([r for r in found if r['line_kind']=='numbered'],next(c for c in counts if c['pdf_page']==page)))
            for old in before:
                if old['pdf_page']!=page:continue
                field=old['margin_xyxy_2x'];anchor=(field[1]+field[3])/4-2.25
                pool=[r for r in found if r['pdf_column']==old['pdf_column'] and r['line_kind']=='numbered']
                r=copy.deepcopy(min(pool,key=lambda r:abs(r['layout_anchor_pdf']-anchor))) if pool else None
                if r is None or abs(r['layout_anchor_pdf']-anchor)>13:
                    rows.append(dict(sample_index=old['sample_index'],missing=True,page=page,anchor=anchor));continue
                r['sample_index']=old['sample_index'];r['development_reference_reused']=True
                r['v2_to_v3_anchor_distance_pt']=abs(r['layout_anchor_pdf']-anchor)
                r['ink_components']=[];rows.append(r)
                if not args.layout_only:
                    r['units'],r['segmentation_cost']=C.segment_units(gray4,gray2,r,rec)
                    continuations=[copy.deepcopy(x) for x in found if x['continuation_of']==r['occurrence_key']]
                    for child in continuations:
                        child['units'],child['segmentation_cost']=C.segment_units(gray4,gray2,child,rec)
                        r['units'].extend(child['units'])
                    r['continuation_boxes_pdf']=[x['glyph_pdf_box'] for x in continuations]
                    box=r['glyph_pdf_box'];field=r['margin_pdf_box'];context=[max(0,min(box[0],field[0])-5),max(58,box[1]-19),min(590,max(box[2],field[2])+5),min(798,max([box[3]]+[x['glyph_pdf_box'][3] for x in continuations])+19)]
                    pix=doc[page-1].get_pixmap(matrix=P.fitz.Matrix(4,4),clip=P.fitz.Rect(context),colorspace=P.fitz.csRGB)
                    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);draw=ImageDraw.Draw(im)
                    draw.rectangle([(box[0]-context[0])*4,(box[1]-context[1])*4,(box[2]-context[0])*4,(box[3]-context[1])*4],outline='red',width=2)
                    for child in continuations:
                        cb=child['glyph_pdf_box'];draw.rectangle([(cb[0]-context[0])*4,(cb[1]-context[1])*4,(cb[2]-context[0])*4,(cb[3]-context[1])*4],outline='red',width=2)
                    for u in r['units']:
                        ub=u['unit_pdf_box'];draw.rectangle([(ub[0]-context[0])*4,(ub[1]-context[1])*4,(ub[2]-context[0])*4,(ub[3]-context[1])*4],outline='#3270bf',width=1)
                    im.save(raw/f'row_{old["sample_index"]:03d}.png')
    rows.sort(key=lambda r:r['sample_index'])
    payload=dict(status='Exploratory',purpose='80 v2 rows used as development',parameters=C.PARAM,
        code_sha256=code_hash,code_unchanged_during_run=code_hash==P.sha(P.HERE/'crop_v3.py'),seconds=time.monotonic()-start,pages=page_results,rows=rows,
        development_count_pages=count_results,development_numbered_row_recall=ER.page_summary(count_results),
        source_reference_sha256=P.sha(P.HERE/'repair/2026-10-07-v2/blind/adjudicated-reference.json'),raw_inspection_directory=str(raw.relative_to(P.ROOT)))
    if not args.layout_only:
        scored=[]
        for r in rows:
            if r.get('missing'):
                r=dict(sample_index=r['sample_index'],units=[],inscription_number=None,classification_code=None)
            ref=copy.deepcopy(refs[r['sample_index']]);ref['crop_correct']=None
            scored.append(E.score_row(r,ref))
        payload['summary']=E.aggregate(scored);payload['scored_rows']=scored
        for start_idx in range(0,80,10):
            sheet=Image.new('RGB',(1500,1050),'white');draw=ImageDraw.Draw(sheet)
            for j in range(10):
                i=start_idx+j;path=raw/f'row_{i:03d}.png'
                if not path.exists():continue
                im=Image.open(path);im.thumbnail((1450,90));sheet.paste(im,(35,j*105+12));draw.text((2,j*105+12),str(i),fill='black')
            sheet.save(raw/f'board_{start_idx:03d}.png')
    P.write(out/'development.json',payload)
    print(json.dumps(dict(output=str(out),summary=payload.get('summary'),matched=sum(not r.get('missing') for r in rows))),flush=True)


if __name__=='__main__':main()
