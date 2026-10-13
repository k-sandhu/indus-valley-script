"""Build authored control ledgers from pinned local witnesses and selected reading."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from acquire_controls import REPO, RAW

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inherited(path, url, prior_record):
    p = REPO / path
    return {'path': path, 'bytes': p.stat().st_size, 'sha256': sha(p),
            'url': url, 'inherited_from': prior_record,
            'rights_status': 'rights-unverified', 'redistribution': 'local-only'}


def source(sid, title, authors, year, scope, witnesses, **extra):
    return {'source_id': sid, 'title': title, 'authors': authors, 'publication_year': year,
            'selected_primary_work': True, 'reading_scope': scope, 'witnesses': witnesses,
            'rights_status': 'rights-unverified', 'redistribution': 'local-only', **extra}


def obs(oid, sid, locus, statement, kind, bearing, limit, anchor=None, pdf_page=None):
    return {'observation_id': oid, 'source_id': sid, 'locus': locus,
            'statement': statement, 'kind': kind, 'rival_bearing': bearing,
            'inference_limit': limit, 'source_anchor': anchor,
            'pdf_page_one_based': pdf_page}


if __name__ == '__main__':
    for name in ['sources.json', 'observations.json']:
        if (HERE / name).exists():
            raise FileExistsError(HERE / name)
    captures = [item for version in [1, 2, 3]
                for item in read(RAW / f'acquisition-v{version}.json')]
    by_route = {r['route_id']: r for r in captures}
    derivatives = read(RAW / 'extraction-v1.json')['derivatives']
    sources = [
        source('R01', 'The Rigveda: The Earliest Religious Poetry of India',
               ['Stephanie W. Jamison', 'Joel P. Brereton'], 2014,
               'Printed p.5, pp.9–10 and14–17. First excerpt PDF pp.5,9,10; second excerpt PDF pp.2–5. Selected introduction only; no entire translation reading.',
               [inherited('data/raw/2026-10-11-early-indian-continuity/review/jamison2014-2-15.pdf',
                          'https://vedisk.sites.ku.dk/files/2021/09/Jamison-Brereton-s.-2-15.pdf',
                          'experiments/2026-10-11-early-indian-continuity/review/sources.json#JB2014'),
                inherited('data/raw/2026-10-11-early-indian-continuity/review/jamison2014-13-22.pdf',
                          'https://vedisk.sites.ku.dk/files/2021/09/13-22-Stephanie_W_Jamison_Joel_P_Brereton_The.pdf',
                          'experiments/2026-10-11-early-indian-continuity/review/sources.json#JB2014')],
               primary_url='https://vedisk.sites.ku.dk/files/2021/09/Jamison-Brereton-s.-2-15.pdf',
               dependency_note='The overlapping excerpts are one work. The new review reuses the previous exact bytes and independently reads the selected passages.',
               rights_observation='Copyrighted Oxford introduction; no redistribution permission observed.'),
        source('R02', 'Introduction to Old Avestan: lessons and exercises', ['P. O. Skjærvø'], 2006,
               'Teaching-edition title/header and PDF metadata; complete relevant pages35,70,101,123,136,161–162. Y45.1 in full; selected translated snippets of Y31.9–11,33.6,46.14. Poppler renders of35,70,123,161–162 visually inspected. No manuscript collation or whole Gāthā corpus reading.',
               [by_route['oldavestan-lessons-lexicons'], by_route['oldavestan-primer-swissbay']],
               primary_url='https://www.lexicons.ru/old/a/avestan/_pdf/old-avestan-exercises.pdf',
               edition_note='169-page author-attributed teaching edition. PDF title is Microsoft Word - Old Avestan PrimerLessons.doc, author P Oktor Skjaervo, creation date25September2006. Printed headers agree. The old official Harvard index returned404.',
               dependency_note='The two public mirrors have identical SHA256 and are one witness lineage. Teaching selection supplies no frequency denominator.',
               composition_date='Not established by this teaching witness; edition date2006 does not date Old Avestan composition.'),
        source('R03', 'HAOMA ii. THE RITUALS', ['Mary Boyce'], 2003,
               'Opening comparative paragraph, source/account identification and selected paragraph connecting the second preparation to Old Avestan liturgy. Full HTML acquired previously; no claim that all described modern rites are Old Avestan.',
               [inherited('data/raw/2026-10-11-early-indian-continuity/review/haoma-rituals.html',
                          'https://www.iranicaonline.org/articles/haoma-ii/',
                          'experiments/2026-10-11-early-indian-continuity/review/sources.json#BOY2003')],
               primary_url='https://www.iranicaonline.org/articles/haoma-ii/',
               publication_date='15December2003', last_updated='12December2013',
               dependency_note='Scholarly comparison of several textual and ethnographic strata, not a separate Bronze Age observation for every ritual detail.'),
        source('R04', 'The formation of human populations in South and Central Asia',
               ['Vagheesh M. Narasimhan et al.'], 2019,
               'Author PDF pp.1–2 summary/introduction; pp.9,12,13 in full at the selected findings/discussion; Fig.3 on PDF p.9 visually checked. No supplement or genetic reanalysis.',
               [inherited('data/raw/2026-10-12-transmission-hypothesis/coordinator/population-v1/narasimhan2019-author.pdf',
                          'https://www.eva.mpg.de/documents/AAAS/Narasimhan_Formation_Science_2019_3166350.pdf',
                          'experiments/2026-10-12-transmission-hypothesis/coordinator/sources-v2.json#C01')],
               primary_url='https://www.eva.mpg.de/documents/AAAS/Narasimhan_Formation_Science_2019_3166350.pdf',
               doi='10.1126/science.aat7487', dependency_note='Shared exact bytes with coordinator C01; independent readers are not independent scientific datasets.'),
        source('R05', 'The Development of the Vedic Canon and its Schools: The Social and Political Milieu',
               ['Michael Witzel'], 1997,
               'Author PDF pp.1–3,8–10,24,79–80; printed pp.258–259,264–266,280,335–336. PDF pp.3,80 rendered and visually checked. Selected canon/school discussion, not all93pages.',
               [by_route['witzel1997-author-tls-exception']],
               primary_url='https://michaelwitzel.org/wp-content/uploads/2014/06/canon.pdf',
               doi='10.11588/xarep.00000110',
               edition_note='Author PDF with93pages and creation metadata2001; header identifies the1997 edited-volume chapter. Printed locators are those actually visible in this witness.',
               dependency_note='Kuru collection and school geography are attributed scholarly reconstructions. Jamison–Brereton explicitly draws on this work, so their agreement is dependent.',
               transport_note='Normal verified-TLS author requests failed hostname validation; institutional route returned a challenge. The successful public GET used a disclosed per-request TLS exception.'),
        {'source_id': 'R06', 'title': 'The Theory of Practice and the Practice of Theory in Indian Intellectual History',
         'authors': ['Sheldon Pollock'], 'publication_year': 1985, 'selected_primary_work': False,
         'doi': '10.2307/601525', 'reading_scope': 'Unavailable primary text. Search metadata only; secondary summaries excluded from substantive observations.',
         'witnesses': [], 'excluded_access_routes': [by_route[k] for k in ['pollock1985-jstor', 'pollock-papers-index', 'pollock1985-doi']],
         'rights_status': 'rights-unverified', 'redistribution': 'local-only',
         'role': 'Prespecified unfulfilled target; no inference from its unseen argument.'},
        source('R07', 'KAYĀNIĀN i. Kavi: Avestan kauui, Pahlavi kay', ['Prods Oktor Skjærvø'], 2013,
               'Header/date; opening definition, Indo-Iranian/Old Indic comparison, Old Avestan role vocabulary and Vištāspa/sovereignty paragraphs. Extraction lines18–275 inspected; later Young Avestan/Middle Iranian discussion not used.',
               [by_route['skjaervo-kayanian']], primary_url='https://www.iranicaonline.org/articles/kayanian-i/',
               publication_date='15May2013', last_updated='4November2016',
               selection_note='Exploratory seventh target after access results and its search snippet were visible, fixed in AMENDMENT-source-access.md.',
               dependency_note='Same scholar as R02; comparative interpretation and teaching edition are separate works, not independent historical attestations.'),
    ]
    observations = [
        obs('O-R01-1', 'R01', 'Printed pp.9–10; first excerpt PDF pp.9–10',
            'The introduction describes poet-patron exchange and attributes the poet’s social position and patronage role to Indo-Iranian and Indo-European inheritance.',
            'attributed comparative reconstruction', 'R2 supplies an ancestral explanation for this role; local contributions to particular practices remain possible.',
            'The claim is a comparative argument, not an observed Bronze Age teacher chain or proof that every institutional feature is inherited.',
            'social position', 10),
        obs('O-R01-2', 'R01', 'Printed p.5 and pp.14–17; first PDF p.5, second PDF pp.2–5',
            'The authors separate hymn composition from older conventions, family collections, later consolidation and school recensions; the Kuru consolidation is attributed to Witzel.',
            'attributed textual chronology and organization', 'R2 and R5 can both contribute; a received canon can combine materials of different ages.',
            'The approximate composition estimate does not date every represented practice, and collection dates remain scholarly estimates.',
            'Family Books', 2),
        obs('O-R01-3', 'R01', 'Printed p.14; second excerpt PDF p.2',
            'The introduction describes shared underlying poetic formulae and identifies parallels in Old Avestan while allowing creative changes to their verbal realization.',
            'attributed comparative verbal inheritance', 'R2 concerns formula history; R5 can reorganize inherited verbal material.',
            'A formula comparison does not by itself trace the technical content of an agricultural image.',
            'Old Avestan', 2),
        obs('O-R02-1', 'R02', 'Yasna45.1, lesson Text3; printed/PDF p.35, reinforced p.101',
            'The edited stanza addresses listeners approaching from near and far and presents a proclamation linked to cosmic order.',
            'presence in an edited Old Avestan passage', 'Organized addressed speech exists in this Iranian comparator; broad teaching sophistication is not uniquely diagnostic of a local urban source.',
            'The represented audience is not an excavated school, a dated examination or a surveyed institution.',
            'Now hear', 35),
        obs('O-R02-2', 'R02', 'Yasna33.6; printed/PDF pp.70,136',
            'The lesson gives zaotā as a libator associated with ritual order and desirable action; its translation retains an uncertain divine referent.',
            'edited role term and qualified translation', 'A ritual-specialist role supplies an Iranian control relevant to R2.',
            'The verse does not enumerate a historical human staffing pattern or authenticate a local institutional donor.',
            'libator', 70),
        obs('O-R02-3', 'R02', 'Selected Yasna31.9–11 phrases; printed/PDF p.123',
            'The passages connect divine fashioning, a cow’s choice, a cattle tender or forager, herds and thought in the edition’s interpretation.',
            'edited figurative and divine relations', 'A pastoral conceptual comparator is available; R2/R4 remain plausible for broad relations.',
            'These selected phrases specify no ploughing, seed-processing or water-lifting sequence and cannot serve as its operation match.',
            'tender of cattle', 123),
        obs('O-R02-4', 'R02', 'Yasna46.14; printed/PDF pp.161–162',
            'The translated passage places Vištāspa with song, gift exchange and audition; the surrounding translated verse retains uncertainty about the named generous figure.',
            'edited support/performance relation', 'A poet-support relationship is represented; a teaching or patronage setting need not be uniquely local.',
            'The presence of a name does not establish an independently dated royal patron or a literal teacher genealogy.',
            'audition', 162),
        obs('O-R03-1', 'R03', 'Opening YASNA paragraph',
            'Boyce attributes a common origin to basic haoma/soma ritual similarities while recording later differences.',
            'attributed comparative ritual reconstruction', 'R2 is an available account for the shared ritual core.',
            'The reconstructed common core does not date all subsequently described ingredients, officiants or ritual operations.',
            'common origin'),
        obs('O-R03-2', 'R03', 'Opening account identification and paragraph on the second parahōm preparation',
            'The detailed account summarizes Bhagaria performance described by Kotwal; links to Old Avestan modifications are stated as suggestions and possibilities.',
            'source-layer and interpretation control', 'R5 and later elaboration affect the received ritual account.',
            'Modern observation, Young Avestan prescription and a proposed early change have different evidential status.',
            'It is this account which is summarized here'),
        obs('O-R04-1', 'R04', 'PDF p.2, article p.1, introduction',
            'The northernmost South Asian transect begins around1200BCE; the IVC-related profile is modeled partly from individuals at culturally connected sites.',
            'published sampling and model scope', 'Demographic continuity or contact can supply opportunity for R1/R3.',
            'The source does not observe a feature-specific teacher, taught recipe or literary transfer.',
            'cultural contact', 2),
        obs('O-R04-2', 'R04', 'Fig.3B/caption, PDF p.9, article p.8',
            'The authors describe ancestry arrows as plausible directions and say sampling does not determine exact routes; the figure marks South Asian entry uncertain.',
            'published geographic uncertainty', 'Possible contacts are compatible with several activity-specific routes.',
            'An ancestry arrow cannot be used as the observed route of a particular institution.',
            'not meant as exact routes', 9),
        obs('O-R04-3', 'R04', 'PDF p.12, article p.11, modern-group comparison',
            'The priestly-group comparison is qualified by shared ancestry, nonblinded selection and potentially changing group classification.',
            'published limitations on an attributed inference', 'The finding can inform population history while institutional descent requires additional premises.',
            'Present classifications cannot be silently assigned to sampled Bronze Age offices.',
            'not a formal test', 12),
        obs('O-R04-4', 'R04', 'PDF p.13, article p.12, Dravidian discussion',
            'The discussion presents both IVC-associated and southern/eastern explanations of proto-Dravidian spread using genetic, archaeological and linguistic premises.',
            'attributed alternative scenarios', 'Several historical routes remain in the source’s own argument.',
            'No scenario authenticates an Indus sign reading or identifies a transferred technical operation.',
            'An alternative possibility', 13),
        obs('O-R05-1', 'R05', 'Printed p.259, PDF p.3',
            'Witzel describes locally accepted school canons and links school differentiation to area, community, ritual and pronunciation.',
            'attributed school history', 'R5 can consolidate distinct local verbal and ritual traditions.',
            'The source’s cited medieval manuscript estimate is not the date of composition or a modern census of every surviving witness.',
            'texts accepted by each school', 3),
        obs('O-R05-2', 'R05', 'Printed pp.264–266, PDF pp.8–10',
            'The chapter distinguishes family-book collection from later rearrangement and argues that Kuru-era ritual and political consolidation brought traditions together.',
            'attributed historical reconstruction', 'R5 supplies a mechanism for mature combinations in a received corpus.',
            'The Kuru setting is a scholarly reconstruction; it does not imply every incorporated component originated then.',
            'Two Stages', 8),
        obs('O-R05-3', 'R05', 'Printed pp.335–336, PDF pp.79–80',
            'The summary discusses neighboring-school influence and later comprehensive compilations while stating that final compilation and redaction dates often remain unknown.',
            'attributed synthesis with explicit chronological limits', 'R3/R5 may interact within the history of Vedic schools.',
            'A broad canon history does not supply a feature-specific Harappan-to-school join.',
            'still open to discussion', 80),
        obs('O-R07-1', 'R07', 'Opening Indo-Iranian/Old Indic/Old Avestan comparison',
            'Skjærvø compares poet-sacrificer roles and the hotar/zaotar, announcement and speech vocabulary across the two traditions.',
            'attributed comparative reconstruction', 'R2 supplies an independently motivated verbal/role control.',
            'The comparison uses philological premises; it does not require an excavated teacher for each cognate or identify every technical practice.',
            'In the Old Avesta'),
        obs('O-R07-2', 'R07', 'Old Avestan kauui/karapan discussion',
            'The article argues that inherited poet/priest labels acquired negative associations in Old Avestan while related role vocabulary remained.',
            'attributed semantic and ritual interpretation', 'A transmitted vocabulary can undergo role evaluation and conceptual change.',
            'Lexical continuity does not imply an unchanged office or unmodified ritual sequence.',
            'incorrect sacrifices'),
        obs('O-R07-3', 'R07', 'Vištāspa and sovereignty paragraphs',
            'The article disputes reading kauui as ruler from later Pahlavi and Perso-Arabic royal sequences back into Avestan.',
            'attributed criticism of a backward interpretation', 'Later narrated genealogy can supply R5 framing of older material.',
            'This is the author’s disputed interpretation, not an adjudicated identification of a historical Vištāspa.',
            'chronological sequence of rulers'),
    ]
    source_doc = {'created_utc': datetime.now(timezone.utc).isoformat(),
                  'scope': 'Six scoped primary works in seven target records; purposive adversarial controls, not independent ancient attestations or a comparative-rarity sample.',
                  'sources': sources, 'acquisition_attempts': captures,
                  'derivatives': derivatives,
                  'protocol_sha256': sha(HERE / 'PROTOCOL.md'),
                  'control_loci_sha256': sha(HERE / 'CONTROL-LOCI.md'),
                  'access_amendment_sha256': sha(HERE / 'AMENDMENT-source-access.md'),
                  'code_sha256': sha(Path(__file__))}
    observation_doc = {'scope': 'Authored summaries at inspected loci. Direct textual presence, published findings and attributed reconstructions remain distinct.',
                       'observations': observations}
    for name, value in [('sources.json', source_doc), ('observations.json', observation_doc)]:
        with (HERE / name).open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
    print(json.dumps({'target_records': len(sources),
                      'scoped_primary_works': sum(s['selected_primary_work'] for s in sources),
                      'observations': len(observations), 'access_attempts': len(captures)}, indent=2))
