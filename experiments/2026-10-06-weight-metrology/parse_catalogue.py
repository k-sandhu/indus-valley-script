"""Extract Ascalone 2022 catalogue; derivatives and PDF witnesses stay local.

Reuses the earlier indus_weight_audit.py entry-start/dehyphenation method
and census.py +x/mark conventions. This extends coverage to all 2058 IDs.
"""
from __future__ import annotations
import argparse
import bisect
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sys

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-weight-metrology'
for name in ('TMP', 'TEMP', 'MPLCONFIGDIR'):
    os.environ[name] = str(RAW / 'tmp')
import fitz
from PIL import Image, ImageDraw, ImageFont

SOURCE = ROOT / 'data/raw/2026-10-02-connections-and-priority/regional-west/ascalone2022.pdf'
SITES = ['Susa (Arjan)', 'Susa', 'Choga Zanbil/Dûr-Untaš', 'Djaffarabad',
         'Tell es-Sinkara/Larsa', 'Telloh/Girsu (eastern tell)', 'Telloh/Girsu',
         'Telloh region', 'Ancient Guimet collection (probably Telloh)',
         'Tell Ingharra/Kish', 'Tell el-Mukayyar/Ur', 'Jiroft valley',
         'Konar Sandal South', 'Tepe Yahya', 'Shahr-i Sokhta', 'Mindasht',
         'Rakhigarhi', 'Farmana', 'Kuntasi', 'Nageshwar', 'Nagwada',
         'Shikarpur', 'Bagasra', 'Dholavira']
SITE_RE = '|'.join(re.escape(s) for s in SITES)
START = re.compile(r'(?m)^(\d{1,4})\.?[^\S\n]+(' + SITE_RE + r')(?=[. \n-])')
SHAPE_RE = (r'(?:Fragmented |Irregular |Truncated |fragmented )?'
            r'(?:Ovoid|ovoid|Duck|duck|Frog|Shell-shaped|Fly-shaped|Pig head|Sphere|sphere|'
            r'Ellipsoid|Hand bag|Cylinder|Biconic|Biconical|Small column|Egg-shaped|'
            r'Parallelepiped|Discoid|discoid|Octagonal|Cuboid|Hemisphere|hemisphere|Cone|'
            r'Pyramid|Pyra|Irregular|Clay sphendonoid|Dome|Trapezoid|Rounded flat|Kudurru|‘Kudurru’|'
            r'KUDURRU|Bead)')
MATERIALS = ['banded chert', 'fluvial limestone', 'black stone', 'white stone', 'green stone',
             'grey stone', 'gray stone', 'red stone', 'pink stone', 'unpolished stone',
             'polished stone', 'volcanic stone', 'carnelian', 'chalcedony', 'limestone',
             'sandstone', 'softstone', 'soapstone', 'steatite', 'serpentinite', 'hornblende',
             'vesuvianite', 'hematite', 'terracotta', 'diorite', 'basalt', 'calcite',
             'alabaster', 'chlorite', 'granite', 'gabbro', 'jasper', 'marble', 'olivine',
             'silver', 'bronze', 'copper', 'bitumen', 'quartz', 'agate', 'chert', 'shell',
             'stone', 'clay', 'faience', 'lead', 'iron', 'bone']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def normalise(text):
    text = text.replace('\u00ad', '').replace('–', '-').replace('−', '-')
    text = re.sub(r'([A-Za-z])-\s*\n\s*([a-z])', r'\1\2', text)
    return re.sub(r'\s+', ' ', text).strip()

def class_of(cat, site, description):
    if site == 'Dholavira':
        if 1294 <= cat <= 1355 or 1650 <= cat <= 2015 or 2051 <= cat <= 2057:
            return 'certain', 'chapter p135 explicit ID ranges'
        if 2016 <= cat <= 2050 or cat == 2058:
            return 'excluded-related-find', 'chapter p135 explicit ID ranges'
        if 1189 <= cat <= 1199:
            return 'possible', 'chapter p135 explicit ID ranges'
        return 'potential', 'remainder of explicit p135 ranges'
    if site == 'Rakhigarhi':
        return ('potential' if 1123 <= cat <= 1126 else 'certain'), 'chapter p122 explicit ID ranges'
    if re.search(r'potential weight', description, re.I):
        return 'potential', 'entry explicit designation'
    if re.search(r'possible weight', description, re.I):
        return 'possible', 'entry explicit designation'
    return 'class-unresolved', 'no explicit entry classification encoded'

def parse():
    doc = fitz.open(SOURCE)
    pages, offsets, snippets = [], [], []
    total = 0
    for i in range(57, 181):
        txt = doc[i].get_text().replace('\u00ad', '')
        # Remove page headers without reordering columns or dropping entry lines.
        lines = [s for s in txt.splitlines() if not re.fullmatch(r'\d{1,3}', s.strip())
                 and not s.startswith(('Weight and Value', 'Enrico Ascalone',
                                       '4 Susiana and Lower Mesopotamia',
                                       '5 Southern and Eastern Iran', '6 Greater Indus Valley'))]
        txt = '\n'.join(lines) + '\n'
        offsets.append(total)
        pages.append(i + 1)
        snippets.append(txt)
        total += len(txt)
    full = ''.join(snippets)
    starts = list(START.finditer(full))
    rows = []
    for j, match in enumerate(starts):
        cat = int(match[1]); site = match[2]
        end = starts[j + 1].start() if j + 1 < len(starts) else len(full)
        literal = full[match.start():end]
        # Any following numbered section is analytical prose, not entry content.
        literal = re.split(r'(?m)^[456]\.\d+(?:\.\d+)*\.', literal, maxsplit=1)[0].strip()
        finish = match.start() + len(literal)
        entry = normalise(literal)
        head = re.match(r'\d+\.?\s+' + re.escape(site) + r'\.?\s*(?:-\s*)?', entry)
        body = entry[head.end():]
        delim = re.search(r'\s*-\s*' + SHAPE_RE, body, re.I)
        if not delim:
            prefix = re.split(r'\b(?:L|H|D|W|Th|T)\.\s*\d', body, maxsplit=1)[0]
            choices = list(re.finditer(r'\s*-\s*', prefix))
            if not choices:
                raise ValueError(f'No description separator: {cat}: {entry}')
            delim = choices[-1]
        context = body[:delim.start()].strip(' -')
        desc_start = delim.start() + len(re.match(r'\s*-\s*', body[delim.start():])[0])
        rest = body[desc_start:]
        dim = re.search(r'\b(?:L|H|D|W|Th|T)\.\s*\d', rest)
        if not dim:
            dim = re.search(r'(?<![\w.])[\d,]+(?:\.\d+)?\s*(?:\+\s*x)?\s*g\b', rest)
        if not dim:
            raise ValueError(f'No dimensions or mass start: {cat}: {entry}')
        description = rest[:dim.start()].strip(' .')
        measure_tail = rest[dim.start():]
        mass = re.search(r'(?<![\w.])([\d,]+(?:\.\d+)?)\s*(\+\s*x)?\s*g\b', measure_tail)
        mass_g = float(mass[1].replace(',', '')) if mass else None
        missing_mass = bool(mass and mass[2])
        dimensions_text = (measure_tail[:mass.start()] if mass else measure_tail.split(' - ')[0]).strip(' ,')
        dimensions = [{'axis': m[1], 'value_cm': float(m[2])} for m in
                      re.finditer(r'\b(L|H|D|W|Th|T)\.\s*(\d+(?:\.\d+)?)\s*cm', dimensions_text)]
        mat = re.search(r'(?i)\b(' + '|'.join(re.escape(m) for m in MATERIALS) + r')\.?$', description)
        material = mat[1].lower() if mat else description.split(',')[-1].strip(' .').lower()
        without_mat = description[:mat.start()].strip(' ,') if mat else ','.join(description.split(',')[:-1])
        shape_literal = without_mat.split(',')[0].strip()
        shape = re.sub(r'(?i)^fragmented\s+', '', shape_literal)
        shape = shape[0].upper() + shape[1:] if shape else shape
        condition = ','.join(without_mat.split(',')[1:]).strip()
        tail = (measure_tail[mass.end():] if mass else ' - '.join(measure_tail.split(' - ')[1:])).strip(' .-')
        period_match = re.search(r'(?:Period\s+[IVX]+(?:-[IVX]+)?|(?:Early|Mature|Late) Harappan|'
                                 r'Neo-Sumerian|Ur III|Old.Elamite|Middle Elamite|Early ICS|Proto.ICS|'
                                 r'Yahya\s+[IVX]+|Shahr-i Sokhta\s+[IVX]+)[^-]*', tail)
        period_literal = re.match(r'(?:[^-]|-(?=\d|[IVX]|C))*', tail)[0].strip() if period_match else None
        stage = re.search(r'\bPeriod\s+([IVX]+(?:-[IVX]+)?)\b', tail)
        dates = re.findall(r'\b(\d{3,4})\s*-\s*(\d{3,4}(?:/\d{3,4})?)\s*BC\b', tail)
        museums = re.findall(r'\bMus\.\s+([^;]+?)(?=\s+-\s+|$)', tail)
        museum_ids = re.findall(r'\(([^)]+)\)', ' '.join(museums))
        identifiers = re.findall(r'\b(?:DHR|AS|AO|Sb|SH|KM|RGR)[ .]*[\dA-Za-z./-]+', context + ' ' + ' '.join(museum_ids))
        area = re.search(r'\b(Middle Town|Lower Town|Castle|Bailey|Citadel|Acropolis)\b', context, re.I)
        level = re.search(r'\bLevel\s+([^,]+)', context, re.I)
        grids = re.findall(r'\b\d+(?:[xX/]\d+)+(?:[xX][A-Za-z0-9/+]+)?', context)
        marking = re.findall(r'with\s+(?:markings?|inscription)[^,.]*(?:\([^)]*\))?', description, re.I)
        unit = re.findall(r'(?:\d+(?:\.\d+)?\s+)?(?:certified\s+)?(?:minas?|shekels?|unit)[^)]*', description, re.I)
        cls, cls_basis = class_of(cat, site, description)
        shape_condition = shape_literal + ', ' + condition
        damage = bool(re.search(r'chipp|fragment|broken|incomplete|damag|restor|missing', shape_condition, re.I))
        worn = bool(re.search(r'worn|wear|abras', shape_condition, re.I))
        intact = bool(re.search(r'\b(good|perfect|excellent)\b', condition, re.I))
        region = 'Greater Indus' if cat >= 1121 else ('Southern/Eastern Iran' if cat >= 888 else 'Susiana/Lower Mesopotamia')
        source_pages = pages[bisect.bisect_right(offsets, match.start()) - 1:
                             bisect.bisect_right(offsets, finish - 1)]
        rows.append(dict(cat=cat, site=site, region=region, context_literal=context,
                         identifiers=identifiers, museum_identifiers=museum_ids, museum_literal=museums,
                         area=area[1].title() if area else None, level=level[1].strip() if level else None,
                         grids=grids, period_literal=period_literal, period_stage=stage[1] if stage else None,
                         date_ranges_bce=dates, shape_literal=shape_literal, shape=shape,
                         material=material, condition_literal=condition, dimensions_text=dimensions_text,
                         dimensions=dimensions, mass_g=mass_g, missing_mass=missing_mass,
                         damage=damage, worn=worn, intact_condition=intact,
                         preservation='damaged' if damage else 'worn' if worn else 'intact' if intact else 'unknown',
                         marks_literal=marking, entry_unit_attribution=unit,
                         balance_class=cls, class_basis=cls_basis,
                         primary_eligible=mass_g is not None and mass_g > 0 and not missing_mass and intact and not damage and not worn,
                         source_pdf_pages=source_pages, source_printed_pages=[p - 15 for p in source_pages],
                         entry_literal=literal))
    ids = [r['cat'] for r in rows]
    assert len(ids) == len(set(ids)) == 2058, (len(ids), [i for i in range(1, 2059) if i not in ids])
    assert set(ids) == set(range(1, 2059))
    return doc, rows

def render_sample(doc, rows, out):
    sample = sorted(random.Random(20261006).sample(range(1, 2059), 60))
    annotations = []
    images = []
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    for cat in sample:
        row = rows[cat - 1]
        parts = []
        for pn in row['source_pdf_pages']:
            page = doc[pn - 1]
            blocks = page.get_text('dict')['blocks']
            candidates = []
            for block in blocks:
                if block['type'] != 0:
                    continue
                txt = '\n'.join(''.join(s['text'] for s in line['spans']) for line in block['lines'])
                if re.search(r'(?m)^' + str(cat) + r'\.?\s+' + re.escape(row['site']), txt):
                    candidates.append((block['bbox'], txt))
            if candidates:
                # A block can hold several entries. Find the target's individual lines.
                target = None
                keep = []
                active = False
                for block in blocks:
                    if block['type'] != 0:
                        continue
                    for line in block['lines']:
                        txt = ''.join(s['text'] for s in line['spans'])
                        if re.match(str(cat) + r'\.?\s+' + re.escape(row['site']), txt):
                            active = True
                        elif active and (START.match(txt) or re.match(r'[456]\.\d', txt)):
                            active = False
                            break
                        if active:
                            keep.append(fitz.Rect(line['bbox']))
                    if keep and not active:
                        break
                if keep:
                    rect = keep[0]
                    for b in keep[1:]:
                        rect |= b
                    rect += (-3, -3, 3, 3)
                else:
                    rect = fitz.Rect(candidates[0][0])
            else:
                # Continuation from preceding page: preserve top quarter of both columns.
                rect = fitz.Rect(30, 55, page.rect.width - 30, 240)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.4, 2.4), clip=rect)
            im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
            if im.width > 1050:
                im = im.resize((1050, round(im.height * 1050 / im.width)))
            parts.append(im)
        width = max(1050, max(p.width for p in parts))
        height = 40 + sum(p.height for p in parts)
        tile = Image.new('RGB', (width, height), 'white')
        ImageDraw.Draw(tile).text((5, 5), f'Cat. {cat}; PDF {row["source_pdf_pages"]}; printed {row["source_printed_pages"]}', fill='black', font=font)
        y = 40
        for part in parts:
            tile.paste(part, (0, y)); y += part.height
        tile.save(out / f'cat-{cat:04}.png')
        images.append(tile)
        annotations.append({'cat': cat, 'pages': row['source_pdf_pages'], 'checked': False,
                            'errors': [], 'notes': ''})
    for start in range(0, 60, 6):
        group = images[start:start + 6]
        height = sum(im.height + 15 for im in group)
        sheet = Image.new('RGB', (1050, height), '#dddddd')
        y = 0
        for tile in group:
            sheet.paste(tile, (0, y)); y += tile.height + 15
        sheet.save(out / f'sheet-{start // 6 + 1:02}.png')
    write_json(out / 'sample-frame.json', {'seed': 20261006, 'design': 'simple random sample of 60 catalogue IDs',
                                         'sample_ids': sample, 'annotations': annotations})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw-output', default='data/raw/2026-10-06-weight-metrology/extraction-v1')
    ap.add_argument('--summary-output', default='experiments/2026-10-06-weight-metrology/extraction-v1.json')
    ap.add_argument('--render-sample', action='store_true')
    args = ap.parse_args()
    out = ROOT / args.raw_output; summary = ROOT / args.summary_output
    if out.exists() or summary.exists():
        raise FileExistsError('Choose new output paths; extraction witnesses are immutable.')
    doc, rows = parse()
    out.mkdir(parents=True)
    write_json(out / 'catalogue-rows.json', rows)
    sites = []
    for site in sorted({r['site'] for r in rows}):
        grp = [r for r in rows if r['site'] == site]
        sites.append({'site': site, 'n': len(grp), 'primary_n': sum(r['primary_eligible'] for r in grp),
                      'classes': dict(Counter(r['balance_class'] for r in grp)),
                      'preservation': dict(Counter(r['preservation'] for r in grp))})
    expected = {'Dholavira': 870, 'Bagasra': 19, 'Nagwada': 16, 'Rakhigarhi': 15, 'Farmana': 8,
                'Shikarpur': 7, 'Kuntasi': 2, 'Nageshwar': 1}
    actual = dict(Counter(r['site'] for r in rows if r['cat'] >= 1121))
    assert actual == expected, actual
    write_json(summary, {'status': 'Verified computation for ID coverage; field review pending',
                        'source_sha256': sha(SOURCE), 'parser_sha256': sha(Path(__file__)),
                        'rows_sha256': sha(out / 'catalogue-rows.json'), 'row_count': len(rows),
                        'id_min': 1, 'id_max': 2058, 'ids_complete_unique': True,
                        'indus_site_counts_match_prior_audit': True, 'site_counts': sites,
                        'material_counts': dict(Counter(r['material'] for r in rows)),
                        'shape_counts': dict(Counter(r['shape'] for r in rows)),
                        'entry_unit_attribution_n': sum(bool(r['entry_unit_attribution']) for r in rows),
                        'raw_rows_path': (out / 'catalogue-rows.json').relative_to(ROOT).as_posix()})
    if args.render_sample:
        dest = out / 'validation-renders'; dest.mkdir()
        render_sample(doc, rows, dest)
    print(json.dumps({'rows': len(rows), 'sites': sites, 'output': str(summary)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
