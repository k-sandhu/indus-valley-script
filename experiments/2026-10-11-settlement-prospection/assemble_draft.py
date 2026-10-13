"""Integrate reviewed source additions and write a complete, hash-frozen draft."""
from pathlib import Path
import json, re, hashlib
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent

def new_json(path,data):
    if path.exists():raise FileExistsError(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def readable(s):
    """Normalize compressed drafting whitespace, preserving identifiers and URLs."""
    protected=[]
    def hold(m):
        protected.append(m.group());return '@@'+chr(0xE000+len(protected)-1)+'@@'
    s=re.sub(r'https?://[^\s)]+|\b[PRM]\d{2}\b|`[^`]+`',hold,s)
    s=re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])',' ',s)
    s=re.sub(r'(?<=\d),(?=\d)',', ',s)
    s=re.sub(r'(?<=\d)±(?=\d)',' ± ',s)
    s=re.sub(r'^(#{1,6})(?=\S)',r'\1 ',s,flags=re.M)
    for i,value in enumerate(protected):s=s.replace('@@'+chr(0xE000+i)+'@@',value)
    return s

def main():
    sources=json.loads((BASE/'sources-v1.json').read_text(encoding='utf-8'))
    for row in sources['sources']:
        for k in ['authors','title','access_depth','locator','observation']:
            row[k]=readable(row[k])
        if row['id']=='R10':
            row['observation']+=' Small-feature checks stopped after ten negatives per regional unit in2017;2018 imagery prefilter removed apparent ponds/dunes. These selection rules limit generalization.'
        if row['id']=='R08':
            row['observation']+=' The20 selected validation mounds were visible in the first iteration; subsequent refinements and a visually chosen threshold mean this was not an untouched regional test.'
        if row['id']=='R32':
            row['access_depth']='Primary abstract/first page and full publisher text sections2,3,5 inspected by independent Codex source auditor'
            row['locator']='Sections2,3,5; trench4km downstream of Lothal; approximate RSL and reservoir correction discussed'
        if row['id']=='R33':
            row['observation']+=' PDF p.5 associates~3000BP with2800-1800BCE Harappan centres; that chronological association is inconsistent and excluded.'
    sources['sources'].append(dict(id='R38',authors='Gregory L. Possehl',year=2002,title='Harappans and hunters: economic interaction and specialization in prehistoric India',url='https://doi.org/10.1017/CBO9780511489631.005',access_depth='Primary publisher Introduction extract read by independent Codex source auditor; full chapter not obtained',observation_id='R38-O1',locator='Forager-Traders in South and Southeast Asia, pp.62-76; Introduction citingPossehl1999AppendixA',observation='1056 Mature sites /96 excavated differs from the teaching chapter1022 /96. Online2009 date does not update this2002 chapter.',as_of='2026-10-11',raw_witness=None))
    mountains=json.loads((BASE/'research/mountain-sources.json').read_text(encoding='utf-8'))
    mapping={'M01':'R39','M02':'R40','M03':'R41','M04':'R42','M09':'R43','M10':'R44','M11':'R45','M08':'R46','M07':'R47'}
    for m in mountains['sources']:
        if m['id'] not in mapping:continue
        sid=mapping[m['id']]
        authors=m.get('authors',m.get('author'))
        if isinstance(authors,list):authors=', '.join(authors)
        witness=None
        if m.get('local_witness'):
            witness=dict(local_path=m['local_witness'],sha256=m['sha256'],bytes=m['bytes'])
        sources['sources'].append(dict(id=sid,authors=authors,year=m['year'],title=m['title'],url=m['url'],access_depth=m['access_depth'],observation_id=sid+'-O1',locator=m['locator'],observation=m['observation'],limits=m.get('limits'),as_of='2026-10-11',raw_witness=witness,mountain_source_id=m['id']))
    new_json(BASE/'sources-v2.json',sources)
    candidates=json.loads((BASE/'candidates-v1.json').read_text(encoding='utf-8'))
    for t in candidates['targets']:
        for k,v in list(t.items()):
            if isinstance(v,str):t[k]=readable(v)
        if t['id']=='P17':
            t['source_ids']=['R39','R40','R45']
            t['origin']='Documented pre-Indus burial analogue and known Nausharo sequence; additional preservation comparison'
            t['name']='Bolan outlet-Dhadar-Nausharo fan margins'
            t['target']='Target-age soils on interfan margins, buried valley surfaces and route-adjacent shelters where chronology supports the question'
        if t['id']=='P18':
            t['source_ids']+=['R41','R42','R43','R44']
            t['target']='Fan/interfluve contrasts and workshop/camp networks; Kai-Naig cave names require concordance before cavity tests'
        if t['id']=='P19':
            t['name']='Siranda-Sonmiani lagoon margins'
            # Lower Sindh analogues are sources; this bbox covers Las Bela, not Thatta.
            t['origin']='Published Las Bela shell sites; Lower Sindh supplies a regional analogue, outside this rectangle'
        if t['id']=='P16':t['source_ids']+=['R47']
    new_json(BASE/'candidates-v2.json',candidates)
    body=readable((BASE/'draft-body.md').read_text(encoding='utf-8'))
    body=body.replace('LetAbe the investigated site\'s area in hectares,fthe fraction opened,hits mean excavated archaeological thickness in metres,dthe recoverable fragment density per cubic metre, andrthe retained recovery fraction.',"Let A be the site's area in hectares, f the fraction opened, h its mean excavated archaeological thickness in metres, d the recoverable fragment density per cubic metre, and r the retained recovery fraction.")
    needle='A fan may aggrade across an occupied terrace'
    insertion="Mehrgarh provides a direct regional burial analogue: Jarrige and Lechevallier describe Neolithic mound flanks covered by Bolan alluvium and exposed by a river-cut section. This is pre-Indus evidence of the process. A2025tooth-enamel study revised the chronology of the sampled PeriodIcemetery, estimating its start at5223-4914calBCE in a preferred model that excluded two dates. It does not date the Bronze Age surfaces sought here. The known Nausharo sequence supplies a local-to-Indus comparator in the Bolan plain. [R39,R40,R45]\n\nGhazi Shah's government inventory records Amri and Indus levels beside a perennial spring and the Bhit Range. A primary report abstract explicitly identifies a2025excavation there. Its full report was unavailable, so recent activity can be confirmed without assigning new stratigraphy or dates. At Kai, the2015government inventory describes a natural cave without architecture or an authenticated Indus date. Kakar's original northern Balochistan shelter survey also lacks absolute dates. These observations favor valley and piedmont tests while leaving cave attribution open. [R41,R42,R43,R44]\n\n"
    body=body.replace(needle,readable(insertion)+needle)
    # Integrate a methodological example with its observed inconsistency in one place.
    seed="\n\nA2024date-seed study from Kech illustrates the need to audit new analytical cohorts. It classifies a selected13seed sample, while Table2 lists15sample IDs and four conventional radiocarbon ages. The relation between those cohorts and a precise calendar phase requires reconciliation. Its reported morphometric result and preservation bias motivate testing modern-date-grove analogies; they cannot estimate the region's ancient crop composition. [R47]"
    body=body.replace('They do not authenticate a proposed decipherment by themselves.','They do not authenticate a proposed decipherment by themselves.'+readable(seed))
    body=body.replace('Abe ', 'A be ').replace('V=10000Afh','V = 10000 A f h').replace('Y=Vdr','Y = V d r')
    body=body.replace('q, the expected','q, the expected').replace('Nq.','N q.').replace('pwould','p would').replace('kafterkvisits','k after k visits')
    # Embedding paths are relative to the manuscript directory, not original draft body.
    figs=BASE/'figures'
    available=[p.name for p in figs.glob('*.png')]
    insertions=[('##5. Processes that can hide or remove evidence','ganweriwala-area-definitions.png','Figure1. Ganweriwala measurements have different definitions and dates; bars are not an uncertainty interval.'),('##6. A geographically specific survey agenda','historical-map-check-yields.png','Figure2. Descriptive yields in Green2019 Table1; changing selection rules prevent population inference.'),('##8. Turning absence into a testable observation','synthetic-fragment-yields.png','Figure3. Synthetic fragment-recovery sensitivity, not an archaeological forecast.')]
    # Figure names are obtained from the worker manifest; exact additions below are adaptive.
    for heading,filename,caption in insertions:
        if filename in available:
            marker=readable(heading)
            body=body.replace(marker,f'![{caption}](../../experiments/2026-10-11-settlement-prospection/figures/{filename})\n\n'+marker)
    appendix=['##AppendixA. Proposed sampling windows','', 'Every entry is an exploratory sampling hypothesis. Comparison strata are required before interpreting candidate success. Sources identify published observations or regional mechanisms; the rectangles are authored here.','']
    for t in candidates['targets']:
        appendix += [f'###{t["id"]}. {t["name"]} (Class{t["priority_class"]})','',f'**Evidence and target.** {t["origin"]}. {t["target"]}. The proposed visibility problem is {t["missingness_mechanism"]}. [{", ".join(t["source_ids"])}]','',f'**Rival and test.** {t["competing_explanation"]}. {t["falsification_test"]}. Compare: {t["comparison_stratum"]}.','',f'**Planning extent.** West/south/east/north: {t["bbox_lonlat"]}. Bounds have0.1-degree editorial precision; access has not been assessed.','']
    appendix+=['##AppendixB. Computational observations and reproduction','',
    'The selected local register contains115entries with85accepted coordinate pairs. Its India/Pakistan/Afghanistan subset contains85entries with76pairs. The separate chronological register has86site entries and213phase labels;49labels carry a radiocarbon basis across28site entries. These are metadata labels, rather than49independent laboratory determinations. Their population was selected for earlier inscription research, so these quantities do not measure regional archaeological coverage.','',
    'The source-driven second run preserves the first run and adds Possehl’s1056historical denominator. Its49checks include rounded-percentage recovery, aggregate consistency, unit constraints, rejection of mixed-period excavation ratios, synthetic-scenario arithmetic and preservation of prior hashes. Original numerical figures are reused after hash checks. The output manifest records inputs and code/environment versions.','',
    '|Observation|Exact output|Interpretation|','|---|---|---|',
    '|Historical ratios and remote unmatched arithmetic|`run-v2/published-count-arithmetic.json`|Attributed counts; unmatched features are not validated new sites|',
    '|Green symbol/size counts|`run-v2/historical-map-checks.json` and cell/symbol CSVs|Unique integer recovery from rounded Table1 percentages|',
    '|Local metadata coverage|`run-v2/metadata-coverage.json`|Selected cohorts, with different populations|',
    '|Square-equivalent dimensions|`run-v2/square-equivalent-geometry.csv`|Geometry under an explicit square equivalence|',
    '|Constructed finds and detection examples|`run-v2/synthetic-scenarios.json` and CSVs|Synthetic inputs; no fitted site probability or find density|',
    '|Verification and provenance|`run-v2/verification.json`, `run-v2/manifest.json`|Computation and preservation checks|','',
    'Output paths above are relative to `experiments/2026-10-11-settlement-prospection/`. Reproduce into fresh directories with `python -X utf8 experiments/2026-10-11-settlement-prospection/analysis.py --help`, then the options in the package README. Reproduction does not require downloaded papers. Source-verification beyond the aggregate inputs requires the linked articles or local witnesses.','',
    'The coordinate diagram is generated from `candidates-v2.json` using `make_map.py`, and exports the same editorial bounds as GeoJSON. It makes no raster-based or bathymetric prediction.','',
    '##References and access','',
    'Bracketed IDs resolve to the sources below. Full reading depth and observation locators are in `sources-v2.json`; the mountain supplement retains its detailed source register. A current access date does not replace an article’s publication or fieldwork date.','']
    for row in sources['sources']:
        year=row['year'] if row['year'] is not None else 'undated; accessed2026'
        appendix.append(f'**[{row["id"]}]** {row["authors"]} ({year}). [{row["title"]}]({row["url"]}). Access: {row["access_depth"]}.')
        appendix.append('')
    final=body+'\n\n'+readable('\n'.join(appendix))+'\n'
    output=BASE/'review/draft-v1.md'
    if output.exists():raise FileExistsError(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(final,encoding='utf-8')
    paths=[output,BASE/'sources-v2.json',BASE/'candidates-v2.json',BASE/'run-v2/manifest.json',BASE/'run-v2/verification.json',BASE/'PROTOCOL.md']
    record={'frozen_utc':datetime.now(timezone.utc).isoformat(),'status':'complete first draft; frozen before manuscript reviews','files':[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'word_count':len(final.split())}
    new_json(BASE/'review/draft-v1-manifest.json',record)
    print(json.dumps({'sources':len(sources['sources']),'targets':len(candidates['targets']),'draft_words':len(final.split()),'draft_sha256':record['files'][0]['sha256']}))

if __name__=='__main__':main()
