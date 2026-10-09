"""Independent counts, source pins, packet neutrality and saved replay checks."""
from pathlib import Path
import argparse, collections, json, re
import fitz
from pdf_followup import ROOT, OWN, OUT, WORK, RAW, PDF, read, write, sha

def main(output,full_replay='pdf-replay-2026-10-09-01',caption_replay='pdf-replay-2026-10-09-02'):
    output=(OWN/output).resolve()
    if not output.is_relative_to(OWN) or output.exists():raise SystemExit('Use a new owned output path')
    full_replay=(OWN/full_replay).resolve();caption_replay=(OWN/caption_replay).resolve()
    if not all(p.is_relative_to(OWN) for p in [full_replay,caption_replay]):raise SystemExit('Replay roots must be owned')
    raw_full=RAW/full_replay.name;raw_caption=RAW/caption_replay.name
    checks=[]
    def check(name,actual,expected):
        checks.append({'check':name,'passed':actual==expected,'actual':actual,'expected':expected})
    baseline=read(OWN/'history/2026-10-09-before-pdf/baseline-files.json')
    editable={'README.md','REPORT.md','RETROSPECTIVE.md','PROTOCOL.md','sources.json','registry-entry.json',
        'claims.jsonl','claims.md','ledger-coverage.json','COMPLETION.md','FILES.json','pdf_followup.py'}
    protected=[]
    for r in baseline:
        p=ROOT/r['path']
        if p.parent==OWN and p.name in editable:continue
        check('preserved '+r['path'],sha(p) if p.exists() else None,r['sha256']);protected.append(r['path'])
    check('PDF SHA256',sha(PDF),'12e8e6b1c427dbdc995e64991d5d0a676b8d397956f28379b046a230a5065f14')
    d=fitz.open(PDF)
    extraction={'pages':len(d),'page_image_resource_entries':sum(len(p.get_images()) for p in d),
        'displayed_image_placements':sum(len(p.get_image_info()) for p in d),
        'inline_image_placements':sum(sum(i['xref']==0 for i in p.get_image_info(xrefs=True)) for p in d)}
    for k,v in {'pages':259,'page_image_resource_entries':2650,'displayed_image_placements':8402,'inline_image_placements':3544}.items():
        check(k,extraction[k],v)
    witness=read(OUT/'witness-v3.json');check('all page character multisets agree',witness['alphanumeric_multiset_equal_pages'],259)
    page_map=read(OUT/'page-map.json');pm=page_map['rows'] if isinstance(page_map,dict) else page_map
    check('page map rows',len(pm),259)
    mapping=read(OUT/'mapping-v2-frozen.json');freeze=read(OUT/'mapping-freeze-v2.json')
    check('frozen mapping SHA256',sha(OUT/'mapping-v2-frozen.json'),freeze['sha256'])
    check('mapping targets',len(mapping['rows']),96)
    check('Mayig candidate counts',dict(collections.Counter('singleton' if len(r['mayig_candidates'])==1 else 'ambiguous' if r['mayig_candidates'] else 'unmapped' for r in mapping['rows'])),{'singleton':85,'ambiguous':3,'unmapped':8})
    for key in ['wells_candidates','helsinki_candidates']:check('mapped '+key,sum(bool(r[key]) for r in mapping['rows']),88)
    packet=RAW/'second-coder-v1';manifest=read(packet/'packet-manifest-v2.json');template=read(packet/'return-template-v2.json')
    check('packet target IDs',sorted(r['sign_id'] for r in template['rows']),sorted(r['sign_id'] for r in mapping['rows']))
    check('packet omits values',manifest['contains_author_values'],False)
    check('packet omits coding',manifest['contains_first_mapping'],False)
    check('template has blank candidate fields',all(not r[k] for r in template['rows'] for k in ['mayig_candidates','wells_candidates','helsinki_candidates','component_sequence_candidates','basis']),True)
    check('v2 packet built after frozen mapping',(packet/'packet-manifest-v2.json').stat().st_mtime>(OUT/'mapping-v2-frozen.json').stat().st_mtime,True)
    check('lexical score created after v2 freeze',(OUT/'lexical-test.json').stat().st_mtime>(OUT/'mapping-v2-frozen.json').stat().st_mtime,True)
    for r in manifest['files']:check('packet hash '+r['path'],sha(packet/r['path']),r['sha256'])
    cat=read(WORK/'sign-catalogue.json');catrows=cat['rows'] if isinstance(cat,dict) else cat
    check('Table drawings',len(catrows),65);check('Table labelled assignments',len({r['table_entry'] for r in catrows}),58)
    check('all Table crops exist',all((ROOT/r['crop_path']).exists() for r in catrows),True)
    rows=read(WORK/'reading-inventory-v4.json');attempts=[r for r in rows if r['is_reading_attempt']]
    cov=read(OUT/'reading-coverage-v5.json')
    actual={'inventory_rows':len(rows),'reading_attempt_rows':len(attempts),
        'unique_primary_labels':len({r['primary_label'] for r in rows}),
        'CISI_joined_rows':sum(bool(r['joined_record_ids']) for r in rows),
        'CISI_joined_attempt_rows':sum(bool(r['joined_record_ids']) for r in attempts),
        'attempts_with_explicit_transcription':sum(bool(r.get('proposed_reading')) for r in attempts),
        'unclear_or_unattested_attempt_rows':sum(r['unclear_or_unattested_flag'] for r in attempts),
        'unjoined_attempt_rows':sum(not r['joined_record_ids'] for r in attempts)}
    for k,v in actual.items():check('inventory census '+k,v,cov[k])
    check('unjoined ID list',sorted(cov['unjoined_reading_ids']),sorted(r['reading_id'] for r in attempts if not r['joined_record_ids']))
    check('sequence length and placement agreement',all(len(r['sign_sequence_visual_ltr'])==len(r['primary_glyphs']) for r in rows),True)
    check('paper order reversals',all(r['sign_sequence_assumed_rtl']==list(reversed(r['sign_sequence_visual_ltr'])) for r in rows),True)
    claims=[json.loads(line) for line in (OWN/'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    check('unique claim IDs',len({r['id'] for r in claims}),1021)
    check('every attempted reading has a ledger record',sorted(r.get('reading_inventory_id') for r in claims if 'reading_inventory_id' in r),sorted(r['reading_id'] for r in attempts))
    check('ledger short quotations',all(not r.get('quotation') or len(r['quotation'].split())<=15 for r in claims),True)
    selection=read(WORK/'lexical-selection-v2.json');selpin=read(OUT/'lexical-selection-freeze-v2.json')
    check('lexical selection SHA256',sha(WORK/'lexical-selection-v2.json'),selpin['selection_sha256'])
    check('selected occurrences',len(selection['readings']),640)
    check('pre-Table21 selected/excluded complete',len(selection['readings'])+len(selection['excluded'])+len(selection['excluded_conflicting_variant_readings']),852)
    check('dictionary SHA256',sha(ROOT/selection['dictionary']['path']),selection['dictionary']['sha256'])
    check('P-L protocol prefix hash',sha(OUT/'protocol-snapshots/P-L-v2.md'),selection['protocol_sha256'])
    check('P-W protocol prefix hash',sha(OUT/'protocol-snapshots/P-W.md'),witness['protocol_sha256'])
    lex=read(OUT/'lexical-test.json');sens=read(OUT/'lexical-caption-sensitivity.json')
    for panel,file,expected in [('caption_extended',lex,(84,228)),('caption_extended',sens,(83,206)),('only_clear_nondictionary_origins',sens,(2,5))]:
        e=file['panels'][panel]['endpoints']['exact'];check('exact '+panel+(' sensitivity' if file is sens else ''),(e['observed_matches'],e['distinct_sequences']),expected)
    clean=sens['panels']['only_clear_nondictionary_origins']['endpoints']
    check('clean exact enumeration',(clean['exact']['assignments_at_least_observed'],clean['exact']['null_assignments'],clean['exact']['tail_fraction']),(24,120,.2))
    check('clean normalized enumeration',(clean['normalized']['assignments_at_least_observed'],clean['normalized']['tail_fraction']),(70,70/120))
    for file,panel in [(lex,'caption_extended'),(sens,'caption_extended')]:
        e=file['panels'][panel]['endpoints']['exact'];check('large-panel add-one tail',(e['assignments_at_least_observed']+1)/(e['null_assignments']+1),e['tail_fraction'])
    fields=read(OUT/'field-test.json');check('canonical field population',sum(fields['classification'].values()),2469)
    mayig=read(OUT/'mayig-fields.json');check('Mayig field population',sum(mayig['classification'].values()),100)
    validation=read(OUT/'validation-audit-v4.json')
    check('ICIT census',len(validation['cohort']),68)
    check('confirmed ICIT overlap',sum(r['has_confirmed_MH_overlap'] for r in validation['cohort']),8)
    check('questioned alias',sum(r['MH_overlap_source_qualification'].startswith('Questioned') for r in validation['cohort']),1)
    # Saved computational replays use original frozen annotation inputs.
    for filename in ['lexical-test.json','field-rules.json','field-test.json','fish-units.json','validation-audit-v3.json']:
        a=read(OUT/filename);b=read(full_replay/filename)
        if filename=='lexical-test.json':a.pop('explicit_caption_only',None);b.pop('explicit_caption_only',None)
        check('replay '+filename,a,b)
    check('replay source-explicit sensitivity',read(OUT/'lexical-caption-sensitivity.json'),read(caption_replay/'lexical-caption-sensitivity.json'))
    for filename in ['lexical-predictions.json','corpus-field-annotations.json','field-and-fish-shuffles.json']:
        check('raw replay '+filename,sha(WORK/filename),sha(raw_full/filename))
    check('raw sensitivity replay',sha(WORK/'lexical-caption-predictions.json'),sha(raw_caption/'lexical-caption-predictions.json'))
    # Avoid embedding large records in the check output: retain only failed values.
    for c in checks:
        if c['passed'] and len(str(c['actual']))>200:c['actual']='equal';c['expected']='equal'
    result={'status':'Verified computation' if all(c['passed'] for c in checks) else 'Failed',
        'checks':len(checks),'passed':sum(c['passed'] for c in checks),
        'protected_existing_files':len(protected),'editable_exclusions':sorted(editable),
        'pdf_extraction_counts':extraction,'results_remain':'Exploratory pending independent coding and source adjudication',
        'records':checks}
    write(output,result)
    print({k:v for k,v in result.items() if k not in ['records','editable_exclusions']})
    for c in checks:
        if not c['passed']:print(c['check'],str(c['actual'])[:500],str(c['expected'])[:500])
    if result['status']=='Failed':raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('pdf-checks-2026-10-09-v3.json'))
    p.add_argument('--full-replay',default='pdf-replay-2026-10-09-01');p.add_argument('--caption-replay',default='pdf-replay-2026-10-09-02')
    a=p.parse_args();main(a.output,a.full_replay,a.caption_replay)
