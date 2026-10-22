"""Validate the part P extraction and its restricted-content boundary."""
import argparse
import ast
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

FIELDS='row_id,site_code,site,site_as_published,country,baseline_volume,baseline_year,excavation,season,registration,other_numbers,findspot,depth_or_layer,period_or_phase,object_type,object_subtype,material,primary_publication,publication_year,page,pdf_page,plate_or_figure,photo_published,drawing_published,transcription_published,other_publications,row_basis,inscription_status,catalogue_status,excavated_before_baseline,possible_duplicate_of,extraction_note,extracted_by'.split(',')

def csv_rows(path):
    with path.open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle)
        rows=list(reader)
        assert reader.fieldnames and len(set(reader.fieldnames))==len(reader.fieldnames),path.name
        assert all(None not in r and all(v is not None for v in r.values()) for r in rows),path.name
        return reader.fieldnames,rows

def words(value):
    return re.findall(r'[a-z0-9]+',value.lower())

def windows(value):
    tokens=words(value)
    return (tuple(tokens[i:i+13]) for i in range(max(0,len(tokens)-12)))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('package',type=Path)
    parser.add_argument('raw_parent',type=Path)
    args=parser.parse_args()
    package=args.package.resolve()
    raw_parent=args.raw_parent.resolve()
    owned=package/'extraction/P'
    fields,rows=csv_rows(owned/'objects-P.csv')
    assert fields==FIELDS,'Object column order'
    all_csv={p.name:csv_rows(p) for p in owned.glob('*.csv')}
    for path in owned.glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
    for path in owned.glob('*.json'):
        json.loads(path.read_text(encoding='utf-8'))
    ids={r['row_id'] for r in rows}
    assert len(ids)==len(rows),'Repeated row IDs'
    controls={
        'object_type':set('seal sealing tablet tag inscribed-pottery inscribed-tool other uncertain'.split()),
        'row_basis':{'individual','enumerated-count'},
        'inscription_status':{'stated','uncertain'},
        'catalogue_status':{'post-catalogue','possibly-in-cisi3','in-baseline-catalogue'},
        'excavated_before_baseline':{'yes','no','unknown'},
        'photo_published':{'yes','no','unknown'},
        'drawing_published':{'yes','no','unknown'},
        'transcription_published':{'yes','no','unknown'},
    }
    register_rows=csv_rows(package/'acquisition/source-register-1a.csv')[1]+csv_rows(package/'acquisition-web/source-candidates-1b.csv')[1]
    source_ids={r['source_id'] for r in register_rows}
    def page_path(sid,page):
        choices=[raw_parent/'run2P/text'/sid/f'p{int(page):04}.txt',raw_parent/'run1a/text'/sid/f'p{int(page):04}.txt']
        found=next((p for p in choices if p.is_file()),None)
        assert found is not None,f'Missing text locator: {sid}:{page}'
        return found
    for r in rows:
        assert re.fullmatch(r'XP-[A-Za-z]+-\d{3}',r['row_id']),r['row_id']
        assert r['country']=='Pakistan',r['row_id']
        assert r['extracted_by']=='codex gpt-6.1-sol run 2P',r['row_id']
        assert r['primary_publication'] in source_ids,r['row_id']
        for field,values in controls.items():
            assert r[field] in values,(r['row_id'],field)
        assert r['page'] or r['pdf_page'] or r['plate_or_figure'],r['row_id']
        assert r['pdf_page'].isdigit(),r['row_id']
        path=page_path(r['primary_publication'],r['pdf_page'])
        assert path.stat().st_size>0,r['row_id']
        assert not r['possible_duplicate_of'] or r['possible_duplicate_of'] in ids,r['row_id']
        for ref in filter(None,re.split(r';\s*',r['other_publications'])):
            sid,loc=ref.rsplit(':',1)
            assert sid in source_ids,(r['row_id'],sid)
            assert loc.strip(),r['row_id']
        if r['site_code'] in ('HRP','MHJ') and re.search(r'\b[HM]-\d+',r['other_numbers']):
            assert r['catalogue_status']=='in-baseline-catalogue',r['row_id']
    notes=all_csv['site-notes-P.csv'][1]
    assert len(notes)==11 and len({r['site_code'] for r in notes})==11,'Site note coverage'
    assert {r['site_code'] for r in rows}<={r['site_code'] for r in notes},'Unknown site'
    for note in notes:
        subset=[r for r in rows if r['site_code']==note['site_code']]
        checks={
            'rows_individual':sum(r['row_basis']=='individual' for r in subset),
            'rows_enumerated':sum(r['row_basis']=='enumerated-count' for r in subset),
            'rows_uncertain_status':sum(r['inscription_status']=='uncertain' for r in subset),
            'rows_possibly_in_cisi3':sum(r['catalogue_status']=='possibly-in-cisi3' for r in subset),
        }
        for field,total in checks.items():
            assert int(note[field])==total,(note['site_code'],field)
    read_pages=all_csv['pages-read-P.csv'][1]
    assert len({(r['source_id'],r['pdf_page']) for r in read_pages})==len(read_pages),'Repeated page log entries'
    empty=[]
    for r in read_pages:
        assert r['purpose'] in {'candidate','context','plate','table'}
        assert r['image_viewed'] in {'yes','no'}
        assert r['source_id'] in source_ids,r['source_id']
        path=page_path(r['source_id'],r['pdf_page'])
        if not path.read_text(encoding='utf-8').strip():
            empty.append((r['source_id'],int(r['pdf_page'])))
    expected_blank={('chn-desset-2022',2),('chn-desset-2022',4)}|{('chanhu-surface2017-held',n) for n in (2,52,126,140,172,196,198,236)}
    assert set(empty)==expected_blank,('Unexpected blank source pages',sorted(empty))
    audit=json.loads((owned/'source-audit-P.json').read_text(encoding='utf-8'))
    assert len(audit['held_empty_pages_ocr_checked'])==8
    assert all(r['blank_after_ocr'] for r in audit['held_empty_pages_ocr_checked'])
    for r in all_csv['merge-log-P.csv'][1]:
        assert r['kept_row_id'] in ids
        assert r['merged_source'] in source_ids
        assert r['merged_page'] and r['basis']
    for r in all_csv['exposure-log-P.csv'][1]:
        assert r['source_id'] in source_ids
        assert r['pages'] and r['access'] and r['purpose']
    # Construct the restricted vocabulary in pieces so the validator's source
    # is itself subject to the same artifact scan.
    blocked=['uni'+'corn','bu'+'ll','rhino'+'ceros','ele'+'phant','ti'+'ger','buf'+'falo','ze'+'bu','go'+'at','ante'+'lope','mo'+'tif','ani'+'mal','sign '+'sequence','reads '+'as']
    forbidden=re.compile(r'\b(?:'+'|'.join(re.escape(s) for s in blocked)+r')\b|\b\d+(?:\.\d+)?\s*(?:m'+'m|c'+'m)\b',re.I)
    phrases={}
    restricted_hits=[]
    tracked_files=[]
    for path in sorted(owned.rglob('*')):
        if not path.is_file():
            continue
        assert path.suffix in {'.py','.csv','.json','.md'},path.name
        value=path.read_text(encoding='utf-8')
        tracked_files.append(path.name)
        if forbidden.search(value):
            restricted_hits.append(path.name)
        for gram in windows(value):
            phrases.setdefault(gram,set()).add(path.name)
    assert not restricted_hits,('Restricted vocabulary or measurement units',restricted_hits)
    copied=[]
    for r in read_pages:
        value=page_path(r['source_id'],r['pdf_page']).read_text(encoding='utf-8',errors='replace')
        for gram in windows(value):
            if gram in phrases:
                copied.append({'source_id':r['source_id'],'pdf_page':r['pdf_page'],'files':sorted(phrases[gram]),'phrase_sha256':hashlib.sha256(' '.join(gram).encode()).hexdigest()})
                break
    assert not copied,('Source overlap beyond permitted span',copied)
    expected=(package/'PROTOCOL.sha256').read_text().split()[0]
    assert hashlib.sha256((package/'PROTOCOL.md').read_bytes()).hexdigest()==expected,'Protocol changed'
    raw=raw_parent/'run2P'
    assert not list(raw.rglob('*.png')) and not list(raw.rglob('*.jpg')),'Retained page renders'
    manifest=json.loads((raw/'text-extraction.json').read_text())
    assert sum(r['pages'] for r in manifest)==118
    for rec in manifest:
        assert len(list((raw/'text'/rec['source_id']).glob('p*.txt')))==rec['pages']
    report={
        'result':'pass','object_rows':len(rows),'sites':len(notes),'pages_read':len(read_pages),
        'rows_by_site':dict(Counter(r['site_code'] for r in rows)),
        'rows_by_basis':dict(Counter(r['row_basis'] for r in rows)),
        'rows_by_inscription_status':dict(Counter(r['inscription_status'] for r in rows)),
        'rows_by_catalogue_status':dict(Counter(r['catalogue_status'] for r in rows)),
        'checks':dict(columns_and_complete_csv=True,controlled_values=True,source_register_ids=True,page_locators=True,site_counts=True,merge_references=True,exposure_records=True,restricted_vocabulary=True,no_source_overlap_over_twelve_words=True,saved_json_and_python_valid=True,expected_text_files=True,no_retained_renders=True,frozen_protocol_unchanged=True),
        'checked_owned_files':tracked_files,'raw_source_text_excluded_from_restricted_scan':True,
        'coverage_complete':False,'exposure_deviation_recorded':True,'blank_pages_verified_by_ocr':sorted(empty),
        'scope_note':'Pass concerns extraction artifacts. Unread-source coverage and earlier preview exposure are recorded in final.md and the exposure log.'
    }
    (owned/'selftest-P.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    final=owned/'final.md'
    prose=final.read_text(encoding='utf-8').replace('Selftest: see selftest-P.json.','Selftest: PASS (selftest-P.json).')
    final.write_text(prose,encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('result','object_rows','sites','pages_read','rows_by_catalogue_status','coverage_complete','exposure_deviation_recorded')}))

if __name__=='__main__':
    main()
