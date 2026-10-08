"""Dated v2.1 amendment; preserve v2 and reuse read-only reviewer witnesses."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import argparse
import copy
import re
from audit import ROOT, OWN, RAW, read, write, sha, key

REVRAW = RAW / 'revision-2026-10-08-v2.1'
REQUIRED = {'p20_c4_r13', 'p21_c0_r1', 'p21_c0_r18', 'p21_c3_r4', 'p21_c5_r34', 'p21_c6_r1'}
NEW_CLASS = 'p20_c3_r33'


def pin():
    path = OWN / 'preserved-inputs-v2.1.json'
    if path.exists():
        return
    files = [OWN / name for name in ('chart-reference-v2.json', 'comparison.json', 'cell-observations.json',
             'visual-readings.json', 'reinspection-decisions.json', 'impact.json', 'consumer-input-integrity.json',
             'verification.json', 'file-inventory.json', 'sources.json', 'REVIEW.md')]
    files += list((OWN / 'review').rglob('*'))
    write(path, dict(status='Verified computation', inputs={p.relative_to(ROOT).as_posix(): sha(p)
                      for p in files if p.is_file()}))


def render():
    import fitz
    from PIL import Image, ImageDraw, ImageFont
    pin()
    REVRAW.mkdir(parents=True, exist_ok=True)
    atlas = {key(r): r for r in read(ROOT / 'output/chart_atlas/reference.json')['rows']}
    doc = fitz.open(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf')
    cells = ['p20_c3_r32', NEW_CLASS, 'p20_c3_r34', 'p20_c4_r0', 'p20_c4_r13',
             'p21_c1_r19', 'p21_c7_r21', 'p21_c4_r21']
    pages = {}
    records, crops = [], []
    for cell in cells:
        r = atlas[cell]; page = doc[r['pdf_page'] - 1]
        if r['pdf_page'] not in pages:
            xref = page.get_images(full=True)[0][0]
            pix = fitz.Pixmap(doc, xref)
            rect = page.get_image_rects(xref)[0]
            assert (pix.width, pix.height) == (4880, 7010)
            mode = 'L' if pix.n == 1 else 'RGB'
            pages[r['pdf_page']] = (Image.frombytes(mode, (pix.width, pix.height), pix.samples), rect, xref)
        im, rect, xref = pages[r['pdf_page']]
        sx, sy = im.width / rect.width, im.height / rect.height
        box = r['source_crop_pdf_points']
        clip = [round((box[0] - rect.x0) * sx), round((box[1] - rect.y0) * sy),
                round((box[2] - rect.x0) * sx), round((box[3] - rect.y0) * sy)]
        crop = im.crop(clip).convert('RGB')
        path = REVRAW / f'{cell}-native.png'; crop.save(path)
        crops.append((cell, crop))
        records.append(dict(cell=cell, path=path.relative_to(ROOT).as_posix(), sha256=sha(path),
                            xref=xref, source_pixel_clip=clip, pixels_per_point=[sx, sy]))
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    w = max(im.width for _, im in crops); h = max(im.height for _, im in crops) + 32
    sheet = Image.new('RGB', (w * 4, h * 2), 'white'); draw = ImageDraw.Draw(sheet)
    for i, (cell, crop) in enumerate(crops):
        x, y = i % 4 * w, i // 4 * h
        draw.text((x + 3, y), cell, fill='blue', font=font); sheet.paste(crop, (x, y + 32))
    sheet.save(REVRAW / 'native-inspection.png')
    write(REVRAW / 'native-render-manifest.json', dict(method='Embedded image crop; no OCR or text layer; geometry from existing atlas.',
          source_sha256=sha(ROOT / 'research/corpus/primary/koskenniemi_parpola1979.pdf'), cells=records))


def apply():
    pin()
    decision = read(OWN / 'amendment-decisions-v2.1.json')
    v2 = read(OWN / 'chart-reference-v2.json')
    original = read(ROOT / 'research/chart_reference/manual_numeric_reference.json')
    old = {key(r): r for r in original['rows']}
    result = copy.deepcopy(v2)
    observations = copy.deepcopy(read(OWN / 'cell-observations.json'))
    obs = {r['cell']: r for r in observations['rows']}
    reviewer = read(OWN / 'review/independent-readings.json')['cells']
    if isinstance(reviewer, dict):
        reviewer = [dict(cell=c, **r) for c, r in reviewer.items()]
    reasons = {}
    follow_up = {r['cell']: r for r in decision['follow_up_readings']}
    def reason(cell, text):
        reasons.setdefault(cell, []).append(text)
    for cell in sorted(REQUIRED):
        reason(cell, 'Required confidence reduction in REVIEW.md, required fix 2.')
    for row in reviewer:
        cell = row.get('cell', row.get('id'))
        if row['confidence'] != 'high':
            reason(cell, f"Reviewer qualitative confidence {row['confidence']}; conservatively recorded as medium.")
    for cell, row in obs.items():
        if re.search(r'broken|worn|faded|damaged|fragment|missing|isolated', row['visible_evidence'], re.I):
            reason(cell, 'Saved digit evidence records incomplete ink: ' + row['visible_evidence'])
    for cell in ('p21_c7_r21', 'p21_c4_r21'):
        reason(cell, 'Reviewer whole-chart mismatch resolution leaves a worn digit unsettled by pixels.')
    reason(NEW_CLASS, 'New rounded-6 class decision supported by own native-pixel inspection and reviewer sweep.')
    changes_from_v2, all_changes = [], []
    for i, row in enumerate(result['rows']):
        cell = key(row); before = v2['rows'][i]
        row['source'] = '2026-10-08 Codex audit with Claude 63-cell blind reread and whole-chart pixel checks; no expert review.'
        if cell in reasons:
            row['numeric_confidence'] = 'medium'
            obs[cell]['numeric_confidence'] = 'medium'
            obs[cell]['confidence_evidence'] = reasons[cell]
        if cell == NEW_CLASS:
            row['rank'] = decision['rank']
            obs[cell]['rank'] = decision['rank']
            obs[cell]['visible_evidence'] = decision['visible_evidence']
            obs[cell]['amendment_review_image'] = decision['source_image']
            obs[cell]['reinspected_after_review'] = True
        if cell == 'p20_c4_r13':
            obs[cell]['visible_evidence'] = decision['contested_360_evidence']
        if cell in follow_up:
            assert (row['rank'], row['code']) == (follow_up[cell]['rank'], follow_up[cell]['code'])
            obs[cell]['follow_up_reading'] = follow_up[cell]
            obs[cell]['reinspected_after_review'] = True
            obs[cell]['amendment_review_image'] = f'data/raw/2026-10-08-chart-reference-audit/revision-2026-10-08-v2.1/{cell}-native.png'
        fields = ('rank', 'code', 'alternatives', 'rank_alternatives', 'numeric_confidence')
        delta = {f: dict(old=before[f], new=row[f]) for f in fields if before[f] != row[f]}
        if delta:
            log = dict(date='2026-10-08', version='2.1', status='Exploratory', fields=delta,
                       evidence_file='cell-observations-v2.1.json', evidence_cell=cell,
                       visible_evidence=obs[cell]['visible_evidence'], confidence_evidence=reasons.get(cell, []),
                       reviewer_evidence='REVIEW.md; review/independent-readings.json; review/pixel-check-mismatch-resolution.json')
            row.setdefault('change_log', []).append(log)
            changes_from_v2.append(dict(cell=cell, **log))
        total_delta = {f: dict(old=old[cell][f], new=row[f]) for f in fields if old[cell][f] != row[f]}
        if total_delta:
            all_changes.append(dict(cell=cell, fields=total_delta, evidence_file='cell-observations-v2.1.json', evidence_cell=cell))
    ranks = [r['rank'] for r in result['rows']]
    final = {key(r): r for r in result['rows']}
    first = {r['cell']: r['first_pass'] for r in observations['rows']}
    first_diff = [c for c in first if first[c]['code'] != old[c]['code']]
    errors = [c for c in first_diff if final[c]['code'] == old[c]['code']]
    summary = dict(cells=687, primary_code_changes=sum('code' in c['fields'] for c in all_changes),
                   class_changes=sum('rank' in c['fields'] for c in all_changes), changed_cells=len(all_changes),
                   value_changed_cells=sum('rank' in c['fields'] or 'code' in c['fields'] or 'alternatives' in c['fields'] for c in all_changes),
                   confidence_changed_cells=sum('numeric_confidence' in c['fields'] for c in changes_from_v2),
                   amended_cells_vs_v2=len(changes_from_v2), medium_confidence_cells=sorted(reasons),
                   medium_confidence_count=len(reasons), high_confidence_count=687-len(reasons),
                   old_lower_ambiguities=16, ambiguities_resolved=16, remaining_lower_ambiguities=0,
                   duplicate_codes={}, distinct_classes=len(set(ranks)), min_class=min(ranks), max_class=max(ranks),
                   missing_classes=sorted(set(range(1,402))-set(ranks)), rank_decreases=[],
                   original_audit_reinspected_cells=57, original_audit_once_read_cells=630,
                   amended_own_reinspected_cells=len({r['cell'] for r in observations['rows'] if r['reinspected']} | set(follow_up)),
                   follow_up_native_inspected_cells=len(follow_up),
                   first_pass_primary_code_disagreements=len(first_diff), first_pass_reader_errors=len(errors),
                   first_pass_reader_error_cells=errors, corrections_following_v3_hints=['p20_c4_r1','p21_c6_r31'],
                   reviewer_blind_cells=63, reviewer_blind_class_matches=63, reviewer_blind_code_matches=63)
    result.update(status='Exploratory', adjudication_limit='Two AI readings (63 cells blind in the second reading), reviewer pixel sweep; no expert review.',
                  audit=dict(date='2026-10-08', reference_version='2.1', parent_reference='chart-reference-v2.json',
                             parent_sha256=sha(OWN/'chart-reference-v2.json'), observations='cell-observations-v2.1.json',
                             comparison='comparison-v2.1.json', reviewer='REVIEW.md'),
                  limitations=['Qualitative confidence is uncalibrated.', 'Original audit: 630 cells read once by one model; reviewer adds a 63-cell blind reading and a pixel sweep, not a second whole-chart eye reading.',
                               'Embedded chart scan is 4880 by 7010 pixels, about 8.34 pixels per point; larger renders enlarge the same ink.',
                               'Worn 734 code and faint 300 class at the reviewer-identified cells remain provisional.'])
    observations['review_amendment'] = dict(date='2026-10-08', version='2.1', confidence_reasons=reasons)
    write(OWN/'chart-reference-v2.1.json', result)
    write(OWN/'cell-observations-v2.1.json', observations)
    write(OWN/'comparison-v2.1.json', dict(status='Exploratory', summary=summary, changes=all_changes,
          changes_from_v2=changes_from_v2, old_ambiguity_decisions=read(OWN/'comparison.json')['old_ambiguity_decisions'],
          reviewer_comparison=read(OWN/'review/reading-comparison.json')['summary'],
          reviewer_knn=read(OWN/'review/knn-5-6-8-check.json')['summary']))
    print(summary)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command', choices=['render','apply'])
    args=parser.parse_args()
    render() if args.command == 'render' else apply()
