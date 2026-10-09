"""Versioned derivation, extraction and alias corrections from the PDF review."""
import argparse, copy, collections, os, re
from pathlib import Path
from pdf_followup import ROOT, OWN, RAW, WORK, OUT, PDF, read, write, sha

BASE = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / BASE.name
EMPTY_CAPTIONS = {
    'R0146': ('SA-DEVA', 'Comma-delimited caption'),
    'R0149': ('DEVA-DAna-PAla-; -4-PAla', 'Name plus quantity, separated by semicolon'),
    'R0441': ('DEVA-DAna-PAla-; -4-PAla', 'Name plus quantity, separated by semicolon'),
    'R0796': ('DEVA-DAna-PAla-; 4-PAla', 'Name plus quantity, separated by semicolon'),
    'R0898': ('DEVA-DAna-PAla-; -4-PAla', 'Name plus quantity, separated by semicolon'),
    'R0946': ('DEVA-DAna-PAla-; 4-PAla', 'Name plus quantity, separated by semicolon'),
    'R0151': ('DEVA-; -DEVA-KA-vara-mAna', 'Separated sign-caption spans'),
    'R0341': ('DEVA-; -DEVA-KA-vara-mAna', 'Separated sign-caption spans'),
    'R0530': ('DEVA-; -DEVA-KA-vara-mAna', 'Separated sign-caption spans'),
    'R0549': ('DEVA-; -DEVA-KA-vara-mAna', 'Separated sign-caption spans'),
    'R0936': ('DEVA-; -DEVA-KA-vara- mAna', 'Separated sign-caption spans; source spacing retained'),
    'R0842': ('Dana-PAla-', 'Caption followed by unseparated romanized name and nested alias')}
BAD_CODES = {'R1094', 'R1097', 'R1100', 'R1112'}
MISJOINS = {'R0374', 'R0633', 'R0860', 'R0873', 'R0917', 'R0951'}


def derivations(output):
    old = read(OUT / 'value-derivations-v2.json')
    rows = copy.deepcopy(old['rows'])
    changes = []
    corrections = {
        17: ('mixed metrological and dictionary-derived', [50, 51, 55, 67, 68, 76, 202], False,
             'pala is proposed from weight/M contexts; pāla from Monier-Williams name endings; bala fitted to balapati.'),
        18: ('pictorial and metrological anchor', [45, 46, 47, 55, 132, 134], True,
             'Bow/wealth near-homonym and numeral/asset contexts; later section labels reverse DAna1/DAna2.'),
        19: ('pictorial and metrological anchor', [45, 46, 47, 55, 132, 134], True,
             'Same initial bow/wealth argument; preserve the source label reversal.'),
        29: ('metrology or M field', [45, 46, 55, 189], True,
             'Fish proposed as a weight unit; mīna is the anchor, while -min is a later extension.'),
        31: ('mixed pictorial/metrological anchor and later extension', [185, 186, 187], True,
             'caru from the pot-like drawing and numeral contexts; cāru as a name element is later.'),
        48: ('mixed pictorial and reading-supported', [215, 216], False,
             'Animal drawing is supported by plausibility of seven of eight readings; the value is provisional.'),
        49: ('mixed pictorial and reading-supported', [215, 216], False,
             'Animal drawing is supported through reading examples; GO is more tentative than ASHVA.'),
        50: ('structural/predicate anchor', [56, 57, 58, 59, 60, 61], True,
             '2014 possession/predicate argument; a non-lexical structural hypothesis.'),
        51: ('structural/predicate and pictorial anchor', [61], True,
             '2014 predicate argument with an arrow/near-homonym proposal.'),
        52: ('structural/predicate anchor', [64, 65, 66], True,
             '2014 nominalization/property proposal from predicate/possession structure.')}
    for row in rows:
        role = row['table18_entry']
        if role in corrections:
            before = copy.deepcopy(row)
            category, pages, certain, basis = corrections[role]
            row.update(category=category, source_pages=pages,
                       dictionary_context_search_excluded_with_confidence=certain, basis=basis)
            if role == 17:
                row['value_origins'] = {'pala': 'metrology or M field',
                                       'pAla': 'dictionary search against contexts',
                                       'bala': 'dictionary-fitted later extension'}
            if role == 29:
                row['value_origins'] = {'mIna': 'metrology or M field', 'min': 'later extension'}
            if role == 31:
                row['value_origins'] = {'caru': 'pictorial/numeral anchor', 'cAru': 'later extension'}
            row['review_evidence'] = 'review-pdf/derivation-recheck.json; second-edition manuscript'
            changes.append({'entry': role, 'before': before, 'after': copy.deepcopy(row)})
    payload = {'status': 'Exploratory', 'supersedes': 'pdf-2026-10-09-v1/value-derivations-v2.json',
               'rows': rows, 'changed_entries': len(changes),
               'classification_note': 'Origins concern the author’s argument. They do not establish a sign value.',
               'numeral_motivation_sensitivity': {'entries': [12, 15], 'pages': [113, 183],
                    'basis': 'Numeral motivation is suggested, but non-lexical derivation is unstated; keep later-extension labels.'}}
    write(output / 'value-derivations-v3.json', payload)
    write(output / 'derivation-changes.json', {'status': 'Exploratory', 'rows': changes})
    return payload


def inventory(output, local, render=False):
    original = read(WORK / 'reading-inventory-v4.json')
    rows = copy.deepcopy(original)
    selected = {r['reading_id']: r for r in read(WORK / 'lexical-selection-v2.json')['readings']}
    changes = []
    for row in rows:
        rid = row['reading_id']; before = copy.deepcopy(row)
        if rid in BAD_CODES:
            assert re.fullmatch(r'[A-Za-z]+-[0-9]+', row['proposed_reading'])
            row['proposed_reading'] = None; row['proposed_gloss'] = None
            row['extraction_correction'] = 'Alias-only continuation caption; catalogue code removed from transcription.'
        if rid in EMPTY_CAPTIONS:
            assert row['proposed_reading'] is None
            caption, basis = EMPTY_CAPTIONS[rid]
            # Source spaces may differ in text extraction; do not fit a lexical result.
            joined = ' '.join(row['caption_blocks'])
            assert re.sub(r'\s', '', caption) in re.sub(r'\s', '', joined), (rid, caption)
            row['proposed_reading'] = caption
            row['extraction_correction'] = basis
            first = row['caption_blocks'][0]
            row['proposed_gloss'] = (first.split('/', 1)[1].strip() if '/' in first else
                                      first[len(caption):].lstrip(' ,'))
        text = row.get('source_text', '')
        added_terms = re.findall(r'\bdoubtful\b|\bquestionable\b|\?', text, re.I)
        if added_terms:
            row['unclear_or_unattested_flag'] = True
            row['uncertainty_terms_added'] = sorted(set(t.lower() for t in added_terms))
            row['uncertainty_scope'] = 'Entry-level source wording; question marks may qualify aliases or transcriptions.'
        if rid in MISJOINS:
            row['probable_misjoin_flag'] = True
            row['join_status_with_probable_misjoins_excluded'] = 'withheld pending source/object adjudication'
            row['join_correction_evidence'] = 'review-pdf/join-audit.json; printed ICIT/CISI conflict and figure-length comparison'
        if row != before:
            changes.append({'reading_id': rid, 'source_page': row['source_page'],
                            'primary_label': row['primary_label'],
                            'transcription_changed': row['proposed_reading'] != before['proposed_reading'],
                            'correction': row.get('extraction_correction'),
                            'unclear_before': before['unclear_or_unattested_flag'],
                            'unclear_after': row['unclear_or_unattested_flag'],
                            'probable_misjoin': rid in MISJOINS,
                            'in_frozen_lexical_selection': rid in selected,
                            'frozen_selection_basis': selected.get(rid, {}).get('basis')})
    attempts = [r for r in rows if r['is_reading_attempt']]
    old_attempts = [r for r in original if r['is_reading_attempt']]
    flagged_families = set().union(*(set(r['joined_object_family_ids']) for r in attempts if r['reading_id'] in MISJOINS))
    joined = [r for r in attempts if r['joined_object_family_ids']]
    kept_rows = [r for r in joined if r['reading_id'] not in MISJOINS]
    kept_objects = [r for r in joined if not (set(r['joined_object_family_ids']) & flagged_families)]
    families = lambda population: set().union(*(set(r['joined_object_family_ids']) for r in population))
    review = read(OWN / 'review-pdf/join-audit.json')
    suspects = [r for r in review['disagreement_objects'] if set(r['rows']) & MISJOINS]
    assert set().union(*(set(r['rows']) for r in suspects)) == MISJOINS
    join_payload = {'status': 'Exploratory', 'attempts': len(attempts),
                    'original_explicit_alias_matches': {'attempts': len(joined), 'families': len(families(joined))},
                    'excluding_six_reading_rows': {'attempts': len(kept_rows), 'families': len(families(kept_rows))},
                    'excluding_four_probable_misjoined_objects': {'attempts': len(kept_objects), 'families': len(families(kept_objects))},
                    'probable_misjoin_rows': sorted(MISJOINS), 'flagged_object_families': len(flagged_families),
                    'source_evidence': suspects,
                    'other_identifier_conflicts': [r for r in review['disagreement_objects'] if not (set(r['rows']) & MISJOINS)],
                    'identity_note': 'Preserve original CISI aliases. ICIT-number/length evidence flags ambiguity; no alternate numeric join adopted.'}
    write(output / 'join-corrections.json', join_payload)
    write(local / 'reading-inventory-v5.json', rows)
    write(local / 'reading-correction-details.json', [
        {'before': a, 'after': b} for a, b in zip(original, rows) if a != b])
    totals = {'status': 'Exploratory', 'source_rows': len(rows), 'attempts': len(attempts),
              'source_labels': len({r['primary_label'] for r in attempts}),
              'transcriptions_before': sum(bool(r['proposed_reading']) for r in old_attempts),
              'transcriptions_after': sum(bool(r['proposed_reading']) for r in attempts),
              'catalogue_code_transcriptions_removed': len(BAD_CODES),
              'empty_transcriptions_recovered': len(EMPTY_CAPTIONS),
              'unclear_before': sum(r['unclear_or_unattested_flag'] for r in old_attempts),
              'unclear_after': sum(r['unclear_or_unattested_flag'] for r in attempts),
              'attempts_newly_flagged': sum(not a['unclear_or_unattested_flag'] and b['unclear_or_unattested_flag']
                  for a, b in zip(original, rows) if b['is_reading_attempt']),
              'attempts_with_added_keyword_or_question_mark': sum(bool(r.get('uncertainty_terms_added')) for r in attempts),
              'lexical_selection': 'Frozen selection unchanged; recovered captions do not automatically add a whole-headword window.',
              'changes': changes, 'joins': {k: v for k, v in join_payload.items() if k not in ['source_evidence', 'other_identifier_conflicts']}}
    write(output / 'reading-corrections.json', totals)
    index_keys = ['reading_id', 'source_page', 'primary_label', 'source_kind', 'is_reading_attempt',
                  'unclear_or_unattested_flag', 'cisi_aliases', 'mh_aliases', 'icit_aliases', 'join_status']
    write(output / 'reading-index-v5.json', {'status': 'Exploratory', 'rows': [
        {k: r.get(k) for k in index_keys} | {'has_transcription': bool(r['proposed_reading']),
            'glyph_count': len(r['sign_sequence_assumed_rtl']),
            'probable_misjoin': r['reading_id'] in MISJOINS,
            'joined_objects_original': len(r['joined_object_family_ids'])} for r in rows]})
    if render:
        render_corrections(rows, local)
    return totals


def render_corrections(rows, local):
    import fitz
    from PIL import Image, ImageDraw
    doc = fitz.open(PDF)
    source_ids = sorted(BAD_CODES | set(EMPTY_CAPTIONS) | MISJOINS)
    pictures = []
    for rid in source_ids:
        r = next(r for r in rows if r['reading_id'] == rid)
        page = doc[r['source_page'] - 1]
        y = r['primary_bbox'][1]
        clip = fitz.Rect(45, max(0, y - 18), page.rect.width - 30, min(page.rect.height, y + 115))
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=clip)
        pic = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        canvas = Image.new('RGB', (pic.width, pic.height + 23), 'white')
        ImageDraw.Draw(canvas).text((4, 4), f'{rid} manuscript page {r["source_page"]}', fill='red')
        canvas.paste(pic, (0, 23)); pictures.append(canvas)
    for i in range(0, len(pictures), 4):
        group = pictures[i:i + 4]
        sheet = Image.new('RGB', (max(p.width for p in group), sum(p.height for p in group) + 10 * len(group)), 'white')
        y = 0
        for pic in group:
            sheet.paste(pic, (0, y)); y += pic.height + 10
        path = local / 'source-checks' / f'corrections-{i // 4 + 1:02d}.png'
        path.parent.mkdir(parents=True, exist_ok=True); sheet.save(path)


def main(output=BASE, local=LOCAL, render=False):
    if any((output / name).exists() for name in ['value-derivations-v3.json', 'reading-corrections.json']):
        raise SystemExit('Source correction endpoint exists')
    local.mkdir(parents=True, exist_ok=True)
    temporary = local / 'tmp'; temporary.mkdir(exist_ok=True)
    for name in ['TMP', 'TEMP', 'MPLCONFIGDIR']:
        os.environ[name] = str(temporary)
    write(output / 'source-registration.json', {'protocol_sha256': sha(OWN / 'PROTOCOL.md'),
        'code_sha256': sha(Path(__file__)), 'inventory_sha256': sha(WORK / 'reading-inventory-v4.json'),
        'PDF_sha256': sha(PDF)})
    derivations(output)
    result = inventory(output, local, render)
    print({k: result[k] for k in ['attempts', 'transcriptions_before', 'transcriptions_after',
          'unclear_before', 'unclear_after', 'attempts_newly_flagged']})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output-dir', default=BASE.name)
    parser.add_argument('--render', action='store_true'); args = parser.parse_args()
    output = (OWN / args.output_dir).resolve(); local = (RAW / args.output_dir).resolve()
    if not output.is_relative_to(OWN) or not local.is_relative_to(RAW):
        raise SystemExit('Output outside package')
    main(output, local, args.render)
