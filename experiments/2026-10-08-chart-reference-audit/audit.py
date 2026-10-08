"""Reproduce the chart pixel witnesses and compare a separately saved visual reading.

Run from the repository root. No PDF text extraction is used.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OWN = Path(__file__).resolve().parent
RAW = ROOT / 'data/raw/2026-10-08-chart-reference-audit'
TMP = RAW / 'tmp'
TMP.mkdir(parents=True, exist_ok=True)
for variable in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[variable] = str(TMP)
sys.dont_write_bytecode = True


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key(r):
    return f"p{r['pdf_page']}_c{r['column']}_r{r['row']}"


def render():
    import fitz
    from PIL import Image, ImageDraw, ImageFont
    pdf_path = ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'
    atlas_path = ROOT / 'output/chart_atlas/reference.json'
    ref_path = ROOT / 'research/chart_reference/manual_numeric_reference.json'
    atlas = read(atlas_path)
    doc = fitz.open(pdf_path)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 18)
    records = []
    for page in (20, 21):
        doc[page-1].get_pixmap(matrix=fitz.Matrix(6, 6), alpha=False).save(RAW / f'page-{page}-6x.png')
    for page in (20, 21):
        for col in range(10):
            rows = [r for r in atlas['rows'] if r['pdf_page'] == page and r['column'] == col]
            crops = []
            for r in rows:
                box = r['source_crop_pdf_points']
                pix = doc[page-1].get_pixmap(matrix=fitz.Matrix(8, 8), clip=fitz.Rect(box), alpha=False)
                im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                name = key(r)
                path = RAW / 'cells-8x' / f'{name}.png'
                path.parent.mkdir(parents=True, exist_ok=True)
                im.save(path)
                crops.append((r, im))
                records.append({'cell': name, 'pdf_page':page, 'column':col, 'row':r['row'],
                                'clip_pdf_points':box, 'pixels_per_point':8, 'path':str(path.relative_to(ROOT)),
                                'sha256':sha(path)})
            # Ten/eleven-cell columns with coordinates outside the source pixels.
            # A sheet contains at most 18 cells in two strips; native source pixels stay 8x.
            for start in range(0, len(crops), 18):
                group = crops[start:start+18]
                tile_w = max(im.width for r, im in group) + 110
                tile_h = max(im.height for r, im in group) + 6
                sheet = Image.new('RGB', (tile_w*2, tile_h*9), 'white')
                draw = ImageDraw.Draw(sheet)
                for i, (r, im) in enumerate(group):
                    x, y = (i//9)*tile_w, (i%9)*tile_h
                    draw.text((x+4,y+10), f"r{r['row']}", fill='blue',font=font)
                    sheet.paste(im,(x+65,y))
                out=RAW/'sheets'/f'p{page}_c{col}_{start:02d}.png'
                out.parent.mkdir(parents=True,exist_ok=True)
                sheet.save(out)
    manifest={'source_pdf':str(pdf_path.relative_to(ROOT)), 'source_sha256':sha(pdf_path),
              'atlas_sha256':sha(atlas_path), 'original_reference_sha256':sha(ref_path),
              'page_scale':6, 'cell_scale':8, 'cells':records, 'count':len(records)}
    write(RAW/'render-manifest.json',manifest)
    print(json.dumps({k:v for k,v in manifest.items() if k!='cells'}))


def first_rows():
    data=read(OWN/'visual-readings.json')
    return [dict(cell=f'{column}_r{i}',rank=pair[0],code=pair[1])
            for column,values in data['columns'].items() for i,pair in enumerate(values)]


def review():
    import fitz
    from PIL import Image, ImageDraw, ImageFont
    atlas={key(r):r for r in read(ROOT/'output/chart_atlas/reference.json')['rows']}
    old={key(r):r for r in read(ROOT/'research/chart_reference/manual_numeric_reference.json')['rows']}
    rows=first_rows()
    duplicates=collections.Counter(r['code'] for r in rows)
    notes=read(OWN/'visual-readings.json')['digit_notes']
    selected=[r['cell'] for r in rows if r['cell'] in notes or old[r['cell']]['alternatives']
              or [r['rank'],r['code']] != [old[r['cell']]['rank'],old[r['cell']]['code']]
              or duplicates[r['code']]>1]
    doc=fitz.open(ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    for start in range(0,len(selected),8):
        crops=[]
        for cell in selected[start:start+8]:
            r=atlas[cell]
            pix=doc[r['pdf_page']-1].get_pixmap(matrix=fitz.Matrix(16,16),clip=fitz.Rect(r['source_crop_pdf_points']),alpha=False)
            im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            out=RAW/'review-16x'/f'{cell}.png'
            out.parent.mkdir(parents=True,exist_ok=True)
            im.save(out)
            # Exclude top/bottom neighbouring-cell context for more compact sheets.
            crops.append((cell,im.crop((0,int(im.height*.22),int(im.width*.91),int(im.height*.89)))))
        tw=max(im.width for cell,im in crops)
        th=max(im.height for cell,im in crops)+34
        sheet=Image.new('RGB',(tw*2,th*4),'white')
        draw=ImageDraw.Draw(sheet)
        for i,(cell,im) in enumerate(crops):
            x,y=(i//4)*tw,(i%4)*th
            draw.text((x+4,y+3),cell,fill='blue',font=font)
            sheet.paste(im,(x,y+34))
        sheet.save(RAW/'review-16x'/f'sheet-{start:02d}.png')
    write(RAW/'review-selection.json',{'selection_rule':'First-pass disagreements, old ambiguities, difficult-digit notes, and all repeated first-pass codes','cells':selected,'count':len(selected),'visual_readings_sha256':sha(OWN/'visual-readings.json')})
    print(json.dumps({'selected':len(selected)}))


def compare():
    import copy
    old=read(ROOT/'research/chart_reference/manual_numeric_reference.json')
    atlas={key(r):r for r in read(ROOT/'output/chart_atlas/reference.json')['rows']}
    fresh={r['cell']:r for r in first_rows()}
    decisions=read(OWN/'reinspection-decisions.json')
    selected=read(RAW/'review-selection.json')['cells']
    selected=list(dict.fromkeys(selected+list(decisions['overrides'])))
    changes=[];observations=[];final=[];second=[]
    for original in old['rows']:
        cell=key(original)
        r=copy.deepcopy(original)
        observed=dict(fresh[cell])
        observed.update({k:v for k,v in decisions['overrides'].get(cell,{}).items() if k in ['rank','code']})
        confidence='medium' if cell in decisions['medium_confidence_cells'] else 'high'
        evidence=decisions['overrides'].get(cell,{}).get('evidence',decisions['special_notes'].get(cell,'Both printed numeric labels read directly from the 8x source-cell image.'))
        crop=atlas[cell]['source_crop_pdf_points']
        observation=dict(observed,pdf_page=r['pdf_page'],column=r['column'],row=r['row'],
                         numeric_confidence=confidence,alternatives=decisions['alternatives'].get(cell,[]),
                         rank_alternatives=[],visible_evidence=evidence,clip_pdf_points=crop,
                         source_image=f'data/raw/2026-10-08-chart-reference-audit/cells-8x/{cell}.png',
                         first_pass={'rank':fresh[cell]['rank'],'code':fresh[cell]['code']},
                         reinspected=cell in selected)
        if cell in selected:
            observation['review_image']=f'data/raw/2026-10-08-chart-reference-audit/review-16x/{cell}.png'
            if not (ROOT/observation['review_image']).exists():
                observation['review_image']=f'data/raw/2026-10-08-chart-reference-audit/digits-24x/{cell}.png'
            second.append({k:observation[k] for k in ['cell','rank','code','numeric_confidence','visible_evidence','review_image']})
        observations.append(observation)
        fields={'rank':observed['rank'],'code':observed['code'],'alternatives':observation['alternatives'],
                'rank_alternatives':[],'numeric_confidence':confidence}
        delta={f:{'old':original[f],'new':v} for f,v in fields.items() if original[f]!=v}
        r.update(fields)
        r['source']='2026-10-08 printed-pixel audit; single visual reader; independent review pending.'
        if delta:
            log=dict(date='2026-10-08',status='Exploratory',fields=delta,
                     evidence_file='cell-observations.json',evidence_cell=cell,visible_evidence=evidence,
                     source_image=observation['source_image'],review_image=observation.get('review_image'))
            r['change_log']=[log]
            changes.append(dict(cell=cell,**log))
        final.append(r)
    codes=collections.defaultdict(list)
    ranks=[]
    for r in final:codes[r['code']].append(key(r));ranks.append(r['rank'])
    duplicates={str(c):cells for c,cells in codes.items() if len(cells)>1}
    decreases=[{'previous_cell':key(final[i-1]),'cell':key(final[i]),'previous_rank':ranks[i-1],'rank':ranks[i]} for i in range(1,len(ranks)) if ranks[i]<ranks[i-1]]
    result=copy.deepcopy(old)
    result.update(status='Exploratory',rows=final,lower_code_ambiguous_cells=sum(bool(r['alternatives']) for r in final),
                  upper_rank_ambiguous_cells=0,numeric_ambiguous_cells=sum(bool(r['alternatives']) for r in final),
                  adjudication_limit='Single AI visual audit after v1 and reported disagreements; reviewer and expert confirmation pending.',
                  limitations=['Qualitative digit confidence is uncalibrated.','Rendering magnifies the existing scan; it does not recover missing ink.',
                               'Numeric label correctness does not certify glyph segmentation or an inscription reading.'],
                  audit={'date':'2026-10-08','reference_version':2,'original_reference_sha256':sha(ROOT/'research/chart_reference/manual_numeric_reference.json'),
                         'observations':'cell-observations.json','comparison':'comparison.json'})
    write(OWN/'chart-reference-v2.json',result)
    write(OWN/'cell-observations.json',dict(status='Exploratory',reader=read(OWN/'visual-readings.json')['reader'],rows=observations))
    summary={'cells':len(final),'primary_code_changes':sum('code' in c['fields'] for c in changes),
             'class_changes':sum('rank' in c['fields'] for c in changes),'changed_cells':len(changes),
             'old_lower_ambiguities':old['lower_code_ambiguous_cells'],
             'ambiguities_resolved':sum(bool(r['alternatives']) and not final[i]['alternatives'] for i,r in enumerate(old['rows'])),
             'remaining_lower_ambiguities':result['lower_code_ambiguous_cells'],'medium_confidence_cells':decisions['medium_confidence_cells'],
             'reinspected_cells':len(selected),'duplicate_codes':duplicates,'rank_decreases':decreases,
             'distinct_classes':len(set(ranks)),'min_class':min(ranks),'max_class':max(ranks),
             'missing_classes':sorted(set(range(1,402))-set(ranks)),
             'first_pass_primary_code_disagreements':sum(fresh[key(r)]['code']!=r['code'] for r in old['rows']),
             'first_pass_class_disagreements':sum(fresh[key(r)]['rank']!=r['rank'] for r in old['rows'])}
    ambiguity_rows=[{'cell':key(r),'old_code':r['code'],'old_alternatives':r['alternatives'],
                     'new_code':final[i]['code'],'new_alternatives':final[i]['alternatives'],
                     'evidence_cell':key(r)} for i,r in enumerate(old['rows']) if r['alternatives']]
    write(OWN/'comparison.json',dict(status='Exploratory',summary=summary,changes=changes,old_ambiguity_decisions=ambiguity_rows,
                                    reinspection_records=second))
    print(json.dumps(summary))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['render','review','compare'])
    args=parser.parse_args()
    if args.command=='render':render()
    elif args.command=='review':review()
    elif args.command=='compare':compare()
