"""Write a separate bibliography for the lecture amendment; preserve sources.json."""
import hashlib
import json
from pathlib import Path

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[1]
RAW = ROOT / 'data/raw/2026-10-06-sign-context-and-seals'


def run():
    dest = OWN / 'sources-followup-2026-10-07.json'
    if dest.exists():
        raise FileExistsError('The follow-up bibliography already exists.')
    records = [
        {'id': 'CAP2026', 'title': "Checking the summary of Frenez's lecture against its captions",
         'authors': ['Project coordinating session'], 'year': 2026, 'venue': 'Private repository source review, 7 October',
         'url': 'https://youtu.be/1i9q17ld_jU', 'access': 'opened_coordinator_review; original video not independently viewed by D2',
         'locations': ['28:45–29:30 inventory', '29:30–30:40 frequency and terminal position', '41:30–43:30 motifs and persistence'],
         'local_review': 'experiments/2026-10-06-research-program/frenez-talk-check.md',
         'relation': 'Source of the newly assigned quantitative hypotheses; automatic captions are paraphrased in the coordinator review.'},
        {'id': 'CH2014', 'title': 'Rarefaction and extrapolation with Hill numbers: a framework for sampling and estimation in species diversity studies',
         'authors': ['Anne Chao', 'Nicholas J. Gotelli', 'T. C. Hsieh', 'Elizabeth L. Sander', 'K. H. Ma', 'Robert K. Colwell', 'Aaron M. Ellison'],
         'year': 2014, 'venue': 'Ecological Monographs 84(1):45–67', 'doi': '10.1890/13-0133.1',
         'url': 'https://www.robertkcolwell.org/publications/6842.pdf', 'access': 'opened_author_pdf_and_extracted_tables',
         'locations': ['Tables 1–2, PDF pp.8–9 and 12–13, printed pp.52–53 and 56–57'],
         'asset_ids': ['chao2014', 'chao2014author'],
         'relation': 'Abundance and incidence rarefaction, Chao unseen lower bounds and short-range extrapolation. No independent-token uncertainty is used as object-level inference.'},
        {'id': 'INEXT', 'title': 'iNEXT: R package for interpolation and extrapolation, R/iNEXT.r',
         'authors': ['T. C. Hsieh and iNEXT contributors'], 'year': 'software witness acquired 2026-10-07',
         'venue': 'Author-maintained GitHub repository, mutable master witness pinned by SHA256',
         'url': 'https://github.com/JohnsonHsieh/iNEXT/blob/master/R/iNEXT.r',
         'access': 'opened_source_code', 'locations': ['EstiBootComm.Ind', 'EstiBootComm.Sam', 'TD.m.est'],
         'asset_ids': ['inextsource'], 'relation': 'Cross-checks standard Chao1/Chao2 zero-doubleton handling; package code was written independently.'},
        {'id': 'KCH2005', 'title': 'Steatite and Faience Manufacturing at Harappa: New Evidence from Mound E Excavations 2000-2001',
         'authors': ['Jonathan Mark Kenoyer'], 'year': 2005,
         'venue': 'Museum Journal (National Museum of Pakistan), Vol. III & IV (Jan–Dec 2002):43–56',
         'url': 'https://www.harappa.com/sites/default/files/pdf/Kenoyer%202005%20Faience%20Workshop.pdf',
         'access': 'opened_pdf_and_page_text', 'locations': ['PDF p.1 bibliographic header; PDF p.2, Faience and Steatite Workshop, first paragraph'],
         'asset_ids': ['kenoyer2005chronology'], 'relation': 'Published broad dates for Harappa 3A, 3B and 3C. The issue date and cited publication year differ and are retained.'},
        {'id': 'FS2016', 'title': 'Bronze Age Salūt (ST1) and the Indus Civilization: recent discoveries and new insights on regional interaction',
         'authors': ['Dennys Frenez', 'Michele Degli Esposti', 'Sophie Méry', 'Jonathan Mark Kenoyer'],
         'year': 2016, 'venue': 'Proceedings of the Seminar for Arabian Studies 46:107–124',
         'url': 'https://harappa.com/sites/default/files/pdf/Bronze-Age-Indus-Connections.pdf',
         'access': 'opened_pdf_and_page_text', 'locations': ['printed pp.116–117, PDF pp.16–17, Figure 9 and adjacent paragraphs'],
         'asset_ids': ['salut2016'], 'relation': 'Identifies Indian bison as Bos gaurus and discusses external Indus-related seals, with reference to Vidale 2005. It does not authenticate every local Gaur code.'},
        {'id': 'F2023', 'title': 'Indus Valley: Early Commercial Connections with Central and Western Asia',
         'authors': ['Dennys Frenez'], 'year': 2023, 'venue': 'Oxford Research Encyclopedia of Asian History, published online 18 October',
         'doi': '10.1093/acrefore/9780190277727.013.595',
         'url': 'https://oxfordre.com/asianhistory/view/10.1093/acrefore/9780190277727.001.0001/acrefore-9780190277727-e-595',
         'access': 'primary_fulltext_blocked_403; bibliographic_search_snippet_and_opened_secondary_summary',
         'locations': ['Harappa.com summary, paragraph beginning Almost 90 percent and Image 2 caption'],
         'secondary_url': 'https://www.harappa.com/content/indus-valley-early-commercial-connections-central-and-western-asia',
         'asset_ids': ['frenez2023primary', 'frenez2024summary'],
         'relation': 'The secondary summary gives near-90% bison among round external seals and about 40% round seals among all external Indus-related seals. Full primary text remains unreviewed; the provisional filename says 2024 but does not set the publication year.'},
        {'id': 'Y2010', 'title': 'Statistical Analysis of the Indus Script Using n-Grams',
         'authors': ['Nisha Yadav', 'Hrishikesh Joglekar', 'Rajesh P. N. Rao', 'Mayank N. Vahia', 'Ronojoy Adhikari', 'Iravatham Mahadevan'],
         'year': 2010, 'venue': 'PLOS ONE 5(3):e9506', 'doi': '10.1371/journal.pone.0009506',
         'url': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0009506',
         'access': 'opened_full_html', 'locations': ['Results and Discussion, Empirical Analysis, Figure 2 and following beginner/ender discussion'],
         'asset_ids': ['yadav2010'], 'relation': 'Prior sign concentration and end-position asymmetry, with duplicate/ambiguity filtering. It uses Mahadevan codes; no 740–342 crosswalk is asserted here.'},
        {'id': 'FSW2004', 'title': 'The Collapse of the Indus-Script Thesis: The Myth of a Literate Harappan Civilization',
         'authors': ['Steve Farmer', 'Richard Sproat', 'Michael Witzel'], 'year': 2004,
         'venue': 'Electronic Journal of Vedic Studies 11(2):19–57', 'url': 'https://safarmer.com/files/fsw3.pdf',
         'access': 'opened_author_pdf_and_page_text', 'locations': ['printed pp.26–27, Paradoxical sign frequencies, Figure 2'],
         'asset_ids': ['farmer2004'],
         'relation': 'Gives top-four 21%, top-eight 31% and top-twenty over 50% for Mahadevan, and a high-frequency comparison with Wells. These are different rank cutoffs from the lecture; the package does not adopt the paper’s linguistic conclusion.'}
    ]
    attempts = []
    for p in sorted(RAW.glob('followup-sources-2026-10-07-*/manifest.json')):
        attempts.extend(json.loads(p.read_text(encoding='utf-8')))
    for record in records:
        record['quotations_used'] = 0
        record['acquisitions'] = [r for r in attempts if r['id'] in record.get('asset_ids', [])]
        if 'local_review' in record:
            record['review_sha256'] = hashlib.sha256((ROOT / record['local_review']).read_bytes()).hexdigest()
    searches = [
        {'queries': ['Frenez unicorn bison outside Indus valley oligopoly seals 2018', 'Frenez bison unicorn', 'Indus Frenez bison outside'],
         'outcome': 'Located the opened Salūt 2016 primary article and the 2023 encyclopedia summary; primary encyclopedia returned 403.'},
        {'queries': ['Wells Indus sign frequency 740 20 percent twenty signs 50', 'Wells 740 frequency', 'Indus Wells 740 sign', 'Bryan Wells The Computational Structure Indus', 'Wells Indus twenty signs frequency'],
         'outcome': 'The exact four lecture percentages and site inventory bands were not traced to an opened Wells table. Located Yadav 2010 and Farmer/Sproat/Witzel 2004 concentration precedents. Modern exploratory sites were not used as published evidence.'},
        {'queries': ['Chao Jost 2014 rarefaction extrapolation incidence sample based formula richness iNEXT', 'Chao 2014 Rarefaction and extrapolation with Hill numbers', 'Chao_etal_2014_EM.pdf', 'Chao 2014 Hill numbers pdf nthu', 'iNEXT R code EstiBootComm abundance Chao1 2014 github'],
         'outcome': 'Harvard PDF failed through web and direct route (404); author-hosted PDF and author-maintained source code succeeded.'},
        {'queries': ['Harappa Period 3A 3B 3C 2600 2450 2200 1900 Kenoyer'],
         'outcome': 'Located published broad chronology in Kenoyer’s workshop article; no dates for 3C-1 to 3C-4 were assigned.'}
    ]
    result = {'stage': 'post-launch amendment', 'status': 'Exploratory', 'sources': records,
              'reused_sources': {'manifest': 'sources.json', 'ids': ['Y2013', 'F2018', 'K1997', 'S2019', 'K2005']},
              'search_and_access_log': searches, 'all_download_attempts': attempts,
              'rights': 'Third-party payloads and extracted text stay local-only under the repository redistribution policy.'}
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(len(records), 'source records;', len(attempts), 'acquisition attempts')


if __name__ == '__main__':
    run()
