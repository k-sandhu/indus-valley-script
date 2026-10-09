"""Summarize the registered three-mapping results and update editable prose/ledger."""
from pathlib import Path
import collections, copy, json, re
from pdf_followup import OWN, RAW, WORK, read, write
from second_coder_sensitivity import BASE, LOCAL

LABELS=['first','second','agreed_only']

def summarize():
    if (BASE/'comparison.json').exists():raise SystemExit('Summary endpoint exists')
    results={}
    for label in LABELS:
        d={name:read(BASE/label/(name+'.json')) for name in ['field-test','fish-units','mayig-fields','lexical-test',
            'lexical-caption-sensitivity','reading-joins','selection-coverage','reading-consistency']}
        results[label]=d
    findings={
        'fish_clustering_all_three':all(d['fish-units']['adjacency']['add_one_tail']<=.05 for d in results.values()),
        'canonical_clean_excess_all_three':all(d['field-test']['canonical_clean_shuffle']['add_one_tail']<=.05 for d in results.values()),
        'full_lexical_conditional_excess_all_three':all(d['lexical-test']['panels']['caption_extended']['endpoints']['exact']['tail_fraction']<=.05 for d in results.values()),
        'caption_lexical_conditional_excess_all_three':all(d['lexical-caption-sensitivity']['panels']['caption_extended']['endpoints']['exact']['tail_fraction']<=.05 for d in results.values()),
        'clear_origin_no_excess_all_three':all(d['lexical-caption-sensitivity']['panels']['only_clear_nondictionary_origins']['endpoints']['exact']['tail_fraction']>.05 for d in results.values()),
        'alias_joins_identical':len({d['reading-joins']['alias_joined_attempt_rows'] for d in results.values()})==1,
        'historical_held_out_entries_identified':0,
        'interpretation':'Conditional structural and lexical findings survive three mappings. Field counts, graphic coverage and lexical panel size vary. Two AI coding rounds without specialist review.'}
    write(BASE/'comparison.json',{'status':'Exploratory','results':results,'conclusions':findings})
    return results,findings

def readable_agreement():
    a=read(BASE/'agreement.json');refs=read(BASE/'reference-check.json')
    lines=['# Agreement of two AI coding rounds','',
        'The first reader was Codex. The independent Claude Sonnet 5.5 round used two fresh sessions for separate halves of the 96-target packet. Returns and part hashes are preserved. Both parts report packet-only reading, with file/folder names outside their assignments visible. No specialist has reviewed the drawings. Counts are target-level; repeated drawings and allographs are included.','',
        'Overlap includes exact singleton matches. Disjoint counts require two nonempty sets. Missing sets are separate. Kappa uses only paired singleton rows and their empirical marginals; it excludes ambiguous and missing rows. Helsinki identity is a chart cell, with code/rank metadata checked separately.','',
        '| Domain | Targets | Exact singleton | Equal nonempty sets | Overlap | Disjoint | Missing | Singleton kappa (paired n) |',
        '|---|---:|---:|---:|---:|---:|---:|---|']
    for domain,r in a['domains'].items():
        lines.append(f'| {domain} | {r["targets"]} | {r["exact_singleton_matches"]} | {r["equal_nonempty_sets"]} | {r["candidate_set_overlap"]} | {r["disjoint_nonempty_sets"]} | {r["missing_one_or_both_sets"]} | {r["kappa_paired_singletons"]:.4f} ({r["paired_singleton_rows"]}) |')
    lines+=['','Helsinki kappa has only eight paired singleton rows. Many chart differences reflect a narrower set of same-class allographs in the second return. The exact target/candidate list is in [agreement.json](agreement.json).','']
    for grouping,groups in a['strata'].items():
        lines += ['## '+grouping.replace('_',' '),'',
            '| Stratum | Domain | Targets | Exact singleton | Overlap | Disjoint | Missing | Kappa (paired n) |',
            '|---|---|---:|---:|---:|---:|---:|---|']
        for stratum,domains in groups.items():
            for domain,r in domains.items():
                k=r['kappa_paired_singletons'];ks='undefined' if k is None else f'{k:.4f}'
                lines.append(f'| {stratum} | {domain} | {r["targets"]} | {r["exact_singleton_matches"]} | {r["candidate_set_overlap"]} | {r["disjoint_nonempty_sets"]} | {r["missing_one_or_both_sets"]} | {ks} ({r["paired_singleton_rows"]}) |')
        lines.append('')
    lines+=['## Reference and instruction checks','',
        'All returned Helsinki class/code payloads match chart v2.1. The `class` field means its printed `rank`; both coding rounds used that meaning. The 96-row v2 template is the operative template. The original instructions remain preserved, with a new local clarification.','',
        'There are 658 ordinary direct Mayig/Parpola-code joins: 624 have Mayig number equal to chart rank and 34 have Mayig number two higher. P373 and P374 list codes 804/805 absent from this chart. The special damage marker P000/V599 joins chart rank 396 and supplies the sole numeric-offset exception. Code 369 prints class 43 but is absent from direct Mayig code lists; Mayig P043 instead lists code 288. Explicit cell/code joins therefore remain necessary. [Reference check](reference-check.json).','',
        'There are 38 targets with a candidate-set or component difference, including 24 with different Mayig sets. [DISAGREEMENTS.md](DISAGREEMENTS.md) gives both codings and short source-image notes. [target-attribution.json](target-attribution.json) identifies outcome-sensitive cases without adjudication.']
    (BASE/'AGREEMENT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    lines=['# Candidate disagreements','',
        'All 38 targets with different candidate sets or component sequences are listed. Notes summarize the second reader’s visible features and were checked against the two local source contact sheets. They select no preferred coding. Full confidence, component sequences and basis strings are preserved in agreement.json.','',
        '| Target | Type | First Mayig / Wells / cells | Second Mayig / Wells / cells | Visual note |','|---|---|---|---|---|']
    def coding(r):
        return ','.join(r['mayig_candidates'])+' / '+','.join(r['wells_candidates'])+' / '+','.join(h['cell_id'] for h in r['helsinki_candidates'])
    for r in a['disagreements']:
        note=' '.join(r['visual_note'].split()[:42])
        lines.append('| '+' | '.join([r['sign_id'],r['target_type'],coding(r['first_coding']),coding(r['second_coding']),note]).replace('\n',' ')+' |')
    lines+=['','B020 has an additional second-reader component decomposition despite the same main class. B074/B075 have the same component sequences, but first-reader Mayig sets were empty; strict Mayig overlap therefore omits them from agreed-only. B078 differs between one class and a two-component decomposition. None is resolved here.']
    (BASE/'DISAGREEMENTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

def section(results):
    lines=['## Independent coding and three-mapping sensitivity','',
        'The second coding covers all 96 targets in two fresh Claude Sonnet 5.5 sessions. Mayig overlap is **78/96**, with **72 exact singleton matches**, **ten disjoint nonempty sets** and **eight first-reader missing sets**. Singleton kappa is **0.9217** on 78 paired rows. Wells has 42 exact singleton matches, overlap 78 and kappa 0.9109 on 46 paired rows. Helsinki has six exact singleton matches, overlap 78 and kappa 0.7193 on eight paired rows. Confidence and target-type splits are in [AGREEMENT.md](two-coder-2026-10-09-v1/AGREEMENT.md). These are **two AI coding rounds without specialist review**.','',
        'Table-drawing Mayig overlap is 51/65, caption-form overlap 16/17 and field/anchor overlap 11/14. Both-high confidence rows agree exactly on 48/49; B043 is the disjoint case. Confidence remains uncalibrated. Thirty-eight targets differ in some candidate set or component sequence, including 24 differing Mayig sets. [All disagreements](two-coder-2026-10-09-v1/DISAGREEMENTS.md).','',
        'The first and second mappings preserve their candidate sets. Agreed-only retains the 78 targets with a nonempty Mayig intersection, using candidate intersections; 18 targets drop. Compounds B074/B075 have agreeing component sequences but no first-reader Mayig set and therefore drop under the registered strict rule. Component agreement is reported separately. Candidate ambiguity and conflicting oval roles remain indeterminate. [Frozen operational mappings](two-coder-2026-10-09-v1/mapping-freeze.json).','',
        '| Exploratory result | First mapping | Second mapping | Agreed-only |','|---|---:|---:|---:|']
    def fmt(fn):return '| '+' | '.join(fn(results[l]) for l in LABELS)+' |'
    entries=[('Lipi clean / conflict / indeterminate',lambda d:'/'.join(str(d['field-test']['classification'][k]) for k in ['clean','conflict','indeterminate'])),
        ('Mean shuffled clean count',lambda d:f'{d["field-test"]["canonical_clean_shuffle"]["null_mean"]:.2f}'),
        ('Fish adjacency / shuffle mean',lambda d:f'{d["fish-units"]["adjacency"]["observed"]} / {d["fish-units"]["adjacency"]["null_mean"]:.2f}'),
        ('Mayig clean / conflict / indeterminate',lambda d:'/'.join(str(d['mayig-fields']['classification'][k]) for k in ['clean','conflict','indeterminate'])),
        ('Full lexical retained occurrences',lambda d:str(d['selection-coverage']['retained_occurrences'])),
        ('Full lexical exact hits / types',lambda d:lexratio(d,'lexical-test','caption_extended')),
        ('Explicit-caption occurrences',lambda d:str(d['lexical-caption-sensitivity']['panels']['caption_extended']['eligible_reading_occurrences'])),
        ('Explicit-caption exact hits / types',lambda d:lexratio(d,'lexical-caption-sensitivity','caption_extended')),
        ('Clear-origin caption exact hits / types',lambda d:lexratio(d,'lexical-caption-sensitivity','only_clear_nondictionary_origins')),
        ('Clear-origin exact tail',lambda d:str(d['lexical-caption-sensitivity']['panels']['only_clear_nondictionary_origins']['endpoints']['exact']['tail_fraction'])),
        ('Clear-origin normalized tail',lambda d:f'{d["lexical-caption-sensitivity"]["panels"]["only_clear_nondictionary_origins"]["endpoints"]["normalized"]["tail_fraction"]:.4f}'),
        ('Alias-joined attempts / object families',lambda d:f'{d["reading-joins"]["alias_joined_attempt_rows"]} / {d["reading-joins"]["alias_joined_object_families"]}'),
        ('Fully reference-supported figures / joined figures',lambda d:f'{d["reading-joins"]["fully_reference_supported_attempts"]} / {d["reading-joins"]["fully_reference_supported_joined_attempts"]}'),
        ('Literal exact consistency / checked targets',lambda d:f'{d["reading-consistency"]["exact_literal_consistent"]} / {d["reading-consistency"]["caption_targets_checked"]}')]
    for name,fn in entries:lines.append('| '+name+' '+fmt(fn))
    lines+=['',
        'Every canonical-clean and fish-adjacency tail is 0.0005. Their shuffle ranges are 395–445, 340–387 and 356–406 for clean counts, and 44–66, 44–66 and 43–66 for fish adjacency. The qualitative ordering/clustering result survives all mappings; its field totals remain mapping-sensitive. All numbers are in [comparison.json](two-coder-2026-10-09-v1/comparison.json), `results`, with separate per-mapping endpoint files.','',
        'The first and second lexical scores are equal because they test the manuscript’s fixed glyph IDs and proposed values. External reference classes change neither. Agreed-only is a coverage restriction: it removes 310/640 occurrences, leaving 330 full-selection and 303 explicit-caption occurrences. Full exact matching changes from 84/228 to 53/123, with null mean 19.42; explicit-caption matching changes from 83/206 to 52/108, mean 19.18. All broad-panel exact tails remain 0.0005. Table-only and normalized endpoints remain available in each mapping’s lexical files. Their conditional excess and unresolved construction dependence survive the mapping comparison.','',
        'The clear-origin caption subset changes from 2/5 exact (tail .20) to 0/1 (tail 1.0); normalized tails are .5833 and .50. B017 and B052 account for its dropped multi-role examples. Thus the absence of detectable clear-origin excess survives all mappings, with a smaller evidence base under agreed-only. Historical held-out membership remains zero, so no held-out score is computed. Alias joins remain 713 because explicit object identifiers are independent of graphic coding. Fully reference-supported figures measure candidate/component coverage and leave transcription accuracy untested.','',
        'For later adjudication, replacing B069 alone changes 153 classifications; replacing B078 alone changes 62. Omitting B074 or B075 separately changes 32 or 21 and lowers fish adjacency to 138 or 139. These post-outcome diagnostics identify sensitivity without selecting a coding. The main threshold conclusions survive; numerical field totals and lexical coverage require specialist adjudication. [Attribution](two-coder-2026-10-09-v1/target-attribution.json).','',
        'The reference check confirms `class` equals printed chart rank, all returned cell payloads are correct and ordinary direct-code joins follow the reported offsets. P000/V599 is a damage-marker exception; P373/P374’s codes are absent from the chart. Code 369 has no direct Mayig-code join, while Mayig P043 has code 288. Explicit chart/code joins remain the basis. Original packet instructions are preserved, with a new dated local clarification. [Reference check](two-coder-2026-10-09-v1/reference-check.json).','']
    return '\n'.join(lines)

def lexratio(d,file,panel):
    x=d[file]['panels'][panel]['endpoints']['exact'];return f'{x["observed_matches"]}/{x["distinct_sequences"]}'

def ledger(change_name='ledger-changes.json'):
    history=OWN/'history/2026-10-09-before-second-coder'
    original=[json.loads(l) for l in (history/'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    rows=copy.deepcopy(original);a=read(BASE/'agreement.json')
    differing={r['sign_id'] for r in a['disagreements']}
    keep={r['sign_id'] for r in read(BASE/'mapping-agreed_only.json')['rows']}
    packet_targets={r['sign_id'] for r in read(BASE/'mapping-first.json')['rows']}
    byreading={r['reading_id']:r for r in read(WORK/'reading-inventory-v4.json')}
    changes=[]
    for r in rows:
        targets=set()
        if r.get('sign_catalogue_id'):targets.add(r['sign_catalogue_id'])
        targets.update((r.get('graphic_identity') or {}).get('catalogue_ids',[]))
        if r.get('reading_inventory_id'):targets.update(byreading[r['reading_inventory_id']]['sign_sequence_visual_ltr'])
        uncatalogued=sorted(targets-packet_targets);targets&=packet_targets
        affected=sorted(targets&differing);tests=[]
        if affected:tests.append('S2-A')
        if (r.get('graphic_identity') or {}).get('catalogue_ids'):tests+=['S2-A','S2-L']
        if r.get('reading_inventory_id'):tests+=['S2-L','S2-J']
        if 'P-F' in r['test_ids']:tests.append('S2-F')
        if not tests:continue
        before=copy.deepcopy(r)
        if (r.get('graphic_identity') or {}).get('catalogue_ids'):
            r['graphic_identity']['status']='Exploratory; two AI coding rounds without specialist review; first mapping retained beside sensitivity'
            r['graphic_identity']['second_coding_evidence']='two-coder-2026-10-09-v1/agreement.json; mapping-second.json; mapping-agreed_only.json'
            r['offered_evidence']='Table 18 in the supplied PDF provides the drawing and printed value list. The three-mapping lexical comparison retains its proposed assignment and tests agreed-only coverage separately.'
        r['test_ids']=list(dict.fromkeys(r['test_ids']+tests))
        r['second_coding_evaluation']={'status':'Exploratory','coding':'Two AI coding rounds without specialist review',
            'different_candidate_targets':affected,'agreed_only_dropped_targets':sorted(targets-keep) if r.get('reading_inventory_id') else sorted(targets-keep),
            'uncatalogued_inventory_targets':uncatalogued,
            'evidence':'two-coder-2026-10-09-v1/comparison.json; agreement.json; per-mapping selection-coverage.json',
            'scope':'Manuscript proposal unchanged; evaluation eligibility/graphic coverage follows each mapping.'}
        changes.append({'id':r['id'],'different_candidate_targets':affected,'added_test_ids':tests,
            'proposed_claim_wording_changed':False})
    (OWN/'claims.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    lines=['# Claim ledger','',f'{len(rows)} records. Source-proposed values and interpretations remain unchanged. Second-coding annotations link affected tests and dropped targets to the three-mapping sensitivity. The PDF is unfoliated; locators are one-based PDF pages.','',
        '| ID | Source location | Type | Paraphrase | Evidence / test |','|---|---|---|---|---|']
    for r in rows:
        extra=' Second coding: '+','.join(r['second_coding_evaluation']['different_candidate_targets']) if r.get('second_coding_evaluation',{}).get('different_candidate_targets') else ''
        cells=[r['id'],r['source_id']+' '+r['source_location'],r['type'],r['paraphrase'],r['offered_evidence']+' Tests: '+','.join(r['test_ids'])+extra]
        lines.append('| '+' | '.join(s.replace('|','/').replace('\n',' ') for s in cells)+' |')
    (OWN/'claims.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    if (BASE/change_name).exists():raise SystemExit('Ledger change endpoint exists')
    write(BASE/change_name,{'status':'Exploratory','retained_records':len(rows),'changed_evaluation_records':len(changes),
        'records_with_candidate_differences':sum(bool(r['different_candidate_targets']) for r in changes),
        'source_proposal_wording_changes':0,'changes':changes})
    cov=read(history/'ledger-coverage.json');cov['second_coder_evaluation_records']=len(changes)
    cov['second_coder_evidence']='two-coder-2026-10-09-v1/'+change_name;write(OWN/'ledger-coverage.json',cov)

def update_docs(results):
    history=OWN/'history/2026-10-09-before-second-coder'
    report=(history/'REPORT.md').read_text(encoding='utf-8-sig');rest=report[report.index('## Witness, scope'):]
    rest=rest.replace('Distinct archaeological classes await independent coding.','Distinct archaeological classes await specialist adjudication.')
    rest=rest.replace('they await the second reader.','the two coding rounds are compared above.')
    rest=rest.replace('Agreement and adjudication await the coordinator’s second coding.','Agreement is now measured above; disputed drawings await adjudication.')
    rest=rest.replace('Independent coding should precede revised graphic tests.','The independent AI coding sensitivity now precedes specialist adjudication.')
    rest=rest.replace('The 96-target crosswalk awaits second coding and contextual referents remain proposed.',
        'The 96-target crosswalk now has two AI coding rounds, with disputed targets awaiting specialist adjudication and contextual referents remaining proposed.')
    rest=rest.replace('pp. 78?79','pp. 78–79')
    opening='''# Steven Bonta’s proposal: independent coding integrated

Bonta proposes an early Indo-Aryan reading of selected signs alongside asset and measure notations. Strong ordering tendencies survive all three mappings. Jar and arrow identities agree across the two AI coding rounds, preserving final shares of 838/1,196 (70.07%) and 192/225 (85.33%), with 358 and 33 non-final exceptions. Fish adjacency is 142, 142 and 135 under the first, second and agreed-only mappings, against shuffle means 55.72, 55.72 and 54.73; every tail is .0005. These are **two AI coding rounds without specialist review**. [Comparison](two-coder-2026-10-09-v1/comparison.json); [terminal exceptions](response-2026-10-08-v2/terminal-exceptions.json).

The broad lexical match excess also survives, with construction dependence unresolved. The first and second external class mappings leave the manuscript’s proposed strings fixed: explicit-caption matching is 83/206 for both. Restricting to the 78 targets with overlapping Mayig sets gives 52/108; all exact tails are .0005. The clear-origin subset gives 2/5, 2/5 and 0/1, with tails .20, .20 and 1.0. Its absence of detectable excess survives the mapping sensitivity, on a small and shrinking base. Zero historical held-out checks are individually identified. [Lexical results](two-coder-2026-10-09-v1/comparison.json), `results`.

Field totals remain mapping-sensitive: clean/conflicting/indeterminate counts are 942/349/1,178, 781/302/1,386 and 844/379/1,246. The canonical rule exceeds its shuffle baseline under each mapping, while wider field boundaries remain unresolved. Explicit object joins stay at 713/859 attempts across all three because their CISI aliases are independent of glyph coding. The historical validation rate and physical metrology remain unmeasurable from the available sources. All endpoints remain **Exploratory**; surviving qualitative conclusions now have a two-AI-coder sensitivity rather than a single-coder qualifier. [Field and join results](two-coder-2026-10-09-v1/comparison.json); [quantity gate](run-2026-10-08-v1/metrology.json).

'''
    (OWN/'REPORT.md').write_text(opening+section(results)+rest,encoding='utf-8')
    readme=(history/'README.md').read_text(encoding='utf-8-sig')
    start=readme.index('The owner’s');readme=readme[start:]
    readme=readme.replace('All mapping-dependent results are **Exploratory until second coding is integrated**.','The second coding is integrated in the three-mapping sensitivity. All endpoints remain **Exploratory**, with two AI coding rounds and no specialist review.')
    readme=readme.replace('Independent mapping, manual adjudication of remaining source attachments,','Specialist adjudication of disputed mappings, manual adjudication of remaining source attachments,')
    intro='''# Package Q: independent coding integrated

Positional tendencies and fish clustering survive all three mappings. The broad lexical excess remains conditional on construction; the clear-origin subsets show no detectable excess. Field totals and graphic coverage vary across the two AI coding rounds, with specialist review still pending.

Mayig overlap is **78/96**: **72 exact singleton matches**, **ten disjoint nonempty sets**, **eight first-reader missing sets**. Paired-singleton kappa is **0.9217 (n=78)**. Wells/Helsinki overlap is also **78/96**. [Agreement and confidence/type splits](two-coder-2026-10-09-v1/AGREEMENT.md); [all 38 candidate/component disagreements](two-coder-2026-10-09-v1/DISAGREEMENTS.md).

| Exploratory result | First | Second | Agreed-only |
|---|---:|---:|---:|
| Clean / conflict / indeterminate fields | 942/349/1178 | 781/302/1386 | 844/379/1246 |
| Fish adjacency / shuffle mean | 142/55.72 | 142/55.72 | 135/54.73 |
| Full lexical exact hits / types | 84/228 | 84/228 | 53/123 |
| Explicit-caption exact hits / types | 83/206 | 83/206 | 52/108 |
| Clear-origin exact hits / types | 2/5 | 2/5 | 0/1 |
| Clear-origin exact tail | .20 | .20 | 1.0 |
| Alias-joined attempts | 713 | 713 | 713 |
| Fully reference-supported attempt figures | 389 | 456 | 228 |

All broad lexical, fish and canonical-clean tails are .0005. The agreed-only panel retains **330/640** full-selection occurrences and **303** explicit-caption occurrences. Source-reading scores are identical under first/second external classes because the manuscript’s sign assignments remain fixed. The agreed-only calculation changes coverage. **Zero historical held-out entries** are individually identified. [Aggregate comparison](two-coder-2026-10-09-v1/comparison.json).

B069 and B078 are the main field cases for later adjudication; B017 and B052 account for the clear-origin types lost under agreement filtering. Both-high confidence agrees on 48/49 targets, with B043 disjoint. No disputed target was resolved. `class` means chart `rank`; direct code joins verify the ordinary numeric offsets, with P000 as a damage exception and P373/P374 absent from the chart. Code 369 is absent from Mayig’s direct code lists. [Reference check](two-coder-2026-10-09-v1/reference-check.json); [post-outcome target diagnostics](two-coder-2026-10-09-v1/target-attribution.json).

## Repeat the independent-coding sensitivity

From the repository root, choose new owned/raw output directories. The replay reads the frozen operational mappings and selections. Repeat the field, lexical and join commands for `second` and `agreed_only`, then use the verifier to compare the new endpoints.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py prepare --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py field --mapping first --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py lexical --mapping first --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/second_coder_sensitivity.py joins --mapping first --output-root experiments/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02 --raw-output-root data/raw/2026-10-08-bonta-review/two-coder-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/verify_second_coder.py --replay two-coder-replay-2026-10-09-02 --output two-coder-checks-replay-2026-10-09-02.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

The registered amendment and its operational clarification precede the main outputs. Earlier outputs and both returns remain frozen. [SECOND-CODER-FILES.json](SECOND-CODER-FILES.json) inventories every created/changed path, and [two-coder-checks-2026-10-09-v2.json](two-coder-checks-2026-10-09-v2.json) records preservation and replay checks. The following paragraphs retain the PDF phase’s source inventory and frozen first-mapping results.

'''
    (OWN/'README.md').write_text(intro+readme,encoding='utf-8')
    retro=(history/'RETROSPECTIVE.md').read_text(encoding='utf-8-sig')
    retro=retro.replace('No second coding has arrived.','At that PDF-phase endpoint, the second coding had yet to arrive.')
    retro+='''

## Independent second coding integrated, 9 October 2026

The coordinator supplied an unchanged merged return from two fresh Claude Sonnet 5.5 sessions, each coding half of the packet. Their notes report packet-only source reading and visibility of outside file/folder names. Part hashes, the merged return and original packet were preserved. A dated amendment registered agreement and three-mapping sensitivities before their outcomes; the current prose and ledger were copied to history/2026-10-09-before-second-coder/.

Mayig sets overlap on 78/96 targets, with 72 exact singleton matches, ten disjoint nonempty sets and eight first-reader missing sets. Singleton kappa is .9217 on 78 paired rows. Wells and Helsinki overlap also equal 78; their kappa bases are 46 and eight paired singletons. Thirty-eight targets differ in some candidate set or component sequence, including 24 differing Mayig sets. Confidence/type splits and both codings are retained. Both-high confidence disagrees on B043, showing why confidence cannot replace visual review.

The schema check confirms class means printed chart rank and all returned cell payloads match the reference. The ordinary code joins have offset zero through P372 and two from P375; the P000 damage marker is an exception. P373/P374 codes are absent from the chart. Code 369 is absent from Mayig's direct code lists, although P043 has code 288. A dated clarification fixes the template/rank wording without editing the original instructions or selecting disputed classes.

The three operational mappings were frozen before scoring. Agreed-only retains the 78 targets with Mayig-set intersection; compounds B074/B075 drop under that rule even though their component sequences agree. B069's broader second-reader oval candidates create indeterminacy. B078 changes from one bent-pair class to a component sequence. Component codes are recognized as a complete sequence, not as the whole compound one code at a time.

The first mapping reproduces the PDF endpoint. Canonical fields change from 942/349/1178 clean/conflict/indeterminate to 781/302/1386 under the second and 844/379/1246 under agreed-only. Fish adjacency is 142, 142 and 135, with means 55.72, 55.72 and 54.73. All canonical-clean and fish tails are .0005. Mayig gives 42/12/46, 35/11/54 and 38/12/50 on the same 100 overlapping clear lines. These are mapping sensitivities on shared objects, with wider field boundaries unresolved.

Source-reading lexical scores are unchanged under the two external class codings because manuscript sign IDs and proposed value bundles remain fixed. Agreement filtering removes 310/640 occurrences. Full exact scores are 84/228, 84/228 and 53/123; explicit-caption scores are 83/206, 83/206 and 52/108, all tails .0005. Clear-origin caption scores are 2/5, 2/5 and 0/1, tails .20, .20 and 1.0. B017 and B052 account for the dropped clear-origin types. The broad conditional excess and unresolved construction dependence survive; no clear-origin excess or historical held-out result emerges.

Explicit alias joins remain 713/859 attempts and 338 object families under all mappings. Fully reference-supported figures change to 389, 456 and 228, which measures graphic coverage separately from object identity. Literal transcription consistency remains 356/593 exact under first/second and becomes 216/306 under agreed-only. No new object evidence or success/failure denominator is inferred.

After seeing all three outcomes, a registered target-attribution diagnostic located the largest field effects: B069 changes 153 classifications alone and B078 changes 62. Omitting B074/B075 changes 32/21 and lowers fish adjacency to 138/139. These post-outcome diagnostics preserve each candidate for a later adjudicator. Source-proposal wording in the ledger remains unchanged; new test annotations identify affected candidate sets and agreement-filtered coverage. Surviving conclusions lose the single-coder qualifier and retain the two-AI-coder/no-specialist-review description. All endpoints remain Exploratory.
'''
    (OWN/'RETROSPECTIVE.md').write_text(retro,encoding='utf-8')
    completion=(history/'COMPLETION.md').read_text(encoding='utf-8-sig')
    completion=completion.replace('The independent coder has the packet and return schema available locally; no coding has arrived. All first-coder mapping results are Exploratory.',
        'The independent AI coding has arrived and is integrated. Agreement and three-mapping sensitivities are complete; disputed targets await specialist adjudication. Endpoints remain Exploratory, with surviving qualitative findings supported by two AI coding rounds without specialist review.')
    (OWN/'COMPLETION.md').write_text(completion+'\nThe second-coding outputs are in two-coder-2026-10-09-v1/. SECOND-CODER-FILES.json inventories this phase. Historical PDF checks remain applicable to their frozen outputs.\n',encoding='utf-8')
    registry=read(history/'registry-entry.json')
    registry['outcome']='Two AI coding rounds without specialist review: Mayig overlap 78/96, exact singleton 72, disjoint nonempty 10, first missing 8; paired-singleton kappa .9217 (n78). Wells/Helsinki overlap 78 each. First/second/agreed-only fields 942/349/1178, 781/302/1386, 844/379/1246; fish 142/142/135 versus means55.72/55.72/54.73, all tails .0005. Full lexical84/228,84/228,53/123 and explicit-caption83/206,83/206,52/108, all exact tails .0005. Clear-origin2/5,2/5,0/1, exact tails .20/.20/1.0. Source assignments fixed across external class codings; agreed-only coverage restriction retains330/640 occurrences. Historical held-out entries0. Alias joins713/859,338objects unchanged; fully reference-supported figures389/456/228. Strong position/clustering and conditional lexical excess survive, with construction dependence and no clear-origin excess. Numerical field totals remain sensitive. Jar838/1196 final,358 nonfinal,241 followed400/090; arrow192/225 final,33nonfinal. Earlier10panel: all13 normalized permutations scoring>=9 keepPU; none600movingPUreaches9;8/10stringsPU/PATI dictionary-derived againstsamecontexts, tailclosetocircular;9matchesexact and normalizationbroaderthanTable18. ICIT68firstlabels48joined,8confirmedMHlinks+1questioned; earlier3repeatedobjects oneICIT-first/oneMH-firstalias/oneiconography and3parserfalseoverlaps. Historical validation denominator unknown;physicalquantityjoins0. All earlier outcomes preserved; no disputed target adjudicated.'
    registry['challenge']='Disjoint/missing graphic candidates and allograph subsets; B069/B078 field sensitivity; B017/B052 clear-origin coverage; two AI coding rounds without specialist review. Unknown lexical construction for later extensions, missing historical check/failure batch and physical quantity joins remain. Captions/audio and source attachment qualifications persist.'
    registry['remedy']='Registered candidate-set agreement and singleton kappa; checked explicit chart/code/rank joins and input part hashes; froze first/second/agreed-only mappings; reran fields, fish, source lexical panels and alias/reference coverage; recorded every candidate disagreement and post-outcome target attribution; preserved all old outputs and coding returns; updated only owned summaries and test annotations.'
    registry['evidence'] += ['experiments/2026-10-08-bonta-review/two-coder-2026-10-09-v1/'+f for f in ['agreement.json','AGREEMENT.md','DISAGREEMENTS.md','reference-check.json','mapping-freeze.json','comparison.json','target-attribution.json','ledger-changes-v2.json']]
    registry['evidence'] += ['experiments/2026-10-08-bonta-review/two-coder-checks-2026-10-09-v2.json','experiments/2026-10-08-bonta-review/SECOND-CODER-FILES.json']
    registry['retry_when']='Specialist adjudication of disputed targets, especially B069/B078 and B017/B052/B043, followed by new versioned reruns. Obtain explicit wider field boundaries, historical ICIT attempted/rejected list and pre-check assignments, or externally reserved finite-rule predictions. Physical metrology needs independent quantity joins.'
    write(OWN/'registry-entry.json',registry)

if __name__=='__main__':
    results,findings=summarize();readable_agreement();ledger();update_docs(results)
    print(findings)
