"""Census all explicitly marked Susa weights; publish bounded aggregates only."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re

import fitz

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
RAW = ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west'


def census():
    source = RAW / 'ascalone2022.pdf'
    doc = fitz.open(source)
    page_texts = [page.get_text() for page in doc]
    text = '\n'.join(page_texts)
    starts = list(re.finditer(r'(?m)^(\d+)\.\s+(Susa|Telloh/Girsu|Tell el-Mukayyar|Tepe Yahya)\.', text))
    rows = []
    errors = []
    for index, start in enumerate(starts):
        if start.group(2) != 'Susa':
            continue
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        raw = text[start.start():end]
        line = re.sub(r'\s+', ' ', raw)
        line = re.sub(r'([IOX])-\s*([IOX])', r'\1\2', line)
        line = re.sub(r'([a-z])-\s+([a-z])', r'\1\2', line)
        marking = re.search(r'with markings?\s*\(([^)]+)\)', line)
        if not marking:
            continue
        cat = int(start.group(1))
        graphic_parts = re.findall(r'[‘\']([IOX]+)[’\']', marking.group(1))
        masses = re.findall(r'([\d,]+(?:\.\d+)?)(\+x)?\s*g\s*-', line)
        if not masses or not graphic_parts:
            errors.append(dict(cat=cat, error='mass or graphic did not parse'))
            continue
        mass, missing = masses[0]
        mass = mass.replace(',', '')
        shape = re.search(r'-\s*(Ovoid/discoid pebble|(?:Fragmented |Irregular )?[Oo]void(?: with [^,]+)?|Duck|Hemisphere|Sphere(?: with [^,]+)?|Cone|Discoid)', line)
        if not shape:
            errors.append(dict(cat=cat, error='shape did not parse'))
            continue
        material = re.split(r'\.\s*(?:L|H|D)\.', line[marking.end():], maxsplit=1)[0].strip(' ,.')
        if not material:
            preceding = re.search(r',\s*([^,]+),\s*with markings?', line)
            material = preceding.group(1).strip() if preceding else 'material-unparsed'
        # Some entries append an object class after the mark rather than material.
        material = re.sub(r',\s*(ingot|potential weight)$', '', material)
        material = re.sub(r'^(ingot|potential weight),\s*', '', material)
        if material.startswith('unpolished '):
            material = material[len('unpolished '):]
        date = re.search(r'(\d{3,4}-\s*\d{3,4})\s*BC\b', line)
        date_bucket = date.group(1).replace(' ', '') + 'BCE' if date else 'date-unprovided'
        inventories = re.findall(r'\((Sb [^)]*)\)', line)
        pages = [i + 1 for i, page in enumerate(page_texts) if re.search(r'(?m)^' + str(cat) + r'\.\s+Susa\.', page)]
        glyph = ''.join(graphic_parts)
        pure = len(set(glyph)) == 1
        family = {'I': 'stroke', 'O': 'circle', 'X': 'cross'}.get(glyph[0]) if pure else 'mixed'
        row = dict(cat=cat, inventory=inventories[0] if inventories else None,
                   shape=shape.group(1), material=material, date_bucket=date_bucket,
                   condition_as_recorded=line[shape.end():marking.start()].strip(' ,'),
                   glyph_sequence=marking.group(1), family=family,
                   count=len(glyph) if pure else None, mass_g=mass,
                   missing_mass=bool(missing), source_pdf_pages=pages)
        rows.append(row)
    if errors:
        raise ValueError(json.dumps(errors))
    return source, rows


def main():
    out = RUN / 'marked-weight-census-v2.json'
    derivative = RAW / 'susa-marked-weight-extraction-v2.json'
    if out.exists() or derivative.exists():
        raise FileExistsError('Existing endpoint; create a new version for changed rules.')
    source, rows = census()
    derivative.write_text(json.dumps(dict(source_sha256=sha256(source.read_bytes()).hexdigest(),
                                           method='census.py catalogue-marking parser v2', objects=rows), indent=2) + '\n', encoding='utf-8')
    groups = defaultdict(list)
    excluded = {119: 'SB13514 repeats with different mass atcat129',
                120: 'SB13747 repeats for a20-minaduck atcat609',
                129: 'SB13514 repeats with different mass atcat119'}
    for row in rows:
        if not row['missing_mass'] and row['family'] != 'mixed' and row['cat'] not in excluded:
            groups[(row['shape'], row['material'], row['date_bucket'], row['family'])].append(row)
    summaries = []
    for key, group in sorted(groups.items()):
        values = [(Fraction(row['mass_g']) / row['count'], row) for row in group]
        low, low_row = min(values, key=lambda value: value[0])
        high, high_row = max(values, key=lambda value: value[0])
        tolerance = (high - low) / (high + low)
        summaries.append(dict(shape=key[0], material=key[1], date_bucket=key[2], family=key[3],
                              count=len(group), catalogue_members=[row['cat'] for row in group],
                              minimum_mass_per_mark_g=float(low), minimum_cat=low_row['cat'],
                              maximum_mass_per_mark_g=float(high), maximum_cat=high_row['cat'],
                              minimum_symmetric_relative_tolerance=float(tolerance),
                              exact_tolerance_fraction=str(tolerance),
                              explicit_shared_date_bucket=key[2] != 'date-unprovided'))
    result = dict(status='exploratory complete census under CENSUS_PROTOCOL.md rules',
                  source_sha256=sha256(source.read_bytes()).hexdigest(),
                  raw_derivative=derivative.relative_to(ROOT).as_posix(),
                  raw_derivative_sha256=sha256(derivative.read_bytes()).hexdigest(),
                  marked_entry_count=len(rows),
                  missing_mass_entry_count=sum(row['missing_mass'] for row in rows),
                  mixed_graphic_entry_count=sum(row['family'] == 'mixed' for row in rows),
                  complete_single_graphic_entry_count=sum(len(group) for group in groups.values()),
                  excluded_accession_collisions=excluded,
                  supersedes='marked-weight-census.json; corrected PDF hyphenation, preserved pebble shape, resolved material parse and excluded accession collisions',
                  eligible_graphic_counts={family: sum(row['family'] == family and not row['missing_mass'] and row['cat'] not in excluded for row in rows)
                                           for family in ['stroke', 'circle', 'cross', 'mixed']},
                  groups=summaries,
                  date_note='An explicit shared broad range is a date category; missing dates do not establish contemporaneity.')
    out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['marked_entry_count','missing_mass_entry_count','mixed_graphic_entry_count','complete_single_graphic_entry_count']}, indent=2))
    print(json.dumps([group for group in summaries if group['count'] >= 2], indent=2))


if __name__ == '__main__':
    main()
