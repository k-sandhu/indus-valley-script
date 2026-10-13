"""Assemble a reviewable revision, preserving prior manuscripts and registers."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
import argparse

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent

def sentence(text):
    return text.strip().rstrip('.')+'.'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-register',type=Path,default=BASE/'sources-v3.json')
    parser.add_argument('--candidate-register',type=Path,default=BASE/'candidates-v3.json')
    parser.add_argument('--map-directory',type=Path,default=BASE/'map-v3')
    parser.add_argument('--output',type=Path,default=BASE/'review/revised-v2.md')
    parser.add_argument('--pilot-output',type=Path,default=BASE/'PILOT-DESIGN-v2.md')
    parser.add_argument('--skip-pilot',action='store_true',help='Preserve an unchanged existing pilot while assembling a layout-only revision')
    a=parser.parse_args()
    sources=json.loads(a.source_register.read_text(encoding='utf-8'))
    aliases=json.loads((BASE/'source-aliases-v3.json').read_text(encoding='utf-8'))
    candidates=json.loads(a.candidate_register.read_text(encoding='utf-8'))
    body=(BASE/'revised-body-v2.md').read_text(encoding='utf-8')
    body=re.sub(r'@@([A-Z_]+)@@',lambda m:aliases[m[1]],body)
    assert '@@' not in body
    appendix=['## Appendix A. Regions, comparisons and decisions','',
      'All bounds below are editorial west/south/east/north rectangles in longitude/latitude degrees. They overlap and provide regional indexing, with partial anchor containment checks rather than terrain validation. Evidence classes are A: documented archaeology or feature follow-up; B: preservation comparison; C: chronology or attribution first. The shared effort, blinding, one-frame overlap and adequate-observation rules are in Sections 2.3 and 6. Each region requires a locally calibrated effort limit and sample allocation before outcomes are inspected; only P08/P09 has the illustrative 24-block workload.','',
      'Information and preservation-evidence levels follow the rubric in Section 2.3. Their assessor is the AI-assisted research and drafting process, with no expert-rating exercise. P2 is common because many regions have a known archaeological anchor, sometimes from another period; it does not rank target-parcel survival or Indus affiliation. All feasibility levels are F0 because project data, partners, parcel access and intervention arrangements have not been verified. Source project dates identify documented prior activity; a complete spatial effort inventory remains to be acquired. Candidate and comparison samples need size, visibility and prior-effort strata.','',
      'Selected published anchor coordinates were checked against their editorial rectangles. Decimal precision below transcribes a source record and does not measure location accuracy. These four checks do not validate the other named places or the intervening landforms.','',
      '| Region and anchor | Latitude N | Longitude E | Source |',
      '|---|---|---|---|']
    for t in candidates['targets']:
        for anchor in t.get('anchor_points',[]):
            appendix.append(f'| {t["id"]}: {anchor["name"]} | {anchor["lat"]} | {anchor["lon"]} | [{anchor["source_id"]}] |')
    appendix.append('')
    for t in candidates['targets']:
        info=t['information_value'].removeprefix('High: ').removeprefix('Medium: ')
        levels=''
        if 'information_level' in t:
            levels=f' ({t["information_level"]}; {t["preservation_evidence_level"]}; {t["feasibility_level"]})'
        component=' The piedmont question is I2; the cave-attribution component is I0.' if t.get('component_information_levels') else ''
        appendix.extend([f'### {t["id"]}. {t["name"]} (evidence class {t["evidence_class"]})','',
         f'**Question and rival.** {sentence(t["target"])} Mechanism: {sentence(t["missingness_mechanism"])} Rival: {sentence(t["competing_explanation"])} [{", ".join(t["source_ids"])}]','',
         f'**Unit and comparison.** {sentence(t["sampling_unit"])} Comparison: {sentence(t["minimum_comparison"])}','',
         f'**Decision.** {sentence(t["demotion_rule"])}','',
         f'**Assessment{levels}.** Information: {sentence(info)} Preservation: {sentence(t.get("preservation_evidence_basis",t["preservation_assessment"]))}{component} Next task: {sentence(t["next_action"])}','',
         f'**Regional index.** {t["bbox_lonlat"]}.',''])
    appendix.extend(['## Appendix B. Reproduction and exact output links','',
     'Paths in this appendix are relative to the dated experiment directory, experiments/2026-10-11-settlement-prospection/. The third numerical endpoint retains the published source IDs alongside an R-number crosswalk. Its inputs and code hashes are in run-v3/manifest.json. The source register used for that numerical run was the preserved sources-v2.json; final narrative and geographic corrections are in '+a.source_register.name+' and '+a.candidate_register.name+'. A separate comparison records that all 32 consumed source fields remain identical across v2/v4/v5 and the recorded run metadata; final package verification extends that check to v6. Numerical inputs are curated constants in the preserved script, not values parsed from changing source prose. No archaeological total was fitted.','',
     '| Manuscript observation | Exact output | Unit and scope |',
     '|---|---|---|',
     '| Historical excavation ratios and Cholistan arithmetic | run-v3/published-count-arithmetic.json | Attributed historical populations and remote clusters |',
     '| Repeat-survey comparisons, Table 2 | run-v3/resurvey-descriptives.json and .csv | Study-specific periods, selection and units retained |',
     '| Green Table 1 reconstruction | run-v3/historical-map-checks.json and cell/symbol/size CSVs | Unique integer recovery from published rounded percentages |',
     '| Area equivalents | run-v3/square-equivalent-geometry.csv | Square geometry, not measured site shapes |',
     '| Conditional repeated detection | run-v3/synthetic-repeat-detection.csv | Constructed independent-visit assumptions |',
     '| Source identity crosswalk | run-v3/source-id-crosswalk.json | Legacy source labels joined to R-numbered observations |',
     '| Computation and preservation | run-v3/verification.json and manifest.json | Implementation checks, not archaeological validation |',
     '| Inline unit/date conversions | run-v3-inline-arithmetic/arithmetic.json | Seven formulas with source IDs, inputs and chronology limits |',
     '| Final consumed-source comparison | review/final-register-numeric-comparison.json | 32 metadata fields and preserved numerical hashes |',
     '| Regions and diagram | '+a.candidate_register.name+'; '+a.map_directory.name+'/survey-windows.geojson | Editorial rectangles and source/decision fields |','',
     'Inline calculations use 39 feet × 0.3048 = 11.8872 metres; 160 × 130 / 10,000 = 2.08 hectares; and 100 × 60 / 10,000 = 0.6 hectares. Calendar-BP endpoints are converted as age minus 1950, yielding the Lothal ranges in Table 1. The rough ka orientations use 1000 × ka minus 1950 and retain the reference-year limitation in Section 2.2. The inline-arithmetic endpoint records 17 implementation checks and a refusal to overwrite its own output.','',
     'A fresh numerical replay uses Python with the declared requirements and new output paths:','',
     '`python -X utf8 experiments/2026-10-11-settlement-prospection/analysis.py --output experiments/2026-10-11-settlement-prospection/replay-new --figures experiments/2026-10-11-settlement-prospection/replay-figures-new --source-register experiments/2026-10-11-settlement-prospection/sources-v2.json`','',
     'This command supplies no amendment note, so it asserts no retrospective amendment history. Existing endpoints must remain unchanged. Reproduction of numerical aggregates does not require downloaded papers. Checking their source attribution requires the linked articles or local witnesses. Original plot rendering can vary by library/font version; manifests distinguish data and file hashes. The package README gives figure-reuse and map commands.','',
     'Supplementary outputs preserve the earlier inscription-oriented metadata audit, its record-level alias comparison and synthetic find-yield examples. They are outside the settlement-coverage inference in this paper. The 64 implementation checks in the third run include rounding, scope guards, arithmetic and provenance; counting them is bookkeeping, not evidential weight. A separate commissioned AI-model review checked selected calculations.','',
     '## References','',
     'Bracketed R-numbers resolve to the records below. The complete source register includes 72 records, including access and correction notes not cited in the paper. It records exact observation locators, reading depth, limits and local witness hashes. Titles and publication dates are preserved; an access date is not an excavation date. Some entries are institutional inventories or project reports rather than journal papers.',''])
    combined=body+'\n\n'+'\n'.join(appendix)
    cited=set(re.findall(r'\bR\d{2}\b',combined))
    known={r['id'] for r in sources['sources']}
    assert cited<=known,(cited-known)
    references=[]
    for row in sorted(sources['sources'],key=lambda r:int(r['id'][1:])):
        if row['id'] not in cited:
            continue
        year=row['year'] if row['year'] is not None else 'undated; accessed 2026'
        references.extend([f'**[{row["id"]}]** {row["authors"]} ({year}). [{row["title"]}]({row["url"]}).',''])
    final=combined+'\n\n'+'\n'.join(references)+'\n'
    output=a.output.resolve()
    if output.exists():
        # Resume only the metadata writes after the recorded pilot-heading error.
        # Verify text equality after platform newline normalization; never rewrite it.
        assert output.read_text(encoding='utf-8')==final,'Existing revision differs; use a new version.'
    else:
        output.write_text(final,encoding='utf-8')
    # Pilot revision is copied from the reviewed body rather than rewriting v1.
    if not a.skip_pilot:
        pilot=re.split(r'### 8\.3\.? A paired-landform pilot for P08/P09\n\n',body,maxsplit=1)[1].split('\n## 9.',1)[0]
        target=a.pilot_output.resolve()
        if target.exists():
            raise FileExistsError(target)
        target.write_text('# Proposed buried-surface pilot, revised after review\n\nUnrun proposal, 11 October 2026. This workload supplies no power calculation, partner agreement or field authorization.\n\n'+pilot+'\n',encoding='utf-8')
    paths=[output,a.source_register.resolve(),a.candidate_register.resolve(),a.map_directory.resolve()/'manifest.json',BASE/'run-v3/manifest.json',BASE/'run-v3-inline-arithmetic/manifest.json']
    if 'figures-v4/observation-chain.png' in final:
        paths.append(BASE/'figures-v4/manifest.json')
    manifest=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),status='complete revised draft for targeted review before final version',
       files=[dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in paths],
       manuscript_words=len(final.split()),source_records=len(known),cited_records=len(cited),regions=len(candidates['targets']),
       evidence_classes=dict(Counter(t['evidence_class'] for t in candidates['targets'])))
    manifest_path=output.with_name(output.stem+'-manifest.json')
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:manifest[k] for k in ['manuscript_words','source_records','cited_records','regions','evidence_classes']}))

if __name__=='__main__':
    main()
