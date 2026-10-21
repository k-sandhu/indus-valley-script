"""Assemble local collation, register crosswalk and count-only audit.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/assemble.py --raw data/raw/2026-10-21-head-direction-corpora
Run records.py for each manual input first. Source wording is read only from local files.
"""
import argparse
import collections
import hashlib
import json
import random
import subprocess
from pathlib import Path

CODE = Path(__file__).resolve().parent
FIELDS = ('source entry sub_entry page_printed page_pdf plates object_text material dimensions object_kind device legend_as_printed legend_lines_as_printed line_division_evidence translation_as_printed doubtful restored illegible_part date_as_printed language_note findspot_as_printed depth_as_printed impressions duplicates cross_references museum uncertain_fields transcriber').split()


def readlines(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]


def writejson(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def writelines(path, values):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in values), encoding='utf-8')


def expand(spec):
    result = []
    for part in filter(None, spec.split(',')):
        ends = [int(x) for x in part.split('-')]
        result.extend(range(ends[0], ends[-1] + 1))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', type=Path, required=True)
    args = ap.parse_args()
    raw = args.raw
    scratch = raw / 'codex-a1'
    td = raw / 'transcriptions'
    patches = json.loads((scratch / 'corrections.json').read_text(encoding='utf-8'))
    appendix = json.loads((CODE / 'bloch-appendix-locators.json').read_text(encoding='utf-8'))
    scans = {}
    for p in (CODE.parent.parent / 'acquisition').glob('asi-ar-*.json'):
        if not (p.name.startswith('asi-ar-1903-04-') or p.name.startswith('asi-ar-1913-14-')):
            continue
        r = json.loads(p.read_text(encoding='utf-8'))
        if r.get('pdf_pages'):
            name = Path(r['local_path']).parent.name.split('-')[-2]
            scans[name] = r['pdf_pages']
    sources = {}
    errors = []
    for source in ['asi-ar-1903-04', 'asi-ar-1913-14']:
        path = td / (source + '.jsonl')
        rows = readlines(path)
        for patch in patches:
            if patch['source'] != source:
                continue
            found = [r for r in rows if r['entry'] == patch.get('match_entry', patch['entry']) and r['sub_entry'] == patch.get('sub_entry')]
            if len(found) != 1:
                raise ValueError(('patch target', patch['entry'], len(found)))
            found[0].update(patch['set'])
        for r in rows:
            if source.endswith('1903-04'):
                r['unit_as_printed'] = 'numbered variety; clay impressions, sometimes grouped'
                r.setdefault('legend_nagari_as_printed', None)
                for plate, figures in appendix['plates'].items():
                    for fig, entries in figures.items():
                        if int(r['entry']) in entries and not any(x.get('plate') == plate and x.get('figure') == fig for x in r['plates']):
                            r['plates'].append({'plate':plate,'figure':fig,'basis':'appendix, printed p. 120; PDF 219'})
            else:
                r['register_number'] = r['entry']
            if r.get('device') and len(r['device'].split()) > 15:
                r['device_full_local'] = r['device']
                r['device'] = ' '.join(r['device'].split()[:15])
        writelines(path, rows)
        sources[source] = rows
    pages = readlines(scratch / 'register-pages.jsonl')
    register = []
    register_all = {}
    for p in pages:
        seal_ids = expand(p['seals'])
        skips = set(expand(p.get('edition_skips','')))
        for n in expand(p['register_range']):
            register_all[n] = {'page_pdf':p['page_pdf'], 'page_printed':p['page_printed'], 'class':'edition skips' if n in skips else ('seal' if n in seal_ids else 'other find')}
        for n in seal_ids:
            r = {f:None for f in FIELDS}
            r.update(source='asi-ar-1913-14', scan='dli35545', entry=str(n), register_number=str(n), sub_entry=None,
                     page_pdf=p['page_pdf'], page_printed=p['page_printed'],
                     class_as_printed='Seal(s)', object_text='See special List of Seals.',
                     plates=[], duplicates=[], cross_references=['special List of Seals'], uncertain_fields=[],
                     doubtful=False, restored=False, illegible_part=False,
                     line_division_evidence='none given',
                     transcriber='Codex (GPT-6), Codex Windows workspace harness; page-image')
            override = p.get('overrides',{}).get(str(n))
            if override:
                r.update(override)
                r['cross_references'] = []
            r['square_as_printed'] = r['findspot_as_printed']
            matching = [x for x in sources['asi-ar-1913-14'] if x['entry'] == str(n) and x['sub_entry'] is None]
            if matching:
                r['special_list_page_pdf'] = matching[0]['page_pdf']
                r['special_list_findspot_as_printed'] = matching[0]['findspot_as_printed']
                r['special_list_depth_as_printed'] = matching[0]['depth_as_printed']
            else:
                r['uncertain_fields'].append({'field':'entry','reason':'Register classifies this number as seal, but special list has no matching entry.'})
            register.append(r)
    writelines(td / 'asi-ar-1913-14.register.jsonl', register)
    sources['asi-ar-1913-14.register'] = register
    gaps = []
    list_ids = {int(r['entry']) for r in sources['asi-ar-1913-14']}
    for n in range(1, max(list_ids)+1):
        if n not in list_ids:
            witness = register_all[n]
            gaps.append({'entry':n, **witness})
    audit = {'bloch_missing_numbers':[n for n in range(1,141) if str(n) not in {r['entry'] for r in sources['asi-ar-1903-04']}],
             'spooner_absent_from_special_list':gaps,
             'register_seals_absent_from_list': sorted({int(r['entry']) for r in register} - list_ids),
             'list_entries_absent_from_register_seal_classes': sorted(list_ids - {int(r['entry']) for r in register}),
             'register_edition_skips':sorted(n for n,r in register_all.items() if r['class']=='edition skips')}
    writejson(CODE / 'numbering-audit.json', audit)
    counts = {'count_basis':'entries counts unique numbered parents; feature counts collapse parent and sub-entries per number. Row counts are also given. Register features are only those actually repeated in register.', 'sources':{}}
    for source, rows in sources.items():
        by_id = collections.defaultdict(list)
        for r in rows:
            by_id[r['entry']].append(r)
            missing = set(FIELDS) - set(r)
            if missing:
                errors.append({'source':source,'entry':r['entry'],'missing':sorted(missing)})
            if r['scan'] not in scans or not 1 <= r['page_pdf'] <= scans[r['scan']]:
                errors.append({'source':source,'entry':r['entry'],'invalid_page':r['page_pdf']})
            year = '1903-04' if source.startswith('asi-ar-1903-04') else '1913-14'
            for page in [r['page_pdf']] + r.get('page_pdf_continued',[]):
                png = raw / ('pages-asi-' + year) / (r['scan'] + '-p' + str(page).zfill(4) + '.png')
                if not png.exists():
                    errors.append({'missing_render':str(png)})
        def count(*fields):
            return sum(any(any(bool(r.get(f)) for f in fields) for r in rr) for rr in by_id.values())
        uncertain = collections.Counter()
        for rr in by_id.values():
            uncertain.update({u['field'] for r in rr for u in r['uncertain_fields']})
        counts['sources'][source] = {'entries':len(by_id),'sub_entries':sum(r['sub_entry'] is not None for r in rows),'jsonl_rows':len(rows),
            'with_legend':count('legend_as_printed','legend_components_as_printed'),
            'with_stated_line_division':sum(any(r['legend_lines_as_printed'] is not None or (r['line_division_evidence'] not in (None,'none given') and any(w in r['line_division_evidence'].lower() for w in ('line','above','below'))) for r in rr) for rr in by_id.values()),
            'with_translation':count('translation_as_printed'),'with_findspot':count('findspot_as_printed'),
            'with_depth':count('depth_as_printed'),'with_impression_count':count('impressions'),
            'with_plate_reference':count('plates'),'doubtful':count('doubtful'),'restored':count('restored'),
            'partly_illegible':count('illegible_part'),'uncertain_fields':dict(sorted(uncertain.items())),
            'pages_with_records':len({(r['scan'],r['page_pdf']) for r in rows}),
            'entries_legend_corrected_from_first_ocr_draft':None,
            'ocr_count_note':'First-pass correction events were not journalled. A separate reproducible comparison with OCR pages records differences; it is not a historical count.'}
    counts['validation'] = {'jsonl_parses':True,'required_fields_present':not errors,'page_references_and_renders_valid':not errors,'errors':errors}
    writejson(CODE / 'transcription-counts.json', counts)
    sample_file = scratch / 'reread-selection.json'
    if not sample_file.exists():
        candidates = sorted([r for source,rows in sources.items() if not source.endswith('.register') for r in rows if r['sub_entry'] is None],key=lambda r:(r['source'],int(r['entry'])))
        selected = random.Random('a1-check').sample(candidates,10)
        writejson(sample_file, [{k:r[k] for k in ('source','entry','page_pdf','scan','page_printed')} for r in selected])
        writelines(scratch / 'reread-first-pass.jsonl', selected)
    print(json.dumps({'counts':{k:(v['entries'],v['sub_entries']) for k,v in counts['sources'].items()},'validation_errors':errors,'numbering_conflicts':{k:v for k,v in audit.items() if k != 'spooner_absent_from_special_list'}}))


if __name__ == '__main__':
    main()
