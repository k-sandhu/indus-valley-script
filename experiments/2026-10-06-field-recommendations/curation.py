"""Manual literature coding after reading the cited passages. No recommendation inference.

This file is the editable authority. build_tables.py exports and checks it.
Bulk source text is held in the local raw directory, not in this catalogue.
"""
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
RAW = 'data/raw/2026-10-06-field-recommendations/rebuild-2026-10-07/'
LIT = 'research/literature/sources/'
D1 = 'experiments/2026-10-06-chronology-region/README.md'
D2 = 'experiments/2026-10-06-sign-context-and-seals/README.md'
E = 'experiments/2026-10-06-backward-chronology/README.md'
G = 'experiments/2026-10-06-resemblance-baseline/README.md'
H = 'experiments/2026-10-06-byproduct-inventory/README.md'
CENSUS = 'experiments/2026-10-06-evidence-census/collections-and-datasets/README.md'
WEST = 'experiments/2026-10-02-connections-and-priority/regional-west/REPORT.md'
CONTROLS = 'research/literature/nonlinguistic_controls/README.md'

sources = []
recommendations = []

def source(sid, title, authors, year, venue, url, witness, scope, access='opened_pdf', note=''):
    sources.append(dict(id=sid, title=title, authors=authors.split('|'), year=year,
        venue=venue, url=url, opened=True, access=access, read_scope=scope,
        witness_path=witness, bibliographic_note=note, reviewed_date='2026-10-07',
        rights='rights-unverified; third-party payload remains local', quotations=[]))

source('FRENEZ-TALK-2026', 'Ongoing decipherments : Writing in the Indus Civilization - by Dennys Frenez',
       'Dennys Frenez', 2026, 'ILARA, Ongoing Decipherments lecture 9; YouTube upload 3 October 2026',
       'https://youtu.be/1i9q17ld_jU', 'experiments/2026-10-06-research-program/frenez-talk-check.md',
       'Opened the coordinator\'s 7 October caption-check note and all timestamped entries; did not independently reopen the captions.',
       'opened_coordinator_caption_check',
       'Description title: Memorizing Meanings: Archaeological Perspectives on Writing in the Indus Civilisation. Upload date is known; recording/event date and physical venue remain unverified. The coordinator reports 1166 auto-caption lines; no full transcript was saved.')
source('FRENEZ-2018', 'Private Person or Public Persona? Use and Significance of Standard Indus Seals as Markers of Formal Socio-Economic Identities',
       'Dennys Frenez', 2018, 'Walking with the Unicorn: Social Organization and Material Culture in Ancient South Asia: J. M. Kenoyer Felicitation Volume, Archaeopress / ISMEO, pp. 166-193',
       'https://www.harappa.com/sites/default/files/pdf/private-person.pdf', LIT+'frenez_2018_private_person.pdf',
       'Printed pp. 167, 170-171, 180-181, 186-187 and front matter; PDF8,11-12,21-22,27-28.', note='PDF carries copyright 2017; the volume publication is 2018. The printed pagination, not the copyright footer, identifies the passage.')
source('WELLS-2015', 'The Archaeology and Epigraphy of Indus Writing', 'Bryan K. Wells', 2015,
       'Archaeopress; technical appendices by Andreas Fuls',
       'https://www.archaeopress.com/Archaeopress/DMS/3608E8E0F92C4920AE82709E2A32643F/9781784910464-sample.pdf',
       RAW+'wells_2015_sample.pdf', 'Preface, printed viii-x, PDF12-14; title and copyright pages. Sample only.')
BOOKLET = 'https://asc.iitgn.ac.in/assets/events/training_workshop/Book_of_Abstracts_com.pdf'
source('FULS-2023', 'A Digital Corpus and Epigraphical Database for Indus Script Research', 'Andreas Fuls', 2023,
       'Book of Abstracts, Emerging Perspectives of the Harappan Civilization, IIT Gandhinagar, 10-12 February 2023, p. 45',
       BOOKLET, RAW+'iitgn_2023_abstracts.pdf', 'Complete abstract, printed/PDF45.', 'opened_abstract')
source('KONASUKAWA-2023', 'Indus Scripts Incised on the Seals Discovered from the Initial Phase of Harappan Period: An Investigation of the Chronology of Indus Writing System',
       'Ayumu Konasukawa', 2023, 'Book of Abstracts, Emerging Perspectives of the Harappan Civilization, IIT Gandhinagar, 10-12 February 2023, pp. 49-50', BOOKLET,
       RAW+'iitgn_2023_abstracts.pdf', 'Complete abstract, printed/PDF49-50 and speaker profile.', 'opened_abstract',
       'Booklet prints KONASAKUWA in speaker heading but Konasukawa in profile; title transcribed without silently correcting its grammar.')
source('GOKHALE-2023', 'The Indus Script: Inputs from Archaeology', 'Pallavee Gokhale', 2023,
       'Book of Abstracts, Emerging Perspectives of the Harappan Civilization, IIT Gandhinagar, 10-12 February 2023, pp. 48-49', BOOKLET, RAW+'iitgn_2023_abstracts.pdf',
       'Complete abstract, printed/PDF48-49.', 'opened_abstract')
source('FRENEZ-VIDALE-2023', 'Of Goods and People: The Indus-related Seals beyond the Harappan World', 'Dennys Frenez|Massimo Vidale', 2023,
       'Book of Abstracts, Emerging Perspectives of the Harappan Civilization, IIT Gandhinagar, 10-12 February 2023, p. 46', BOOKLET, RAW+'iitgn_2023_abstracts.pdf',
       'Complete abstract, printed/PDF46.', 'opened_abstract')
source('KENOYER-2020', 'Origin and Development of the Indus Script: Insights from Harappa and other sites', 'Jonathan Mark Kenoyer', 2020,
       'Studies on Indus Script, edited by Kaleemullah Lashari, National Fund for Mohenjodaro, Karachi, pp. 217-236',
       'https://www.harappa.com/content/origin-and-development-indus-script-insights-harappa-and-other-sites',
       LIT+'kenoyer2020_origin.pdf', 'Printed pp. 217,223,230-231 (PDF1,7,14-15); conclusion and relevant mark classifications.',
       note='Heading omits The; self-citation at foot of p.217 includes The and gives pp.217-236. Local witness contains 20 pages through p.236; recommendations were read on pp.223,230-231.')
source('KENOYER-2006', 'The Origin, Context and Function of the Indus Script: Recent Insights from Harappa', 'Jonathan Mark Kenoyer', 2006,
       'Proceedings of the Pre-symposium of RIHN and 7th ESCA Harvard-Kyoto Roundtable, edited by OSADA Toshiki with HASE Noriko, RIHN, Kyoto, pp. 9-27',
       'https://www.harappa.com/sites/default/files/pdf/Kenoyer2006_The%20Origin%2C%20Context%20and%20Function%20of%20the%20Indus%20Sc.pdf', LIT+'kenoyer_2006_context.pdf',
       'Visually read scan PDF1 cover and PDF8, printed pp.20-21; closing discussion on p.21.', 'opened_scan',
       'URL is a discovery link from the earlier source inventory; the reused local PDF is the inspected witness. No text layer for this passage.')
source('RAO-2009', 'A Markov model of the Indus script', 'Rajesh P. N. Rao|Nisha Yadav|Mayank N. Vahia|Hrishikesh Joglekar|Ronojoy Adhikari|Iravatham Mahadevan', 2009,
       'Proceedings of the National Academy of Sciences 106(33):13685-13690', 'https://doi.org/10.1073/pnas.0906237106',
       LIT+'rao_2009_markov.pdf', 'Title page and Discussion, printed pp.13689-13690, PDF5-6.')
source('YADAV-2013', 'Sensitivity of Indus Script to Site and Type of Object', 'Nisha Yadav', 2013,
       'SCRIPTA 5:67-103', 'https://www.harappa.com/sites/default/files/201311/Nisha%20Yadav_Scripta%202013.pdf',
       LIT+'yadav_2013_site_type.pdf', 'Conclusions, printed pp.96-98, PDF30-32; title page.',
       note='The local witness establishes the page locators. The URL is retained as a discovery location, not a newly verified download.')
source('GANESAN-ETAL-2010', 'The Indus Script: Text and Context: A Statistical-Positional Analysis of Significant Text Segments',
       'Sundar Ganesan|Chandrasekhar Subramanian|G. C. Suresh Babu|Iravatham Mahadevan', 2010,
       'World Classical Tamil Conference paper, Coimbatore', 'https://s3.us-east-1.amazonaws.com/rmrldl.in/RP/IM/The%20Indus%20Script%20Text%20and%20Context_2010/index.html', LIT+'rmrl/mahadevan_2010_context/page_06.png',
       'OCR reader pp.1,5-6, section8; original reader image p.6 visually read and checked against OCR.', 'opened_reader_image',
       'Reused RMRL reader page assets and original URL from fetch_rmrl_flipbooks.py. Page6 visually confirms the stated language-identification goal; sign glyphs in OCR are not used as authenticated transcriptions.')
source('PARPOLA-2008', 'Is the Indus script indeed not a writing system?', 'Asko Parpola', 2008,
       'Airavati: Felicitation Volume in Honour of Iravatham Mahadevan, Varalaaru.com, Chennai, pp.111-131',
       'https://www.harappa.com/script/indus-writing.pdf', LIT+'airavati_2008.pdf',
       'Chapter introduction p.111; rare signs and repetition pp.113-115; conclusion pp.127-128. In the local volume PDF, printed page equals PDF page.')
source('FSW-2004', 'The Collapse of the Indus-Script Thesis: The Myth of a Literate Harappan Civilization', 'Steve Farmer|Richard Sproat|Michael Witzel', 2004,
       'Electronic Journal of Vedic Studies 11(2):19-57', 'https://www.safarmer.com/fsw2.pdf',
       LIT+'farmer_sproat_witzel_2004_author.pdf', 'Printed pp.37 n.23,43 n.28,44,46 (PDF19,25,26,28) and title page.')
source('SPROAT-2010', 'Ancient Symbols, Computational Linguistics, and the Reviewing Practices of the General Science Journals', 'Richard Sproat', 2010,
       'Computational Linguistics 36(3):585-594', 'https://aclanthology.org/J10-3012/',
       LIT+'sproat_2010_last_words.pdf', 'Printed pp.585,591-593, PDF1,7-9; statistical requirements and section 3.')
source('RAO-REPLY-2010', 'Entropy, the Indus Script, and Language: A Reply to R. Sproat', 'Rajesh P. N. Rao|Nisha Yadav|Mayank N. Vahia|Hrishikesh Joglekar|Ronojoy Adhikari|Iravatham Mahadevan', 2010,
       'Computational Linguistics 36(4):795-805', 'https://doi.org/10.1162/coli_c_00030', LIT+'rao_2010_reply.pdf',
       'Printed pp.795,798-799,803-805 (PDF1,4-5,9-11); reply, inductive framework and conclusion.')
source('SPROAT-REPLY-2010', 'Reply to Rao et al. and Lee et al.', 'Richard Sproat', 2010,
       'Computational Linguistics 36(4):807-816; inspected author manuscript', 'https://doi.org/10.1162/coli_c_00031',
       RAW+'sproat_2015_response.pdf', 'Author-manuscript PDF1, section 2, opening clarification of scope.',
       note='Acquisition filename incorrectly says 2015; actual publication is 2010. It is retained to preserve the downloaded witness. Manuscript has ten pages; no printed journal pagination, so comparison cites manuscript PDF1.')
source('SPROAT-2013', 'Corpora and Statistical Analysis of Non-Linguistic Symbol Systems', 'Richard Sproat', 2013,
       'Author monograph, dated 21 January 2013; prepublication research document', 'https://richardsproat.com/monograph.pdf',
       RAW+'sproat_2014_monograph.pdf', 'Title/abstract, section 9, printed/PDF84-86.',
       note='Acquisition filename says 2014; title-page date is 2013. This is a prepublication monograph, not the 2014 Language article.')
source('SPROAT-2014', 'A Statistical Comparison of Written Language and Nonlinguistic Symbol Systems', 'Richard Sproat', 2014,
       'Language 90(2):457-481; supplementary materials DOI10.1353/lan.2014.0042', 'https://doi.org/10.1353/lan.2014.0031',
       RAW+'sproat_2014_full.pdf', 'Opened Cambridge abstract and bibliographic record; captured response is a PDF rendering of the web page, not the journal article.',
       'opened_abstract', 'Cambridge online migration date is not publication date. Main full text not recovered. Publisher URL returned an unrelated sponsor page with HTTP200; excluded as evidence. No recommendation attributed to this abstract.')
source('RAO-REPLY-2015', 'On statistical measures and ancient writing systems', 'Rajesh P. N. Rao|Rob Lee|Nisha Yadav|Mayank Vahia|Philip Jonathan|Pauline Ziman', 2015,
       'Language 91(4):e198-e205', 'https://www.lsadc.org/Files/Language/Language%202015/91.4_e03Rao.pdf',
       RAW+'rao_2015_reply.pdf', 'Printed e198 and e203-e204 (PDF1,6-7); critique of Sproat 2014 and conclusion.')
source('VIDALE-2007', 'The Collapse Melts Down: A Reply to Farmer, Sproat & Witzel', 'Massimo Vidale', 2007,
       'East and West 57(1/4):333-366, IsIAO', 'https://www.jstor.org/stable/29757733',
       RAW+'vidale_web_excerpt.json', 'Read article text on Scribd mirror: introduction p.333, conclusion pp.361-362, Appendix pp.363-364; saved web excerpt.',
       'opened_article_mirror', 'Mirror URL https://www.scribd.com/document/394657225/29757733. Ignore its AI-generated title/summary. Padua institutional record has deposit year 2008; journal cover identifies publication as December 2007.')
source('MUKHOPADHYAY-2023', 'Semantic scope of Indus inscriptions comprising taxation, trade and craft licensing, commodity control and access control: archaeological and script-internal evidence',
       'Bahata Ansumali Mukhopadhyay', 2023, 'Humanities and Social Sciences Communications 10:972', 'https://doi.org/10.1057/s41599-023-02320-7',
       LIT+'mukhopadhyay_2023.pdf', 'Article pp.1-2 and p.29; introductory recommendation and explicit future goblet study.')
source('RAO-2018', 'The Indus Script and Economics. A Role for Indus Seals and Tablets in Rationing and Administration of Labor', 'Rajesh P. N. Rao', 2018,
       'Walking with the Unicorn: Social Organization and Material Culture in Ancient South Asia: J. M. Kenoyer Felicitation Volume, Archaeopress / ISMEO, pp.518-525',
       'https://arxiv.org/abs/1812.00049', LIT+'rao_2018_economics.pdf', 'Printed pp.524-525, PDF7-8; title verified in local source.')
source('AMERI-2013', 'Regional Diversity in the Harappan World: The Evidence of the Seals', 'Marta Ameri', 2013,
       'Connections and Complexity: New Approaches to the Archaeology of South Asia, edited by Shinu Anna Abraham, Praveena Gullapalli, Teresa P. Raczek and Uzma Z. Rizvi, Left Coast Press, pp.355-374',
       'https://www.harappa.com/sites/default/files/pdf/Ameri-%20Regional%20Variation%20in%20the%20Indus%20with%20front%20matter.pdf',
       RAW+'ameri_2013.pdf', 'Printed pp.371-372, PDF23-24; conclusion and notes, with front matter.')
source('GREEN-2016', 'Finding Harappan Seal Carvers: An Operational Sequence Approach to Identifying People in the Past', 'Adam S. Green', 2016,
       'Journal of Archaeological Science 72:128-141', 'https://doi.org/10.1016/j.jas.2016.06.008',
       RAW+'green_author_excerpt.html', 'Harappa page reproducing author abstract and conclusion; read both quoted extracts.',
       'opened_author_extracts', 'Full paper not recovered. Page editorial predictions are not Green recommendations. Author method description excluded from recommendation rows.')
source('PETRIE-LYNAM-2020', 'Revisiting Settlement Contemporaneity and Exploring Stability and Instability: Case Studies from the Indus Civilization', 'Cameron A. Petrie|Frank Lynam', 2020,
       'Journal of Field Archaeology 45(1):1-15; first online 30 September 2019', 'https://doi.org/10.1080/00934690.2019.1664848',
       RAW+'petrie_lynam_accepted.pdf', 'Accepted manuscript PDF24-26, lines630-681; conclusion.',
       note='Author accepted version at https://api.repository.cam.ac.uk/server/api/core/bitstreams/1a2bf7ed-26a6-4ce2-babf-ff9b409a1f89/content. Recommendations located by manuscript lines, not guessed journal pages.')
source('LAW-2011', "Inter-Regional Interaction and Urbanism in the Ancient Indus Valley: A Geologic Provenience Study of Harappa's Rock and Mineral Assemblage", 'Randall William Law', 2011,
       'RIHN, Occasional Paper 11, Linguistics, Archaeology and the Human Past', 'https://www.harappa.com/content/summary-and-discussion-concluding-remarks',
       RAW+'law_ch14.pdf', 'Chapter 14, printed pp.500-503, PDF1-4; complete substantive concluding remarks.')
source('MILLER-PROJECT-2025', 'Biography', 'Heather M.-L. Miller', None,
       'University of Toronto Mississauga, author research page; project launched 2025', 'https://sites.utm.utoronto.ca/heathermlmiller/node/19',
       RAW+'miller_projects.html', 'Research paragraph beginning with technologies of record-keeping and writing, project launch 2025.',
       'opened_author_page', 'Undated page, retrieved 7 October 2026. This actual project replaces the nonexistent Miller-2013 citation; 2025 is project start, not page publication year.')
source('VAHIA-2025', 'Understanding the Harappan Script: going beyond grammar and language', 'Mayank N. Vahia', 2025,
       'BITS Scripts 2025, Institute of Mathematical Sciences, Chennai, lecture slides',
       'https://www.imsc.res.in/~sitabhra/meetings/bitsscripts25/assets/talks/Vahia_Lecture_1.pdf',
       RAW+'vahia_2025_slides.pdf', 'Printed slides35-36,43,47 (PDF34-35,40,44); Path to decipherment?, composite signs and Conclusion.',
       'opened_slides', 'Printed slide numbering differs from PDF-page numbering. Both are recorded.')
source('POSSEHL-PAGE-1996', 'G. L. Possehl: Indus Age Series', 'Gregory L. Possehl', None,
       'University of Pennsylvania author page describing Indus Age: The Writing System, published November 1996',
       'https://www.sas.upenn.edu/~gpossehl/IndusAge.html', RAW+'possehL_proxy.txt',
       'Paragraph beginning The current state of knowledge, complete three-principle agenda.', 'opened_author_page_proxy',
       'Page undated; 1996 is the book date. Direct page returned403; text proxy https://r.jina.ai/https://www.sas.upenn.edu/~gpossehl/IndusAge.html returned the author page. Book itself not opened.')
source('RAJAN-SIVANANTHAM-2025', 'Indus Signs and Graffiti Marks of Tamil Nadu: A Morphological Study', 'K. Rajan|R. Sivanantham', 2025,
       'Department of Archaeology, Government of Tamil Nadu, illustrated eight-page brochure',
       'https://tamildigitallibrary.in/assets/docs/uploads/catalogue_article_file/BOK/upload/2025/08/TVA_BOK_0065888_Indus_Signs_and_Graffiti_Marks_of_Tamil_Nadu_A_Morphological_Study.pdf',
       'data/raw/2026-10-02-connections-and-priority/south-india/morphological-study-2025.pdf',
       'Final PDF8, paragraphs on material evidence and future research.', note='Reused Package G witness. This is an eight-page brochure, not the full monograph; its contact and contemporaneity claims remain the authors\' hypotheses.')
source('RAO-INTERVIEW-2026', 'Will the Indus Valley script ever be deciphered?', 'Owen Jarus', 2026,
       'Live Science, 15 March 2026; Rajesh Rao quoted/interviewed', 'https://www.livescience.com/archaeology/will-the-indus-valley-script-ever-be-deciphered',
       RAW+'rao_2026_interview.html', 'Final three paragraphs attributed to Rao: partial number-system reconstruction and excavation.',
       'opened_interview_report', 'Rao is the speaker, Jarus the article author. Reporter paraphrase and direct quotation are distinguishable in the page.')
source('RATNAGAR-INTERVIEW-2018', 'An Interview with Shereen Ratnagar', 'Shereen Ratnagar|Omar Khan', 2018,
       'Harappa.com, interview conducted Bombay, 18 December 2018', 'https://www.harappa.com/content/interview-shereen-ratnagar',
       RAW+'ratnagar_2018_interview.html', 'Read later interview from Indus Studies question through seal/figurine discussion; bone/plant collecting paragraph.',
       'opened_interview', 'Interview date known; page publication date not specified.')
source('FRENEZ-2021', 'Crafting a Writing System: Insights on the Invention and Development of the Indus Script', 'Dennys Frenez', 2021,
       'University of Bologna, Invention of Writing workshop, 13 January 2021, author abstract',
       'https://www.inscribercproject.com/workshop/speakers/frenez.php', RAW+'frenez_2021_abstract.html',
       'Complete author abstract.', 'opened_abstract', 'Separate from the 12 March 2025 Sorbonne seminar listing; the opened 2025 programme gives date/title but no abstract. Do not transplant the 2021 text to 2025.')

source('GREEN-2021', 'Killing the Priest-King: Addressing Egalitarianism in the Indus Civilization', 'Adam S. Green', 2021,
       'Journal of Archaeological Research 29:153-202; online 16 September 2020', 'https://doi.org/10.1007/s10814-020-09147-9',
       RAW+'green_2021_priest_king.pdf', 'Title page; future-work discussion printed pp.182-184, PDF30-32; conclusion p.185, PDF33.',
       note='Author repository supplied the published PDF. Additional source located in continuation; distinct from the excluded 2016 method paper.')
sources[-1]['quotations'] = [{'locator':'printed182, PDF30, penultimate paragraph',
                            'text':'These other potential loci of inequality deserve further research'}]

def compare(sid, locator, relation, statement):
    return dict(source_id=sid, locator=locator, relation=relation, statement=statement)

REGIONAL = [compare('WELLS-2015', 'printed viii-ix, PDF12-13', 'shared_priority', 'Explicitly asks for regional text-structure research and spatial/temporal separation.'),
            compare('YADAV-2013', 'printed97-98, PDF31-32', 'shared_priority', 'Explicitly asks interpretations to account for site and object-type fluctuations.')]
ACCESS = [compare('KENOYER-2020', 'printed231, PDF15', 'shared_priority', 'Calls for continued collaboration and accessible data publication.')]
DEBATE = [compare('PARPOLA-2008', 'printed111,113-115,127; same PDF pages', 'disputes_underlying_thesis', 'Defends a logo-syllabic system and disputes the rare-sign and repetition arguments.'),
          compare('VIDALE-2007', 'printed361-362, Conclusion', 'disputes_underlying_thesis', 'Rejects the claimed archaeological demonstration of non-writing; acknowledges questions about repetition.')]
STATS = [compare('RAO-REPLY-2010', 'printed798-799,803; PDF4-5,9', 'direct_dispute_on_inference', 'Defends multiple statistical tests as inductive evidence; denies entropy similarity alone proves language.'),
         compare('RAO-REPLY-2015', 'printed e198,e203; PDF1,6', 'direct_dispute_on_inference', 'Disputes Sproat 2014 interpretation and length-linked classifiers; commends his larger comparison corpora.')]

def rec(rid, researcher, sid, locator, theme, sentence, requires, feasible, links=(), repo='Partial coverage; inspect linked work before proposing a new run.', comparisons=(), limit=''):
    recommendations.append(dict(id=rid, status='Exploratory', researcher=researcher,
        source_id=sid, source_locator=locator, theme=theme, recommendation=sentence,
        required_data_or_collaboration=requires, testable_with_existing_data=feasible,
        repository_status=repo, repository_links=list(links), comparisons=list(comparisons),
        comparison_scope='No direct response located for this recommendation.' if not comparisons else 'Relations apply only to the specified passage and scope.',
        limitation=limit))

rec('F01','Dennys Frenez','FRENEZ-TALK-2026','30:05-30:25; coordinator caption check table/team entry','collaboration and access',
    'Work in teams with different kinds of expertise.', 'Archaeologists, epigraphers and other relevant specialists with shared data.', 'Organizational; cannot be validated by corpus statistics.', [H,CENSUS], comparisons=ACCESS,
    limit='Caption-mediated attribution; team composition is our implementation suggestion, not a list transcribed from the talk.')
rec('F02','Dennys Frenez','FRENEZ-TALK-2026','24:45-25:40; coordinator caption check regional/chronology entry','context and chronology',
    'Separate inscriptions into chronological and regional corpora for analysis.', 'Secure dates, sites, regional definitions and object links.', 'Partial: current site labels and dated Harappa subsets; broad period coverage is incomplete.', [D1,D2,E], comparisons=REGIONAL,
    limit='His criticism of earlier monolithic studies does not establish that earlier regional work was absent.')
rec('F03','Dennys Frenez','FRENEZ-TALK-2026','28:45-30:40; coordinator caption check frequency entry','context and chronology',
    'Study sign frequency and inventory size against assemblage size, site and context.', 'Per-site artefact/token counts, object types, contextual records and inventory definitions.', 'Partial: counts and types available; excavation exposure is not uniformly recorded.', [D1,D2], comparisons=[compare('FULS-2023','printed/PDF45','shared_priority','Explicitly treats unequal per-site artefact counts and heterogeneous inscribed sets.')],
    limit='The talk reports sign740 near10% and sample-size questions; the row is a research priority, not a verified frequency estimate.')
rec('F04','Dennys Frenez','FRENEZ-TALK-2026','51:00-53:00; coordinator caption check external entry','data and corpora',
    'Study non-canonical inscriptions outside the Indus core for unusual affixes, ordering and sign use.', 'External find locations, images, transcription witnesses and core comparators.', 'Partial: external sample exists; provenance and small counts limit interpretation.', [WEST,D1,D2],
    limit='Patronymics or different languages are his proposed interpretations, not established readings.')
rec('F05','Bryan K. Wells','WELLS-2015','Preface printed viii, PDF12','context and chronology',
    'Define regional differences in text structure in future research.', 'Regional corpora and comparable text-structure measures.', 'Yes for present labels; chronology and missingness need sensitivity analysis.', [D1,D2], comparisons=[compare('RAO-2009','printed13690, PDF6','shared_priority','Proposes a more detailed site-by-site sequential analysis.')])
rec('F06','Bryan K. Wells','WELLS-2015','Preface printed viii, PDF12, paragraph beginning Bigger issues','context and chronology',
    'Establish chronological control to study the development of Indus writing.', 'Corpus with secure dates and regional labels.', 'Partial: dated coverage is limited.', [D1,E,WEST], comparisons=REGIONAL)
rec('F07','Bryan K. Wells','WELLS-2015','Preface printed ix, PDF13','collaboration and access',
    'Pursue international and interdisciplinary cooperation.', 'Cross-institutional archaeological, epigraphic and linguistic collaboration.', 'Organizational; present data can support shared review.', [H,CENSUS], comparisons=ACCESS)
rec('F08','Bryan K. Wells','WELLS-2015','Preface printed x, PDF14','linguistic approaches',
    'Have linguists use detailed structural evidence to identify or eliminate candidate underlying languages.', 'Language expertise and structural evidence grounded in archaeological context.', 'Partial structural tests; language identification cannot be checked with current unlabelled texts.', [D1],
    limit='The proposal assumes underlying language; this repository cannot authenticate candidate-language readings.')
rec('F09','Andreas Fuls','FULS-2023','printed/PDF45, final paragraph','collaboration and access',
    'Make the epigraphic database accessible worldwide and update it after new inscriptions are published.', 'Maintained corpus, images, sign list, permissions and publication updates.', 'Organizational; metadata can be prepared now, access depends on owners.', [H,CENSUS], comparisons=ACCESS)
rec('F10','Andreas Fuls','FULS-2023','printed/PDF45, paragraph beginning Since the inscribed artifacts','context and chronology',
    'Treat inscribed artefacts as heterogeneous sets with different purposes.', 'Site artefact counts, object purposes/types and sign frequencies.', 'Partial: site/type analyses possible; purposes are often unknown.', [D1,D2], comparisons=REGIONAL,
    limit='The same abstract already uses modified chi-square expectations based on unequal per-site artefact counts. It does not provide excavation-area denominators.')
rec('F11','Jonathan Mark Kenoyer','KENOYER-2020','printed223, PDF7','data and corpora',
    'Distinguish pre-firing producer marks from post-firing user or consumer graffiti.', 'Object surfaces, production-stage coding and archaeological documentation.', 'Partial: literature-coded specimens available; corpus-wide coding is incomplete.', [E,D1], comparisons=[compare('VIDALE-2007','Appendix proposal4, printed364','shared_priority','Explicitly separates pre- and post-firing pottery inscriptions and requires direct access.')])
rec('F12','Jonathan Mark Kenoyer','KENOYER-2020','Conclusion printed230, PDF14','new excavation and science',
    'Excavate Early Harappan sites more extensively to increase samples of early writing.', 'Permitted excavation, stratigraphic recording and early-mark expertise.', 'No: requires new field data.', [E,CENSUS], repo='E documents available early evidence; it cannot supply new excavation.')
rec('F13','Jonathan Mark Kenoyer','KENOYER-2020','Conclusion printed230, PDF14','context and chronology',
    'Record and quantify pottery marks in more detail across regions.', 'Regional records of pre- and post-firing marks with dated contexts.', 'Partial: E offers a specimen/source register; new object records are needed.', [E,D1], comparisons=REGIONAL)
rec('F14','Jonathan Mark Kenoyer','KENOYER-2020','printed231, PDF15','collaboration and access',
    'Continue collaboration and publish data in forms scholars can readily access.', 'Author and institution participation, reusable metadata and source rights.', 'Organizational; documentation and access ledgers can be improved now.', [CENSUS,H], comparisons=[compare('WELLS-2015','Preface ix, PDF13','shared_priority','Calls for international and interdisciplinary cooperation.')])
rec('F15','Jonathan Mark Kenoyer','KENOYER-2006','Conclusion printed21, scan PDF8 right column','context and chronology',
    'Re-examine seals and inscribed objects from earlier excavations to sort them chronologically.', 'Earlier excavation registers, physical objects and chronology expertise.', 'Partial: published registers can be audited; object access remains necessary.', [D1,E,CENSUS], comparisons=[compare('KONASUKAWA-2023','printed/PDF50, paragraph2','shared_priority','Requires seal chronology in script discussion.')])
rec('F16','Rajesh P. N. Rao and coauthors','RAO-2009','Discussion printed13690, PDF6 paragraph1','data and corpora',
    'Repeat the analysis with all known texts and newer sign lists.', 'Versioned corpus, sign-list concordances and compatible model inputs.', 'Partial: present normalized corpus supports a new versioned analysis, not all known texts.', [D1,H,CENSUS],
    limit='Current corpus completeness must be measured; all known texts is an objective, not present coverage.')
rec('F17','Rajesh P. N. Rao and coauthors','RAO-2009','Discussion printed13690, PDF6 paragraph1','context and chronology',
    'Analyze sequential sign patterns site by site.', 'Site labels, enough texts within sites and uncertainty-aware sequence measures.', 'Yes for covered sites; small external/site samples constrain estimates.', [D1,D2,WEST], comparisons=REGIONAL)
rec('F18','Rajesh P. N. Rao and coauthors','RAO-2009','Discussion printed13690, PDF6 paragraph2','computational method',
    'Use statistical and machine-learning techniques to infer grammar directly from inscriptions.', 'Corpus, statistical modelling and language-informed validation.', 'Partial: structural models possible; linguistic grammar remains unverified.', [D1,CONTROLS],
    comparisons=[compare('SPROAT-2013','section9, printed/PDF86','shared_method_with_different_inference','Names grammar induction as possible future work but requires specifically linguistic structure.')])
rec('F19','Nisha Yadav','YADAV-2013','Conclusions printed96-98, PDF30-32','context and chronology',
    'Include site and object-type fluctuations in models interpreting the inscriptions.', 'Object types, sites, text lengths and sign distributions.', 'Yes for present site/type labels; interpretation needs additional evidence.', [D1,D2], comparisons=[compare('FULS-2023','printed/PDF45','shared_priority','States that the artefact sets should not be treated as homogeneous.')])
rec('F20','Nisha Yadav','YADAV-2013','Conclusions printed98, PDF32 final substantive paragraph','data and corpora',
    'Analyze stylistic sign variants across sites and object types in detail.', 'Images, variant judgements and regional/object metadata.', 'Partial: images and IDs exist; expert variant adjudication is required.', [H,D1],
    comparisons=[compare('VAHIA-2025','printed43, PDF40','shared_priority','Calls for isolating composite signs and identifying add-on elements.')])
rec('F21','Sundar Ganesan, Chandrasekhar Subramanian, G. C. Suresh Babu and Iravatham Mahadevan','GANESAN-ETAL-2010','section8, OCR reader pp.5-6; section1 reader p.1','linguistic approaches',
    'Extend textual and contextual analysis of frequent segments toward identifying the language.', 'Frequent signs, pairs/triplets, site, object and field-symbol data.', 'Partial: segment/context tables can be recomputed; language identification remains unverified.', [D1,D2],
    limit='Stated research goal in section8, visually confirmed on original reader p.6. The first-pass reproducibility/duplicate recommendation was unsupported and removed.')
rec('F22','Asko Parpola','PARPOLA-2008','printed127, local volume PDF127, final paragraph','linguistic approaches',
    'Establish the iconic meaning of signs before considering rebus uses.', 'Graphic variants, pictorial identification and archaeological comparators.', 'Partial: graphic/context tests possible; iconic identification and rebus readings are hypotheses.', [G,H],
    comparisons=[compare('FSW-2004','printed46, PDF28','disputes_underlying_thesis','Assumes non-writing in its cultural-cohesion agenda; Parpola explicitly challenges this thesis.')])
rec('F23','Steve Farmer, Richard Sproat and Michael Witzel','FSW-2004','printed37 n.23, PDF19','data and corpora',
    'Study rare signs to investigate how the symbol system functioned and was controlled.', 'Sign-by-sign audit, definitions and dated rare-sign occurrences.', 'Partial: rarity can be measured; catalogue definitions and date coverage limit historical inference.', [D1,H], comparisons=DEBATE,
    limit='The dispute concerns their non-writing interpretation and rarity arguments, not the usefulness of studying rare signs.')
rec('F24','Steve Farmer, Richard Sproat and Michael Witzel','FSW-2004','printed43 n.28, PDF25','context and chronology',
    'Account for possible second-hand seals before linking Near Eastern seal symbols to users.', 'Find contexts, use wear, ownership histories and comparable foreign seals.', 'Partial: published histories can be audited; many ownership histories are unavailable.', [WEST,CENSUS])
rec('F25','Steve Farmer, Richard Sproat and Michael Witzel','FSW-2004','printed44, PDF26','context and chronology',
    'Explore whether sign-frequency changes in nonlinguistic models can indicate historical developments.', 'Dated strata, palaeography and contextual histories.', 'Partial for dated Harappa subsets; broad historical attribution is unverified.', [D1,D2], comparisons=DEBATE,
    limit='They frame this within a nonlinguistic interpretation; frequency changes alone do not identify religious or political events.')
rec('F26','Steve Farmer, Richard Sproat and Michael Witzel','FSW-2004','printed46, PDF28 final paragraph before next heading','context and chronology',
    'Investigate the symbols\' role in cultural cohesion and its decline.', 'Dated distributions, social context and independent historical evidence.', 'Partial descriptive comparisons; causal social explanation needs more evidence.', [D1,D2], comparisons=DEBATE,
    limit='Their stated challenge assumes non-writing; opened replies contest that premise.')
rec('F27','Richard Sproat','SPROAT-2010','printed592, PDF8 final paragraph of section2','computational method',
    'Validate proposed classifiers on a large sample of known linguistic and nonlinguistic systems.', 'Attested comparison corpora, measured classification errors and adequate sample sizes.', 'Partial: existing controls can be audited and extended with rights-cleared comparators.', [CONTROLS,H], comparisons=STATS,
    limit='Replies contest the statistical inference and his description of earlier work; they do not reject the collection of comparison corpora.')
rec('F28','Richard Sproat','SPROAT-2010','section3 printed593, PDF9','collaboration and access',
    'Include qualified computational linguists in peer review of statistical claims about ancient symbols.', 'Specialist review and source/sample documentation.', 'Organizational; repository review can adopt this now.', [H],
    comparisons=[compare('RAO-REPLY-2010','printed803-804, PDF9-10','direct_dispute_on_assessment','Challenges his account of computational linguistics\' contribution and defends statistical work.')])
rec('F29','Richard Sproat','SPROAT-2013','section9 printed/PDF86, paragraph2','data and corpora',
    'Extend the taxonomy and corpora of nonlinguistic systems to cover additional groups.', 'Documented symbol corpora with explicit functional categories and permissions.', 'Partial: current controls cover a limited range of systems.', [CONTROLS,H],
    comparisons=[compare('RAO-REPLY-2015','printed e203, PDF6 section6','explicit_agreement_on_resource','Commends the assembly of larger nonlinguistic corpora while disputing the inference.')])
rec('F30','Richard Sproat','SPROAT-2013','section9 printed/PDF85-86','computational method',
    'Investigate features independent of text length, including grammar induction, for system classification.', 'Attested comparators, length-controlled features and grammar-induction experiments.', 'Partial: structural controls possible; specifically linguistic hierarchy is difficult to verify.', [CONTROLS,D1], comparisons=STATS,
    limit='2013 author monograph; do not cite this as a recommendation in the unopened 2014 main article.')
rec('F31','Rajesh P. N. Rao and coauthors','RAO-REPLY-2010','Conclusion printed803, PDF9','computational method',
    'Develop better statistical tests using multiple properties in an inductive framework.', 'Multiple measurements, uncertainty estimates and comparison evidence.', 'Partial: formal structural tests possible; posterior language claims depend on unverified model assumptions.', [CONTROLS,D1],
    comparisons=[compare('SPROAT-REPLY-2010','author manuscript PDF1, section2','direct_counterreply','Maintains that his original Science-paper critique concerns that paper\'s merits, even if later results are correct.')])
rec('F32','Massimo Vidale','VIDALE-2007','Appendix proposal1, printed363','collaboration and access',
    'Form an international expert committee to adjudicate signs, variants and unique cases.', 'Experts familiar with objects, contexts and inscriptions; agreed decision rules.', 'Organizational; candidate variant lists available, adjudication requires experts.', [H,CENSUS], comparisons=[compare('POSSEHL-PAGE-1996','final agenda paragraph, principle1','shared_priority','Calls for an authoritative sign list and orthographic research.')])
rec('F33','Massimo Vidale','VIDALE-2007','Appendix proposal2, printed363','data and corpora',
    'Create standardized Indus fonts, controlled additions and a central accessible contextual archive.', 'Accepted sign list, software, contextual records and rights agreements.', 'Partial metadata/software work; authoritative additions and access require collaboration.', [H,CENSUS], comparisons=ACCESS)
rec('F34','Massimo Vidale','VIDALE-2007','Appendix proposal3, printed363','context and chronology',
    'Coordinate international palaeographic research on physical objects through student theses.', 'Direct object access, dated Harappa/Nausharo frames and coordinated supervision.', 'Partial published-record audit; physical inspection and supervision require collaboration.', [D1,E,CENSUS], comparisons=[compare('KENOYER-2006','printed21, scan PDF8','shared_priority','Calls for chronological sorting of earlier-excavation objects.')])
rec('F35','Massimo Vidale','VIDALE-2007','Appendix proposal4, printed363-364','context and chronology',
    'Separate inscriptions by material, function, location and production stage before synthesis.', 'Physical artefacts, seal/sealing links, medium, inscription position and pre/post-firing coding.', 'Partial: present site/type strata help; direct access and detailed material coding remain missing.', [D1,D2,E], comparisons=REGIONAL,
    limit='His prescription explicitly requires direct access for pottery marks and begins with very small analytical contexts.')
rec('F36','Bahata Ansumali Mukhopadhyay','MUKHOPADHYAY-2023','Introduction article p.2, PDF2','linguistic approaches',
    'Narrow the semantic scope of inscriptions before assigning individual signs values.', 'Archaeological use contexts and sign-pattern constraints across inscriptions.', 'Partial: contextual falsification possible; proposed semantic domains remain hypotheses.', [D2,H],
    comparisons=[compare('PARPOLA-2008','printed127, PDF127','different_stated_sequence','Starts with iconic meanings before rebus analysis; this is a methodological difference, not a published reply to Mukhopadhyay.')])
rec('F37','Bahata Ansumali Mukhopadhyay','MUKHOPADHYAY-2023','article p.29, PDF29, paragraph beginning In this context','new excavation and science',
    'Test whether stamped pointed-base goblets were standardized vessels in commercial administration.', 'Measured goblets, stamps, capacities, dates and use contexts.', 'Partial literature audit; adequate measurements and use evidence must be obtained.', [D2,H],
    limit='Explicit future test within her administrative hypothesis; no direct reply located.')
rec('F38','Rajesh P. N. Rao','RAO-2018','Conclusions printed525, PDF8','new excavation and science',
    'Obtain additional analysis and archaeological evidence to test proposed economic functions of text components.', 'Contextual economic evidence and independently testable component predictions.', 'Partial: internal patterns available; external anchors needed.', [D2,H],
    limit='Proto-Elamite parallels motivate his hypotheses; they do not establish Indus meanings.')
rec('F39','Dennys Frenez','FRENEZ-2018','printed186 n.11, PDF27; model continues p.187/PDF28','context and chronology',
    'Further test the application of branding assumptions with a stronger theoretical basis.', 'Explicit branding-model predictions, dated seal motifs and production/use evidence.', 'Partial: concentration and dated motif patterns are measured; regulatory mechanisms need evidence.', [D1,D2],
    limit='This explicit test request accompanies the oligopoly hypothesis; the model itself is recorded separately in positions.json.')
rec('F40','Marta Ameri','AMERI-2013','Conclusion printed371, PDF23 paragraph1','context and chronology',
    'Conduct more detailed studies of particular material classes, including architecture, to clarify regional differences.', 'Comparable regional material inventories and specialist studies.', 'Partial for seals; broader material classes require more data.', [D1,D2,CENSUS], comparisons=REGIONAL)
rec('F41','Cameron A. Petrie and Frank Lynam','PETRIE-LYNAM-2020','accepted manuscript PDF25, lines656-658','new excavation and science',
    'Investigate local subsistence, geomorphology and hydrology to understand settlement lifeways.', 'Local bioarchaeological, geomorphological and hydrological observations.', 'No complete local datasets in this package; requires specialist field/source work.', [CENSUS],
    limit='Their settlement-context priority does not by itself prescribe a script-decipherment method.')
rec('F42','Cameron A. Petrie and Frank Lynam','PETRIE-LYNAM-2020','accepted manuscript PDF25, lines675-678','computational method',
    'Explore Cholistan mobility models linking sedentary and pastoral communities.', 'Survey chronology, settlement durations and demographic/mobility models.', 'Partial published survey reanalysis; credible local input distributions must be obtained.', [CENSUS,H],
    limit='Specific to their Cholistan interpretation, which they say needs further evidence.')
rec('F43','Randall William Law','LAW-2011','Chapter14 printed500-501, PDF1-2, steatite paragraph','new excavation and science',
    'Expand geological sampling of steatite sources in the northern regions and other unresolved source areas.', 'Geological field sampling, permission and comparative artefact chemistry.', 'No: needs samples and scientific analysis.', [CENSUS,H])
rec('F44','Randall William Law','LAW-2011','Chapter14 printed503, PDF4 paragraph2','new excavation and science',
    'Conduct question-oriented excavation or re-excavation in the northern borderlands to study interaction.', 'Contextual field records, material assemblages and regional exchange questions.', 'No: requires new contextual data.', [CENSUS],
    limit='Names Ropar, Manda, Musa Khel and Hisham Dheri; this is an interaction agenda, not an assigned linguistic value.')
rec('F45','Randall William Law','LAW-2011','Chapter14 printed503, PDF4 final paragraph','collaboration and access',
    'Collaborate internationally on a long-term program to source stone and metal artefacts from large and small sites.', 'Institutional object access, geological reference sets and laboratory expertise.', 'Partial collection planning; sourcing requires physical materials and facilities.', [CENSUS,H], comparisons=ACCESS)
rec('F46','Heather M.-L. Miller','MILLER-PROJECT-2025','Biography research paragraph, project launched2025','new excavation and science',
    'Use technological evidence to identify possible ancient bureaucracies and record-keeping centres.', 'Material/technology records, artefact associations and specialist collaboration.', 'Partial: candidate-context inventory possible; technological study requires additional records.', [D2,H,CENSUS],
    limit='Author\'s stated project aim on an undated institutional page; replace, do not rehabilitate, the nonexistent 2013 citation.')
rec('F47','Mayank N. Vahia','VAHIA-2025','printed35 and47, PDF34 and44','context and chronology',
    'Understand sign modifications and other object imagery within the wider Harappan context.', 'Sign variants, motifs, object forms and cultural context.', 'Partial: object/type and motif data exist; contextual interpretation remains open.', [D2,H], comparisons=REGIONAL)
rec('F48','Mayank N. Vahia','VAHIA-2025','printed43, PDF40','data and corpora',
    'Isolate composite signs and identify their add-on elements for study.', 'Images, component coding and expert allograph decisions.', 'Partial: image inventory available; component labels need adjudication.', [H,G], comparisons=[compare('YADAV-2013','printed98, PDF32','shared_priority','Calls for detailed analysis of stylistic sign variants.')])
rec('F49','Gregory L. Possehl','POSSEHL-PAGE-1996','final agenda paragraph, principle1','data and corpora',
    'Research form and orthography more thoroughly and develop an authoritative sign list.', 'Images, orthographic analyses and expert sign-list decisions.', 'Partial: variants can be inventoried; authority requires collective adjudication.', [H,CENSUS], comparisons=[compare('VIDALE-2007','Appendix proposal1, printed363','shared_priority','Calls for expert adjudication of signs and variants.')])
rec('F50','Gregory L. Possehl','POSSEHL-PAGE-1996','final agenda paragraph, principle2','collaboration and access',
    'Study the script through many small-scale research efforts.', 'Bounded research questions and shared cumulative records.', 'Organizational; existing packages provide bounded work units.', [H,D1,D2,E,G], comparisons=[compare('VIDALE-2007','Appendix proposal4, printed364','shared_priority','Begins with fragmented small contextual studies before synthesis.')])
rec('F51','Gregory L. Possehl','POSSEHL-PAGE-1996','final agenda paragraph, principle3','computational method',
    'Test decipherment claims through multiple independent lines of inference.', 'Independent archaeological, epigraphic and other evidence with explicit predictions.', 'Partial: independent structural checks possible; meanings have no authenticated labels.', [D1,D2,E,G],
    limit='The institutional page was read through a proxy; the book passage itself remains unopened.')
rec('F52','K. Rajan and R. Sivanantham','RAJAN-SIVANANTHAM-2025','PDF8 final two paragraphs','new excavation and science',
    'Document graffiti potsherds and obtain further material evidence to evaluate proposed cultural contact.', 'Dated pottery, material associations, exploration, excavation and scientific study.', 'Partial corpus/shape controls available; dated contact evidence remains incomplete.', [E,G,CENSUS],
    limit='Their proposed contact and contemporaneity are hypotheses; additional-material request is explicit. No blinded comparison design is attributed to them.')
rec('F53','Rajesh P. N. Rao (interviewed)','RAO-INTERVIEW-2026','final three Rao-attributed paragraphs; number-system paragraph','computational method',
    'Investigate partial reconstruction of the number system using tally marks and weight ratios.', 'Tally-bearing texts, metrological data and independent numerical constraints.', 'Partial: candidate numerical patterns can be tested; semantic labels remain uncertain.', [D2,H],
    limit='Interview suggestion reported by Jarus, not a proven numerical decipherment.')
rec('F54','Rajesh P. N. Rao (interviewed)','RAO-INTERVIEW-2026','final Rao-attributed paragraph, excavation','new excavation and science',
    'Seek more texts through excavation, hoping for longer or bilingual inscriptions.', 'Permitted excavation at unexcavated sites and contextual inscription recording.', 'No: requires new field discoveries.', [CENSUS,E],
    limit='A stated hope for evidence, not a prediction that such texts exist.')
rec('F55','Shereen Ratnagar','RATNAGAR-INTERVIEW-2018','figurine discussion, paragraph referring to ICANE and dog femur bones','new excavation and science',
    'Reconsider routine collection of plant and animal remains when specialist studies become repetitive.', 'Question-led sampling plans and consultation with specialists.', 'Organizational for future collection; no field collection undertaken here.', [CENSUS],
    limit='Her explicit methodological concern follows an anecdote about a Turkish professor; it is not a call to stop collecting environmental evidence.')
rec('F56','Ayumu Konasukawa','KONASUKAWA-2023','printed/PDF50 paragraph2','context and chronology',
    'Take seal chronology into account when discussing the Indus script.', 'Dated seal typology and specimen-level provenance.', 'Partial: dated Harappa material supports bounded comparisons.', [D1,D2,E], comparisons=[compare('KENOYER-2006','printed21, scan PDF8','shared_priority','Calls for chronological sorting of earlier-excavation seals.')])
rec('F57','Adam S. Green','GREEN-2021','printed182, PDF30, penultimate paragraph','context and chronology',
    'Research potential inequalities associated with age, gender, material culture and urban infrastructure.',
    'Mortuary and settlement records with demographic and contextual comparisons.',
    'Limited: present seal/context data cannot measure these inequalities directly.', [CENSUS,H],
    limit='Agenda arises within his egalitarian interpretation; no endorsement of that interpretation is implied.')
rec('F58','Adam S. Green','GREEN-2021','printed183, PDF31, paragraph ending Exploring these questions','context and chronology',
    'Ask whether heterarchical corporate groups were more numerous in the Indus than in societies with exclusionary elites, and why.',
    'Comparable corporate-group indicators across ancient societies.',
    'Limited: existing motif data do not identify corporate-group counts.', [D2,H],
    limit='His comparative question does not establish a mapping from motifs to groups.')
rec('F59','Adam S. Green','GREEN-2021','printed184, PDF32, first paragraph','context and chronology',
    'Explore specialization, egalitarian growth and attachments among heterarchical corporate groups.',
    'Craft-production contexts and comparative evidence of group attachments.',
    'Limited: requires production-context joins beyond present inscriptions.', [D2,CENSUS],
    limit='The prescription is separate from the carver-identification method in his 2016 paper.')

positions = [
    dict(id='P01',source_id='FRENEZ-2018',locator='printed186-187, PDF27-28',status='Exploratory',
         position='Proposes standard-seal motifs as an unbalanced oligopoly of formal socio-economic identities.',
         observation='Uses unicorn share about65% from Ameri2013 Table19.1 and motif persistence to motivate the model.',
         scope='Tentative social interpretation, not evidence that regulatory mechanisms have been excavated.',repository_links=[D1,D2]),
    dict(id='P02',source_id='FRENEZ-2018',locator='printed167,170-171, PDF8,11-12',status='Exploratory',
         position='Places script/seal development within indigenous traditions; dates standard seals and early script at Harappa to2800-2600BCE.',
         observation='Connects post-firing graffiti and early seals, with earlier pottery-to-seal experiments noted in footnote5.',
         scope='Written parallel to the origin position in the talk; p.167 concerns urban tradition broadly.',repository_links=[E,D1]),
    dict(id='P03',source_id='FRENEZ-TALK-2026',locator='41:30-43:30,42:55-43:30,47:45-48:30',status='Exploratory',
         position='Associates standard seals with a persistent oligopoly and corporate or formal roles in administration.',
         observation='Coordinator caption check reports the unicorn majority and stable motif frequencies as his argument.',
         scope='Timestamped attribution mediated by auto-caption check; stability is a prediction to test with dated samples.',repository_links=[D1,D2]),
    dict(id='P04',source_id='FRENEZ-TALK-2026',locator='16:20-17:05,48:25,53:05',status='Exploratory',
         position='Argues Indus people knew neighbouring writing but deliberately developed different conventions.',
         observation='Coordinator reports his rejection of direct diffusion and long-narrative conventions.',
         scope='No written source located here establishes deliberate rejection as archaeological fact.',repository_links=[E]),
    dict(id='P05',source_id='FRENEZ-TALK-2026',locator='17:05-24:00,53:05',status='Exploratory',
         position='Places conceptual foundations before2800BCE and script consolidation during the early third millennium.',
         observation='Caption check distinguishes early marks, seals and later script elaboration.',
         scope='Exact caption place names can be garbled; use specimen/source records in E for archaeological dates.',repository_links=[E]),
    dict(id='P06',source_id='FRENEZ-2021',locator='complete author abstract, middle and final paragraphs',status='Exploratory',
         position='Attributes local script development to3200-2600BCE and emphasizes coherent synchronic corpora and discovery contexts.',
         observation='Explicit abstract for the2021 Bologna workshop; date differs from the2025 seminar programme.',
         scope='Written abstract parallel to talk position, not a substitute for the unpublished full talk.',repository_links=[E,D1]),
    dict(id='P07',source_id='FRENEZ-2018',locator='printed171 n.6, PDF12',status='Exploratory',
         position='Identifies absence of a systematic count of standard seals made of high-fired steatite.',
         observation='His approximate percentages derive from grayscale catalogue photographs.',
         scope='Research gap; no explicit new study prescription in this footnote, so excluded from recommendations.',repository_links=[H,D2]),
]

# Rows absent from recommendations are coverage records, never empty recommendations.
coverage = [
    dict(researcher='Adam S. Green',source_ids=['GREEN-2016','GREEN-2021'],disposition='2016 method excluded; 2021 explicit agendas admitted as F57-F59',
         reason='No explicit future recommendation located in the opened 2016 extracts; its full paper remains unread. A final search located the 2021 review, whose explicit future-work passages on pp.182-184 qualify.'),
    dict(researcher='Rita P. Wright',source_ids=[],disposition='Unresolved coverage gap',
         reason='2010 Cambridge excerpt search identified exact book and author, but direct download timed out. No page-level agenda admitted. First-pass contextual recommendation was removed.'),
    dict(researcher='Vasant Shinde',source_ids=[],disposition='Unresolved coverage gap',
         reason='Ancient Asia DOI10.5334/aa.12317 web open failed; two publisher routes returned404. No recommendation admitted.'),
    dict(researcher='R. S. Bisht',source_ids=[],disposition='Unresolved coverage gap',
         reason='No inspectable recommendation passage in the available excavation-report lead; documentation of Dholavira is not itself an agenda.'),
    dict(researcher='Pallavee Gokhale',source_ids=['GOKHALE-2023'],disposition='Opened abstract; retained contextual critique, no recommendation row',
         reason='The abstract criticizes neglect of artefact purpose/place and emphasizes archaeological inputs, but the inspected text does not prescribe a specific future study. See missing-item disposition.'),
    dict(researcher='Dennys Frenez and Massimo Vidale',source_ids=['FRENEZ-VIDALE-2023'],disposition='Opened abstract; retained background, no recommendation row',
         reason='External-seal presentation scope and claims about standardization are not explicit future recommendations. Frenez lecture and Vidale Appendix provide direct prescriptions.'),
]

# Corrections cover all fourteen source records identified in source-checks.csv.
corrections = [
 ('FULS-2022','FULS-2023','Wrong title, year and venue; replace with opened2023 abstract p.45.'),
 ('KENoyer-2006','KENOYER-2006','Venue corrected from visually inspected RIHN proceedings cover.'),
 ('FRENEZ-2017','FRENEZ-2018','Correct chapter title and2018 volume; retain2017 copyright-footer distinction.'),
 ('FRENZEZ-OMAN-2022',None,'Drop recommendation. Actual source is Bronze Age Salūt (ST1) and the Indus Civilization: recent discoveries and new insights on regional interaction, Frenez, Degli Esposti, Méry and Kenoyer,2016, Proceedings of the Seminar for Arabian Studies46:107-124. Local frenez_2016_salut.pdf title and bibliography checked.'),
 ('FRENEZ-2005',None,'Drop recommendation. Opened author-deposited Zenodo record https://zenodo.org/records/5514283: Dennys Frenez and Maurizio Tosi, Lothal Sealings: Records from an Indus Civilization town at the eastern end of the maritime trade networks across the Arabian Sea, Studi in Onore di Enrica Fiandra. Contributi di archeologia egea e vicinorientale, De Boccard, Paris,2005,pp.65-103. Saved frenez_2005_zenodo.html in local raw rebuild directory. Record title agrees with official CV; Ameri bibliography differs. No recommendation or comparison attributed from the descriptive abstract.'),
 ('FRENEZ-2024',None,'Drop recommendation. Crossref DOI record opened7October2026: Dennys Frenez, Were the Cretulae (Clay Sealings) from the Indus Port Town of Lothal Part of an Administrative Archive? Contextual, Interpretive, and Comparative Evidence, South Asian Studies40(2):214-234,2024, DOI10.1080/02666030.2024.2401206. Saved frenez_2024_crossref.json in local raw rebuild directory. Published title differs from forthcoming CV title; article text inaccessible, no recommendation attributed.'),
 ('GREEN-2016','GREEN-2016','Correct title, Journal of Archaeological Science72:128-141 and DOI; author extracts opened, no method-as-recommendation row.'),
 ('YADAV-2010',None,'Drop inferred held-out-validation recommendation. Correct author order: Nisha Yadav, Hrishikesh Joglekar, Rajesh P. N. Rao, Mayank N. Vahia, Ronojoy Adhikari, Iravatham Mahadevan. Statistical analysis of the Indus script using n-grams, PLoS ONE5(3):e9506,2010, DOI10.1371/journal.pone.0009506; checked in Rao2010 bibliography p.805.'),
 ('SPROAT-2014','SPROAT-2014','Correct main DOI10.1353/lan.2014.0031; ACLJ10-3012 is2010. Main article unavailable; abstract and published replies read. Actual future-work recommendations use2010 and2013 sources.'),
 ('RAO-2026-INTERVIEW','RAO-INTERVIEW-2026','Article by Owen Jarus,15March2026; Rao interviewed/quoted, not article author.'),
 ('PETRIE-2020','PETRIE-LYNAM-2020','Coauthor Frank Lynam; Journal of Field Archaeology45(1):1-15,2020issue/2019online. Opened accepted manuscript.'),
 ('MILLER-2013','MILLER-PROJECT-2025','Nonexistent source removed; replaced with actual institutional Biography project aim. Undated webpage, project launched2025.'),
 ('RAJAN-2025','RAJAN-SIVANANTHAM-2025','Correct accessible brochure URL and source scope; admit only explicit additional-evidence request onPDF8.'),
 ('POSSEHL-2002','POSSEHL-PAGE-1996','Unsupported agenda attribution to2002 book removed; three principles from opened author institutional page about1996book, through identified proxy.'),
]

# Final polish is an explicit dated correction layer, not a new source survey.
_polished = runpy.run_path(str(Path(__file__).with_name('polish_coding.py')))['apply'](globals().copy())
for _key in ['sources','recommendations','positions','coverage','corrections','author_groups','action_ranking']:
    globals()[_key] = _polished[_key]
