"""Verify final joins and preserved endpoints without rerunning the research."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, subprocess, argparse
import fitz

ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=BASE/'review/final-verification-v2.json')
    a=p.parse_args()
    output=a.output
    if output.exists():raise FileExistsError(output)
    checks=[]
    def check(name,condition,detail):
        checks.append(dict(name=name,passed=bool(condition),detail=detail))
    paper=ROOT/'papers/005-settlement-survey-gaps/manuscript.md'
    text=paper.read_text(encoding='utf-8')
    sources=read(BASE/'sources-v6.json');byid={r['id']:r for r in sources['sources']}
    regions=read(BASE/'candidates-v5.json');targets=regions['targets']
    claims=read(BASE/'claims-v3.json')
    check('counts_and_unique_ids',len(byid)==len(sources['sources'])==72 and len(targets)==21 and len({t['id'] for t in targets})==21,'72 source records and 21 distinct region IDs')
    check('final_text_matches_frozen_revision',paper.read_bytes()==(BASE/'review/revised-v5.md').read_bytes(),'Final canonical text matches the preserved post-review layout revision')
    check('layout_revision_only', (BASE/'review/revised-v4.md').read_text(encoding='utf-8').replace('figures-v3/observation-chain.png','figures-v4/observation-chain.png')==text,'Only a figure path changes between revised-v4 and v5')
    check('no_placeholders_or_duplicate_periods','@@' not in text and 'insufficient..' not in text,'No unresolved citation aliases or flagged duplicate terminal period')
    cited=set(re.findall(r'\bR\d{2}\b',text))
    check('cited_ids_known',len(cited)==69 and cited<=byid.keys(),'All 69 cited R-number records resolve')
    refs=set(re.findall(r'\*\*\[(R\d{2})\]\*\*',text))
    check('references_match_citations',refs==cited,'The bibliography contains each cited source exactly once')
    images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text)
    check('four_existing_figures',len(images)==4 and all((paper.parent/path).is_file() for path in images),'All four Markdown images exist at their actual final paths')
    obs={r['observation_id'] for r in sources['sources']}
    check('claim_observation_joins',len(claims['claims'])==32 and all(set(c['source_observations'])<=obs for c in claims['claims']),'32 claims link to valid observations or explicit proposals')
    outputs=[path for c in claims['claims'] for path in c.get('analysis_outputs',[])+c.get('protocol_files',[])]
    check('claim_output_paths',all((ROOT/path).is_file() for path in outputs),'Every exact numerical or protocol path in the final claim map exists')
    check('claim_current_registers',claims['source_register']=='sources-v6.json' and claims['region_register']=='candidates-v5.json','Claim map names current source and region registers')
    crosswalk=read(BASE/'run-v3/source-id-crosswalk.json')
    field_rows=[]
    for sid,row in crosswalk.items():
        for field,value in [('id',sid),('title',row['title']),('url',row['url']),('observation_id',row['register_observation_id'])]:
            field_rows.append(dict(source=sid,field=field,recorded=value,final=byid[sid][field],matches=value==byid[sid][field]))
    check('v6_consumed_metadata_matches',len(field_rows)==32 and all(r['matches'] for r in field_rows),'32 consumed metadata fields match final v6 and the frozen run; numerical constants are in code')
    prior={r['id']:r for r in read(BASE/'sources-v5.json')['sources']}
    check('v6_raw_witnesses_unchanged_from_audit',all(r.get('raw_witness')==prior[r['id']].get('raw_witness') for r in sources['sources']),'All raw-witness metadata is identical to the 50 hash/byte checks in the commissioned audit')
    witness_paths=[r['raw_witness']['local_path'] for r in sources['sources'] if r.get('raw_witness')]
    check('witness_count_and_existence',len(witness_paths)==50 and all((ROOT/path).is_file() for path in witness_paths),'50 local witnesses exist; their hashes were checked by the source audit')
    # Git reads LF stdin literally on Windows. NUL-delimited bytes avoid text
    # mode turning each path into a CR-suffixed, quoted filename.
    ignore=subprocess.run(['git','check-ignore','-z','--stdin'],input=('\0'.join(witness_paths)+'\0').encode('utf-8'),capture_output=True,cwd=ROOT)
    ignored={v for v in ignore.stdout.decode('utf-8').split('\0') if v}
    check('raw_witnesses_ignored',ignored==set(witness_paths),'Every acquired witness remains ignored in Git; binary NUL-delimited check uses actual paths')
    check('no_raw_witness_tracked',not subprocess.run(['git','ls-files','data/raw/2026-10-11-settlement-prospection/'],capture_output=True,text=True,cwd=ROOT).stdout.strip(),'No raw file from this acquisition directory is tracked')
    preserved=[]
    for name in ('draft-v1','revised-v2','revised-v3','revised-v4','revised-v5'):
        manifest=read(BASE/f'review/{name}-manifest.json')
        for item in manifest['files']:
            path=ROOT/item['path'];preserved.append(dict(endpoint=name,path=item['path'],matches=path.exists() and sha(path)==item['sha256']))
    check('frozen_manuscript_endpoints',all(r['matches'] for r in preserved),'All five draft/revision manifests and their declared files retain hashes')
    run_records=[]
    for name in ('run-v1','run-v2','run-v3'):
        manifest=read(BASE/f'{name}/manifest.json')
        for item in manifest['inputs']+manifest['outputs']:
            path=ROOT/item['path'];run_records.append(dict(run=name,path=item['path'],matches=path.exists() and sha(path)==item['sha256']))
    check('frozen_numerical_inputs_outputs',all(r['matches'] for r in run_records),'All recorded inputs and outputs across three numerical runs retain hashes')
    run3=read(BASE/'run-v3/manifest.json')
    check('main_code_unchanged',sha(BASE/'analysis.py')==run3['script']['sha256'],'The final layout repair did not alter the numerical script')
    arithmetic=read(BASE/'run-v3-inline-arithmetic/manifest.json')
    check('inline_endpoint_preserved',all(sha(ROOT/r['path'])==r['sha256'] for r in arithmetic['inputs']+arithmetic['outputs']+[arithmetic['code']]),'Seven-row inline code, inputs and outputs retain recorded hashes')
    for folder in ('figures-v3','figures-v4'):
        manifest=read(BASE/f'{folder}/manifest.json')
        check(folder+'_hashes',all(sha(ROOT/r['path'])==r['sha256'] for r in manifest['files']),'Original project figure file hashes match their manifest')
    map_manifest=read(BASE/'map-v5/manifest.json')
    check('current_map_input',sha(BASE/'candidates-v5.json')==map_manifest['sha256'],'Current map comes from the final region register')
    check('map_code_snapshot',sha(BASE/'map-v5/make_map-snapshot.py')==map_manifest['code_sha256'],'Map generation code was preserved with the diagram')
    feature=read(BASE/'map-v5/survey-windows.geojson')['features']
    check('geojson_region_identity',len(feature)==21 and [f['properties'] for f in feature]==targets,'GeoJSON contains the same 21 source/decision records')
    check('region_source_joins',all(set(t['source_ids'])<=byid.keys() for t in targets),'All region sources resolve')
    anchors=[]
    for t in targets:
        w,s,e,n=t['bbox_lonlat']
        for point in t.get('anchor_points',[]):
            anchors.append(dict(region=t['id'],name=point['name'],contained=w<=point['lon']<=e and s<=point['lat']<=n))
    check('four_anchor_checks',len(anchors)==4 and all(p['contained'] for p in anchors),'Published Ghazi, Kai, Kalibangan and Sutkagen-Dor points lie inside their editorial boxes')
    check('no_site_or_artifact_predictions',all(all(t[key] is None for key in ('predicted_site_count','predicted_area_ha','predicted_artifact_total')) for t in targets),'Registers supply no unsupported numerical discovery or artifact forecast')
    check('rubric_and_feasibility',all(t['information_level'] in ('I0','I1','I2') and t['preservation_evidence_level'] in ('P0','P1','P2') and t['feasibility_level']=='F0' and t.get('preservation_evidence_basis') for t in targets),'Separate levels and rationales exist; every feasibility assessment remains unverified')
    pilot=(BASE/'PILOT-DESIGN-v4.md').read_text(encoding='utf-8')
    check('pilot_inference_terms',all(v in pilot for v in ('The block is the inferential unit','no adequate blocks remains unresolved','Descriptive preservation reporting eventually includes all 24 blocks','held aside only for prediction-model evaluation')),'Current pilot retains block-level and holdout qualifications')
    check('shared_frame_rule','selected once' in regions['shared_frame_rule'] and 'P02known-margin' in regions['shared_frame_rule'],'One shared frame covers every overlap and excludes known-margin negative draws')
    for version in (1,2):
        invocation=read(BASE/f'review/claude-opus55-v{version}/invocation.json')
        result=read(BASE/f'review/claude-opus55-v{version}/cli-result.json')
        check(f'claude_v{version}_actual_success',result.get('is_error') is False and result.get('subtype')=='success' and 'claude-opus-5-5' in result.get('modelUsage',{}),'Retained actual CLI result identifies the requested canonical model and successful review')
        check(f'claude_v{version}_packet_preserved',sha(ROOT/invocation['packet_path'])==invocation['packet_sha256'],'The actual supplied review packet retains its recorded hash')
    response=(BASE/'review/response-to-reviewers.md').read_text(encoding='utf-8')
    check('second_review_findings_covered',all(f'V2-F{i}:' in response for i in range(1,13)),'Response includes every numbered second-pass finding')
    check('no_pending_export_claim','remain pending' not in response and '33 pages, 69 verified reference URLs' in response,'Response records actual final export status')
    pdf=ROOT/'output/pdf/indus_settlement_survey_gaps_2026-10-11.pdf'
    qa=read(BASE/'review/pdf-inspection.json')
    check('final_pdf_hash',sha(pdf)==qa['final_pdf']['sha256'] and sha(paper)==qa['manuscript']['sha256'],'Final PDF and manuscript match the inspected versions')
    doc=fitz.open(pdf);urls={r['uri'] for page in doc for r in page.get_links() if 'uri' in r}
    check('pdf_pages_and_reference_targets',len(doc)==33 and urls=={byid[sid]['url'] for sid in cited},'33 pages and all 69 complete reference targets are present')
    check('pdf_inspection_completed',qa['status']=='passed after visual corrections' and not qa['remaining_observed_visual_issues'] and qa['margin_issues']==0,'Actual visual record identifies corrected versions and inspected pages')
    check('local_docs_exist',all((ROOT/path).is_file() for path in ['papers/005-settlement-survey-gaps/README.md','papers/005-settlement-survey-gaps/methods.md','experiments/2026-10-11-settlement-prospection/README.md','experiments/2026-10-11-settlement-prospection/ASSET-REVIEW.md','knowledge/retrospectives/2026-10-11-settlement-prospection.md']),'Paper, package and research-memory documents exist')
    scan=read(BASE/'review/final-prose-scan-v2.json')
    check('prose_scan',not scan.get('flags'),'Owned final prose scan has no flagged stock pattern; the scan is not an authorship or scientific test')
    failed=[r for r in checks if not r['passed']]
    report=dict(completed_utc=datetime.now(timezone.utc).isoformat(),status='passed' if not failed else 'failed',check_count=len(checks),failed=failed,
        preceding_report='review/final-verification.json',verification_repair='Replace Windows newline-translated stdin with NUL-delimited binary paths; original failed report preserved',
        checks=checks,source_fields=field_rows,anchor_points=anchors,frozen_revisions=preserved,numerical_records=run_records,
        counts=dict(manuscript_words=len(text.split()),sources=72,cited_references=69,local_witnesses=50,regions=21,claims=32,pdf_pages=33),
        scope='Preservation, attribution joins, protocol consistency and actual export verification; no new fieldwork or archaeological probability validation')
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(checks=len(checks),passed=len(checks)-len(failed),failed=len(failed),failed_names=[r['name'] for r in failed])))
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
