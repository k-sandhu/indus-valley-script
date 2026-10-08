"""Prepare two blind role packets from pinned v3 geometry and v2.1 chart labels."""
from __future__ import annotations
import argparse
import copy
import json
import os
import random
import shutil
import time
from collections import defaultdict
from pathlib import Path
import workflow as W

P = W.ROOT / 'experiments/2026-10-08-chart-reference-audit'
V3 = W.M / 'repair/2026-10-08-v3'
PROPOSALS = W.ROOT / 'data/raw/2026-10-07-helsinki1979-digitization/2026-10-08-v3/full-v2/proposals.jsonl'
CHART = P / 'chart-reference-v2.1.json'
PAIRS = [{8,764},{9,765},{10,766},{543,769},{501,768}]
GUIDANCE = W.HERE / 'pilot-2/2026-10-08-v1'


def select():
    reasons, dependencies = defaultdict(list), {}
    def add(pages, origin):
        for page in pages:
            if type(page) is int and 22 <= page <= 180 and origin not in reasons[page]:
                reasons[page].append(origin)
    def physical_pages(value):
        result = set()
        if isinstance(value, dict):
            if type(value.get('pdf_page')) is int:
                result.add(value['pdf_page'])
            for key, val in value.items():
                if key in ('development_pages','count_pages','random_count_pages','stress_pages','sampled_pages') and isinstance(val,list):
                    result.update(p for p in val if type(p) is int)
                # Eligible/excluded lists are selection frames, not uses of pages.
                if key not in ('eligible_pages','excluded_pages','denominators','eligible_rows','frame'):
                    result.update(physical_pages(val))
        elif isinstance(value,list):
            for val in value:
                result.update(physical_pages(val))
        return result
    add([22,25,30,37,62,78,100,129,130,145], 'original development pages')
    paths = (set(W.M.glob('**/blind/selection*.json')) | set(W.M.glob('**/freeze-manifest.json'))
             | set(W.M.glob('follow-up/**/layout-development-*.json'))
             | set(V3.glob('blind/**/*.json')) | set(V3.glob('*development*.json'))
             | set(W.M.glob('repair/2026-10-08-v3/**/development*.json')))
    for path in sorted(paths):
        dependencies[W.relative(path)] = W.sha(path)
        add(physical_pages(W.read(path)), W.relative(path))
    prior = W.RAW / 'pilot-2026-10-08-v2/coordinator/private-manifest.json'
    dependencies[W.relative(prior)] = W.sha(prior)
    old = W.read(prior)
    add([b['pdf_page'] for b in old['batches']], 'N pilot 1 target pages')
    add([r['pdf_page'] for b in old['batches'] for r in b['controls'].values()], 'N pilot 1 control pages')
    # Pixel/image delivery names also count as exposure, even if no row JSON names them.
    import re
    for file in sorted((V3/'blind').rglob('*.png')):
        match = re.search(r'(?:page[-_]?|pdf)(\d{2,3})',file.name)
        if match:
            add([int(match.group(1))], W.relative(file))
    eligible = [p for p in range(22,181) if p not in reasons]
    if len(eligible) < 2:
        raise ValueError(f'Only {len(eligible)} fresh pages; no exclusion relaxation allowed')
    return dict(seed=2026100805, rule='sample two without replacement from ascending eligible pages; sort for delivery',
                eligible_pages=eligible, selected_pages=sorted(random.Random(2026100805).sample(eligible,2)),
                excluded_pages={str(p): reasons[p] for p in sorted(reasons)}, dependency_hashes=dependencies)


def control_pool():
    impact = W.read(P/'impact-v2.1.json')
    old, new = W.read(W.M/'chart-snapshot.json')['rows'], W.read(CHART)['rows']
    identity = lambda r:(r['pdf_page'],r['column'],r['row'])
    revised = {identity(r):r for r in new}
    changed_codes = set()
    changed_cells = []
    for row in old:
        newrow = revised[identity(row)]
        codes = {row['code'],*row['alternatives']}
        if codes != {newrow['code'],*newrow['alternatives']}:
            changed_codes.update(codes)
            changed_cells.append(identity(row))
    v2 = impact['M_references']['v2']
    affected = {r['sample_index'] for key in ('unit_changes','potential_mappings','class_metadata','affected_chart_locations')
                for r in v2.get(key,[]) if 'sample_index' in r}
    # Walk all impact records so an added affected-record category cannot silently escape filtering.
    def indices(d):
        if isinstance(d,dict):
            return ({d['sample_index']} if 'sample_index' in d else set()) | set().union(*(indices(v) for v in d.values()))
        if isinstance(d,list):
            return set().union(*(indices(v) for v in d))
        return set()
    affected |= indices(v2)
    prior = W.read(W.RAW/'pilot-2026-10-08-v2/coordinator/private-manifest.json')
    old_controls = {r['sample_index'] for b in prior['batches'] for r in b['controls'].values()}
    refs = W.read(W.V2/'blind/adjudicated-reference.json')['rows']
    eligible, audit = [], []
    for row in refs:
        why = []
        if row['sample_index'] in affected: why.append('P v2 affected/potential impact')
        if row['sample_index'] in old_controls: why.append('pilot 1 control')
        codes = {c for u in row['units'] for field in ('strict_candidate_codes','shape_only_candidate_codes') for c in u.get(field,[])}
        if codes & changed_codes: why.append('old code from changed strip')
        for u in row['units']:
            strict = set(u['strict_candidate_codes'])
            if not strict: why.append('empty strict set')
            if any(strict & pair and not pair <= strict for pair in PAIRS): why.append('incomplete coincident pair')
            if strict & {596,454} and u['unit_kind'] != 'hatched_span': why.append('hatched unit kind conflict')
        if any(row.get(k) is None for k in ('printed_inscription_id','classification_literal','drawn_unit_count','crop_correct')):
            why.append('incomplete required field')
        if row.get('unresolved_fields'): why.append('unresolved required fields')
        if not why: eligible.append(row)
        audit.append(dict(sample_index=row['sample_index'],eligible=not why,reasons=sorted(set(why))))
    return eligible, dict(changed_cells=changed_cells, changed_old_codes=sorted(changed_codes), rows=audit,
                          method='Conservative exclusion; no numeric or unit-kind remapping; selected scored fields unchanged')


def charts(out):
    from PIL import Image,ImageDraw,ImageFont
    labels = W.read(CHART)['rows']
    old = W.read(W.M/'chart-snapshot.json')['rows']
    if [(r['pdf_page'],r['column'],r['row']) for r in old] != [(r['pdf_page'],r['column'],r['row']) for r in labels]:
        raise ValueError('Chart card identity/order mismatch')
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    out.mkdir(parents=True)
    for start in range(0,len(labels),60):
        original = Image.open(W.V2/'blind/position-chart'/f'chart_{start:03d}.png').convert('RGB')
        canvas = Image.new('RGB',(1600,1320),'white'); draw=ImageDraw.Draw(canvas)
        for i,label in enumerate(labels[start:start+60]):
            # Preserve the source glyph panel; replace only the separate machine-added label strips.
            ox,oy=(i%10)*120,(i//10)*200
            panel=original.crop((ox+8,oy+8,ox+110,oy+86))
            x,y=(i%10)*160,(i//10)*220
            canvas.paste(panel,(x+20,y+8))
            codes=sorted({label['code'],*label['alternatives']})
            draw.text((x+4,y+96),'codes '+ '/'.join(map(str,codes)),font=font,fill='black')
            draw.text((x+4,y+119),f"{label['pdf_page']}:{label['column']}:{label['row']} class {label['rank']}",font=font,fill='black')
            draw.text((x+4,y+143),'label: '+label['numeric_confidence'],font=font,
                      fill='darkred' if label['numeric_confidence']=='medium' else 'black')
            draw.text((x+4,y+167),'reference v2.1',font=font,fill='black')
        canvas.save(out/f'chart_{start:03d}.png',optimize=True)
    W.write(out/'chart-labels-v2.1.json',dict(version='N-reader-chart-v2.1-2026-10-08-v1',reference_sha256=W.sha(CHART),rows=labels))
    W.write_text(out/'CHART-NOTICE.md',(GUIDANCE/'CHART-NOTICE.md').read_text(encoding='utf-8'))


def prepare(out, summary_out):
    out=W.owned(out)
    if not out.is_relative_to(W.RAW) or out.exists() or Path(summary_out).exists():
        raise ValueError('Use fresh raw packet and aggregate paths')
    W.setup(); start=time.monotonic()
    selection=select()
    W.write(out/'coordinator/selection.json',selection)  # Pin selection before examining selected proposals.
    rows=[]
    with PROPOSALS.open(encoding='utf-8-sig') as stream:
        for line in stream:
            row=json.loads(line)
            if row['pdf_page'] in selection['selected_pages']: rows.append(row)
    if {r['pdf_page'] for r in rows} != set(selection['selected_pages']): raise ValueError('Missing selected proposal page')
    targets=[r for r in rows if r['line_kind']=='numbered']
    batches=sorted({(r['pdf_page'],r['pdf_column']) for r in targets})
    eligible,audit=control_pool()
    ambiguous=[r for r in eligible if any(len(u['strict_candidate_codes'])>1 for u in r['units'])]
    single=[r for r in eligible if all(len(u['strict_candidate_codes'])==1 for u in r['units'])]
    rng=random.Random(2026100806);rng.shuffle(ambiguous);rng.shuffle(single)
    if len(ambiguous)<len(batches) or len(single)<2*len(batches):
        W.write(out/'coordinator/control-filter-failed.json',audit)
        raise ValueError(f'Insufficient compatible controls: ambiguous={len(ambiguous)}, singleton={len(single)}, batches={len(batches)}')
    W.write(out/'coordinator/control-filter.json',audit)
    W.write(out/'coordinator/proposals-v3-selected.json',dict(status='Proposed',source_path=W.relative(PROPOSALS),source_sha256=W.sha(PROPOSALS),rows=rows))
    pred={r['sample_index']:r for r in W.read(W.V2/'predictions.json')['rows']}
    pdf=W.ROOT/'research/corpus/primary/koskenniemi_parpola1979.pdf'
    if W.sha(pdf)!=W.read(CHART)['source_sha256']:raise ValueError('Chart/source witness mismatch')
    dependencies={W.relative(p):W.sha(p) for p in [PROPOSALS,CHART,P/'impact-v2.1.json',P/'RECOMMENDED-USE.md',W.M/'OPTION-B-INTERFACE.md',W.V2/'blind/adjudicated-reference.json',W.V2/'predictions.json',V3/'full-transport-manifest.json' if (V3/'full-transport-manifest.json').exists() else V3/'full-summary.json']}
    dependencies.update({W.relative(p):W.sha(p) for p in (W.V2/'blind/position-chart').glob('*.png')})
    private=dict(schema_version=1,pilot_version=2,status='Proposed',created_utc=W.now(),source_sha256=W.sha(pdf),selection=selection,
                 protocol_sha256=W.sha(W.HERE/'PROTOCOL.md'),dependencies=dependencies,batches=[],
                 adjudicator_instructions=W.relative(GUIDANCE/'adjudication/INSTRUCTIONS.md'),
                 planning=dict(numbered_occurrences=11702,printed_columns=328,continuation_lines=67))
    import fitz
    summaries=[]
    with fitz.open(pdf) as doc:
        for role in ('reader-1','reader-2'):
            W.write_text(out/role/'INSTRUCTIONS.md',(GUIDANCE/role/'INSTRUCTIONS.md').read_text(encoding='utf-8'))
            if role=='reader-1':charts(out/role/'charts')
            else:shutil.copytree(out/'reader-1/charts',out/role/'charts')
            for page in (16,17,18,20,21):
                doc[page-1].get_pixmap(matrix=fitz.Matrix(3,3),colorspace=fitz.csGRAY).save(out/role/'charts'/f'original_pdf{page}.png')
        for bi,(page,column) in enumerate(batches):
            bid=f'pdf{page:03d}-c{column}'
            numbered=sorted([r for r in targets if (r['pdf_page'],r['pdf_column'])==(page,column)],key=lambda r:r['row_index'])
            controls=[ambiguous[bi],single[2*bi],single[2*bi+1]]
            mixed=[(r,None) for r in numbered]+[(pred[r['sample_index']],r) for r in controls];rng.shuffle(mixed)
            items,answers,keys=[],{},{}
            ncols=len({r['pdf_column'] for r in rows if r['pdf_page']==page})
            width,height=doc[page-1].rect.width,doc[page-1].rect.height
            column_box=[max(0,width*column/ncols-12),35,min(width,width*(column+1)/ncols+12),height-25]
            for ix,(r,ref) in enumerate(mixed):
                iid='item-'+W.digest(dict(batch=bid,index=ix,seed=2026100806))[:12]
                rp=r['pdf_page'];w,h=doc[rp-1].rect.width,doc[rp-1].rect.height
                nc=ncols if ref is None else 2
                y=r['row_anchor_y_2x']/2
                continuation=[q for q in rows if q.get('continuation_of')==r['occurrence_key']]
                lower=max([y+32]+[q['row_anchor_y_2x']/2+16 for q in continuation])
                context=[max(0,w*r['pdf_column']/nc-12),max(0,y-28),min(w,w*(r['pdf_column']+1)/nc+12),min(h,lower)]
                items.append(dict(item_id=iid,sample_index=bi*1000+ix,pdf_page=rp,pdf_column=r['pdf_column'],target_y_pdf=y,
                                  target_glyph_pdf_box=r['glyph_pdf_box'],context_pdf_box=context,context_image=f'{iid}-context.png',
                                  exact_image=f'{iid}-exact.png',page_image=f'page-{rp}.png'))
                if ref is None:keys[iid]=r['occurrence_key']
                else:answers[iid]=copy.deepcopy(ref)
            mapping=dict(batch_id=bid,pdf_page=page,pdf_column=column,detected_page_columns=ncols,controls=answers,target_keys=keys,
                         physical_line_keys=[r['occurrence_key'] for r in rows if (r['pdf_page'],r['pdf_column'])==(page,column)],
                         provisional_continuations=[dict(occurrence_key=r['occurrence_key'],continuation_of=r['continuation_of'],segment_id=r['segment_id'])
                             for r in rows if (r['pdf_page'],r['pdf_column'])==(page,column) and r['line_kind']=='continuation'],packets={})
            for role in ('reader-1','reader-2'):
                folder=out/role/bid;folder.mkdir(parents=True)
                for rp in sorted({i['pdf_page'] for i in items}):
                    doc[rp-1].get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY).save(folder/f'page-{rp}.png')
                doc[page-1].get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(column_box),colorspace=fitz.csGRAY).save(folder/'column.png')
                for item in items:
                    for boxfield,filefield in [('context_pdf_box','context_image'),('target_glyph_pdf_box','exact_image')]:
                        doc[item['pdf_page']-1].get_pixmap(matrix=fitz.Matrix(5,5),clip=fitz.Rect(item[boxfield]),colorspace=fitz.csGRAY).save(folder/item[filefield])
                files=sorted(folder.glob('*.png'))+sorted((out/role/'charts').glob('*'))+[out/role/'INSTRUCTIONS.md']
                assets=[dict(path=Path(os.path.relpath(f,folder)).as_posix(),sha256=W.sha(f),bytes=f.stat().st_size) for f in files]
                packet=dict(schema_version=1,status='Proposed',pilot_version=2,role=role,batch_id=bid,reader_mode='blind',
                            source_sha256=private['source_sha256'],source_attribution=W.ATTRIBUTION,license='CC BY 4.0',source_url='http://hdl.handle.net/10138/342677',
                            modifications='Page/column/row raster crops; v3 proposed boxes; unchanged glyph cards with v2.1 label strips',
                            chart_reference=dict(version='N-reader-chart-v2.1-2026-10-08-v1',path=W.relative(CHART),sha256=W.sha(CHART)),
                            chart_code_universe=sorted({c for r in W.read(CHART)['rows'] for c in [r['code']]+r['alternatives']}),
                            assigned_column=dict(pdf_page=page,pdf_column=column,column_pdf_box=column_box,detected_page_columns=ncols,column_image='column.png'),
                            page_dimensions={str(i['pdf_page']):list(doc[i['pdf_page']-1].rect)[2:] for i in items},items=items,assets=assets,instructions='../INSTRUCTIONS.md',proposals=None)
                packet['packet_sha256']=W.packet_hash(packet)
                W.write(folder/'packet.json',packet);W.write(folder/'return-template.json',W.template(packet));W.check_packet(folder/'packet.json')
                mapping['packets'][role]=dict(path=W.relative(folder/'packet.json'),sha256=packet['packet_sha256'])
                summaries.append(dict(role=role,batch_id=bid,target_rows=len(numbered),control_rows=3,assigned_rows=len(items),packet_path=W.relative(folder/'packet.json'),packet_sha256=packet['packet_sha256']))
            private['batches'].append(mapping)
    W.write_text(out/'adjudication/INSTRUCTIONS.md',(GUIDANCE/'adjudication/INSTRUCTIONS.md').read_text(encoding='utf-8'))
    W.write_text(out/'adjudication/PENDING.md','No reading or adjudication has been performed. Generate dispute packets after both blind returns are frozen.\n')
    private['preparation_seconds']=time.monotonic()-start
    W.write(out/'coordinator/private-manifest.json',private)
    summary=dict(status='Verified computation',reader_evaluation_status='Proposed',pilot_version=2,reader_mode='two blind',selected_pages=selection['selected_pages'],
                 eligible_pages=len(selection['eligible_pages']),excluded_pages=len(selection['excluded_pages']),target_detected_rows=len(targets),
                 continuation_proposals=len(rows)-len(targets),columns=len(batches),role_packets=len(summaries),controls_per_role=3*len(batches),
                 compatible_control_pool=dict(ambiguous=len(ambiguous),singleton=len(single)),batches=summaries,raw_directory=W.relative(out),
                 chart_version='N-reader-chart-v2.1-2026-10-08-v1',chart_cells=len(W.read(CHART)['rows']),
                 medium_confidence_labels=sum(r['numeric_confidence']=='medium' for r in W.read(CHART)['rows']),
                 preparation_seconds=private['preparation_seconds'],local_bytes=sum(f.stat().st_size for f in out.rglob('*') if f.is_file()),
                 private_manifest_sha256=W.sha(out/'coordinator/private-manifest.json'),selection_sha256=W.sha(out/'coordinator/selection.json'),
                 dependencies=dependencies,script_sha256=W.sha(__file__),protocol_sha256=private['protocol_sha256'])
    W.write(summary_out,summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('batches','dependencies')},indent=2))
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--summary-out',type=Path,required=True)
    args=parser.parse_args();prepare(args.out,args.summary_out)
