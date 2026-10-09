"""Apply source/interpretation corrections to editable summaries; preserve frozen files."""
import copy, json, re
from pdf_followup import OWN, RAW, ROOT, read, write, sha
from pdf_review_sources import BAD_CODES, EMPTY_CAPTIONS, MISJOINS

OUT = OWN / 'pdf-review-response-2026-10-09-v1'
LOCAL = RAW / OUT.name
HISTORY = OWN / 'history/2026-10-09-before-pdf-review'


def paragraph(text, prefix, replacement):
    start = text.index(prefix)
    end = text.find('\n\n', start)
    if end < 0:
        end = len(text)
    return text[:start] + replacement + text[end:]


def ledger():
    if (OUT / 'ledger-changes.json').exists():
        raise SystemExit('Ledger audit exists')
    original = [json.loads(line) for line in (HISTORY / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    rows = copy.deepcopy(original)
    inv = {r['reading_id']: r for r in read(LOCAL / 'reading-inventory-v5.json')}
    derivations = {r['table18_entry']: r for r in read(OUT / 'value-derivations-v3.json')['rows']}
    derivation_changes = {r['entry'] for r in read(OUT / 'derivation-changes.json')['rows']}
    selection = {r['reading_id']: r for r in read(RAW / 'pdf-2026-10-09-v1/lexical-selection-v2.json')['readings']}
    split = read(LOCAL / 'derivation-split-membership.json')
    labels = set(split['labels'])
    changed = []
    for old, row in zip(original, rows):
        if row.get('note'):
            row['note'] = row['note'].replace(' Mapping awaits second coding.', '')
        if 'P-L' in row.get('test_ids', []) or 'S2-L' in row.get('test_ids', []):
            row['pdf_review_evaluation'] = {
                'status': 'Exploratory', 'lexical_external_mapping_used': False,
                'agreed_only_effect': 'Eligibility exclusions only',
                'clear_origin_inference': 'Frozen five-type construction cannot attain significance; corrected source histories are value-specific.',
                'evidence': 'pdf-review-response-2026-10-09-v1/lexical-corrections.json'}
            row['test_ids'] = list(dict.fromkeys(row['test_ids'] + ['PR-L', 'PR-H']))
        if 'P-F' in row.get('test_ids', []) or 'S2-F' in row.get('test_ids', []):
            row['test_ids'] = list(dict.fromkeys(row['test_ids'] + ['PR-F', 'PR-O']))
            row['field_test_update'] = 'Final-or-penultimate terminal sensitivity and separate M-order endpoint; pdf-review-response-2026-10-09-v1/{first,second,agreed_only}/field-corrections.json.'
        match = re.fullmatch(r'Q(\d+)', row['id'])
        role = int(match[1]) - 54 if match else None
        if role in derivation_changes and 55 <= int(match[1]) <= 112:
            row['value_derivation_evidence'] = {
                'table18_entry': role, 'source_pages': derivations[role]['source_pages'],
                'category': derivations[role]['category'], 'basis': derivations[role]['basis'],
                'file': 'pdf-review-response-2026-10-09-v1/value-derivations-v3.json'}
            row['test_ids'] = list(dict.fromkeys(row['test_ids'] + ['PR-D']))
            row['offered_evidence'] = 'The Table 18 drawing/value list and the author’s derivation passages are distinguished in value_derivation_evidence. The lexical scorer uses manuscript roles; agreed-only changes eligibility.'
        rid = row.get('reading_inventory_id')
        if rid:
            source = inv[rid]
            row['offered_evidence'] = f'Local reading-inventory-v5.json row {rid}: PDF drawing/caption, transcription, qualifiers and preserved explicit alias joins; tracked reading-index-v5.json.'
            row['unclear_or_unattested_source_flag'] = source['unclear_or_unattested_flag']
            row['probable_misjoin_source_flag'] = rid in MISJOINS
            row['pdf_review_inventory_evaluation'] = {
                'status': 'Exploratory', 'extraction_correction': source.get('extraction_correction'),
                'frozen_lexical_selection_eligible': rid in selection,
                'named_derivation_label': source['primary_label'] in labels,
                'reading_failure_rate_inferred': False,
                'evidence': 'pdf-review-response-2026-10-09-v1/reading-corrections.json; join-corrections.json'}
            row['test_ids'] = list(dict.fromkeys(row['test_ids'] + ['PR-R', 'PR-J']))
            if rid in EMPTY_CAPTIONS:
                row['paraphrase'] = f'He prints a whole or partial proposed sign-caption reading under {source["primary_label"]}; the earlier empty transcription was an extraction defect.'
            elif rid in BAD_CODES:
                row['paraphrase'] = f'He prints a continuation figure associated with {source["primary_label"]}, followed by a catalogue alias rather than an individual reading caption.'
        if row['id'] == 'Q134':
            row['paraphrase'] = 'He limits canonical O groups to at most two units and F groups to at most three nonrepeating units.'
            row['offered_evidence'] = 'Manuscript p. 21. The repeated-O prohibition in the operational grammar is an unstated assumption affecting three first-mapping texts.'
        if row['id'] == 'Q053':
            row['source_location'] = 'Introductory letter hosted by Jeff Lindsay, PDF p. 5'
            row['offered_evidence'] = 'The separate letter’s PDF p. 5 gives the author’s account; Lecture 7 and the second-edition manuscript foreword each report one withdrawn value.'
        if row != old:
            changed.append({'id': row['id'], 'source_paraphrase_changed': row['paraphrase'] != old['paraphrase'],
                            'source_location_changed': row['source_location'] != old['source_location'],
                            'reading_id': rid, 'derivation_entry': role if role in derivation_changes else None})
    assert len(rows) == 1021 and [r['id'] for r in rows] == [r['id'] for r in original]
    (OWN / 'claims.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    lines = ['# Claim ledger', '',
             'Source claims retain their IDs and witnesses. Sounds, meanings and readings are Bonta’s proposals. PDF-review corrections separate lexical construction, source extraction and object identity; earlier ledger states remain in history/.', '']
    for row in rows:
        lines += [f'## {row["id"]}', '', f'**{row["type"]}**. Source: {row["source_id"]}, {row["source_location"]}.', '',
                  row['paraphrase'], '', f'Evidence: {row["offered_evidence"]}', '',
                  f'Tests: {", ".join(row["test_ids"])}. Status: {row["assessment_status"]}.', '']
        if row.get('quotation'):
            lines += [f'Source wording: “{row["quotation"]}”', '']
        if row.get('value_derivation_evidence'):
            detail = row['value_derivation_evidence']
            lines += [f'Derivation: {detail["basis"]} Manuscript pages {", ".join(map(str, detail["source_pages"]))}.', '']
        if row.get('probable_misjoin_source_flag'):
            lines += ['Object join: probable mistyped-CISI alias; retain the original match and exclude it in the conservative join count.', '']
    (OWN / 'claims.md').write_text('\n'.join(lines), encoding='utf-8')
    write(OUT / 'ledger-changes.json', {'status': 'Exploratory', 'records': len(rows), 'changed_records': len(changed),
         'source_paraphrases_changed': sum(r['source_paraphrase_changed'] for r in changed), 'changes': changed,
         'quotation_preservation': all(a.get('quotation') == b.get('quotation') for a, b in zip(original, rows))})
    coverage = read(HISTORY / 'ledger-coverage.json')
    coverage['pdf_review_response'] = {'records': len(rows), 'changed_records': len(changed),
                                      'audit': 'pdf-review-response-2026-10-09-v1/ledger-changes.json'}
    write(OWN / 'ledger-coverage.json', coverage)


def report():
    base = (HISTORY / 'REPORT.md').read_text(encoding='utf-8')
    rest = base[base.index('## Witness, scope and preserved evidence'):]
    # Repair only existing punctuation encoding defects in current prose.
    rest = rest.replace('â€™', '’').replace('â€“', '–')
    opening = '''# Steven Bonta’s proposal: PDF-review corrections

Bonta proposes an early Indo-Aryan reading of selected signs together with asset and measure notation. The strongest results concern ordering. The jar is final in **838/1,196 tokens (70.07%)** and the arrow in **192/225 (85.33%)**, with **358** and **33** non-final exceptions. Fish adjacency is **142, 142 and 135** under the first, second and agreed-only mappings, against shuffle means **55.72, 55.72 and 54.73**. M-unit order is **288/331 (87.0%)**, **226/249 (90.8%)** and **288/331 (87.0%)**, against **58.9%, 68.4% and 58.9%** under shuffling; all fish and M-order tails are **.0005**. These Exploratory results use **two AI coding rounds without specialist review**. [Terminal exceptions](response-2026-10-08-v2/terminal-exceptions.json); [fish](two-coder-2026-10-09-v1/comparison.json); [M order](pdf-review-response-2026-10-09-v1/first/field-corrections.json), with second/agreed-only files beside it.

The broad lexical panel gives **83/206 exact type matches**, tail **.0005**, with substantial construction dependence. In the earlier ten-type panel, eight strings use PU/PATI values derived by searching the same dictionary against those contexts. All 13 permutations reaching nine matches retain PU; none of the 600 moving it reaches nine. The lexical scorer reads manuscript role IDs and proposed value bundles. First/second external mappings are absent from that calculation; agreed-only changes eligibility and gives **52/108**. Lexical mapping-survival claims are withdrawn. [Frozen lexical panels](pdf-2026-10-09-v1/lexical-caption-sensitivity.json); [PU census](review/role-pair-census.json).

The frozen clear-origin panel cannot show an excess under its own construction. Three mahā- types become unmatchable when maha is removed, so **2/5, tail .20**, is its best attainable exact score. Both hits use dictionary-derived pāla; one also uses reading-supported ASHVA. A partial split excluding **129 derivation labels** gives **5/8**, tail **.0256**, and all five hits require PU, PATI or maha. It separates named derivation examples from other examples, while the paper leaves their historical reservation and later value fitting unresolved. The corrected anchor-only panel gives **0/7** exact matches and **2/7** normalized matches (tail **.7556**); its exact null also has no hits. These source subsets cannot provide a larger independently reserved test. [Lexical corrections](pdf-review-response-2026-10-09-v1/lexical-corrections.json); [hit dependence](pdf-review-response-2026-10-09-v1/source-diagnostics.json).

The wider field boundaries, historical validation rate and physical metrology remain unmeasurable. Admitting a penultimate terminal, as the manuscript permits, gives **1,144 clean, 136 conflicting and 1,189 indeterminate texts**, versus a shuffle mean **622.54** under the first mapping. The frozen final-only rule gave **942/349/1,178**, and **683/942 clean texts have no M field**, so much of its excess restates the terminal tendency. Explicit alias matches remain **713/859 attempts across 338 object families**; excluding six probable mistyped-CISI joins leaves **707/859 across 334 families**. [Field correction](pdf-review-response-2026-10-09-v1/first/field-corrections.json); [join correction](pdf-review-response-2026-10-09-v1/join-corrections.json).

## Review response and reference coding

[REVIEW-PDF.md](REVIEW-PDF.md) and its [independent calculations](review-pdf/) are preserved and reused. New source corrections and outcomes are in [pdf-review-response-2026-10-09-v1/](pdf-review-response-2026-10-09-v1/). Earlier runs and the pre-review summaries remain frozen. [Protocol amendment](PROTOCOL.md); [snapshot](history/2026-10-09-before-pdf-review/).

Mayig candidate sets overlap on **78/96 targets**, with **72 exact singleton matches**, **ten disjoint sets** and **eight first-reader missing sets**; paired-singleton κ is **.9217 (n=78)**. Wells and Helsinki overlap are also 78, with κ **.9109 (n=46)** and **.7193 (n=8)**. The blind second packet remains intact. The first coder compared the **17 caption forms with Table 18 families**, so that part of the first coding was informed by Bonta’s grouping. The second coder’s half-height/full-height stroke inference remains a field-mapping uncertainty. [Agreement](two-coder-2026-10-09-v1/AGREEMENT.md); [38 disagreements](two-coder-2026-10-09-v1/DISAGREEMENTS.md).

Agreed-only retains the 78 targets with overlapping Mayig sets and uses their candidate intersections. Components B074/B075 drop under this strict rule despite matching decompositions. B069 and B078 produce the largest field-count changes; no disputed target was adjudicated. The reference check verifies `class` as printed chart `rank`, ordinary Mayig offsets through P372/from P375, the P000 damage exception, and the absence of a direct Mayig code-369 join. [Frozen mappings](two-coder-2026-10-09-v1/mapping-freeze.json); [reference check](two-coder-2026-10-09-v1/reference-check.json); [attribution](two-coder-2026-10-09-v1/target-attribution.json).

| Exploratory field endpoint | First | Second | Agreed-only |
|---|---:|---:|---:|
| Frozen final-only clean/conflict/indeterminate | 942/349/1178 | 781/302/1386 | 844/379/1246 |
| Final-or-penultimate clean/conflict/indeterminate | 1144/136/1189 | 970/100/1399 | 1040/172/1257 |
| Widened clean shuffle mean | 622.54 | 563.38 | 583.56 |
| M units in O–F–MS order | 288/331 | 226/249 | 288/331 |
| M-order shuffle mean | 58.87% | 68.39% | 58.89% |
| Fish adjacency | 142 | 142 | 135 |

Every widened-clean, M-order and fish tail is .0005. The widened clean reference ranges are **596–649**, **539–589** and **557–610**. M-order ranges are **54.4–63.4%**, **63.9–73.1%** and **54.7–63.1%**. The second mapping’s ambiguous oval assignments change its eligible M denominator. M order is measured among recognized units in each text, independently of whether the full text is classified clean. Lexical-versus-metrological fish use and independently marked field boundaries remain unresolved. [First](pdf-review-response-2026-10-09-v1/first/field-corrections.json), [second](pdf-review-response-2026-10-09-v1/second/field-corrections.json), [agreed-only](pdf-review-response-2026-10-09-v1/agreed_only/field-corrections.json).

'''
    rest = paragraph(rest, 'Explicit manuscript CISI aliases join', '''The frozen explicit-alias audit joins 713/859 attempts to 338 object families through 340 CISI aliases, with 146 unjoined attempts and 33 source-qualified entries. The review identifies probable mistyped-CISI aliases on four objects: H-271/ICIT513 (R0374), M-707/ICIT2983 (R0633, R0860, R0873), M-106/ICIT3401 (R0917) and M-122/ICIT3557 (R0951). Their figure lengths are 6, 4, 4 and 7, compared with CISI-object lengths 4, 7, 6 and 3; the objects named by the printed ICIT numbers match those figure lengths. Partial figures make length agreement suggestive. The original joins remain flagged, and excluding the six readings/four families gives **707 joined attempts and 334 families**. Six other identifier conflicts and the 33 source-qualified entries stay separate. [Join evidence](pdf-review-response-2026-10-09-v1/join-corrections.json); [review audit](review-pdf/join-audit.json).''')
    rest = paragraph(rest, 'The current claim ledger contains', '''The claim ledger retains **1,021 records**, comprising 130 earlier records, 32 PDF source claims and 859 extracted reading annotations. This response corrects source derivations, transcription/uncertainty annotations, probable joins and lexical/field test interpretations. All quotations are preserved. The inventory repairs four catalogue-code transcriptions, including R1097, and twelve empty sign captions, including R0146. Transcription coverage changes from **718 to 726** attempts; the 859-attempt denominator stays fixed. The widened row-local uncertainty search adds **57 flags**, changing **103 to 160**. Question marks can qualify an alias as well as a reading, so the flag supplies no failed-reading rate. The review’s reported 94 keyword rows/60 additions does not reproduce on retained row-local `source_text`; the registered search finds 69 matching attempts and 57 additions. [Corrections](pdf-review-response-2026-10-09-v1/reading-corrections.json); [keyword reconciliation](pdf-review-response-2026-10-09-v1/source-diagnostics.json); [ledger changes](pdf-review-response-2026-10-09-v1/ledger-changes.json).''')
    rest = paragraph(rest, 'Bonta’s canonical reading order', '''Bonta’s canonical reading order is P, M, C, T, with optional spans. P contains prefixes or authorities and can end at a juncture. M contains oval units before fish units before the MA-like sign plus strokes; C contains the name/title sequences used for most lexical readings. Jar and arrow often delimit an ending. The manuscript permits a jar in final or penultimate position (p. 15) and describes other terminal environments on p. 57. Canonical O groups contain at most two units and F groups at most three nonrepeating units (pp. 20–24). The operational repeated-O prohibition is an unstated assumption affecting three first-mapping texts. Table 19 gives 19 wider metrological templates (pp. 234–240), with contextual boundaries outside these endpoints. [Frozen rules](pdf-2026-10-09-v1/field-rules.json); [corrected rule](pdf-review-response-2026-10-09-v1/first/field-corrections.json); Q134.''')
    rest = paragraph(rest, 'The registered canonical test checks', '''The frozen final-only canonical rule checks P-exclusive junctures before a contiguous O–F–MS span, count/repetition restrictions, residual C and final T. Its first mapping gives **942 clean, 349 conflicting and 1,178 indeterminate** texts, shuffle mean **419.87**, range **395–445**, tail **.0005**. Of 289 texts excluded for terminal position, **215 have a penultimate terminal**; these are outside the narrower registered rule while the manuscript allows that position. Widening T gives **1,144/136/1,189**, mean **622.54**, range **596–649**, tail **.0005**. Of the frozen 942 clean texts, **683 lack M**, including **323 C-plus-T texts** and **360 with P but no M**; **259 contain M**. Thus the clean excess largely restates the terminal preference. The separate conditional M-order result is **288/331 (87.0%)**, against **58.9%** under unit shuffling, tail **.0005**; both other mapping results are tabulated above. [Decomposition and correction](pdf-review-response-2026-10-09-v1/first/field-corrections.json); [review decomposition](review-pdf/field-decomposition.json).''')
    rest = paragraph(rest, '[Frozen full calculation]', '''[Frozen full calculation](pdf-2026-10-09-v1/lexical-test.json), `panels`; [caption sensitivity](pdf-2026-10-09-v1/lexical-caption-sensitivity.json), `panels`. The full normalized score is 100/228, mean 45.09; explicit-caption score is 98/206, mean 46.39, both tails .0005. Normalization exceeds Table 18’s value lists, while its vowel-length collapse also follows Bonta’s position on manuscript p. 68. Some section headings state vowel-length variants absent from the fixed bundles, so exact matching is slightly conservative relative to those variants. The reviewer’s Table-class-restricted null still gives 83 exact hits against mean 35.2 (maximum 55), and 98 normalized against 54.6, tails .0005. These controls retain construction dependence. [Independent lexical audit](review-pdf/lexical-recheck.json), `class_restricted_null`.''')
    rest = paragraph(rest, 'The derivation inventory classifies', '''The corrected derivation inventory treats mIn(a) as an M-field anchor (pp. 45–46, 55, 189), caru as a pot/numeral-context anchor (pp. 185–187), and AS/ISH/ASTI as structural/predicate proposals from 2014 (pp. 56–66). PAla has distinct histories: pala from weight contexts (pp. 50–51), pāla from Monier-Williams name endings (pp. 67–68), and bala fitted later (p. 76). ASHVA is supported by seven of eight readings on p. 215; GO is more tentative on p. 216. Both are mixed pictorial/reading-supported hypotheses. DAna’s initial bow argument belongs at pp. 45–47 and 55, with the later label reversal retained. [Versioned derivations](pdf-review-response-2026-10-09-v1/value-derivations-v3.json).''')
    after = '''

The frozen five-type clear-origin panel contains MA–PALA, MA–DHANA1, MA–ASHVA, DHANA2–PALA and ASHVA–PALA. Its first three intended mahā- strings become unmatchable after removing maha. The maximum own-bundle score is **2/5**, with tail **.20**; reaching the .05 threshold requires three hits. The null histogram is 60, 36, 18 and 6 assignments scoring zero through three. Both attainable hits use dictionary-derived pāla, and ASHVA’s value is supported by its own readings. The full-selection endpoint remains **2/7**, and agreed-only **0/1**, as frozen source subsets with the same limits. The review’s expanded source-origin variants have exact tails .17 or higher. [Attainability](pdf-review-response-2026-10-09-v1/lexical-corrections.json), `clear_origin_attainability`; [review variants](review-pdf/lexical-recheck.json).

Using the corrected non-lexical-anchor variants, twelve explicit-caption occurrences yield **seven types, zero exact hits**; the exact null mean is also zero. Normalization gives **2/7**, mean 2.10, tail **.7556**. Adding entries 12/15, whose numeral motivation is suggested but whose derivation is unstated, gives **4/13** exact, mean 3.48, tail **.4860**. This broader sensitivity retains unknown lexical histories. These small, source-selected panels cannot establish independent lexical confirmation. [New panels](pdf-review-response-2026-10-09-v1/lexical-corrections.json), `panels`.

The reviewer’s partial split uses the **129 primary MH/ICIT labels** appearing on manuscript pp. 39–77. Early-value caption readings give **11/16** exact, mean 3.76; excluding those labels leaves **14 occurrences, eight types and five exact hits**, mean **2.14**, tail **.0256**. All five require PU, PATI or maha. Excluding PU/PATI and fitted maha/bala leaves **0/3** exact; the corrected anchor-only split gives **0/5**, normalized **1/5**, tail **.7667**. Closing membership through literal same-manuscript aliases and explicit CISI identities finds **76 joined derivation families** and leaves the held-out scores unchanged. This split separates named derivation examples, while repeated confirmation before adopting early values (p. 76) prevents identifying a sealed batch. The unknown later-extension histories, attempted failures and independently reserved examples prevent a better-powered non-circular test from these sources. [Partial split](pdf-review-response-2026-10-09-v1/lexical-corrections.json), `partial_split`, `panels`; [review split](review-pdf/heldout-sensitivity.json).
'''
    marker = '\n\nThe earlier ten-type panel'
    rest = rest.replace(marker, after + marker, 1)
    rest = paragraph(rest, 'The PDF foreword (p. 5)', '''The **second-edition manuscript foreword, PDF p. 5**, describes MH-first development, an ICIT check and one withdrawn value. Its entry-format rule (pp. 84–85) permits ICIT-first headings when their transcription of an MH object was more accurate. The frozen inventory has 68 distinct ICIT-first labels in 113 attempt rows; 48 labels have explicit corpus aliases, with eight confirmed MH links and one questioned link, ICIT3355/MH2280(?) on p. 92. These are source-use counts; probable mistyped-CISI joins require separate qualification. The partial derivation-label split above identifies later examples, while the individually named historical post-fix batch and its attempted/failed denominator remain unavailable. [Frozen audit](pdf-2026-10-09-v1/validation-audit-v4.json); [probable joins](pdf-review-response-2026-10-09-v1/join-corrections.json).''')
    rest = rest.replace('The introductory letter, PDF p. 5, instead says', 'The separate undated introductory letter hosted by Jeff Lindsay, PDF p. 5, says')
    rest = rest.replace('Language Log’s 6 March 2025 discussion contains informal chance-match concerns.',
        'Yves Rehbein’s 7 March 2025 reader comment on Language Log quotes a YouTube commenter’s chance-match concern; the parent post is dated 6 March.')
    (OWN / 'REPORT.md').write_text(opening + rest, encoding='utf-8')


def readme():
    text = '''# Package Q: PDF-review corrections

Jar/arrow final tendencies, fish clustering and M-unit order reproduce. The broad lexical panel remains construction-dependent; the frozen clear-origin panel cannot attain significance. Wider field boundaries, historical validation success and physical metrology remain unresolved. Results are Exploratory, based on two AI coding rounds without specialist review.

| Headline result | First | Second | Agreed-only |
|---|---:|---:|---:|
| Frozen final-only fields: clean/conflict/indeterminate | 942/349/1178 | 781/302/1386 | 844/379/1246 |
| Final-or-penultimate fields | 1144/136/1189 | 970/100/1399 | 1040/172/1257 |
| Widened clean shuffle mean | 622.54 | 563.38 | 583.56 |
| M units in O–F–MS order | 288/331 | 226/249 | 288/331 |
| M-order shuffle mean | 58.87% | 68.39% | 58.89% |
| Fish adjacency / shuffle mean | 142/55.72 | 142/55.72 | 135/54.73 |

All widened-clean, M-order and fish tails are **.0005**. The first frozen clean count has **683/942 texts without M**, including **323 C-plus-T only**; its excess largely restates terminal position. Jar and arrow final counts remain **838/1,196** and **192/225**, with **358** and **33** exceptions. [First fields](pdf-review-response-2026-10-09-v1/first/field-corrections.json), [second](pdf-review-response-2026-10-09-v1/second/field-corrections.json), [agreed-only](pdf-review-response-2026-10-09-v1/agreed_only/field-corrections.json); [terminal exceptions](response-2026-10-08-v2/terminal-exceptions.json).

Broad exact matching remains **84/228** full-selection and **83/206** explicit-caption, tails **.0005**. The scorer reads manuscript roles/value bundles; external mapping files are absent from the scoring path, so first/second equality is by construction. Agreed-only removes target coverage and gives **53/123** full and **52/108** caption types. The earlier ten-type panel has **8/10 PU/PATI contexts** used in dictionary-based derivation; all **13** permutations scoring at least nine keep PU, and **0/600** moving it reaches nine. [Frozen panels](pdf-2026-10-09-v1/lexical-caption-sensitivity.json); [census](review/role-pair-census.json).

The frozen clear-origin result **2/5, tail .20**, is the best attainable score after dropping maha from three mahā- types. Both hits use dictionary-derived pāla; one uses reading-supported ASHVA. The full-selection **2/7** and agreed-only **0/1** remain preserved. The partial split excluding **129 derivation labels** yields **5/8**, tail **.0256**, with all five hits requiring PU, PATI or maha. It removes named derivation examples, while their historical reservation and subsequent value fitting remain unresolved. The corrected anchor-only panel gives **0/7 exact** (null mean zero), **2/7 normalized**, tail **.7556**; the numeral-motivation sensitivity gives **4/13 exact**, tail **.4860**. The sources cannot supply a larger independently reserved test. [Lexical corrections](pdf-review-response-2026-10-09-v1/lexical-corrections.json); [source diagnostics](pdf-review-response-2026-10-09-v1/source-diagnostics.json).

Explicit alias matches remain **713/859 attempts and 338 object families**. Six readings on H-271, M-707, M-106 and M-122 have probable mistyped-CISI aliases; excluding them gives **707/859 and 334 families**. Four catalogue-code transcriptions and twelve empty captions are repaired: **718 → 726** attempts have transcriptions. The row-local uncertainty search adds **57 flags**, **103 → 160**, without defining a failed-reading rate. [Join evidence](pdf-review-response-2026-10-09-v1/join-corrections.json); [inventory corrections](pdf-review-response-2026-10-09-v1/reading-corrections.json).

The [derivation successor](pdf-review-response-2026-10-09-v1/value-derivations-v3.json) separates pala/pāla/bala, adds the fish, caru and 2014 predicate anchors, marks ASHVA/GO as reading-supported and fixes their locators. Mayig agreement remains **72 exact singleton, 78/96 overlapping, ten disjoint and eight first-reader missing**, κ **.9217 (n=78)**. Wells/Helsinki overlap is 78, κ **.9109 (n=46)** / **.7193 (n=8)**. The blind second packet is preserved. The first coder saw Table 18 families when coding the 17 caption forms. [Agreement](two-coder-2026-10-09-v1/AGREEMENT.md); [disagreements](two-coder-2026-10-09-v1/DISAGREEMENTS.md).

## Source and file scope

The 259-page manuscript witness, 58 Table 18 labels, 65 drawings, 96 coding targets and [blind packet](../../data/raw/2026-10-08-bonta-review/second-coder-v1/) stay preserved. The source inventory retains **1,200 rows and 859 attempt rows**. The ledger retains **1,021 records**, with versioned source and test corrections. PDF crops, complete captions, corrected inventory rows and per-query predictions remain local raw. [Witness](pdf-2026-10-09-v1/witness-v3.json); [corrected reading index](pdf-review-response-2026-10-09-v1/reading-index-v5.json); [ledger](claims.md).

[REVIEW-PDF.md](REVIEW-PDF.md) and [review-pdf/](review-pdf/) were reused unchanged. Current summaries and the previous ledger are preserved in [history/2026-10-09-before-pdf-review/](history/2026-10-09-before-pdf-review/). [PDF-REVIEW-FILES.json](PDF-REVIEW-FILES.json) lists this phase’s changes; [FILES.json](FILES.json) inventories current contents. Shared registry/index and other contributors’ directories were untouched. [Report](REPORT.md), [protocol](PROTOCOL.md), [retrospective](RETROSPECTIVE.md), [sources](sources.json), [registry proposal](registry-entry.json).

## Repeat from the repository root

System Python, PyMuPDF and Pillow are used. Choose a new output basename within both package trees; scripts refuse existing endpoints. The lexical audit reuses the reviewer’s independent matcher read-only and the pinned dictionary. Repeat the field command for `second` and `agreed_only`.

```powershell
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_review_sources.py --output-dir pdf-review-replay-2026-10-09-02 --render
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_review_lexical.py --output-dir pdf-review-replay-2026-10-09-02
python -B -X utf8 experiments/2026-10-08-bonta-review/pdf_review_fields.py --output-dir pdf-review-replay-2026-10-09-02 --mapping first
python -B -X utf8 experiments/2026-10-08-bonta-review/verify_pdf_review.py --replay pdf-review-replay-2026-10-09-02 --output pdf-review-checks-replay-2026-10-09-02.json
python tools/review_prose.py --path experiments/2026-10-08-bonta-review --no-write
```

Completed replay and preservation checks are recorded in [pdf-review-checks-2026-10-09-v1.json](pdf-review-checks-2026-10-09-v1.json). Earlier PDF and second-coder verifiers remain evidence for their frozen endpoints. Reviewer sampling should repeat the source-origin passages on manuscript pp. 45–47, 55, 67–68, 185–187 and 215–216; terminal rule p. 15; the twelve repaired captions; probable joins on pp. 126, 172, 210–211, 221 and 226; and the partial-split membership. The separate introductory letter’s p. 5 and the manuscript foreword’s p. 5 are distinct documents. Language Log’s chance remark belongs to Yves Rehbein’s **7 March 2025 reader comment**, quoting a YouTube commenter. Kalyanaraman’s substantive content remains unverified after HTTP 403. [Remaining scope](COMPLETION.md).
'''
    (OWN / 'README.md').write_text(text, encoding='utf-8')


def metadata():
    sources = read(HISTORY / 'sources.json')
    for source in sources['sources']:
        if source['id'] == 'LL25':
            source['claim_attribution'] = 'Yves Rehbein, reader comment, 7 March 2025 at 7:56 a.m., quoting YouTube commenter @extremaz9908; not the author’s parent-post claim.'
            source['comment_url'] = source['url'] + '#comment-1628065'
            source['location'] = 'Parent post: 6 March 2025. Chance remark: comment-1628065, 7 March 2025, 7:56 a.m.; retained language-log.html.'
    sources['independent_second_coding']['first_coder_exposure_note'] = 'The first coder compared 17 caption forms with Table 18 families and saw the author’s grouping; the second packet was blind.'
    sources['pdf_review_response'] = {'date': '2026-10-09', 'review': 'REVIEW-PDF.md',
        'review_outputs': 'review-pdf/', 'opened': True, 'new_downloads': 0,
        'source_passages_checked': [15, 45, 46, 47, 55, 67, 68, 113, 183, 185, 186, 187, 215, 216],
        'reading_crops_inspected': 'local raw pdf-review-response-2026-10-09-v1/source-checks/',
        'outputs': 'pdf-review-response-2026-10-09-v1/', 'new_quotations': 0}
    write(OWN / 'sources.json', sources)
    registry = read(HISTORY / 'registry-entry.json')
    registry['outcome'] = ('Jar final 838/1,196; arrow final 192/225, with 358 and 33 exceptions. '
        'Fish adjacency first/second/agreed-only 142/142/135 versus means 55.72/55.72/54.73. '
        'M order 288/331, 226/249 and 288/331 versus shuffle fractions 58.9%, 68.4% and 58.9%; tails .0005. '
        'Widened terminal fields 1,144/136/1,189, 970/100/1,399 and 1,040/172/1,257; clean means 622.54/563.38/583.56, tails .0005. '
        '683/942 frozen first-mapping clean texts lack M. Broad caption lexical score 83/206 is construction-dependent; external mappings are absent from scoring, while agreement-only eligibility gives 52/108. '
        'The frozen clear-origin 2/5 (.20) is its best attainable exact score after blocking three maha readings; both hits use dictionary-derived pāla. '
        'Partial split excludes 129 derivation labels: 5/8 exact, tail .0256, all five requiring PU/PATI/maha. The label/explicit-object closure leaves that result unchanged; no sealed batch is identifiable. '
        'Corrected anchors give 0/7 exact (null mean zero), 2/7 normalized (tail .7556); numeral-motivation sensitivity gives 4/13 exact (tail .4860). '
        'Alias matches 713/859, 338 families; excluding six probable mistyped-CISI readings on four objects gives 707/859, 334 families. '
        'Four code transcriptions and twelve empty captions repaired, 718 to 726 transcribed attempts; row-local unclear flags 103 to 160. '
        'Mayig overlap 78/96, exact singleton 72, disjoint 10, first missing 8; κ .9217 on 78 paired singletons. '
        'Two AI coding rounds without specialist review; first caption-form coding saw Table 18. Earlier ten-panel tail is close to circular: all 13 high-scoring permutations keep PU, none of 600 moving PU reaches nine, eight of ten strings use dictionary-derived PU/PATI; nine observed matches are exact. '
        'Historical ICIT success denominator, wider field boundaries and physical quantity joins remain unavailable. Earlier endpoints and all reviewer files stay frozen.')
    registry['challenge'] = ('Lexical derivation and confirmation are entangled; the frozen clear-origin subset cannot attain significance. '
        'Source-selected non-lexical anchors supply too few lexical types, and unknown later extensions prevent a larger independent sample. '
        'Disputed graphic candidates, informed first caption-form coding, probable mistyped aliases and incomplete source attachments remain. '
        'The historical check batch, rejected attempts and physical quantity joins are absent.')
    registry['remedy'] = ('Registered source corrections, widened terminal compatibility, M-order unit shuffles, attainability and partial derivation-label/object splits; '
        'reused the reviewer’s independent matcher, outputs and source audit without editing them; repaired inventory and source records; '
        'reported conservative join totals and corrected interpretation in a versioned response.')
    registry['retry_when'] = ('Specialist adjudication of disputed signs/aliases; explicit wider field boundaries; a historically reserved batch with pre-fixed values and attempted failures; '
        'or new externally reserved objects under finite acceptance rules. Physical metrology requires independent quantity joins.')
    registry['evidence'] += [(OUT / f).relative_to(ROOT).as_posix() for f in [
        'value-derivations-v3.json', 'reading-corrections.json', 'join-corrections.json',
        'lexical-corrections.json', 'source-diagnostics.json', 'first/field-corrections.json',
        'second/field-corrections.json', 'agreed_only/field-corrections.json', 'ledger-changes.json']]
    registry['evidence'] += ['experiments/2026-10-08-bonta-review/REVIEW-PDF.md',
        'experiments/2026-10-08-bonta-review/pdf-review-checks-2026-10-09-v1.json',
        'experiments/2026-10-08-bonta-review/PDF-REVIEW-FILES.json']
    write(OWN / 'registry-entry.json', registry)


def retrospective():
    old = (HISTORY / 'RETROSPECTIVE.md').read_text(encoding='utf-8')
    text = '''

## PDF-extension review response, 9 October 2026

The reviewer reproduced every earlier number and verified the freeze chain and blind packet. The response reused REVIEW-PDF.md, the independent lexical matcher and reviewer field/derivation/join outputs read-only. Editable summaries and the ledger were preserved before the protocol amendment. New calculations and source rows use pdf-review-response-2026-10-09-v1/ in the owned/local raw trees.

Source derivations differed from the earlier classification. The successor separates pala from dictionary-derived pāla and fitted bala, restores fish, caru and 2014 predicate anchors, and marks ASHVA/GO as reading-supported. It corrects bow and animal locators. The frozen clear-origin panel was uninformative: three maha readings were blocked by construction, so two hits with tail .20 were the best attainable score. Both hits depended on pāla, and one on ASHVA. The current summaries withdraw the earlier absence-of-excess conclusion.

The partial split reproduced the review’s 129-label derivation set and 5/8 exact result, tail .0256. All five matching types require PU, PATI or maha. Literal manuscript aliases and explicit CISI joins close 76 derivation families without changing the scores. The paper’s repeated-confirmation history leaves the split unsealed. The corrected anchor-only test gives 0/7 exact with null mean zero and 2/7 normalized, tail .7556. The broader numeral-motivation sensitivity gives 4/13 exact, tail .4860. Unknown later-extension histories and reserved failures/examples prevent a larger independent test from these sources. The lexical scorer never reads external mappings; agreed-only is an eligibility restriction. Mapping-survival wording was removed.

The field classifier was narrower than manuscript p. 15. Its successor admits a single final/penultimate terminal, preserving other rules. Counts are 1,144/136/1,189, 970/100/1,399 and 1,040/172/1,257 under first/second/agreed-only. Of the frozen 942 first-mapping clean texts, 683 lack M. The separate M-order test gives 288/331, 226/249 and 288/331, against shuffle fractions 58.9%, 68.4% and 58.9%; all tails .0005. Recognized M units are tested independently of clean status, with compounds held whole. The second mapping’s ambiguous ovals reduce its eligible denominator. Repeated-O prohibition remains an operational assumption rather than an explicit source rule.

Six probable mistyped-CISI joins on four objects remain flagged instead of being replaced through ICIT numbers. Exclusion changes 713/859 attempts and 338 families to 707/859 and 334 families. Crops confirm the twelve empty-caption and four catalogue-code defects; transcription coverage changes 718 to 726. The registered row-local doubtful/questionable/question-mark search adds 57 flags (103 to 160), and finds 69 keyword-bearing attempts. The review’s 94/60 does not reproduce on these source_text fields; the mismatch and row IDs are preserved in source-diagnostics.json and local source-diagnostic-rows.json. A keyword flag can concern an alias or an accepted unattested compound, and supplies no failure count.

A diagnostic read initially failed on an invalid regular expression; it wrote no output and was replaced with a simpler source-caption inspection. All substantive calculations completed. Language Log attribution was corrected to Yves Rehbein’s 7 March reader comment quoting a YouTube commenter. The separate letter/manuscript p. 5 references are named. Registry prose was rewritten with spaces. The first coder’s Table 18 exposure for 17 caption forms is now explicit, while the second packet remains blind. Current ledger annotations and the file inventory record the corrections; earlier retrospective accounts remain historical.
'''
    (OWN / 'RETROSPECTIVE.md').write_text(old + text, encoding='utf-8')
    completion = '''# Completion scope after PDF review, 9 October 2026

The 259-page witness, 96-target packet, frozen mappings and earlier outcomes stay preserved. Source corrections and calculations are in pdf-review-response-2026-10-09-v1/. All requested review-response calculations are complete: value-level origins, lexical attainability, partial derivation-label/object split, corrected anchor panels, widened terminal compatibility, M-order tests under each mapping, probable-join exclusions and inventory repairs.

The inventory retains 1,200 source rows and 859 attempt rows; 726 attempts now carry a transcription. Its 160 uncertainty flags include alias qualification and accepted unattested compounds. The extraction census is separate from the paper’s unknown historical attempt/success denominator. Twelve repaired captions and four removed catalogue-code transcriptions are recorded in the successor; unlabelled/damaged figures and other source attachments still need manual adjudication.

The partial split separates 129 named derivation labels; its five exact hits all require PU/PATI/maha. No sealed historical batch or larger independent value/readings split can be reconstructed. Later-extension discovery histories and rejected examples remain absent. Wider Table 19 fields, contextual fish boundaries, finite phonological/multiword acceptance and independent quantity joins remain unresolved. Specialist adjudication is needed for disputed candidates, stroke heights and probable mistyped aliases. No disputed sign or object identity was selected by its statistical result.

The second packet remains blind; the first coder saw Table 18 families for the 17 caption forms. Shared registry/index and other contributors’ files were untouched. PDF-REVIEW-FILES.json inventories this phase, FILES.json the current tree, and pdf-review-checks-2026-10-09-v1.json records preservation and replay checks. Historical reviews/verifiers apply to their frozen outputs.
'''
    (OWN / 'COMPLETION.md').write_text(completion, encoding='utf-8')


if __name__ == '__main__':
    ledger(); report(); readme(); metadata(); retrospective()
    print('Applied PDF-review source and interpretation corrections.')
