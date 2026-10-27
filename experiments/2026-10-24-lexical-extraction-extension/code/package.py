"""Write provenance and proposed registry records from versioned outputs."""
from datetime import datetime, timezone
import json
import extract as e

def read(p):return json.loads(p.read_text(encoding='utf8'))

def main():
    frozen=read(e.PKG/'FREEZE-v3.json')
    sources=[]
    for slug,key in [('2026-10-22-rebus-winslow',None),('2026-10-21-rebus-base-rate','tamil-lex')]:
        p=e.ROOT/'experiments'/slug/'SOURCES.json'
        original=read(p)
        metadata=original['source'] if key is None else original['sources'][key]
        pages=[x for x in frozen['pages'] if slug in x['logical_path']]
        sources.append(dict(parent_manifest=p.relative_to(e.ROOT).as_posix(),parent_sha256=e.sha(p),
            original_metadata=metadata,pages=len(pages),bytes=sum(r['bytes'] for r in pages),
            page_records='FREEZE-v3.json#/pages',new_retrieval=False,
            rights_status='rights-unverified' if key is None else 'explicit-license',
            handling='local-only originals and detailed derivatives'))
    logs=[]
    for p in sorted(e.WRAW.glob('requests*.jsonl')):
        for r in e.rows(p):
            if r.get('finished_utc'):logs.append(r['finished_utc'])
    sources[0]['retrieval_finished_utc_first']=min(logs)
    sources[0]['retrieval_finished_utc_last']=max(logs)
    outputs=[]
    for p in sorted((e.RAW/'run-v1').glob('*')):
        outputs.append(dict(logical_path='data/raw/2026-10-24-lexical-extraction-extension/run-v1/'+p.name,
            physical_path=str(p),bytes=p.stat().st_size,sha256=e.sha(p)))
    e.dump(e.PKG/'source-manifest-v1.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        sources=sources,output_files=outputs,pinned_code_and_inputs=frozen['pins'],
        freeze_sha256=e.sha(e.PKG/'FREEZE-v3.json'),source_exposure=dict(
            machine_content_access='All held Winslow and Tamil Lexicon pages hashed; complete Winslow parsed; Lexicon boundary metadata read',
            displayed_content='Prior lexical reports and selected am source block; author regression replay writes local source records',
            archaeological_confirmation_objects_opened=0)))
    result=read(e.PKG/'results-v1.json')
    validations=read(e.PKG/'validation-v2.json')
    report=f'''# Complete lexical extraction with source-qualified boundaries

We re-extracted all {result['records']:,} held Winslow records from {result['pages']} DSAL pages. The version preserves every parent row identity, keeps parent origin marks on subentries, and separates direct Winslow parsing from boundaries supplied by the Tamil Lexicon. The selected two-member count changes from {result['prior_two_member']:,} to {result['revised_two_member']:,}. These are extracted structural records; every row still requires lexical eligibility review before a comparative scorer uses it.

## What the extraction changes

[results-v1.json](results-v1.json) records {result['member_changes']:,} changed member lists: {result['added_two_member']:,} enter the two-member table, {result['removed_two_member']:,} leave it, and {result['changed_two_member']:,} retain two members with a changed analysis. The local delta table preserves each before-and-after decision. The original extraction remains unchanged.

An exact NFC Tamil headword and a unique compatible two-member analysis admit a Tamil Lexicon boundary. Every such decision records its printed romanisation, homograph, query page and original page hash. Single consonant connectors remain visible in the printed romanisation. Conflicting homographs retain an unresolved status. We retain the original derived transliteration as a legacy field; selected boundaries are the explicit members field and their separate source references.

The inherited e/ē and o/ō comparison is used only to align roman transcriptions of the same Tamil headword. It affects {result['lexicon_assisted_rows_using_e_or_o_length_alignment']:,} assisted rows and is identified per source reference. This convention supplies no lexical substitution rule. Tamil vowel spelling, other vowel lengths and consonant doubling remain distinct.

The source-backed grammatical guard suppresses the known false ja plus mīṉ analysis of jamīṉ, Winslow p.528. The Lexicon's ai-n-taru analysis, p.577, replaces the wrong aint plus aru boundary in Winslow p.195 and recovers the same headword under taru on p.553. The previously documented game and cheerfulness omissions are included in the complete exact-headword comparison, with their actual outcomes retained in the local regression table.

## Increment candidates and lexical scope

The connecting-particle sense of am in Winslow p.31 and the euphonic-augment sense in Tamil Lexicon p.94 motivate a general candidate generator. For an exact noun principal ending in u, it tries am and the matching nasal before a stop, and requires the other lemma to be another exact noun principal. It operates in both nesting directions. The known murukkampū entry recovers a unique candidate analysis with murukku. Murukkañcettal remains outside the candidate generator because Winslow labels its parent cettal as a verbal noun, while the frozen candidate scope requires exact noun principals. Both selected member lists remain empty; expanding that noun policy and establishing the increment distribution require linguistic adjudication. The doubled consonant in murukku is retained.

The complete run has this increment disposition: {json.dumps(result['increment_status'],ensure_ascii=False)}. Parent marks are preserved on {result['parent_marked_subentries']:,} subentry rows. A borrowed parent does not settle the origin of the entire compound. The output retains unresolved whole-entry origin and false comparative-scorer eligibility on every record. Two structural members require separate evidence before they qualify as two native picturable nouns.

The source-assisted layer creates dependence between Winslow and the Tamil Lexicon. It is useful for finding and reviewing boundaries, but a later comparison cannot count those boundaries as independent agreement between dictionaries. The raw Winslow members after the grammatical guard remain available as a separate field.

## Checks, source access and remaining work

[validation-v2.json](validation-v2.json) records {validations['tests_run']} passing focused tests, exact source and hash bindings for all 43 previously reviewed rows, reparsing of their referenced original Lexicon blocks, full population preservation, and separate known regression checks. The [segmentation](segmentation-synthetic-v1.json) and [shots](shots-synthetic-v1.json) generated controls pass. These are author implementation checks on examined source material. They estimate neither dictionary-wide precision nor recall and do not supply independent Tamil review.

[FREEZE-v3.json](FREEZE-v3.json) pins the protocol, adapter, imported code, both parent tables, 978 Winslow pages and 4,400 Lexicon pages before extraction. The first freeze and exact first adapter are preserved; versions 2 and 3 add parallel hash verification, per-run hash reuse, and explicit accounting for malformed headword blocks skipped by the inherited parser before extraction outcomes. [source-manifest-v1.json](source-manifest-v1.json) records source titles, URLs, rights, inherited acquisition times, bytes, hashes, output locations and source exposure. Full tables, source blocks and detailed reviews are physically on D:. No dictionary was newly downloaded, no substantive rebus effect was recomputed, and no real confirmation cohort was opened.

The residual queue needs a Dravidianist's review of increment distribution, conflicting or unmarked boundaries, noun senses, phrase status, native and borrowed ancestry, historical attestations and principal compounds without an etymology or a matching printed boundary. The current source selection also retains the earlier Lexicon page stream's known acquisition gaps; hashing that stream adds no missing pages.

The strongest supported reading is that the known extraction defects can be repaired or exposed by general source-qualified operations across the complete held dictionary. The test that would decide readiness for a fair lexical comparison is an independent specialist adjudication of stratified accepted and unresolved records, followed by a calibrated scorer using declared senses, morphology and dictionary dependence.
'''
    with (e.PKG/'REPORT.md').open('x',encoding='utf8') as f:f.write(report)
    prefix=e.PKG.relative_to(e.ROOT).as_posix()
    entry=dict(id='LEXICAL-EXTRACTION-EXTENSION-2026-10-24',theme='Source-qualified complete dictionary extraction and conservative morphology candidates',
        status='completed-versioned-extraction; specialist-eligibility-pending',status_class='exploratory',area='methods',
        question='Can general source-backed extraction repairs preserve the complete Winslow population and expose unresolved morphology for a fair later reading comparison?',
        outcome=f"Re-extracted {result['records']} Winslow records from {result['pages']} pages. Selected two-member rows changed from {result['prior_two_member']} to {result['revised_two_member']}; {result['member_changes']} member lists changed. Lexicon assistance, parent borrowing marks and unresolved increment candidates have separate provenance. All comparative-scorer eligibility remains false. No rebus effect or real confirmation was run.",
        challenge='Printed boundaries and lexical senses are distinct. Lexicon-assisted Winslow rows create comparative source dependence; borrowed parents, morphological increments and historical senses require specialist review.',
        remedy='Pinned protocol, imported parents, complete tables and all source pages; retained original and guarded members, exact-headword cross-source evidence, unresolved candidates and separate known-regression checks.',
        evidence=[prefix+'/'+x for x in ['PROTOCOL.md','FREEZE-v1.json','FREEZE-v2.json','FREEZE-v3.json','REPORT.md','RETROSPECTIVE.md','DATA-UPDATE.md','results-v1.json','validation-v2.json','source-manifest-v1.json','segmentation-synthetic-v1.json','shots-synthetic-v1.json']],
        retry_when='Independent Tamil specialist review resolves remaining morphology, senses and lexical eligibility; a later calibrated comparison declares dictionary dependence and freezes all participants before reviewed unexamined confirmation.',
        package=prefix,authors=[dict(model='gpt-6.1-sol',harness='Codex collaboration',agent='lexical extraction worker',qualifications='AI source reviewer without specialist Tamil credentials')],verification_tier='submitted')
    e.dump(e.ROOT/'knowledge/registry/attempts/LEXICAL-EXTRACTION-EXTENSION-2026-10-24.json',entry)
    commands=['python experiments/2026-10-24-lexical-extraction-extension/code/extract.py freeze',
        'python experiments/2026-10-24-lexical-extraction-extension/code/extract.py freeze2',
        'python experiments/2026-10-24-lexical-extraction-extension/code/extract.py freeze3',
        'python experiments/2026-10-24-lexical-extraction-extension/code/extract.py run',
        'python -m unittest discover -s experiments/2026-10-24-lexical-extraction-extension/code -p test_extract.py -v',
        'python -m bench segmentation --synthetic --out experiments/2026-10-24-lexical-extraction-extension/segmentation-synthetic-v1.json',
        'python -m bench shots --synthetic --out experiments/2026-10-24-lexical-extraction-extension/shots-synthetic-v1.json',
        'python experiments/2026-10-24-lexical-extraction-extension/code/validate.py',
        'python experiments/2026-10-24-lexical-extraction-extension/code/package.py']
    e.dump(e.PKG/'commands-v1.json',dict(commands=commands,author_checks_pass=validations['pass_all'],
        interrupted_attempt='Initial source scan stopped before writing a freeze or extraction endpoint; resumable page scan replaced it'))

if __name__=='__main__':main()
