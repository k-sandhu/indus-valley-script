"""Build authored source/claim annotations and reading locators, not source payloads.

The manual claim list is deliberately separated from raw caption/page text.
Generated top-level files refuse replacement. Review annotations before reuse.
"""
from pathlib import Path
import argparse, collections, hashlib, json, re

ROOT=Path(__file__).resolve().parents[2]
OWN=Path(__file__).resolve().parent
RAW=ROOT/'data/raw/2026-10-08-bonta-review'
REPLACE=False

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):
    if p.exists() and not REPLACE:raise FileExistsError(p)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    global REPLACE
    ap=argparse.ArgumentParser()
    ap.add_argument('--replace-author-annotations',action='store_true',help='Refresh authored top-level annotations only; never numerical endpoints')
    REPLACE=ap.parse_args().replace_author_annotations
    first=read(ROOT/'research/literature/2026-10-08-bonta-first-pass/sources.json')
    sources=[]
    def source(i,title,author,year,venue,url,access,location=None,licence=None):
        sources.append(dict(id=i,title=title,authors=author,year=year,venue=venue,url=url,
          access=access,opened=access.startswith('Opened'),location=location,licence=licence,
          access_date_local='2026-10-08',short_quotation=None))
    for f in sorted((RAW/'captions').glob('*.txt')):
        t=f.read_text(encoding='utf-8');h=dict(re.findall(r'^([a-z_]+): (.*)$',t[:3000],re.M))
        n=int(f.name[:2])
        source(f'L{n:02}',h['title'],'Steven C. Bonta',2025,'YouTube lecture',h['url'],
          'Opened supplied auto-generated captions; selected substantive passages inspected; video images not reviewed',
          f.relative_to(ROOT).as_posix())
        sources[-1].update(publish_date=h['publish_date'],length_seconds=int(h['length_seconds']),
          sha256=hashlib.sha256(f.read_bytes()).hexdigest(),caption_errors='Names, proposed Sanskrit forms and sign descriptions require manuscript corroboration')
    title='A Partial Decipherment of the Indus Valley Script: Proposed Phonetic and Logographic Values for Selected Indus Signs and Readings of Indus Texts'
    source('B24',title+' (2nd ed.)','Steven C. Bonta',2024,'Author-posted manuscript',first['sources'][1]['url'],
      'Opened supplied public-page text; glyphs/figures absent; full manuscript PDF unavailable',
      'data/raw/2026-10-08-bonta-review/papers/bonta-2024-partial-decipherment-2nd-ed.page-text.txt')
    source('B23',title,'Steven C. Bonta',2023,'Author-posted manuscript',first['sources'][2]['url'],
      'First-pass public-page identification reused; this session direct download failed HTTP 403; full edition comparison unavailable')
    source('B23-requested','Unresolved requested Academia identifier 105134798','Steven C. Bonta (requested attribution)',2023,'Unresolved',
      'https://www.academia.edu/105134798','Failed direct download HTTP 403; title and identity not verified')
    source('B10','The Indus Valley Script: A New Interpretation','Steven C. Bonta',2010,'Penn State Altoona manuscript; current 2024 bibliography describes a 2014 Epigraphic Society publication',
      'https://www.academia.edu/8691385/The_Indus_Valley_Script_A_New_Interpretation',
      'Opened public page through web reader; direct HTTP download failed 403; title page dated 2010',
      'Title page and distributional/method discussion')
    source('B10-alt','The Indus Valley Script: A New Interpretation (alternate requested identifier)','Steven C. Bonta',2010,'Unresolved duplicate page',
      'https://www.academia.edu/8691466','Failed web open and HTTP 403 download')
    source('B15-wedge',"Decipherment of the Indus Valley Script: In Search of an 'Entering Wedge'",'Steven C. Bonta',2015,'Conference draft',
      'https://www.academia.edu/12412747','Search snippet/profile listing only; web open failed; HTTP download failed 403; draft not used for substantive argument')
    source('B15-eval',"'Decipherment' of the Indus Valley script: Expectations and Outcomes",'Steven C. Bonta',2015,'Conference draft, May 2015',
      'https://www.academia.edu/12412722/_Decipherment_of_the_Indus_Valley_script_Expectations_and_Outcomes',
      'Opened public page through web reader; draft marked not for citation; identification only; HTTP download failed 403')
    source('B24-aror','Towards a Partial Decipherment of the Indus Script: An introduction to methodology, language, and reading','Steven C. Bonta',2024,'Aror University presentation, April 2024',first['sources'][3]['url'],
      'First-pass public-page text identification reused; draft not for citation; identification only')
    source('B-letter','Introductory letter about the partial decipherment','Steven C. Bonta',None,'Undated six-page author letter hosted by Jeff Lindsay',
      'https://www.jefflindsay.com/Bonta-introductory-letter.pdf','Opened PDF text and rendered pages 1–4; pages 2 and 4 preserve six graphic roles',
      'PDF pp. 2, 4–6',licence='No reuse licence established; local only')
    source('IMSC15','Annual Report 2014–2015','The Institute of Mathematical Sciences',2015,'Institutional annual report',
      'https://www.imsc.res.in/annrep/Archive/2015.pdf','Opened downloaded PDF and extracted programme/participant pages',
      'PDF pp. 91–92, printed pp. 83–84, section 4.1.1')
    source('B-video23','Three-hour 2023 presentation (requested video; title unverified in this session)','Steven C. Bonta',2023,'YouTube',
      'https://www.youtube.com/watch?v=rOZ21f3DKs4','Failed web open; linked by Language Log comment; video/captions not reviewed')
    source('B-videoY','Bonta hosts Yajnadevam (requested video; title/date unverified)','Steven C. Bonta and Yajnadevam',None,'YouTube',
      'https://www.youtube.com/watch?v=A-M8IoAlaGI','Failed web open; no source content reviewed')
    source('K24','Interpretation is not decipherment','S. Kalyanaraman',2024,'Author-posted response, 13 January 2024',
      'https://www.academia.edu/113408961/Interpretation_is_not_decipherment','Opened public page through web reader; direct download failed HTTP 403',
      'Opening response and discussion of stroke/numerical interpretation')
    source('LL25','Decipherment of the Indus script: new angles and approaches','Victor Mair; comments by Yves Rehbein and Martin Schwartz',2025,'Language Log, 6 March 2025',
      'https://languagelog.ldc.upenn.edu/nll/?p=68508','Opened public post and comments; HTML downloaded',
      'Comments dated 7 March 2025: Yves Rehbein 7:56 a.m.; Martin Schwartz 4:55 p.m.')
    source('Elst23','Requested November 2023 X response; post not located','Koenraad Elst (requested attribution)',2023,'X',
      None,'Failed searches; no exact post recovered or verified')
    source('Muk19','Interrogating Indus inscriptions to unravel their mechanisms of meaning conveyance','Bahata Ansumali Mukhopadhyay',2019,'Palgrave Communications 5, 73; DOI 10.1057/s41599-019-0274-1',
      'https://www.nature.com/articles/s41599-019-0274-1','Opened full publisher article through web reader and downloaded HTML',
      'Sections on numerical/metrological signs, functional classes and references')
    source('Rao18','The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor','Rajesh P. N. Rao',2018,
      'In Walking with the Unicorn, Archaeopress, pp. 518–525',
      'https://www.harappa.com/sites/default/files/pdf/The-Indus-Script.pdf','Opened downloaded PDF text',
      'Excerpt PDF pp. 7, 11; printed pp. 518, 522')
    source('Seng23','Fish Symbolism in Indus Valley Epigraphy and Protohistoric Accounts','Shamashis Sengupta',2023,
      'Studia Orientalia Electronica 11(1), pp. 86–102; DOI 10.23993/store.110917',
      'https://journal.fi/store/article/download/110917/88837','Opened downloaded PDF text; article page initially returned a bot challenge',
      'PDF p. 5, printed p. 90; bibliography p. 100',licence='CC BY-NC-SA 4.0 stated on first page')
    source('Khanna25','A Computational Analysis of the Indus Script: Identifying Sign Functions in Logo-Syllabic Writing Systems','Ruhan Khanna and Louie Merriam',2025,
      'International Journal of Computer Applications 187(64), pp. 19–22; DOI 10.5120/ijca2025926075',
      'https://www.ijcaonline.org/archives/volume187/number64/a-computational-analysis-of-the-indus-script-identifying-sign-functions-in-logo-syllabic-writing-systems/',
      'Opened publisher abstract, metadata and references; full paper not inspected', 'Reference 7 cites Bonta 2010')
    source('Y24','A cryptanalytic decipherment of the Indus script','yajnadevam',2024,'Author manuscript compiled 13 November 2024; peer-review status unverified',
      'https://rarebooksocietyofindia.org/book_archive/A_cryptanalytic_decipherment_of_the_Indu.pdf','Opened downloaded PDF text',
      'PDF pp. 1, 11, 26, 94')
    source('K03','The Dravidian Languages: Nominals: nouns, pronouns, numerals and time and place adverbs','Bhadriraju Krishnamurti',2003,
      'Cambridge University Press, chapter 6, pp. 205–276; DOI 10.1017/CBO9780511486876.008',first['sources'][4]['url'],
      'Opened publisher chapter summary; full chapter not acquired', 'Summary: noun+noun compounds and reconstructed kannir')
    source('MD03','Decipherment','Anna Morpurgo Davies',2003,'In International Encyclopedia of Linguistics, 2nd ed., vol. 1, Oxford University Press, pp. 417–422',
      'https://www.ling-phil.ox.ac.uk/files/amd_decipherment_encyclopedia_of_linguistics_v._i_2nd_ed_2003.pdf',
      'Opened scanned PDF; rendered and visually read PDF pp. 2, 3, 5, 7; no extractable text',
      'Printed pp. 417–418, 420, 422')
    source('Parpola-interview','Interview with Asko Parpola','Asko Parpola; interviewer Omar Khan',None,'Harappa.com interview',
      'https://www.harappa.com/content/interview-asko-parpola','Opened public interview and downloaded HTML',
      'Bonta/Sanskrit objection is in the interviewer’s question; do not attribute that wording to Parpola')
    source('MW','Monier-Williams Sanskrit-English Dictionary (digitized headword data)','Monier Monier-Williams; Cologne Digital Sanskrit Dictionaries',1899,
      'sanskrit-lexicon/csl-orig, commit 55e8addbd96e8d9001b8789026b026763f4049c1',
      'https://github.com/sanskrit-lexicon/csl-orig','Opened repository, LICENSE and pinned v02/mw/mw.txt',
      'k1 fields; v1 acquisition manifest',licence='CC BY-SA 4.0 for csl-orig data; LICENSE opened and pinned')
    for i,title,path in [
      ('Firstpass','Steven Bonta first-pass source review','research/literature/2026-10-08-bonta-first-pass/README.md'),
      ('Corpus','Corpus provenance report','research/corpus/CORPUS_REPORT.md'),
      ('D2','Sign context and seals','experiments/2026-10-06-sign-context-and-seals/REPORT.md'),
      ('G','Indus weight metrology across sites and regions','experiments/2026-10-06-weight-metrology/REPORT.md'),
      ('H','Cross-script shape resemblance pilot','experiments/2026-10-06-resemblance-baseline/REPORT.md'),
      ('Fish-audit','Primary stroke-height audit','research/corpus/plate_audit/fish_strokes/README.md'),
      ('Fuls-audit','Conditional numerical equalities: exact algebra and its limits','research/methods/NUMERICAL_CONSTRAINT_AUDIT.md'),
      ('Assessment','Contribution assessment after a second precedent search','experiments/2026-10-06-contribution-assessment/REPORT.md'),
      ('Frenez','Earlier Frenez lecture check','experiments/2026-10-06-research-program/frenez-talk-check.md')]:
        source(i,title,'Indus research project',2026,'Private repository research output',path,'Opened local source; reused, not edited',path)
    failures=[{'query':q,'outcome':'No verified requested X post found'} for q in [
      '"Bonta" "Koenraad" "2023"','"Koenraad Elst" "Bonta" November 2023','"Koenraad" "Bonta" site:x.com']]
    failures += [{'query':'Steven Bonta Indus review citation partial decipherment 2024 2025',
      'outcome':'Found citations to the earlier distributional work and informal responses; no opened formal peer-reviewed review of the 2024 value system'},
      {'path':'research/corpus/fish_strokes/','outcome':'Requested path absent; located and reused research/corpus/plate_audit/fish_strokes/'},
      {'query':'Bonta 68508','outcome':'Generic search returned irrelevant Nebraska results; direct Language Log URL succeeded'}]
    manifest=[]
    for p in [RAW/'acquisition-2026-10-08-v1/manifest.json',RAW/'acquisition-2026-10-08-v2/manifest.json']:
        manifest.extend(read(p))
    write(OWN/'sources.json',{'status':'Exploratory','date':'2026-10-08','sources':sources,
      'prior_firstpass':first['scope'],'downloads':manifest,'failed_searches':failures,
      'policy':'All downloaded payloads and lexical/per-reading outputs remain local. No direct quotations are used.',
      'search_limit':'Bounded primary-source search; absence of an opened review is not proof that none exists.'})

    claims=[]
    def claim(src,loc,kind,paraphrase,evidence,test,verdict='Exploratory',graphic=None):
        claims.append({'id':f'Q{len(claims)+1:03}', 'source_id':src,'source_location':loc,
          'type':kind,'paraphrase':paraphrase,'quotation':None,'offered_evidence':evidence,
          'testable_here':bool(test),'test_ids':test.split(',') if test else [],
          'assessment_status':verdict,'graphic_identity':graphic,
          'note':'All sounds/meanings in this ledger are Bonta’s proposals.'})
    # Authored summaries of the substantive argument, with repetitions grouped.
    rows=[
    ('B24','Introduction, segments 8–12','method','He proposes a partial logosyllabic decipherment of an early Indo-Aryan language.','Distributional segmentation, metrology anchors and Sanskrit names/titles.','D1,D2,L1'),
    ('L01','0:02:54–0:05:20','historical, linguistic or archaeological','He describes a Cornell linguistics PhD and earlier work on Dravidian and Indo-European languages.','Autobiographical account, also in the introductory letter p. 6.',''),
    ('L03','0:06:26–0:08:20; B24 segment 16','segmentation or structure','Most inscriptions are read right to left; seals and impressions require distinguishing the mirrored face.','Sign crowding and orientation of source inscriptions.','D1'),
    ('B24','Sections 3–4, segments 15–33','segmentation or structure','Patterned texts have recurring ordered fields; complex texts contain more variable, language-like sequences.','Repeated sign classes, junctures, substitutions and positional restrictions.','D1,D2'),
    ('L03','0:56:37–0:59:40','method','He distinguishes transcriptive writing from notational writing and treats both as present in Indus texts.','Different ordering and repetition patterns across clusters.','D2'),
    ('L04','0:39:16–0:44:00; B24 segments 27–33','segmentation or structure','Reading-order fields are P, M, C and T, with optional omissions. P is a position label rather than a grammatical prefix.','Recurring complex clusters around M fields and final signs.','D2'),
    ('L04','0:02:10–0:09:35; B24 segments 18–20','corpus-distributional','M fields contain an oval subfield, a fish subfield and a mortar/pestle-plus-three-strokes subfield.','Illustrated recurrent clusters.','D2'),
    ('L04','0:09:55–0:10:17; B24 segment 20','segmentation or structure','Within a complete M field, the reading order is oval, fish, MS.','Repeated complete fields; manuscript explicitly reverses its printed left-to-right display.','D2'),
    ('L04','0:06:00–0:09:35; B24 segments 18–19','corpus-distributional','The fish subfield uses seven entries, has at most three entries and does not repeat an entry.','Selected sequences and a proposed compound-sign treatment of fish with paired strokes.','D2'),
    ('B24','Section 3, segments 19–20','corpus-distributional','The oval subfield uses three entries and has ordering restrictions comparable to fish.','Illustrated oval clusters, absent from the available page text.','D2'),
    ('B24','Section 3, segments 21–25','corpus-distributional','The MS construction strongly associates the mortar/pestle-like sign with three long strokes.','Co-occurrence and exceptional variants.','D2'),
    ('B24','Sections 3–4, segments 25–33','corpus-distributional','Jar and arrow signs function as terminal-field signs and can accompany other fields.','High frequency in final positions and patterned texts.','D1'),
    ('L09','0:04:17–0:13:00; B24 segments 55–65','segmentation or structure','Short ticks and paired bars delimit parts of patterned inscriptions and express a case-like relationship.','Positions between recurring fields; contrasts among juncture forms.','D1,D3'),
    ('L10','0:05:00–0:06:27','method','He clarifies that his CASE label represents a case-like relationship, perhaps dative/benefactive or genitive.','Context of proposed patterned readings; exact relationship remains tentative.','D3'),
    ('B24','Section 4, segments 34–37','method','An earlier exhaustive CV dictionary approach failed to produce satisfactory readings and was abandoned.','His retrospective account of dictionary searches and methodological difficulties.',''),
    ('L05','0:09:20–0:13:20; B24 segments 38–42','typology','Reordered complex clusters are interpreted as compound elements rather than ordinary fixed suffix strings.','Comparisons of recurring sequences in different positions.','D3'),
    ('B24','Table 6–7 discussion, segment 41','typology','The manuscript treats noun compounding as relatively rare in Dravidian and much more extensive in Sanskrit.','A comparison with Sanskrit and Dravidian examples.','D3'),
    ('L05','0:29:39–0:29:48','typology','The lecture categorically says Dravidian lacks noun compounding.','Typological argument excluding a Dravidian interpretation.','D3'),
    ('B24','Sections 4–5, segments 42–54','historical, linguistic or archaeological','He identifies Indo-Aryan as the most likely language from inferred compounding, affix behavior and proposed lexical readings.','Selected typological observations and Sanskrit matches.','D3,L1'),
    ('L06','0:01:27–0:04:58; B24 segments 43–49','method','He uses M fields as an entering wedge because metrological referents could constrain candidate values.','Short ordered non-repeating sequences and comparison with known weight systems.','M1'),
    ('B24','Metrological discussion, segments 23–24','sign value (phonetic or logographic)','He proposes a binary fish series of 1, 2, 4, 8, 16, 32 and 64 units and higher oval denominations.','Inventory size and ordering compared with Harappan weight multiples.','M1'),
    ('L06','0:08:52–0:10:15; B24 segments 49–51','sign value (phonetic or logographic)','He proposes pala for the staff/fork-like sign, using a Sanskrit straw/weight association and its non-M uses.','Pictorial identification, metrological vocabulary and pala/pala protector homophony.','L1,M1'),
    ('L06','0:14:37–0:18:48; B24 segments 52–53','sign value (phonetic or logographic)','He reads the MS construction as ma-tra and proposes matra, a measure or amount.','The recurring two-part construction and proposed word-final tra behavior.','L1,D1,D2'),
    ('L06','0:18:48–0:24:00; B24 segments 53–54','sign value (phonetic or logographic)','He proposes dhana/dhanu-related values for the bow-bearing figure, linking bow and wealth.','Graphic bow identification and Sanskrit lexical comparison.','L1'),
    ('L07','0:10:06–0:18:32; B24 segments 67–71','method','He obtains PU/bhu through the intersection of contexts ending in pala, ma, dhana and tra.','Candidate words must share the same initial sign value across contexts.','L2'),
    ('L07','0:18:32–0:24:37; B24 forewords, segments 2–7','method','He reports developing values on Mahadevan, then checking them on ICIT material with approximately 12–15 readable new inscriptions and one correction.','Personal account of the sequence of research and new catalogue consultation.','V1'),
    ('B24','Catalogue conventions, segment 84','method','An ICIT-first label generally means it was first encountered there, but can instead signal a more accurate transcription.','Explicit source-labelling convention.','V1'),
    ('B24','Cross-checking, segments 66–77','method','A sign value is strengthened when it forms recognizable Sanskrit words in several independent sign contexts.','Context intersections, names, titles and substitutions.','L1,L2'),
    ('B24','Table 18, segments 78–81','method','He lists 55 selected signs plus additional logographic/ligature constructions and leaves many frequent and rare signs unresolved.','The published value table and later individual examples.','L1'),
    ('B24','Section 6, segments 85–216','reading of a text','Hundreds of catalogue examples are offered as names, titles, compounds or partial readings using the proposed values.','A source-indexed series of individual proposed readings.','L1,V1'),
    ('L08','0:59:59–1:04:00; B24 segment 81','method','Some compound signs are interpreted as ligatures with honorific or lexical values; ordering alternatives may be admitted.','Proposed graphic compositions and readings such as shripati and related forms.','L1'),
    ('B24','Sections 5–6, segments 55–65 and 78–81','sign value (phonetic or logographic)','He proposes AS for the jar, ISH for the arrow and ASTI for a group of asset-related signs.','Terminal distributions and Sanskrit predicates/property vocabulary.','D1,M1'),
    ('L09','0:36:37–0:37:42','historical, linguistic or archaeological','He links the proposed ASTI readings to property/asset vocabulary in Sanskrit and later languages.','Lexical analogy and patterned contexts.','M1'),
    ('L10','0:01:07–0:03:36','historical, linguistic or archaeological','He interprets some very short seal inscriptions as asset or metrological notations.','Numeral-like strokes and signs treated as measure markers.','D2,M1'),
    ('L10','0:07:30–0:16:48; B24 segments 227–249','historical, linguistic or archaeological','He proposes deposits, pledges and temple donations as uses of patterned inscriptions.','Proposed names/amounts, asset predicates and analogy with later donative epigraphy.','M1'),
    ('L10','0:17:08–0:17:49','reading of a text','He interprets MH4470 and MH4603 as oblation-related records, including proposed chu offerings.','Proposed readings of sign clusters and later sacrificial vocabulary.','M1'),
    ('L10','0:28:25–0:31:14','historical, linguistic or archaeological','He infers princes, monarchs and caste-related titles from his name and title readings.','Readings including bahuja and royal honorifics.','L1'),
    ('L10','0:30:32–0:31:14','historical, linguistic or archaeological','He suggests some lunar-dynasty mythology could preserve features of Indus society.','A proposed Somabhu royal name and later mythic narratives.',''),
    ('L10','0:31:14–0:32:19','evaluation criterion','He explicitly leaves common context-invariant and infrequent signs unresolved.','Insufficient contextual variation to cross-check their values.',''),
    ('L11','0:00:22–0:03:57','historical, linguistic or archaeological','He describes the main language as early Indo-Aryan and leaves its relation to the Indo-Iranian split partly open.','The proposed names and titles; no separate linguistic chronology test.','L1'),
    ('L11','0:04:17–0:14:31','typology','He infers prefix/preposition-like uses of proposed ati, para and related elements.','Recurring graphic sequences interpreted using their proposed Sanskrit values.','D3'),
    ('L11','0:14:51–0:29:22','historical, linguistic or archaeological','He reconstructs earlier forms behind atman from the proposed atima spellings.','Proposed phonetic reading plus historical sound-change reasoning.',''),
    ('L11','0:30:48–0:33:40','historical, linguistic or archaeological','He derives sabha from a proposed earlier sahapa through metathesis.','A proposed inscription reading and Sanskrit saha/pa decomposition.',''),
    ('L11','0:34:00–0:38:00','typology','He proposes a possessive or genitive-like ka affix in selected readings.','Name sequences interpreted with Sanskrit ka morphology.','D3'),
    ('L12','0:04:17–0:04:40','evaluation criterion','A claim of full decipherment should account for data that do not fit, including M-field distributions.','Examples of competing claims ignoring patterned notational clusters.','E1'),
    ('L12','0:12:07–0:12:51','evaluation criterion','Distributional evidence should determine script typology before assumptions about links to another script.','Criticism of Brahmi-related proto-abugida proposals.','E1'),
    ('L12','0:28:36–0:28:57','evaluation criterion','Proposed sign values should use distribution as well as graphology.','Different distributions of similarly drawn fish/oval/jar classes.','E1'),
    ('L12','0:37:10–0:37:30','evaluation criterion','A candidate language should not be imposed through a prior preference.','Comparison with unsuccessful aspirational readings.','E1'),
    ('L12','0:41:42–0:42:25','evaluation criterion','Readings should not require ad hoc explanations for implausible content.','Examples of bizarre readings excused as mystical formulas.','E1'),
    ('L12','0:46:18–0:46:40','evaluation criterion','Claims to read virtually every sign and every cited inscription deserve scrutiny.','Incomplete coverage persists in established decipherments.','E1'),
    ('B10','2010 title page and distributional discussion','method','The earlier work develops distributional field analysis and markedness before the later phonetic value table.','Patterned texts and comparisons of sign combinations.','P1'),
    ('B24','Forewords, segments 2–7','method','The second edition reports expansion and correction of the first edition, including consideration of the larger ICIT corpus.','Author’s edition history; first-edition full witness not available for a line-by-line comparison.','V1,P1'),
    ('B-letter','PDF p. 5','method','The undated introductory letter describes a couple of small modifications on later corpus checking.','Author’s research-history account; unlike the lecture’s singular correction count.','V1'),
    ('L02','0:23:46–0:27:00','historical, linguistic or archaeological','He presents Indo-Aryan speakers as a candidate for Indus and separates it from politically motivated arguments.','Historical overview; no independent excavation-language join.',''),
    ]
    for row in rows:claim(*row)
    # Every distinguishable Table 18 entry has an authored claim record. The glyph
    # identity remains unknown unless resolved through the separate letter witness.
    values=[
      (78,'ka','ka/kaa/kha/khaa'),(78,'dhu','dhu/dhuu'),(78,'ni','ni/nii/ne'),
      (78,'PA','pa/paa/ba/baa/bha/bhaa'),(78,'PU','pu/puu/bhu/bhuu'),
      (78,'MA','ma/maa and word-initial maha/mahaa'),(78,'ja','ja/jaa'),
      (78,'sa','sa/saa'),(78,'SU1','su/suu/shu/so/sho'),(79,'SU2','su'),
      (79,'ra','ra/raa'),(79,'vi','vi/vii'),(79,'hu','hu'),
      (79,'ana','ana/aana/retroflex ana/aana'),(79,'eka','ka/eka'),
      (79,'ati','aat/ati/adhi/atii'),(79,'PALA','pala/paala/bala'),
      (79,'DHANA','dhana/dhaana/daana, first form'),(79,'DHANA2','dhana/dhaana/daana, second form'),
      (79,'para','para/pra'),(79,'jaya','jaya/jya'),(79,'vara','var/vara'),
      (79,'mana','man/mana/maana'),(79,'shara','shar/shara'),(79,'shri','shri/suri'),
      (80,'tya','tya/taya/taaya'),(80,'saha','saha/saa'),(80,'natha','nata/naatha'),
      (80,'mina','miina/min'),(80,'vasu','vasu/vaasu'),(80,'caru','caru/caaru'),
      (80,'mana2','mana/maana/manaa'),(80,'kara1','kara/kra/kar/kaara'),
      (80,'kara2','kara/kar/kaara'),(80,'pra','pra'),(80,'TRA','tra/traa/tri'),
      (80,'rashtra','raashtra logogram'),(80,'laksha','laksha logogram'),
      (80,'sena','senaa logogram'),(80,'arya','aarya logogram'),(80,'dhara','dhara logogram'),
      (80,'sam','sam logogram'),(81,'raksha','raksha logogram'),(81,'raja','raajan logogram'),
      (81,'dhanya','dhaanya logogram'),(81,'deva','deva logogram'),(81,'PATI','pati logogram'),
      (81,'ashva','ashva logogram'),(81,'go','go logogram'),(81,'AS','belong/be predicate'),
      (81,'ISH','be accepted/be worth; possible own/possess sense'),(81,'ASTI','property, with possible number distinctions'),
      (81,'shripati','shripati/suripati ligature'),(81,'shripatideva','shripatideva or alternatives of compound order'),
      (81,'paka','paka/bhaka/bhaga ligature'),(81,'shripala','shripala ligature'),
      (81,'aryaka','aryaka ligature'),(81,'karapala','karapala ligature')]
    selected=read(OWN/'selection.json')
    for seg,label,description in values:
        claim('B24',f'Table 18, text segment {seg}', 'sign value (phonetic or logographic)',
          f'He assigns {description} to the illustrated Table 18 entry labelled {label}.',
          'The table and individual contextual examples in section 6.',
          'L1' if label in selected['values_slp1'] else 'D1' if label in ['AS','ISH'] else '',
          graphic=selected['graphic_roles'].get(label))
    for item in selected['panel']:
        claim('B24',item['source'],'reading of a text',
          'He combines the proposed roles '+', '.join(item['roles'])+' as a Sanskrit word, name or title.',
          'Repeated contexts in Tables 13–17 and the MS discussion; proposed role values are checked together.',
          'L1',graphic={'panel_id':item['id'],'roles':item['roles']})
    for row in [
      ('B24','Segment 43; Table 8, segments 44–45','corpus-distributional','He reports that the secondary U/pot-plus-numeral field has no stroke number above four.','Examples on opposite faces or secondary lines.','D2'),
      ('B24','Segment 47; Table 10, segments 47–49','corpus-distributional','He treats two staff-like forms as allographs because they have similar distributions and do not co-occur.','Separate catalogue entries with overlapping contexts.','D2'),
      ('B24','Segment 46','method','He acknowledges a plausible Dravidian bow/price comparison as well as a Sanskrit bow/wealth comparison.','Candidate homophones appropriate to an assumed value context.','L1'),
      ('B24','Segments 227–249; Tables 19–21','reading of a text','He interprets complete patterned fields as assets belonging to a named owner, assigned to a deity or authority.','The combined proposed P/C names, M quantities and terminal predicates.','D2,M1')
    ]:claim(*row)
    # The parser supplies a locator inventory, never a certified complete reading set.
    examples=read(RAW/'run-2026-10-08-v1/paper-examples.json')
    locator=collections.defaultdict(set)
    for e in examples:locator[e['primary']].add(e['segment'])
    write(OWN/'reading-locators.json',{'status':'Exploratory','unique_primary_labels':len(locator),
      'parsed_occurrences':len(examples),'scope':'Identifiers and text-segment locators only; adjacent/unlabelled examples and broken brackets require manual review',
      'entries':[{'primary_label':k,'text_segments':sorted(v)} for k,v in sorted(locator.items())]})
    p=OWN/'claims.jsonl'
    if p.exists() and not REPLACE:raise FileExistsError(p)
    p.write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in claims),encoding='utf-8')
    counts=dict(collections.Counter(c['type'] for c in claims))
    write(OWN/'ledger-coverage.json',{'claim_records':len(claims),'by_type':counts,
      'table18_distinguishable_text_entries':len(values),'author_stated_selected_signs':55,
      'selected_lexical_reading_types':len(selected['panel']), 'lecture_sources_represented':12,
      'complete_substantive_claim_inventory':False,
      'missing':'No exhaustive adjudication of all individual section-6 readings, lecture background assertions, historical etymologies, or missing graphic examples. Caption searches are not a full audiovisual review.',
      'table18_note':'58 distinguishable written entries include extra logographic/ligature items. They cannot be equated to the author’s 55 glyph count without images.',
      'reading_locator_inventory':'reading-locators.json'})
    links={s['id']:s['url'] for s in sources}
    md=['# Claim ledger','',f'This ledger contains {len(claims)} authored claim records. Repeated illustrations of one assertion are grouped. [Coverage](ledger-coverage.json) identifies the unfinished exhaustive reading audit; [reading locators](reading-locators.json) preserve the parser’s source frame. All values are Bonta’s proposals. No direct quotations are used.','']
    for c in claims:
        url=links[c['source_id']]
        source_text=f"[{c['source_id']}]({url})" if url else c['source_id']
        md.extend([f"## {c['id']}: {c['type']}",'',c['paraphrase'],'',
          f"Source: {source_text}, {c['source_location']}. Offered evidence: {c['offered_evidence']}",'',
          'Test: '+(', '.join(c['test_ids']) if c['test_ids'] else 'No completed test in this package.')+' Identity: '+('candidate mapping recorded' if c['graphic_identity'] else 'see source; glyph identity may remain unresolved')+'.',''])
    p=OWN/'claims.md'
    if p.exists() and not REPLACE:raise FileExistsError(p)
    p.write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps({'sources':len(sources),'claims':len(claims),'table_entries':len(values),'reading_labels':len(locator)},indent=2))

if __name__=='__main__':main()
