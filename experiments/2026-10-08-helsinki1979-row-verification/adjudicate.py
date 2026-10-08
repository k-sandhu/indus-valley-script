"""Build anonymous, source-only adjudication packets from frozen returns."""
from __future__ import annotations
import argparse
import copy
import os
import random
import shutil
from pathlib import Path
import workflow as W
import score_pilot as S


def anonymous(row):
    if row is None:
        return None
    fields = ('item_id', 'sample_index', 'pdf_page', 'pdf_column', 'source_row_ordinal', 'source_y_pdf',
              'printed_inscription_id', 'classification_literal', 'drawn_unit_count', 'crop_correct',
              'valid_printed_target', 'blank_gaps', 'continuation_y_pdf', 'continuation_rows', 'unresolved_fields',
              'unresolved_boundary', 'source_observations')
    result = {k: copy.deepcopy(row.get(k)) for k in fields}
    result['units'] = [{k: copy.deepcopy(u[k]) for k in ('strict_candidate_codes', 'unit_kind', 'underline_dashes',
                        'uncertainty_reason', 'source_line_y_pdf', 'note', 'chart_locations') if k in u} for u in row['units']]
    return result


def prepare(run, returns, out):
    out = W.owned(out)
    if not out.is_relative_to(W.RAW) or out.exists():
        raise ValueError('Choose fresh local raw adjudication output')
    state = S.collect(run, returns)
    if state['errors']:
        raise ValueError('Invalid initial returns must be corrected in new files before adjudication')
    rng = random.Random(2026100804)
    summary = []
    for b in state['batches']:
        rows, coverage = S.comparison(b)
        disputed = [r for r in rows if r['requires_adjudication']]
        if not disputed:
            continue
        bid = b['batch']['batch_id']
        source_packet_path = W.ROOT / b['batch']['packets']['reader-2']['path']
        source_packet = b['packet']['reader-2']
        role = out / 'adjudicator'
        folder = role / bid
        folder.mkdir(parents=True)
        instructions = (W.HERE / 'pilot/adjudication/INSTRUCTIONS.md').read_text(encoding='utf-8')
        if not (role / 'INSTRUCTIONS.md').exists():
            W.write_text(role / 'INSTRUCTIONS.md', instructions)
        # Copy images and chart only. No proposal file or original reader metadata is delivered.
        for asset in source_packet['assets']:
            if not asset['path'].endswith('.png'):
                continue
            target = (folder / asset['path']).resolve()
            W.owned(target)
            if not target.is_relative_to(role):
                raise ValueError('Adjudication asset escapes delivery root')
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copyfile(source_packet_path.parent / asset['path'], target)
        labels, readings, items = {}, {}, []
        originals = {r['item_id']: r for r in source_packet['items']}
        for dispute in disputed:
            iid = dispute['item_id']
            order = ['reader-1', 'reader-2']
            rng.shuffle(order)
            labels[iid] = dict(zip(('A', 'B'), order))
            byrole = {'reader-1': dispute['a'], 'reader-2': dispute['b']}
            readings[iid] = dict(A=anonymous(byrole[order[0]]), B=anonymous(byrole[order[1]]),
                                 disputed_fields=dispute['differences'])
            loc = originals.get(iid)
            if loc is None:
                row = dispute['a'] or dispute['b']
                loc = dict(item_id=iid, sample_index=row['sample_index'], pdf_page=row['pdf_page'],
                           pdf_column=row['pdf_column'], target_y_pdf=row['source_y_pdf'],
                           context_image='column.png', exact_image='column.png',
                           page_image=f'page-{row["pdf_page"]}.png',
                           target_glyph_pdf_box=source_packet['assigned_column']['column_pdf_box'])
            items.append(copy.deepcopy(loc))
        # Inventory labels are independently randomized; they do not disclose the per-item mapping.
        order = ['reader-1', 'reader-2']
        rng.shuffle(order)
        inventory = {letter: copy.deepcopy(b['readings'][who]['columns']) for letter, who in zip(('A', 'B'), order)}
        W.write(folder / 'readings.json', dict(rows=readings, column_inventories=inventory))
        assets = [dict(path=Path(os.path.relpath(p, folder)).as_posix(), sha256=W.sha(p), bytes=p.stat().st_size)
                  for p in sorted(folder.glob('*.png')) + sorted((role / 'charts').glob('*.png'))
                  + [folder / 'readings.json', role / 'INSTRUCTIONS.md']]
        packet = dict(schema_version=1, status='Proposed', batch_id=bid, role='adjudicator',
                      source_sha256=source_packet['source_sha256'], source_attribution=W.ATTRIBUTION,
                      license='CC BY 4.0', items=items, assets=assets,
                      assigned_column=source_packet['assigned_column'], page_dimensions=source_packet['page_dimensions'],
                      instructions='../INSTRUCTIONS.md', readings='readings.json', proposals=None,
                      requires_complete_inventory=not coverage)
        packet['packet_sha256'] = W.packet_hash(packet)
        W.write(folder / 'packet.json', packet)
        form = W.template(packet)
        for row in form['rows']:
            row['adjudication_basis'] = None
        W.write(folder / 'return-template.json', form)
        W.check_packet(folder / 'packet.json')
        W.write(out / 'coordinator' / (bid + '.json'), dict(labels=labels, inventory_labels=dict(zip(('A', 'B'), order)),
                   initial_reading_hashes={r: b['hashes'][r]['sha256'] for r in ('reader-1', 'reader-2')},
                   packet_sha256=packet['packet_sha256']))
        summary.append(dict(batch_id=bid, disputed_rows=len(disputed), packet_sha256=packet['packet_sha256'],
                            path=W.relative(folder / 'packet.json')))
    W.write(out / 'coordinator/preparation-summary.json', dict(status='Verified computation', packets=summary,
                  pending_initial_batches=sum(len(b['readings']) < 2 for b in state['batches']), seed=2026100804,
                  script_sha256=W.sha(__file__)))
    print(f'Prepared {len(summary)} adjudication packets')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--returns', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    prepare(args.run, args.returns, args.out)
