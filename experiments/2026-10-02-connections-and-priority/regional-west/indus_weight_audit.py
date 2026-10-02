"""Bounded text audit of Greater Indus weight records in Ascalone2022."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re

import fitz

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
SOURCE = ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf'


def main():
    out = RUN / 'indus-weight-audit.json'
    if out.exists():
        raise FileExistsError('Existing frozen endpoint.')
    doc = fitz.open(SOURCE)
    text = '\n'.join(page.get_text() for page in doc[136:181])
    text = re.sub(r'([A-Za-z])-\s+([A-Za-z])', r'\1\2', text)
    starts = list(re.finditer(r'(?m)^(\d{4})\.\s+([A-Za-z][A-Za-z -]+?)\.?\s+-', text))
    starts = [match for match in starts if 1121 <= int(match.group(1)) <= 2058]
    ids = [int(match.group(1)) for match in starts]
    assert len(ids) == len(set(ids)) == 938
    assert set(ids) == set(range(1121, 2059))
    terms = r'\b(mark(?:ing)?s?|inscri\w*|incis\w*|dots?|engraved|graffi\w*)\b'
    flagged = []
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        entry = re.split(r'(?m)^\d\.\d+(?:\.\d+)*\.', text[match.start():end])[0]
        found = re.findall(terms, entry, re.IGNORECASE)
        if found:
            flagged.append(dict(cat=int(match.group(1)), site=match.group(2), terms=found))
    data = dict(status='bounded text search plus selected visual inspection; negative catalogue-description result',
                source_sha256=sha256(SOURCE.read_bytes()).hexdigest(),
                source_pdf_pages=[137,181], catalogue_ids=[1121,2058],
                total_records=938, site_counts=dict(Counter(match.group(2) for match in starts)),
                search_regex=terms, flagged_records=flagged,
                inspected_dholavira_plates=[dict(plate=56,pdf_page=286),dict(plate=58,pdf_page=288),
                                            dict(plate=60,pdf_page=290),dict(plate=61,pdf_page=291),
                                            dict(plate=62,pdf_page=292)],
                visual_result='No newly readable Indus glyph or ancient number joined to a mass was identified in selected compressed plates. Modern collection ink and natural banding appear in several photographs; minute marks remain unresolved.',
                appendix_result='Tavernier pp179-183 describes29inscribedweights with cuneiform/Elamite readings; no Indus-script reading is supplied.',
                useful_context_field='Dholavira chapterpp135-136 reports870objects;505have archaeological context;435classed as certain balance weights.',
                limitations=['Catalogue descriptions do not document every object face.',
                             'Selected plate review does not cover every photograph.',
                             'Original Dholavira photos and sign/weight assemblage joins remain to acquire.'],
                next_observation='Join DHR collection number plus trench/grid/level to excavation seal and sealing records, then inspect all faces of a candidate marked weight.')
    out.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(total_records=data['total_records'], site_counts=data['site_counts'], flagged_records=flagged), indent=2))


if __name__ == '__main__':
    main()
