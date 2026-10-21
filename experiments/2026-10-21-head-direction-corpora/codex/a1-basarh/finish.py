"""Write source inventory, local reading notes, re-read audit and coverage counts.

Command: python -I experiments/2026-10-21-head-direction-corpora/codex/a1-basarh/finish.py --raw data/raw/2026-10-21-head-direction-corpora
The source context JSON, OCR drafts and transcriptions remain in the local raw tree.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path

CODE = Path(__file__).resolve().parent


def readrows(p):
    return [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]


def write(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def nums(spec):
    result = set()
    for part in spec.split(','):
        ends = [int(x) for x in part.split('-')]
        result.update(range(ends[0],ends[-1]+1))
    return sorted(result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw', type=Path, required=True)
    a = ap.parse_args()
    scratch = a.raw / 'codex-a1'
    td = a.raw / 'transcriptions'
    counts = json.loads((CODE / 'transcription-counts.json').read_text(encoding='utf-8'))
    read = json.loads((CODE / 'pages-read.json').read_text(encoding='utf-8'))
    allrows = {}
    for source in counts['sources']:
        rows = readrows(td / (source + '.jsonl'))
        allrows[source] = rows
        if not source.endswith('.register'):
            counts['sources'][source]['pages_read'] = sum(len(nums(spec)) for scan,spec in read[source].items())
            counts['sources'][source]['pages_read_by_scan'] = {scan:nums(spec) for scan,spec in read[source].items()}
        else:
            counts['sources'][source]['pages_read'] = 32
        not_preserved = set()
        legend_rows = 0
        for r in rows:
            legend = r.get('legend_as_printed')
            if not legend:
                continue
            legend_rows += 1
            draft = []
            year = '1903' if source.startswith('asi-ar-1903-04') else '1913'
            for page in [r['page_pdf']] + r.get('page_pdf_continued',[]):
                path = scratch / ('ocr'+year) / (r['scan']+'-p'+str(page).zfill(4)+'.txt')
                if path.exists():
                    draft.append(path.read_text(encoding='utf-8'))
            # Only whitespace is folded; punctuation, case and diacritics remain distinct.
            if ' '.join(legend.split()) not in ' '.join('\n'.join(draft).split()):
                not_preserved.add(r['entry'])
        counts['sources'][source]['ocr_postcollation_audit'] = {'legend_rows_compared':legend_rows,'entries_with_legend_not_preserved_verbatim_in_ocr':len(not_preserved),'criterion':'Whitespace folded; case, punctuation and diacritics compared exactly. This is not a count of first-pass correction events.'}
    first = {(r['source'],r['entry']):r for r in readrows(scratch/'reread-first-pass.jsonl')}
    second = readrows(scratch/'reread-second-pass.jsonl')
    additions = {(r['source'],r['entry']):r for r in json.loads((scratch/'reread-additions.json').read_text(encoding='utf-8'))}
    selection = {(r['source'],r['entry']):r for r in json.loads((scratch/'reread-selection.json').read_text(encoding='utf-8'))}
    for r in second:
        key = (r['source'],r['entry'])
        r.update(additions[key])
        r.update(selection[key])
        r['sub_entry'] = None
        r['transcriber'] = 'Codex (GPT-6), Codex Windows workspace harness; page-image'
    (scratch/'reread-second-pass.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in second),encoding='utf-8')
    differences = []
    fields = set()
    for r in second:
        old = first[(r['source'],r['entry'])]
        for key,value in r.items():
            if key in ('source','entry','plate_pairs'):
                continue
            fields.add(key)
            if old.get(key) != value:
                differences.append({'source':r['source'],'entry':r['entry'],'field':key,'first':old.get(key),'second':value})
        pairs = sorted((x['plate'],x['figure']) for x in old['plates'])
        if pairs != sorted(tuple(x) for x in r['plate_pairs']):
            differences.append({'source':r['source'],'entry':r['entry'],'field':'plates','first':pairs,'second':r['plate_pairs']})
    write(scratch/'reread-differences.json',differences)
    counts['reread'] = {'seed':'a1-check','sample_size':10,'selection_unit':'unique numbered parent across both lists, sorted by source and numeric entry; Python random.Random(seed).sample',
        'fields_compared':sorted(fields|{'plates'}),'differences_total':len(differences),'differences_by_field':dict(collections.Counter(d['field'] for d in differences)),
        'disposition':'Translation punctuation and omitted explicit impression count corrected. Quoted duplicate shorthand and cross-page duplicate links retained from first pass after review. Object/device differences record independent condensation of the same printed description; first-pass wording retained.',
        'sample_identifiers':[{'source':r['source'],'entry':r['entry']} for r in second],
        'limitation':'Same agent second image reading; not independent-contributor verification.'}
    acquisitions = []
    for p in sorted((CODE.parent.parent/'acquisition').glob('asi-ar-*.json')):
        if p.name.startswith(('asi-ar-1903-04-','asi-ar-1913-14-')):
            r = json.loads(p.read_text(encoding='utf-8'))
            r['record_path'] = p.as_posix()
            acquisitions.append(r)
    counts['acquisition'] = {'records':len(acquisitions),'fixed_files_checked':sum(r.get('expected_sha1') is not None for r in acquisitions),'sha1_matches_expected':sum(r.get('sha1_matches_expected') is True for r in acquisitions),'bytes_match_expected':sum(r.get('bytes_match_expected') is True for r in acquisitions),'mismatches':[r['record_path'] for r in acquisitions if r.get('sha1_matches_expected') is False or r.get('bytes_match_expected') is False],'metadata_witnesses':sum(r['local_path'].endswith('metadata.json') for r in acquisitions)}
    write(CODE/'transcription-counts.json',counts)
    header = '# Sources\n\nWe acquired six pinned source files and four metadata witnesses with `fetch_source.py`. Every pinned byte count and SHA-1 matched. Each file occupies its own acquisition directory. Metadata witnesses have observed bytes and SHA-256, without an expected digest. All rights records use `rights-unverified`.\n\n'
    header += '| Source | Item | File | Bytes | SHA-256 | PDF pages | Printed pages read | PDF pages read | Rights |\n|---|---|---|---:|---|---:|---|---|---|\n'
    for r in acquisitions:
        path = Path(r['local_path'])
        item = r['url'].split('/')[4] if '/download/' in r['url'] else r['url'].split('/')[-1]
        scan = path.parent.name.split('-')[-2]
        pdfpages = r.get('pdf_pages','n/a')
        printed = '101–120; postscript 121; title; plates XL–XLII' if r['source_id'].endswith('1903-04') else '124–185; title; errata; plates XLVI–L'
        actual = read.get(r['source_id'],{}).get(scan,'n/a') if r.get('pdf_pages') else 'n/a'
        if not r.get('pdf_pages'):
            printed = 'OCR draft / metadata witness'
        elif scan == 'ignca21816':
            printed = 'title; 102, 104, 105, 107; plates XL–XLII; blanks'
        elif scan == 'ministry09311':
            printed = 'title; errata; 105, 114; initial legibility checks'
        header += f"| {r['source_id']} | {item} | {path.name} | {r['bytes']} | {r['sha256']} | {pdfpages} | {printed} | {actual} | rights-unverified |\n"
    header += '\nThe larger 1903–04 scan supplies the list. The smaller 1913–14 scan supplies the list and register because its text is sharper. The larger 1903–04 scan omits Plate XLII at the expected position; the IGNCA scan supplies it. `pages-read.json` records displayed pages, including locator checks. Earlier extra views of the larger Spooner scan were not individually journalled, so its displayed-page count is conservative.\n\n'
    header += 'Both 1903–04 title pages print *Archæological Survey of India. Annual Report 1903–04*, Calcutta: Office of the Superintendent of Government Printing, India, 1906 (dli207529 PDF 6; ignca21816 PDF 8). The larger scan’s verso names the Government of India Central Printing Office, 8, Hastings Street (PDF 7). Both 1913–14 title pages print *Archæological Survey of India. Annual Report 1913–14*, edited by Sir John Marshall, Calcutta: Superintendent Government Printing, India, 1917 (ministry09311 PDF 3; dli35545 PDF 2).\n\n'
    for year in (1906,1917):
        header += f'Rights note for {year}: “Government of India publication of {year}; public domain by age in India and the United States (our assessment); Internet Archive item states no licence”.\n\n'
    (CODE/'SOURCES.md').write_text(header,encoding='utf-8')
    contexts = json.loads((scratch/'source-context.json').read_text(encoding='utf-8'))
    for source,context in contexts.items():
        rows = allrows[source]
        text = context + '\n\nUncertain fields recorded during transcription:\n\n'
        for r in rows:
            for u in r['uncertain_fields']:
                text += f"- No. {r['entry']}{r['sub_entry'] or ''}, {u['field']}: {u['reason']} (printed p. {r['page_printed']}, {r['scan']} PDF {r['page_pdf']}).\n"
        text += '\nEdition reading flags are retained on each JSONL record. A null legend means the entry supplies no continuous reading; duplicate-only references are not expanded from another entry. A quoted shorthand may remain in object_text or remarks_as_printed. Source typography is transcribed in Unicode NFC; inch and foot marks use double and single primes. Descriptive prose is condensed; device fields contain at most fifteen words.\n'
        (td/(source+'.notes.md')).write_text(text,encoding='utf-8')
    print(json.dumps({'reread_differences':counts['reread']['differences_by_field'],'acquisition':counts['acquisition'],'sources':{k:{x:v[x] for x in ('entries','sub_entries','with_legend','pages_read')} for k,v in counts['sources'].items()}}))


if __name__ == '__main__':
    main()
