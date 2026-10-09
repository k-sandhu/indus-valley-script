"""Apply the source-checked review response to the preserved original ledger.

This curation command rebuilds the current ledger and its itemized audit. It reads
the immutable pre-response snapshot, rather than applying changes repeatedly.
The prose and source annotations below were checked against the local witnesses.
"""
from pathlib import Path
import collections, hashlib, json

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-08-bonta-review'
BASE = OWN / 'history/2026-10-08-before-review-response'
SAMPLED = {2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 20, 21, 22,
           23, 24, 25, 26, 27, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
           44, 45, 46, 47, 48, 49, 50, 53, 54, 71, 72, 90, 101, 104, 123, 124, 125}
# The review's 30 fair plus 22 correction rows, including Q010/Q011/Q013.
REQUIRED = {3, 5, 6, 10, 11, 13, 15, 16, 18, 20, 21, 22, 24, 25, 34, 35, 36, 41, 42, 44, 53, 72}

def write(name, data):
    (OWN / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    original = [json.loads(l) for l in (BASE / 'claims.jsonl').read_text(encoding='utf-8').splitlines()]
    claims = {int(r['id'][1:]): dict(r) for r in original}
    reasons = {}
    checked = {}
    def amend(number, reason, **fields):
        claims[number].update(fields)
        reasons.setdefault(number, []).append(reason)
    def locate(number, witness, observation):
        checked[number] = {'checked_against': witness, 'source_check': observation}

    amend(1, 'The original introduction range does not contain the full script-model claim.',
          source_location='Sections III–IV, segments 33–35, 54 and 76–78',
          offered_evidence='He proposes Indo-Aryan in segment 54 and CV/root signs with logograms in segments 76–78; segment 33 discusses a logosyllabic inventory.')
    amend(3, 'No sign-crowding argument appears in the cited passage.', source_location='0:06:26–0:08:34; B24 segment 15',
          offered_evidence='A seal and its mirrored impression are compared; he uses the impression as the canonical right-to-left display. The grounds for direction are left largely unstated.')
    amend(4, 'The cited segments belong to Section III; correct the section label while retaining the claim.',
          source_location='Section III, segments 15–33')
    amend(5, 'The passage illustrates the distinction through English and mathematical examples.',
          source_location='0:56:37–0:59:59',
          offered_evidence='English weights, prices, dates and mathematical formulas illustrate abbreviation, changed spoken order and mixed notation. He announces application to Harappan texts at 0:59:44.')
    amend(6, 'The field order precedes the original range; its paper definition is segment 16.',
          source_location='0:36:28–0:39:58; B24 segments 16–20',
          offered_evidence='Illustrated sequences show P–M–C–T and missing fields; P is explained as a positional convenience at 0:39:16.')
    amend(7, 'Use Bonta’s own graphic description, rather than the package’s mortar/pestle gloss.',
          paraphrase='His M-field model has three optional components: an oval subfield, a fish subfield and an MS pair of a container with a central stick beside three long bars.',
          source_location='0:02:10–0:10:38; B24 segment 20')
    amend(10, 'No within-oval ordering restriction is stated.', source_location='Section III, segment 20; L06 0:01:27–0:02:31',
          paraphrase='The oval subfield has at most two non-repeating members of a three-sign inventory.',
          offered_evidence='The textual definition gives the inventory size and maximum count; the lecture supplies non-repetition. The available manuscript text omits the glyphs.')
    amend(11, 'The original range covers fish tables; locate the MS definition and interpretation separately.',
          source_location='Section III, segment 20 and segments 50–53; L04 0:03:34–0:04:15',
          paraphrase='He treats the container-with-stick and three-long-bars pairing as an MS construction, usually concluding an M field.',
          offered_evidence='The recurrent pair is defined in segment 20 and illustrated in Table 11; segments 52–53 propose mātra from its placement and the suggested tra value.')
    amend(12, 'The original range supplies M-field examples, while the terminal argument is elsewhere.',
          source_location='Section III, segment 14; segments 55–60',
          offered_evidence='Segment 14 describes final or penultimate placement, including ends of embedded sequences; segments 55–60 argue for predicates from recurring terminal contexts.')
    amend(13, 'Separate the tentative lecture proposal from the paper’s case-like interpretation.',
          source_location='0:04:17–0:13:31',
          paraphrase='He doubts that the juncture signs are case endings and tentatively suggests honorific or benefactive functions; gender and number are additional possibilities.',
          quotation='at a very very tentative guess',
          offered_evidence='He compares juncture combinations with P signs and reports exceptions to their mostly contrasting distributions. At 0:09:42 he doubts case endings; at 0:10:04 he labels his alternative tentative.')
    amend(15, 'The abandoned method compared positional CV frequencies, rather than searching exhaustively for readings.',
          source_location='Section III, segments 34–35',
          paraphrase='He compared initial, medial and final CV-syllable frequencies in Monier-Williams and the Cologne Tamil lexicon with deduplicated Indus sign dossiers. Both comparisons largely failed, apart from a handful of signs.',
          offered_evidence='He describes substring-frequency queries and dossiers for signs with roughly more than 20 occurrences; he attributes the failure partly to stylized inscriptions.')
    amend(16, 'Replace a claim absent from the cited passage with its actual concatenation argument.',
          source_location='0:10:25–0:15:04; B24 Table 6, segments 38–40',
          paraphrase='Recurring shorter C-field sequences are concatenated in a longer C field, which he interprets as evidence for noun compounds.',
          offered_evidence='Table 6 compares autonomous C sequences with their combination, especially MH4335; the passage supplies no reordering or suffix contrast.')
    amend(18, 'Include the historical hedge beside the categorical statement about attested Dravidian.',
          source_location='0:28:36–0:30:01; B24 segment 41',
          paraphrase='He categorically says attested Dravidian lacks noun compounding, while allowing that a Harappan-period ancestor could have had it. The paper makes a weaker comparison about extensive multi-noun name compounds.',
          quotation='do not allow noun compounding in any form',
          offered_evidence='He compares inferred compounding, gemination and prefixing with Indo-Aryan; the spoken hedge allows earlier typological change. Krishnamurti’s chapter summary documents noun-plus-noun compounds.')
    amend(20, 'Locate the weight-series comparison in the paper, alongside the lecture’s entering-wedge argument.',
          source_location='0:01:27–0:04:58; B24 segments 20–24',
          offered_evidence='The lecture summarizes limited non-repeating fish/oval combinations and the invariant MS pair. Segment 23 separately compares the inventory sizes with Marshall’s weight series.')
    amend(19, 'The cited typology/anchor segments belong to Section III; correct the section label.',
          source_location='Section III, segments 42–54')
    amend(21, 'Credit Marshall’s series and remove the invented ordering argument.',
          paraphrase='He rates it very likely that seven fish signs correspond to Marshall’s 1, 2, 4, 8, 16, 32, 64 series and three oval signs to 160, 320, 640.',
          offered_evidence='Matching inventory sizes and the absence of geminated fish signs motivate the hypothesis; he gives no sign-by-sign assignment to weighed objects.')
    amend(22, 'Extend the range to cover the protector homophone.', source_location='0:08:52–0:13:53; B24 segments 47–50, 66–67',
          offered_evidence='Grain-staff graphology, numeral adjacency and the Sanskrit pala weight motivate the first value; at 0:12:03–0:13:53 he adds pāla, protector, for non-metrological contexts.')
    amend(24, 'Specify the bow/bowman distribution and distinguish the two glyphs.', source_location='0:18:48–0:24:42; B24 segments 44–46, 54',
          offered_evidence='At 0:19:30–0:21:58 he compares bow and bowman substitutions and asset-like contexts; the following Sanskrit bow/wealth comparison motivates near-related values.')
    amend(25, 'Lecture 7 has three lexical lists and a fourth positional criterion; TRA belongs to a later paper check.',
          source_location='0:05:28–0:11:55; B24 segments 69–70',
          paraphrase='He obtains the proposed PU/bhu value by intersecting words ending in dhana, ma and pala, then requiring that the shared initial element also be common as a final or suffix element.',
          offered_evidence='Three Cologne dictionary substring lists supply candidate X values; the fourth condition is final/suffix use. The same contexts helped choose PU and later appear in the tested panel.')
    amend(26, 'Preserve the ambiguous caption wording and distinguish success counts from attempted counts.',
          quotation='nothing that was not readable, nothing that that contradicted my results',
          offered_evidence='His research-history account reports a dozen or fifteen readable inscriptions and one value withdrawn. The caption permits both no unreadable attempts and no readable counterexample; no attempted list resolves the ambiguity.')
    amend(28, 'Context checks are part of value construction; independence is unestablished.',
          paraphrase='He strengthens proposed values by repeated lexical cross-checking in different contexts, yielding recognizable Sanskrit names, titles and compounds.',
          offered_evidence='PU and PATI are chosen by dictionary searches across their contexts; segment 76 describes trial and error and abandoned candidates.')
    amend(29, 'Include the text introducing the stated sign count.', source_location='Section IV introduction and Table 18, segments 77–81',
          offered_evidence='He states 55 signs in segment 77; Table 18 adds certain logograms and ligatures. He also identifies omitted numerical compounds and unresolved signs.')
    amend(30, 'Replace an uncounted quantitative paraphrase with the directly observable source structure.',
          source_location='Section IV, segments 82–216',
          paraphrase='He offers a long catalogue of complete or partial readings as names, titles and compounds, arranged under individual proposed sign values.',
          offered_evidence='Segment 82 introduces the catalogue and segments 83–84 explain source labels, alternate readings and the format. The package’s occurrence parser supplies a separate count.')
    amend(32, 'Locate the proposed predicate and nominal values precisely.', source_location='Segments 55–65; Table 18, segment 81',
          offered_evidence='He argues for AS from terminal distributions and possessive copula analogies, ISH from valuation and arrow homophony, and ASTI from modified-jar distributions and property vocabulary.')
    amend(34, 'State the strength of his asset/metrology interpretation.',
          paraphrase='He calls the short seal examples sufficient to show asset or metrological notations and says they cannot reasonably be interpreted otherwise.',
          quotation='necessary and sufficient',
          offered_evidence='Numeral-like strokes beside a staff sign on seals with bosses and animal figures are his stated evidence; 0:03:13–0:03:36 gives the categorical interpretation.')
    amend(35, 'Include the temple-as-bank analogy and narrow the manuscript range.', source_location='0:04:00–0:16:48; B24 segments 241–243',
          offered_evidence='His proposed names and amounts are joined to analogies with temples as depositories/lenders and later donative epigraphy; 0:16:28–0:16:48 describes both functions.')
    amend(36, 'Distinguish the examples from the later sacrificial-vocabulary explanation.', source_location='0:16:48–0:18:10; 0:30:10–0:30:32',
          offered_evidence='The first passage gives proposed readings of MH4470 and MH4603; 0:30:10 separately links chu to a rice/grain offering or its preparation pot.')
    amend(41, 'Record the categorical language assertion and its non-exclusive prefix qualification.',
          paraphrase='He asserts that the language has prepositions beyond reasonable doubt, on his readings of ati, para, vi and related elements. He says the signs also occur elsewhere within words.',
          quotation='beyond any reasonable doubt',
          offered_evidence='Selected readings suggest prepositional values. At 0:11:00 he rejects strictly prefix-only status; at 0:14:10 he asserts the language-level conclusion.')
    amend(42, 'His earlier-form proposal is explicitly a possibility alongside approximate spelling.', source_location='0:19:26–0:24:00',
          paraphrase='He proposes two possibilities for the suggested atima spelling: an approximate spelling of ātman or a phonetic rendering of an earlier form, with compensatory lengthening after vowel loss.',
          offered_evidence='He offers the earlier-form etymology tentatively at 0:21:35, describes the sound-change mechanism and leaves the judgement to the listener at 0:23:40.')
    amend(44, 'Extend the source range through the modern-genitive descent argument.', source_location='0:34:00–0:40:05',
          paraphrase='He proposes a non-case ka affix with possessive/genitive-like uses and suggests it explains velar-related genitives in several modern Indo-Aryan languages.',
          offered_evidence='Selected readings such as Satyadevaka motivate possessive ka; later comparisons with Hindi, Sinhala, Marathi and Sindhi extend the claim to descent.')
    for n in range(45, 51):
        amend(n, 'Replace the undefined E1 identifier with the registered source-review task.', test_ids=['C1-R'])
    amend(51, 'Recheck the early chronology through the available primary retrospective, rather than an unretained public-page passage.',
          source_id='B24', source_location='Foreword, segment 3; earlier values restated and withdrawn in segments 54–65',
          test_ids=['C1-R'],
          paraphrase='He reports developing metrological field analysis in the 1990s and arguing for Indo-Aryan by 2010, before his later expanded value system.',
          offered_evidence='The 2024 author retrospective dates the field analysis and initial language argument; it describes a 2014 monograph and later methodological failure. This is his retrospective chronology, rather than a new direct collation of the 2010 witness.')
    amend(52, 'Separate second-edition changes from the initial MH-to-ICIT history.', source_location='Second-edition foreword, segments 6–7',
          test_ids=['V1', 'C1-R'],
          paraphrase='He describes the second edition as nearly identical to the first, with expanded fish/M-field discussion, one corrected sign and affected readings, and an added KARAPALA ligature.',
          offered_evidence='The second-edition foreword identifies these changes; first-edition full text is unavailable for a line-by-line collation.')
    amend(53, 'Invalidated values is stronger and more precise than small modifications.',
          paraphrase='The undated letter says the later ICIT cross-check invalidated a couple of previously proposed sign values.',
          quotation='invalidated only a couple of previously-proposed sign values',
          offered_evidence='PDF p. 5 gives the author’s account; Lecture 7 and the first foreword each report one withdrawn value. The witnesses give differing correction counts.')

    labels = ['kA','dhU','nI','PA','PU','mA','jA','sA','SU1','SU2','rA','vI','hu','ANa','(e)ka','ATI',
              'PAla','DAna1','DAna2','p(a)ra','j(a)ya','var(a)','mAn(a)','Sar(a)','S(u)ri','t(a)ya','sA(ha)',
              'nATa','mIn(a)','vAsu','cAru','mANA','kara1','kAra2','pra','trA','RASHTRA','LAKSH(A)',
              'SENA','ARYA','DHAR(A)','SAM','RAKSH(a)','RAJA(n)','DHANYA','DEVA','PATI','ASHVA','GO',
              'AS','ISH','ASTI','ŚRIPATI/SURIPATI','ŚRIPATIDEVA','PAKA','ŚRIPALA','ARYAKA','KARAPALA']
    for n, label in zip(range(55, 113), labels):
        old = claims[n]['paraphrase']
        prefix = old.split(' to the illustrated Table 18 entry labelled ')[0]
        amend(n, 'Use the actual Table 18 label and restrict offered evidence to the table checked here.',
              paraphrase=prefix + f' to the Table 18 entry labelled {label}.',
              offered_evidence='Table 18 explicitly lists this proposed value; the available page text omits its glyph. This audit checks the table, without certifying all later readings offered for the sign.')
    # The label var(a) has no separately bracketed list; explain the expansion.
    amend(76, 'var(a) denotes optional final a, rather than a separate explicit bracket list.',
          paraphrase='He lists var(a), interpreted here as var/vara, for the Table 18 entry with that label.')
    # These are proposed roles; Table 18 labels are retained literally to avoid DAna/DHANA confusion.
    readings = {
        113: ('mātra', 'The MS discussion treats the pair as a measure/amount word and also mentions a masculine Brahmin sense.', 'Segments 52–53; introductory letter PDF p. 2'),
        114: ('dhanapāla', 'He uses the bow-related dhana and staff-related pāla values to propose treasurer or an attested name.', 'Table 13, segments 67–68; MH4624/H-467 and MH2449/M-320'),
        115: ('bhūpāla', 'The unknown square sign is assigned bhū through dictionary-based cross-checking; this pair is one of its construction contexts.', 'Table 14, segments 69–70; MH4650/M-1592'),
        116: ('bhūma', 'He treats the same unknown-sign-plus-ma contexts as supporting the dictionary-derived bhū value.', 'Table 15, segment 70; MH1056, MH1310 and MH4447'),
        117: ('bhūdhana', 'He treats the unknown-sign-plus-dhana contexts as supporting the dictionary-derived bhū value.', 'Table 15, segment 70; MH4260 and MH2638'),
        118: ('putra', 'bhūtra is unattested; he prefers adding pu to the PU alternatives. Segments 95–96 question the three cited stroke shapes, explicitly calling the short-stroke reading doubtful.', 'Table 16, segments 71–72; catalogue notes 95–96: MH2109/M-1688, MH2348/M-958, MH2564/M-979'),
        119: ('dhanapati', 'He selects pati by dictionary searches against known preceding roles and standalone-title use; this pair helps construct the value.', 'Table 17, segments 73–75'),
        120: ('palapati/pālapati or balapati', 'He notes that palapati and pālapati are absent from Sanskrit dictionaries, cites a surname, and adds the attested balapati reading by allowing bala.', 'Table 17 discussion, segment 75'),
        121: ('bhūpati', 'He selects pati by dictionary searches including this PU context; he calls bhūpati an attested monarch/prince term and name.', 'Table 17, segments 74–75; MH8104'),
        122: ('dhanapālapati', 'He includes this sequence among the pati construction contexts; the package’s exact and normalized whole-headword tests find no match for it.', 'Table 17, segments 73–75; MH1400/M-314 line 3')}
    for n, (reading, evidence, location) in readings.items():
        amend(n, 'Replace generic context evidence with the particular reading and its construction history.',
              paraphrase=f'He proposes the reading {reading} for the retained role sequence.',
              offered_evidence=evidence, source_location=location)
    amend(126, 'Narrow the range to the complete patterned interpretation.', source_location='Section VII, segments 231–249, especially 243 and 247–249')

    # Every original row was checked; record exactly where and what was checked.
    # Text-only sign-value checks cannot certify the absent sign glyphs.
    for n, row in claims.items():
        locate(n, row['source_id'] + ': ' + row['source_location'],
               'Proposed table value and printed label checked in the complete segments 78–81; glyph identity remains unresolved.' if 55 <= n <= 112 else
               'Specific proposed reading, context and stated uncertainty checked in segments 52–53 or 67–75 and, for PU-TRA, 95–96.' if 113 <= n <= 122 else
               'Paraphrase, strength, location and offered evidence checked against the caption blocks or page-text segments listed; reviewer observations reused for the sampled rows.')
    assert len(SAMPLED) == 52 and len(set(claims) - SAMPLED) == 74
    assert REQUIRED.issubset(reasons)
    additions = [
        {'id': 'Q127', 'source_id': 'L04', 'source_location': '0:45:40–0:46:24', 'type': 'corpus-distributional',
         'paraphrase': 'He says the jar always occurs in terminal context, apart from a couple of Middle Eastern seals that might represent another language.',
         'quotation': 'always always always', 'offered_evidence': 'His summary of extreme T-context rigidity; the caption garbles terminal as tran. The surrounding T-field discussion establishes the intended label.',
         'testable_here': True, 'test_ids': ['D1', 'D1-R']},
        {'id': 'Q128', 'source_id': 'B24', 'source_location': 'Segments 19–20 and 241–242', 'type': 'segmentation or structure',
         'paraphrase': 'The paper suggests a noun-case or case-like relationship for juncture signs, possibly genitive/dative, while also allowing an honorific sense.',
         'quotation': None, 'offered_evidence': 'Juncture position and the proposed relations between assets and a named recipient; this paper interpretation differs in emphasis from the tentative Lecture 9 alternatives.',
         'testable_here': True, 'test_ids': ['D1', 'D3']},
        {'id': 'Q129', 'source_id': 'L09', 'source_location': '0:35:13–0:35:54', 'type': 'corpus-distributional',
         'paraphrase': 'He says the arrow occurs outside the terminal environment only once or twice, then revises that to a handful of times.',
         'quotation': None, 'offered_evidence': 'A spoken summary accompanying the proposed ISH/ĪŚ value; the positional exceptions are counted separately from unresolved T-field membership.',
         'testable_here': True, 'test_ids': ['D1', 'D1-R']},
        {'id': 'Q130', 'source_id': 'B24', 'source_location': 'Segments 71–72 and 95–96', 'type': 'method',
         'paraphrase': 'The PU-TRA context prompts him to prefer polyvalent PU, including pu, over an unattested earlier bhūtra form; the detailed catalogue notes express doubts about these stroke identities.',
         'quotation': None, 'offered_evidence': 'He contrasts unattested bhūtra with attested putra and uses the latter to broaden PU. The catalogue notes distinguish tall and short strokes.',
         'testable_here': True, 'test_ids': ['L1', 'L1-R']}]
    for row in additions:
        row.update({'assessment_status': 'Exploratory', 'graphic_identity': None,
                    'note': 'All sounds/meanings in this ledger are Bonta’s proposals.'})
    final = [claims[n] for n in sorted(claims)] + additions
    (OWN / 'claims.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in final), encoding='utf-8')
    audit_rows = []
    for before in original:
        n = int(before['id'][1:])
        after = claims[n]
        delta = {k: {'before': before.get(k), 'after': after.get(k)} for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)}
        audit_rows.append({'id': before['id'], 'reviewer_sample': n in SAMPLED, 'changed': bool(delta),
                           **checked[n], 'reasons': reasons.get(n, ['Source check retained the original wording.']),
                           'changed_fields': delta})
    counts = {'original_rows_checked': 126, 'reviewer_sample_rows_checked': 52, 'outside_sample_rows_checked': 74,
              'reviewer_sample_rows_changed': sum(x['changed'] for x in audit_rows if x['reviewer_sample']),
              'outside_sample_rows_changed': sum(x['changed'] for x in audit_rows if not x['reviewer_sample']),
              'required_correction_rows_changed': len(REQUIRED), 'new_rows': len(additions), 'current_rows': len(final),
              'table_evidence_narrowed_rows': 58, 'reading_evidence_specific_rows': 10,
              'outside_sample_table_rows_changed': sum(x['changed'] and not x['reviewer_sample'] and 55 <= int(x['id'][1:]) <= 112 for x in audit_rows),
              'outside_sample_reading_rows_changed': sum(x['changed'] and not x['reviewer_sample'] and 113 <= int(x['id'][1:]) <= 122 for x in audit_rows),
              'outside_sample_other_rows_changed': sum(x['changed'] and not x['reviewer_sample'] and not 55 <= int(x['id'][1:]) <= 122 for x in audit_rows)}
    write('claim-source-audit-2026-10-08-v2.json', {'status': 'Exploratory', 'date': '2026-10-08',
        'baseline': (BASE / 'claims.jsonl').relative_to(ROOT).as_posix(),
        'baseline_sha256': hashlib.sha256((BASE / 'claims.jsonl').read_bytes()).hexdigest(),
        'counts': counts, 'scope': 'All existing records checked, including 74 outside the reviewer sample. This checks the scoped ledger; the full manuscript reading inventory remains incomplete.',
        'source_limitations': 'Machine captions remain unchecked against audio; page segments are zero-based form-feed indices, without certified printed-page numbers; full manuscript glyphs are missing.',
        'records': audit_rows, 'added_ids': [r['id'] for r in additions]})
    coverage = json.loads((BASE / 'ledger-coverage.json').read_text(encoding='utf-8'))
    coverage.update({'claim_records': len(final), 'by_type': dict(collections.Counter(r['type'] for r in final)),
                     'review_response_audit': counts, 'audit_file': 'claim-source-audit-2026-10-08-v2.json'})
    coverage['missing'] = 'No exhaustive adjudication of every individual Section IV reading, lecture background assertion, historical etymology or missing graphic example. All 126 existing ledger rows have now been source-checked; captions remain unchecked against audio.'
    write('ledger-coverage.json', coverage)
    lines = ['# Bonta claim ledger', '',
             'Revised 8 October 2026 after the source review. All 126 original rows were checked; four rows were added. '
             'The [itemized audit](claim-source-audit-2026-10-08-v2.json) preserves the original wording, every changed field and sample membership. '
             'This scoped ledger contains proposed values and interpretations. Full reading and glyph coverage remains incomplete.', '',
             '| ID | Source location | Type | Claim | Offered evidence | Quotation | Tests |',
             '|---|---|---|---|---|---|---|']
    for r in final:
        cells = [r['id'], r['source_id'] + ': ' + r['source_location'], r['type'], r['paraphrase'],
                 r['offered_evidence'], r['quotation'] or '', ', '.join(r['test_ids'])]
        lines.append('| ' + ' | '.join(str(c).replace('|', '\\|').replace('\n', ' ') for c in cells) + ' |')
    (OWN / 'claims.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(counts, indent=2))

if __name__ == '__main__':
    main()
