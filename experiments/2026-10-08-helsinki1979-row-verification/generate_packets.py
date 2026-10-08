"""Prepare immutable column batches. Never performs source readings."""
from __future__ import annotations
import argparse
import copy
import json
import random
import shutil
import time
from collections import defaultdict
from pathlib import Path
import workflow as W

SECTIONS = [('number_order', 22, 78), ('end_sorted', 79, 130), ('beginning_sorted', 131, 180)]


def exclusions():
    reasons = defaultdict(list)
    dependencies = {}
    def add(pages, origin):
        for page in pages:
            if type(page) is int and 22 <= page <= 180 and origin not in reasons[page]:
                reasons[page].append(origin)
    add([22, 25, 30, 37, 62, 78, 100, 129, 130, 145], 'known development pages in protocol')
    paths = sorted(set(W.M.glob('**/blind/selection*.json')) | set(W.M.glob('blind/selection*.json'))
                   | set(W.M.glob('**/freeze-manifest.json'))
                   | set(W.M.glob('follow-up/**/layout-development-*.json')))
    for path in paths:
        d = W.read(path)
        origin = W.relative(path)
        dependencies[origin] = W.sha(path)
        add(d.get('development_pages', []), origin)
        for field in ('count_pages', 'random_count_pages', 'stress_pages'):
            add(d.get(field, []), origin)
        for row in d.get('rows', []):
            add([row.get('pdf_page')], origin)
        for page in d.get('pages', []):
            if isinstance(page, dict):
                add([page.get('pdf_page')], origin)
    rng = random.Random(20261008)
    pools = {name: [p for p in range(lo, hi + 1) if p not in reasons] for name, lo, hi in SECTIONS}
    if any(not pool for pool in pools.values()):
        raise ValueError('No eligible page in a section')
    pages = {name: rng.choice(pool) for name, pool in pools.items()}
    return dict(seed=20261008, rule='one choice per section in section order from ascending eligible lists',
                eligible_pages=pools, selected_pages=pages,
                excluded_pages={str(p): reasons[p] for p in sorted(reasons)}, dependency_hashes=dependencies)


def export_proposal(row):
    return dict(printed_inscription_id=row.get('inscription_number'),
                classification_literal=row.get('classification_code'), drawn_unit_count=len(row['units']),
                units=[dict(unit_index=i, strict_candidate_codes=u['alternatives'][0]['codes'] if u['alternatives'] else [],
                            alternatives=[dict(codes=a['codes'], chart_location=a['template_key']) for a in u['alternatives']],
                            underline_dashes=u['alternatives'][0].get('dashed_auxiliary') if u['alternatives'] else None,
                            unit_kind='unresolved', proposal_confidence=u.get('confidence'))
                       for i, u in enumerate(row['units'])])


def make(out, summary_out, proposal_path=None, pages=None):
    out = W.owned(out)
    if not out.is_relative_to(W.RAW) or out.exists():
        raise ValueError('Choose a fresh local raw packet directory')
    if Path(summary_out).exists():
        raise FileExistsError(summary_out)
    W.setup()
    started = time.monotonic()
    selection = exclusions()
    if proposal_path:
        if not pages or any(p < 22 or p > 180 for p in pages) or len(set(pages)) != len(pages):
            raise ValueError('External proposals require explicit unique corpus pages')
        selection = dict(rule='Explicit full-run or reviewed follow-up page list; not the seeded pilot',
                         seed=None, selected_pages={f'{next(s for s, lo, hi in SECTIONS if lo <= p <= hi)}:{p}': p for p in sorted(pages)},
                         eligible_pages={}, excluded_pages={}, dependency_hashes={W.relative(proposal_path): W.sha(proposal_path)})
    # Commit selection before loading inference or examining output.
    W.write(out / 'coordinator/selection.json', selection)
    freeze = W.read(W.V2 / 'freeze-manifest.json')
    paths = [W.M / p for p in freeze['code_hashes']]
    for path in paths:
        if W.sha(path) != freeze['code_hashes'][path.relative_to(W.M).as_posix()]:
            raise ValueError(f'V2 frozen dependency changed: {path}')
    pdf = W.ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'
    if W.sha(pdf) != freeze['source_sha256']:
        raise ValueError('PDF hash differs from v2 source')
    import fitz
    def disk_gate():
        free = shutil.disk_usage(out).free
        if free < 1000000000:
            raise OSError(f'Stop before packet writes: {free} bytes free (<1 GB)')
    disk_gate()
    targets, pages_meta = [], []
    if proposal_path:
        payload = W.read(proposal_path) if Path(proposal_path).suffix != '.jsonl' else dict(rows=[json.loads(line) for line in Path(proposal_path).read_text(encoding='utf-8').splitlines() if line.strip()])
        targets = [r for r in payload['rows'] if r['pdf_page'] in pages]
        for page in sorted(pages):
            rows = [r for r in targets if r['pdf_page'] == page]
            if not rows:
                raise ValueError(f'No supplied proposal rows for page {page}')
            required = {'pdf_column', 'row_index', 'glyph_pdf_box', 'row_anchor_y_2x', 'units', 'occurrence_key'}
            if any(not required.issubset(r) for r in rows):
                raise ValueError('External proposal adapter lacks required geometry/unit fields')
            pages_meta.append(dict(pdf_page=page, section=next(s for s, lo, hi in SECTIONS if lo <= page <= hi),
                                   detected_rows=len(rows), columns=len({r['pdf_column'] for r in rows}), proposal_seconds=None))
    else:
        P = W.load_module('pipeline', W.M / 'pipeline.py', redirect_pipeline=True)
        L = W.load_module('helsinki_n_layout', W.M / 'layout_v3.py')
        rec = P.Recognizer(P.templates(), W.M / 'development/classifier.pt')
        with fitz.open(pdf) as doc:
            for section, page in selection['selected_pages'].items():
                t = time.monotonic()
                _, rows, meta = L.process(doc, page, rec)
                for row in rows:
                    row['section'] = section
                targets.extend(rows)
                pages_meta.append(dict(pdf_page=page, section=section, detected_rows=len(rows),
                                       columns=meta['column_count'], proposal_seconds=time.monotonic() - t,
                                       layout=meta))
                print(json.dumps(dict(page=page, detected_rows=len(rows), columns=meta['column_count'])), flush=True)
    if any(p['detected_rows'] == 0 for p in pages_meta):
        raise RuntimeError('Selected page has zero detections: prepare a reviewed source inventory before packet generation')
    W.write(out / 'coordinator/proposals-v2.json', dict(status='Proposed', rows=targets, pages=pages_meta,
                                                       method_freeze_sha256=W.sha(W.V2 / 'freeze-manifest.json')))
    refs = W.read(W.V2 / 'blind/adjudicated-reference.json')['rows']
    pred = {r['sample_index']: r for r in W.read(W.V2 / 'predictions.json')['rows']}
    batches = sorted({(r['pdf_page'], r['pdf_column']) for r in targets})
    control_rng = random.Random(2026100801)
    ambiguous = [r for r in refs if any(len(u['strict_candidate_codes']) > 1 for u in r['units'])]
    single = [r for r in refs if all(len(u['strict_candidate_codes']) == 1 for u in r['units'])]
    control_rng.shuffle(ambiguous)
    control_rng.shuffle(single)
    if not proposal_path and (len(ambiguous) < len(batches) or len(single) < 2 * len(batches)):
        raise ValueError('Insufficient distinct controls for batch count')
    chart_files = sorted((W.V2 / 'blind/position-chart').glob('*.png'))
    if not chart_files:
        raise FileNotFoundError('V2 positional chart cards absent')
    private = dict(schema_version=1, status='Proposed', created_utc=W.now(),
                   source_sha256=W.sha(pdf), selection=selection, batches=[],
                   protocol_sha256=W.sha(W.HERE / 'PROTOCOL.md'),
                   dependencies={W.relative(p): W.sha(p) for p in paths + [W.V2 / 'blind/adjudicated-reference.json',
                                                                          W.V2 / 'predictions.json', W.M / 'evaluate.py']})
    summaries = []
    with fitz.open(pdf) as doc:
        for role in ('reader-1', 'reader-2'):
            chart = out / role / 'charts'
            chart.mkdir(parents=True)
            for file in chart_files:
                shutil.copyfile(file, chart / file.name)
            for page in (16, 17, 18, 20, 21):
                disk_gate()
                doc[page - 1].get_pixmap(matrix=fitz.Matrix(3, 3), colorspace=fitz.csGRAY).save(chart / f'original_pdf{page}.png')
            instructions = (W.HERE / 'pilot' / role / 'INSTRUCTIONS.md').read_text(encoding='utf-8')
            W.write_text(out / role / 'INSTRUCTIONS.md', instructions)
        for bidx, (page, column) in enumerate(batches):
            bid = f'pdf{page:03d}-c{column}'
            target = sorted([r for r in targets if (r['pdf_page'], r['pdf_column']) == (page, column)], key=lambda r: r['row_index'])
            controls = [ambiguous[bidx % len(ambiguous)], single[(2 * bidx) % len(single)], single[(2 * bidx + 1) % len(single)]]
            all_rows = [(r, None) for r in target] + [(pred[r['sample_index']], r) for r in controls]
            control_rng.shuffle(all_rows)
            item_specs, answers, proposals, target_keys = [], {}, {}, {}
            for idx, (r, reference) in enumerate(all_rows):
                iid = 'item-' + W.digest(dict(batch=bid, offset=idx, seed=2026100801))[:12]
                width, height = doc[r['pdf_page'] - 1].rect.width, doc[r['pdf_page'] - 1].rect.height
                # Include the whole broad column, rather than a model's truncated glyph-to-field edge.
                ncols = next((p['columns'] for p in pages_meta if p['pdf_page'] == r['pdf_page']), 2)
                left, right = max(0, width * r['pdf_column'] / ncols - 12), min(width, width * (r['pdf_column'] + 1) / ncols + 12)
                box = r['glyph_pdf_box']
                y = r['row_anchor_y_2x'] / 2
                context = [left, max(0, y - 28), right, min(height, y + 32)]
                item_specs.append(dict(item_id=iid, sample_index=bidx * 1000 + idx, pdf_page=r['pdf_page'],
                                       pdf_column=r['pdf_column'], target_y_pdf=y,
                                       target_glyph_pdf_box=box, context_pdf_box=context,
                                       context_image=f'{iid}-context.png', exact_image=f'{iid}-exact.png',
                                       page_image=f'page-{r["pdf_page"]}.png'))
                proposals[iid] = export_proposal(r)
                if reference is not None:
                    answers[iid] = copy.deepcopy(reference)
                else:
                    target_keys[iid] = r['occurrence_key']
            page_dimensions = {str(r['pdf_page']): list(doc[r['pdf_page'] - 1].rect)[2:] for r in item_specs}
            column_box = [max(0, doc[page - 1].rect.width * column / len({r['pdf_column'] for r in targets if r['pdf_page'] == page}) - 12),
                          35, min(doc[page - 1].rect.width, doc[page - 1].rect.width * (column + 1) / len({r['pdf_column'] for r in targets if r['pdf_page'] == page}) + 12),
                          doc[page - 1].rect.height - 25]
            mapping = dict(batch_id=bid, pdf_page=page, pdf_column=column,
                           detected_page_columns=next(p['columns'] for p in pages_meta if p['pdf_page'] == page),
                           controls=answers, target_keys=target_keys, packets={})
            for role in ('reader-1', 'reader-2'):
                folder = out / role / bid
                folder.mkdir(parents=True)
                disk_gate()
                for rp in sorted({r['pdf_page'] for r in item_specs}):
                    doc[rp - 1].get_pixmap(matrix=fitz.Matrix(2, 2), colorspace=fitz.csGRAY).save(folder / f'page-{rp}.png')
                doc[page - 1].get_pixmap(matrix=fitz.Matrix(3, 3), clip=fitz.Rect(column_box), colorspace=fitz.csGRAY).save(folder / 'column.png')
                for loc in item_specs:
                    for field, filefield in [('context_pdf_box', 'context_image'), ('target_glyph_pdf_box', 'exact_image')]:
                        doc[loc['pdf_page'] - 1].get_pixmap(matrix=fitz.Matrix(5, 5), clip=fitz.Rect(loc[field]), colorspace=fitz.csGRAY).save(folder / loc[filefield])
                if role == 'reader-1':
                    W.write(folder / 'proposals.json', dict(method='External pinned proposals' if proposal_path else 'Package M frozen v2; unverified proposals', rows=proposals))
                files = sorted(folder.glob('*.png')) + sorted((out / role / 'charts').glob('*.png')) + [out / role / 'INSTRUCTIONS.md']
                if role == 'reader-1':
                    files.append(folder / 'proposals.json')
                assets = [dict(path=Path(__import__('os').path.relpath(f, folder)).as_posix(), sha256=W.sha(f), bytes=f.stat().st_size) for f in files]
                packet = dict(schema_version=1, status='Proposed', role=role, batch_id=bid,
                              source_sha256=private['source_sha256'], source_attribution=W.ATTRIBUTION,
                              license='CC BY 4.0', source_url='http://hdl.handle.net/10138/342677',
                              modifications='Page and row raster crops; positional chart card arrangement',
                              assigned_column=dict(pdf_page=page, pdf_column=column, column_pdf_box=column_box,
                                                   detected_page_columns=mapping['detected_page_columns'],
                                                   column_image='column.png'), page_dimensions=page_dimensions,
                              items=item_specs, assets=assets,
                              instructions='../INSTRUCTIONS.md', proposals='proposals.json' if role == 'reader-1' else None)
                packet['packet_sha256'] = W.packet_hash(packet)
                W.write(folder / 'packet.json', packet)
                W.write(folder / 'return-template.json', W.template(packet))
                W.check_packet(folder / 'packet.json')
                mapping['packets'][role] = dict(path=W.relative(folder / 'packet.json'), sha256=packet['packet_sha256'])
                summaries.append(dict(role=role, batch_id=bid, pdf_page=page, pdf_column=column,
                                      target_rows=len(target), control_rows=3, assigned_rows=len(item_specs),
                                      packet_path=W.relative(folder / 'packet.json'), packet_sha256=packet['packet_sha256']))
            private['batches'].append(mapping)
    private['preparation_seconds'] = time.monotonic() - started
    W.write(out / 'coordinator/private-manifest.json', private)
    raw_bytes = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    summary = dict(status='Verified computation', reader_evaluation_status='Proposed', created_utc=W.now(),
                   selected_pages=selection['selected_pages'], eligible_page_counts={s: len(p) for s, p in selection['eligible_pages'].items()},
                   excluded_pages=len(selection['excluded_pages']), target_detected_rows=len(targets),
                   columns=len(batches), controls_per_role=3 * len(batches), distinct_controls=len({r['sample_index'] for b in private['batches'] for r in b['controls'].values()}),
                   role_packets=len(summaries), batches=summaries, raw_directory=W.relative(out),
                   local_bytes=raw_bytes, preparation_seconds=private['preparation_seconds'], pages=pages_meta,
                   private_manifest_sha256=W.sha(out / 'coordinator/private-manifest.json'),
                   selection_sha256=W.sha(out / 'coordinator/selection.json'),
                   source_sha256=private['source_sha256'], dependency_hashes=private['dependencies'],
                   generator_sha256=W.sha(__file__), workflow_sha256=W.sha(W.HERE / 'workflow.py'),
                   external_proposal_path=W.relative(proposal_path) if proposal_path else None,
                   external_proposal_sha256=W.sha(proposal_path) if proposal_path else None,
                   control_reuse_policy='Distinct within pilot; cyclic seeded pool for explicit full-run batches',
                   scratch_path_adaptation='Only pipeline RAW constant redirected in memory to package N; no M writes')
    # Do not retain OCR strings, column layout payloads or source-derived rows in tracked aggregate.
    summary['pages'] = [{k: v for k, v in p.items() if k != 'layout'} for p in pages_meta]
    W.write(summary_out, summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('batches', 'dependency_hashes', 'pages')}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--summary-out', type=Path, required=True)
    parser.add_argument('--proposals', type=Path, help='Reviewed external v3 proposal JSON/JSONL using documented adapter fields')
    parser.add_argument('--pages', nargs='+', type=int, help='Explicit pages for external proposals; does not alter pilot rule')
    args = parser.parse_args()
    make(args.out, args.summary_out, args.proposals, args.pages)
