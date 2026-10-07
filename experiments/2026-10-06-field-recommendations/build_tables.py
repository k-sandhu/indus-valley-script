"""Export manual source coding; --check validates without writing.

Mechanical validation does not verify the truth of the manual attribution.
Historical snapshots and reviewer files are immutable encoding exceptions.
"""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07'
TEXT_SUFFIXES = {'.py', '.md', '.json', '.csv', '.txt'}
MOJIBAKE = ('\u00e2\u20ac', '\u00c3\u00a9', '\u00c3\u00a8', '\u00c2\u00a0', '\u00ef\u00bf\u00bd')

def encoding_check(path):
    data = path.read_bytes()
    if data.startswith(b'\xef\xbb\xbf'):
        raise ValueError(f'UTF-8 BOM: {path}')
    text = data.decode('utf-8', errors='strict')
    if '\ufffd' in text:
        raise ValueError(f'Replacement character: {path}')
    if any(marker in text for marker in MOJIBAKE):
        raise ValueError(f'Suspected mojibake: {path}')
    if re.search(r'\w\?\w', text):
        raise ValueError(f'Suspected lost character between word characters: {path}')
    return text

def dumped(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'

def csv_text(rows):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, ensure_ascii=False, separators=(',', ':'))
                         if isinstance(value, (list, dict)) else value
                         for key, value in row.items()})
    return out.getvalue()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Check deterministic outputs without writing.')
    args = parser.parse_args()
    encoding_check(HERE/'curation.py')
    coded = runpy.run_path(str(HERE/'curation.py'))
    acquisition = json.loads((RAW/'acquisition-log.json').read_text(encoding='utf-8'))
    witnesses = {row['path']:row for row in acquisition if row.get('path')}
    sources = coded['sources']
    by_id = {s['id']:s for s in sources}
    assert len(by_id) == len(sources), 'Duplicate source ID'
    for s in sources:
        assert s['opened'] and s['read_scope'] and s['url'] and s['title']
        path = ROOT / s['witness_path']
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert s['witness_path'] in witnesses, f'Witness absent from acquisition log: {s["id"]}'
        assert actual == witnesses[s['witness_path']]['sha256'], f'Witness changed: {s["id"]}'
        s['sha256'] = actual
        s['witness_bytes'] = path.stat().st_size
        s['acquisition_log'] = str((RAW/'acquisition-log.json').relative_to(ROOT)).replace('\\','/')
    rows = coded['recommendations']
    assert len({r['id'] for r in rows}) == len(rows), 'Duplicate recommendation ID'
    links = set()
    for r in rows:
        assert r['status'] == 'Exploratory'
        assert r['source_locator'] and r['recommendation'] and r['required_data_or_collaboration']
        s = by_id[r['source_id']]
        r.update(source_title=s['title'], authors=s['authors'], year=s['year'], venue=s['venue'],
                 url=s['url'], source_access=s['access'], witness_path=s['witness_path'], witness_sha256=s['sha256'])
        for c in r['comparisons']:
            assert c['source_id'] in by_id and c['locator'] and c['statement'] and c['relation']
        links.update(r['repository_links'])
    for p in coded['positions']:
        assert p['source_id'] in by_id and p['locator'] and p['status'] == 'Exploratory'
        links.update(p['repository_links'])
    for rel in links:
        assert (ROOT/rel).is_file(), f'Broken repository link: {rel}'
    corrections = [dict(old_source_id=old, replacement_source_id=new, correction=note)
                   for old,new,note in coded['corrections']]
    assert len(corrections) == 14
    missing = list(csv.DictReader((HERE/'review/missing-recommendations.csv').open(encoding='utf-8')))
    dispositions = [
        (['F39'], ['P01','P02','P07'], 'Oligopoly/origin and material-count gap are positions. Explicit model-test request admitted.'),
        (['F09','F10'], [], 'Read abstract45, including per-site artefact counts and heterogeneous-set prescription.'),
        (['F05','F06','F07','F08'], [], 'Read printed viii-x. Explicit future priorities admitted; monolithic-corpus description is background.'),
        (['F19','F20','F21'], [], 'Read Yadav96-98 and Mahadevan-group section8; original reader image6 visually checked.'),
        (['F23','F24','F25','F26'], [], 'Read all four locators. Conditional proposal on44 and its nonlinguistic premise are explicit.'),
        (['F22','F27','F28','F31','F32','F33','F34','F35'], [], 'Opened published replies and counterreply; exact scopes are in comparisons.'),
        (['F16','F17'], [], 'Read PNAS Discussion13690.'),
        (['F11','F12','F13','F14','F15'], [], 'Read2020text223,230-231 and visually read2006scan printed21.'),
        (['F38'], [], 'Read2018chapter524-525; external evidence requested on525.'),
        (['F46'], [], 'Actual institutional project aim replaces false2013record.'),
        (['F56'], [], 'Read both abstracts. Konasukawa prescription admitted; Gokhale critique retained in coverage, no study instruction inferred.'),
        (['F40'], [], 'Ameri371 requests material-class studies. Table19.1 and external-seal presentation scope are background.'),
        ([], ['P06'], 'Read2021abstract and2025programme.2025listing has no abstract; no transfer of2021text to2025.'),
        (['F49','F50','F51'], [], 'Read institutional author page through proxy; book unopened.'),
        (['F47','F48'], [], 'Read printed35,43,47 and record distinct PDF pages.'),
        (['F57','F58','F59'], [], 'Read Green2016 author extracts; method excluded and full2016paper unread. Additional2021review read on182-185; explicit agendas admitted.'),
    ]
    assert len(missing) == len(dispositions)
    missing_out = [dict(review_item=i,researcher=r['researcher'],recommendation_ids=d[0],
                        position_ids=d[1],disposition=d[2])
                   for i,(r,d) in enumerate(zip(missing,dispositions),1)]
    summary = dict(status='Exploratory', recommendations=len(rows), source_records=len(sources),
                   sources_used_for_recommendations=len({r['source_id'] for r in rows}),
                   themes=dict(sorted(Counter(r['theme'] for r in rows).items())),
                   source_access=dict(sorted(Counter(s['access'] for s in sources).items())),
                   lecture_rows=sum(r['source_id']=='FRENEZ-TALK-2026' for r in rows),
                   positions=len(coded['positions']), named_coverage_gaps=sum('gap' in x['disposition'] for x in coded['coverage']),
                   source_corrections=len(corrections), missing_review_items=len(missing_out),
                   comparison_entries=sum(len(r['comparisons']) for r in rows), repository_links=len(links),
                   semantic_validation='Manual coding; reviewer must check passages. No automatic attribution verification.')
    outputs = {'sources.json':dumped(sources), 'recommendations.json':dumped(rows),
               'recommendations.csv':csv_text(rows), 'positions.json':dumped(coded['positions']),
               'coverage.json':dumped(coded['coverage']), 'source-corrections.json':dumped(corrections),
               'missing-item-disposition.json':dumped(missing_out), 'summary.json':dumped(summary)}
    for name, content in outputs.items():
        path = HERE/name
        if args.check:
            assert path.read_bytes() == content.encode('utf-8'), f'Export differs: {name}'
        else:
            path.write_bytes(content.encode('utf-8'))
    checked = []
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(HERE)
        if relative.parts[0] in {'first-pass','review'} or relative.name == 'REVIEW.md':
            continue
        encoding_check(path)
        checked.append(str(relative).replace('\\','/'))
    snap = json.loads((HERE/'first-pass-manifest.json').read_text(encoding='utf-8'))
    for row in snap:
        assert hashlib.sha256((HERE/row['path']).read_bytes()).hexdigest() == row['sha256']
    for rel in ['REVIEW.md','review/row-audit.csv','review/source-checks.csv','review/missing-recommendations.csv']:
        assert (HERE/rel).read_bytes() == (HERE/'first-pass'/rel).read_bytes(), f'Reviewer witness changed: {rel}'
    result = dict(status='Verified computation',recommendations=len(rows),source_records=len(sources),
                  witness_hashes_checked=len(sources),repository_links_checked=len(links),
                  encoding_files_checked=checked,historical_files_hash_checked=len(snap),
                  reviewer_files_byte_equal=4,deterministic_export_files=len(outputs),
                  encoding_exclusions=['first-pass/**','review/**','REVIEW.md'],
                  note='Mechanical checks only; attribution remains Exploratory.')
    if not args.check:
        (HERE/'validation.json').write_bytes(dumped(result).encode('utf-8'))
    print(dumped(summary))
    print('Checks passed; catalogue attribution remains Exploratory.')

if __name__ == '__main__':
    main()
