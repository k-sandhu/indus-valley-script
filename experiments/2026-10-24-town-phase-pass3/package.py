from pathlib import Path
import json, hashlib

P = Path(__file__).resolve().parent
R = Path('D:/projects/indus_valley_script/data/raw/2026-10-24-town-phase-pass3')
def dump(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf8')
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    acquisitions = json.loads((R/'acquisitions-requests.json').read_text())
    sources = []
    bounds = {'nomination':[0,73,409,410,411,412,413,418,468,469], 'maps':[0,1]}
    for a in acquisitions:
        if a.get('status') != 200:
            continue
        s = {k:v for k,v in a.items() if k != 'hits'}
        s.update(title='Dholavira: A Harappan City, Nomination Dossier, Volume I' if a['id']=='nomination' else 'Dholavira: a Harappan City - maps of the inscribed property', authors='Archaeological Survey of India', year=2020, edition='2020 nomination; map sheet dated JAN.2020', rights='rights-unverified; local-only', logical_path='data/raw/2026-10-24-town-phase-pass3/'+Path(a['physical_path']).name, pages_read_zero_based=bounds[a['id']])
        sources.append(s)
    dump(P/'source-manifest.json', {'sources':sources, 'failed_routes':'data/raw/2026-10-24-town-phase-pass3/acquisitions.json and acquisitions-requests.json'})
    rows = [
      dict(id='TP3-1',source='nomination',pdf_index=409,printed_page=386,relation='2000-01 numbered-stone documentation and resetting, east gate to northern corner',kind='modern restoration',dependency='same institutional chronology as pass2',missing='stone identifiers and target southeast footprint'),
      dict(id='TP3-2',source='nomination',pdf_index=410,printed_page=387,relation='Figs4.2–4.4: Lower Town and eastern reservoir 2000-01; StageVII pillar reconstruction after2001 earthquake',kind='modern restoration photographs',dependency='ASI nomination publication',missing='2005-06 southeast Castle photographic register'),
      dict(id='TP3-3',source='nomination',pdf_index=411,printed_page=388,relation='2005-06 southern reservoir and southeast citadel dismantling before resetting',kind='repeat of prior intervention',dependency='same episode already admitted in pass2 management plan',missing='numbered stones, original face coordinates and phase key'),
      dict(id='TP3-4',source='maps',pdf_index=0,printed_page=None,relation='January2020 site plan labels southern reservoirs SR1–5 spatially; legend repeats SR4 for fifth',kind='institutional location plan',dependency='ASI nomination map',missing='restoration footprint, wall phase key, survey datum/control')]
    dump(R/'relations.json', rows)
    queries=['site.asi.nic.in Lothal volume I pdf plates','site.asi.nic.in "2005-06" "Dholavira"','"DHR93" "TL" Dholavira','"Indian Archaeology 2005-2006" pdf','site.whc.unesco.org Dholavira nomination maps 1645','"Lothal" "Volume I" "ignca.gov.in/Asi_data"','"2005-2006.pdf" archaeology','"Lothal" "XXXVIII" pdf','"DHR 93/TL/8"']
    dump(R/'search-log.json',dict(queries=queries,first_response_complete=False,first_response_leads=['IGNCA40421 Ancient India18&19','Google Books YtVtAAAAMAAJ bibliographic record','Scribd286-page IVC text candidate'],saved_responses=['search2.json','search3.json','open1.json'],screening='case-insensitive PDF text-layer keyword screening only; selected page reads listed in source manifest'))
    dump(P/'aggregate.json',dict(protocol_sha256=sha(P/'PROTOCOL.md'),queries=9,primary_sources_acquired=2,acquisition_targets=3,new_pages_read=12,observation_records=4,new_excavation_observations=0,construction_sample_joins=0,new_determinations=0,bearings=0,bench='inapplicable: metadata-only source work'))
    dump(P/'exposure-manifest.json',dict(pages=bounds,visual_checks=[dict(source='maps',pdf_index=0,content='site plan'),dict(source='nomination',pdf_index=410,content='three conservation photograph pairs and stylized inscription footer')],incidental_inscription_exposure=True,transcriptions=0,sequence_tests=0,freshness_claim=False,scope='Text extraction of selected pages; whole-document keyword screening; query snippets mentioning seals. Rendered but unviewed images do not count as visual inspection.'))
    files=[]
    for f in sorted(R.rglob('*')):
        if f.is_file():
            files.append(dict(physical_path=str(f),logical_path='data/raw/2026-10-24-town-phase-pass3/'+f.relative_to(R).as_posix(),bytes=f.stat().st_size,sha256=sha(f),rights='rights-unverified; local-only; project helper code own-work',transformation='requests acquisition or PyMuPDF text/render derivative; tool-response preservation; parent source hashes in source-manifest.json'))
    dump(P/'local-file-manifest.json',dict(files=files))
    record=dict(id='TOWN-PHASE-PASS3-2026-10-24',theme='Dholavira restoration documentation and Lothal original-source gaps',status='completed-bounded-source-review',status_class='source-review',area='data',question='Can institutional nomination drawings and conservation records close the Q-1032 wall-to-phase and sample joins?',outcome='Two primary source copies and twelve pages inspected; plan locator and earlier conservation photographs recovered. Zero new excavation observations or construction-sample joins. Target southeast stone register, Lothal original plate and TL contexts remain missing.',challenge='Annual review403; nomination too large for text service; target records absent from inspected pages.',remedy='Direct requests acquisition, local extraction, explicit dependent-source accounting and precise open fields.',evidence=[str(P.relative_to(Path.cwd())/n).replace('\\','/') for n in ['PROTOCOL.md','REPORT.md','RETROSPECTIVE.md','DATA-UPDATE.md','aggregate.json','source-manifest.json','validation.json','exposure-manifest.json']],retry_when='Actual numbered-stone restoration register or phase-keyed footprint, original Lothal plate/sample section or original TL collection documentation becomes available.',package='experiments/2026-10-24-town-phase-pass3',authors=[dict(model='gpt-6.1-sol',harness='Codex collaboration')],verification_tier='submitted')
    reg=Path('knowledge/registry/attempts/TOWN-PHASE-PASS3-2026-10-24.json');dump(reg,record)
    changed=[str(f.relative_to(Path.cwd())).replace('\\','/') for f in P.iterdir() if f.is_file()]+[str(reg).replace('\\','/')]
    changed += ['experiments/2026-10-24-town-phase-pass3/'+x for x in ['changed-paths.json','validation.json','prose-review.json','kb-check.json']]
    dump(P/'changed-paths.json',dict(changed_paths=sorted(set(changed)),raw_directory=str(R)))
    errors=[]
    for f in files:
        path=Path(f['physical_path'])
        if sha(path)!=f['sha256']:errors.append(str(path))
    assert sum(len(s['pages_read_zero_based']) for s in sources)==12
    for row in rows:
        assert row['pdf_index'] in bounds[row['source']]
    dump(P/'validation.json',dict(passed=not errors,errors=errors,source_hashes_checked=2,local_files_checked=len(files),page_bounds_checked=12,observation_bindings_checked=4,protocol_sha256=sha(P/'PROTOCOL.md'),tier='author validation; no separate specialist review'))
if __name__=='__main__':
    main()
